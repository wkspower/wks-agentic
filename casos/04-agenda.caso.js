// Agenda: sobreposição, horário de funcionamento, preço por porte, estados.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const {
  dados, hoje, proximo, com, acao, acionar, escolher, preencher, ve, linha, agendar,
} = require('./apoio');

const SEGUNDA = proximo(1);
const DOMINGO = proximo(0);

const base = () => ({
  clientes: [{ id: 1, nome: 'Maria Silva', telefone: '11999990001', ativo: true }],
  pets: [
    { id: 1, nome: 'Rex', cliente_id: 1, especie: 'cao', porte: 'M', ativo: true },
    { id: 2, nome: 'Mimi', cliente_id: 1, especie: 'gato', porte: 'P', ativo: true },
    { id: 3, nome: 'Thor', cliente_id: 1, especie: 'cao', porte: 'G', ativo: true },
  ],
});
const banhoDoRex = () => ({
  id: 1, pet_id: 1, servico: 'banho', data: SEGUNDA, hora_inicio: '10:00', hora_fim: '11:00',
  preco_centavos: 5500, status: 'marcado', venda_id: null,
});

// ORIGEM: resposta do usuário (B11, B12; duração e preço aceitos em N2).
test('B11/B12: banho de pet M às 10:00 é marcado das 10:00 às 11:00 por R$ 55,00', () =>
  com(dados(base()), async (s) => {
    await agendar(s.page, { pet: 'Rex', servico: 'Banho', data: SEGUNDA, hora: '10:00' });
    await ve(s.page, 'Agendamento marcado');
    assert.deepEqual(s.ler().agendamentos, [banhoDoRex()]);
    await acionar(s.page, 'Agenda');
    await linha(s.page, 'Rex').filter({ hasText: 'R$ 55,00' }).filter({ hasText: 'Marcado' }).first().waitFor();
  }));

// ORIGEM: resposta do usuário (B11; um atendimento por vez aceito em N3).
test('B11: com banho 10:00–11:00 marcado, tosa às 10:30 é recusada com "Horário ocupado"', () =>
  com(dados({ ...base(), agendamentos: [banhoDoRex()] }), async (s) => {
    await agendar(s.page, { pet: 'Mimi', servico: 'Tosa', data: SEGUNDA, hora: '10:30' });
    await ve(s.page, 'Horário ocupado');
    assert.equal(s.ler().agendamentos.length, 1);
  }));

// ORIGEM: resposta do usuário (B11; horário aceito em N1).
test('B11: agendar no domingo é recusado', () =>
  com(dados(base()), async (s) => {
    await agendar(s.page, { pet: 'Rex', servico: 'Banho', data: DOMINGO, hora: '10:00' });
    await ve(s.page, 'Fora do horário de funcionamento');
    assert.equal(s.ler().agendamentos.length, 0);
  }));

// ORIGEM: resposta do usuário (B11; horário aceito em N1).
test('B11: agendar às 19:00 é recusado', () =>
  com(dados(base()), async (s) => {
    await agendar(s.page, { pet: 'Rex', servico: 'Banho', data: SEGUNDA, hora: '19:00' });
    await ve(s.page, 'Fora do horário de funcionamento');
    assert.equal(s.ler().agendamentos.length, 0);
  }));

// ORIGEM: resposta do usuário (B12; tabela aceita em N2).
const TABELA = [
  ['Mimi', 'Banho', 'banho', '08:00', '09:00', 4000],
  ['Thor', 'Banho', 'banho', '09:00', '10:00', 7500],
  ['Mimi', 'Tosa', 'tosa', '10:00', '11:30', 6000],
  ['Rex', 'Tosa', 'tosa', '11:30', '13:00', 8000],
  ['Thor', 'Tosa', 'tosa', '13:00', '14:30', 11000],
  ['Mimi', 'Banho e tosa', 'banho_e_tosa', '08:00', '10:00', 9000],
  ['Rex', 'Banho e tosa', 'banho_e_tosa', '10:00', '12:00', 12000],
  ['Thor', 'Banho e tosa', 'banho_e_tosa', '14:00', '16:00', 16000],
];
for (const [pet, servico, codigo, inicio, fim, preco] of TABELA) {
  test(`B12: ${servico} para ${pet} dura até ${fim} e custa ${preco} centavos`, () =>
    com(dados(base()), async (s) => {
      await agendar(s.page, { pet, servico, data: SEGUNDA, hora: inicio });
      await ve(s.page, 'Agendamento marcado');
      const a = s.ler().agendamentos[0];
      assert.equal(a.servico, codigo);
      assert.equal(a.hora_inicio, inicio);
      assert.equal(a.hora_fim, fim);
      assert.equal(a.preco_centavos, preco);
    }));
}

