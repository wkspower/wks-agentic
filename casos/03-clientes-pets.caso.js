// Clientes e pets: obrigatórios, telefone único, dono, apagar e inativar.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const { dados, venda, proximo, com, acionar, preencher, escolher, ve, linha, semLinha } = require('./apoio');

const maria = { id: 1, nome: 'Maria Silva', telefone: '11999990001', ativo: true };
const joao = { id: 2, nome: 'João Souza', telefone: '11999990002', ativo: true };
const rex = { id: 1, nome: 'Rex', cliente_id: 1, especie: 'cao', porte: 'M', ativo: true };

async function novoCliente(page, nome, telefone) {
  await acionar(page, 'Clientes');
  await acionar(page, 'Novo cliente');
  await preencher(page, 'Nome', nome);
  await preencher(page, 'Telefone', telefone);
  await acionar(page, 'Salvar');
}

// ORIGEM: resposta do usuário (B8).
test('B8: cliente com nome e telefone é salvo e aparece na lista', () =>
  com(dados(), async (s) => {
    await novoCliente(s.page, 'Maria Silva', '11999990001');
    await ve(s.page, 'Cliente salvo');
    assert.deepEqual(s.ler().clientes, [maria]);
    await acionar(s.page, 'Clientes');
    await linha(s.page, 'Maria Silva').filter({ hasText: '11999990001' }).first().waitFor();
  }));

// ORIGEM: resposta do usuário (B8).
test('B8: cliente sem telefone é recusado', () =>
  com(dados(), async (s) => {
    await novoCliente(s.page, 'Maria Silva', '');
    await ve(s.page, 'Telefone é obrigatório');
    assert.equal(s.ler().clientes.length, 0);
  }));

// ORIGEM: resposta do usuário (B8).
test('B8: cliente sem nome é recusado', () =>
  com(dados(), async (s) => {
    await novoCliente(s.page, '', '11999990001');
    await ve(s.page, 'Nome é obrigatório');
    assert.equal(s.ler().clientes.length, 0);
  }));

// ORIGEM: resposta do usuário (B8).
test('B8: telefone repetido é recusado mostrando quem já usa', () =>
  com(dados({ clientes: [maria] }), async (s) => {
    await novoCliente(s.page, 'Outra Pessoa', '11999990001');
    await ve(s.page, 'Telefone já cadastrado para Maria Silva');
    assert.equal(s.ler().clientes.length, 1);
  }));

// ORIGEM: resposta do usuário (C: busca "acha por nome ou telefone").
test('C: a busca acha por parte do nome e por parte do telefone', () =>
  com(dados({ clientes: [maria, joao] }), async (s) => {
    const { page } = s;
    await acionar(page, 'Clientes');
    await preencher(page, 'Busca', 'Mari');
    await acionar(page, 'Buscar');
    await linha(page, 'Maria Silva').first().waitFor();
    await semLinha(page, 'João Souza');
    await preencher(page, 'Busca', '0002');
    await acionar(page, 'Buscar');
    await linha(page, 'João Souza').first().waitFor();
    await semLinha(page, 'Maria Silva');
  }));

// ORIGEM: resposta do usuário (B9).
test('B9: pet é salvo com dono, espécie e porte', () =>
  com(dados({ clientes: [maria] }), async (s) => {
    const { page } = s;
    await acionar(page, 'Pets');
    await acionar(page, 'Novo pet');
    await preencher(page, 'Nome', 'Rex');
    await escolher(page, 'Dono', 'Maria Silva');
    await escolher(page, 'Espécie', 'Cão');
    await escolher(page, 'Porte', 'M');
    await acionar(page, 'Salvar');
    await ve(page, 'Pet salvo');
    assert.deepEqual(s.ler().pets, [rex]);
    await acionar(page, 'Pets');
    await linha(page, 'Rex').filter({ hasText: 'Maria Silva' }).first().waitFor();
  }));

// ORIGEM: resposta do usuário (B9).
test('B9: pet sem dono é recusado', () =>
  com(dados({ clientes: [maria] }), async (s) => {
    const { page } = s;
    await acionar(page, 'Pets');
    await acionar(page, 'Novo pet');
    await preencher(page, 'Nome', 'Rex');
    await escolher(page, 'Espécie', 'Gato');
    await escolher(page, 'Porte', 'P');
    await acionar(page, 'Salvar');
    await ve(page, 'Dono é obrigatório');
    assert.equal(s.ler().pets.length, 0);
  }));

// ORIGEM: resposta do usuário (B10).
test('B10: cliente com venda não pode ser apagado', () =>
  com(dados({ clientes: [maria], vendas: [venda({ id: 1, cliente_id: 1, total_centavos: 4500 })] }), async (s) => {
    const { page } = s;
    await acionar(page, 'Clientes');
    await acionar(linha(page, 'Maria Silva').first(), 'Apagar');
    await ve(page, 'Cliente possui histórico e não pode ser apagado');
    assert.equal(s.ler().clientes.length, 1);
  }));

// ORIGEM: resposta do usuário (B10).
test('B10: inativar cliente tira da lista e mantém o histórico', () =>
  com(dados({ clientes: [maria, joao], vendas: [venda({ id: 1, cliente_id: 1, total_centavos: 4500 })] }), async (s) => {
    const { page } = s;
    await acionar(page, 'Clientes');
    await acionar(linha(page, 'Maria Silva').first(), 'Inativar');
    await ve(page, 'Cliente inativado');
    const d = s.ler();
    assert.equal(d.clientes.find((c) => c.id === 1).ativo, false);
    assert.equal(d.vendas.length, 1);
    await acionar(page, 'Clientes');
    await linha(page, 'João Souza').first().waitFor();
    await semLinha(page, 'Maria Silva');
    await preencher(page, 'Busca', 'Maria');
    await acionar(page, 'Buscar');
    await semLinha(page, 'Maria Silva');
    await acionar(page, 'Vendas');
    await linha(page, 'R$ 45,00').first().waitFor();
  }));

// ORIGEM: suposição minha (decorre do B10: só o histórico impede apagar).
test('B10: cliente sem histórico pode ser apagado', () =>
  com(dados({ clientes: [maria, joao] }), async (s) => {
    const { page } = s;
    await acionar(page, 'Clientes');
    await acionar(linha(page, 'João Souza').first(), 'Apagar');
    await ve(page, 'Cliente apagado');
    assert.deepEqual(s.ler().clientes.map((c) => c.id), [1]);
  }));

// ORIGEM: resposta do usuário (B10).
test('B10: pet com agendamento não pode ser apagado', () =>
  com(dados({
    clientes: [maria],
    pets: [rex],
    agendamentos: [{
      id: 1, pet_id: 1, servico: 'banho', data: proximo(1), hora_inicio: '10:00', hora_fim: '11:00',
      preco_centavos: 5500, status: 'marcado', venda_id: null,
    }],
  }), async (s) => {
    const { page } = s;
    await acionar(page, 'Pets');
    await acionar(linha(page, 'Rex').first(), 'Apagar');
    await ve(page, 'Pet possui histórico e não pode ser apagado');
    assert.equal(s.ler().pets.length, 1);
  }));
