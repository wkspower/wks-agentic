'use strict';
// Sistema do pet shop: servidor HTTP local, sem dependências externas.
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

const PORTA = Number(process.env.PORTA) || 3000;
const ARQUIVO = process.env.ARQUIVO_DADOS
  ? path.resolve(process.env.ARQUIVO_DADOS)
  : path.join(__dirname, 'dados', 'petshop.json');

const TIPOS = ['clientes', 'pets', 'produtos', 'vendas', 'agendamentos'];
const ESPECIES = { cao: 'Cão', gato: 'Gato', outro: 'Outro' };
const PORTES = ['P', 'M', 'G'];
const FORMAS = { dinheiro: 'Dinheiro', pix: 'Pix', cartao: 'Cartão' };
const SERVICOS = {
  banho: { nome: 'Banho', minutos: 60, precos: { P: 4000, M: 5500, G: 7500 } },
  tosa: { nome: 'Tosa', minutos: 90, precos: { P: 6000, M: 8000, G: 11000 } },
  banho_e_tosa: { nome: 'Banho e tosa', minutos: 120, precos: { P: 9000, M: 12000, G: 16000 } },
};
const SITUACAO_VENDA = { finalizada: 'Finalizada', cancelada: 'Cancelada' };
const SITUACAO_AGENDA = { marcado: 'Marcado', concluido: 'Concluído', cancelado: 'Cancelado' };
const ABRE = 8 * 60;
const FECHA = 18 * 60;

// ---------------------------------------------------------------- dados

class Recusa extends Error {
  constructor(mensagens) {
    const lista = Array.isArray(mensagens) ? mensagens : [mensagens];
    super(lista.join('; '));
    this.mensagens = lista;
  }
}

function carregar() {
  const vazio = { versao: 1, proximo_id: {}, clientes: [], pets: [], produtos: [], vendas: [], agendamentos: [] };
  let d = vazio;
  if (fs.existsSync(ARQUIVO)) {
    try {
      d = JSON.parse(fs.readFileSync(ARQUIVO, 'utf8'));
    } catch (e) {
      console.error(`Não foi possível ler ${ARQUIVO}: ${e.message}`);
      console.error('O sistema não vai iniciar para não gravar por cima desse arquivo.');
      process.exit(1);
    }
    if (!d || typeof d !== 'object' || Array.isArray(d)) {
      console.error(`${ARQUIVO} não tem o formato esperado.`);
      process.exit(1);
    }
  }
  if (d.versao === undefined) d.versao = 1;
  if (!d.proximo_id || typeof d.proximo_id !== 'object') d.proximo_id = {};
  for (const t of TIPOS) {
    if (!Array.isArray(d[t])) d[t] = [];
    const minimo = Math.max(0, ...d[t].map((x) => Number(x.id) || 0)) + 1;
    if (!Number.isInteger(d.proximo_id[t]) || d.proximo_id[t] < minimo) d.proximo_id[t] = minimo;
  }
  return d;
}

let db = carregar();

function gravar(d) {
  fs.mkdirSync(path.dirname(ARQUIVO), { recursive: true });
  const tmp = `${ARQUIVO}.${process.pid}.tmp`;
  fs.writeFileSync(tmp, JSON.stringify(d, null, 2) + '\n');
  fs.renameSync(tmp, ARQUIVO);
}

// Aplica uma alteração numa cópia; só grava e passa a valer se não houver recusa.
function alterar(fn) {
  const copia = structuredClone(db);
  const r = fn(copia);
  gravar(copia);
  db = copia;
  return r;
}

function novoId(d, tipo) {
  const id = d.proximo_id[tipo];
  d.proximo_id[tipo] = id + 1;
  return id;
}

const porId = (lista, id) => lista.find((x) => x.id === id);

// ---------------------------------------------------------------- utilidades

const p2 = (n) => String(n).padStart(2, '0');
function agora() {
  const d = new Date();
  return {
    data: `${d.getFullYear()}-${p2(d.getMonth() + 1)}-${p2(d.getDate())}`,
    hora: `${p2(d.getHours())}:${p2(d.getMinutes())}`,
  };
}
function dataValida(s) {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(s || '');
  if (!m) return null;
  const d = new Date(+m[1], +m[2] - 1, +m[3]);
  if (d.getFullYear() !== +m[1] || d.getMonth() !== +m[2] - 1 || d.getDate() !== +m[3]) return null;
  return d;
}
function minutos(s) {
  const m = /^([01]\d|2[0-3]):([0-5]\d)(:\d\d)?$/.exec(s || '');
  return m ? +m[1] * 60 + +m[2] : null;
}
const horaDe = (min) => `${p2(Math.floor(min / 60))}:${p2(min % 60)}`;
const DIAS = ['dom', 'seg', 'ter', 'qua', 'qui', 'sex', 'sáb'];
function dataBR(s) {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(s || '');
  return m ? `${m[3]}/${m[2]}/${m[1]}` : String(s || '');
}
function dataComDia(s) {
  const d = dataValida(s);
  return d ? `${dataBR(s)} (${DIAS[d.getDay()]})` : dataBR(s);
}

function reais(centavos) {
  const c = Math.abs(Math.round(Number(centavos) || 0));
  const inteiro = String(Math.floor(c / 100)).replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  return `${centavos < 0 ? '-' : ''}R$ ${inteiro},${p2(c % 100)}`;
}
// Para preencher campos: 1250 -> "12,50"
function reaisCampo(centavos) {
  return `${Math.floor(centavos / 100)},${p2(centavos % 100)}`;
}
// Devolve centavos, null se vazio, NaN se inválido.
function lerDinheiro(texto) {
  const t = String(texto || '').trim().replace(/^R\$/i, '').replace(/\s/g, '');
  if (!t) return null;
  let inteiro, fracao;
  let m = /^(\d{1,3}(?:\.\d{3})+)(?:,(\d{1,2}))?$/.exec(t);
  if (m) {
    inteiro = m[1].replace(/\./g, '');
    fracao = m[2] || '';
  } else {
    m = /^(\d+)(?:[.,](\d{1,2}))?$/.exec(t);
    if (!m) return NaN;
    inteiro = m[1];
    fracao = m[2] || '';
  }
  if (inteiro.length > 9) return NaN;
  return Number(inteiro) * 100 + Number(fracao.padEnd(2, '0'));
}

