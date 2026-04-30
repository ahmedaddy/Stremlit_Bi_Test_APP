import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SalesIQ · Business Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Main background */
.stApp {
    background: #0f1117;
    color: #e8eaf0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #161b27 !important;
    border-right: 1px solid #1e2535;
}
[data-testid="stSidebar"] * {
    color: #c5cad8 !important;
}

/* KPI Cards */
.kpi-card {
    background: linear-gradient(135deg, #1a2035 0%, #1e2840 100%);
    border: 1px solid #2a3550;
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3);
}
.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}
.kpi-label {
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #6b7a99;
    margin-bottom: 8px;
}
.kpi-value {
    font-size: 32px;
    font-weight: 700;
    color: #e8eaf0;
    margin-bottom: 6px;
    font-family: 'DM Mono', monospace;
}
.kpi-delta-pos {
    font-size: 13px;
    color: #34d399;
    font-weight: 600;
}
.kpi-delta-neg {
    font-size: 13px;
    color: #f87171;
    font-weight: 600;
}

/* Section headers */
.section-header {
    font-size: 18px;
    font-weight: 600;
    color: #e8eaf0;
    margin: 32px 0 16px 0;
    padding-bottom: 8px;
    border-bottom: 1px solid #1e2535;
    letter-spacing: -0.3px;
}

