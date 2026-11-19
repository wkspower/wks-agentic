// Casos nascidos da segunda rodada: diferenças entre as duas construções
// independentes (D) e coincidências que nenhum caso decidia (C).
// ORIGEM de todos: resposta do usuário em 2026-11-19 ("aceito suas
// recomendações"), salvo onde está marcado SUPOSIÇÃO.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const {
  dados, venda, proximo, com, acionar, preencher, escolher, ve, linha, semLinha, agendar,
} = require('./apoio');

const SEG = proximo(1);
const segundaPassada = (() => {
  const d = new Date(`${SEG}T12:00:00`);
  d.setDate(d.getDate() - 14);
  const p = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
})();
const maria = { id: 1, nome: 'Maria Silva', telefone: '11999990001', ativo: true };
const rex = { id: 1, nome: 'Rex', cliente_id: 1, especie: 'cao', porte: 'M', ativo: true };
const mimi = { id: 2, nome: 'Mimi', cliente_id: 1, especie: 'gato', porte: 'P', ativo: true };
const racao = { id: 1, nome: 'Ração 1kg', preco_centavos: 4500, estoque: 10 };
const banho = (x = {}) => ({
  id: 1, pet_id: 1, servico: 'banho', data: SEG, hora_inicio: '10:00', hora_fim: '11:00',
  preco_centavos: 5500, status: 'marcado', venda_id: null, ...x,
});
const vendaRacao = () => venda({
  id: 1, itens: [{ produto_id: 1, descricao: 'Ração 1kg', preco_unitario_centavos: 4500, quantidade: 2 }],
});

async function produto(page, nome, preco, estoque = '1') {
  await acionar(page, 'Produtos');
  await acionar(page, 'Novo produto');
  await preencher(page, 'Nome', nome);
  await preencher(page, 'Preço', preco);
  await preencher(page, 'Estoque', estoque);
  await acionar(page, 'Salvar');
}
async function cliente(page, nome, telefone) {
  await acionar(page, 'Clientes');
  await acionar(page, 'Novo cliente');
  await preencher(page, 'Nome', nome);
  await preencher(page, 'Telefone', telefone);
  await acionar(page, 'Salvar');
}
async function cancelarVenda(page, total) {
  await acionar(page, 'Vendas');
  await acionar(linha(page, total).first(), 'Cancelar');
  await preencher(page, 'Motivo', 'erro');
  await acionar(page, 'Confirmar cancelamento');
}

// ---- D1: teto de preço (R$ 99.999,99)
test('D1: preço 99.999,99 é aceito', () =>
  com(dados(), async (s) => {
    await produto(s.page, 'Caro', '99.999,99');
    await ve(s.page, 'Produto salvo');
    assert.equal(s.ler().produtos[0].preco_centavos, 9999999);
  }));
for (const v of ['100.000,00', '99999999999']) {
  test(`D1: preço ${v} é recusado com "Valor inválido"`, () =>
    com(dados(), async (s) => {
      await produto(s.page, 'Caro', v);
      await ve(s.page, 'Valor inválido');
      assert.equal(s.ler().produtos.length, 0);
    }));
}

// ---- D2: nome de produto repetido
test('D2: segundo produto com o mesmo nome é recusado', () =>
  com(dados({ produtos: [racao] }), async (s) => {
    await produto(s.page, 'Ração 1kg', '1,00');
    await ve(s.page, 'Já existe um produto com esse nome');
    assert.equal(s.ler().produtos.length, 1);
  }));
// SUPOSIÇÃO minha: editar um produto mantendo o próprio nome não conta como repetição.
test('D2: editar o preço de um produto mantendo o nome é aceito', () =>
  com(dados({ produtos: [racao] }), async (s) => {
    const { page } = s;
    await acionar(page, 'Produtos');
    await acionar(linha(page, 'Ração 1kg').first(), 'Editar');
    await preencher(page, 'Preço', '46,00');
    await acionar(page, 'Salvar');
    await ve(page, 'Produto salvo');
    assert.equal(s.ler().produtos[0].preco_centavos, 4600);
  }));

// ---- D3: inativar cliente inativa os pets dele
test('D3: inativar cliente inativa o pet, que some da lista de pets e da agenda', () =>
  com(dados({
    clientes: [maria, { id: 2, nome: 'João Souza', telefone: '11999990002', ativo: true }],
    pets: [rex, { ...mimi, cliente_id: 2 }],
  }), async (s) => {
    const { page } = s;
    await acionar(page, 'Clientes');
    await acionar(linha(page, 'Maria Silva').first(), 'Inativar');
    await ve(page, 'Cliente inativado');
    const d = s.ler();
    assert.equal(d.pets.find((p) => p.id === 1).ativo, false);
    assert.equal(d.pets.find((p) => p.id === 2).ativo, true);
    await acionar(page, 'Pets');
    await linha(page, 'Mimi').first().waitFor();
    await semLinha(page, 'Rex');
    await acionar(page, 'Agenda');
    await acionar(page, 'Novo agendamento');
    const sel = page.getByLabel('Pet', { exact: true });
    await sel.waitFor();
    const ops = await sel.evaluate((el) => [...el.options].map((o) => o.text));
    assert.ok(ops.some((o) => o.includes('Mimi')));
    assert.ok(!ops.some((o) => o.includes('Rex')));
  }));

