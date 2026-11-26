# Inadimplência em crédito consignado

Dashboard interativo desenvolvido em Streamlit para o Projeto 2, Grupo 3.

## Integrantes

- Joao Victor Dumont Mauad
- João Pedro Mansolelli
- Rennan Destefani Siqueira Lopes

## Executar localmente

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Publicar no Streamlit Community Cloud

1. Envie este diretório para um repositório público no GitHub.
2. Em Streamlit Community Cloud, conecte o repositório e selecione `app.py`.
3. O aplicativo lê `inadimplencia_consignado.csv` incluído neste projeto.

## Dados

O projeto usa os 50.000 registros do arquivo distribuído com o material do Projeto 2. Cada linha representa um contrato e `inadimplente = 1` indica atraso superior a 90 dias nos 12 meses seguintes à contratação. Não foi feita exclusão de linhas ou imputação de dados; o aplicativo calcula as estatísticas sobre o recorte indicado pelos filtros.

Os resultados são descritivos e mostram associações. Eles não identificam causas nem devem ser interpretados como avaliação de risco para decisões individuais.
