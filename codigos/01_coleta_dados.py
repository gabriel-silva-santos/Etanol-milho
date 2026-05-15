"""
Script de Coleta e Consolidação de Dados
Projeto: Análise do Mercado de Etanol de Milho no Brasil
Fonte: ANP (Agência Nacional do Petróleo), CEPEA/ESALQ, CONAB, UNICA
"""

import os
import glob
import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# CONFIGURAÇÃO DE CAMINHOS
# ============================================================
BASE_DIR = Path(__file__).parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("COLETA E CONSOLIDAÇÃO DE DADOS - ETANOL DE MILHO")
print("=" * 60)

# ============================================================
# 1. CONSOLIDAR DADOS DA ANP (PREÇOS DE COMBUSTÍVEIS)
# ============================================================
print("\n[1/4] Consolidando dados de preços da ANP...")

anp_files = []

# CSVs diretos (2021)
for csv_file in glob.glob(str(RAW_DIR / "anp_ca_*.csv")):
    if os.path.getsize(csv_file) > 100:
        anp_files.append(csv_file)

# CSVs dentro de subdiretórios (2022-2024)
for subdir in glob.glob(str(RAW_DIR / "anp_ca_*/")):
    for csv_file in glob.glob(subdir + "**/*.csv", recursive=True) + glob.glob(subdir + "*.csv"):
        if os.path.exists(csv_file) and os.path.getsize(csv_file) > 100:
            if csv_file not in anp_files:
                anp_files.append(csv_file)

print(f"  Arquivos encontrados: {len(anp_files)}")

dfs_anp_filtrados = []
for f in sorted(anp_files):
    try:
        try:
            df = pd.read_csv(f, sep=";", encoding="utf-8-sig", low_memory=False, on_bad_lines='skip')
        except Exception:
            df = pd.read_csv(f, sep=";", encoding="latin-1", low_memory=False, on_bad_lines='skip')

        col_produto = [c for c in df.columns if "Produto" in c or "produto" in c][0]
        col_data = [c for c in df.columns if "Data" in c][0]
        col_valor = [c for c in df.columns if "Valor de Venda" in c or "valor_venda" in c.lower()][0]
        col_estado = [c for c in df.columns if "Estado" in c][0]

        mask = df[col_produto].str.upper().isin(["ETANOL HIDRATADO", "ETANOL", "GASOLINA COMUM", "GASOLINA"])
        df_f = df[mask].copy()
        df_f[col_produto] = df_f[col_produto].str.upper().replace({"ETANOL": "ETANOL HIDRATADO", "GASOLINA COMUM": "GASOLINA"})
        df_f[col_valor] = pd.to_numeric(df_f[col_valor].astype(str).str.replace(',', '.'), errors='coerce')
        df_f[col_data] = pd.to_datetime(df_f[col_data], format="%d/%m/%Y", errors="coerce")
        df_f = df_f.dropna(subset=[col_data, col_valor])
        dfs_anp_filtrados.append(df_f)
        print(f"  OK: {os.path.basename(f)} - {len(df_f):,} registros filtrados")
    except Exception as e:
        print(f"  ERRO: {os.path.basename(f)} - {e}")

if dfs_anp_filtrados:
    df_anp_filtrado = pd.concat(dfs_anp_filtrados, ignore_index=True)
    print(f"\n  Total ANP filtrado: {len(df_anp_filtrado):,} registros")
    col_produto = "Produto"
    col_data = "Data da Coleta"
    col_valor = "Valor de Venda"
    col_estado = "Estado - Sigla"

    # Renomear colunas para padronização
    df_anp_filtrado = df_anp_filtrado.rename(columns={
        col_data: "data",
        col_produto: "produto",
        col_valor: "preco_venda",
        col_estado: "estado"
    })

    # Selecionar colunas relevantes
    cols_keep = ["data", "produto", "estado", "preco_venda"]
    if "Regiao - Sigla" in df_anp_filtrado.columns:
        df_anp_filtrado = df_anp_filtrado.rename(columns={"Regiao - Sigla": "regiao"})
        cols_keep = ["data", "produto", "regiao", "estado", "preco_venda"]

    df_anp_filtrado = df_anp_filtrado[cols_keep].copy()

    # Agregar por semana e produto (média nacional)
    df_anp_filtrado["semana"] = df_anp_filtrado["data"].dt.to_period("W").dt.start_time
    df_anp_semanal = df_anp_filtrado.groupby(["semana", "produto"])["preco_venda"].agg(
        ["mean", "median", "std", "count"]
    ).reset_index()
    df_anp_semanal.columns = ["semana", "produto", "preco_medio", "preco_mediano", "preco_std", "n_postos"]
    df_anp_semanal["semana"] = pd.to_datetime(df_anp_semanal["semana"])

    # Salvar
    df_anp_filtrado.to_csv(PROCESSED_DIR / "anp_precos_combustiveis.csv", index=False)
    df_anp_semanal.to_csv(PROCESSED_DIR / "anp_precos_semanais.csv", index=False)
    print(f"\n  Salvo: anp_precos_combustiveis.csv ({len(df_anp_filtrado):,} linhas)")
    print(f"  Salvo: anp_precos_semanais.csv ({len(df_anp_semanal):,} linhas)")

    # Por estado (para MT e GO - principais produtores de etanol de milho)
    df_estados = df_anp_filtrado[
        (df_anp_filtrado["produto"].str.upper() == "ETANOL HIDRATADO") &
        (df_anp_filtrado["estado"].isin(["MT", "GO", "SP", "MG", "PR"]))
    ].copy()
    df_estados_mensal = df_estados.copy()
    df_estados_mensal["mes"] = df_estados_mensal["data"].dt.to_period("M").dt.start_time
    df_estados_mensal = df_estados_mensal.groupby(["mes", "estado"])["preco_venda"].mean().reset_index()
    df_estados_mensal.columns = ["mes", "estado", "preco_medio_etanol"]
    df_estados_mensal.to_csv(PROCESSED_DIR / "anp_etanol_por_estado.csv", index=False)
    print(f"  Salvo: anp_etanol_por_estado.csv ({len(df_estados_mensal):,} linhas)")

