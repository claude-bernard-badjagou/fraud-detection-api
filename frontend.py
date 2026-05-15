import os
import streamlit as st
import requests
import pandas as pd
import numpy as np
import json
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px


# CONFIGURATION

st.set_page_config(
    page_title="Fraud Detection",
    page_icon="shield",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Bascule automatique local / production

API_URL_LOCAL      = "http://localhost:8000"
API_URL_PRODUCTION = "https://fraud-detection-api-production-9fb6.up.railway.app"

with st.sidebar:
    env = st.radio("Environnement", ["Local", "Production"], index=1)
    API_URL = API_URL_PRODUCTION if env == "Production" else API_URL_LOCAL
    st.markdown("---")

SVG_SHIELD = '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#5eead4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>'
SVG_ACTIVITY = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#5eead4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>'
SVG_DATABASE = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#5eead4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>'
SVG_CLOCK = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#5eead4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>'
SVG_BAR_CHART = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#5eead4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/></svg>'

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: #141518;
        color: #f4f4f5;
    }
    .stApp {
        background-color: #141518;
        color: #f4f4f5;
    }
    .stMarkdown, .stMarkdown p, .stMarkdown span,
    .stMarkdown li, .stMarkdown td, .stMarkdown th,
    [data-testid="stMarkdownContainer"],
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stText"],
    .stApp p, .stApp span, .stApp label,
    .stRadio label, .stSelectbox label, .stNumberInput label,
    .stFileUploader label {
        color: #f4f4f5 !important;
    }
    section[data-testid="stSidebar"] { background-color: #1c1d21; }
    div[data-testid="stSidebarContent"] { background-color: #1c1d21; }
    div[data-testid="stSidebarContent"] p,
    div[data-testid="stSidebarContent"] span,
    div[data-testid="stSidebarContent"] label {
        color: #f4f4f5 !important;
    }

    .block-container {
        padding-top: 1.5rem !important;
    }

    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        color: #f4f4f5;
        font-weight: 600;
        letter-spacing: -0.025em;
    }

    .app-header {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 0 0 12px 0;
        border-bottom: 1px solid #27272a;
        margin-bottom: 16px;
    }
    .app-header h1 {
        margin: 0;
        font-size: 1.4rem;
        font-weight: 600;
        color: #f4f4f5;
    }
    .app-header .version-badge {
        background: #27272a;
        border: 1px solid #3f3f46;
        border-radius: 4px;
        padding: 2px 8px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem;
        color: #a1a1aa;
        letter-spacing: 0.05em;
    }

    .metric-card {
        background: #1c1d21;
        border: 1px solid #27272a;
        border-radius: 8px;
        padding: 16px;
        margin: 6px 0;
    }
    .metric-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.5rem;
        font-weight: 600;
        color: #5eead4;
    }
    .metric-label {
        font-size: 0.7rem;
        color: #a1a1aa;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 4px;
    }

    .risk-critical {
        background: #1c1d21;
        border: 1px solid #dc2626;
        border-left: 4px solid #dc2626;
        border-radius: 6px;
        padding: 14px 20px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 1rem;
        font-weight: 500;
        color: #fca5a5;
        text-align: center;
    }
    .risk-high {
        background: #1c1d21;
        border: 1px solid #ea580c;
        border-left: 4px solid #ea580c;
        border-radius: 6px;
        padding: 14px 20px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 1rem;
        font-weight: 500;
        color: #fdba74;
        text-align: center;
    }
    .risk-medium {
        background: #1c1d21;
        border: 1px solid #ca8a04;
        border-left: 4px solid #ca8a04;
        border-radius: 6px;
        padding: 14px 20px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 1rem;
        font-weight: 500;
        color: #fde68a;
        text-align: center;
    }
    .risk-low {
        background: #1c1d21;
        border: 1px solid #16a34a;
        border-left: 4px solid #16a34a;
        border-radius: 6px;
        padding: 14px 20px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 1rem;
        font-weight: 500;
        color: #86efac;
        text-align: center;
    }

    .stButton > button {
        background: #5eead4;
        color: #000000;
        border: none;
        border-radius: 6px;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 0.85rem;
        padding: 10px 24px;
        width: 100%;
        transition: all 0.15s ease;
    }
    .stButton > button:hover {
        background: #99f6e4;
        color: #000000;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(94,234,212,0.15);
    }

    .stTabs [data-baseweb="tab-list"] {
        background-color: #1c1d21;
        border-radius: 8px;
        padding: 6px;
        gap: 6px;
        border: 1px solid #27272a;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        font-size: 0.82rem;
        color: #a1a1aa;
        background-color: transparent;
        border-radius: 6px;
        padding: 8px 16px;
        border: 1px solid transparent;
        transition: all 0.15s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #f4f4f5;
        background-color: #27272a;
    }
    .stTabs [aria-selected="true"] {
        background-color: #27272a !important;
        color: #5eead4 !important;
        border: 1px solid #3f3f46 !important;
    }

    .stDataFrame { border-radius: 8px; overflow: hidden; }

    .section-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 12px;
    }
    .section-header h3 {
        margin: 0;
        font-size: 1.1rem;
    }

    div[data-testid="stMetric"] {
        background: #1c1d21;
        border: 1px solid #27272a;
        border-radius: 8px;
        padding: 12px 16px;
    }
    div[data-testid="stMetric"] label {
        color: #a1a1aa;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #f4f4f5;
        font-family: 'JetBrains Mono', monospace;
    }

    hr { border-color: #27272a; }

    .sidebar-model-info {
        font-size: 0.7rem;
        color: #a1a1aa;
        font-family: 'JetBrains Mono', monospace;
        padding: 8px 0;
    }

    div[data-testid="stFileUploader"] {
        border: 1px dashed #3f3f46;
        border-radius: 8px;
        padding: 8px;
    }
    div[data-testid="stFileUploader"] span,
    div[data-testid="stFileUploader"] p,
    div[data-testid="stFileUploader"] small,
    div[data-testid="stFileUploader"] button,
    div[data-testid="stFileUploader"] section span {
        color: #000000 !important;
    }

    .stDownloadButton > button,
    .stDownloadButton > button span,
    .stDownloadButton > button p,
    .stDownloadButton button,
    [data-testid="stDownloadButton"] button,
    [data-testid="stDownloadButton"] button span,
    [data-testid="stDownloadButton"] button p {
        color: #000000 !important;
    }

    .stButton > button span,
    .stButton > button p {
        color: #000000 !important;
    }

    input, select, textarea,
    [data-baseweb="input"] input,
    [data-baseweb="select"] span,
    .stNumberInput input,
    .stSelectbox [data-baseweb="select"] {
        color: #1a1a1a !important;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# SESSION STATE
# =============================================================================
if "history" not in st.session_state:
    st.session_state.history = []


# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================
def check_api_status():
    try:
        r = requests.get(f"{API_URL}/health", timeout=3)
        return r.status_code == 200, r.json()
    except Exception:
        return False, {}


def get_model_info():
    try:
        r = requests.get(f"{API_URL}/model/info", timeout=3)
        return r.json() if r.status_code == 200 else {}
    except Exception:
        return {}


def predict_single(payload: dict):
    try:
        r = requests.post(f"{API_URL}/predict", json=payload, timeout=10)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


def predict_batch(transactions: list):
    try:
        r = requests.post(f"{API_URL}/predict/batch",
                          json={"transactions": transactions}, timeout=30)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


def risk_badge(level: str) -> str:
    icons = {"CRITICAL": "CRITIQUE", "HIGH": "ELEVE", "MEDIUM": "MOYEN", "LOW": "FAIBLE"}
    css   = {"CRITICAL": "risk-critical", "HIGH": "risk-high",
             "MEDIUM": "risk-medium", "LOW": "risk-low"}
    label = icons.get(level, level)
    cls   = css.get(level, "risk-low")
    return f'<div class="{cls}">Risque {label}</div>'


def gauge_chart(proba: float, threshold: float):
    color = "#ef4444" if proba >= threshold else "#22c55e"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(proba * 100, 1),
        number={"suffix": "%", "font": {"color": color, "size": 36,
                                        "family": "JetBrains Mono"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#3f3f46",
                     "tickfont": {"color": "#a1a1aa", "size": 10}},
            "bar": {"color": color, "thickness": 0.25},
            "bgcolor": "#1c1d21",
            "bordercolor": "#27272a",
            "steps": [
                {"range": [0, 30],  "color": "#14332a"},
                {"range": [30, threshold * 100], "color": "#2d2305"},
                {"range": [threshold * 100, 100], "color": "#331111"},
            ],
            "threshold": {
                "line": {"color": "#f59e0b", "width": 3},
                "thickness": 0.8,
                "value": threshold * 100
            }
        }
    ))
    fig.update_layout(
        height=220, margin=dict(t=20, b=0, l=20, r=20),
        paper_bgcolor="#141518", font_color="#f4f4f5"
    )
    return fig