/* Page header */
.page-header {
    background: linear-gradient(135deg, #1a2035 0%, #1e2840 100%);
    border: 1px solid #2a3550;
    border-radius: 20px;
    padding: 32px 40px;
    margin-bottom: 32px;
    display: flex;
    align-items: center;
    gap: 16px;
}
.page-title {
    font-size: 28px;
    font-weight: 700;
    color: #e8eaf0;
    letter-spacing: -0.5px;
    margin: 0;
}
.page-subtitle {
    font-size: 14px;
    color: #6b7a99;
    margin: 4px 0 0 0;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #161b27;
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
    border: 1px solid #1e2535;
}
.stTabs [data-baseweb="tab"] {
    color: #6b7a99 !important;
    border-radius: 8px;
    font-weight: 500;
    font-size: 14px;
    padding: 8px 20px;
}
.stTabs [aria-selected="true"] {
    background: #2a3550 !important;
    color: #e8eaf0 !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background: #1a2035;
    border: 1px solid #2a3550;
    border-radius: 12px;
    padding: 16px;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border: 1px solid #2a3550 !important;
    border-radius: 12px;
    overflow: hidden;
}

/* Select boxes and sliders */
.stSelectbox > div > div, .stMultiselect > div > div {
    background: #1a2035 !important;
    border-color: #2a3550 !important;
    color: #e8eaf0 !important;
    border-radius: 10px !important;
}

/* Divider */
hr { border-color: #1e2535 !important; }

/* Hide default streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ─── Data Generation ─────────────────────────────────────────────────────────
@st.cache_data
def generate_data():
    np.random.seed(42)
    n = 2000
    start = datetime(2023, 1, 1)
    dates = [start + timedelta(days=int(x)) for x in np.random.randint(0, 730, n)]

    regions = ["North America", "Europe", "Asia Pacific", "Latin America", "Middle East"]
    categories = ["Electronics", "Apparel", "Home & Garden", "Sports", "Beauty", "Books"]
    channels = ["Online", "Retail", "Wholesale", "Direct"]
    reps = [f"Rep {i:02d}" for i in range(1, 21)]

    region_w   = [0.38, 0.25, 0.20, 0.10, 0.07]
    category_w = [0.28, 0.20, 0.18, 0.15, 0.12, 0.07]
    channel_w  = [0.45, 0.30, 0.15, 0.10]

    df = pd.DataFrame({
        "date":     dates,
        "region":   np.random.choice(regions,     n, p=region_w),
        "category": np.random.choice(categories,  n, p=category_w),
        "channel":  np.random.choice(channels,    n, p=channel_w),
        "rep":      np.random.choice(reps,         n),
        "units":    np.random.randint(1, 200, n),
        "revenue":  np.random.lognormal(7.5, 0.8, n).round(2),
        "cost":     np.random.lognormal(6.8, 0.8, n).round(2),
        "csat":     np.clip(np.random.normal(4.1, 0.6, n), 1, 5).round(1),
    })

    # boost recent trend
    df["revenue"] *= (1 + (pd.to_datetime(df["date"]) - pd.Timestamp("2023-01-01")).dt.days / 730 * 0.3)
    df["profit"] = (df["revenue"] - df["cost"]).round(2)
    df["margin"] = ((df["profit"] / df["revenue"]) * 100).round(1)
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["quarter"] = df["date"].dt.to_period("Q").astype(str)
    df["year"] = df["date"].dt.year
    return df.sort_values("date").reset_index(drop=True)

df_all = generate_data()

# ─── Plotly Theme ────────────────────────────────────────────────────────────
COLORS = ["#6366f1", "#34d399", "#f59e0b", "#f87171", "#60a5fa", "#a78bfa", "#fb923c"]
CHART_BG = "#0f1117"
PAPER_BG = "#161b27"
GRID_COLOR = "#1e2535"
TEXT_COLOR = "#c5cad8"

def chart_layout(fig, height=380):
    fig.update_layout(
        height=height,
        plot_bgcolor=CHART_BG,
        paper_bgcolor=PAPER_BG,
        font=dict(family="DM Sans", color=TEXT_COLOR, size=13),
        margin=dict(l=16, r=16, t=40, b=16),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor=GRID_COLOR,
            font=dict(color=TEXT_COLOR),
        ),
        colorway=COLORS,
    )
    fig.update_xaxes(gridcolor=GRID_COLOR, zeroline=False, color=TEXT_COLOR)
    fig.update_yaxes(gridcolor=GRID_COLOR, zeroline=False, color=TEXT_COLOR)
    return fig

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 SalesIQ")
    st.markdown("---")
    st.markdown("### Filters")

    year_opts = sorted(df_all["year"].unique())
    selected_years = st.multiselect("Year", year_opts, default=year_opts)

    region_opts = sorted(df_all["region"].unique())
    selected_regions = st.multiselect("Region", region_opts, default=region_opts)

    cat_opts = sorted(df_all["category"].unique())
    selected_cats = st.multiselect("Category", cat_opts, default=cat_opts)

    chan_opts = sorted(df_all["channel"].unique())
    selected_channels = st.multiselect("Channel", chan_opts, default=chan_opts)

    st.markdown("---")
    st.markdown("### Time Granularity")
    granularity = st.selectbox("Group by", ["Month", "Quarter"])

    st.markdown("---")
    st.markdown(
        "<span style='color:#6b7a99; font-size:12px'>SalesIQ BI v2.0 · Demo Data</span>",
        unsafe_allow_html=True
    )

# ─── Apply Filters ───────────────────────────────────────────────────────────
mask = (
    df_all["year"].isin(selected_years) &
    df_all["region"].isin(selected_regions) &
    df_all["category"].isin(selected_cats) &
    df_all["channel"].isin(selected_channels)
)
df = df_all[mask].copy()

if df.empty:
    st.warning("No data matches your filters. Please adjust the sidebar selections.")
    st.stop()

time_col = "month" if granularity == "Month" else "quarter"

# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
  <div>
    <p class="page-title">📊 SalesIQ · Business Intelligence</p>
    <p class="page-subtitle">Executive dashboard · Real-time analytics · 2023–2024</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── KPI Cards ───────────────────────────────────────────────────────────────
total_rev    = df["revenue"].sum()
total_profit = df["profit"].sum()
avg_margin   = df["margin"].mean()
avg_csat     = df["csat"].mean()
total_orders = len(df)
total_units  = df["units"].sum()

# Compare to "previous period" (first half vs second half of filtered data)
mid = df["date"].median()
df_prev = df[df["date"] <= mid]
df_curr = df[df["date"] >  mid]

def delta_pct(curr, prev):
    if prev == 0: return 0
    return ((curr - prev) / prev) * 100

d_rev    = delta_pct(df_curr["revenue"].sum(), df_prev["revenue"].sum())
d_profit = delta_pct(df_curr["profit"].sum(),  df_prev["profit"].sum())
d_margin = delta_pct(df_curr["margin"].mean(), df_prev["margin"].mean())
d_csat   = delta_pct(df_curr["csat"].mean(),   df_prev["csat"].mean())

def kpi(label, value, delta, fmt="$"):
    arrow = "▲" if delta >= 0 else "▼"
    cls   = "kpi-delta-pos" if delta >= 0 else "kpi-delta-neg"
    val_str = f"${value:,.0f}" if fmt == "$" else f"{value:,.1f}{fmt}"
    return f"""
    <div class="kpi-card">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{val_str}</div>
      <div class="{cls}">{arrow} {abs(delta):.1f}% vs prev period</div>
    </div>"""

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.markdown(kpi("Total Revenue",  total_rev,    d_rev),    unsafe_allow_html=True)
k2.markdown(kpi("Net Profit",     total_profit, d_profit), unsafe_allow_html=True)
k3.markdown(kpi("Avg Margin",     avg_margin,   d_margin, fmt="%"), unsafe_allow_html=True)
k4.markdown(kpi("Avg CSAT",       avg_csat,     d_csat,   fmt="★"), unsafe_allow_html=True)
k5.markdown(kpi("Total Orders",   total_orders, 0,         fmt=" orders").replace("$",""), unsafe_allow_html=True)
k6.markdown(kpi("Units Sold",     total_units,  0,         fmt=" units").replace("$",""),  unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Tabs ────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📈 Revenue", "🌍 Geography", "🏷️ Products", "👤 Sales Reps"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 · REVENUE
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("<div class='section-header'>Revenue & Profit Over Time</div>", unsafe_allow_html=True)

    trend = (
        df.groupby(time_col)
          .agg(revenue=("revenue","sum"), profit=("profit","sum"), orders=("revenue","count"))
          .reset_index()
    )

    fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
    fig_trend.add_trace(go.Bar(
        x=trend[time_col], y=trend["revenue"],
        name="Revenue", marker_color=COLORS[0], opacity=0.85
    ), secondary_y=False)
    fig_trend.add_trace(go.Scatter(
        x=trend[time_col], y=trend["profit"],
        name="Profit", line=dict(color=COLORS[1], width=2.5),
        mode="lines+markers", marker=dict(size=5)
    ), secondary_y=False)
    fig_trend.add_trace(go.Scatter(
        x=trend[time_col], y=trend["orders"],
        name="Orders", line=dict(color=COLORS[2], width=1.5, dash="dot"),
        mode="lines", opacity=0.7
    ), secondary_y=True)
    fig_trend.update_yaxes(title_text="Revenue / Profit ($)", secondary_y=False, gridcolor=GRID_COLOR, color=TEXT_COLOR)
    fig_trend.update_yaxes(title_text="Order Count", secondary_y=True, gridcolor=GRID_COLOR, color=TEXT_COLOR)
    chart_layout(fig_trend, 420)
    st.plotly_chart(fig_trend, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='section-header'>Revenue by Channel</div>", unsafe_allow_html=True)
        ch = df.groupby(["channel", time_col])["revenue"].sum().reset_index()
        fig_ch = px.area(ch, x=time_col, y="revenue", color="channel",
                         color_discrete_sequence=COLORS)
        fig_ch.update_traces(line=dict(width=1.5))
        chart_layout(fig_ch)
        st.plotly_chart(fig_ch, use_container_width=True)

    with c2:
        st.markdown("<div class='section-header'>Margin Distribution</div>", unsafe_allow_html=True)
        fig_margin = px.histogram(df, x="margin", nbins=40,
                                  color_discrete_sequence=[COLORS[3]],
                                  labels={"margin": "Profit Margin (%)"})
        fig_margin.add_vline(x=df["margin"].mean(), line_dash="dash",
                             line_color=COLORS[1], annotation_text="Mean",
                             annotation_font_color=COLORS[1])
        chart_layout(fig_margin)
        st.plotly_chart(fig_margin, use_container_width=True)

    st.markdown("<div class='section-header'>Revenue vs Profit Scatter</div>", unsafe_allow_html=True)
    fig_scat = px.scatter(
        df.sample(600, random_state=1), x="revenue", y="profit",
        color="category", size="units", hover_data=["region", "channel", "csat"],
        color_discrete_sequence=COLORS, opacity=0.7,
        labels={"revenue":"Revenue ($)", "profit":"Profit ($)"}
    )
    chart_layout(fig_scat, 400)
    st.plotly_chart(fig_scat, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 · GEOGRAPHY
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='section-header'>Revenue by Region</div>", unsafe_allow_html=True)
        reg = df.groupby("region").agg(
            revenue=("revenue","sum"), profit=("profit","sum"),
            orders=("revenue","count"), margin=("margin","mean")
        ).reset_index().sort_values("revenue", ascending=False)
        fig_reg = px.bar(reg, x="revenue", y="region", orientation="h",
                         color="margin", color_continuous_scale=["#6366f1","#34d399"],
                         labels={"revenue":"Revenue ($)", "margin":"Avg Margin %"},
                         text=reg["revenue"].apply(lambda x: f"${x:,.0f}"))
        fig_reg.update_traces(textposition="outside")
        chart_layout(fig_reg)
        st.plotly_chart(fig_reg, use_container_width=True)

    with c2:
        st.markdown("<div class='section-header'>Market Share by Region</div>", unsafe_allow_html=True)
        fig_pie = px.pie(reg, names="region", values="revenue",
                         color_discrete_sequence=COLORS, hole=0.5)
        fig_pie.update_traces(textinfo="percent+label", textfont_size=12)
        chart_layout(fig_pie)
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("<div class='section-header'>Region × Channel Heatmap</div>", unsafe_allow_html=True)
    heat = df.pivot_table(values="revenue", index="region", columns="channel", aggfunc="sum").fillna(0)
    fig_heat = px.imshow(
        heat, text_auto=".2s", aspect="auto",
        color_continuous_scale=["#1a2035","#6366f1","#34d399"],
        labels=dict(color="Revenue ($)")
    )
    chart_layout(fig_heat, 350)
    st.plotly_chart(fig_heat, use_container_width=True)

    st.markdown("<div class='section-header'>Regional Trend Over Time</div>", unsafe_allow_html=True)
    rt = df.groupby(["region", time_col])["revenue"].sum().reset_index()
    fig_rt = px.line(rt, x=time_col, y="revenue", color="region",
                     color_discrete_sequence=COLORS, markers=True,
                     labels={"revenue":"Revenue ($)"})
    fig_rt.update_traces(line=dict(width=2), marker=dict(size=4))
    chart_layout(fig_rt, 380)
    st.plotly_chart(fig_rt, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 · PRODUCTS
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='section-header'>Revenue by Category</div>", unsafe_allow_html=True)
        cat = df.groupby("category").agg(
            revenue=("revenue","sum"), profit=("profit","sum"),
            units=("units","sum"), margin=("margin","mean")
        ).reset_index().sort_values("revenue", ascending=True)
        fig_cat = px.bar(cat, x="revenue", y="category", orientation="h",
                         color="margin", color_continuous_scale=["#6366f1","#f59e0b"],
                         text=cat["revenue"].apply(lambda x: f"${x:,.0f}"))
        fig_cat.update_traces(textposition="outside")
        chart_layout(fig_cat)
        st.plotly_chart(fig_cat, use_container_width=True)

    with c2:
        st.markdown("<div class='section-header'>Margin vs Revenue Bubble</div>", unsafe_allow_html=True)
        fig_bub = px.scatter(
            cat, x="revenue", y="margin", size="units",
            text="category", color="category",
            color_discrete_sequence=COLORS,
            labels={"revenue":"Revenue ($)", "margin":"Avg Margin (%)"}
        )
        fig_bub.update_traces(textposition="top center", marker=dict(opacity=0.8))
        chart_layout(fig_bub)
        st.plotly_chart(fig_bub, use_container_width=True)

    st.markdown("<div class='section-header'>Category Performance Over Time</div>", unsafe_allow_html=True)
    ct = df.groupby(["category", time_col])["revenue"].sum().reset_index()
    fig_ct = px.area(ct, x=time_col, y="revenue", color="category",
                     color_discrete_sequence=COLORS, labels={"revenue":"Revenue ($)"})
    chart_layout(fig_ct, 380)
    st.plotly_chart(fig_ct, use_container_width=True)

    st.markdown("<div class='section-header'>CSAT by Category & Region</div>", unsafe_allow_html=True)
    csat_pivot = df.pivot_table(values="csat", index="category", columns="region", aggfunc="mean").round(2)
    fig_csat = px.imshow(csat_pivot, text_auto=True, aspect="auto",
                         color_continuous_scale=["#f87171","#fbbf24","#34d399"],
                         zmin=3.5, zmax=4.5, labels=dict(color="CSAT"))
    chart_layout(fig_csat, 340)
    st.plotly_chart(fig_csat, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 · SALES REPS
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("<div class='section-header'>Top Sales Representatives</div>", unsafe_allow_html=True)

    reps_df = df.groupby("rep").agg(
        revenue=("revenue","sum"), profit=("profit","sum"),
        orders=("revenue","count"), units=("units","sum"),
        margin=("margin","mean"), csat=("csat","mean")
    ).reset_index().sort_values("revenue", ascending=False)

    top_n = st.slider("Show top N reps", 5, 20, 10)
    top_reps = reps_df.head(top_n)

    c1, c2 = st.columns(2)
    with c1:
        fig_rep = px.bar(top_reps.sort_values("revenue"), x="revenue", y="rep",
                         orientation="h", color="margin",
                         color_continuous_scale=["#6366f1","#34d399"],
                         text=top_reps.sort_values("revenue")["revenue"].apply(lambda x: f"${x:,.0f}"))
        fig_rep.update_traces(textposition="outside")
        fig_rep.update_layout(title="Revenue by Rep")
        chart_layout(fig_rep)
        st.plotly_chart(fig_rep, use_container_width=True)

    with c2:
        fig_csat_rep = px.bar(top_reps.sort_values("csat"), x="csat", y="rep",
                              orientation="h", color="csat",
                              color_continuous_scale=["#f87171","#fbbf24","#34d399"],
                              text=top_reps.sort_values("csat")["csat"].apply(lambda x: f"{x:.2f}"),
                              range_color=[3.5, 4.5])
        fig_csat_rep.update_traces(textposition="outside")
        fig_csat_rep.update_layout(title="CSAT Score by Rep")
        chart_layout(fig_csat_rep)
        st.plotly_chart(fig_csat_rep, use_container_width=True)

    st.markdown("<div class='section-header'>Rep Performance Table</div>", unsafe_allow_html=True)
    display_df = reps_df.copy()
    display_df["revenue"]  = display_df["revenue"].apply(lambda x: f"${x:,.0f}")
    display_df["profit"]   = display_df["profit"].apply(lambda x: f"${x:,.0f}")
    display_df["margin"]   = display_df["margin"].apply(lambda x: f"{x:.1f}%")
    display_df["csat"]     = display_df["csat"].apply(lambda x: f"{x:.2f} ★")
    display_df.columns     = ["Rep","Revenue","Profit","Orders","Units","Margin","CSAT"]
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown("<div class='section-header'>Revenue vs CSAT Scatter</div>", unsafe_allow_html=True)
    fig_rv = px.scatter(reps_df, x="revenue", y="csat", size="orders",
                        text="rep", color="margin",
                        color_continuous_scale=["#6366f1","#34d399"],
                        labels={"revenue":"Total Revenue ($)", "csat":"Avg CSAT", "margin":"Margin %"})
    fig_rv.update_traces(textposition="top center", marker=dict(opacity=0.85))
    chart_layout(fig_rv, 420)
    st.plotly_chart(fig_rv, use_container_width=True)

# ─── Footer ──────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#6b7a99; font-size:12px'>SalesIQ BI · Built with Streamlit & Plotly · Demo synthetic data</p>",
    unsafe_allow_html=True
)