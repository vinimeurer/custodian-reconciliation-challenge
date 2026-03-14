# Conciliador de Custódia

## Sumário
- [Visão Geral](#visão-geral)
- [Configuração do Ambiente](#configuração-do-ambiente)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Configuração](#configuração)
- [Arquivos de Entrada e Saída](#arquivos-de-entrada-e-saída)
- [Como Executar](#como-executar)
- [Valores de Status](#valores-de-status)
- [Observações](#observações)


## Visão Geral

Script de conciliação entre o sistema interno de uma Gestora de Recursos e o extrato recebido do custodiante. O script compara as posições dos dois sistemas, identificando e classificando divergências de quantidade e valor financeiro.


## Configuração do Ambiente

1. **Clone o repositório:**
   ```sh
   git clone <url-do-repositorio>
   ```

2. **Entre no diretório:**
   ```sh
   cd custodian-reconciliation-challenge
   ```

3. **Criação do ambiente virtual:**
   ```sh
   python3 -m venv .venv
   ```

4. **Ative o ambiente virtual:**
   - Linux/macOS:
     ```sh
     source .venv/bin/activate
     ```
   - Windows:
     ```sh
     .venv\Scripts\activate
     ```

5. **Instalação das dependências:**
   ```sh
   pip install -r requirements.txt
   ```


## Estrutura do Projeto

```
custodian-reconciliation-challenge/
    ├── conciliador.py          # Script principal de conciliação
    ├── config.py               # Configurações: caminhos, de-para e parâmetros
    ├── internal_system.json    # Posições do sistema interno (entrada)
    ├── custodian_extract.csv   # Extrato do custodiante (entrada)
    ├── relatorio_final.csv     # Relatório gerado ao executar o script (saída)
    ├── requirements.txt        # Dependências Python
    └── README.md               # Documentação do projeto
```


## Configuração

Todas as configurações ficam centralizadas em `config.py`:

| Parâmetro | Descrição |
| --------- | --------- |
| `CAMINHO_SISTEMA_INTERNO` | Caminho para o arquivo JSON do sistema interno |
| `CAMINHO_EXTRATO_CUSTODIANTE` | Caminho para o CSV do extrato do custodiante |
| `CAMINHO_RELATORIO` | Caminho de saída do relatório CSV |
| `DE_PARA` | Dicionário de mapeamento nome banco → ticker |
| `TOLERANCIA_FINANCEIRA` | Diferença financeira mínima relevante (padrão: R$ 0,01) |

Para adicionar novos ativos ao mapeamento, edite o dicionário `DE_PARA` em `config.py`:

```python
DE_PARA: dict[str, str] = {
    "NOME USADO PELO BANCO": "TICKER",
    ...
}
```


## Arquivos de Entrada e Saída

### Entrada

| Arquivo | Descrição |
| ------- | --------- |
| `internal_system.json` | Posições consolidadas do sistema interno (ticker, quantidade, financeiro) |
| `custodian_extract.csv` | Extrato recebido do custodiante (nome completo do ativo, quantidade, saldo financeiro) |

### Saída

`relatorio_final.csv` — gerado na mesma pasta do script, com as colunas:

| Coluna | Descrição |
| ------ | --------- |
| `Ticker` | Ticker do ativo (referência do sistema interno) |
| `Status` | Resultado da conciliação |
| `Divergencia_Qtde` | Quantidade banco − quantidade sistema |
| `Divergencia_Financ` | Financeiro banco − financeiro sistema |


## Como Executar

```bash
python3 conciliador.py
```

O script imprime um resumo no terminal e salva o `relatorio_final.csv` na mesma pasta.


## Valores de Status

| Status | Condição |
| ------ | --------- |
| `OK` | Sem divergências |
| `ERRO_QUANTIDADE` | Diferença de quantidade entre sistema e banco |
| `ERRO_FINANCEIRO` | Quantidade igual, mas divergência financeira ≥ R$ 0,01 |
| `FALTANTE_NO_BANCO` | Ativo no sistema interno, ausente no extrato do banco |
| `NAO_CADASTRADO` | Ativo no extrato do banco, ausente no sistema interno |

## Observações
- O script é idempotente: pode ser executado várias vezes sem alterar o resultado, desde que os arquivos de entrada permaneçam os mesmos.
- A tolerância financeira pode ser ajustada em `config.py` para considerar divergências menores como irrelevantes.
- Para mais detalhes, consulte os arquivos descritivos do desafio [challenge.pdf](./challenge.pdf) ou [challenge.md](./challenge.md).