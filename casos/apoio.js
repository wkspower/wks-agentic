// Apoio dos casos: inicia o sistema com um arquivo de dados próprio,
// abre um navegador de verdade e oferece ações pelo que o usuário vê.
// Não há regra de negócio aqui; as regras estão nos arquivos *.caso.js.
const { spawn } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const net = require('node:net');
const { chromium } = require('playwright');

const SISTEMA = path.resolve(process.env.SISTEMA || path.join(__dirname, '..', 'sistema'));
const TIPOS = ['clientes', 'pets', 'produtos', 'vendas', 'agendamentos'];

function portaLivre() {
  return new Promise((resolve, reject) => {
    const s = net.createServer();
    s.on('error', reject);
    s.listen(0, '127.0.0.1', () => {
      const p = s.address().port;
      s.close(() => resolve(p));
    });
  });
}

// Monta um arquivo de dados no formato fixo, calculando proximo_id.
function dados(parcial = {}) {
  const d = { versao: 1, clientes: [], pets: [], produtos: [], vendas: [], agendamentos: [], ...parcial };
  if (!d.proximo_id) {
    d.proximo_id = {};
    for (const t of TIPOS) d.proximo_id[t] = Math.max(0, ...d[t].map((x) => x.id)) + 1;
  }
  return d;
}

function venda(campos) {
  const itens = campos.itens || [
    { produto_id: null, descricao: 'Avulso', preco_unitario_centavos: campos.total_centavos, quantidade: 1 },
  ];
  const subtotal = itens.reduce((s, i) => s + i.preco_unitario_centavos * i.quantidade, 0);
  const forma = campos.forma_pagamento || 'pix';
  return {
    data: hoje(),
    hora: '09:00',
    cliente_id: null,
    origem: 'balcao',
    agendamento_id: null,
    itens,
    subtotal_centavos: subtotal,
    desconto_centavos: 0,
    total_centavos: subtotal,
    forma_pagamento: forma,
    recebido_centavos: forma === 'dinheiro' ? subtotal : null,
    troco_centavos: forma === 'dinheiro' ? 0 : null,
    status: 'finalizada',
    cancelamento: null,
    ...campos,
  };
}

function iso(d) {
  const p = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
}
function hoje() {
  return iso(new Date());
}
function diasAtras(n) {
  const d = new Date();
  d.setDate(d.getDate() - n);
  return iso(d);
}
// Próxima data (depois de hoje) que cai no dia da semana pedido (0 = domingo).
function proximo(diaDaSemana) {
  const d = new Date();
  do d.setDate(d.getDate() + 1);
  while (d.getDay() !== diaDaSemana);
  return iso(d);
}

async function abrir(inicial) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'caso-'));
  const arquivo = path.join(dir, 'petshop.json');
  if (inicial) fs.writeFileSync(arquivo, JSON.stringify(inicial, null, 2));
  const porta = await portaLivre();
  const proc = spawn('npm', ['start', '--silent'], {
    cwd: SISTEMA,
    env: { ...process.env, PORTA: String(porta), ARQUIVO_DADOS: arquivo },
    stdio: 'ignore',
    detached: true,
  });
  let saiu = false;
  proc.on('exit', () => (saiu = true));
  proc.on('error', () => (saiu = true));
  const base = `http://127.0.0.1:${porta}/`;
  const limite = Date.now() + 15000;
  for (;;) {
    try {
      await fetch(base);
      break;
    } catch {
      if (saiu || Date.now() > limite) {
        try { process.kill(-proc.pid); } catch {}
        throw new Error(`o sistema em ${SISTEMA} não respondeu em ${base} (npm start)`);
      }
      await new Promise((r) => setTimeout(r, 100));
    }
  }
  const navegador = await chromium.launch();
  const page = await navegador.newPage();
  page.setDefaultTimeout(5000);
  page.on('dialog', (d) => d.accept());
  await page.goto(base);
  return {
    page,
    base,
    arquivo,
    existe: () => fs.existsSync(arquivo),
    ler: () => JSON.parse(fs.readFileSync(arquivo, 'utf8')),
    bytes: () => fs.readFileSync(arquivo),
    async fechar() {
      await navegador.close();
      try { process.kill(-proc.pid); } catch {}
      fs.rmSync(dir, { recursive: true, force: true });
    },
  };
}

