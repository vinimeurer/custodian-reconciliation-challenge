# Teste Técnico — Conciliadora de Custódia

## Contexto

Você trabalha no backoffice de uma Gestora de Recursos. Todo dia útil, dois sistemas precisam estar em sincronia:

- **Sistema Interno (`internal_system.json`)**: posição consolidada da carteira (ticker, quantidade, financeiro).
- **Custodiante (`custodian_extract.csv`)**: extrato recebido do banco.

O problema: os dois sistemas não falam a mesma língua. O interno usa **tickers de bolsa** (`PETR4`), enquanto o banco usa o **nome completo** (`PETROLEO BRASILEIRO S.A.`).

Além disso, erros operacionais podem gerar divergências de quantidade ou valor financeiro.

Seu trabalho é criar um **script que concilie as duas fontes e produza um relatório de exceções.**

# Arquivos de entrada

## `internal_system.json`

```json
[
  { "ticker": "PETR4", "quantidade": 1000, "financeiro": 35000.0 },
  { "ticker": "VALE3", "quantidade": 500, "financeiro": 32500.0 },
  { "ticker": "ITUB4", "quantidade": 200, "financeiro": 6400.0 },
  { "ticker": "BBDC4", "quantidade": 300, "financeiro": 4200.0 },
  { "ticker": "MGLU3", "quantidade": 150, "financeiro": 1200.0 },
  { "ticker": "WEGE3", "quantidade": 400, "financeiro": 22000.0 }
]
```

## `custodian_extract.csv`

```csv
Ativo,Quantidade,Saldo_Financeiro
PETROLEO BRASILEIRO S.A.,1000,35000.00
VALE S.A.,490,31850.00
ITAU UNIBANCO HOLDING S.A.,200,6400.05
MAGAZINE LUIZA S.A.,150,1200.00
WEG S.A.,420,23100.00
KNIP11,100,10500.00
HGLG11,50,7500.00
```

**Nota:** o **de-para entre os nomes do banco e os tickers do sistema interno faz parte do desafio** — você deve implementá-lo no seu script.


# O que você deve entregar

Um script na linguagem de sua preferência (**Python, R, SQL, VBA, JavaScript, etc.**) chamado **`conciliador`** que:

1. Leia os dois arquivos de entrada.
2. Trate a diferença de nomenclatura entre o sistema interno e o banco (**de-para de nomes**).
3. Compare **quantidade** e **valor financeiro** entre as duas fontes.
4. **Ignore diferenças financeiras menores que R$ 0,01.**
5. Gere um arquivo **`relatorio_final.csv`** com as colunas:

| Coluna             | Descrição                                                         |
| ------------------ | ----------------------------------------------------------------- |
| Ticker             | Ticker do ativo (use o ticker do sistema interno como referência) |
| Status             | Resultado da conciliação (valores possíveis abaixo)               |
| Divergencia_Qtde   | Quantidade do banco menos quantidade do sistema                   |
| Divergencia_Financ | Financeiro do banco menos financeiro do sistema                   |

---

# Valores possíveis para Status

| Valor             | Quando usar                                                          |
| ----------------- | -------------------------------------------------------------------- |
| OK                | Ativo conciliado sem divergências                                    |
| ERRO_QUANTIDADE   | Há diferença na quantidade entre sistema e banco                     |
| ERRO_FINANCEIRO   | Quantidade igual, mas diferença financeira >= R$ 0,01                |
| FALTANTE_NO_BANCO | Ativo existe no sistema interno, mas não aparece no extrato do banco |
| NAO_CADASTRADO    | Ativo aparece no extrato do banco, mas não existe no sistema interno |

# Critérios de Avaliação

* Clareza e organização do código
* Tratamento correto das diferenças de nomenclatura
* Identificação correta de todos os tipos de divergência
* **Robustez**: o script não deve quebrar com dados inesperados

# Como executar sua solução

No seu **README** ou nos comentários do script, inclua instruções para que consigamos rodar o seu código. No mínimo:

* Linguagem e versão utilizada (ex: **Python 3.11**, **Node 20**, **R 4.3**...)
* Dependências e como instalá-las

  * Exemplo:

  ```bash
  pip install -r requirements.txt
  ```
* Comando exato para executar o script

  * Exemplo:

  ```bash
  python conciliador.py
  ```

# Regras

* Use a linguagem de sua preferência (**Python, R, SQL, VBA, JavaScript, etc.**).
* O arquivo de saída deve ser um **CSV chamado `relatorio_final.csv`**.
* O foco **não é a velocidade**, mas a **qualidade do raciocínio**.
* Quando finalizar, **compacte todo o projeto em um arquivo `.zip` e envie por e-mail ou WhatsApp.**

---

**Boa sorte!**
