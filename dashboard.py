# dashboard.py - Dashboard interativo com Streamlit

import json
import os
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime
from config import PROCESSED_LOGS_FILE

st.set_page_config(
    page_title="Fraud Detector Dashboard",
    page_icon="🔐",
    layout="wide",
)


@st.cache_data(ttl=30)
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Carrega e separa logs normais e suspeitos."""
    if not os.path.exists(PROCESSED_LOGS_FILE):
        return pd.DataFrame(), pd.DataFrame()

    with open(PROCESSED_LOGS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not data:
        return pd.DataFrame(), pd.DataFrame()

    df = pd.json_normalize(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["classification"] = df.get("analysis.classification", "INDETERMINADO")

    suspicious = df[df["classification"].str.contains("SUSPEITO", na=False)].copy()
    return df, suspicious


def render_metrics(df: pd.DataFrame, suspicious: pd.DataFrame):
    col1, col2, col3, col4 = st.columns(4)
    total = len(df)
    n_sus = len(suspicious)
    rate = round(n_sus / total * 100, 1) if total > 0 else 0

    col1.metric("📋 Total Analisado", total)
    col2.metric("🚨 Suspeitos / Fraude", n_sus)
    col3.metric("✅ Normais", total - n_sus)
    col4.metric("📊 Taxa de Fraude", f"{rate}%")


def render_event_type_chart(suspicious: pd.DataFrame):
    st.subheader("📌 Distribuição por Tipo de Evento (Suspeitos)")
    if suspicious.empty or "event_type" not in suspicious.columns:
        st.info("Sem dados suficientes.")
        return
    counts = suspicious["event_type"].value_counts().reset_index()
    counts.columns = ["Tipo de Evento", "Quantidade"]
    fig = px.bar(counts, x="Tipo de Evento", y="Quantidade", color="Tipo de Evento",
                 color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(fig, use_container_width=True)


def render_timeline_chart(suspicious: pd.DataFrame):
    st.subheader("📈 Tendência de Fraudes ao Longo do Tempo")
    if suspicious.empty or "timestamp" not in suspicious.columns:
        st.info("Sem dados suficientes.")
        return
    timeline = suspicious.set_index("timestamp").resample("h").size().reset_index()
    timeline.columns = ["Hora", "Ocorrências"]
    fig = px.line(timeline, x="Hora", y="Ocorrências", markers=True,
                  color_discrete_sequence=["#EF553B"])
    st.plotly_chart(fig, use_container_width=True)


def render_top_users(suspicious: pd.DataFrame):
    st.subheader("👤 Usuários Mais Frequentes em Fraudes")
    if suspicious.empty or "user_id" not in suspicious.columns:
        st.info("Sem dados suficientes.")
        return
    top_users = suspicious["user_id"].value_counts().head(10).reset_index()
    top_users.columns = ["Usuário", "Ocorrências"]
    fig = px.bar(top_users, x="Ocorrências", y="Usuário", orientation="h",
                 color="Ocorrências", color_continuous_scale="Reds")
    st.plotly_chart(fig, use_container_width=True)


def render_top_ips(suspicious: pd.DataFrame):
    st.subheader("🌐 IPs Mais Frequentes em Fraudes")
    if suspicious.empty or "source_ip" not in suspicious.columns:
        st.info("Sem dados suficientes.")
        return
    top_ips = suspicious["source_ip"].value_counts().head(10).reset_index()
    top_ips.columns = ["IP", "Ocorrências"]
    fig = px.bar(top_ips, x="Ocorrências", y="IP", orientation="h",
                 color="Ocorrências", color_continuous_scale="Oranges")
    st.plotly_chart(fig, use_container_width=True)


def render_suspicious_table(suspicious: pd.DataFrame):
    st.subheader("🗂️ Eventos Suspeitos Recentes")
    if suspicious.empty:
        st.info("Nenhum evento suspeito encontrado.")
        return

    cols = ["timestamp", "user_id", "event_type", "source_ip", "status", "analysis.justification"]
    available = [c for c in cols if c in suspicious.columns]
    display = suspicious[available].sort_values("timestamp", ascending=False).head(50)
    display.columns = [c.replace("analysis.", "") for c in display.columns]

    # Filtros
    if "event_type" in display.columns:
        event_filter = st.multiselect("Filtrar por tipo de evento:",
                                      options=display["event_type"].unique().tolist(),
                                      default=display["event_type"].unique().tolist())
        display = display[display["event_type"].isin(event_filter)]

    st.dataframe(display, use_container_width=True)


# ── Layout principal ───────────────────────────────────────────────────────────

st.title("🔐 Fraud Detector Dashboard")
st.caption(f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

if st.button("🔄 Atualizar dados"):
    st.cache_data.clear()
    st.rerun()

df, suspicious = load_data()

if df.empty:
    st.warning("⚠️ Nenhum dado encontrado. Execute a análise de logs primeiro:")
    st.code("python main.py --analyze-logs")
else:
    render_metrics(df, suspicious)
    st.divider()

    col_left, col_right = st.columns(2)
    with col_left:
        render_event_type_chart(suspicious)
    with col_right:
        render_timeline_chart(suspicious)

    col_left2, col_right2 = st.columns(2)
    with col_left2:
        render_top_users(suspicious)
    with col_right2:
        render_top_ips(suspicious)

    st.divider()
    render_suspicious_table(suspicious)