// Roda um caso com o sistema aberto e sempre fecha no fim.
async function com(inicial, fn) {
  const s = await abrir(inicial);
  try {
    await fn(s);
  } finally {
    await s.fechar();
  }
}

function acao(alvo, nome) {
  return alvo
    .getByRole('button', { name: nome, exact: true })
    .or(alvo.getByRole('link', { name: nome, exact: true }));
}
async function acionar(alvo, nome) {
  await acao(alvo, nome).first().click();
}
async function preencher(page, rotulo, valor) {
  await page.getByLabel(rotulo, { exact: true }).fill(valor);
}
// Escolhe num <select> a opção de texto igual ao pedido ou, se não houver, a que o contém.
async function escolher(page, rotulo, texto) {
  const sel = page.getByLabel(rotulo, { exact: true });
  await sel.waitFor();
  const valor = await sel.evaluate((el, t) => {
    const limpa = (s) => s.replace(/\s+/g, ' ').trim();
    const ops = [...el.options];
    const o = ops.find((x) => limpa(x.text) === t) || ops.find((x) => limpa(x.text).includes(t));
    if (!o) throw new Error(`sem opção "${t}" em: ${ops.map((x) => limpa(x.text)).join(' | ')}`);
    return o.value;
  }, texto);
  await sel.selectOption(valor);
}
async function ve(page, texto) {
  try {
    await page.getByText(texto).first().waitFor({ state: 'visible' });
  } catch {
    const corpo = (await page.locator('body').innerText()).replace(/\s+/g, ' ').slice(0, 600);
    throw new Error(`esperava ver "${texto}". A página mostra: ${corpo}`);
  }
}
async function aparece(page, texto, ms = 1000) {
  try {
    await page.getByText(texto).first().waitFor({ state: 'visible', timeout: ms });
    return true;
  } catch {
    return false;
  }
}
function linha(page, texto) {
  return page.getByRole('row').filter({ hasText: texto });
}

// Espera até não haver nenhuma linha com o texto (a página pode estar trocando).
async function semLinha(page, texto) {
  const fim = Date.now() + 5000;
  while ((await linha(page, texto).count()) > 0) {
    if (Date.now() > fim) throw new Error(`ainda há linha com "${texto}"`);
    await new Promise((r) => setTimeout(r, 100));
  }
}

async function vender(page, { itens, cliente, desconto, forma = 'Pix', recebido }) {
  await acionar(page, 'Vendas');
  await acionar(page, 'Nova venda');
  if (cliente) await escolher(page, 'Cliente', cliente);
  for (const [produto, quantidade] of itens) {
    await escolher(page, 'Produto', produto);
    await preencher(page, 'Quantidade', String(quantidade));
    await acionar(page, 'Adicionar item');
  }
  if (desconto) await preencher(page, 'Desconto', desconto);
  await escolher(page, 'Forma de pagamento', forma);
  if (recebido) await preencher(page, 'Valor recebido', recebido);
  await acionar(page, 'Finalizar venda');
}

async function agendar(page, { pet, servico, data, hora }) {
  await acionar(page, 'Agenda');
  await acionar(page, 'Novo agendamento');
  await escolher(page, 'Pet', pet);
  await escolher(page, 'Serviço', servico);
  await preencher(page, 'Data', data);
  await preencher(page, 'Hora', hora);
  await acionar(page, 'Agendar');
}

module.exports = {
  SISTEMA, dados, venda, hoje, diasAtras, proximo, abrir, com,
  acao, acionar, preencher, escolher, ve, aparece, linha, semLinha, vender, agendar,
};
