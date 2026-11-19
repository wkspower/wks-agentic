# Sistema do pet shop — descrição

Aplicação web local, em português, usada no balcão de um pet shop por um
único usuário, sem login. Cobre: clientes, pets, agenda de serviços,
produtos com estoque, vendas no balcão e fechamento do dia.

Fora do escopo: fiscal (NF-e), funcionários, veterinária, hotel, vendas online.

O que está escrito aqui e nos casos (`casos/`) é fixo. Tudo o que não está
escrito é livre: linguagem interna, estrutura do código, aparência, endereços
das páginas, ordem das listas, títulos e textos de ajuda.

## 1. Como o sistema é iniciado

- Fica numa pasta própria com um `package.json`. Inicia com `npm start`.
- Roda em Node 22 sem instalar nada (sem dependências externas).
- Variável `PORTA`: porta HTTP (padrão 3000). Atende em `http://127.0.0.1:PORTA/`.
- Variável `ARQUIVO_DADOS`: caminho do arquivo de dados (padrão `dados/petshop.json`).
- Se o arquivo não existe, o sistema começa vazio e cria o arquivo na primeira gravação.
- Se o arquivo existe, o sistema lê o que está nele ao iniciar.

## 2. Dados guardados

Um único arquivo JSON. Ordem das chaves e espaçamento são livres; nomes,
tipos e valores são fixos.

```json
{
  "versao": 1,
  "proximo_id": { "clientes": 2, "pets": 2, "produtos": 2, "vendas": 2, "agendamentos": 2 },
  "clientes": [
    { "id": 1, "nome": "Maria Silva", "telefone": "11999990001", "ativo": true }
  ],
  "pets": [
    { "id": 1, "nome": "Rex", "cliente_id": 1, "especie": "cao", "porte": "M", "ativo": true }
  ],
  "produtos": [
    { "id": 1, "nome": "Ração 1kg", "preco_centavos": 4500, "estoque": 10 }
  ],
  "vendas": [
    {
      "id": 1,
      "data": "2026-11-19",
      "hora": "14:30",
      "cliente_id": null,
      "origem": "balcao",
      "agendamento_id": null,
      "itens": [
        { "produto_id": 1, "descricao": "Ração 1kg", "preco_unitario_centavos": 4500, "quantidade": 1 }
      ],
      "subtotal_centavos": 4500,
      "desconto_centavos": 0,
      "total_centavos": 4500,
      "forma_pagamento": "dinheiro",
      "recebido_centavos": 5000,
      "troco_centavos": 500,
      "status": "finalizada",
      "cancelamento": null
    }
  ],
  "agendamentos": [
    {
      "id": 1,
      "pet_id": 1,
      "servico": "banho",
      "data": "2026-11-23",
      "hora_inicio": "10:00",
      "hora_fim": "11:00",
      "preco_centavos": 5500,
      "status": "marcado",
      "venda_id": null
    }
  ]
}
```

Valores permitidos:

- `especie`: `cao`, `gato`, `outro`. `porte`: `P`, `M`, `G`.
- `servico`: `banho`, `tosa`, `banho_e_tosa`.
- `forma_pagamento`: `dinheiro`, `pix`, `cartao`.
- venda `status`: `finalizada`, `cancelada`. `origem`: `balcao`, `agendamento`.
- agendamento `status`: `marcado`, `concluido`, `cancelado`.
- `cancelamento`: `null` ou `{ "data": "AAAA-MM-DD", "hora": "HH:MM", "motivo": "..." }`.
- `recebido_centavos` e `troco_centavos`: números quando a forma é dinheiro; `null` nas outras.
- Item de venda vindo de serviço: `produto_id` é `null` e `descricao` é o nome do serviço (`Banho`, `Tosa`, `Banho e tosa`).

Regras do formato:

- Dinheiro é sempre inteiro em centavos. Datas `AAAA-MM-DD`, horas `HH:MM` (24h, hora local).
- Identificadores são números sequenciais por tipo, começando em 1, e nunca
  são reutilizados, mesmo depois de apagar. `proximo_id` guarda o próximo de cada tipo.
- Uma operação recusada não altera o arquivo (nem um byte).

## 3. Telas

Convenções que valem para todas as telas:

- Toda página tem um menu com os links: `Clientes`, `Pets`, `Produtos`,
  `Agenda`, `Vendas`, `Fechamento do dia`.
- Os nomes abaixo são textos visíveis exatos. "Campo" é um campo de
  formulário com esse rótulo (`<label>` associado). "Ação" é um botão ou
  link com esse texto.
- Toda lista é uma tabela, uma linha (`<tr>`) por registro. Ações sobre um
  registro ficam dentro da linha dele.
- Campos de escolha são `<select>`. Quando a escolha é opcional ou começa
  vazia, a primeira opção é vazia.
- Depois de cada ação, a mensagem de sucesso ou de erro aparece na página
  que o usuário vê em seguida.
- Valores em dinheiro aparecem como `R$ 1.234,56`.
- Campos de dinheiro aceitam vírgula decimal: `12,5` vale R$ 12,50. Texto
  que não é número, ou valor negativo, é recusado com `Valor inválido`.

### Clientes

- Lista: clientes ativos, cada linha com nome e telefone.
- Campo `Busca` e ação `Buscar`: filtra por parte do nome ou do telefone.
- Ação `Novo cliente` → campos `Nome`, `Telefone`; ação `Salvar`.
  - Sucesso: `Cliente salvo`.
  - Erros: `Nome é obrigatório`; `Telefone é obrigatório`;
    `Telefone já cadastrado para <nome de quem já usa>`.
