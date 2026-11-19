// Estoque, cancelamento de venda (o que não se desfaz) e gravação íntegra.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const {
  dados, venda, com, acao, acionar, preencher, escolher, ve, aparece, linha, vender,
} = require('./apoio');

const racao = (estoque) => [{ id: 1, nome: 'Ração 1kg', preco_centavos: 4500, estoque }];

// Tenta vender mais do que há. O sistema pode recusar ao adicionar o item
// ou ao finalizar (isso é livre); a mensagem e o resultado são fixos.
async function tentaVenderDemais(page, produto, quantidade) {
  await acionar(page, 'Vendas');
  await acionar(page, 'Nova venda');
  await escolher(page, 'Produto', produto);
  await preencher(page, 'Quantidade', String(quantidade));
  await acionar(page, 'Adicionar item');
  if (await aparece(page, 'Estoque insuficiente')) return;
  await escolher(page, 'Forma de pagamento', 'Pix');
  await acionar(page, 'Finalizar venda');
}

// ORIGEM: resposta do usuário (B6).
test('B6: vender baixa o estoque', () =>
  com(dados({ produtos: racao(5) }), async (s) => {
    await vender(s.page, { itens: [['Ração 1kg', 2]] });
    await ve(s.page, 'Venda finalizada');
    assert.equal(s.ler().produtos[0].estoque, 3);
  }));

// ORIGEM: resposta do usuário (B6).
test('B6: estoque 2, vender 3 é recusado com "Estoque insuficiente (disponível: 2)"', () =>
  com(dados({ produtos: racao(2) }), async (s) => {
    await tentaVenderDemais(s.page, 'Ração 1kg', 3);
    await ve(s.page, 'Estoque insuficiente (disponível: 2)');
    const d = s.ler();
    assert.equal(d.vendas.length, 0);
    assert.equal(d.produtos[0].estoque, 2);
  }));

// ORIGEM: resposta do usuário (B16).
test('B16: venda recusada por estoque deixa o arquivo idêntico byte a byte', () =>
  com(dados({ produtos: racao(3) }), async (s) => {
    await vender(s.page, { itens: [['Ração 1kg', 1]] }); // faz o sistema gravar do jeito dele
    await ve(s.page, 'Venda finalizada');
    const antes = s.bytes();
    await tentaVenderDemais(s.page, 'Ração 1kg', 3);
    await ve(s.page, 'Estoque insuficiente (disponível: 2)');
    assert.ok(antes.equals(s.bytes()), 'o arquivo mudou numa operação recusada');
  }));

// ORIGEM: resposta do usuário (B7).
test('B7: cancelar com motivo mantém a venda como Cancelada, devolve o estoque e tira do fechamento', () =>
  com(dados({ produtos: racao(5) }), async (s) => {
    const { page } = s;
    await vender(page, { itens: [['Ração 1kg', 2]] });
    await ve(page, 'Venda finalizada');
    assert.equal(s.ler().produtos[0].estoque, 3);

    await acionar(page, 'Vendas');
    await acionar(linha(page, 'R$ 90,00').first(), 'Cancelar');
    await preencher(page, 'Motivo', 'erro');
    await acionar(page, 'Confirmar cancelamento');
    await ve(page, 'Venda cancelada');

    const d = s.ler();
    assert.equal(d.vendas.length, 1);
    assert.equal(d.vendas[0].status, 'cancelada');
    assert.equal(d.vendas[0].cancelamento.motivo, 'erro');
    assert.equal(d.vendas[0].total_centavos, 9000);
    assert.equal(d.produtos[0].estoque, 5);

    await acionar(page, 'Vendas');
    await linha(page, 'R$ 90,00').filter({ hasText: 'Cancelada' }).first().waitFor();
    await acionar(page, 'Fechamento do dia');
    await ve(page, 'Total: R$ 0,00');
  }));

// ORIGEM: resposta do usuário (B7: cancelar duas vezes é recusado).
test('B7: venda cancelada não oferece mais "Cancelar"', () =>
  com(dados({
    vendas: [venda({
      id: 1, total_centavos: 9000, status: 'cancelada',
      cancelamento: { data: '2026-11-19', hora: '10:00', motivo: 'erro' },
    })],
  }), async (s) => {
    await acionar(s.page, 'Vendas');
    const l = linha(s.page, 'R$ 90,00').first();
    await l.waitFor();
    assert.equal(await acao(l, 'Cancelar').count(), 0);
  }));

// ORIGEM: resposta do usuário (B7: "com motivo").
test('B7: cancelar sem motivo é recusado', () =>
  com(dados({ vendas: [venda({ id: 1, total_centavos: 9000 })] }), async (s) => {
    const { page } = s;
    await acionar(page, 'Vendas');
    await acionar(linha(page, 'R$ 90,00').first(), 'Cancelar');
    await preencher(page, 'Motivo', '');
    await acionar(page, 'Confirmar cancelamento');
    await ve(page, 'Motivo é obrigatório');
    assert.equal(s.ler().vendas[0].status, 'finalizada');
  }));

// ORIGEM: resposta do usuário (B7: não se edita nem se apaga).
test('B7: venda finalizada não tem ação de editar nem de apagar', () =>
  com(dados({ vendas: [venda({ id: 1, total_centavos: 9000 })] }), async (s) => {
    await acionar(s.page, 'Vendas');
    const l = linha(s.page, 'R$ 90,00').first();
    await l.waitFor();
    for (const nome of ['Editar', 'Apagar', 'Excluir', 'Remover']) {
      assert.equal(await acao(l, nome).count(), 0, `a venda oferece "${nome}"`);
    }
  }));
