# Inadimplência em crédito consignado

Dashboard interativo em Streamlit desenvolvido para o Projeto 2, Grupo 3.

**Dashboard público:** [abrir o painel](https://inadimplencia-consignado-dashboard-gvxfjzdjg4xyf65qee79dw.streamlit.app/)  
**Repositório do projeto:** [jpmansolelli/inadimplencia-consignado-dashboard](https://github.com/jpmansolelli/inadimplencia-consignado-dashboard)  
**Download da base CSV:** [inadimplencia_consignado.csv](https://raw.githubusercontent.com/jpmansolelli/inadimplencia-consignado-dashboard/main/inadimplencia_consignado.csv)

## Integrantes

- Joao Victor Dumont Mauad
- João Pedro Mansolelli
- Rennan Destefani Siqueira Lopes

## Executar localmente

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Dados e método

A base acompanha o material do Projeto 2 e contém 50.000 contratos, 17 colunas e contratações entre 01/01/2023 e 30/06/2025. Cada linha representa um contrato; `inadimplente = 1` indica atraso superior a 90 dias nos 12 meses seguintes à contratação.

Não foram removidas linhas nem imputados valores. O app converte a data de contratação para data e agrega os registros para as visualizações. Os filtros afetam todos os gráficos e a tabela. Os resultados são descritivos; diferenças observadas não demonstram causalidade nem devem ser usadas para decisões individuais de crédito.