- Ações na linha: `Inativar`, `Apagar`.
  - `Apagar` cliente com histórico (venda ou agendamento):
    recusa com `Cliente possui histórico e não pode ser apagado`.
  - `Apagar` sem histórico: `Cliente apagado`, o registro sai do arquivo.
  - `Inativar`: `Cliente inativado`; `ativo` vira `false`; some da lista,
    da busca e dos campos de escolha; o histórico continua.

### Pets

- Lista: pets ativos, cada linha com nome do pet e nome do dono.
- Ação `Novo pet` → campos `Nome`, `Dono` (clientes ativos; a opção contém
  o nome do cliente), `Espécie` (`Cão`, `Gato`, `Outro`), `Porte` (`P`,
  `M`, `G`); ação `Salvar`.
  - Sucesso: `Pet salvo`.
  - Erros: `Nome é obrigatório`; `Dono é obrigatório`.
- Ações na linha: `Inativar` (`Pet inativado`), `Apagar` (`Pet apagado`).
  - `Apagar` pet com histórico (agendamento):
    recusa com `Pet possui histórico e não pode ser apagado`.

### Produtos

- Lista: cada linha com nome, preço e estoque.
- Ação `Novo produto` → campos `Nome`, `Preço`, `Estoque`; ação `Salvar`.
  - Sucesso: `Produto salvo`.
  - Erros: `Nome é obrigatório`; `Valor inválido` (preço); `Estoque inválido`
    (estoque que não é inteiro maior ou igual a zero).
- Ações na linha: `Editar` (mesmos campos, ação `Salvar`), `Apagar`
  (`Produto apagado`).

### Vendas

- Lista: todas as vendas, cada linha com número, data, total, forma de
  pagamento (`Dinheiro`, `Pix`, `Cartão`) e situação (`Finalizada`,
  `Cancelada`).
- Ação `Nova venda`:
  - Campo `Cliente` (opcional).
  - Campos `Produto` (a opção contém o nome do produto) e `Quantidade`;
    ação `Adicionar item`. Pode repetir para vários itens.
  - A página mostra `Total: R$ 54,99` com a soma dos itens já adicionados.
  - Campo `Desconto` (em reais, opcional).
  - Campo `Forma de pagamento`: `Dinheiro`, `Pix`, `Cartão`.
  - Campo `Valor recebido` (só para dinheiro).
  - Ação `Finalizar venda`.
  - Sucesso: `Venda finalizada`. Em dinheiro, mostra também `Troco: R$ 0,01`.
  - Erros: `Estoque insuficiente (disponível: 2)`;
    `Desconto maior que o total`; `Valor recebido insuficiente`;
    `Valor inválido`.
- Regras:
  - Subtotal = soma de preço × quantidade. Total = subtotal − desconto.
  - A venda guarda descrição e preço de cada item no momento da venda;
    mudar o produto depois não muda a venda.
  - Finalizar baixa o estoque. O estoque nunca fica negativo.
  - Venda finalizada não tem ação de editar nem de apagar.
- Ação na linha de venda finalizada: `Cancelar` → campo `Motivo`, ação
  `Confirmar cancelamento`.
  - Sucesso: `Venda cancelada`. A venda continua na lista como
    `Cancelada`, o estoque dos itens volta, e ela sai do fechamento.
  - Erro: `Motivo é obrigatório`.
  - Venda cancelada não tem mais a ação `Cancelar`.

### Agenda

- Lista: todos os agendamentos, cada linha com data, hora, nome do pet,
  serviço (`Banho`, `Tosa`, `Banho e tosa`), preço e situação (`Marcado`,
  `Concluído`, `Cancelado`).
- Ação `Novo agendamento` → campos `Pet` (pets ativos; a opção contém o
  nome do pet), `Serviço`, `Data` (`<input type="date">`), `Hora`
  (`<input type="time">`); ação `Agendar`.
  - Sucesso: `Agendamento marcado`.
  - Erros: `Horário ocupado`; `Fora do horário de funcionamento`.
- Funcionamento: segunda a sábado, das 08:00 às 18:00. Um atendimento por vez.
- Serviços (duração; preço por porte P / M / G):
  - Banho: 60 min; R$ 40,00 / R$ 55,00 / R$ 75,00
  - Tosa: 90 min; R$ 60,00 / R$ 80,00 / R$ 110,00
  - Banho e tosa: 120 min; R$ 90,00 / R$ 120,00 / R$ 160,00
- O preço é o do porte do pet e fica gravado no agendamento.
- Ações na linha de agendamento marcado:
  - `Concluir` → campo `Forma de pagamento` (e `Valor recebido` para
    dinheiro), ação `Confirmar conclusão`. Sucesso: `Agendamento concluído`.
    Cria uma venda com `origem` `agendamento`, datada do dia da conclusão,
    que entra no fechamento como qualquer venda.
  - `Cancelar`. Sucesso: `Agendamento cancelado`.
- Agendamento concluído ou cancelado não tem mais essas ações.

### Fechamento do dia

- Abre mostrando o dia de hoje. Campo `Data` e ação `Ver fechamento` para outro dia.
- Mostra, somando as vendas finalizadas daquele dia (canceladas não entram):
  `Dinheiro: R$ 59,99`, `Pix: R$ 55,00`, `Cartão: R$ 0,00`, `Total: R$ 114,99`.