function esc(v) {
  return String(v ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}
const semAcento = (s) => String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
const soDigitos = (s) => String(s || '').replace(/\D/g, '');
const texto = (v) => String(v ?? '').replace(/\s+/g, ' ').trim();

// Mensagens que aparecem na página seguinte a um redirecionamento.
const avisos = new Map();
function guardarAviso(tipo, mensagens) {
  const chave = crypto.randomBytes(8).toString('hex');
  avisos.set(chave, { tipo, mensagens: Array.isArray(mensagens) ? mensagens : [mensagens] });
  if (avisos.size > 200) avisos.delete(avisos.keys().next().value);
  return chave;
}

// ---------------------------------------------------------------- HTML

const CSS = `
*{box-sizing:border-box}
body{margin:0;font:16px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;color:#1f2933;background:#f4f6f8}
header{background:#14532d;color:#fff}
header .dentro{max-width:1000px;margin:0 auto;padding:10px 16px;display:flex;flex-wrap:wrap;gap:6px 22px;align-items:center}
header .marca{font-weight:700;font-size:18px;color:#fff;text-decoration:none}
nav{display:flex;flex-wrap:wrap;gap:4px}
nav a{color:#e7f5ec;text-decoration:none;padding:6px 10px;border-radius:6px}
nav a:hover,nav a.atual{background:#166534;color:#fff}
main{max-width:1000px;margin:0 auto;padding:18px 16px 60px}
h1{font-size:24px;margin:6px 0 14px}
h2{font-size:18px;margin:22px 0 8px}
table{width:100%;border-collapse:collapse;background:#fff;border:1px solid #d9dee3;border-radius:8px}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid #e6e9ec;vertical-align:middle}
th{background:#eef1f4;font-size:14px}
tr:last-child td{border-bottom:0}
td.num,th.num{text-align:right;white-space:nowrap}
td.acoes{white-space:nowrap;text-align:right}
td.acoes form{display:inline}
.rolagem{overflow-x:auto}
.botao,button{display:inline-block;font:inherit;cursor:pointer;border:1px solid #166534;background:#166534;color:#fff;padding:7px 14px;border-radius:6px;text-decoration:none}
.botao:hover,button:hover{background:#14532d}
.botao.leve,button.leve{background:#fff;color:#14532d;border-color:#9fb8a8;padding:4px 10px;font-size:14px}
.botao.leve:hover,button.leve:hover{background:#eef6f0}
button.perigo,.botao.perigo{color:#9b1c1c;border-color:#e0b4b4;background:#fff;padding:4px 10px;font-size:14px}
button.perigo:hover,.botao.perigo:hover{background:#fdf0f0}
.barra{display:flex;flex-wrap:wrap;gap:10px;align-items:end;justify-content:space-between;margin-bottom:14px}
.barra form{display:flex;gap:8px;align-items:end;flex-wrap:wrap}
.cartao{background:#fff;border:1px solid #d9dee3;border-radius:8px;padding:16px;max-width:560px}
.cartao.largo{max-width:none}
.campo{margin-bottom:12px}
.linha-campos{display:flex;flex-wrap:wrap;gap:12px;align-items:end}
label{display:block;font-size:14px;font-weight:600;margin-bottom:3px}
input,select{font:inherit;padding:7px 9px;border:1px solid #b8c0c8;border-radius:6px;background:#fff;width:100%;max-width:340px}
input.curto{max-width:120px}
.msg{padding:10px 14px;border-radius:6px;margin:0 0 10px;font-weight:600}
.msg.ok{background:#e3f6e8;border:1px solid #9bd3aa;color:#14532d}
.msg.erro{background:#fde8e8;border:1px solid #f0b0b0;color:#8a1c1c}
.total{font-size:22px;font-weight:700;margin:14px 0}
.resumo p{font-size:18px;margin:4px 0}
.resumo p.total{font-size:22px;border-top:1px solid #d9dee3;padding-top:8px}
.vazio{color:#66727e;background:#fff;border:1px dashed #c5ccd3;border-radius:8px;padding:16px}
.etiqueta{display:inline-block;padding:1px 9px;border-radius:999px;font-size:13px;font-weight:600;background:#e6e9ec}
.etiqueta.bom{background:#dcf3e2;color:#14532d}.etiqueta.ruim{background:#fbe1e1;color:#8a1c1c}.etiqueta.espera{background:#fff1cc;color:#6b4e00}
.suave{color:#66727e;font-size:14px}
.rodape-form{display:flex;gap:10px;align-items:center;margin-top:6px}
`;

const MENU = [
  ['/clientes', 'Clientes'], ['/pets', 'Pets'], ['/produtos', 'Produtos'],
  ['/agenda', 'Agenda'], ['/vendas', 'Vendas'], ['/fechamento', 'Fechamento do dia'],
];

function pagina(titulo, corpo, { aviso, erros, secao } = {}) {
  let msgs = '';
  if (aviso) {
    const classe = aviso.tipo === 'erro' ? 'erro' : 'ok';
    msgs += aviso.mensagens.map((m) => `<p class="msg ${classe}" role="${classe === 'erro' ? 'alert' : 'status'}">${esc(m)}</p>`).join('');
  }
  if (erros && erros.length) msgs += erros.map((m) => `<p class="msg erro" role="alert">${esc(m)}</p>`).join('');
  const menu = MENU.map(([h, t]) => `<a href="${h}"${secao === h ? ' class="atual"' : ''}>${t}</a>`).join('');
  return `<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(titulo)} · Pet shop</title>
<style>${CSS}</style>
</head>
<body>
<header><div class="dentro"><a class="marca" href="/">Pet shop</a><nav>${menu}</nav></div></header>
<main>
${msgs}
<h1>${esc(titulo)}</h1>
${corpo}
</main>
</body>
</html>`;
}

function campo(rotulo, nome, valor = '', extra = '') {
  return `<div class="campo"><label for="c-${nome}">${rotulo}</label><input id="c-${nome}" name="${nome}" value="${esc(valor)}" autocomplete="off" ${extra}></div>`;
}
// opcoes: [[valor, texto], ...]
function escolha(rotulo, nome, opcoes, atual = '', { vazia = true } = {}) {
  const ops = (vazia ? [['', '']] : []).concat(opcoes)
    .map(([v, t]) => `<option value="${esc(v)}"${String(v) === String(atual ?? '') ? ' selected' : ''}>${esc(t)}</option>`).join('');
  return `<div class="campo"><label for="c-${nome}">${rotulo}</label><select id="c-${nome}" name="${nome}">${ops}</select></div>`;
}
function tabela(cabecalho, linhas, vazio) {
  if (!linhas.length) return `<p class="vazio">${esc(vazio)}</p>`;
  return `<div class="rolagem"><table><thead><tr>${cabecalho.join('')}</tr></thead><tbody>${linhas.join('')}</tbody></table></div>`;
}
function botaoLinha(url, rotulo, { classe = 'leve', confirma } = {}) {
  const c = confirma ? ` onsubmit="return confirm('${esc(confirma)}')"` : '';
  return `<form method="post" action="${url}"${c}><button class="${classe}">${rotulo}</button></form>`;
}
const etiquetaVenda = (s) => `<span class="etiqueta ${s === 'finalizada' ? 'bom' : 'ruim'}">${SITUACAO_VENDA[s] || esc(s)}</span>`;
const etiquetaAgenda = (s) => `<span class="etiqueta ${s === 'concluido' ? 'bom' : s === 'cancelado' ? 'ruim' : 'espera'}">${SITUACAO_AGENDA[s] || esc(s)}</span>`;

const opcoesClientes = () => db.clientes.filter((c) => c.ativo)
  .sort((a, b) => a.nome.localeCompare(b.nome, 'pt-BR'))
  .map((c) => [c.id, `${c.nome} — ${c.telefone}`]);
const nomeCliente = (id) => (id == null ? '' : (porId(db.clientes, id) || {}).nome || `Cliente nº ${id}`);
const nomePet = (id) => (porId(db.pets, id) || {}).nome || `Pet nº ${id}`;
const opcoesFormas = () => Object.entries(FORMAS);

const SCRIPT_RECEBIDO = `<script>
(function(){var f=document.getElementById('c-forma'),b=document.getElementById('bloco-recebido');
if(!f||!b)return;function v(){b.style.display=f.value==='dinheiro'?'':'none'}f.addEventListener('change',v);v();})();
</script>`;
function camposPagamento(v) {
  return `<div class="linha-campos">${escolha('Forma de pagamento', 'forma', opcoesFormas(), v.forma)}
<div id="bloco-recebido">${campo('Valor recebido', 'recebido', v.recebido, 'inputmode="decimal" class="curto" placeholder="0,00"')}</div></div>`;
}

// Valida forma de pagamento e valor recebido. Devolve os campos da venda.
function pagamento(v, total, erros) {
  const forma = v.forma;
  if (!FORMAS[forma]) {
    erros.push('Forma de pagamento é obrigatória');
    return null;
  }
  if (forma !== 'dinheiro') return { forma_pagamento: forma, recebido_centavos: null, troco_centavos: null };
  const recebido = lerDinheiro(v.recebido);
  if (Number.isNaN(recebido)) {
    erros.push('Valor inválido');
    return null;
  }
  if ((recebido || 0) < total) {
    erros.push('Valor recebido insuficiente');
    return null;
  }
  return { forma_pagamento: forma, recebido_centavos: recebido || 0, troco_centavos: (recebido || 0) - total };
}

// ---------------------------------------------------------------- clientes

function temHistoricoCliente(d, id) {
  const pets = d.pets.filter((p) => p.cliente_id === id).map((p) => p.id);
  return d.vendas.some((v) => v.cliente_id === id) || d.agendamentos.some((a) => pets.includes(a.pet_id));
}

function listaClientes(q) {
  const busca = texto(q.get('busca'));
  let lista = db.clientes.filter((c) => c.ativo);
  if (busca) {
    const n = semAcento(busca);
    const dig = soDigitos(busca);
    lista = lista.filter((c) => semAcento(c.nome).includes(n) || c.telefone.includes(busca)
      || (dig && soDigitos(c.telefone).includes(dig)));
  }
  lista.sort((a, b) => a.nome.localeCompare(b.nome, 'pt-BR'));
  const linhas = lista.map((c) => {
    const pets = db.pets.filter((p) => p.cliente_id === c.id && p.ativo).map((p) => p.nome).join(', ');
    return `<tr><td>${esc(c.nome)}</td><td>${esc(c.telefone)}</td><td>${esc(pets) || '<span class="suave">—</span>'}</td>
<td class="acoes"><a class="botao leve" href="/clientes/${c.id}/editar">Editar</a>
${botaoLinha(`/clientes/${c.id}/inativar`, 'Inativar', { confirma: 'Inativar este cliente? Ele e os pets dele saem das listas; o histórico continua.' })}
${botaoLinha(`/clientes/${c.id}/apagar`, 'Apagar', { classe: 'perigo', confirma: 'Apagar este cliente de vez?' })}</td></tr>`;
  });
  const inativos = db.clientes.filter((c) => !c.ativo).length;
  return `<div class="barra">
<form method="get" action="/clientes"><div><label for="c-busca">Busca</label><input id="c-busca" name="busca" value="${esc(busca)}" placeholder="nome ou telefone"></div><button>Buscar</button>${busca ? '<a class="botao leve" href="/clientes">Limpar</a>' : ''}</form>
<a class="botao" href="/clientes/novo">Novo cliente</a></div>
${tabela(['<th>Nome</th>', '<th>Telefone</th>', '<th>Pets</th>', '<th></th>'], linhas, busca ? 'Nenhum cliente encontrado.' : 'Nenhum cliente cadastrado.')}
${inativos ? `<p class="suave"><a href="/clientes/inativos">Ver clientes inativos (${inativos})</a></p>` : ''}`;
}

function listaClientesInativos() {
  const linhas = db.clientes.filter((c) => !c.ativo).sort((a, b) => a.nome.localeCompare(b.nome, 'pt-BR'))
    .map((c) => `<tr><td>${esc(c.nome)}</td><td>${esc(c.telefone)}</td><td class="acoes">${botaoLinha(`/clientes/${c.id}/reativar`, 'Reativar')}</td></tr>`);
  return `${tabela(['<th>Nome</th>', '<th>Telefone</th>', '<th></th>'], linhas, 'Nenhum cliente inativo.')}
<p><a href="/clientes">Voltar para clientes</a></p>`;
}

function formCliente(v, id) {
  return `<form class="cartao" method="post" action="${id ? `/clientes/${id}/editar` : '/clientes/novo'}">
${campo('Nome', 'nome', v.nome)}
${campo('Telefone', 'telefone', v.telefone, 'inputmode="tel"')}
<div class="rodape-form"><button>Salvar</button><a href="/clientes">Voltar</a></div></form>`;
}

function salvarCliente(v, id) {
  return alterar((d) => {
    const erros = [];
    const nome = texto(v.nome);
    const telefone = soDigitos(v.telefone);
    if (!nome) erros.push('Nome é obrigatório');
    if (!texto(v.telefone)) erros.push('Telefone é obrigatório');
    else if (!telefone) erros.push('Telefone inválido');
    else {
      const outro = d.clientes.find((c) => c.id !== id && soDigitos(c.telefone) === telefone);
      if (outro) erros.push(`Telefone já cadastrado para ${outro.nome}`);
    }
    if (erros.length) throw new Recusa(erros);
    if (id) {
      const c = porId(d.clientes, id);
      if (!c) throw new Recusa('Cliente não encontrado');
      c.nome = nome;
      c.telefone = telefone;
    } else {
      d.clientes.push({ id: novoId(d, 'clientes'), nome, telefone, ativo: true });
    }
  });
}

// ---------------------------------------------------------------- pets

function listaPets() {
  const lista = db.pets.filter((p) => p.ativo).sort((a, b) => a.nome.localeCompare(b.nome, 'pt-BR'));
  const linhas = lista.map((p) => `<tr><td>${esc(p.nome)}</td><td>${esc(nomeCliente(p.cliente_id))}</td><td>${ESPECIES[p.especie] || ''}</td><td>${esc(p.porte)}</td>
<td class="acoes"><a class="botao leve" href="/pets/${p.id}/editar">Editar</a>
${botaoLinha(`/pets/${p.id}/inativar`, 'Inativar', { confirma: 'Inativar este pet? Ele sai das listas; o histórico continua.' })}
${botaoLinha(`/pets/${p.id}/apagar`, 'Apagar', { classe: 'perigo', confirma: 'Apagar este pet de vez?' })}</td></tr>`);
  const inativos = db.pets.filter((p) => !p.ativo).length;
  return `<div class="barra"><span></span><a class="botao" href="/pets/novo">Novo pet</a></div>
${tabela(['<th>Nome</th>', '<th>Dono</th>', '<th>Espécie</th>', '<th>Porte</th>', '<th></th>'], linhas, 'Nenhum pet cadastrado.')}
${inativos ? `<p class="suave"><a href="/pets/inativos">Ver pets inativos (${inativos})</a></p>` : ''}`;
}

function listaPetsInativos() {
  const linhas = db.pets.filter((p) => !p.ativo).sort((a, b) => a.nome.localeCompare(b.nome, 'pt-BR'))
    .map((p) => `<tr><td>${esc(p.nome)}</td><td>${esc(nomeCliente(p.cliente_id))}</td><td class="acoes">${botaoLinha(`/pets/${p.id}/reativar`, 'Reativar')}</td></tr>`);
  return `${tabela(['<th>Nome</th>', '<th>Dono</th>', '<th></th>'], linhas, 'Nenhum pet inativo.')}
<p><a href="/pets">Voltar para pets</a></p>`;
}

function formPet(v, id) {
  return `<form class="cartao" method="post" action="${id ? `/pets/${id}/editar` : '/pets/novo'}">
${campo('Nome', 'nome', v.nome)}
${escolha('Dono', 'cliente_id', opcoesClientes(), v.cliente_id)}
${escolha('Espécie', 'especie', Object.entries(ESPECIES), v.especie)}
${escolha('Porte', 'porte', PORTES.map((p) => [p, p]), v.porte)}
<p class="suave">O porte define o preço do banho e da tosa.</p>
<div class="rodape-form"><button>Salvar</button><a href="/pets">Voltar</a></div></form>`;
}

function salvarPet(v, id) {
  return alterar((d) => {
    const erros = [];
    const nome = texto(v.nome);
    const dono = d.clientes.find((c) => c.id === Number(v.cliente_id) && c.ativo);
    if (!nome) erros.push('Nome é obrigatório');
    if (!dono) erros.push('Dono é obrigatório');
    if (!ESPECIES[v.especie]) erros.push('Espécie é obrigatória');
    if (!PORTES.includes(v.porte)) erros.push('Porte é obrigatório');
    if (erros.length) throw new Recusa(erros);
    if (id) {
      const p = porId(d.pets, id);
      if (!p) throw new Recusa('Pet não encontrado');
      Object.assign(p, { nome, cliente_id: dono.id, especie: v.especie, porte: v.porte });
    } else {
      d.pets.push({ id: novoId(d, 'pets'), nome, cliente_id: dono.id, especie: v.especie, porte: v.porte, ativo: true });
    }
  });
}

// ---------------------------------------------------------------- produtos

function listaProdutos() {
  const lista = [...db.produtos].sort((a, b) => a.nome.localeCompare(b.nome, 'pt-BR'));
  const linhas = lista.map((p) => `<tr><td>${esc(p.nome)}</td><td class="num">${reais(p.preco_centavos)}</td><td class="num">${p.estoque}${p.estoque === 0 ? ' <span class="etiqueta ruim">sem estoque</span>' : ''}</td>
<td class="acoes"><a class="botao leve" href="/produtos/${p.id}/editar">Editar</a>
${botaoLinha(`/produtos/${p.id}/apagar`, 'Apagar', { classe: 'perigo', confirma: 'Apagar este produto? As vendas já feitas não mudam.' })}</td></tr>`);
  return `<div class="barra"><span></span><a class="botao" href="/produtos/novo">Novo produto</a></div>
${tabela(['<th>Nome</th>', '<th class="num">Preço</th>', '<th class="num">Estoque</th>', '<th></th>'], linhas, 'Nenhum produto cadastrado.')}`;
}

function formProduto(v, id) {
  return `<form class="cartao" method="post" action="${id ? `/produtos/${id}/editar` : '/produtos/novo'}">
${campo('Nome', 'nome', v.nome)}
${campo('Preço', 'preco', v.preco, 'inputmode="decimal" class="curto" placeholder="0,00"')}
${campo('Estoque', 'estoque', v.estoque, 'inputmode="numeric" class="curto"')}
<div class="rodape-form"><button>Salvar</button><a href="/produtos">Voltar</a></div></form>`;
}

function salvarProduto(v, id) {
  return alterar((d) => {
    const erros = [];
    const nome = texto(v.nome);
    const preco = lerDinheiro(v.preco);
    const est = texto(v.estoque);
    if (!nome) erros.push('Nome é obrigatório');
    if (preco === null || Number.isNaN(preco) || preco > 9999999) erros.push('Valor inválido');
    if (!/^\d{1,7}$/.test(est)) erros.push('Estoque inválido');
    if (nome && d.produtos.some((x) => x.nome === nome && x.id !== Number(id || 0))) erros.push('Já existe um produto com esse nome');
    if (erros.length) throw new Recusa(erros);
    if (id) {
      const p = porId(d.produtos, id);
      if (!p) throw new Recusa('Produto não encontrado');
      Object.assign(p, { nome, preco_centavos: preco, estoque: Number(est) });
    } else {
      d.produtos.push({ id: novoId(d, 'produtos'), nome, preco_centavos: preco, estoque: Number(est) });
    }
  });
}

// ---------------------------------------------------------------- vendas

function resumoItens(v) {
  return v.itens.map((i) => `${i.quantidade} × ${i.descricao}`).join(', ');
}

function listaVendas() {
  const lista = [...db.vendas].sort((a, b) => b.id - a.id);
  const linhas = lista.map((v) => `<tr><td>${v.id}</td><td>${dataBR(v.data)} ${esc(v.hora)}</td><td>${esc(resumoItens(v))}${v.cliente_id != null ? `<br><span class="suave">${esc(nomeCliente(v.cliente_id))}</span>` : ''}</td>
<td class="num">${reais(v.total_centavos)}</td><td>${FORMAS[v.forma_pagamento] || ''}</td><td>${etiquetaVenda(v.status)}</td>
<td class="acoes"><a class="botao leve" href="/vendas/${v.id}">Detalhes</a>
${v.status === 'finalizada' ? `<a class="botao perigo" href="/vendas/${v.id}/cancelar">Cancelar</a>` : ''}</td></tr>`);
  return `<div class="barra"><span></span><a class="botao" href="/vendas/nova">Nova venda</a></div>
${tabela(['<th>Nº</th>', '<th>Data</th>', '<th>Itens</th>', '<th class="num">Total</th>', '<th>Pagamento</th>', '<th>Situação</th>', '<th></th>'], linhas, 'Nenhuma venda registrada.')}`;
}

function detalheVenda(v) {
  const itens = v.itens.map((i) => `<tr><td>${esc(i.descricao)}</td><td class="num">${i.quantidade}</td><td class="num">${reais(i.preco_unitario_centavos)}</td><td class="num">${reais(i.preco_unitario_centavos * i.quantidade)}</td></tr>`);
  const c = v.cancelamento;
  return `<p>${dataBR(v.data)} às ${esc(v.hora)} · ${etiquetaVenda(v.status)} · ${v.origem === 'agendamento' ? 'Serviço da agenda' : 'Balcão'}${v.cliente_id != null ? ` · Cliente: ${esc(nomeCliente(v.cliente_id))}` : ''}</p>
${tabela(['<th>Item</th>', '<th class="num">Qtd.</th>', '<th class="num">Preço</th>', '<th class="num">Soma</th>'], itens, 'Sem itens.')}
<div class="resumo">
<p>Subtotal dos itens: ${reais(v.subtotal_centavos)}</p>
<p>Desconto: ${reais(v.desconto_centavos)}</p>
<p class="total">Total: ${reais(v.total_centavos)}</p>
<p>Pagamento: ${FORMAS[v.forma_pagamento] || ''}${v.forma_pagamento === 'dinheiro' ? ` · recebido ${reais(v.recebido_centavos)} · troco ${reais(v.troco_centavos)}` : ''}</p>
${c ? `<p>Cancelada em ${dataBR(c.data)} às ${esc(c.hora)}. Motivo: ${esc(c.motivo)}</p>` : ''}
</div>
<p class="rodape-form">${v.status === 'finalizada' ? `<a class="botao perigo" href="/vendas/${v.id}/cancelar">Cancelar venda</a>` : ''}<a href="/vendas">Voltar para vendas</a></p>`;
}

// O carrinho viaja no próprio formulário (campos ocultos "item" = produto:quantidade).
function lerCarrinho(corpo) {
  const itens = [];
  for (const bruto of corpo.getAll('item')) {
    const m = /^(\d+):(\d{1,6})$/.exec(bruto);
    if (!m || +m[2] < 1) continue;
    const ja = itens.find((i) => i.produto_id === +m[1]);
    if (ja) ja.quantidade += +m[2];
    else itens.push({ produto_id: +m[1], quantidade: +m[2] });
  }
  return itens;
}

const vendasFeitas = new Set(); // fichas de formulários já finalizados (evita venda em dobro)

function formVenda(v, itens) {
  let subtotal = 0;
  const linhas = itens.map((i, n) => {
    const p = porId(db.produtos, i.produto_id);
    const preco = p ? p.preco_centavos : 0;
    subtotal += preco * i.quantidade;
    return `<tr><td>${esc(p ? p.nome : 'Produto removido')}</td><td class="num">${i.quantidade}</td><td class="num">${reais(preco)}</td><td class="num">${reais(preco * i.quantidade)}</td>
<td class="acoes"><button class="perigo" name="remover" value="${n}" formnovalidate>Remover</button></td></tr>`;
  });
  const ocultos = itens.map((i) => `<input type="hidden" name="item" value="${i.produto_id}:${i.quantidade}">`).join('');
  const produtos = [...db.produtos].sort((a, b) => a.nome.localeCompare(b.nome, 'pt-BR'))
    .map((p) => [p.id, `${p.nome} — ${reais(p.preco_centavos)} (estoque: ${p.estoque})`]);
  return `<form class="cartao largo" method="post" action="/vendas/nova">
<input type="hidden" name="ficha" value="${esc(v.ficha)}">${ocultos}
${escolha('Cliente', 'cliente_id', opcoesClientes(), v.cliente_id)}
<h2>Itens</h2>
<div class="linha-campos">${escolha('Produto', 'produto_id', produtos, v.produto_id)}
${campo('Quantidade', 'quantidade', v.quantidade || '1', 'inputmode="numeric" class="curto"')}
<div class="campo"><button name="acao" value="adicionar">Adicionar item</button></div></div>
${tabela(['<th>Produto</th>', '<th class="num">Qtd.</th>', '<th class="num">Preço</th>', '<th class="num">Soma</th>', '<th></th>'], linhas, 'Nenhum item adicionado ainda.')}
<p class="total">Total: ${reais(subtotal)}</p>
<h2>Pagamento</h2>
${campo('Desconto', 'desconto', v.desconto, 'inputmode="decimal" class="curto" placeholder="0,00"')}
${camposPagamento(v)}
<div class="rodape-form"><button name="acao" value="finalizar">Finalizar venda</button><a href="/vendas">Voltar sem vender</a></div>
</form>${SCRIPT_RECEBIDO}`;
}

function adicionarItem(v, itens) {
  const p = porId(db.produtos, Number(v.produto_id));
  if (!p) return ['Escolha um produto'];
  const q = texto(v.quantidade);
  if (!/^\d{1,6}$/.test(q) || Number(q) < 1) return ['Quantidade inválida'];
  const ja = itens.find((i) => i.produto_id === p.id);
  const totalQ = Number(q) + (ja ? ja.quantidade : 0);
  if (totalQ > p.estoque) return [`Estoque insuficiente (disponível: ${p.estoque})`];
  if (ja) ja.quantidade = totalQ;
  else itens.push({ produto_id: p.id, quantidade: Number(q) });
  v.produto_id = '';
  v.quantidade = '1';
  return [];
}

function finalizarVenda(v, itens) {
  return alterar((d) => {
    if (vendasFeitas.has(v.ficha)) throw new Recusa('Esta venda já foi finalizada. Comece uma nova venda.');
    if (texto(v.produto_id)) throw new Recusa('Há um produto escolhido que ainda não foi adicionado. Use "Adicionar item" ou deixe o campo Produto vazio.');
    if (!itens.length) throw new Recusa('Adicione pelo menos um item');
    const erros = [];
    const itensVenda = [];
    let subtotal = 0;
    for (const i of itens) {
      const p = porId(d.produtos, i.produto_id);
      if (!p) throw new Recusa('Um produto da venda não existe mais. Remova o item e tente de novo.');
      if (i.quantidade > p.estoque) throw new Recusa(`Estoque insuficiente (disponível: ${p.estoque})`);
      itensVenda.push({ produto_id: p.id, descricao: p.nome, preco_unitario_centavos: p.preco_centavos, quantidade: i.quantidade });
      subtotal += p.preco_centavos * i.quantidade;
    }
    const desconto = lerDinheiro(v.desconto) ?? 0;
    if (Number.isNaN(desconto)) throw new Recusa('Valor inválido');
    if (desconto > subtotal) throw new Recusa('Desconto maior que o total');
    const total = subtotal - desconto;
    const pg = pagamento(v, total, erros);
    if (!pg) throw new Recusa(erros);
    const cliente = d.clientes.find((c) => c.id === Number(v.cliente_id) && c.ativo);
    for (const i of itensVenda) porId(d.produtos, i.produto_id).estoque -= i.quantidade;
    const t = agora();
    const venda = {
      id: novoId(d, 'vendas'), data: t.data, hora: t.hora, cliente_id: cliente ? cliente.id : null,
      origem: 'balcao', agendamento_id: null, itens: itensVenda,
      subtotal_centavos: subtotal, desconto_centavos: desconto, total_centavos: total,
      ...pg, status: 'finalizada', cancelamento: null,
    };
    d.vendas.push(venda);
    return venda;
  });
}

function formCancelarVenda(v, motivo = '') {
  return `<p>Venda nº ${v.id} de ${dataBR(v.data)} · ${esc(resumoItens(v))} · <strong>${reais(v.total_centavos)}</strong> (${FORMAS[v.forma_pagamento] || ''})</p>
<p class="suave">A venda continua na lista como cancelada, o estoque dos produtos volta e ela sai do fechamento do dia. Não dá para desfazer.</p>
<form class="cartao" method="post" action="/vendas/${v.id}/cancelar">
${campo('Motivo', 'motivo', motivo)}
<div class="rodape-form"><button>Confirmar cancelamento</button><a href="/vendas">Voltar sem cancelar</a></div></form>`;
}

function cancelarVenda(id, motivoBruto) {
  return alterar((d) => {
    const v = porId(d.vendas, id);
    if (!v) throw new Recusa('Venda não encontrada');
    if (v.status !== 'finalizada') throw new Recusa('Venda já está cancelada');
    const motivo = texto(motivoBruto);
    if (!motivo) throw new Recusa('Motivo é obrigatório');
    for (const i of v.itens) {
      const p = i.produto_id == null ? null : porId(d.produtos, i.produto_id);
      if (p) p.estoque += i.quantidade;
    }
    const t = agora();
    v.status = 'cancelada';
    v.cancelamento = { data: t.data, hora: t.hora, motivo };
  });
}

// ---------------------------------------------------------------- agenda

function linhaAgenda(a, comAcoes = true) {
  const pet = porId(db.pets, a.pet_id);
  const acoes = a.status === 'marcado'
    ? `<a class="botao leve" href="/agenda/${a.id}/concluir">Concluir</a>
${botaoLinha(`/agenda/${a.id}/cancelar`, 'Cancelar', { classe: 'perigo', confirma: 'Cancelar este agendamento?' })}` : '';
  return `<tr><td>${dataComDia(a.data)}</td><td>${esc(a.hora_inicio)}–${esc(a.hora_fim)}</td><td>${esc(nomePet(a.pet_id))}${pet ? `<br><span class="suave">${esc(nomeCliente(pet.cliente_id))}</span>` : ''}</td>
<td>${(SERVICOS[a.servico] || {}).nome || esc(a.servico)}</td><td class="num">${reais(a.preco_centavos)}</td><td>${etiquetaAgenda(a.status)}</td>${comAcoes ? `<td class="acoes">${acoes}</td>` : ''}</tr>`;
}
const chaveAgenda = (a) => `${a.data} ${a.hora_inicio}`;

function listaAgenda() {
  // Marcados primeiro, do mais próximo ao mais distante; depois o que já passou, do mais recente ao mais antigo.
  const marcados = db.agendamentos.filter((a) => a.status === 'marcado').sort((a, b) => chaveAgenda(a).localeCompare(chaveAgenda(b)));
  const outros = db.agendamentos.filter((a) => a.status !== 'marcado').sort((a, b) => chaveAgenda(b).localeCompare(chaveAgenda(a)));
  return `<div class="barra"><span class="suave">Atendimento de segunda a sábado, das 08:00 às 18:00.</span><a class="botao" href="/agenda/novo">Novo agendamento</a></div>
${tabela(['<th>Data</th>', '<th>Hora</th>', '<th>Pet</th>', '<th>Serviço</th>', '<th class="num">Preço</th>', '<th>Situação</th>', '<th></th>'], [...marcados, ...outros].map((a) => linhaAgenda(a)), 'Nenhum agendamento.')}`;
}

function formAgendamento(v) {
  const pets = db.pets.filter((p) => p.ativo).sort((a, b) => a.nome.localeCompare(b.nome, 'pt-BR'))
    .map((p) => [p.id, `${p.nome} (${nomeCliente(p.cliente_id)}, porte ${p.porte})`]);
  const precos = Object.values(SERVICOS).map((s) => `<tr><td>${s.nome}</td><td>${s.minutos} min</td>${PORTES.map((p) => `<td class="num">${reais(s.precos[p])}</td>`).join('')}</tr>`);
  return `<form class="cartao" method="post" action="/agenda/novo">
${escolha('Pet', 'pet_id', pets, v.pet_id)}
${escolha('Serviço', 'servico', Object.entries(SERVICOS).map(([k, s]) => [k, s.nome]), v.servico)}
<div class="linha-campos">
<div class="campo"><label for="c-data">Data</label><input id="c-data" type="date" name="data" value="${esc(v.data)}"></div>
<div class="campo"><label for="c-hora">Hora</label><input id="c-hora" type="time" name="hora" value="${esc(v.hora)}"></div></div>
<div class="rodape-form"><button>Agendar</button><a href="/agenda">Voltar</a></div></form>
<h2>Tabela de serviços</h2>
${tabela(['<th>Serviço</th>', '<th>Duração</th>', ...PORTES.map((p) => `<th class="num">Porte ${p}</th>`)], precos, '')}`;
}

function agendar(v) {
  return alterar((d) => {
    const erros = [];
    const pet = d.pets.find((p) => p.id === Number(v.pet_id) && p.ativo);
    const servico = Object.hasOwn(SERVICOS, v.servico) ? SERVICOS[v.servico] : null;
    const dia = dataValida(v.data);
    const inicio = minutos(v.hora);
    if (!pet) erros.push('Pet é obrigatório');
    if (!servico) erros.push('Serviço é obrigatório');
    if (!dia) erros.push(texto(v.data) ? 'Data inválida' : 'Data é obrigatória');
    if (inicio === null) erros.push(texto(v.hora) ? 'Hora inválida' : 'Hora é obrigatória');
    if (erros.length) throw new Recusa(erros);
    if (!PORTES.includes(pet.porte)) throw new Recusa('O pet está sem porte; corrija o cadastro dele');
    const fim = inicio + servico.minutos;
    if (dia.getDay() === 0 || inicio < ABRE || fim > FECHA) throw new Recusa('Fora do horário de funcionamento');
    if (v.data < agora().data) throw new Recusa('Data já passou');
    const ocupado = d.agendamentos.some((a) => a.status !== 'cancelado' && a.data === v.data
      && inicio < minutos(a.hora_fim) && minutos(a.hora_inicio) < fim);
    if (ocupado) throw new Recusa('Horário ocupado');
    d.agendamentos.push({
      id: novoId(d, 'agendamentos'), pet_id: pet.id, servico: v.servico, data: v.data,
      hora_inicio: horaDe(inicio), hora_fim: horaDe(fim), preco_centavos: servico.precos[pet.porte],
      status: 'marcado', venda_id: null,
    });
  });
}

function formConcluir(a, v) {
  return `<p>${esc(nomePet(a.pet_id))} · ${(SERVICOS[a.servico] || {}).nome || ''} · ${dataComDia(a.data)} das ${esc(a.hora_inicio)} às ${esc(a.hora_fim)}</p>
<p class="total">Valor: ${reais(a.preco_centavos)}</p>
<form class="cartao" method="post" action="/agenda/${a.id}/concluir">
${camposPagamento(v)}
<div class="rodape-form"><button>Confirmar conclusão</button><a href="/agenda">Voltar</a></div></form>${SCRIPT_RECEBIDO}`;
}

function concluir(id, v) {
  return alterar((d) => {
    const a = porId(d.agendamentos, id);
    if (!a) throw new Recusa('Agendamento não encontrado');
    if (a.status !== 'marcado') throw new Recusa('Este agendamento não está mais marcado');
    const erros = [];
    const pg = pagamento(v, a.preco_centavos, erros);
    if (!pg) throw new Recusa(erros);
    const pet = porId(d.pets, a.pet_id);
    const t = agora();
    const venda = {
      id: novoId(d, 'vendas'), data: t.data, hora: t.hora, cliente_id: pet ? pet.cliente_id : null,
      origem: 'agendamento', agendamento_id: a.id,
      itens: [{ produto_id: null, descricao: SERVICOS[a.servico].nome, preco_unitario_centavos: a.preco_centavos, quantidade: 1 }],
      subtotal_centavos: a.preco_centavos, desconto_centavos: 0, total_centavos: a.preco_centavos,
      ...pg, status: 'finalizada', cancelamento: null,
    };
    d.vendas.push(venda);
    a.status = 'concluido';
    a.venda_id = venda.id;
    return venda;
  });
}

// ---------------------------------------------------------------- fechamento e início

function fechamento(q) {
  const pedida = q.get('data');
  const data = dataValida(pedida) ? pedida : agora().data;
  const doDia = db.vendas.filter((v) => v.data === data);
  const validas = doDia.filter((v) => v.status === 'finalizada');
  const soma = { dinheiro: 0, pix: 0, cartao: 0 };
  for (const v of validas) if (v.forma_pagamento in soma) soma[v.forma_pagamento] += v.total_centavos;
  const total = soma.dinheiro + soma.pix + soma.cartao;
  const linhas = doDia.sort((a, b) => a.id - b.id).map((v) => `<tr><td>${v.id}</td><td>${esc(v.hora)}</td><td>${esc(resumoItens(v))}</td><td class="num">${reais(v.total_centavos)}</td><td>${FORMAS[v.forma_pagamento] || ''}</td><td>${etiquetaVenda(v.status)}</td></tr>`);
  const canceladas = doDia.length - validas.length;
  return `<div class="barra"><form method="get" action="/fechamento"><div><label for="c-data">Data</label><input id="c-data" type="date" name="data" value="${data}"></div><button>Ver fechamento</button></form></div>
<div class="cartao resumo">
<p class="suave">${dataComDia(data)} · ${validas.length} venda(s)${canceladas ? ` · ${canceladas} cancelada(s), fora da soma` : ''}</p>
<p>Dinheiro: ${reais(soma.dinheiro)}</p>
<p>Pix: ${reais(soma.pix)}</p>
<p>Cartão: ${reais(soma.cartao)}</p>
<p class="total">Total: ${reais(total)}</p>
</div>
<h2>Vendas do dia</h2>
${tabela(['<th>Nº</th>', '<th>Hora</th>', '<th>Itens</th>', '<th class="num">Valor</th>', '<th>Pagamento</th>', '<th>Situação</th>'], linhas, 'Nenhuma venda neste dia.')}`;
}

function inicio() {
  const hoje = agora().data;
  const doDia = db.agendamentos.filter((a) => a.data === hoje).sort((a, b) => a.hora_inicio.localeCompare(b.hora_inicio));
  const poucos = db.produtos.filter((p) => p.estoque <= 2).sort((a, b) => a.estoque - b.estoque);
  return `<p class="rodape-form"><a class="botao" href="/vendas/nova">Nova venda</a><a class="botao" href="/agenda/novo">Novo agendamento</a></p>
<h2>Agenda de hoje · ${dataComDia(hoje)}</h2>
${tabela(['<th>Data</th>', '<th>Hora</th>', '<th>Pet</th>', '<th>Serviço</th>', '<th class="num">Preço</th>', '<th>Situação</th>', '<th></th>'], doDia.map((a) => linhaAgenda(a)), 'Nenhum agendamento para hoje.')}
${poucos.length ? `<h2>Estoque acabando</h2>${tabela(['<th>Produto</th>', '<th class="num">Estoque</th>'], poucos.map((p) => `<tr><td>${esc(p.nome)}</td><td class="num">${p.estoque}</td></tr>`), '')}` : ''}`;
}

// ---------------------------------------------------------------- servidor

function lerCorpo(req) {
  return new Promise((resolve, reject) => {
    let tamanho = 0;
    const partes = [];
    req.on('data', (c) => {
      tamanho += c.length;
      if (tamanho > 200000) {
        reject(new Error('corpo grande demais'));
        req.destroy();
      } else partes.push(c);
    });
    req.on('end', () => resolve(new URLSearchParams(Buffer.concat(partes).toString('utf8'))));
    req.on('error', reject);
  });
}

function tratar(req, res, url, corpo) {
  const q = url.searchParams;
  const caminho = url.pathname.replace(/\/+$/, '') || '/';
  const post = req.method === 'POST';
  const aviso = q.has('m') ? avisos.get(q.get('m')) : undefined;
  if (aviso) avisos.delete(q.get('m'));

  const html = (titulo, conteudo, opc = {}, status = 200) => {
    res.writeHead(status, { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store' });
    res.end(pagina(titulo, conteudo, { aviso, ...opc }));
  };
  const ir = (destino, tipo, mensagens) => {
    const m = mensagens ? `${destino.includes('?') ? '&' : '?'}m=${guardarAviso(tipo, mensagens)}` : '';
    res.writeHead(303, { Location: destino + m });
    res.end();
  };
  const campos = (...nomes) => Object.fromEntries(nomes.map((n) => [n, corpo ? corpo.get(n) ?? '' : '']));
  // Executa uma ação de linha: sucesso ou recusa aparecem na lista.
  const acaoLinha = (destino, sucesso, fn) => {
    try {
      alterar(fn);
      ir(destino, 'ok', sucesso);
    } catch (e) {
      if (!(e instanceof Recusa)) throw e;
      ir(destino, 'erro', e.mensagens);
    }
  };
  const naoAchei = () => html('Página não encontrada', '<p>Esta página não existe. Use o menu acima.</p>', {}, 404);

  let m;
  if (caminho === '/') return html('Início', inicio(), { secao: '/' });

  // ---- clientes
  if (caminho === '/clientes') return html('Clientes', listaClientes(q), { secao: '/clientes' });
  if (caminho === '/clientes/inativos') return html('Clientes inativos', listaClientesInativos(), { secao: '/clientes' });
  if (caminho === '/clientes/novo' || (m = /^\/clientes\/(\d+)\/editar$/.exec(caminho))) {
    const id = m ? Number(m[1]) : null;
    const atual = id ? porId(db.clientes, id) : null;
    if (id && !atual) return naoAchei();
    const titulo = id ? 'Editar cliente' : 'Novo cliente';
    if (!post) return html(titulo, formCliente(atual || {}, id), { secao: '/clientes' });
    const v = campos('nome', 'telefone');
    try {
      salvarCliente(v, id);
      return ir('/clientes', 'ok', 'Cliente salvo');
    } catch (e) {
      if (!(e instanceof Recusa)) throw e;
      return html(titulo, formCliente(v, id), { secao: '/clientes', erros: e.mensagens }, 422);
    }
  }
  if (post && (m = /^\/clientes\/(\d+)\/(inativar|reativar|apagar)$/.exec(caminho))) {
    const id = Number(m[1]);
    if (m[2] === 'inativar') {
      return acaoLinha('/clientes', 'Cliente inativado', (d) => {
        const c = porId(d.clientes, id);
        if (!c) throw new Recusa('Cliente não encontrado');
        c.ativo = false;
        for (const p of d.pets) if (p.cliente_id === id) p.ativo = false;
      });
    }
    if (m[2] === 'reativar') {
      return acaoLinha('/clientes', 'Cliente reativado', (d) => {
        const c = porId(d.clientes, id);
        if (!c) throw new Recusa('Cliente não encontrado');
        c.ativo = true;
      });
    }
    return acaoLinha('/clientes', 'Cliente apagado', (d) => {
      if (!porId(d.clientes, id)) throw new Recusa('Cliente não encontrado');
      if (temHistoricoCliente(d, id)) throw new Recusa('Cliente possui histórico e não pode ser apagado');
      if (d.pets.some((p) => p.cliente_id === id)) throw new Recusa('Cliente possui pets cadastrados; apague os pets antes ou use Inativar');
      d.clientes = d.clientes.filter((c) => c.id !== id);
    });
  }

  // ---- pets
  if (caminho === '/pets') return html('Pets', listaPets(), { secao: '/pets' });
  if (caminho === '/pets/inativos') return html('Pets inativos', listaPetsInativos(), { secao: '/pets' });
  if (caminho === '/pets/novo' || (m = /^\/pets\/(\d+)\/editar$/.exec(caminho))) {
    const id = m ? Number(m[1]) : null;
    const atual = id ? porId(db.pets, id) : null;
    if (id && !atual) return naoAchei();
    const titulo = id ? 'Editar pet' : 'Novo pet';
    if (!post) return html(titulo, formPet(atual || {}, id), { secao: '/pets' });
    const v = campos('nome', 'cliente_id', 'especie', 'porte');
    try {
      salvarPet(v, id);
      return ir('/pets', 'ok', 'Pet salvo');
    } catch (e) {
      if (!(e instanceof Recusa)) throw e;
      return html(titulo, formPet(v, id), { secao: '/pets', erros: e.mensagens }, 422);
    }
  }
  if (post && (m = /^\/pets\/(\d+)\/(inativar|reativar|apagar)$/.exec(caminho))) {
    const id = Number(m[1]);
    if (m[2] === 'inativar') {
      return acaoLinha('/pets', 'Pet inativado', (d) => {
        const p = porId(d.pets, id);
        if (!p) throw new Recusa('Pet não encontrado');
        p.ativo = false;
      });
    }
    if (m[2] === 'reativar') {
      return acaoLinha('/pets', 'Pet reativado', (d) => {
        const p = porId(d.pets, id);
        if (!p) throw new Recusa('Pet não encontrado');
        const dono = porId(d.clientes, p.cliente_id);
        if (!dono || !dono.ativo) throw new Recusa('O dono deste pet está inativo; reative o cliente antes');
        p.ativo = true;
      });
    }
    return acaoLinha('/pets', 'Pet apagado', (d) => {
      if (!porId(d.pets, id)) throw new Recusa('Pet não encontrado');
      if (d.agendamentos.some((a) => a.pet_id === id)) throw new Recusa('Pet possui histórico e não pode ser apagado');
      d.pets = d.pets.filter((p) => p.id !== id);
    });
  }

  // ---- produtos
  if (caminho === '/produtos') return html('Produtos', listaProdutos(), { secao: '/produtos' });
  if (caminho === '/produtos/novo' || (m = /^\/produtos\/(\d+)\/editar$/.exec(caminho))) {
    const id = m ? Number(m[1]) : null;
    const atual = id ? porId(db.produtos, id) : null;
    if (id && !atual) return naoAchei();
    const titulo = id ? 'Editar produto' : 'Novo produto';
    if (!post) {
      const v = atual ? { nome: atual.nome, preco: reaisCampo(atual.preco_centavos), estoque: atual.estoque } : {};
      return html(titulo, formProduto(v, id), { secao: '/produtos' });
    }
    const v = campos('nome', 'preco', 'estoque');
    try {
      salvarProduto(v, id);
      return ir('/produtos', 'ok', 'Produto salvo');
    } catch (e) {
      if (!(e instanceof Recusa)) throw e;
      return html(titulo, formProduto(v, id), { secao: '/produtos', erros: e.mensagens }, 422);
    }
  }
  if (post && (m = /^\/produtos\/(\d+)\/apagar$/.exec(caminho))) {
    const id = Number(m[1]);
    return acaoLinha('/produtos', 'Produto apagado', (d) => {
      if (!porId(d.produtos, id)) throw new Recusa('Produto não encontrado');
      d.produtos = d.produtos.filter((p) => p.id !== id);
    });
  }

  // ---- vendas
  if (caminho === '/vendas') return html('Vendas', listaVendas(), { secao: '/vendas' });
  if (caminho === '/vendas/nova') {
    if (!post) return html('Nova venda', formVenda({ ficha: crypto.randomBytes(8).toString('hex') }, []), { secao: '/vendas' });
    const v = campos('ficha', 'cliente_id', 'produto_id', 'quantidade', 'desconto', 'forma', 'recebido');
    const itens = lerCarrinho(corpo);
    let erros = [];
    if (corpo.has('remover')) {
      itens.splice(Number(corpo.get('remover')), 1);
    } else if (corpo.get('acao') === 'finalizar') {
      try {
        const venda = finalizarVenda(v, itens);
        vendasFeitas.add(v.ficha);
        const msgs = ['Venda finalizada'];
        if (venda.forma_pagamento === 'dinheiro') msgs.push(`Troco: ${reais(venda.troco_centavos)}`);
        return ir('/vendas', 'ok', msgs);
      } catch (e) {
        if (!(e instanceof Recusa)) throw e;
        erros = e.mensagens;
      }
    } else {
      erros = adicionarItem(v, itens);
    }
    return html('Nova venda', formVenda(v, itens), { secao: '/vendas', erros }, erros.length ? 422 : 200);
  }
  if ((m = /^\/vendas\/(\d+)$/.exec(caminho))) {
    const v = porId(db.vendas, Number(m[1]));
    if (!v) return naoAchei();
    return html(`Venda nº ${v.id}`, detalheVenda(v), { secao: '/vendas' });
  }
  if ((m = /^\/vendas\/(\d+)\/cancelar$/.exec(caminho))) {
    const v = porId(db.vendas, Number(m[1]));
    if (!v) return naoAchei();
    if (v.status !== 'finalizada') return ir('/vendas', 'erro', 'Venda já está cancelada');
    if (!post) return html('Cancelar venda', formCancelarVenda(v), { secao: '/vendas' });
    try {
      cancelarVenda(v.id, corpo.get('motivo'));
      return ir('/vendas', 'ok', 'Venda cancelada');
    } catch (e) {
      if (!(e instanceof Recusa)) throw e;
      return html('Cancelar venda', formCancelarVenda(v, corpo.get('motivo') || ''), { secao: '/vendas', erros: e.mensagens }, 422);
    }
  }

  // ---- agenda
  if (caminho === '/agenda') return html('Agenda', listaAgenda(), { secao: '/agenda' });
  if (caminho === '/agenda/novo') {
    if (!post) return html('Novo agendamento', formAgendamento({}), { secao: '/agenda' });
    const v = campos('pet_id', 'servico', 'data', 'hora');
    try {
      agendar(v);
      return ir('/agenda', 'ok', 'Agendamento marcado');
    } catch (e) {
      if (!(e instanceof Recusa)) throw e;
      return html('Novo agendamento', formAgendamento(v), { secao: '/agenda', erros: e.mensagens }, 422);
    }
  }
  if ((m = /^\/agenda\/(\d+)\/concluir$/.exec(caminho))) {
    const a = porId(db.agendamentos, Number(m[1]));
    if (!a) return naoAchei();
    if (a.status !== 'marcado') return ir('/agenda', 'erro', 'Este agendamento não está mais marcado');
    if (!post) return html('Concluir agendamento', formConcluir(a, {}), { secao: '/agenda' });
    const v = campos('forma', 'recebido');
    try {
      const venda = concluir(a.id, v);
      const msgs = ['Agendamento concluído'];
      if (venda.forma_pagamento === 'dinheiro') msgs.push(`Troco: ${reais(venda.troco_centavos)}`);
      return ir('/agenda', 'ok', msgs);
    } catch (e) {
      if (!(e instanceof Recusa)) throw e;
      return html('Concluir agendamento', formConcluir(a, v), { secao: '/agenda', erros: e.mensagens }, 422);
    }
  }
  if (post && (m = /^\/agenda\/(\d+)\/cancelar$/.exec(caminho))) {
    const id = Number(m[1]);
    return acaoLinha('/agenda', 'Agendamento cancelado', (d) => {
      const a = porId(d.agendamentos, id);
      if (!a) throw new Recusa('Agendamento não encontrado');
      if (a.status !== 'marcado') throw new Recusa('Este agendamento não está mais marcado');
      a.status = 'cancelado';
    });
  }

  // ---- fechamento
  if (caminho === '/fechamento') return html('Fechamento do dia', fechamento(q), { secao: '/fechamento' });

  return naoAchei();
}

const servidor = http.createServer(async (req, res) => {
  try {
    const url = new URL(req.url, 'http://127.0.0.1');
    if (req.method !== 'GET' && req.method !== 'POST' && req.method !== 'HEAD') {
      res.writeHead(405, { Allow: 'GET, POST' });
      return res.end();
    }
    let corpo = null;
    if (req.method === 'POST') {
      // Só aceita formulários enviados pelas próprias páginas do sistema.
      const origem = req.headers.origin;
      if (origem && origem !== 'null') {
        let hostOrigem = '';
        try { hostOrigem = new URL(origem).host; } catch {}
        if (hostOrigem !== req.headers.host) {
          res.writeHead(403, { 'Content-Type': 'text/plain; charset=utf-8' });
          return res.end('Pedido recusado.');
        }
      }
      corpo = await lerCorpo(req);
    }
    tratar(req, res, url, corpo);
  } catch (e) {
    console.error(e);
    if (!res.headersSent) res.writeHead(500, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(pagina('Erro', '<p>Algo deu errado e nada foi alterado. Tente de novo.</p>'));
  }
});

servidor.listen(PORTA, '127.0.0.1', () => {
  console.log(`Pet shop em http://127.0.0.1:${PORTA}/ (dados em ${ARQUIVO})`);
});
