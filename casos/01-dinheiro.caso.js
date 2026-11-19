// Dinheiro: entrada, exibição, total, desconto, pagamento, troco, preço do momento.
// ORIGEM de cada caso está no comentário acima dele.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const { dados, com, acionar, preencher, ve, linha, vender } = require('./apoio');

const produtos = () => [
  { id: 1, nome: 'Petisco', preco_centavos: 333, estoque: 50 },
  { id: 2, nome: 'Ração 1kg', preco_centavos: 4500, estoque: 50 },
];

async function novoProduto(page, nome, preco, estoque = '10') {
  await acionar(page, 'Produtos');
  await acionar(page, 'Novo produto');
  await preencher(page, 'Nome', nome);
  await preencher(page, 'Preço', preco);
  await preencher(page, 'Estoque', estoque);
  await acionar(page, 'Salvar');
}

// ORIGEM: resposta do usuário (B1, aceito em 2026-11-19).
test('B1: preço "12,5" é guardado como 1250 centavos e mostrado como R$ 12,50', () =>
  com(dados(), async (s) => {
    await novoProduto(s.page, 'Coleira', '12,5');
    await ve(s.page, 'Produto salvo');
    const p = s.ler().produtos;
    assert.equal(p.length, 1);
    assert.equal(p[0].preco_centavos, 1250);
    await acionar(s.page, 'Produtos');
    await linha(s.page, 'Coleira').filter({ hasText: 'R$ 12,50' }).first().waitFor();
  }));

// ORIGEM: resposta do usuário (B1).
for (const ruim of ['abc', '-5']) {
  test(`B1: preço "${ruim}" é recusado com "Valor inválido" e nada é gravado`, () =>
    com(dados(), async (s) => {
      await novoProduto(s.page, 'Coleira', ruim);
      await ve(s.page, 'Valor inválido');
      assert.equal(s.ler().produtos.length, 0);
    }));
}

// ORIGEM: resposta do usuário (B1: formato R$ 1.234,56).
test('B1: milhar é mostrado com ponto: R$ 1.234,56', () =>
  com(dados({ produtos: [{ id: 1, nome: 'Aquário', preco_centavos: 123456, estoque: 1 }] }), async (s) => {
    await acionar(s.page, 'Produtos');
    await linha(s.page, 'Aquário').filter({ hasText: 'R$ 1.234,56' }).first().waitFor();
  }));

// ORIGEM: resposta do usuário (B2).
test('B2: 3 × R$ 3,33 + 1 × R$ 45,00 dá Total: R$ 54,99', () =>
  com(dados({ produtos: produtos() }), async (s) => {
    await vender(s.page, { itens: [['Petisco', 3], ['Ração 1kg', 1]], forma: 'Pix' });
    await ve(s.page, 'Venda finalizada');
    const v = s.ler().vendas[0];
    assert.equal(v.subtotal_centavos, 5499);
    assert.equal(v.total_centavos, 5499);
    assert.equal(v.itens.length, 2);
  }));

// ORIGEM: resposta do usuário (B2: o total aparece na tela antes de finalizar).
test('B2: a tela da venda mostra "Total: R$ 54,99" depois de adicionar os itens', () =>
  com(dados({ produtos: produtos() }), async (s) => {
    const { page } = s;
    const { escolher } = require('./apoio');
    await acionar(page, 'Vendas');
    await acionar(page, 'Nova venda');
    for (const [nome, qtd] of [['Petisco', '3'], ['Ração 1kg', '1']]) {
      await escolher(page, 'Produto', nome);
      await preencher(page, 'Quantidade', qtd);
      await acionar(page, 'Adicionar item');
    }
    await ve(page, 'Total: R$ 54,99');
  }));

