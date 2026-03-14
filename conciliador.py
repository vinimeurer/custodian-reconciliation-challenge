"""
Script - Conciliador de Custódia

Compara as posições do sistema interno com o extrato recebido do custodiante,
identificando e classificando divergências de quantidade e valor financeiro.
"""
# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

import sys
import pandas as pd
from config import (
    DE_PARA, 
    TOLERANCIA_FINANCEIRA, 
    CAMINHO_SISTEMA_INTERNO, 
    CAMINHO_EXTRATO_CUSTODIANTE, 
    CAMINHO_RELATORIO
)



# ---------------------------------------------------------------------------
# Leitura dos arquivos de entrada
# ---------------------------------------------------------------------------


def carregar_sistema_interno(caminho: str) -> pd.DataFrame:
    """
    Carrega as posições do sistema interno a partir de um arquivo JSON.

    Parameters
        caminho (str): caminho do arquivo JSON.

    Returns
        DataFrame com colunas: Ticker, Qtde_Sistema, Financ_Sistema.
    """

    df = pd.read_json(caminho)
    df = df.rename(columns={"ticker": "Ticker", "quantidade": "Qtde_Sistema", "financeiro": "Financ_Sistema"})
    df["Qtde_Sistema"] = df["Qtde_Sistema"].astype(int)
    df["Financ_Sistema"] = df["Financ_Sistema"].astype(float)
    return df


def carregar_extrato_custodiante(caminho: str, depara: dict[str, str]) -> pd.DataFrame:
    """
    Carrega o extrato do custodiante a partir de um arquivo CSV e aplica o de-para
    para traduzir os nomes do banco para tickers do sistema interno.

    Parameters
        caminho (str): caminho do arquivo CSV.
        depara (dict): mapeamento no padrão {nome_banco: ticker}.

    Returns
        DataFrame com colunas: Ticker, Nome_Banco, Qtde_Banco, Financ_Banco.
    """

    df = pd.read_csv(caminho, dtype={"Quantidade": int, "Saldo_Financeiro": float})
    df = df.rename(columns={"Ativo": "Nome_Banco", "Quantidade": "Qtde_Banco", "Saldo_Financeiro": "Financ_Banco"})
    df["Nome_Banco"] = df["Nome_Banco"].str.strip()
    df["Ticker"] = df["Nome_Banco"].map(depara)
    return df


# ---------------------------------------------------------------------------
# Lógica de conciliação
# ---------------------------------------------------------------------------


def _classificar_status(row: pd.Series) -> str:
    """
    Classifica o status de uma linha já com as divergências calculadas.

    Parameters
        row (pd.Series): linha do DataFrame com Divergencia_Qtde e Divergencia_Financ.

    Returns
        String com o status: "OK", "ERRO_QUANTIDADE" ou "ERRO_FINANCEIRO".
    """

    if row["Divergencia_Qtde"] != 0:
        return "ERRO_QUANTIDADE"
    if abs(row["Divergencia_Financ"]) >= TOLERANCIA_FINANCEIRA:
        return "ERRO_FINANCEIRO"
    return "OK"