// ---- D8: redação das mensagens de erro que faltava fixar
test('D8: telefone sem dígitos é recusado com "Telefone inválido"', () =>
  com(dados(), async (s) => {
    await cliente(s.page, 'Ana', 'abc');
    await ve(s.page, 'Telefone inválido');
    assert.equal(s.ler().clientes.length, 0);
  }));
for (const [falta, msg] of [['Espécie', 'Espécie é obrigatória'], ['Porte', 'Porte é obrigatório']]) {
  test(`D8: pet sem ${falta} é recusado com "${msg}"`, () =>
    com(dados({ clientes: [maria] }), async (s) => {
      const { page } = s;
      await acionar(page, 'Pets');
      await acionar(page, 'Novo pet');
      await preencher(page, 'Nome', 'Bob');
      await escolher(page, 'Dono', 'Maria Silva');
      if (falta !== 'Espécie') await escolher(page, 'Espécie', 'Cão');
      if (falta !== 'Porte') await escolher(page, 'Porte', 'P');
      await acionar(page, 'Salvar');
      await ve(page, msg);
      assert.equal(s.ler().pets.length, 0);
    }));
}
test('D8: quantidade 0 é recusada com "Quantidade inválida"', () =>
  com(dados({ produtos: [racao] }), async (s) => {
    const { page } = s;
    await acionar(page, 'Vendas');
    await acionar(page, 'Nova venda');
    await escolher(page, 'Produto', 'Ração 1kg');
    await preencher(page, 'Quantidade', '0');
    await acionar(page, 'Adicionar item');
    await ve(page, 'Quantidade inválida');
  }));
test('D8: adicionar item sem produto mostra "Escolha um produto"', () =>
  com(dados({ produtos: [racao] }), async (s) => {
    const { page } = s;
    await acionar(page, 'Vendas');
    await acionar(page, 'Nova venda');
    await preencher(page, 'Quantidade', '1');
    await acionar(page, 'Adicionar item');
    await ve(page, 'Escolha um produto');
  }));
test('D8: finalizar sem itens é recusado com "Adicione pelo menos um item"', () =>
  com(dados({ produtos: [racao] }), async (s) => {
    const { page } = s;
    await acionar(page, 'Vendas');
    await acionar(page, 'Nova venda');
    await escolher(page, 'Forma de pagamento', 'Pix');
    await acionar(page, 'Finalizar venda');
    await ve(page, 'Adicione pelo menos um item');
    assert.equal(s.ler().vendas.length, 0);
  }));
test('D8: finalizar sem forma de pagamento é recusado com "Forma de pagamento é obrigatória"', () =>
  com(dados({ produtos: [racao] }), async (s) => {
    const { page } = s;
    await acionar(page, 'Vendas');
    await acionar(page, 'Nova venda');
    await escolher(page, 'Produto', 'Ração 1kg');
    await preencher(page, 'Quantidade', '1');
    await acionar(page, 'Adicionar item');
    await acionar(page, 'Finalizar venda');
    await ve(page, 'Forma de pagamento é obrigatória');
    assert.equal(s.ler().vendas.length, 0);
  }));

// ---- C1: o serviço precisa terminar até as 18:00
const agenda = (ag = []) => dados({ clientes: [maria], pets: [rex, mimi], agendamentos: ag });
test('C1: tosa às 17:00 (terminaria 18:30) é recusada', () =>
  com(agenda(), async (s) => {
    await agendar(s.page, { pet: 'Rex', servico: 'Tosa', data: SEG, hora: '17:00' });
    await ve(s.page, 'Fora do horário de funcionamento');
    assert.equal(s.ler().agendamentos.length, 0);
  }));
test('C1: banho às 17:00 (termina 18:00) é aceito', () =>
  com(agenda(), async (s) => {
    await agendar(s.page, { pet: 'Rex', servico: 'Banho', data: SEG, hora: '17:00' });
    await ve(s.page, 'Agendamento marcado');
    assert.equal(s.ler().agendamentos[0].hora_fim, '18:00');
  }));

// ---- C2: data passada (D8 fixa a redação)
test('C2: agendar em data passada é recusado com "Data já passou"', () =>
  com(agenda(), async (s) => {
    await agendar(s.page, { pet: 'Rex', servico: 'Banho', data: segundaPassada, hora: '10:00' });
    await ve(s.page, 'Data já passou');
    assert.equal(s.ler().agendamentos.length, 0);
  }));

