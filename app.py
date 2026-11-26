from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="Crédito consignado | Grupo 3", page_icon="📊", layout="wide")

DATA_PATH = Path(__file__).parent / "inadimplencia_consignado.csv"
PALETTE = {"Em dia": "#1f8a70", "Inadimplente": "#d45c4c"}
PAYER_PALETTE = {"inss": "#315f86", "federal": "#de9d38", "estadual": "#1f8a70", "municipal": "#d45c4c"}


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH, parse_dates=["data_contratacao"])
    df["status"] = df["inadimplente"].map({0: "Em dia", 1: "Inadimplente"})
    df["ano_mes"] = df["data_contratacao"].dt.to_period("M").dt.to_timestamp()
    return df


df = load_data()

st.markdown(
    """
    <style>
    .block-container {padding-top: 2rem; padding-bottom: 3rem; max-width: 1440px;}
    [data-testid="stMetric"] {background: #f5f7fa; color: #182331; border: 1px solid #e5e9ef; padding: 16px 18px; border-radius: 12px;}
    [data-testid="stMetricLabel"], [data-testid="stMetricValue"], [data-testid="stMetricDelta"] {color: #182331 !important;}
    h1, h2, h3 {letter-spacing: -0.02em;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Inadimplência em crédito consignado")
st.caption("Grupo 3 · Contratos de janeiro de 2023 a junho de 2025 · Cada linha representa um contrato")

with st.sidebar:
    st.header("Filtros")
    orgaos = sorted(df["orgao_pagador"].dropna().unique().tolist())
    orgao_selecionado = st.multiselect("Órgão pagador", orgaos, default=orgaos)
    canais = sorted(df["canal_contratacao"].dropna().unique().tolist())
    canal_selecionado = st.multiselect("Canal de contratação", canais, default=canais)
    min_date = df["data_contratacao"].min().date()
    max_date = df["data_contratacao"].max().date()
    periodo = st.date_input("Período de contratação", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    score_range = st.slider("Faixa de score", 0, 1000, (0, 1000), step=10)
    st.caption("A taxa é a proporção de contratos com inadimplência igual a 1 no recorte.")

if len(periodo) == 2:
    start_date, end_date = periodo
else:
    start_date = end_date = periodo[0]

filtered = df[
    df["orgao_pagador"].isin(orgao_selecionado)
    & df["canal_contratacao"].isin(canal_selecionado)
    & df["data_contratacao"].dt.date.between(start_date, end_date)
    & df["score_credito"].between(score_range[0], score_range[1])
].copy()

if filtered.empty:
    st.warning("Nenhum contrato corresponde aos filtros selecionados.")
    st.stop()

total = len(filtered)
taxa = filtered["inadimplente"].mean()
valor_medio = filtered["valor_emprestado"].mean()
score_medio = filtered["score_credito"].mean()

k1, k2, k3 = st.columns(3)
k1.metric("Contratos no recorte", f"{total:,.0f}".replace(",", "."))
k2.metric("Taxa de inadimplência", f"{taxa:.2%}".replace(".", ","))
k3.metric("Valor médio emprestado", f"R$ {valor_medio:,.0f}".replace(",", "."))
st.caption(f"Score médio no recorte: {score_medio:.0f} pontos · Os filtros afetam todos os gráficos e a tabela.")

st.divider()

st.header("Pergunta 1 · Como a inadimplência varia ao longo do tempo?")
monthly = filtered.groupby("ano_mes", as_index=False).agg(contratos=("id_contrato", "count"), taxa=("inadimplente", "mean"))
fig = px.line(monthly, x="ano_mes", y="taxa", markers=True, title="Taxa de inadimplência por mês de contratação", hover_data={"contratos": ":,", "taxa": ":.2%", "ano_mes": "|%b/%Y"},
              labels={"ano_mes": "Mês de contratação", "taxa": "Taxa de inadimplência", "contratos": "Contratos"})
fig.update_traces(line_color="#315f86", marker_color="#315f86", line_width=3)
fig.update_yaxes(tickformat=".0%", title="Contratos inadimplentes (%)")
fig.update_layout(margin=dict(l=10, r=10, t=55, b=10), hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)
st.info("Acompanhe a linha mensal e o volume de contratos no hover. As taxas oscilam entre as coortes; o recorte de jun/2025 registra 5,79% no conjunto completo.")

left, right = st.columns(2)
with left:
    st.header("Pergunta 2 · Quais grupos apresentam taxas diferentes?")
    payer = filtered.groupby("orgao_pagador", as_index=False).agg(contratos=("id_contrato", "count"), taxa=("inadimplente", "mean"))
    payer = payer.sort_values("taxa", ascending=True)
    fig2 = px.bar(payer, x="taxa", y="orgao_pagador", orientation="h", title="Taxa de inadimplência por órgão pagador", text=payer["taxa"].map(lambda x: f"{x:.1%}"),
                  hover_data={"contratos": ":,", "taxa": ":.2%"}, labels={"orgao_pagador": "Órgão pagador", "taxa": "Taxa de inadimplência", "contratos": "Contratos"}, color_discrete_sequence=["#477da5"])
    fig2.update_xaxes(tickformat=".0%", title="Contratos inadimplentes (%)")
    fig2.update_layout(margin=dict(l=5, r=10, t=55, b=10), showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)
    st.caption("No conjunto completo: municipal 10,58%; estadual 3,36%; INSS 3,04%; federal 0,65%.")

with right:
    st.subheader("Taxa por canal e órgão pagador")
    by_channel = filtered.groupby(["canal_contratacao", "orgao_pagador"], as_index=False).agg(contratos=("id_contrato", "count"), taxa=("inadimplente", "mean"))
    fig3 = px.bar(by_channel, x="canal_contratacao", y="taxa", color="orgao_pagador", barmode="group", title="Taxa por canal e órgão pagador",
                  hover_data={"contratos": ":,", "taxa": ":.2%"}, labels={"canal_contratacao": "Canal", "taxa": "Taxa de inadimplência", "orgao_pagador": "Órgão pagador", "contratos": "Contratos"},
                  color_discrete_map=PAYER_PALETTE)
    fig3.update_yaxes(tickformat=".0%", title="Contratos inadimplentes (%)")
    fig3.update_layout(margin=dict(l=5, r=10, t=55, b=10), legend_title="Órgão")
    st.plotly_chart(fig3, use_container_width=True)

st.divider()
st.header("Pergunta 3 · Como características de risco se associam à inadimplência?")
left, right = st.columns(2)
with left:
    score_plot = filtered.copy()
    score_plot["status"] = pd.Categorical(score_plot["status"], ["Em dia", "Inadimplente"], ordered=True)
    fig4 = px.box(score_plot, x="status", y="score_credito", color="status", points=False, title="Score de crédito por situação do contrato", color_discrete_map=PALETTE,
                  labels={"status": "Situação", "score_credito": "Score de crédito (pontos)"})
    fig4.update_layout(margin=dict(l=5, r=10, t=55, b=10), showlegend=False)
    st.plotly_chart(fig4, use_container_width=True)
    st.caption("Distribuição do score de crédito segundo a situação do contrato.")

with right:
    sample = filtered.sample(min(3500, len(filtered)), random_state=27) if len(filtered) > 3500 else filtered
    fig5 = px.scatter(sample, x="comprometimento_renda", y="valor_emprestado", color="status", opacity=0.48, title="Valor emprestado versus comprometimento da renda",
                      color_discrete_map=PALETTE, hover_data=["uf", "orgao_pagador", "canal_contratacao", "score_credito", "num_emprestimos_ativos"],
                      labels={"comprometimento_renda": "Parcela / renda (%)", "valor_emprestado": "Valor emprestado (R$)", "status": "Situação"})
    fig5.update_xaxes(tickformat=".0%")
    fig5.update_layout(margin=dict(l=5, r=10, t=55, b=10), legend_title="Situação")
    st.plotly_chart(fig5, use_container_width=True)
    st.caption("Cada ponto representa um contrato; a visualização limita a amostra a 3.500 pontos para facilitar a leitura.")

score_bins = pd.cut(filtered["score_credito"], [0, 400, 550, 700, 850, 1000], include_lowest=True,
                    labels=["0–400", "401–550", "551–700", "701–850", "851–1000"])
score_rates = filtered.assign(faixa_score=score_bins).groupby("faixa_score", observed=False, as_index=False).agg(contratos=("id_contrato", "count"), taxa=("inadimplente", "mean"))
fig6 = px.bar(score_rates, x="faixa_score", y="taxa", title="Taxa de inadimplência por faixa de score", text=score_rates["taxa"].map(lambda x: f"{x:.1%}" if pd.notna(x) else ""),
              hover_data={"contratos": ":,", "taxa": ":.2%"}, labels={"faixa_score": "Score (pontos)", "taxa": "Taxa de inadimplência", "contratos": "Contratos"}, color_discrete_sequence=["#de9d38"])
fig6.update_yaxes(tickformat=".0%", title="Contratos inadimplentes (%)")
fig6.update_layout(margin=dict(l=5, r=10, t=55, b=10), showlegend=False)
st.plotly_chart(fig6, use_container_width=True)
st.info("No conjunto completo, as faixas de score mais baixas concentram taxas maiores: 10,07% até 400 pontos, contra 1,17% entre 851 e 1.000 pontos. Associação descritiva não demonstra causalidade.")

st.divider()
st.header("Resumo por categoria")
summary = filtered.groupby("orgao_pagador", as_index=False).agg(
    contratos=("id_contrato", "count"),
    inadimplentes=("inadimplente", "sum"),
    taxa_inadimplencia=("inadimplente", "mean"),
    emprestimo_medio=("valor_emprestado", "mean"),
    score_medio=("score_credito", "mean"),
    parcela_media=("valor_parcela", "mean"),
)
summary["taxa_inadimplencia"] = summary["taxa_inadimplencia"].map(lambda x: f"{x:.2%}")
for col in ["emprestimo_medio", "parcela_media"]:
    summary[col] = summary[col].map(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
summary["score_medio"] = summary["score_medio"].round(0).astype("Int64")
summary = summary.rename(columns={"orgao_pagador": "Órgão pagador", "contratos": "Contratos", "inadimplentes": "Inadimplentes", "taxa_inadimplencia": "Taxa de inadimplência", "emprestimo_medio": "Empréstimo médio (R$)", "score_medio": "Score médio (pontos)", "parcela_media": "Parcela média (R$/mês)"})
st.dataframe(summary, use_container_width=True, hide_index=True)

with st.expander("Sobre os dados e os gráficos"):
    st.write("Base simulada de contratos de crédito consignado. O indicador inadimplente vale 1 quando houve atraso superior a 90 dias nos 12 meses seguintes à contratação. A taxa é calculada por contagem de contratos, sem ponderação pelo valor emprestado.")
    st.write("Fonte: arquivo distribuído para o Projeto 2, `inadimplencia_consignado.csv` (50.000 contratos; 17 colunas; 01/01/2023 a 30/06/2025).")
    st.write("Integrantes: Joao Victor Dumont Mauad · João Pedro Mansolelli · Rennan Destefani Siqueira Lopes")