// ORIGEM: resposta do usuário (B3).
test('B3: desconto de 5,00 sobre R$ 54,99 dá R$ 49,99', () =>
  com(dados({ produtos: produtos() }), async (s) => {
    await vender(s.page, { itens: [['Petisco', 3], ['Ração 1kg', 1]], desconto: '5,00', forma: 'Pix' });
    await ve(s.page, 'Venda finalizada');
    const v = s.ler().vendas[0];
    assert.equal(v.desconto_centavos, 500);
    assert.equal(v.total_centavos, 4999);
    await acionar(s.page, 'Vendas');
    await linha(s.page, 'R$ 49,99').filter({ hasText: 'Pix' }).first().waitFor();
  }));

// ORIGEM: resposta do usuário (B3).
test('B3: desconto de 60,00 sobre R$ 54,99 é recusado', () =>
  com(dados({ produtos: produtos() }), async (s) => {
    await vender(s.page, { itens: [['Petisco', 3], ['Ração 1kg', 1]], desconto: '60,00', forma: 'Pix' });
    await ve(s.page, 'Desconto maior que o total');
    const d = s.ler();
    assert.equal(d.vendas.length, 0);
    assert.equal(d.produtos[0].estoque, 50);
  }));

// ORIGEM: resposta do usuário (B4).
test('B4: total R$ 49,99 pago com 50,00 em dinheiro mostra Troco: R$ 0,01', () =>
  com(dados({ produtos: produtos() }), async (s) => {
    await vender(s.page, {
      itens: [['Petisco', 3], ['Ração 1kg', 1]], desconto: '5,00', forma: 'Dinheiro', recebido: '50,00',
    });
    await ve(s.page, 'Venda finalizada');
    await ve(s.page, 'Troco: R$ 0,01');
    const v = s.ler().vendas[0];
    assert.equal(v.forma_pagamento, 'dinheiro');
    assert.equal(v.recebido_centavos, 5000);
    assert.equal(v.troco_centavos, 1);
  }));

// ORIGEM: resposta do usuário (B4).
test('B4: total R$ 49,99 com 40,00 recebidos é recusado', () =>
  com(dados({ produtos: produtos() }), async (s) => {
    await vender(s.page, {
      itens: [['Petisco', 3], ['Ração 1kg', 1]], desconto: '5,00', forma: 'Dinheiro', recebido: '40,00',
    });
    await ve(s.page, 'Valor recebido insuficiente');
    assert.equal(s.ler().vendas.length, 0);
  }));

// ORIGEM: resposta do usuário (B4: três formas de pagamento).
test('B4: venda no cartão é guardada como "cartao", sem recebido nem troco', () =>
  com(dados({ produtos: produtos() }), async (s) => {
    await vender(s.page, { itens: [['Ração 1kg', 1]], forma: 'Cartão' });
    await ve(s.page, 'Venda finalizada');
    const v = s.ler().vendas[0];
    assert.equal(v.forma_pagamento, 'cartao');
    // SUPOSIÇÃO minha: null para recebido/troco fora do dinheiro (formato do arquivo).
    assert.equal(v.recebido_centavos, null);
    assert.equal(v.troco_centavos, null);
  }));

// ORIGEM: resposta do usuário (B5).
test('B5: mudar o preço do produto não muda a venda já feita', () =>
  com(dados({ produtos: produtos() }), async (s) => {
    const { page } = s;
    await vender(page, { itens: [['Ração 1kg', 1]], forma: 'Pix' });
    await ve(page, 'Venda finalizada');
    await acionar(page, 'Produtos');
    await acionar(linha(page, 'Ração 1kg').first(), 'Editar');
    await preencher(page, 'Preço', '50,00');
    await acionar(page, 'Salvar');
    await ve(page, 'Produto salvo');
    const d = s.ler();
    assert.equal(d.produtos.find((p) => p.id === 2).preco_centavos, 5000);
    assert.equal(d.vendas[0].total_centavos, 4500);
    assert.equal(d.vendas[0].itens[0].preco_unitario_centavos, 4500);
    await acionar(page, 'Vendas');
    await linha(page, 'R$ 45,00').first().waitFor();
  }));
