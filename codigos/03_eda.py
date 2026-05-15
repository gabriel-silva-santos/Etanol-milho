import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Configurações de estilo
plt.style.use('ggplot')
sns.set_theme(style="whitegrid")

# Caminhos
BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
FIGURES_DIR = BASE_DIR / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

def gerar_visualizacoes():
    print("Gerando visualizações da EDA...")
    
    # 1. Carregar dados limpos
    df = pd.read_csv(PROCESSED_DIR / "dataset_master_clean.csv", parse_dates=['mes'])
    
    # --- GRÁFICO 1: Séries Temporais de Preços ---
    plt.figure(figsize=(12, 6))
    plt.plot(df['mes'], df['preco_etanol_hidratado_sp_R_L'], label='Etanol Hidratado (SP)', color='#2E8B57', lw=2)
    plt.plot(df['mes'], df['preco_gasolina_comum_sp_R_L'], label='Gasolina Comum (SP)', color='#DAA520', lw=2)
    plt.title('Evolução de Preços: Etanol vs Gasolina', fontsize=14, fontweight='bold')
    plt.ylabel('Preço (R$/Litro)')
    plt.legend()
    plt.savefig(FIGURES_DIR / "01_tendencia_precos.png", dpi=150)
    plt.close()

    # --- GRÁFICO 2: Competitividade (Paridade 70%) ---
    plt.figure(figsize=(12, 6))
    plt.plot(df['mes'], df['relacao_etanol_gasolina'], color='purple', lw=2)
    plt.axhline(y=0.70, color='red', linestyle='--', label='Ponto de Paridade (70%)')
    plt.fill_between(df['mes'], df['relacao_etanol_gasolina'], 0.70, 
                     where=(df['relacao_etanol_gasolina'] < 0.70), color='green', alpha=0.3, label='Etanol Competitivo')
    plt.title('Competitividade do Etanol em relação à Gasolina', fontsize=14, fontweight='bold')
    plt.ylabel('Relação de Preço (Etanol/Gasolina)')
    plt.legend()
    plt.savefig(FIGURES_DIR / "02_competitividade.png", dpi=150)
    plt.close()

    # --- GRÁFICO 3: Matriz de Correlação ---
    plt.figure(figsize=(10, 8))
    cols_corr = ['preco_etanol_hidratado_sp_R_L', 'preco_milho_campinas_R_sc60', 
                 'preco_gasolina_comum_sp_R_L', 'relacao_etanol_gasolina', 'mm12_etanol']
    sns.heatmap(df[cols_corr].corr(), annot=True, cmap='RdYlGn', fmt=".2f")
    plt.title('Matriz de Correlação entre Variáveis', fontsize=14, fontweight='bold')
    plt.savefig(FIGURES_DIR / "03_correlacoes.png", dpi=150)
    plt.close()

    # --- GRÁFICO 4: Dashboard Resumo (O "Grand Finale") ---
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle('Dashboard: Mercado de Etanol de Milho no Brasil', fontsize=20, fontweight='bold')

    # Top Esquerda: Milho vs Etanol
    axes[0,0].scatter(df['preco_milho_campinas_R_sc60'], df['preco_etanol_hidratado_sp_R_L'], alpha=0.6, color='orange')
    axes[0,0].set_title('Correlação Milho vs Etanol')
    axes[0,0].set_xlabel('Preço Milho (R$/Saca)')
    axes[0,0].set_ylabel('Preço Etanol (R$/L)')

    # Top Direita: Sazonalidade Mensal
    sns.boxplot(x='mes_num', y='preco_etanol_hidratado_sp_R_L', data=df, ax=axes[0,1], palette='viridis')
    axes[0,1].set_title('Sazonalidade Mensal de Preços')
    axes[0,1].set_xlabel('Mês')

    # Bottom Esquerda: Distribuição da Relação de Preço
    sns.histplot(df['relacao_etanol_gasolina'], kde=True, ax=axes[1,0], color='skyblue')
    axes[1,0].set_title('Distribuição da Paridade Etanol/Gasolina')

    # Bottom Direita: Tendência de Longo Prazo (Médias Móveis)
    axes[1,1].plot(df['mes'], df['preco_etanol_hidratado_sp_R_L'], alpha=0.3, label='Real')
    axes[1,1].plot(df['mes'], df['mm12_etanol'], color='red', label='Tendência (MM12)')
    axes[1,1].set_title('Tendência de Longo Prazo')
    axes[1,1].legend()

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(FIGURES_DIR / "04_dashboard_resumo.png", dpi=200)
    plt.close()

    print(f"✅ Sucesso! 4 gráficos gerados na pasta: {FIGURES_DIR}")

if __name__ == "__main__":
    gerar_visualizacoes()
