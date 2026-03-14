"""
Arquivo de configuração para o Conciliador de Custódia.
"""
# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
from pathlib import Path

# ---------------------------------------------------------------------------
# Caminhos dos arquivos
# ---------------------------------------------------------------------------
DIRETORIO_RAIZ = Path(__file__).parent

CAMINHO_SISTEMA_INTERNO = DIRETORIO_RAIZ / "internal_system.json"
CAMINHO_EXTRATO_CUSTODIANTE = DIRETORIO_RAIZ / "custodian_extract.csv"
CAMINHO_RELATORIO = DIRETORIO_RAIZ / "relatorio_final.csv"

# ---------------------------------------------------------------------------
# De-Para: nome usado pelo banco → ticker do sistema interno
# Adicione novos mapeamentos aqui conforme necessário.
# ---------------------------------------------------------------------------
DE_PARA: dict[str, str] = {
    "PETROLEO BRASILEIRO S.A.": "PETR4",
    "VALE S.A.": "VALE3",
    "ITAU UNIBANCO HOLDING S.A.": "ITUB4",
    "BRADESCO S.A.": "BBDC4",
    "MAGAZINE LUIZA S.A.": "MGLU3",
    "WEG S.A.": "WEGE3",
}

# ---------------------------------------------------------------------------
# Parâmetros de conciliação
# ---------------------------------------------------------------------------

# Diferença financeira mínima considerada relevante (em R$)
TOLERANCIA_FINANCEIRA = 0.01