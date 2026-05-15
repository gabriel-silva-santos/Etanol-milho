# Análise e Previsão do Mercado de Etanol de Milho no Brasil 🌽⛽

Este projeto de Ciência de Dados explora o crescimento do etanol de milho no Brasil, integrando dados da ANP, CEPEA e CONAB para realizar análises de mercado e desenvolver um modelo preditivo de preços.

## 🎯 Objetivos
- **Análise de Mercado:** Avaliar a competitividade do etanol frente à gasolina.
- **Engenharia de Dados:** Consolidar mais de 1,4 milhão de registros públicos da ANP.
- **Machine Learning:** Prever o preço do etanol para o mês subsequente (t+1).

## 📂 Estrutura do Repositório
- `data/`: Datasets processados.
- `figures/`: Gráficos e Dashboard gerados na análise exploratória (EDA).
- `src/`: Scripts Python de coleta, limpeza, EDA e modelagem.
- `relatorio_tecnico.md`: Documentação detalhada dos insights.

## 📈 Principais Resultados
- O modelo de **Regressão Ridge** obteve o melhor desempenho com um erro médio (MAE) de apenas **R$ 0,05/litro**.
- Identificamos uma correlação de **0.99** entre o preço do milho e o etanol.
- O projeto demonstra o papel do etanol de milho como estabilizador de preços na entressafra da cana.

## 🚀 Como Executar
1. Instale as dependências: `pip install pandas numpy matplotlib seaborn scikit-learn`
2. Execute os scripts na ordem:
   ```bash
   python src/01_coleta_dados.py
   python src/02_limpeza_dados.py
   python src/03_eda.py
   python src/04_modelagem.py