def conciliar(df_sistema: pd.DataFrame, df_banco: pd.DataFrame) -> pd.DataFrame:
    """
    Executa a conciliação entre sistema interno e extrato do custodiante.

    Realiza um full outer join pelos tickers e classifica cada ativo conforme
    as divergências encontradas.

    Parameters
        df_sistema (pd.DataFrame): posições do sistema interno.
        df_banco (pd.DataFrame): extrato do custodiante com ticker mapeado.

    Returns
        DataFrame com colunas: Ticker, Status, Divergencia_Qtde, Divergencia_Financ.
    """

    # Ativos do banco sem ticker mapeado são NAO_CADASTRADO antes do join
    sem_mapeamento = df_banco[df_banco["Ticker"].isna()].copy()
    df_banco_mapeado = df_banco[df_banco["Ticker"].notna()].copy()

    # Full outer join pelos tickers
    merged = pd.merge(
        df_sistema,
        df_banco_mapeado[["Ticker", "Qtde_Banco", "Financ_Banco"]],
        on="Ticker",
        how="outer",
    )

    # Ativos presentes apenas no banco (Qtde_Sistema NaN após o join)
    nao_cadastrados_via_join = merged[merged["Qtde_Sistema"].isna()].copy()
    merged = merged[merged["Qtde_Sistema"].notna()].copy()

    # Calcula divergências para os ativos em ambas as fontes ou faltantes no banco
    merged["Divergencia_Qtde"] = (merged["Qtde_Banco"].fillna(0) - merged["Qtde_Sistema"]).astype(int)
    merged["Divergencia_Financ"] = (merged["Financ_Banco"].fillna(0) - merged["Financ_Sistema"]).round(2)

    # Classifica os ativos que possuem par nos dois lados ou FALTANTE_NO_BANCO
    def status_com_faltante(row: pd.Series) -> str:
        if pd.isna(row["Qtde_Banco"]):
            return "FALTANTE_NO_BANCO"
        return _classificar_status(row)

    merged["Status"] = merged.apply(status_com_faltante, axis=1)

    relatorio = merged[["Ticker", "Status", "Divergencia_Qtde", "Divergencia_Financ"]].copy()

    # Adiciona NAO_CADASTRADO do join (ativos do banco sem correspondência no sistema)
    if not nao_cadastrados_via_join.empty:
        nao_cad_join = pd.DataFrame({
            "Ticker": nao_cadastrados_via_join["Ticker"],
            "Status": "NAO_CADASTRADO",
            "Divergencia_Qtde": nao_cadastrados_via_join["Qtde_Banco"].astype(int),
            "Divergencia_Financ": nao_cadastrados_via_join["Financ_Banco"].round(2),
        })
        relatorio = pd.concat([relatorio, nao_cad_join], ignore_index=True)

    # Adiciona NAO_CADASTRADO dos ativos sem mapeamento de-para
    if not sem_mapeamento.empty:
        nao_cad_sem_mapa = pd.DataFrame({
            "Ticker": sem_mapeamento["Nome_Banco"],
            "Status": "NAO_CADASTRADO",
            "Divergencia_Qtde": sem_mapeamento["Qtde_Banco"].astype(int),
            "Divergencia_Financ": sem_mapeamento["Financ_Banco"].round(2),
        })
        relatorio = pd.concat([relatorio, nao_cad_sem_mapa], ignore_index=True)

    return relatorio.reset_index(drop=True)


# ---------------------------------------------------------------------------
# Geração do relatório
# ---------------------------------------------------------------------------


def salvar_relatorio(relatorio: pd.DataFrame, caminho: str) -> None:
    """
    Salva o relatório de conciliação em um arquivo CSV.

    Parameters
        relatorio (pd.DataFrame): resultado da conciliação.
        caminho (Path): destino do arquivo CSV de saída.

    Returns
        None
    """
    relatorio.to_csv(caminho, index=False, encoding="utf-8")


def imprimir_resumo(relatorio: pd.DataFrame) -> None:
    """
    Exibe um resumo da conciliação no terminal.

    Parameters
        relatorio (pd.DataFrame): resultado da conciliação.

    Returns
        None
    """
    
    print(f"\n{'Ticker':<14} {'Status':<20} {'Div. Qtde':>10} {'Div. Financ':>14}")
    print("-" * 62)
    for _, row in relatorio.iterrows():
        print(
            f"{row['Ticker']:<14} "
            f"{row['Status']:<20} "
            f"{int(row['Divergencia_Qtde']):>10} "
            f"{row['Divergencia_Financ']:>14.2f}"
        )
    print("-" * 62)

    contagem = relatorio["Status"].value_counts()
    print(f"Total: {len(relatorio)} ativo(s)")
    for status, qtde in contagem.sort_index().items():
        print(f"  {status}: {qtde}")


# ---------------------------------------------------------------------------
# Ponto de entrada
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    for caminho in (CAMINHO_SISTEMA_INTERNO, CAMINHO_EXTRATO_CUSTODIANTE):
        if not caminho.exists():
            print(f"Erro: arquivo não encontrado → {caminho}", file=sys.stderr)
            sys.exit(1)

    df_sistema = carregar_sistema_interno(CAMINHO_SISTEMA_INTERNO)
    df_banco = carregar_extrato_custodiante(CAMINHO_EXTRATO_CUSTODIANTE, DE_PARA)

    relatorio = conciliar(df_sistema, df_banco)

    salvar_relatorio(relatorio, CAMINHO_RELATORIO)
    imprimir_resumo(relatorio)

    print(f"\nRelatório salvo em: {CAMINHO_RELATORIO}")
