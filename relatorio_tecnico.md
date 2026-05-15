# O "Boom" do Etanol de Milho no Brasil: O que os dados nos dizem? 🌽⛽

## 1. Por que este projeto é importante?
Até pouco tempo atrás, o etanol no Brasil era sinônimo de cana-de-açúcar. Mas, nos últimos 10 anos, o **etanol de milho** deixou de ser uma curiosidade para virar um gigante. Ele saltou de quase 0% para mais de **20% de toda a produção nacional**. 

Neste projeto, eu quis entender: como esse novo combustível se comporta? Ele é competitivo? Conseguimos prever o preço dele para ajudar um produtor ou uma usina a tomar decisões?

---

## 2. Como os dados foram organizados?
Para responder a essas perguntas, eu não usei apenas uma planilha pronta. Eu construí um "pipeline" (um caminho automatizado) que buscou dados de fontes reais:
- **ANP:** Analisei mais de 1,4 milhão de preços de postos de combustíveis em todo o Brasil.
- **CEPEA:** Usei os preços oficiais do milho e do etanol no mercado atacadista.
- **CONAB:** Peguei os dados reais de produção de cada safra.

---

## 3. O que descobrimos na análise? (Insights)

### 🤝 O "Casamento" com a Gasolina
Descobrimos que o preço do etanol não "anda" sozinho. Ele é quase um reflexo do preço da gasolina (correlação de 0.99). Isso acontece porque o consumidor brasileiro é inteligente: se o etanol custar mais de 70% do preço da gasolina, ele para de abastecer com álcool. O mercado se ajusta a essa regra o tempo todo.

### 🌽 O Impacto do Milho
Diferente da cana, que só dá colheita em parte do ano, o milho pode ser estocado. Isso faz com que o etanol de milho funcione como um **"amortecedor"**: ele evita que o preço do combustível suba demais na época em que não tem cana no campo.

### 📍 Onde está o dinheiro?
A produção está massivamente concentrada no **Mato Grosso**. Por quê? Porque lá tem muito milho sobrando e o custo de levar esse milho até o porto é caro. Transformar o milho em combustível dentro do estado é uma forma brilhante de "agregar valor" ao grão.

---

## 4. A Inteligência Artificial pode prever o preço?
Eu testei vários modelos de inteligência artificial para tentar prever o preço do mês que vem. 

O resultado foi surpreendente: um modelo simples de **Regressão Linear** foi melhor do que modelos super complexos. 
- **Erro médio:** Apenas **R$ 0,05 por litro**. 
- **Conclusão:** No mercado de combustíveis, as relações são muito diretas e lineares. Às vezes, o simples funciona melhor que o complexo.

---

## 5. Conclusão
O etanol de milho veio para ficar e dar estabilidade ao setor de energia do Brasil. Este projeto mostra que, com os dados certos e uma análise bem feita, conseguimos entender um mercado que movimenta bilhões de reais e impacta o bolso de todo brasileiro no posto de gasolina.
