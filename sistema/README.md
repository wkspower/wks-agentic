# Sistema do pet shop

Aplicação web local para o balcão: clientes, pets, agenda de banho e tosa,
produtos com estoque, vendas e fechamento do dia.

## Como usar

    npm start

Abra `http://127.0.0.1:3000/` no navegador. Precisa só do Node 22; não há
nada para instalar.

Variáveis de ambiente:

- `PORTA` — porta HTTP (padrão `3000`).
- `ARQUIVO_DADOS` — arquivo de dados (padrão `dados/petshop.json`, dentro desta pasta).

## Dados

Tudo fica em um único arquivo JSON, criado na primeira gravação. Cada
gravação é feita em um arquivo temporário e depois trocada de uma vez, para
o arquivo nunca ficar pela metade. Para fazer cópia de segurança, basta
copiar esse arquivo. Se o arquivo existir mas estiver ilegível, o sistema
não inicia (para não gravar por cima).

O código está todo em `server.js`.
