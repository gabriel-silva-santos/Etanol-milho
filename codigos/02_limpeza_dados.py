import pandas as pd
import numpy as np
from pathlib import Path
import os

# Configurações de caminhos - Ajustado para ser mais flexível
# Ele vai procurar a pasta 'data' na mesma pasta onde o script está ou uma acima
BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

def realizar_limpeza_e_features():
    print("Iniciando Limpeza e Feature Engineering...")
    
    # Caminho do arquivo de entrada
    input_file = PROCESSED_DIR / "precos_mensais_etanol_milho.csv"
    
    if not input_file.exists():
        print(f"❌ ERRO: O arquivo {input_file} não foi encontrado!")
        return

    # 1. Carregar dados
    df = pd.read_csv(input_file)
    
    # 🛠️ CORREÇÃO: Forçar a conversão para datetime
    df['mes'] = pd.to_datetime(df['mes'], errors='coerce')
    
    # Verifica se a conversão deu certo
    if df['mes'].isnull().any():
        print("⚠️ Aviso: Algumas datas não foram reconhecidas e ficaram vazias.")

    # 2. Criar Features de Negócio
    df['relacao_etanol_gasolina'] = df['preco_etanol_hidratado_sp_R_L'] / df['preco_gasolina_comum_sp_R_L']
    df['razao_milho_etanol'] = df['preco_milho_campinas_R_sc60'] / df['preco_etanol_hidratado_sp_R_L']
    
    # 3. Lags e Médias Móveis
    for lag in [1, 2, 3, 6, 12]:
        df[f'etanol_lag_{lag}m'] = df['preco_etanol_hidratado_sp_R_L'].shift(lag)
        
    df['mm3_etanol'] = df['preco_etanol_hidratado_sp_R_L'].rolling(window=3).mean()
    df['mm12_etanol'] = df['preco_etanol_hidratado_sp_R_L'].rolling(window=12).mean()
    
    # 4. Sazonalidade (Agora o .dt vai funcionar!)
    df['mes_num'] = df['mes'].dt.month
    df['trimestre'] = df['mes'].dt.quarter
    
    # 5. Limpeza final (remove linhas com NaN criadas pelos lags)
    df_clean = df.dropna().reset_index(drop=True)
    
    # Salvar o dataset final
    output_path = PROCESSED_DIR / "dataset_master_clean.csv"
    df_clean.to_csv(output_path, index=False)
    
    print(f"✅ Sucesso! O arquivo '{output_path.name}' foi gerado com {len(df_clean)} linhas.")

if __name__ == "__main__":
    realizar_limpeza_e_features()