// ---- C3: cancelado libera o horário; concluído continua ocupando
test('C3: horário de agendamento cancelado pode ser marcado de novo', () =>
  com(agenda([banho({ status: 'cancelado' })]), async (s) => {
    await agendar(s.page, { pet: 'Mimi', servico: 'Banho', data: SEG, hora: '10:00' });
    await ve(s.page, 'Agendamento marcado');
    assert.equal(s.ler().agendamentos.length, 2);
  }));
test('C3: horário de agendamento concluído continua ocupado', () =>
  com(agenda([banho({ status: 'concluido' })]), async (s) => {
    await agendar(s.page, { pet: 'Mimi', servico: 'Banho', data: SEG, hora: '10:00' });
    await ve(s.page, 'Horário ocupado');
    assert.equal(s.ler().agendamentos.length, 1);
  }));
test('C3: horário encostado no fim de outro (11:00 após 10:00–11:00) é aceito', () =>
  com(agenda([banho()]), async (s) => {
    await agendar(s.page, { pet: 'Mimi', servico: 'Banho', data: SEG, hora: '11:00' });
    await ve(s.page, 'Agendamento marcado');
  }));

// ---- C5: produto vendido pode ser apagado; a venda fica
test('C5: produto já vendido pode ser apagado e a venda continua igual', () =>
  com(dados({ produtos: [racao], vendas: [vendaRacao()] }), async (s) => {
    const { page } = s;
    const antes = s.ler().vendas;
    await acionar(page, 'Produtos');
    await acionar(linha(page, 'Ração 1kg').first(), 'Apagar');
    await ve(page, 'Produto apagado');
    const d = s.ler();
    assert.equal(d.produtos.length, 0);
    assert.deepEqual(d.vendas, antes);
  }));
test('C5: cancelar venda de produto apagado funciona e não recria o produto', () =>
  com(dados({
    produtos: [], vendas: [vendaRacao()],
    proximo_id: { clientes: 1, pets: 1, produtos: 2, vendas: 2, agendamentos: 1 },
  }), async (s) => {
    await cancelarVenda(s.page, 'R$ 90,00');
    await ve(s.page, 'Venda cancelada');
    const d = s.ler();
    assert.equal(d.vendas[0].status, 'cancelada');
    assert.equal(d.produtos.length, 0);
  }));

// ---- C6: cancelar a venda de um serviço não mexe no agendamento
test('C6: cancelar venda vinda da agenda deixa o agendamento como concluído', () =>
  com(dados({
    clientes: [maria], pets: [rex],
    agendamentos: [banho({ status: 'concluido', venda_id: 1 })],
    vendas: [venda({
      id: 1, cliente_id: 1, origem: 'agendamento', agendamento_id: 1,
      itens: [{ produto_id: null, descricao: 'Banho', preco_unitario_centavos: 5500, quantidade: 1 }],
    })],
  }), async (s) => {
    await cancelarVenda(s.page, 'R$ 55,00');
    await ve(s.page, 'Venda cancelada');
    const d = s.ler();
    assert.equal(d.vendas[0].status, 'cancelada');
    assert.equal(d.agendamentos[0].status, 'concluido');
  }));

// ---- C7: telefone guardado só com dígitos
test('C7: "(11) 99999-0001" é guardado como "11999990001"', () =>
  com(dados(), async (s) => {
    await cliente(s.page, 'Ana', '(11) 99999-0001');
    await ve(s.page, 'Cliente salvo');
    assert.equal(s.ler().clientes[0].telefone, '11999990001');
  }));
test('C7: o mesmo telefone com pontuação diferente conta como repetido', () =>
  com(dados({ clientes: [maria] }), async (s) => {
    await cliente(s.page, 'Ana', '(11) 99999-0001');
    await ve(s.page, 'Telefone já cadastrado para Maria Silva');
    assert.equal(s.ler().clientes.length, 1);
  }));
test('C7: telefone curto "123" é aceito', () =>
  com(dados(), async (s) => {
    await cliente(s.page, 'Ana', '123');
    await ve(s.page, 'Cliente salvo');
    assert.equal(s.ler().clientes[0].telefone, '123');
  }));

// ---- C10: formatos de dinheiro aceitos
for (const [digitado, centavos] of [['12.50', 1250], ['1.234,56', 123456], ['R$ 12,50', 1250], ['1234', 123400]]) {
  test(`C10: preço "${digitado}" vale ${centavos} centavos`, () =>
    com(dados(), async (s) => {
      await produto(s.page, 'X', digitado);
      await ve(s.page, 'Produto salvo');
      assert.equal(s.ler().produtos[0].preco_centavos, centavos);
    }));
}
test('C10: preço com três casas decimais ("12,555") é recusado', () =>
  com(dados(), async (s) => {
    await produto(s.page, 'X', '12,555');
    await ve(s.page, 'Valor inválido');
    assert.equal(s.ler().produtos.length, 0);
  }));
