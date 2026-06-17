import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import html
from ai_engine import (
    segment_customer,
    generate_personalized_message,
    generate_customer_dna,
    generate_predictions,
    generate_explanation,
    generate_business_strategy,
    generate_timeline_data,
    simulate_whatif,
    ask_personax,
    generate_insight_summary,     # NEW — Mini Story Mode
    generate_timeline_interpretation, # NEW: Timeline insight
)

st.set_page_config(page_title="PersonaX AI Digital Twin", page_icon="🧬", layout="wide")

# ================================================================
# STYLING — PREMIUM GLASSMORPHISM + DARK FUTURISTIC THEME
# ================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&display=swap');

    /* --- Global Reset --- */
    * { font-family: 'Outfit', 'Inter', sans-serif; }

    /* --- SaaS Navbar Header --- */
    .saas-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(15, 18, 28, 0.8);
        backdrop-filter: blur(25px);
        -webkit-backdrop-filter: blur(25px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 18px;
        padding: 24px 32px;
        margin-bottom: 28px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }
    .saas-header::before {
        content: ''; position: absolute; top: -50%; left: -50%;
        width: 200%; height: 200%;
        background: radial-gradient(circle at 10% 30%, rgba(255, 45, 85, 0.04) 0%, transparent 40%),
                    radial-gradient(circle at 90% 70%, rgba(175, 82, 222, 0.04) 0%, transparent 40%);
        pointer-events: none;
    }
    .saas-header-left {
        z-index: 1;
    }
    .saas-title {
        font-size: 34px; font-weight: 800;
        background: linear-gradient(135deg, #FF2D55 0%, #AF52DE 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin: 4px 0; letter-spacing: -0.5px;
    }
    .saas-subtitle {
        color: #999; font-size: 14px; margin: 0; font-weight: 400;
    }
    .saas-badge {
        display: inline-block; padding: 4px 12px; border-radius: 12px;
        font-size: 10px; font-weight: 700; color: #FF2D55; letter-spacing: 1.5px;
        background: rgba(255, 45, 85, 0.1);
        border: 1px solid rgba(255, 45, 85, 0.25);
        text-transform: uppercase;
    }
    .saas-header-right {
        display: flex; gap: 24px; z-index: 1;
    }
    .saas-header-stat {
        text-align: right;
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 10px 18px;
        border-radius: 12px;
    }
    .saas-header-stat .stat-num {
        color: #FF2D55; font-size: 20px; font-weight: 800;
        display: block; margin-bottom: 2px;
    }
    .saas-header-stat .stat-label {
        color: #666; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;
    }

    /* --- Consistent Premium iOS Card Containers --- */
    .glass-card, .dna-card, .pred-card, .strategy-card, .whatif-box, .explain-box, .profile-card, .insight-story {
        background: rgba(20, 24, 38, 0.45) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 16px !important;
        padding: 22px !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
        transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.4s ease, box-shadow 0.4s ease !important;
        margin-bottom: 12px !important;
        text-align: left !important;
    }
    .glass-card:hover, .dna-card:hover, .pred-card:hover, .strategy-card:hover, .whatif-box:hover, .explain-box:hover, .profile-card:hover, .insight-story:hover {
        transform: scale(1.01) translateY(-2px) !important;
        border-color: rgba(255, 45, 85, 0.25) !important;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4), 0 0 15px rgba(255, 45, 85, 0.05) !important;
    }
    .glass-card .label, .dna-card .label, .pred-card .pred-label, .whatif-box .wif-label, .insight-story .story-label {
        color: #888; font-size: 11px; text-transform: uppercase;
        letter-spacing: 1.2px; margin-bottom: 8px; font-weight: 700;
    }
    .glass-card .value, .dna-card .value {
        color: #fff; font-size: 28px; font-weight: 800;
    }

    /* --- DNA Accent Colors --- */
    .dna-card .value.pink { color: #FF2D55; }
    .dna-card .value.purple { color: #AF52DE; }
    .dna-card .value.green { color: #34C759; }
    .dna-card .value.orange { color: #FF9500; }
    .dna-card .value.blue { color: #5AC8FA; }
    .dna-card .value.red { color: #FF3B30; }

    /* --- Smart Highlights --- */
    .highlight-green {
        background: rgba(52, 199, 89, 0.15); color: #34C759;
        padding: 4px 10px; border-radius: 8px; font-weight: 700;
        border: 1px solid rgba(52, 199, 89, 0.25);
    }
    .highlight-red {
        background: rgba(255, 59, 48, 0.15); color: #FF3B30;
        padding: 4px 10px; border-radius: 8px; font-weight: 700;
        border: 1px solid rgba(255, 59, 48, 0.25);
    }
    .highlight-purple {
        background: rgba(175, 82, 222, 0.15); color: #AF52DE;
        padding: 4px 10px; border-radius: 8px; font-weight: 700;
        border: 1px solid rgba(175, 82, 222, 0.25);
    }
    .highlight-orange {
        background: rgba(255, 149, 0, 0.15); color: #FF9500;
        padding: 4px 10px; border-radius: 8px; font-weight: 700;
        border: 1px solid rgba(255, 149, 0, 0.25);
    }

    /* --- Predictions & Actions Specific style overrides --- */
    .pred-card { border-left: 4px solid #FF2D55 !important; }
    .pred-card .pred-value { color: #f5f5f7; font-size: 18px; font-weight: 600; margin-top: 4px; }
    
    .explain-box { border: 1px solid rgba(175, 82, 222, 0.25) !important; color: #e5e5ea; line-height: 1.6; }
    .explain-box .explain-title { color: #AF52DE; font-weight: 700; font-size: 13px; text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 8px; }

    .strategy-card .strat-badge {
        display: inline-block; padding: 4px 12px; border-radius: 12px;
        font-size: 10px; font-weight: 700; color: #fff;
        margin-bottom: 12px; letter-spacing: 0.5px;
    }
    .strategy-card .strat-badge.high { background: #FF3B30; box-shadow: 0 0 10px rgba(255, 59, 48, 0.2); }
    .strategy-card .strat-badge.medium { background: #FF9500; box-shadow: 0 0 10px rgba(255, 149, 0, 0.2); }
    .strategy-card .strat-badge.low { background: #34C759; box-shadow: 0 0 10px rgba(52, 199, 89, 0.2); }

    .profile-card h4 { color: #FF2D55; margin-bottom: 12px; font-weight: 700; }
    .profile-card p { color: #d1d1d6; margin: 6px 0; font-size: 14px; line-height: 1.5; }

    /* --- Sidebar Custom Glow Menu Buttons --- */
    [data-testid="stSidebar"] {
        background-color: #0b0c10 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    [data-testid="stSidebar"] .stButton > button {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        color: #8e8e93 !important;
        border-radius: 10px !important;
        padding: 8px 16px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        text-align: left !important;
        justify-content: flex-start !important;
        margin-bottom: 6px !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.08) !important;
        color: #fff !important;
        border-color: rgba(255, 45, 85, 0.2) !important;
        transform: translateX(2px);
    }
    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #FF2D55, #AF52DE) !important;
        border: none !important;
        color: #fff !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(255, 45, 85, 0.25) !important;
    }

    /* --- What-If Comparison --- */
    .whatif-box .wif-before { color: #8e8e93; font-size: 20px; font-weight: 600; text-decoration: line-through; margin: 6px 0; }
    .whatif-box .wif-after { color: #34C759; font-size: 32px; font-weight: 800; }
    .whatif-box .wif-lift { color: #FF2D55; font-size: 14px; font-weight: 700; margin-top: 4px; }

    /* --- Chat Messages --- */
    .chat-user {
        background: rgba(255, 45, 85, 0.06);
        border: 1px solid rgba(255, 45, 85, 0.12);
        border-radius: 18px 18px 4px 18px;
        padding: 14px 20px; margin: 8px 0; color: #f5f5f7;
        font-size: 15px; line-height: 1.5;
    }
    .chat-user .chat-role { color: #FF2D55; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; }
    
    .chat-ai {
        background: rgba(20, 24, 38, 0.6);
        border: 1px solid rgba(175, 82, 222, 0.15);
        border-radius: 18px 18px 18px 4px;
        padding: 14px 20px; margin: 8px 0; color: #f5f5f7;
        font-size: 15px; line-height: 1.6;
    }
    .chat-ai .chat-role { color: #AF52DE; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; }

    /* --- UI Section Headers --- */
    .section-head {
        font-size: 20px; font-weight: 700; color: #FF2D55;
        border-bottom: 1px solid rgba(255, 45, 85, 0.15);
        padding-bottom: 8px; margin: 28px 0 16px 0;
        letter-spacing: 0.3px;
    }
    .section-divider {
        height: 1px; border: none;
        background: linear-gradient(90deg, transparent, rgba(255, 45, 85, 0.2), transparent);
        margin: 28px 0;
    }

    /* --- Premium Primary Buttons --- */
    .stButton > button[kind="primary"] {
        box-shadow: 0 4px 20px rgba(255, 45, 85, 0.2) !important;
        transition: all 0.3s ease !important;
        background: linear-gradient(135deg, #FF2D55, #AF52DE) !important;
        border: none !important;
        border-radius: 10px !important;
        color: white !important;
    }
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 6px 25px rgba(255, 45, 85, 0.35) !important;
        transform: translateY(-1px) !important;
    }

    /* --- Live Status dot --- */
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
    .live-dot {
        display: inline-block; width: 8px; height: 8px;
        background: #34C759; border-radius: 50%;
        margin-right: 6px; animation: pulse 2s infinite;
    }
</style>
""", unsafe_allow_html=True)

# ================================================================
# HELPER: Smart Highlight System
# ================================================================
def smart_highlight(value, metric_type="score"):
    """Return appropriate highlight CSS class based on value and type."""
    if metric_type == "score":
        if isinstance(value, (int, float)):
            if value >= 70: return "highlight-green"
            elif value <= 35: return "highlight-red"
            else: return "highlight-orange"
    elif metric_type == "churn":
        if value == "High": return "highlight-red"
        elif value == "Low": return "highlight-green"
        else: return "highlight-orange"
    elif metric_type == "mood":
        moods = {"Excited": "highlight-green", "Loyal": "highlight-green",
                 "Curious": "highlight-purple", "Hesitant": "highlight-orange",
                 "Drifting": "highlight-red"}
        return moods.get(value, "highlight-purple")
    elif metric_type == "priority":
        if value == "High": return "highlight-red"
        elif value == "Low": return "highlight-green"
        else: return "highlight-orange"
    return "highlight-purple"


# ---------- LOAD DATA ----------
@st.cache_data
def load_data():
    return pd.read_csv("customers.csv")

df = load_data()

# NEW: Confidence score helper
def render_confidence_badge(confidence):
    """Render a beautiful glassmorphism badge with confidence score."""
    if confidence >= 85:
        color = "#66BB6A"  # green
    elif confidence >= 70:
        color = "#FFA726"  # orange
    else:
        color = "#EF5350"  # red
        
    return f"""
    <div style="display: inline-flex; align-items: center; background: rgba(255,255,255,0.05); 
                border: 1px solid rgba(255,255,255,0.1); padding: 4px 10px; border-radius: 12px; margin-top: 6px;">
        <span style="font-size: 10px; font-weight: 700; color: #aaa; text-transform: uppercase; letter-spacing: 0.5px; margin-right: 6px;">AI Confidence:</span>
        <span style="font-size: 11px; font-weight: 800; color: {color};">{confidence}%</span>
    </div>
    """

# NEW: Cross-filter initialization
if "global_filter_cities" not in st.session_state:
    st.session_state["global_filter_cities"] = sorted(df["city"].unique())
if "global_filter_categories" not in st.session_state:
    st.session_state["global_filter_categories"] = sorted(df["fav_category"].unique())
if "global_filter_spend" not in st.session_state:
    st.session_state["global_filter_spend"] = (int(df["total_spent"].min()), int(df["total_spent"].max()))

def get_filtered_df():
    selected_cities = st.session_state.get("global_filter_cities", [])
    selected_categories = st.session_state.get("global_filter_categories", [])
    spent_range = st.session_state.get("global_filter_spend", (int(df["total_spent"].min()), int(df["total_spent"].max())))
    
    if not selected_cities:
        selected_cities = list(df["city"].unique())
    if not selected_categories:
        selected_categories = list(df["fav_category"].unique())
        
    return df[
        (df["city"].isin(selected_cities)) &
        (df["fav_category"].isin(selected_categories)) &
        (df["total_spent"].between(spent_range[0], spent_range[1]))
    ]

# FIX: performance
# NEW: Precompute AI columns to make cross-filtering instant and global
@st.cache_data
def precompute_data(_df):
    _df = _df.copy()
    segments = []
    churns = []
    
    # FIX: performance (only compute for first 20 records, use fast rule-based fallback for the rest)
    for i, (_, row) in enumerate(_df.iterrows()):
        c = row.to_dict()
        if i < 20:
            seg_res = segment_customer(c)
            # FIX: consistency
            dna_res = generate_customer_dna(c, segment=seg_res)
            segments.append(seg_res.get("segment", "New Explorer"))
            churns.append(dna_res.get("churn_risk", "Medium"))
        else:
            # Replicate baseline logic consistently
            abandoned = c.get("cart_abandoned") == "Yes"
            spent = c.get("total_spent", 0)
            visits = c.get("visits_per_month", 0)
            
            if abandoned:
                seg = "Cart Abandoner"
                churn = "High"
            elif spent > 30000:
                seg = "High-Value Loyalist"
                churn = "Low"
            elif c.get("avg_order_value", 9999) < 1000:
                seg = "Bargain Hunter"
                churn = "Medium"
            else:
                seg = "New Explorer"
                churn = "Medium"
            segments.append(seg)
            churns.append(churn)
            
    _df["segment"] = segments
    _df["churn_risk"] = churns
    return _df

# FIX: caching
@st.cache_data
def get_cached_timeline_data(customer_name):
    """Timeline loading function decorated with st.cache_data using name as simple string cache_key."""
    c_row = df[df["name"] == customer_name].iloc[0].to_dict()
    return generate_timeline_data(c_row)

df = precompute_data(df)
filtered_df = get_filtered_df()

# ================================================================
# UI UPGRADE: SaaS Top Navbar Header with Stats Panel
# ================================================================
st.markdown(f"""
<div class="saas-header">
    <div class="saas-header-left">
        <span class="saas-badge">🧬 PREDICTIVE AI DIGITAL TWIN</span>
        <h1 class="saas-title">PersonaX AI</h1>
        <p class="saas-subtitle">Predicting customer behavior in real-time, driving autonomous growth loops.</p>
    </div>
    <div class="saas-header-right">
        <div class="saas-header-stat">
            <span class="stat-num">{len(filtered_df)}</span>
            <span class="stat-label">Twins Active</span>
        </div>
        <div class="saas-header-stat">
            <span class="stat-num">₹{filtered_df['total_spent'].sum():,}</span>
            <span class="stat-label">Spend Tracked</span>
        </div>
        <div class="saas-header-stat">
            <span class="stat-num">{0 if filtered_df.empty else (filtered_df['cart_abandoned']=='Yes').mean()*100:.0f}%</span>
            <span class="stat-label">Cart Abandon Rate</span>
        </div>
        <div class="saas-header-stat">
            <span class="stat-num"><span class="live-dot"></span>Live</span>
            <span class="stat-label">System Status</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------- SIDEBAR ----------
# Initialize navigation page in state
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "📊 Dashboard"

# UI UPGRADE: Grouped Sidebar Navigation Buttons
st.sidebar.markdown("<h3 style='color: #FF2D55; margin-bottom: 12px; font-weight: 700; font-size: 14px; text-transform: uppercase; letter-spacing: 1.5px;'>📊 Analytics</h3>", unsafe_allow_html=True)
if st.sidebar.button("📊 Dashboard", key="btn_dashboard", type="primary" if st.session_state["current_page"] == "📊 Dashboard" else "secondary", use_container_width=True):
    st.session_state["current_page"] = "📊 Dashboard"
    st.rerun()
if st.sidebar.button("🧠 Segmentation", key="btn_segmentation", type="primary" if st.session_state["current_page"] == "🧠 Segmentation" else "secondary", use_container_width=True):
    st.session_state["current_page"] = "🧠 Segmentation"
    st.rerun()

st.sidebar.markdown("<h3 style='color: #AF52DE; margin-top: 20px; margin-bottom: 12px; font-weight: 700; font-size: 14px; text-transform: uppercase; letter-spacing: 1.5px;'>🧠 Intelligence</h3>", unsafe_allow_html=True)
if st.sidebar.button("🧬 Customer DNA", key="btn_dna", type="primary" if st.session_state["current_page"] == "🧬 Customer DNA" else "secondary", use_container_width=True):
    st.session_state["current_page"] = "🧬 Customer DNA"
    st.rerun()
if st.sidebar.button("📅 Timeline", key="btn_timeline", type="primary" if st.session_state["current_page"] == "📅 Timeline" else "secondary", use_container_width=True):
    st.session_state["current_page"] = "📅 Timeline"
    st.rerun()

st.sidebar.markdown("<h3 style='color: #34C759; margin-top: 20px; margin-bottom: 12px; font-weight: 700; font-size: 14px; text-transform: uppercase; letter-spacing: 1.5px;'>⚡ Actions</h3>", unsafe_allow_html=True)
if st.sidebar.button("✨ Personalize", key="btn_personalize", type="primary" if st.session_state["current_page"] == "✨ Personalize" else "secondary", use_container_width=True):
    st.session_state["current_page"] = "✨ Personalize"
    st.rerun()
if st.sidebar.button("🔬 What-If Lab", key="btn_whatif", type="primary" if st.session_state["current_page"] == "🔬 What-If Lab" else "secondary", use_container_width=True):
    st.session_state["current_page"] = "🔬 What-If Lab"
    st.rerun()
if st.sidebar.button("📈 Impact", key="btn_impact", type="primary" if st.session_state["current_page"] == "📈 Impact" else "secondary", use_container_width=True):
    st.session_state["current_page"] = "📈 Impact"
    st.rerun()

st.sidebar.markdown("<h3 style='color: #FF9500; margin-top: 20px; margin-bottom: 12px; font-weight: 700; font-size: 14px; text-transform: uppercase; letter-spacing: 1.5px;'>🤖 AI Recommender</h3>", unsafe_allow_html=True)
if st.sidebar.button("🤖 Ask PersonaX", key="btn_ask", type="primary" if st.session_state["current_page"] == "🤖 Ask PersonaX" else "secondary", use_container_width=True):
    st.session_state["current_page"] = "🤖 Ask PersonaX"
    st.rerun()
if st.sidebar.button("📊 AI Insights", key="btn_insights", type="primary" if st.session_state["current_page"] == "📊 AI Insights" else "secondary", use_container_width=True):
    st.session_state["current_page"] = "📊 AI Insights"
    st.rerun()

page = st.session_state["current_page"]

# ====================================================
# PAGE 1: DASHBOARD
# ====================================================
if page == "📊 Dashboard":
    # UI UPGRADE: Wrap Dashboard cross-filtering controls inside st.expander
    with st.expander("🔍 Global Filter Controls", expanded=False):
        f1, f2, f3 = st.columns(3)
        cities = sorted(df["city"].unique())
        categories = sorted(df["fav_category"].unique())
        min_spent = int(df["total_spent"].min())
        max_spent = int(df["total_spent"].max())
        
        with f1:
            st.multiselect(
                "City Filter", 
                options=cities, 
                key="global_filter_cities"
            )
        with f2:
            st.multiselect(
                "Category Filter", 
                options=categories, 
                key="global_filter_categories"
            )
        with f3:
            st.slider(
                "Spending Range (₹)", 
                min_spent, 
                max_spent, 
                key="global_filter_spend"
            )
        
    filtered_df = get_filtered_df()
    
    # NEW: Micro interactions
    st.toast("AI updated ⚡")
    
    if filtered_df.empty:
        st.warning("⚠️ No customers match the selected filters. Showing all data instead.")
        filtered_df = df

    # NEW: Summary Insight Panel
    st.markdown('<div class="section-head">💡 AI Summary Insights</div>', unsafe_allow_html=True)
    si_col1, si_col2, si_col3 = st.columns(3)
    
    with si_col1:
        top_seg = filtered_df["segment"].value_counts().idxmax() if not filtered_df.empty else "N/A"
        top_seg_count = filtered_df["segment"].value_counts().max() if not filtered_df.empty else 0
        st.markdown(f"""
        <div class="glass-card">
            <div class="label">🏆 Top Segment</div>
            <div class="value" style="font-size: 22px; color: #E91E63;">{top_seg}</div>
            <div style="font-size: 12px; color: #aaa; margin-top: 4px;">Dominating with {top_seg_count} customers</div>
        </div>
        """, unsafe_allow_html=True)
        
    with si_col2:
        city_rev = filtered_df.groupby("city")["total_spent"].sum()
        top_city = city_rev.idxmax() if not city_rev.empty else "N/A"
        top_city_rev = city_rev.max() if not city_rev.empty else 0
        st.markdown(f"""
        <div class="glass-card">
            <div class="label">📍 Top Revenue City</div>
            <div class="value" style="font-size: 22px; color: #CE93D8;">{top_city}</div>
            <div style="font-size: 12px; color: #aaa; margin-top: 4px;">Total Spend: ₹{top_city_rev:,}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with si_col3:
        high_risk_count = len(filtered_df[filtered_df["churn_risk"] == "High"])
        st.markdown(f"""
        <div class="glass-card">
            <div class="label">⚠️ High-Risk Customers</div>
            <div class="value" style="font-size: 22px; color: #EF5350;">{high_risk_count} Active</div>
            <div style="font-size: 12px; color: #aaa; margin-top: 4px;">Need immediate engagement</div>
        </div>
        """, unsafe_allow_html=True)

    # Core Metrics
    st.markdown('<div class="section-head">📊 Performance Metrics</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Customers", len(filtered_df))
    c2.metric("Avg. Order Value", f"₹{int(filtered_df['avg_order_value'].mean()) if not filtered_df.empty else 0}")
    c3.metric("Cart Abandon Rate", f"{0 if filtered_df.empty else (filtered_df['cart_abandoned']=='Yes').mean()*100:.0f}%")
    c4.metric("Total Revenue", f"₹{filtered_df['total_spent'].sum():,}")

    col1, col2 = st.columns(2)
    with col1:
        # NEW: Interactive chart (Category Pie Chart with tooltips)
        fig = px.pie(filtered_df, names="fav_category", title="Customers by Category",
                     color_discrete_sequence=px.colors.sequential.RdPu)
        fig.update_traces(
            hovertemplate="<b>Category:</b> %{label}<br><b>Customers:</b> %{value}<br><b>Percentage:</b> %{percent}<br><extra>Select category in explorer below to drill down</extra>"
        )
        # FIX: chart visibility
        fig.update_layout(
            template="plotly_dark",
            font=dict(color="white"),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        # NEW: Interactive chart (City Revenue Hover Details)
        city_data = filtered_df.groupby("city").agg(
            total_revenue=("total_spent", "sum"),
            total_customers=("name", "count"),
            avg_spending=("total_spent", "mean")
        ).reset_index()

        city_data["avg_spending"] = city_data["avg_spending"].round(0).astype(int)

        fig2 = px.bar(
            city_data,
            x="city", y="total_revenue",
            title="Revenue by City",
            color="total_revenue",
            color_continuous_scale="RdPu",
            hover_data=["total_customers", "avg_spending"],
            labels={"city": "City", "total_revenue": "Total Spend (₹)", "total_customers": "Total Customers", "avg_spending": "Avg Spend (₹)"}
        )
        fig2.update_traces(
            hovertemplate="<b>City:</b> %{x}<br><b>Total Revenue:</b> ₹%{y:,}<br><b>Total Customers:</b> %{customdata[0]}<br><b>Avg Spending:</b> ₹%{customdata[1]:,}<br><extra>Insight: Highlighted target markets</extra>"
        )
        # FIX: chart visibility
        fig2.update_layout(
            template="plotly_dark",
            font=dict(color="white"),
            coloraxis_showscale=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig2, use_container_width=True)

    # NEW: Interactive chart (Drill-down Explorer)
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-head">🔍 Category Drill-Down Explorer</div>', unsafe_allow_html=True)
    categories = sorted(filtered_df["fav_category"].unique())
    if categories:
        drill_cat = st.selectbox("Select a Category to Explore", options=categories, key="drill_cat")
        
        # Micro interaction toast when category changes
        st.toast(f"Drilling down: {drill_cat} ⚡")
        
        cat_df = filtered_df[filtered_df["fav_category"] == drill_cat]
        
        dcol1, dcol2 = st.columns(2)
        with dcol1:
            st.markdown(f"##### 🏆 Top Customers in {drill_cat}")
            top_cust = cat_df.nlargest(5, "total_spent")[["name", "city", "visits_per_month", "total_spent"]]
            top_cust.columns = ["Name", "City", "Visits/Mo", "Total Spent (₹)"]
            st.dataframe(top_cust, use_container_width=True, hide_index=True)
        with dcol2:
            st.markdown(f"##### 💰 City Revenue Breakdown for {drill_cat}")
            city_breakdown = cat_df.groupby("city")["total_spent"].sum().reset_index()
            fig_breakdown = px.bar(city_breakdown, x="city", y="total_spent",
                                   labels={"city": "City", "total_spent": "Spend (₹)"},
                                   color="total_spent", color_continuous_scale="RdPu")
            # FIX: chart visibility
            fig_breakdown.update_layout(
                template="plotly_dark",
                font=dict(color="white"),
                height=200,
                showlegend=False,
                margin=dict(t=10, b=10, l=10, r=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_breakdown, use_container_width=True)

    # NEW: Advanced charts
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-head">🔬 Advanced AI Analytics</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🎯 Behavior Clusters (Scatter)", "🌡️ Category vs City Heatmap", "📈 Engagement vs Spend Trend"])

    with tab1:
        fig_scatter_clusters = px.scatter(
            filtered_df,
            x="visits_per_month",
            y="total_spent",
            color="segment",
            hover_name="name",
            size="avg_order_value",
            labels={"visits_per_month": "Visits per Month", "total_spent": "Total Spent (₹)", "segment": "Segment", "avg_order_value": "Avg Order Value"},
            title="Customer Behavior Clusters",
            color_discrete_sequence=["#E91E63", "#9C27B0", "#673AB7", "#FF9800"]
        )
        fig_scatter_clusters.update_traces(
            hovertemplate="<b>Name:</b> %{hovertext}<br><b>Visits/Mo:</b> %{x}<br><b>Total Spent:</b> ₹%{y:,}<br><b>Avg Order:</b> ₹%{marker.size:,}<br><extra>Insight: High visits + high spend are Loyalists</extra>"
        )
        # FIX: chart visibility
        fig_scatter_clusters.update_layout(
            template="plotly_dark",
            font=dict(color="white"),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=400
        )
        st.plotly_chart(fig_scatter_clusters, use_container_width=True)

    with tab2:
        heatmap_data = filtered_df.pivot_table(
            index="city",
            columns="fav_category",
            values="total_spent",
            aggfunc="sum",
            fill_value=0
        )
        
        if not heatmap_data.empty:
            fig_heatmap = px.imshow(
                heatmap_data,
                labels=dict(x="Product Category", y="City", color="Total Spending (₹)"),
                x=heatmap_data.columns,
                y=heatmap_data.index,
                color_continuous_scale="RdPu",
                title="City vs Category Spending Heatmap"
            )
            fig_heatmap.update_traces(
                hovertemplate="<b>City:</b> %{y}<br><b>Category:</b> %{x}<br><b>Total Spend:</b> ₹%{z:,}<extra>Insight: Darker cells indicate higher sales concentration</extra>"
            )
            # FIX: chart visibility
            fig_heatmap.update_layout(
                template="plotly_dark",
                font=dict(color="white"),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=400
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
        else:
            st.info("No data available for heatmap.")

    with tab3:
        @st.cache_data
        def aggregate_timeline(names_list):
            from ai_engine import generate_timeline_data
            import pandas as pd
            import numpy as np
            
            if not names_list:
                return pd.DataFrame()
                
            all_dates = None
            all_eng = []
            all_spend = []
            
            sampled_names = names_list[:15]
            
            for name in sampled_names:
                c_row = df[df["name"] == name].iloc[0].to_dict()
                t_data = generate_timeline_data(c_row)
                if all_dates is None:
                    all_dates = t_data["dates"]
                all_eng.append(t_data["engagement"])
                all_spend.append(t_data["spending"])
                
            if all_dates is None:
                return pd.DataFrame()
                
            avg_eng = np.mean(all_eng, axis=0)
            avg_spend = np.mean(all_spend, axis=0)
            
            return pd.DataFrame({
                "Date": pd.to_datetime(all_dates),
                "Engagement": avg_eng,
                "Spending": avg_spend
            })
            
        with st.spinner("Calculating portfolio trends..."):
            trend_df = aggregate_timeline(filtered_df["name"].tolist())
            
        if not trend_df.empty:
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(
                x=trend_df["Date"], y=trend_df["Engagement"],
                mode="lines+markers", name="Avg Engagement",
                line=dict(color="#E91E63", width=2)
            ))
            fig_trend.add_trace(go.Bar(
                x=trend_df["Date"], y=trend_df["Spending"],
                name="Avg Daily Spend (₹)", marker_color="#CE93D8", opacity=0.6,
                yaxis="y2"
            ))
            
            # FIX: chart visibility
            fig_trend.update_layout(
                title="Portfolio Trend: Engagement vs Spending Over Time",
                height=400,
                template="plotly_dark",
                font=dict(color="white"),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(title="Engagement Score (0-100)", side="left"),
                yaxis2=dict(title="Daily Spend (₹)", side="right", overlaying="y", showgrid=False),
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
                margin=dict(t=50, b=30)
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("No data available for trend chart.")

    st.subheader("Customer Database")
    st.dataframe(filtered_df, use_container_width=True)

# ====================================================
# PAGE 2: SEGMENTATION
# ====================================================
elif page == "🧠 Segmentation":
    st.subheader("🧠 AI-Powered Customer Segmentation")
    st.write("Click below to let AI classify every customer into behavioral segments.")

    if st.button("🚀 Run AI Segmentation", type="primary"):
        progress = st.progress(0)
        segments = []
        sample = filtered_df.head(20)
        for i, (_, row) in enumerate(sample.iterrows()):
            result = segment_customer(row.to_dict())
            segments.append(result["segment"])
            progress.progress((i + 1) / len(sample))
        sample = sample.copy()
        sample["segment"] = segments
        st.session_state["segmented"] = sample
        st.success("✅ Segmentation complete!")
        st.toast("AI updated ⚡")

    if "segmented" in st.session_state:
        seg_df = st.session_state["segmented"]
        col1, col2 = st.columns([1, 2])
        with col1:
            counts = seg_df["segment"].value_counts().reset_index()
            counts.columns = ["segment", "count"]
            fig = px.pie(counts, names="segment", values="count",
                         title="Segment Distribution",
                         color_discrete_sequence=px.colors.sequential.RdPu)
            # FIX: chart visibility
            fig.update_layout(
                template="plotly_dark",
                font=dict(color="white"),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.dataframe(seg_df[["name", "fav_category", "total_spent", "segment"]],
                         use_container_width=True)

# ====================================================
# PAGE 3: PERSONALIZE
# ====================================================
elif page == "✨ Personalize":
    st.subheader("✨ Hyper-Personalized Content + AI Predictions")

    customer_name = st.selectbox("Select a customer", filtered_df["name"].tolist())
    customer = filtered_df[filtered_df["name"] == customer_name].iloc[0].to_dict()

    # ---- Real-Time Simulation Sliders ----
    st.markdown('<div class="section-head">🎛️ Real-Time Simulation</div>', unsafe_allow_html=True)
    st.caption("Adjust these values to see how predictions change in real-time.")

    sim_col1, sim_col2 = st.columns(2)
    with sim_col1:
        sim_visits = st.slider("📊 Visits per Month", 0, 30,
                               value=int(customer.get("visits_per_month", 10)), key="sim_visits")
    with sim_col2:
        sim_spent = st.slider("💰 Total Spent (₹)", 0, 100000, step=500,
                               value=int(customer.get("total_spent", 5000)), key="sim_spent")

    sim_customer = dict(customer)
    sim_customer["visits_per_month"] = sim_visits
    sim_customer["total_spent"] = sim_spent

    # NEW: Micro interactions for dynamic slider changes
    if "prev_sim_visits" not in st.session_state or st.session_state["prev_sim_visits"] != sim_visits or st.session_state["prev_sim_spent"] != sim_spent:
        st.session_state["prev_sim_visits"] = sim_visits
        st.session_state["prev_sim_spent"] = sim_spent
        st.toast("AI updated ⚡")

    # FIX: performance (reduce re-render cost) & FIX: consistency logic
    sim_key = f"sim_{sim_customer['name']}_{sim_visits}_{sim_spent}"
    if "current_sim_key" not in st.session_state or st.session_state["current_sim_key"] != sim_key:
        st.session_state["current_sim_key"] = sim_key
        with st.spinner("🧠 AI processing DNA metrics & predictions..."):
            # FIX: safe rendering
            try:
                st.session_state["sim_seg"] = segment_customer(sim_customer)
            except Exception:
                st.session_state["sim_seg"] = {"segment": "New Explorer", "reason": "System fallback classification.", "confidence": 50}

            try:
                st.session_state["sim_dna"] = generate_customer_dna(sim_customer, segment=st.session_state["sim_seg"])
            except Exception:
                st.session_state["sim_dna"] = {"intent_score": 50, "engagement_score": 50, "predicted_purchase": "Products", "churn_risk": "Medium", "lifetime_value_estimate": 5000, "confidence": 50}

            try:
                st.session_state["sim_preds"] = generate_predictions(sim_customer, dna=st.session_state["sim_dna"])
            except Exception:
                st.session_state["sim_preds"] = {"next_likely_action": "Browse products", "purchase_probability": 50, "best_time_to_engage": "Evening 6-8 PM", "best_channel": "Email", "mood": "Neutral", "confidence": 50}

            try:
                st.session_state["sim_strategy"] = generate_business_strategy(sim_customer, dna=st.session_state["sim_dna"], predictions=st.session_state["sim_preds"])
            except Exception:
                st.session_state["sim_strategy"] = {"best_action": "Nurture with customized campaign", "expected_outcome": "Steady engagement lift", "reason": "Standard fallback strategy", "priority": "Medium", "action_type": "Engagement", "confidence": 50}

            try:
                st.session_state["sim_insight_data"] = generate_insight_summary(sim_customer, dna=st.session_state["sim_dna"], predictions=st.session_state["sim_preds"])
            except Exception:
                st.session_state["sim_insight_data"] = {"summary": "Customer displays stable behavior metrics.", "confidence": 50}

    seg = st.session_state["sim_seg"]
    dna = st.session_state["sim_dna"]
    preds = st.session_state["sim_preds"]
    strategy = st.session_state["sim_strategy"]
    insight_data = st.session_state["sim_insight_data"]
    insight_summary = insight_data.get("summary", "")

    # FIX: html bug
    # FIX: safe rendering
    st.markdown('<div class="insight-story">', unsafe_allow_html=True)
    st.markdown('<div class="story-label">🧠 AI Insight Summary</div>', unsafe_allow_html=True)
    st.markdown('<div class="story-text" style="font-size: 16px; line-height: 1.7; color: #e8e0f0; font-weight: 400;">', unsafe_allow_html=True)
    st.write(insight_summary)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(render_confidence_badge(insight_data.get("confidence", 90)), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ---- Customer Profile + Message ----
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"""
        <div class="profile-card">
            <h4>👤 {sim_customer['name']}</h4>
            <p>🎂 <strong>Age:</strong> {sim_customer['age']} &nbsp;|&nbsp; 📍 <strong>City:</strong> {sim_customer['city']}</p>
            <p>❤️ <strong>Loves:</strong> {sim_customer['fav_category']}</p>
            <p>🛒 <strong>Last bought:</strong> {sim_customer['last_purchase']}</p>
            <p>💰 <strong>Total spent:</strong> ₹{sim_customer['total_spent']:,}</p>
            <p>📊 <strong>Visits/month:</strong> {sim_customer['visits_per_month']}</p>
            <p>⏰ <strong>Active time:</strong> {sim_customer['active_time']}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        if st.button("✨ Generate Personalized Message", type="primary"):
            with st.spinner("🧠 AI is thinking..."):
                # Use cached seg dynamically
                msg = generate_personalized_message(sim_customer, seg["segment"])
                explanation = generate_explanation(sim_customer, seg["segment"], msg)
            st.session_state["gen_msg"] = msg
            st.session_state["gen_explain"] = explanation
            st.toast("AI updated ⚡")

        if "gen_msg" in st.session_state and "current_sim_key" in st.session_state:
            msg = st.session_state["gen_msg"]
            explanation = st.session_state["gen_explain"]

            st.markdown(f"**🏷️ Segment:** `{seg['segment']}` — _{seg['reason']}_")
            # Display AI confidence score
            st.markdown(render_confidence_badge(msg.get("confidence", 85)), unsafe_allow_html=True)
            st.markdown("---")
            st.markdown(f"### 📧 {msg['subject']}")
            st.info(msg["body"])
            cc1, cc2 = st.columns(2)
            cc1.success(f"🎁 Offer: **{msg['offer']}**")
            cc2.warning(f"🛍️ Recommended: **{msg['recommended_product']}**")
            cc1.write(f"📲 **Channel:** {msg['best_channel']}")
            cc2.write(f"⏰ **Send time:** {msg['best_send_time']}")
            st.caption(f"💡 Why: {msg['reasoning']}")

            # FIX: html bug
            # FIX: safe rendering
            st.markdown('<div class="explain-box">', unsafe_allow_html=True)
            st.markdown('<div class="explain-title">🧠 Why This Recommendation?</div>', unsafe_allow_html=True)
            st.write(explanation)
            st.markdown('</div>', unsafe_allow_html=True)

    # ---- AI Predictions with Smart Highlights ----
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.markdown('<div class="section-head">🔮 AI Predictions</div>', unsafe_allow_html=True)
    st.caption("AI-powered behavioral predictions update dynamically with simulation sliders.")

    # Smart Highlights on prediction values
    prob_val = int(preds.get('purchase_probability', 50))
    prob_class = smart_highlight(prob_val)
    mood = preds.get("mood", "Neutral")
    mood_class = smart_highlight(mood, "mood")
    mood_emoji = {"Excited": "🔥", "Curious": "🤔", "Hesitant": "😟",
                  "Loyal": "💎", "Drifting": "🌊"}.get(mood, "😐")

    # FIX: html bug
    safe_next_action = html.escape(preds['next_likely_action'])
    safe_best_time = html.escape(preds['best_time_to_engage'])
    safe_best_channel = html.escape(preds['best_channel'])

    p1, p2 = st.columns(2)
    with p1:
        st.markdown(f"""
        <div class="pred-card">
            <div class="pred-label">🎯 Next Likely Action</div>
            <div class="pred-value">{safe_next_action}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="pred-card">
            <div class="pred-label">⏰ Best Time to Engage</div>
            <div class="pred-value">{safe_best_time}</div>
        </div>
        """, unsafe_allow_html=True)
    with p2:
        st.markdown(f"""
        <div class="pred-card">
            <div class="pred-label">🛒 Purchase Probability</div>
            <div class="pred-value"><span class="{prob_class}">{prob_val}%</span></div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="pred-card">
            <div class="pred-label">📲 Best Channel</div>
            <div class="pred-value">{safe_best_channel}</div>
        </div>
        """, unsafe_allow_html=True)

    # FIX: html bug
    safe_mood = html.escape(mood)
    st.markdown(f"""
    <div class="pred-card" style="text-align:center; border-left-color:#9C27B0;">
        <div class="pred-label">🧠 Customer Mood</div>
        <div class="pred-value">{mood_emoji} <span class="{mood_class}">{safe_mood}</span></div>
    </div>
    """, unsafe_allow_html=True)

    # Display Predictions confidence badge
    st.markdown(f"""
    <div style="text-align: center; margin-top: 10px;">
        {render_confidence_badge(preds.get("confidence", 80))}
    </div>
    """, unsafe_allow_html=True)

    # ---- AI Business Strategy ----
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.markdown('<div class="section-head">💡 AI Recommended Action</div>', unsafe_allow_html=True)

    priority = strategy.get("priority", "Medium").lower()
    action_type = strategy.get("action_type", "Engagement")

    # FIX: html bug
    # FIX: safe rendering
    st.markdown(f"""
    <div class="strategy-card">
        <span class="strat-badge {priority}">{strategy.get('priority', 'Medium')} Priority</span>
        <span class="strat-badge" style="background:#673AB7; margin-left:8px;">
            {action_type}
        </span>
    """, unsafe_allow_html=True)
    st.markdown('<div class="strat-action" style="color: #fff; font-size: 20px; font-weight: 700; margin: 8px 0; line-height: 1.3;">', unsafe_allow_html=True)
    st.write(strategy['best_action'])
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="strat-outcome" style="color: #66BB6A; font-size: 16px; font-weight: 600;">📈 ', unsafe_allow_html=True)
    st.write(strategy['expected_outcome'])
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="strat-reason" style="color: #999; font-size: 14px; margin-top: 8px; line-height: 1.6;">💬 ', unsafe_allow_html=True)
    st.write(strategy['reason'])
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(render_confidence_badge(strategy.get("confidence", 88)), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # NEW: AI Decision Flow
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.markdown('<div class="section-head">🔄 AI Decision Flow</div>', unsafe_allow_html=True)
    st.caption("How the AI processes DNA signals to predict actions and recommend strategy.")

    flow_col1, flow_col2, flow_col3 = st.columns(3)

    # FIX: html bug
    safe_flow_next = html.escape(preds['next_likely_action'])
    safe_flow_channel = html.escape(preds['best_channel'].split('—')[0].strip())
    safe_flow_action = html.escape(strategy['best_action'])
    safe_flow_action_type = html.escape(strategy['action_type'])

    with flow_col1:
        intent_class = smart_highlight(dna['intent_score'])
        st.markdown(f"""
        <div class="glass-card" style="border-top: 4px solid #E91E63; height: 100%;">
            <div style="font-size: 11px; font-weight: 700; color: #E91E63; text-transform: uppercase;">Step 1: DNA Insight</div>
            <h4 style="margin: 8px 0; color: #fff;">Intent Analyzer</h4>
            <p style="color: #ccc; font-size: 13px;">Identified purchase intent level is <strong class="{intent_class}">{dna['intent_score']}/100</strong> with a <strong>{dna['churn_risk']}</strong> churn risk profile.</p>
        </div>
        """, unsafe_allow_html=True)

    with flow_col2:
        st.markdown(f"""
        <div class="glass-card" style="border-top: 4px solid #9C27B0; height: 100%;">
            <div style="font-size: 11px; font-weight: 700; color: #9C27B0; text-transform: uppercase;">Step 2: AI Prediction</div>
            <h4 style="margin: 8px 0; color: #fff;">Behavior Predictor</h4>
            <p style="color: #ccc; font-size: 13px;">Next action: <strong>"{safe_flow_next}"</strong> via <strong>{safe_flow_channel}</strong>.</p>
        </div>
        """, unsafe_allow_html=True)

    with flow_col3:
        st.markdown(f"""
        <div class="glass-card" style="border-top: 4px solid #66BB6A; height: 100%;">
            <div style="font-size: 11px; font-weight: 700; color: #66BB6A; text-transform: uppercase;">Step 3: Strategy</div>
            <h4 style="margin: 8px 0; color: #fff;">Action Recommender</h4>
            <p style="color: #ccc; font-size: 13px;">Deploy <strong>"{safe_flow_action}"</strong> targeting <strong>{safe_flow_action_type}</strong>.</p>
        </div>
        """, unsafe_allow_html=True)


# ====================================================
# PAGE 4: CUSTOMER DNA
# ====================================================
elif page == "🧬 Customer DNA":
    st.subheader("🧬 Customer DNA Profile")
    st.caption("Deep AI analysis of customer behavioral DNA — scores, predictions, and lifetime value.")

    customer_name = st.selectbox("Select a customer", filtered_df["name"].tolist(), key="dna_select")
    customer = filtered_df[filtered_df["name"] == customer_name].iloc[0].to_dict()

    st.markdown('<div class="section-head">🎛️ Real-Time Simulation</div>', unsafe_allow_html=True)

    sim_col1, sim_col2 = st.columns(2)
    with sim_col1:
        sim_visits = st.slider("📊 Visits per Month", 0, 30,
                               value=int(customer.get("visits_per_month", 10)), key="dna_visits")
    with sim_col2:
        sim_spent = st.slider("💰 Total Spent (₹)", 0, 100000, step=500,
                               value=int(customer.get("total_spent", 5000)), key="dna_spent")

    sim_customer = dict(customer)
    sim_customer["visits_per_month"] = sim_visits
    sim_customer["total_spent"] = sim_spent

    # NEW: Micro interactions
    if "prev_dna_visits" not in st.session_state or st.session_state["prev_dna_visits"] != sim_visits or st.session_state["prev_dna_spent"] != sim_spent:
        st.session_state["prev_dna_visits"] = sim_visits
        st.session_state["prev_dna_spent"] = sim_spent
        st.toast("AI updated ⚡")

    # FIX: performance (reduce re-render cost) & FIX: consistency logic
    dna_key = f"dna_{sim_customer['name']}_{sim_visits}_{sim_spent}"
    if "current_dna_key" not in st.session_state or st.session_state["current_dna_key"] != dna_key:
        st.session_state["current_dna_key"] = dna_key
        st.session_state["dna_seg"] = segment_customer(sim_customer)
        st.session_state["dna_data"] = generate_customer_dna(sim_customer, segment=st.session_state["dna_seg"])
        
    dna = st.session_state["dna_data"]

    # Smart Highlights on DNA scores
    intent_class = smart_highlight(dna['intent_score'])
    eng_class = smart_highlight(dna['engagement_score'])
    churn_class = smart_highlight(dna['churn_risk'], 'churn')

    st.markdown('<div class="section-head">📊 DNA Scores</div>', unsafe_allow_html=True)
    st.markdown(render_confidence_badge(dna.get("confidence", 85)), unsafe_allow_html=True)

    d1, d2, d3, d4, d5 = st.columns(5)
    with d1:
        st.markdown(f"""
        <div class="dna-card">
            <div class="label">🎯 Intent Score</div>
            <div class="value"><span class="{intent_class}">{dna['intent_score']}</span></div>
        </div>
        """, unsafe_allow_html=True)
    with d2:
        st.markdown(f"""
        <div class="dna-card">
            <div class="label">⚡ Engagement</div>
            <div class="value"><span class="{eng_class}">{dna['engagement_score']}</span></div>
        </div>
        """, unsafe_allow_html=True)
    with d3:
        st.markdown(f"""
        <div class="dna-card">
            <div class="label">⚠️ Churn Risk</div>
            <div class="value"><span class="{churn_class}">{dna['churn_risk']}</span></div>
        </div>
        """, unsafe_allow_html=True)
    with d4:
        st.markdown(f"""
        <div class="dna-card">
            <div class="label">🛒 Predicted Buy</div>
            <div class="value blue" style="font-size:16px;">{html.escape(dna['predicted_purchase'])}</div>
        </div>
        """, unsafe_allow_html=True)
    with d5:
        ltv = dna["lifetime_value_estimate"]
        st.markdown(f"""
        <div class="dna-card">
            <div class="label">💎 Lifetime Value</div>
            <div class="value green">₹{ltv:,}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-head">📈 Score Visualization</div>', unsafe_allow_html=True)

    gauge_col1, gauge_col2 = st.columns(2)
    with gauge_col1:
        fig_intent = go.Figure(go.Indicator(
            mode="gauge+number", value=dna["intent_score"],
            title={"text": "Intent Score", "font": {"size": 16}},
            gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#E91E63"},
                   "steps": [{"range": [0, 33], "color": "#2a1a2e"},
                             {"range": [33, 66], "color": "#3a1a3e"},
                             {"range": [66, 100], "color": "#4a1a4e"}]}
        ))
        # FIX: chart visibility
        fig_intent.update_layout(
            template="plotly_dark",
            font=dict(color="white"),
            height=250,
            margin=dict(t=50, b=20, l=30, r=30),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_intent, use_container_width=True)
    with gauge_col2:
        fig_eng = go.Figure(go.Indicator(
            mode="gauge+number", value=dna["engagement_score"],
            title={"text": "Engagement Score", "font": {"size": 16}},
            gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#9C27B0"},
                   "steps": [{"range": [0, 33], "color": "#1a1a2e"},
                             {"range": [33, 66], "color": "#1a2a3e"},
                             {"range": [66, 100], "color": "#1a3a4e"}]}
        ))
        # FIX: chart visibility
        fig_eng.update_layout(
            template="plotly_dark",
            font=dict(color="white"),
            height=250,
            margin=dict(t=50, b=20, l=30, r=30),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_eng, use_container_width=True)

    st.markdown(f"""
    <div class="profile-card" style="margin-top: 12px;">
        <h4>👤 {sim_customer['name']} — Full Profile</h4>
        <p>🎂 <strong>Age:</strong> {sim_customer['age']} &nbsp;|&nbsp;
           📍 <strong>City:</strong> {sim_customer['city']} &nbsp;|&nbsp;
           ❤️ <strong>Loves:</strong> {sim_customer['fav_category']}</p>
        <p>🛒 <strong>Last purchase:</strong> {sim_customer['last_purchase']} &nbsp;|&nbsp;
           💰 <strong>Total spent:</strong> ₹{sim_customer['total_spent']:,} &nbsp;|&nbsp;
           📊 <strong>Visits/month:</strong> {sim_customer['visits_per_month']}</p>
        <p>🛑 <strong>Cart abandoned:</strong> {sim_customer['cart_abandoned']} &nbsp;|&nbsp;
           ⏰ <strong>Active time:</strong> {sim_customer['active_time']} &nbsp;|&nbsp;
           💳 <strong>Avg order:</strong> ₹{sim_customer['avg_order_value']:,}</p>
    </div>
    """, unsafe_allow_html=True)


# ====================================================
# PAGE 5: DIGITAL TWIN TIMELINE
# ====================================================
elif page == "📅 Timeline":
    st.subheader("📅 Customer Behavior Timeline")
    st.caption("Digital Twin: Past 30-day trend → Current state → 7-day AI prediction")

    customer_name = st.selectbox("Select a customer", filtered_df["name"].tolist(), key="tl_select")
    customer = filtered_df[filtered_df["name"] == customer_name].iloc[0].to_dict()

    # NEW: Micro interactions
    if "prev_tl_cust" not in st.session_state or st.session_state["prev_tl_cust"] != customer_name:
        st.session_state["prev_tl_cust"] = customer_name
        st.toast("AI updated ⚡")

    # FIX: caching timeline calculations using `@st.cache_data` helper
    timeline = get_cached_timeline_data(customer_name)
    today_idx = timeline["today_index"]

    tl_df = pd.DataFrame({
        "Date": pd.to_datetime(timeline["dates"]),
        "Engagement": timeline["engagement"],
        "Spending": timeline["spending"],
    })
    tl_df["Period"] = ["Past"] * today_idx + ["Today"] + ["Predicted"] * 7

    st.markdown('<div class="section-head">⚡ Engagement Score Over Time</div>', unsafe_allow_html=True)

    fig_eng = go.Figure()
    past = tl_df[tl_df["Period"].isin(["Past", "Today"])]
    fig_eng.add_trace(go.Scatter(
        x=past["Date"], y=past["Engagement"],
        mode="lines+markers", name="Actual",
        line=dict(color="#E91E63", width=2), marker=dict(size=3),
    ))
    future = tl_df[tl_df["Period"].isin(["Today", "Predicted"])]
    fig_eng.add_trace(go.Scatter(
        x=future["Date"], y=future["Engagement"],
        mode="lines+markers", name="AI Predicted",
        line=dict(color="#CE93D8", width=2, dash="dash"),
        marker=dict(size=4, symbol="diamond"),
    ))
    fig_eng.add_vline(x=tl_df.loc[today_idx, "Date"], line_dash="dot",
                       line_color="rgba(255,255,255,0.4)", annotation_text="Today")
    # FIX: chart visibility
    fig_eng.update_layout(
        height=350, template="plotly_dark",
        font=dict(color="white"),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis_title="Engagement Score", xaxis_title="",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=40, b=30),
    )
    st.plotly_chart(fig_eng, use_container_width=True)

    st.markdown('<div class="section-head">💰 Spending Pattern Over Time</div>', unsafe_allow_html=True)

    fig_spend = go.Figure()
    fig_spend.add_trace(go.Bar(x=past["Date"], y=past["Spending"],
                                name="Actual Spend", marker_color="#E91E63", opacity=0.8))
    fig_spend.add_trace(go.Bar(x=future["Date"], y=future["Spending"],
                                name="Predicted Spend", marker_color="#CE93D8", opacity=0.6))
    fig_spend.add_vline(x=tl_df.loc[today_idx, "Date"], line_dash="dot",
                         line_color="rgba(255,255,255,0.4)", annotation_text="Today")
    # FIX: chart visibility
    fig_spend.update_layout(
        height=300, template="plotly_dark",
        font=dict(color="white"),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis_title="Daily Spend (₹)", xaxis_title="", barmode="stack",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=40, b=30),
    )
    st.plotly_chart(fig_spend, use_container_width=True)

    # NEW: Timeline insight (Story-driven analysis)
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-head">🧠 AI Timeline Interpretation</div>', unsafe_allow_html=True)
    
    with st.spinner("AI is analyzing timeline trends..."):
        interpretation_data = generate_timeline_interpretation(timeline, customer)
        
    # FIX: html bug
    # FIX: safe rendering
    st.markdown("""
    <div class="insight-story" style="border-left: 5px solid #CE93D8;">
        <div class="story-label">📈 Trend Analysis</div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="story-text" style="font-size: 15px;">', unsafe_allow_html=True)
    st.write(interpretation_data['interpretation'])
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    col_h1, col_h2 = st.columns(2)
    for idx, highlight in enumerate(interpretation_data['highlights']):
        with col_h1 if idx % 2 == 0 else col_h2:
            # FIX: html bug
            # FIX: safe rendering
            st.markdown("""
            <div class="pred-card" style="border-left-color: #9C27B0; margin-bottom: 10px;">
                <div class="pred-label">Highlight Signal</div>
            """, unsafe_allow_html=True)
            st.markdown('<div class="pred-value" style="font-size: 14px; margin-top: 4px;">', unsafe_allow_html=True)
            st.write(highlight)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    avg_past_eng = round(np.mean(timeline["engagement"][:today_idx]), 1)
    avg_future_eng = round(np.mean(timeline["engagement"][today_idx+1:]), 1)
    eng_trend = avg_future_eng - avg_past_eng
    avg_past_spend = round(np.mean(timeline["spending"][:today_idx]))
    avg_future_spend = round(np.mean(timeline["spending"][today_idx+1:]))

    m1.metric("Avg Past Engagement", f"{avg_past_eng}")
    m2.metric("Predicted Engagement", f"{avg_future_eng}", f"{eng_trend:+.1f}")
    m3.metric("Avg Daily Spend", f"₹{avg_past_spend:,}")
    m4.metric("Predicted Daily Spend", f"₹{avg_future_spend:,}",
              f"₹{avg_future_spend - avg_past_spend:+,}")


# ====================================================
# PAGE 6: WHAT-IF LAB
# ====================================================
elif page == "🔬 What-If Lab":
    st.subheader("🔬 What-If Simulation Lab")
    st.caption("Test marketing interventions and see predicted impact BEFORE execution.")

    customer_name = st.selectbox("Select a customer", filtered_df["name"].tolist(), key="wif_select")
    customer = filtered_df[filtered_df["name"] == customer_name].iloc[0].to_dict()

    # NEW: Micro interactions
    if "prev_wif_cust" not in st.session_state or st.session_state["prev_wif_cust"] != customer_name:
        st.session_state["prev_wif_cust"] = customer_name
        st.toast("AI updated ⚡")

    st.markdown(f"""
    <div class="profile-card">
        <h4>👤 {customer['name']}</h4>
        <p>❤️ {customer['fav_category']} lover &nbsp;|&nbsp;
           💰 ₹{customer['total_spent']:,} spent &nbsp;|&nbsp;
           📊 {customer['visits_per_month']} visits/mo &nbsp;|&nbsp;
           🛑 Cart abandoned: {customer['cart_abandoned']}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-head">🧪 Choose a Scenario</div>', unsafe_allow_html=True)

    sc1, sc2, sc3 = st.columns(3)
    scenario = None
    with sc1:
        if st.button("🏷️ Apply 20% Discount", use_container_width=True, type="primary"):
            scenario = "20% Discount"
    with sc2:
        if st.button("🌙 Send Evening Campaign", use_container_width=True, type="primary"):
            scenario = "Evening Campaign"
    with sc3:
        if st.button("🛡️ Launch Retention Offer", use_container_width=True, type="primary"):
            scenario = "Retention Offer"

    if scenario:
        st.session_state["wif_scenario"] = scenario
        with st.spinner("🧠 AI is simulating..."):
            st.session_state["wif_result"] = simulate_whatif(customer, scenario)
        # NEW: Micro interactions
        st.success("Simulation applied 🚀")
        st.toast("AI updated ⚡")

    if "wif_result" in st.session_state:
        result = st.session_state["wif_result"]
        sc_name = st.session_state["wif_scenario"]

        # FIX: html bug
        safe_prob_before = result['before']['purchase_probability']
        safe_prob_after = result['after']['purchase_probability']
        safe_prob_lift = html.escape(result['lift']['probability_lift'])

        safe_conv_before = result['before']['conversion_rate']
        safe_conv_after = result['after']['conversion_rate']
        safe_conv_lift = html.escape(result['lift']['conversion_lift'])

        safe_rev_before = result['before']['monthly_revenue']
        safe_rev_after = result['after']['monthly_revenue']
        safe_rev_lift = html.escape(result['lift']['revenue_impact'])

        st.markdown(f'<div class="section-head">📊 Results: {html.escape(sc_name)}</div>', unsafe_allow_html=True)

        r1, r2, r3 = st.columns(3)
        with r1:
            st.markdown(f"""
            <div class="whatif-box">
                <div class="wif-label">🛒 Purchase Probability</div>
                <div class="wif-before">{safe_prob_before}%</div>
                <div class="wif-after">{safe_prob_after}%</div>
                <div class="wif-lift">{safe_prob_lift}</div>
            </div>
            """, unsafe_allow_html=True)
        with r2:
            st.markdown(f"""
            <div class="whatif-box">
                <div class="wif-label">📈 Conversion Rate</div>
                <div class="wif-before">{safe_conv_before}%</div>
                <div class="wif-after">{safe_conv_after}%</div>
                <div class="wif-lift">{safe_conv_lift}</div>
            </div>
            """, unsafe_allow_html=True)
        with r3:
            st.markdown(f"""
            <div class="whatif-box">
                <div class="wif-label">💰 Monthly Revenue</div>
                <div class="wif-before">₹{safe_rev_before:,}</div>
                <div class="wif-after">₹{safe_rev_after:,}</div>
                <div class="wif-lift">{safe_rev_lift}/mo</div>
            </div>
            """, unsafe_allow_html=True)

        compare_df = pd.DataFrame({
            "Metric": ["Purchase Prob.", "Conversion Rate", "Revenue (₹100s)"],
            "Before": [result["before"]["purchase_probability"],
                       result["before"]["conversion_rate"],
                       result["before"]["monthly_revenue"] / 100],
            "After": [result["after"]["purchase_probability"],
                      result["after"]["conversion_rate"],
                      result["after"]["monthly_revenue"] / 100],
        })
        fig_wif = go.Figure()
        fig_wif.add_trace(go.Bar(name="Before", x=compare_df["Metric"],
                                  y=compare_df["Before"], marker_color="#555"))
        fig_wif.add_trace(go.Bar(name="After", x=compare_df["Metric"],
                                  y=compare_df["After"], marker_color="#E91E63"))
        # FIX: chart visibility
        fig_wif.update_layout(
            barmode="group", height=320, template="plotly_dark",
            font=dict(color="white"),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            title="Before vs After Intervention", margin=dict(t=50, b=30),
        )
        st.plotly_chart(fig_wif, use_container_width=True)

        # FIX: html bug
        # FIX: safe rendering
        st.markdown("""
        <div class="explain-box">
            <div class="explain-title">🧠 AI Insight</div>
        """, unsafe_allow_html=True)
        st.write(result['insight'])
        st.markdown(render_confidence_badge(result.get("confidence", 92)), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ====================================================
# PAGE 7: AI INSIGHTS
# ====================================================
elif page == "📊 AI Insights":
    st.subheader("📊 Multi-Customer AI Insights Dashboard")
    st.caption("Portfolio-level intelligence across all customers.")

    @st.cache_data
    def compute_all_dna(_df):
        results = []
        for _, row in _df.iterrows():
            c = row.to_dict()
            # FIX: consistency
            seg = segment_customer(c)
            dna = generate_customer_dna(c, segment=seg)
            dna["name"] = c["name"]
            dna["total_spent"] = c["total_spent"]
            dna["visits_per_month"] = c["visits_per_month"]
            dna["fav_category"] = c["fav_category"]
            dna["cart_abandoned"] = c["cart_abandoned"]
            dna["age"] = c["age"]
            dna["city"] = c["city"]
            results.append(dna)
        return pd.DataFrame(results)

    with st.spinner("🧬 Running AI analysis on all customers..."):
        all_dna = compute_all_dna(filtered_df)

    m1, m2, m3, m4 = st.columns(4)
    high_churn = len(all_dna[all_dna["churn_risk"] == "High"])
    avg_intent = round(all_dna["intent_score"].mean(), 1) if not all_dna.empty else 0
    avg_engage = round(all_dna["engagement_score"].mean(), 1) if not all_dna.empty else 0
    total_ltv = all_dna["lifetime_value_estimate"].sum() if not all_dna.empty else 0

    m1.metric("🔥 High Churn Risk", f"{high_churn} customers")
    m2.metric("🎯 Avg Intent Score", f"{avg_intent}/100")
    m3.metric("⚡ Avg Engagement", f"{avg_engage}/100")
    m4.metric("💎 Total Portfolio LTV", f"₹{total_ltv:,}")

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown('<div class="section-head">💎 Top 5 High-Value Customers</div>', unsafe_allow_html=True)
        if not all_dna.empty:
            top5 = all_dna.nlargest(5, "lifetime_value_estimate")[
                ["name", "lifetime_value_estimate", "engagement_score", "intent_score"]
            ].reset_index(drop=True)
            top5.columns = ["Name", "Lifetime Value (₹)", "Engagement", "Intent"]
            top5.index = range(1, len(top5) + 1)
            st.dataframe(top5, use_container_width=True)
        else:
            st.info("No customer data matched.")

    with col_right:
        st.markdown('<div class="section-head">⚠️ High Churn Risk Customers</div>', unsafe_allow_html=True)
        if not all_dna.empty:
            churn_df = all_dna[all_dna["churn_risk"] == "High"][
                ["name", "churn_risk", "engagement_score", "visits_per_month", "total_spent"]
            ].reset_index(drop=True)
            churn_df.columns = ["Name", "Churn Risk", "Engagement", "Visits/Mo", "Total Spent"]
            if len(churn_df) > 0:
                st.dataframe(churn_df, use_container_width=True)
            else:
                st.success("✅ No high churn-risk customers detected!")
        else:
            st.info("No customer data matched.")

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    @st.cache_data
    def compute_all_segments(_df):
        segs = []
        for _, row in _df.iterrows():
            result = segment_customer(row.to_dict())
            segs.append(result["segment"])
        return segs

    with st.spinner("🧠 Segmenting all customers..."):
        all_segs = compute_all_segments(filtered_df)

    if not filtered_df.empty:
        seg_analysis = filtered_df.copy()
        seg_analysis["segment"] = all_segs

        st.markdown('<div class="section-head">🏆 Best Performing Segment</div>', unsafe_allow_html=True)

        seg_stats = seg_analysis.groupby("segment").agg(
            count=("name", "count"),
            avg_spent=("total_spent", "mean"),
            avg_visits=("visits_per_month", "mean"),
            total_revenue=("total_spent", "sum"),
        ).reset_index()
        seg_stats["avg_spent"] = seg_stats["avg_spent"].round(0).astype(int)
        seg_stats["avg_visits"] = seg_stats["avg_visits"].round(1)

        best_seg = seg_stats.loc[seg_stats["avg_spent"].idxmax()]

        bs1, bs2 = st.columns([1, 2])
        with bs1:
            st.markdown(f"""
            <div class="dna-card" style="padding:28px;">
                <div class="label">🏆 Top Segment</div>
                <div class="value pink" style="font-size:24px;">{best_seg['segment']}</div>
                <div style="color:#66BB6A; font-size:16px; margin-top:8px;">
                    ₹{int(best_seg['avg_spent']):,} avg spend &nbsp;|&nbsp; {best_seg['count']} customers
                </div>
            </div>
            """, unsafe_allow_html=True)
        with bs2:
            fig_seg = px.bar(seg_stats, x="segment", y="total_revenue",
                             color="segment", title="Revenue by Segment",
                             color_discrete_sequence=["#E91E63", "#9C27B0", "#673AB7", "#FF9800"])
            # FIX: chart visibility
            fig_seg.update_layout(
                height=300, template="plotly_dark",
                font=dict(color="white"),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False, margin=dict(t=50, b=30),
            )
            st.plotly_chart(fig_seg, use_container_width=True)
    else:
        st.info("No data available for segment performance.")

    st.markdown('<div class="section-head">📈 Engagement vs Spend Matrix</div>', unsafe_allow_html=True)

    if not all_dna.empty:
        scatter_df = all_dna.copy()
        fig_scatter = px.scatter(
            scatter_df, x="engagement_score", y="lifetime_value_estimate",
            size="intent_score", color="churn_risk",
            hover_name="name", size_max=30,
            color_discrete_map={"Low": "#66BB6A", "Medium": "#FFA726", "High": "#EF5350"},
            title="Customer Portfolio Map",
        )
        # FIX: chart visibility
        fig_scatter.update_layout(
            height=400, template="plotly_dark",
            font=dict(color="white"),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis_title="Engagement Score", yaxis_title="Lifetime Value (₹)",
            margin=dict(t=50, b=30),
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("No data available for portfolio matrix.")


# ====================================================
# PAGE 8: ASK PERSONAX CHAT
# ====================================================
elif page == "🤖 Ask PersonaX":
    st.subheader("🤖 Ask PersonaX AI")
    st.caption("Your AI marketing strategist. Ask anything about customers, segments, or growth strategies.")

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # Optional customer context
    use_ctx = st.checkbox("📎 Attach a customer context for personalized answers", value=False)
    chat_customer = None
    if use_ctx:
        cname = st.selectbox("Select customer", filtered_df["name"].tolist(), key="chat_cust")
        chat_customer = filtered_df[filtered_df["name"] == cname].iloc[0].to_dict()
        st.markdown(f"""
        <div class="profile-card" style="padding:14px 20px; margin-bottom:12px;">
            <p style="margin:0;">📎 Context: <strong>{chat_customer['name']}</strong> &nbsp;|&nbsp;
            {chat_customer['fav_category']} &nbsp;|&nbsp;
            ₹{chat_customer['total_spent']:,} spent &nbsp;|&nbsp;
            {chat_customer['visits_per_month']} visits/mo</p>
        </div>
        """, unsafe_allow_html=True)

    # NEW: Chat improvement context building
    top_seg_name = filtered_df["segment"].value_counts().idxmax() if not filtered_df.empty else "N/A"
    high_churn_count = len(filtered_df[filtered_df["churn_risk"] == "High"])
    best_city_name = filtered_df.groupby("city")["total_spent"].sum().idxmax() if not filtered_df.empty else "N/A"
    chat_context = f"Top performing segment: {top_seg_name}. High churn risk count: {high_churn_count} customers. Highest revenue city: {best_city_name}."

    # Chat-style display with bubbles
    # Chat-style display with bubbles
    for item in st.session_state["chat_history"]:
        # FIX: html bug
        # FIX: safe rendering
        st.markdown('<div class="chat-user"><div class="chat-role">👤 You</div>', unsafe_allow_html=True)
        st.write(item['question'])
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="chat-ai"><div class="chat-role">🧬 PersonaX AI</div>', unsafe_allow_html=True)
        st.write(item['answer'])
        st.markdown('</div>', unsafe_allow_html=True)

    # Chat input
    question = st.text_input(
        "Ask PersonaX AI anything...",
        placeholder="e.g. Who should I target today? / How to reduce churn? / Best campaign for high-value users?",
        key="chat_input"
    )

    if st.button("🚀 Ask", type="primary") and question:
        with st.spinner("🧠 AI is thinking..."):
            answer = ask_personax(question, customer=chat_customer, context=chat_context)
        st.session_state["chat_history"].append({
            "question": question,
            "answer": answer,
        })
        st.toast("AI updated ⚡")
        st.rerun()

    # NEW: Quick-ask buttons
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.markdown("**⚡ Quick Ask:**")
    qa1, qa2, qa3 = st.columns(3)
    with qa1:
        if st.button("🎯 Who to target today?", use_container_width=True):
            with st.spinner("🧠 AI is thinking..."):
                answer = ask_personax("Who should I target today?", customer=chat_customer, context=chat_context)
            st.session_state["chat_history"].append({
                "question": "Who should I target today?",
                "answer": answer,
            })
            st.toast("AI updated ⚡")
            st.rerun()
    with qa2:
        if st.button("⚠️ Churn risk customers?", use_container_width=True):
            with st.spinner("🧠 AI is thinking..."):
                answer = ask_personax("Which users are most likely to churn?", customer=chat_customer, context=chat_context)
            st.session_state["chat_history"].append({
                "question": "Which users are most likely to churn?",
                "answer": answer,
            })
            st.toast("AI updated ⚡")
            st.rerun()
    with qa3:
        if st.button("📈 Best campaign to run?", use_container_width=True):
            with st.spinner("🧠 AI is thinking..."):
                answer = ask_personax("What campaign should I run right now for maximum ROI?", customer=chat_customer, context=chat_context)
            st.session_state["chat_history"].append({
                "question": "What campaign should I run right now for maximum ROI?",
                "answer": answer,
            })
            st.toast("AI updated ⚡")
            st.rerun()

    # Clear chat history button
    if st.session_state["chat_history"]:
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        if st.button("🗑️ Clear Chat History"):
            st.session_state["chat_history"] = []
            st.toast("AI updated ⚡")
            st.rerun()


# ====================================================
# PAGE: IMPACT
# ====================================================
elif page == "📈 Impact":
    st.subheader("📈 Measurable Business Impact")

    c1, c2, c3 = st.columns(3)
    c1.metric("Click-Through Rate", "6.8%", "+4.7%")
    c2.metric("Conversion Rate", "3.9%", "+2.7%")
    c3.metric("Campaign Time", "30 sec", "-99%")

    st.markdown("### Before vs After PersonaAI")
    compare = pd.DataFrame({
        "Metric": ["CTR", "Conversion", "Engagement", "Revenue/User"],
        "Before AI": [2.1, 1.2, 18, 100],
        "After AI": [6.8, 3.9, 47, 240],
    })
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Before AI", x=compare["Metric"], y=compare["Before AI"], marker_color="#ccc"))
    fig.add_trace(go.Bar(name="After AI", x=compare["Metric"], y=compare["After AI"], marker_color="#E91E63"))
    # FIX: chart visibility
    fig.update_layout(
        barmode="group",
        template="plotly_dark",
        font=dict(color="white"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        title="Performance Lift with AI Personalization"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.success("🚀 **Scalability:** Same effort personalizes for 10 customers or 10 million.")