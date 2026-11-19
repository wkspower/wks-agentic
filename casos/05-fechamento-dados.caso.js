// Fechamento do dia e formato dos dados guardados.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const {
  dados, venda, hoje, diasAtras, com, acionar, preencher, ve, linha, vender,
} = require('./apoio');

// ORIGEM: resposta do usuário (B14).
test('B14: fechamento soma por forma de pagamento e ignora as canceladas', () =>
  com(dados({
    vendas: [
      venda({ id: 1, total_centavos: 4999, forma_pagamento: 'dinheiro' }),
      venda({ id: 2, total_centavos: 1000, forma_pagamento: 'dinheiro' }),
      venda({ id: 3, total_centavos: 5500, forma_pagamento: 'pix' }),
      venda({
        id: 4, total_centavos: 7700, forma_pagamento: 'cartao', status: 'cancelada',
        cancelamento: { data: hoje(), hora: '10:00', motivo: 'erro' },
      }),
    ],
  }), async (s) => {
    await acionar(s.page, 'Fechamento do dia');
    await ve(s.page, 'Dinheiro: R$ 59,99');
    await ve(s.page, 'Pix: R$ 55,00');
    await ve(s.page, 'Cartão: R$ 0,00');
    await ve(s.page, 'Total: R$ 114,99');
  }));

// ORIGEM: resposta do usuário (B14: é o fechamento "do dia").
test('B14: vendas de outro dia não entram em hoje, e aparecem ao escolher a data', () =>
  com(dados({
    vendas: [
      venda({ id: 1, total_centavos: 1000, forma_pagamento: 'pix' }),
      venda({ id: 2, total_centavos: 2500, forma_pagamento: 'cartao', data: diasAtras(1) }),
    ],
  }), async (s) => {
    const { page } = s;
    await acionar(page, 'Fechamento do dia');
    await ve(page, 'Total: R$ 10,00');
    await preencher(page, 'Data', diasAtras(1));
    await acionar(page, 'Ver fechamento');
    await ve(page, 'Cartão: R$ 25,00');
    await ve(page, 'Total: R$ 25,00');
  }));

// ORIGEM: resposta do usuário (B15).
test('B15: identificador não é reutilizado: apago o produto 3, o próximo é 4', () =>
  com(dados({
    produtos: [1, 2, 3].map((id) => ({ id, nome: `Produto ${id}`, preco_centavos: 100, estoque: 1 })),
  }), async (s) => {
    const { page } = s;
    await acionar(page, 'Produtos');
    await acionar(linha(page, 'Produto 3').first(), 'Apagar');
    await ve(page, 'Produto apagado');
    assert.deepEqual(s.ler().produtos.map((p) => p.id), [1, 2]);
    await acionar(page, 'Produtos');
    await acionar(page, 'Novo produto');
    await preencher(page, 'Nome', 'Novo');
    await preencher(page, 'Preço', '1,00');
    await preencher(page, 'Estoque', '1');
    await acionar(page, 'Salvar');
    await ve(page, 'Produto salvo');
    const d = s.ler();
    assert.equal(d.produtos.find((p) => p.nome === 'Novo').id, 4);
    assert.equal(d.proximo_id.produtos, 5);
  }));

// ORIGEM: resposta do usuário (A3 e B15: um arquivo JSON com "versao", datas
// AAAA-MM-DD, horas HH:MM, campos em português). Os nomes exatos dos campos
// são SUPOSIÇÃO minha, escrita em DESCRICAO.md seção 2.
test('A3/B15: começando sem arquivo, a primeira venda grava o formato completo', () =>
  com(null, async (s) => {
    const { page } = s;
    await acionar(page, 'Produtos');
    await acionar(page, 'Novo produto');
    await preencher(page, 'Nome', 'Ração 1kg');
    await preencher(page, 'Preço', '45,00');
    await preencher(page, 'Estoque', '10');
    await acionar(page, 'Salvar');
    await ve(page, 'Produto salvo');
    await vender(page, { itens: [['Ração 1kg', 1]], forma: 'Dinheiro', recebido: '50,00' });
    await ve(page, 'Venda finalizada');

    const d = s.ler();
    assert.deepEqual(Object.keys(d).sort(), [
      'agendamentos', 'clientes', 'pets', 'produtos', 'proximo_id', 'vendas', 'versao',
    ]);
    assert.equal(d.versao, 1);
    assert.deepEqual(d.proximo_id, { clientes: 1, pets: 1, produtos: 2, vendas: 2, agendamentos: 1 });
    assert.deepEqual(d.produtos, [{ id: 1, nome: 'Ração 1kg', preco_centavos: 4500, estoque: 9 }]);
    assert.equal(d.vendas.length, 1);
    const { hora, ...v } = d.vendas[0];
    assert.match(hora, /^([01]\d|2[0-3]):[0-5]\d$/);
    assert.deepEqual(v, {
      id: 1,
      data: hoje(),
      cliente_id: null,
      origem: 'balcao',
      agendamento_id: null,
      itens: [{ produto_id: 1, descricao: 'Ração 1kg', preco_unitario_centavos: 4500, quantidade: 1 }],
      subtotal_centavos: 4500,
      desconto_centavos: 0,
      total_centavos: 4500,
      forma_pagamento: 'dinheiro',
      recebido_centavos: 5000,
      troco_centavos: 500,
      status: 'finalizada',
      cancelamento: null,
    });
  }));

// ORIGEM: resposta do usuário (B16).
test('B16: cadastro recusado deixa o arquivo idêntico byte a byte', () =>
  com(dados(), async (s) => {
    const { page } = s;
    const cadastra = async (nome, telefone) => {
      await acionar(page, 'Clientes');
      await acionar(page, 'Novo cliente');
      await preencher(page, 'Nome', nome);
      await preencher(page, 'Telefone', telefone);
      await acionar(page, 'Salvar');
    };
    await cadastra('Maria Silva', '11999990001');
    await ve(page, 'Cliente salvo');
    const antes = s.bytes();
    await cadastra('Outra Pessoa', '11999990001');
    await ve(page, 'Telefone já cadastrado para Maria Silva');
    assert.ok(antes.equals(s.bytes()), 'o arquivo mudou numa operação recusada');
  }));