// ORIGEM: resposta do usuário (B12: o preço fica gravado no agendamento).
test('B12: o preço mostrado é o gravado no agendamento', () =>
  com(dados({ ...base(), agendamentos: [{ ...banhoDoRex(), preco_centavos: 5000 }] }), async (s) => {
    await acionar(s.page, 'Agenda');
    await linha(s.page, 'Rex').filter({ hasText: 'R$ 50,00' }).first().waitFor();
  }));

// ORIGEM: resposta do usuário (B13).
test('B13: concluir banho de R$ 55,00 no pix gera venda e entra no fechamento de hoje', () =>
  com(dados({ ...base(), agendamentos: [banhoDoRex()] }), async (s) => {
    const { page } = s;
    await acionar(page, 'Agenda');
    await acionar(linha(page, 'Rex').first(), 'Concluir');
    await escolher(page, 'Forma de pagamento', 'Pix');
    await acionar(page, 'Confirmar conclusão');
    await ve(page, 'Agendamento concluído');

    const d = s.ler();
    assert.equal(d.agendamentos[0].status, 'concluido');
    assert.equal(d.vendas.length, 1);
    const v = d.vendas[0];
    assert.equal(d.agendamentos[0].venda_id, v.id);
    assert.equal(v.total_centavos, 5500);
    assert.equal(v.forma_pagamento, 'pix');
    assert.equal(v.status, 'finalizada');
    // SUPOSIÇÃO minha: campos que ligam a venda ao agendamento e data = dia da conclusão.
    assert.equal(v.origem, 'agendamento');
    assert.equal(v.agendamento_id, 1);
    assert.equal(v.data, hoje());
    assert.deepEqual(v.itens, [
      { produto_id: null, descricao: 'Banho', preco_unitario_centavos: 5500, quantidade: 1 },
    ]);

    await acionar(page, 'Fechamento do dia');
    await ve(page, 'Pix: R$ 55,00');
    await ve(page, 'Total: R$ 55,00');
  }));

// ORIGEM: resposta do usuário (B13 + B4: troco só em dinheiro).
test('B13: concluir em dinheiro com 60,00 recebidos guarda troco de 5,00', () =>
  com(dados({ ...base(), agendamentos: [banhoDoRex()] }), async (s) => {
    const { page } = s;
    await acionar(page, 'Agenda');
    await acionar(linha(page, 'Rex').first(), 'Concluir');
    await escolher(page, 'Forma de pagamento', 'Dinheiro');
    await preencher(page, 'Valor recebido', '60,00');
    await acionar(page, 'Confirmar conclusão');
    await ve(page, 'Agendamento concluído');
    const v = s.ler().vendas[0];
    assert.equal(v.forma_pagamento, 'dinheiro');
    assert.equal(v.recebido_centavos, 6000);
    assert.equal(v.troco_centavos, 500);
  }));

// ORIGEM: resposta do usuário (B13: concluído não volta a Marcado).
test('B13: agendamento concluído não oferece mais "Concluir" nem "Cancelar"', () =>
  com(dados({ ...base(), agendamentos: [{ ...banhoDoRex(), status: 'concluido' }] }), async (s) => {
    await acionar(s.page, 'Agenda');
    const l = linha(s.page, 'Rex').first();
    await l.waitFor();
    await l.getByText('Concluído').first().waitFor();
    assert.equal(await acao(l, 'Concluir').count(), 0);
    assert.equal(await acao(l, 'Cancelar').count(), 0);
  }));

// ORIGEM: resposta do usuário (B13).
test('B13: cancelar agendamento marcado muda para Cancelado e não gera venda', () =>
  com(dados({ ...base(), agendamentos: [banhoDoRex()] }), async (s) => {
    const { page } = s;
    await acionar(page, 'Agenda');
    await acionar(linha(page, 'Rex').first(), 'Cancelar');
    await ve(page, 'Agendamento cancelado');
    const d = s.ler();
    assert.equal(d.agendamentos[0].status, 'cancelado');
    assert.equal(d.vendas.length, 0);
    await acionar(page, 'Agenda');
    await linha(page, 'Rex').filter({ hasText: 'Cancelado' }).first().waitFor();
  }));