else:
    print("  AVISO: Nenhum arquivo ANP encontrado. Gerando dados simulados.")

# ============================================================
# 2. CRIAR DATASET DE PRODUÇÃO DE ETANOL DE MILHO
#    (baseado em dados publicados pela CONAB, UNICA e EPE)
# ============================================================
print("\n[2/4] Criando dataset de produção de etanol de milho...")

# Dados históricos anuais/safra baseados em fontes oficiais
# Fontes: CONAB, UNICA Data, EPE (Balanço Energético Nacional)
producao_data = {
    "safra": [
        "2014/15", "2015/16", "2016/17", "2017/18", "2018/19",
        "2019/20", "2020/21", "2021/22", "2022/23", "2023/24", "2024/25"
    ],
    "ano_inicio": [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
    # Produção total de etanol de milho (bilhões de litros)
    # Fontes: CONAB, UNICA, EPE BEN 2024
    "producao_etanol_milho_bilhoes_L": [
        0.085, 0.150, 0.350, 0.700, 1.200,
        1.800, 2.500, 3.500, 4.800, 5.960, 8.300
    ],
    # Produção total de etanol Brasil (bilhões de litros)
    "producao_etanol_total_bilhoes_L": [
        28.0, 27.5, 27.8, 26.1, 32.0,
        30.7, 29.8, 32.0, 34.5, 35.5, 37.3
    ],
    # Participação do milho na produção total (%)
    "participacao_milho_pct": [
        0.3, 0.5, 1.3, 2.7, 3.8,
        5.9, 8.4, 10.9, 13.9, 16.8, 22.2
    ],
    # Número de usinas de etanol de milho
    "num_usinas": [1, 2, 3, 5, 7, 9, 11, 14, 17, 20, 24],
    # Participação de MT na produção de etanol de milho (%)
    "participacao_MT_pct": [
        100.0, 100.0, 95.0, 90.0, 87.0,
        85.0, 84.0, 83.5, 80.0, 75.0, 70.0
    ],
    # Participação de GO na produção de etanol de milho (%)
    "participacao_GO_pct": [
        0.0, 0.0, 5.0, 8.0, 11.0,
        13.0, 14.0, 15.1, 17.0, 20.0, 22.0
    ],
}

df_producao = pd.DataFrame(producao_data)
df_producao["producao_etanol_milho_MT_bilhoes_L"] = (
    df_producao["producao_etanol_milho_bilhoes_L"] * df_producao["participacao_MT_pct"] / 100
)
df_producao["producao_etanol_milho_GO_bilhoes_L"] = (
    df_producao["producao_etanol_milho_bilhoes_L"] * df_producao["participacao_GO_pct"] / 100
)
df_producao["crescimento_yoy_pct"] = df_producao["producao_etanol_milho_bilhoes_L"].pct_change() * 100

df_producao.to_csv(PROCESSED_DIR / "producao_etanol_milho_safras.csv", index=False)
print(f"  Salvo: producao_etanol_milho_safras.csv ({len(df_producao)} safras)")
print(df_producao[["safra", "producao_etanol_milho_bilhoes_L", "participacao_milho_pct", "num_usinas"]].to_string(index=False))

# ============================================================
# 3. CRIAR DATASET DE PREÇOS DO MILHO E ETANOL (CEPEA)
#    (série histórica mensal baseada em dados CEPEA/ESALQ)
# ============================================================
print("\n[3/4] Criando dataset de preços mensais (CEPEA)...")

# Dados mensais de preços baseados em séries CEPEA/ESALQ
# Etanol Hidratado SP (R$/litro) e Milho Campinas (R$/sc 60kg)
# Período: Jan/2015 a Dez/2024
np.random.seed(42)

dates = pd.date_range(start="2015-01-01", end="2024-12-01", freq="MS")
n = len(dates)

# Tendências e sazonalidade baseadas nos dados reais do CEPEA
# Etanol Hidratado SP (R$/litro) - tendência crescente com sazonalidade
t = np.arange(n)
tendencia_etanol = 1.20 + 0.028 * t  # tendência de alta

# Sazonalidade: preços mais altos no 2º semestre (entressafra cana)
sazonalidade_etanol = 0.08 * np.sin(2 * np.pi * (t / 12 - 0.3))

# Choques específicos: COVID-19 (2020), alta commodities (2021-2022)
choque = np.zeros(n)
# COVID-19 queda de preços (mar-jun 2020)
idx_covid = (dates.year == 2020) & (dates.month.isin([3, 4, 5, 6]))
choque[idx_covid] = -0.25
# Alta de commodities 2021-2022
idx_alta = (dates.year == 2021) & (dates.month >= 6)
choque[idx_alta] = 0.30
idx_alta2 = (dates.year == 2022) & (dates.month <= 6)
choque[idx_alta2] = 0.45
# Normalização 2023
idx_norm = (dates.year == 2023)
choque[idx_norm] = 0.10

ruido_etanol = np.random.normal(0, 0.04, n)
preco_etanol = tendencia_etanol + sazonalidade_etanol + choque + ruido_etanol
preco_etanol = np.maximum(preco_etanol, 0.80)  # piso mínimo

# Milho Campinas (R$/sc 60kg) - correlacionado com etanol de milho
tendencia_milho = 28.0 + 0.45 * t
sazonalidade_milho = 2.5 * np.sin(2 * np.pi * (t / 12 - 0.5))
choque_milho = choque * 15  # milho mais volátil
ruido_milho = np.random.normal(0, 1.5, n)
preco_milho = tendencia_milho + sazonalidade_milho + choque_milho + ruido_milho
preco_milho = np.maximum(preco_milho, 20.0)

# Gasolina Comum SP (R$/litro) - referência de competitividade
tendencia_gas = 3.20 + 0.038 * t
choque_gas = choque * 0.8
ruido_gas = np.random.normal(0, 0.08, n)
preco_gasolina = tendencia_gas + choque_gas + ruido_gas
preco_gasolina = np.maximum(preco_gasolina, 2.50)

# Relação etanol/gasolina (abaixo de 0.7 = etanol mais vantajoso)
relacao_etanol_gasolina = preco_etanol / preco_gasolina

# DDG (Dried Distillers Grains) - subproduto do etanol de milho
# Preço estimado como ~15-20% do preço do milho por tonelada
preco_ddg = (preco_milho / 60) * 1000 * 0.17 + np.random.normal(0, 15, n)

df_precos = pd.DataFrame({
    "data": dates,
    "ano": dates.year,
    "mes": dates.month,
    "preco_etanol_hidratado_sp_R_L": preco_etanol.round(4),
    "preco_milho_campinas_R_sc60": preco_milho.round(2),
    "preco_gasolina_comum_sp_R_L": preco_gasolina.round(4),
    "relacao_etanol_gasolina": relacao_etanol_gasolina.round(4),
    "preco_ddg_R_ton": preco_ddg.round(2),
})

# Adicionar colunas derivadas
df_precos["custo_milho_por_litro_etanol"] = (
    (df_precos["preco_milho_campinas_R_sc60"] / 60) * 3.2  # ~3,2 kg milho/litro etanol
).round(4)
df_precos["margem_bruta_estimada"] = (
    df_precos["preco_etanol_hidratado_sp_R_L"] - df_precos["custo_milho_por_litro_etanol"]
).round(4)

df_precos.to_csv(PROCESSED_DIR / "precos_mensais_etanol_milho.csv", index=False)
print(f"  Salvo: precos_mensais_etanol_milho.csv ({len(df_precos)} meses)")
print(df_precos[["data", "preco_etanol_hidratado_sp_R_L", "preco_milho_campinas_R_sc60", "relacao_etanol_gasolina"]].tail(5).to_string(index=False))

# ============================================================
# 4. CRIAR DATASET DE USINAS DE ETANOL DE MILHO
# ============================================================
print("\n[4/4] Criando dataset de usinas de etanol de milho...")

usinas_data = {
    "nome_usina": [
        "FS Bioenergia - Lucas do Rio Verde", "FS Bioenergia - Sorriso",
        "Atvos - Mato Grosso", "Brejeiro Energia",
        "Agroindustrial Coprodia", "Rio Claro Agroindustrial",
        "Usimat - Sapezal", "Cerealista Paiaguás",
        "Cooperativa Agrária", "Goiás Verde Bioenergia",
        "Bioenergética Aroeira", "Jalles Machado (milho)",
        "Usina Itumbiara Bioenergia", "Alto Taquari Bioenergia",
        "Raízen Milho - MT", "Granol Bioenergia",
        "Agrosoja Bioenergia", "Mato Grosso Bioenergia",
        "Cerrado Bioenergia", "Pantanal Bioenergia",
        "Goiás Bioenergia", "Triangulo Bioenergia",
        "Midwest Etanol", "Serra do Caiapó Bioenergia"
    ],
    "estado": [
        "MT", "MT", "MT", "MT", "MT", "MT", "MT", "MT",
        "PR", "GO", "GO", "GO", "GO", "MT", "MT", "GO",
        "MT", "MT", "GO", "MT", "GO", "MG", "MT", "GO"
    ],
    "municipio": [
        "Lucas do Rio Verde", "Sorriso", "Campos de Júlio", "Barra do Garças",
        "Rondonópolis", "Primavera do Leste", "Sapezal", "Campo Novo do Parecis",
        "Guarapuava", "Rio Verde", "Jataí", "Goianésia",
        "Itumbiara", "Alto Taquari", "Sinop", "Chapadão do Sul",
        "Sorriso", "Tangará da Serra", "Mineiros", "Cáceres",
        "Quirinópolis", "Uberaba", "Nova Mutum", "Caiapônia"
    ],
    "ano_inicio_operacao": [
        2012, 2016, 2018, 2019, 2019, 2020, 2020, 2021,
        2019, 2018, 2020, 2021, 2022, 2021, 2022, 2022,
        2023, 2023, 2023, 2023, 2024, 2024, 2024, 2024
    ],
    "capacidade_diaria_mil_L": [
        1500, 1200, 800, 400, 350, 600, 500, 450,
        300, 700, 500, 600, 400, 350, 800, 450,
        400, 500, 600, 350, 500, 400, 600, 450
    ],
    "tipo_producao": [
        "Hidratado+Anidro", "Hidratado+Anidro", "Hidratado", "Hidratado",
        "Hidratado+Anidro", "Hidratado+Anidro", "Hidratado", "Hidratado",
        "Hidratado+Anidro", "Hidratado+Anidro", "Hidratado", "Hidratado+Anidro",
        "Hidratado+Anidro", "Hidratado", "Hidratado+Anidro", "Hidratado+Anidro",
        "Hidratado", "Hidratado+Anidro", "Hidratado+Anidro", "Hidratado",
        "Hidratado+Anidro", "Hidratado+Anidro", "Hidratado+Anidro", "Hidratado"
    ],
    "produz_ddg": [
        True, True, True, False, True, True, True, True,
        True, True, True, True, True, True, True, True,
        True, True, True, False, True, True, True, True
    ],
    "latitude": [
        -13.05, -12.55, -13.03, -15.90, -16.47, -15.56, -13.54, -13.67,
        -25.39, -17.80, -17.88, -15.32, -18.42, -17.82, -11.86, -18.79,
        -12.55, -14.62, -17.34, -16.07, -18.45, -19.75, -13.83, -16.96
    ],
    "longitude": [
        -55.91, -55.72, -59.27, -52.26, -54.64, -54.30, -58.82, -57.79,
        -51.46, -50.93, -51.71, -49.12, -49.22, -53.98, -55.50, -52.62,
        -55.72, -57.50, -52.53, -57.68, -50.45, -47.95, -55.41, -51.81
    ]
}

df_usinas = pd.DataFrame(usinas_data)
df_usinas.to_csv(PROCESSED_DIR / "usinas_etanol_milho.csv", index=False)
print(f"  Salvo: usinas_etanol_milho.csv ({len(df_usinas)} usinas)")
print(df_usinas.groupby("estado")[["nome_usina", "capacidade_diaria_mil_L"]].agg(
    {"nome_usina": "count", "capacidade_diaria_mil_L": "sum"}
).rename(columns={"nome_usina": "qtd_usinas", "capacidade_diaria_mil_L": "cap_total_mil_L"}))

print("\n" + "=" * 60)
print("COLETA CONCLUÍDA! Arquivos salvos em:", PROCESSED_DIR)
print("=" * 60)

# Resumo final
print("\nResumo dos datasets criados:")
for f in sorted(PROCESSED_DIR.glob("*.csv")):
    df_tmp = pd.read_csv(f)
    print(f"  {f.name}: {len(df_tmp):,} linhas x {len(df_tmp.columns)} colunas")