# =============================================================================
# SIDEBAR
# =============================================================================
with st.sidebar:
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">'
        f'{SVG_SHIELD}'
        f'<span style="font-family:Inter;font-weight:600;font-size:1rem;color:#f4f4f5">Fraud Detection</span>'
        f'</div>',
        unsafe_allow_html=True
    )
    st.markdown("---")

    api_ok, health = check_api_status()
    if api_ok:
        st.success("API en ligne")
        info = get_model_info()
        if info:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Version</div>
                <div style="font-family:'JetBrains Mono';color:#5eead4;font-size:0.9rem">{info.get('version','—')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Modele</div>
                <div style="font-family:'JetBrains Mono';color:#5eead4;font-size:0.9rem">{info.get('model_type','—').upper()}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Arbres</div>
                <div class="metric-value">{info.get('n_trees','—')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Features</div>
                <div class="metric-value">{info.get('n_features','—')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Seuil</div>
                <div class="metric-value">{info.get('threshold','—')}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.error("API hors ligne")
        st.info(f"Verifie que l'API tourne sur {API_URL}")

    st.markdown("---")
    st.markdown(
        '<div class="sidebar-model-info">'
        'IEEE-CIS Fraud Detection<br>AUC-ROC : 0.9269</div>',
        unsafe_allow_html=True
    )


# =============================================================================
# HEADER
# =============================================================================
st.markdown(
    f'<div class="app-header">'
    f'{SVG_SHIELD}'
    f'<h1>Fraud Detection</h1>'
    f'<span class="version-badge">v1.0.0</span>'
    f'</div>',
    unsafe_allow_html=True
)


# =============================================================================
# ONGLETS
# =============================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Simple Prediction",
    "Prediction par lot",
    "Modele",
    "Historique",
    "Monitoring"
])


# ------------------------------------------------------------------ ONGLET 1
with tab1:
    st.markdown(
        f'<div class="section-header">{SVG_ACTIVITY}<h3>Analyser une transaction</h3></div>',
        unsafe_allow_html=True
    )
    st.markdown(
        "Renseigne les champs ci-dessous. Les champs non renseignes "
        "utilisent la valeur par defaut -999."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Transaction**")
        amt     = st.number_input("Montant (TransactionAmt)", min_value=0.0,
                                  value=75.0, step=0.01)
        prod    = st.selectbox("ProductCD", [0, 1, 2, 3, 4],
                               format_func=lambda x: ["W","H","C","S","R"][x])
        card1   = st.number_input("card1", value=4000.0)
        card4   = st.selectbox("card4 (reseau)", [-999, 0, 1, 2, 3],
                               format_func=lambda x: "Inconnu" if x == -999
                               else ["Discover","Mastercard","Visa","Amex"][x])

    with col2:
        st.markdown("**Variables C (compteurs)**")
        c1  = st.number_input("C1",  value=1.0)
        c2  = st.number_input("C2",  value=-999.0)
        c6  = st.number_input("C6",  value=-999.0)
        c13 = st.number_input("C13", value=1.0)
        c14 = st.number_input("C14", value=1.0)

    with col3:
        st.markdown("**Variables D (delta jours)**")
        d1  = st.number_input("D1",  value=14.0)
        d4  = st.number_input("D4",  value=-999.0)
        d10 = st.number_input("D10", value=-999.0)
        d15 = st.number_input("D15", value=300.0)

    st.markdown("")
    if st.button("Analyser la transaction", key="btn_predict"):
        payload = {
            "TransactionAmt": amt,
            "ProductCD": int(prod),
            "card1": card1,
            "card4": int(card4),
            "C1": c1, "C2": c2, "C6": c6,
            "C13": c13, "C14": c14,
            "D1": d1, "D4": d4, "D10": d10, "D15": d15,
        }
        with st.spinner("Analyse en cours..."):
            result = predict_single(payload)

        if result:
            proba     = result["fraud_probability"]
            is_fraud  = result["is_fraud"]
            threshold = result["threshold"]
            risk      = result["risk_level"]

            c_gauge, c_result = st.columns([1, 1])
            with c_gauge:
                st.plotly_chart(gauge_chart(proba, threshold),
                                use_container_width=True)
            with c_result:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(risk_badge(risk), unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                verdict = "Fraude detectee" if is_fraud else "Transaction legitime"
                color   = "#fca5a5" if is_fraud else "#86efac"
                st.markdown(
                    f"<div style='font-family:JetBrains Mono;font-size:1rem;"
                    f"color:{color};text-align:center'>{verdict}</div>",
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"<div style='font-family:JetBrains Mono;font-size:0.8rem;"
                    f"color:#a1a1aa;text-align:center;margin-top:8px'>"
                    f"Seuil : {threshold} | Proba : {proba}</div>",
                    unsafe_allow_html=True
                )

            # Ajouter a l'historique
            st.session_state.history.append({
                "Horodatage": datetime.now().strftime("%H:%M:%S"),
                "Montant":    amt,
                "Probabilite": proba,
                "Risque":      risk,
                "Verdict":     "Fraude" if is_fraud else "Legitime"
            })
        else:
            st.error("Erreur lors de l'appel a l'API. Verifie que le serveur tourne.")


# ------------------------------------------------------------------ ONGLET 2
with tab2:
    st.markdown(
        f'<div class="section-header">{SVG_DATABASE}<h3>Analyse par lot</h3></div>',
        unsafe_allow_html=True
    )
    st.markdown(
        "Le fichier CSV doit contenir au minimum les colonnes "
        "`TransactionAmt` et `ProductCD`. "
        "Les autres colonnes optionnelles sont celles de `feature_cols.json`."
    )

    st.download_button(
        label="Telecharger le modele CSV",
        data="TransactionAmt,ProductCD,card1,C1,C13,C14,D1,D15\n"
             "75.0,1,4000,1.0,1.0,1.0,14.0,300.0\n"
             "500.0,3,2000,2.0,5.0,2.0,7.0,150.0\n"
             "9999.0,2,100,10.0,50.0,5.0,1.0,5.0\n",
        file_name="modele_transactions.csv",
        mime="text/csv"
    )

    uploaded = st.file_uploader("Choisir un fichier CSV", type=["csv"])

    if uploaded:
        df_input = pd.read_csv(uploaded)
        st.markdown(f"**{len(df_input)} transactions chargees**")
        st.dataframe(df_input.head(5), use_container_width=True)

        if st.button("Lancer l'analyse batch", key="btn_batch"):
            transactions = df_input.fillna(-999).to_dict(orient="records")
            transactions = [
                {k: (int(v) if k in ["ProductCD", "card4"] else float(v))
                 for k, v in t.items()}
                for t in transactions
            ]

            with st.spinner(f"Analyse de {len(transactions)} transactions..."):
                result = predict_batch(transactions)

            if result:
                preds = result["predictions"]
                df_result = df_input.copy()
                df_result["fraud_probability"] = [p["fraud_probability"] for p in preds]
                df_result["is_fraud"]          = [p["is_fraud"]          for p in preds]
                df_result["risk_level"]        = [p["risk_level"]        for p in preds]

                # Metriques batch
                n_fraud  = df_result["is_fraud"].sum()
                n_total  = len(df_result)
                pct_fraud = n_fraud / n_total * 100

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Total",       n_total)
                m2.metric("Fraudes",     n_fraud)
                m3.metric("Taux fraude", f"{pct_fraud:.1f}%")
                m4.metric("Score moyen", f"{df_result['fraud_probability'].mean():.3f}")

                # Distribution des probabilites
                fig_hist = px.histogram(
                    df_result, x="fraud_probability", nbins=30,
                    color="is_fraud",
                    color_discrete_map={True: "#f87171", False: "#5eead4"},
                    title="Distribution des probabilites de fraude",
                    labels={"fraud_probability": "Probabilite", "is_fraud": "Fraude"}
                )
                fig_hist.update_layout(
                    paper_bgcolor="#141518", plot_bgcolor="#1c1d21",
                    font_color="#f4f4f5", title_font_family="Inter"
                )
                st.plotly_chart(fig_hist, use_container_width=True)

                # Tableau resultats
                st.markdown("**Resultats complets**")
                st.dataframe(
                    df_result.sort_values("fraud_probability", ascending=False),
                    use_container_width=True
                )

                # Export
                csv_export = df_result.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="Exporter les resultats CSV",
                    data=csv_export,
                    file_name=f"resultats_fraude_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

                # Ajouter a l'historique
                for i, p in enumerate(preds):
                    st.session_state.history.append({
                        "Horodatage": datetime.now().strftime("%H:%M:%S"),
                        "Montant":    df_input.iloc[i].get("TransactionAmt", 0),
                        "Probabilite": p["fraud_probability"],
                        "Risque":      p["risk_level"],
                        "Verdict":     "Fraude" if p["is_fraud"] else "Legitime"
                    })
            else:
                st.error("Erreur lors de l'appel batch a l'API.")


# ------------------------------------------------------------------ ONGLET 3
with tab3:
    st.markdown(
        f'<div class="section-header">{SVG_BAR_CHART}<h3>Metriques du modele</h3></div>',
        unsafe_allow_html=True
    )

    info = get_model_info()
    if info:
        metrics = info.get("metrics", {})

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("AUC-ROC",   metrics.get("auc_roc", "—"))
        c2.metric("PR-AUC",    metrics.get("pr_auc", "—"))
        c3.metric("Precision", metrics.get("precision_fraud", "—"))
        c4.metric("Rappel",    metrics.get("recall_fraud", "—"))
        c5.metric("F1-Score",  metrics.get("f1_fraud", "—"))

        st.markdown("---")

        col_a, col_b = st.columns(2)

        with col_a:
            # Radar chart des metriques
            categories = ["AUC-ROC", "PR-AUC", "Precision", "Rappel", "F1"]
            values = [
                metrics.get("auc_roc", 0),
                metrics.get("pr_auc", 0),
                metrics.get("precision_fraud", 0),
                metrics.get("recall_fraud", 0),
                metrics.get("f1_fraud", 0),
            ]
            fig_radar = go.Figure(go.Scatterpolar(
                r=values + [values[0]],
                theta=categories + [categories[0]],
                fill="toself",
                fillcolor="rgba(94,234,212,0.1)",
                line=dict(color="#5eead4", width=2),
                name="Modele"
            ))
            fig_radar.update_layout(
                polar=dict(
                    bgcolor="#1c1d21",
                    radialaxis=dict(visible=True, range=[0, 1],
                                   tickfont=dict(color="#71717a")),
                    angularaxis=dict(tickfont=dict(color="#f4f4f5"))
                ),
                paper_bgcolor="#141518",
                font_color="#f4f4f5",
                title="Profil de performance",
                title_font_family="Inter",
                showlegend=False,
                height=350
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        with col_b:
            st.markdown("**Contexte du modele**")
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Dataset</div>
                <div style="font-family:'JetBrains Mono';color:#f4f4f5;font-size:0.85rem">
                    IEEE-CIS Fraud Detection
                </div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Algorithme</div>
                <div style="font-family:'JetBrains Mono';color:#5eead4;font-size:0.85rem">
                    {info.get('model_type','—').upper()} — Ensemble XGBoost + LightGBM
                </div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Nombre d arbres</div>
                <div class="metric-value">{info.get('n_trees','—')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Seuil de decision</div>
                <div class="metric-value">{info.get('threshold','—')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Desequilibre classes</div>
                <div style="font-family:'JetBrains Mono';color:#f4f4f5;font-size:0.85rem">
                    96.5% legitimes — 3.5% fraudes (ratio 1:27)
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("Impossible de recuperer les informations du modele. Verifie que l'API tourne.")


# ------------------------------------------------------------------ ONGLET 4
with tab4:
    st.markdown(
        f'<div class="section-header">{SVG_CLOCK}<h3>Historique des predictions</h3></div>',
        unsafe_allow_html=True
    )

    if st.session_state.history:
        df_hist = pd.DataFrame(st.session_state.history)

        h1, h2, h3 = st.columns(3)
        h1.metric("Total analyses",    len(df_hist))
        h2.metric("Fraudes detectees", (df_hist["Verdict"] == "Fraude").sum())
        h3.metric("Taux fraude",
                  f"{(df_hist['Verdict'] == 'Fraude').mean() * 100:.1f}%")

        # Evolution des probabilites
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=list(range(len(df_hist))),
            y=df_hist["Probabilite"],
            mode="lines+markers",
            line=dict(color="#5eead4", width=2),
            marker=dict(
                color=["#f87171" if v == "Fraude" else "#5eead4"
                       for v in df_hist["Verdict"]],
                size=8
            ),
            name="Probabilite"
        ))
        fig_line.add_hline(
            y=0.7426, line_dash="dash",
            line_color="#f59e0b", annotation_text="Seuil",
            annotation_font_color="#f59e0b"
        )
        fig_line.update_layout(
            title="Evolution des probabilites de fraude",
            paper_bgcolor="#141518", plot_bgcolor="#1c1d21",
            font_color="#f4f4f5", title_font_family="Inter",
            xaxis_title="Index", yaxis_title="Probabilite",
            height=300
        )
        st.plotly_chart(fig_line, use_container_width=True)

        # Tableau
        st.dataframe(
            df_hist.sort_values("Horodatage", ascending=False),
            use_container_width=True
        )

        if st.button("Effacer l'historique"):
            st.session_state.history = []
            st.rerun()

        # Export
        csv_hist = df_hist.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Exporter l'historique CSV",
            data=csv_hist,
            file_name=f"historique_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info(
            "Aucune prediction effectuee pour l'instant. "
            "Utilise l'onglet 'Simple Prediction' ou 'Prediction par lot'."
        )


# ------------------------------------------------------------------ ONGLET 5
with tab5:
    st.markdown(
        f'<div class="section-header">{SVG_ACTIVITY}<h3>Monitoring de production</h3></div>',
        unsafe_allow_html=True
    )

    try:
        r = requests.get(f"{API_URL}/monitoring/stats", timeout=5)
        if r.status_code == 200:
            stats = r.json()

            if stats.get("total", 0) == 0:
                st.info("Aucune prediction enregistree pour l'instant.")
            else:
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Total predictions",  stats["total"])
                m2.metric("Fraudes detectees",  stats["fraud_count"])
                m3.metric("Taux de fraude",
                          f"{stats['fraud_rate'] * 100:.2f}%")
                m4.metric("Proba moyenne",
                          f"{stats['proba_mean']:.4f}")

                st.markdown("---")
                col_a, col_b = st.columns(2)

                with col_a:
                    # Distribution des niveaux de risque
                    risk_data = stats["risk_counts"]
                    fig_risk  = go.Figure(go.Bar(
                        x=list(risk_data.keys()),
                        y=list(risk_data.values()),
                        marker_color=["#f87171","#fb923c","#fbbf24","#5eead4"]
                    ))
                    fig_risk.update_layout(
                        title="Distribution des niveaux de risque",
                        paper_bgcolor="#141518",
                        plot_bgcolor="#1c1d21",
                        font_color="#f4f4f5",
                        title_font_family="Inter",
                        height=300
                    )
                    st.plotly_chart(fig_risk, use_container_width=True)

                with col_b:
                    st.markdown("**Statistiques des probabilites**")
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Minimum</div>
                        <div class="metric-value">{stats['proba_min']:.4f}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Maximum</div>
                        <div class="metric-value">{stats['proba_max']:.4f}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Moyenne</div>
                        <div class="metric-value">{stats['proba_mean']:.4f}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("Endpoint monitoring non disponible.")
    except Exception:
        st.warning("API hors ligne ou endpoint monitoring absent.")
