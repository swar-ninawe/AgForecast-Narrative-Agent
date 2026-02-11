import streamlit as st
import pandas as pd
import time
import pydeck as pdk
import requests
import json
import os

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="AgForecast",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- STYLES ----------------
# ---------------- THEME MANAGMENT ----------------
# Sidebar Toggle for Theme
with st.sidebar:
    st.markdown("### 🎨 Appearance")
    is_dark_mode = st.toggle("Dark Mode", value=True)
    status_text = "ON" if is_dark_mode else "OFF"
    status_color = "#00D17A" if is_dark_mode else "#ef4444"
    st.markdown(f"<span style='color: {status_color}; font-weight: 700; font-size: 0.85rem;'>{status_text}</span>", unsafe_allow_html=True)

# Define Premium Theme Palettes
if is_dark_mode:
    tm = {
        "bg": "#07090B", # Deep Charcoal
        "bg_grad_1": "rgba(255, 255, 255, 0.02)",
        "glass_bg": "rgba(18, 22, 26, 0.92)", # Frosted Glass
        "border": "rgba(255, 255, 255, 0.04)",
        "text": "#E6EEF6",
        "muted": "#9AA4B2",
        "cyan": "#00F6FF",
        "magenta": "#FF4DD2",
        "green": "#00D17A",
        "amber": "#FFB86B",
        "shadow": "0 18px 40px rgba(0,0,0,0.6)"
    }
else:
    # Pro Light Mode (Inverted High Contrast)
    tm = {
        "bg": "#F5F7FA",
        "bg_grad_1": "rgba(0, 0, 0, 0.03)",
        "glass_bg": "rgba(255, 255, 255, 0.9)",
        "border": "rgba(0, 0, 0, 0.06)",
        "text": "#111827",
        "muted": "#6B7280",
        "cyan": "#00A3A8", # Darker for white bg
        "magenta": "#D128A8",
        "green": "#008F53",
        "amber": "#D97706",
        "shadow": "0 4px 12px rgba(0,0,0,0.08)"
    }

# ---------------- STYLES ----------------
st.markdown(f"""
<style>
/* IMPORTS: Sora (Headers), Montserrat (Numbers), Inter (Body) */
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@600;700&family=Montserrat+Alternates:wght@700;800&family=Inter:wght@400;500;600&display=swap');

/* VARIABLES */
:root {{
    --bg: {tm["bg"]};
    --glass: {tm["glass_bg"]};
    --border: {tm["border"]};
    --fg: {tm["text"]};
    --muted: {tm["muted"]};
    --cyan: {tm["cyan"]};
    --magenta: {tm["magenta"]};
    --green: {tm["green"]};
    --amber: {tm["amber"]};
}}

/* BASE SETTINGS */
body {{
    background-color: var(--bg);
    color: var(--fg);
    font-family: 'Inter', sans-serif;
}}

[data-testid="stAppViewContainer"] {{
    background-color: var(--bg);
    background-image: 
        radial-gradient(circle at 10% 20%, rgba(0, 246, 255, 0.03) 0%, transparent 20%),
        radial-gradient(circle at 90% 80%, rgba(255, 77, 210, 0.03) 0%, transparent 20%);
}}

[data-testid="stHeader"] {{
    background: transparent;
}}

/* GLOWING TEXT UTILITY (Softened) */
.neon-text {{
    color: var(--fg);
    text-shadow: 
        0 0 10px rgba(0, 246, 255, 0.5),
        0 0 20px rgba(0, 246, 255, 0.3);
}}

.neon-text-magenta {{
    color: #fff;
    text-shadow: 
        0 0 10px rgba(255, 255, 255, 0.6),
        0 0 20px rgba(255, 77, 210, 0.4),
        0 0 40px rgba(255, 77, 210, 0.2);
}}

/* GLOBAL HEADER GLOW (Tasteful) */
h1, h2, h3, h4 {{
    font-family: 'Sora', sans-serif;
    letter-spacing: -0.5px;
    color: var(--fg) !important;
    text-shadow: 0 4px 12px rgba(0, 0, 0, 0.5); /* Deep shadow for contrast */
}}

/* HOVER GLOW FOR HEADERS */
h1:hover, h2:hover {{
    text-shadow: 0 0 15px rgba(255, 255, 255, 0.15);
    transition: text-shadow 0.3s ease;
}}

/* LOGIN CARD */
.login-card {{
    background: var(--glass);
    border: 1px solid var(--border);
    backdrop-filter: blur(14px);
    padding: 40px;
    border-radius: 20px;
    box-shadow: {tm["shadow"]};
    width: 100%;
    max-width: 400px;
    margin: auto;
    animation: slideUp 0.6s cubic-bezier(.22,.98,.36,1) forwards;
}}

/* ANIMATIONS */
@keyframes slideUp {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes pulse {{
    0% {{ box-shadow: 0 0 0 0 rgba(0, 246, 255, 0.4); }}
    70% {{ box-shadow: 0 0 0 10px rgba(0, 246, 255, 0); }}
    100% {{ box-shadow: 0 0 0 0 rgba(0, 246, 255, 0); }}
}}
@keyframes neonBreathe {{
    0% {{ box-shadow: 0 0 20px rgba(0, 209, 122, 0.15); border-color: rgba(0, 209, 122, 0.2); }}
    50% {{ box-shadow: 0 0 40px rgba(0, 209, 122, 0.35); border-color: rgba(0, 209, 122, 0.5); }}
    100% {{ box-shadow: 0 0 20px rgba(0, 209, 122, 0.15); border-color: rgba(0, 209, 122, 0.2); }}
}}

/* PARTICLE GRID BACKGROUND (Subtle) */
[data-testid="stAppViewContainer"]::before {{
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    background-image: 
        radial-gradient(circle, rgba(255,255,255,0.015) 1px, transparent 1px);
    background-size: 40px 40px;
    z-index: 0;
    opacity: 0.5;
}}

/* GLASS CARD CLASS */
.glass-card {{
    background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
    backdrop-filter: blur(14px) saturate(120%);
    border: 1px solid var(--border);
    border-radius: 16px;
    color: var(--fg);
    transition: transform 0.38s cubic-bezier(.22,.98,.36,1), box-shadow 0.38s;
    animation: slideUp 0.4s ease-out;
}}
.glass-card:hover {{
    transform: translateY(-6px);
    box-shadow: 0 18px 40px rgba(0,0,0,0.6);
    border-top-color: var(--cyan);
}}

/* SIGNAL CARD (Neon Breathing) */
.signal-card {{
    background: var(--glass);
    border: 2px solid rgba(0, 209, 122, 0.3);
    border-radius: 18px;
    padding: 28px;
    text-align: center;
    box-shadow: 0 6px 30px rgba(0,0,0,0.2);
    margin-bottom: 20px;
}}
.signal-card.breathing {{
    animation: neonBreathe 2s infinite ease-in-out;
}}

/* KPI CONTAINER */
.kpi-container {{
    font-family: 'Montserrat Alternates', sans-serif;
    font-weight: 800;
    color: var(--fg);
    animation: slideUp 0.5s ease-out;
}}
.kpi-value {{
    font-size: 3.5rem;
    line-height: 1;
    text-shadow: 0 0 20px rgba(0, 246, 255, 0.15);
}}
.kpi-label {{
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    color: var(--muted);
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
}}

/* PROGRESS BAR (Momentum) */
.progress-bar-container {{
    background: rgba(255,255,255,0.05);
    border-radius: 8px;
    height: 10px;
    overflow: hidden;
}}
.progress-bar-fill {{
    height: 100%;
    background: linear-gradient(90deg, var(--cyan), var(--green));
    border-radius: 8px;
    transition: width 0.8s cubic-bezier(.22,.98,.36,1);
}}

/* TAG CHIPS */
.tag-chip {{
    background: rgba(255,255,255,0.05);
    border: 1px solid var(--border);
    padding: 5px 14px;
    border-radius: 6px;
    font-size: 0.7rem;
    font-family: 'Sora', sans-serif;
    color: var(--muted);
    display: inline-block;
    margin: 4px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

/* EXPANDER GLASS STYLE */
div[data-testid="stExpander"] {{
    background: var(--glass);
    backdrop-filter: blur(14px);
    border: 1px solid var(--border);
    border-radius: 16px;
    box-shadow: {tm["shadow"]};
    transition: transform 0.38s cubic-bezier(.22,.98,.36,1);
    animation: slideUp 0.4s ease-out;
}}
div[data-testid="stExpander"]:hover {{
    transform: translateY(-4px);
    border-top: 1px solid var(--cyan);
}}

/* BUTTONS */
div[data-testid="stButton"] > button {{
    background: linear-gradient(135deg, var(--cyan) 0%, #00C2FF 100%);
    color: #000;
    font-weight: 700;
    font-family: 'Sora', sans-serif;
    border: none;
    border-radius: 999px;
    padding: 0.6rem 1.5rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(0, 246, 255, 0.3);
}}
div[data-testid="stButton"] > button:hover {{
    transform: scale(1.05);
    box-shadow: 0 6px 25px rgba(0, 246, 255, 0.5);
}}

/* REDUCED MOTION SUPPORT */
@media (prefers-reduced-motion: reduce) {{
    *, *::before, *::after {{
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }}
}}

</style>
""", unsafe_allow_html=True)

# ---------------- DATA LOADING ----------------
# UPDATED: Sending POST request to match n8n configuration
N8N_WEBHOOK_URL = "https://arjunbhosale.app.n8n.cloud/webhook/NARRATIVEDETECTINGAGENTWORKFLOW"

# PATH RESOLUTION FOR ASSETS
import os
import base64

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(BASE_DIR, "logo.png")

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

try:
    img_base64 = get_base64_of_bin_file(logo_path)
    logo_html = f'<img src="data:image/png;base64,{img_base64}" width="120" style="margin-bottom: 20px;">'
except:
    logo_html = "" # Fallback

@st.cache_data(ttl=600)  # Cache for 10 minutes
def fetch_live_data_cached():
    """Fetching data without any UI elements to avoid CacheReplayClosureError"""
    try:
        response = requests.post(N8N_WEBHOOK_URL)
        response.raise_for_status()
        return response.json(), None  # Return (data, error_message)
    except Exception as e:
        error_text = str(e)
        if hasattr(e, 'response') and e.response is not None:
             error_text = f"Server Error ({e.response.status_code}): {e.response.text}"
        return None, error_text

def get_market_data():
    # 1. Try fetching live data with UI feedback
    with st.spinner("🧠 Connecting to n8n logic core..."):
        data, error = fetch_live_data_cached()
    
    if data:
        if isinstance(data, list) and len(data) > 0:
            data = data[0]
        st.toast("✅ Live market data fetched successfully!", icon="📡")
        return data, None

    # 2. Handle Errors
    if error:
        st.error(f"⚠️ Live Connection Failed: {error}")
        st.warning("🔄 Switching to offline/cached data mode...")

    # 3. Fallback to local file
    file_path = "n8n_data.json"
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
            if isinstance(data, list) and len(data) > 0:
                return data[0], error # Return data + error status
            return data, error
    
    return None, error

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------------- LOGIN (PREMIUM UI) ----------------
if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        # Unified Card with Embedded Image to fix "Empty Box" issue
        st.markdown(f"""
        <div class='login-card'>
            {logo_html}
            <h1 class='neon-text-magenta' style='font-size: 2.5rem; margin-bottom: 10px;'>WELCOME BACK</h1>
            <p style='color: var(--muted); font-size: 1.1rem; letter-spacing: 1px;'>Sign in to access AgForecast</p>
        </div>
        """, unsafe_allow_html=True)
        
        name = st.text_input("Username", placeholder="Enter your name")
        email = st.text_input("Email Address", placeholder="name@gmail.com")
        
        if st.button("Sign In", type="primary", use_container_width=True):
            if name and email.endswith("@gmail.com"):
                st.session_state.logged_in = True
                st.session_state.user_name = name
                st.rerun()
            else:
                st.error("Please enter a valid Gmail address.")
    
    st.markdown("<br><br><br>", unsafe_allow_html=True) 
    st.stop()

# ---------------- DATA LOADING (AFTER LOGIN) ----------------
data, error = get_market_data()

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.image(logo_path, use_container_width=True)
    st.markdown("### 📊 Market Summary")
    if data:
        ms = data.get("market_state", {})
        
        # Vertical Tag Stack for Sidebar
        st.markdown(f"""
        <div style='background:rgba(255,255,255,0.03); padding:15px; border-radius:12px; border:1px solid var(--border);'>
            <div style='margin-bottom:12px;'>
                <span style='font-size:0.8rem; color:var(--muted); text-transform:uppercase;'>Macro Regime</span>
                <div style='font-size:1.2rem; font-weight:700; color:var(--cyan);'>{ms.get('macro_regime', 'N/A')}</div>
            </div>
            <div style='margin-bottom:12px;'>
                <span style='font-size:0.8rem; color:var(--muted); text-transform:uppercase;'>Trend</span>
                <div style='font-size:1.2rem; font-weight:700; color:var(--purple);'>{ms.get('silver_trend', 'N/A').title()}</div>
            </div>
             <div>
                <span style='font-size:0.8rem; color:var(--muted); text-transform:uppercase;'>Volatility</span>
                <div style='font-size:1.2rem; font-weight:700; color:var(--amber);'>{ms.get('volatility_level', 'N/A').title()}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    
    # Data Source Status
    if error:
         st.markdown(f"<div style='background:rgba(220,53,69,0.2); color:#ff6b6b; padding:8px; border-radius:8px; text-align:center; border:1px solid #ff6b6b;'>🔴 Offline Mode</div>", unsafe_allow_html=True)
    else:
         st.markdown(f"<div style='background:linear-gradient(90deg, rgba(0,209,122,0.2), transparent); color:var(--green); padding:8px 12px; border-radius:99px; border:1px solid var(--green); font-size:0.85rem; font-weight:600;'>🟢 Source: Live n8n Workflow</div>", unsafe_allow_html=True)

    st.caption("Powered by n8n Workflow Engine")

# ---------------- HEADER ----------------
l, r = st.columns([8,1])
with l:
    st.markdown(f"<h1 class='neon-text' style='font-size:3rem;'>AgForecast <span style='font-size:1.5rem; vertical-align:middle'>🧬</span></h1>", unsafe_allow_html=True)
with r:
    st.markdown(f"""
        <div style='
            width: 48px;
            height: 48px;
            border-radius: 50%;
            background: var(--glass);
            border: 2px solid var(--cyan);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.3rem;
            font-weight: 700;
            color: var(--fg);
            box-shadow: 0 0 15px rgba(0,246,255,0.2);
        '>{st.session_state.user_name[0].upper()}</div>
    """, unsafe_allow_html=True)

st.markdown("---")

if not data:
    st.error("❌ No data received from n8n backend. Please check n8n_data.json.")
    st.stop()

# ---------------- MAIN DASHBOARD ----------------

import yfinance as yf

@st.cache_data(ttl=300) # Cache for 5 minutes
def fetch_market_pulse():
    """Fetches live Silver price, INR rate, and ETF data"""
    try:
        # Batch fetch all tickers
        tickers = yf.Tickers("SI=F INR=X SLV SIVR SIL")
        
        # Silver Futures
        si = tickers.tickers["SI=F"].history(period="2d")
        current_si = si["Close"].iloc[-1] if not si.empty else 0
        prev_si = si["Close"].iloc[-2] if len(si) > 1 else current_si
        si_change = ((current_si - prev_si) / prev_si) * 100
        
        # USD/INR
        inr = tickers.tickers["INR=X"].history(period="1d")
        current_inr = inr["Close"].iloc[-1] if not inr.empty else 83.0
        
        # ETFs
        etf_data = []
        for sym in ["SLV", "SIVR", "SIL"]:
            hist = tickers.tickers[sym].history(period="2d")
            if not hist.empty:
                curr = hist["Close"].iloc[-1]
                prev = hist["Close"].iloc[-2] if len(hist) > 1 else curr
                chg = ((curr - prev) / prev) * 100
                etf_data.append({"Ticker": sym, "Price": curr, "Change %": chg})
                
        return current_si, si_change, current_inr, etf_data
    except Exception:
        return 0, 0, 0, []

@st.cache_data(ttl=3600) # Cache price data for 1 hour
def fetch_price_history():
    try:
        # Fetch Silver Futures (SI=F)
        ticker = yf.Ticker("SI=F")
        hist = ticker.history(period="1mo")
        return hist
    except Exception as e:
        return None

# 0. MARKET PULSE (HERO SECTION)
current_ag, ag_change, current_inr, etfs = fetch_market_pulse()

mp_c1, mp_c2, mp_c3 = st.columns([1.5, 1, 2])

with mp_c1:
    delta_color = "var(--green)" if ag_change >= 0 else "#ef4444"
    arrow = "▲" if ag_change >= 0 else "▼"
    
    st.markdown(f"""
    <div class='kpi-container'>
        <div class='kpi-label'>Silver Futures (USD)</div>
        <div class='kpi-value neon-text'>{current_ag:.2f}</div>
        <div style='font-size: 1.2rem; color: {delta_color}; font-weight: 700; margin-top: 5px;'>
            {arrow} {ag_change:.2f}%
        </div>
    </div>
    """, unsafe_allow_html=True)

with mp_c2:
    st.markdown(f"""
    <div class='kpi-container' style='opacity:0.8'>
        <div class='kpi-label'>USD / INR</div>
        <div class='kpi-value' style='font-size:2.5rem;'>₹{current_inr:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with mp_c3:
    st.markdown("<div class='kpi-label' style='margin-bottom:10px;'>ETF WATCHLIST</div>", unsafe_allow_html=True)
    if etfs:
        cols = st.columns(len(etfs))
        for idx, etf in enumerate(etfs):
            c_color = "var(--green)" if etf['Change %'] >= 0 else "#ef4444"
            with cols[idx]:
                st.markdown(f"""
                <div style='background:rgba(255,255,255,0.05); padding:10px; border-radius:12px; text-align:center; border:1px solid var(--border);'>
                    <div style='font-weight:700; color:var(--fg); font-size:0.9rem;'>{etf['Ticker']}</div>
                    <div style='font-size:1.1rem; color:{c_color}; font-weight:800;'>{etf['Change %']:+.1f}%</div>
                </div>
                """, unsafe_allow_html=True)

st.markdown("---")

# 1. MARKET STATE & SUMMARY
st.subheader("📡 Market Summary & Signal")
m_summary = data.get("market_summary", {})
signal = data.get("trading_signal", {})

col1, col2 = st.columns([2, 1])

with col1:
    st.info(f"**Current Story:** {m_summary.get('current_market_story', 'N/A')}")
    st.markdown(f"**Forward Outlook:** {m_summary.get('forward_outlook', 'N/A')}")

with col2:
    sig_label = signal.get("signal", "NEUTRAL").upper().replace("_", " ")
    confidence = signal.get("confidence", 0.0)
    sig_color = "var(--green)" if "buy" in sig_label.lower() else "#ef4444"
    if "neutral" in sig_label.lower(): sig_color = "var(--muted)"
    
    # Add breathing class if confidence > 75%
    breathing_class = "breathing" if confidence > 0.75 else ""
    
    st.markdown(f"""
    <div class='signal-card {breathing_class}'>
        <h2 style='color: {sig_color}; margin: 0; font-size: 2.2rem; font-weight: 800; letter-spacing: 1px;'>{sig_label}</h2>
        <p style='margin: 10px 0 0 0; font-weight: 600; color: var(--muted); font-size: 1rem;'>Confidence: {confidence*100:.0f}%</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📝 See Reasoning", expanded=False):
        for reason in signal.get("reasoning", []):
            st.markdown(f"- {reason}")

import plotly.express as px
import plotly.graph_objects as go

# ... (Previous code) ...

# ---------------- CHARTS ----------------
def create_macro_radar(macro_data):
    """Creates a Radar Chart for Macro Pressure"""
    categories = [k.replace("_", " ").title() for k in macro_data.keys()]
    values = [v * 100 for v in macro_data.values()]
    
    fig = go.Figure(data=go.Scatterpolar(
      r=values,
      theta=categories,
      fill='toself',
      name='Macro Pressure'
    ))
    
    fig.update_layout(
      polar=dict(
        radialaxis=dict(
          visible=True,
          range=[0, 100]
        )),
      showlegend=False,
      margin=dict(l=40, r=40, t=40, b=40),
      height=300
    )
    return fig

def create_narrative_scatter(narratives):
    """Creates a Scatter Plot for Narrative Confidence vs Momentum"""
    df = pd.DataFrame(narratives)
    if df.empty: return None
    
    fig = px.scatter(
        df, 
        x="confidence_score", 
        y="momentum_score",
        size=[10]*len(df), # Fixed bubble size or based on another metric
        color="narrative_type",
        hover_name="narrative_name", # Shows title on hover
        hover_data=["key_drivers"],
        title="Narrative Matrix: Confidence vs Momentum",
        labels={"confidence_score": "Confidence", "momentum_score": "Momentum", "narrative_type": "Type"}
    )
    # Removed fixed textposition to keep chart clean
    fig.update_layout(height=400, xaxis_range=[0, 1], yaxis_range=[0, 1])
    return fig

# ... (Inside Main Dashboard) ...

# 2. MACRO PRESSURE INDEX (Replacing simple metrics with Radar + Metrics)
st.markdown("### 📉 Macro Pressure Index")
macro = data.get("macro_pressure_index", {})

mac_col1, mac_col2 = st.columns([1, 2])
with mac_col1:
    # Key Metrics List
    for k, v in macro.items():
        st.metric(k.replace("_", " ").title(), f"{v*100:.0f}%")
with mac_col2:
    # Radar Chart
    st.plotly_chart(create_macro_radar(macro), use_container_width=True)

st.markdown("---")

# 3. DOMINANT NARRATIVES (TUG OF WAR)
st.subheader("📊 Dominant Narratives: Bull vs Bear")
narratives = data.get("dominant_narratives", [])

# Insert Scatter Chart before the list
if narratives:
    st.plotly_chart(create_narrative_scatter(narratives), use_container_width=True)

# Split Narratives
bullish_narratives = [n for n in narratives if "bull" in n.get("price_impact_direction", "").lower()]
bearish_narratives = [n for n in narratives if "bear" in n.get("price_impact_direction", "").lower()]
neutral_narratives = [n for n in narratives if "bull" not in n.get("price_impact_direction", "").lower() and "bear" not in n.get("price_impact_direction", "").lower()]

def format_supporting_data(supp_data):
    """Helper to convert raw JSON supporting data into readable markdown"""
    if not supp_data: return "_No specific data points._"
    
    md = ""
    for category, items in supp_data.items():
        if items:
             md += f"**{category.title()}:**\n"
             for item in items:
                 md += f"- {item}\n"
    return md

def render_narrative_card(n, color):
    """Renders a single narrative card"""
    # Determine class based on color
    card_class = "bull-card" if color == "#28a745" else "bear-card" if color == "#dc3545" else "neutral-card"
    
    st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
    with st.expander(f"{n.get('narrative_name')} ({n.get('narrative_type').upper()}) - Conf: {n.get('confidence_score')}"):
        st.markdown(f"**Impact:** <span style='color:{color};font-weight:bold'>{n.get('price_impact_direction', '').title()}</span>", unsafe_allow_html=True)
        st.markdown(f"**Horizon:** {n.get('expected_time_horizon', '').title()}")
        st.progress(n.get('momentum_score', 0.0), text=f"Momentum: {n.get('momentum_score')}")
        
        st.write("**Key Drivers:**")
        # Chips style for drivers (Black text on Grey)
        drivers_html = "".join([f"<span class='custom-chip'>{d}</span>" for d in n.get("key_drivers", [])])
        st.markdown(drivers_html, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown(f"_{n.get('reasoning_summary')}_")
        st.caption("🔍 Supporting Evidence")
        st.markdown(format_supporting_data(n.get("supporting_data", {})))
    st.markdown('</div>', unsafe_allow_html=True)

col_bull, col_bear = st.columns(2)

with col_bull:
    st.markdown("### 🐂 Bullish Narratives")
    if bullish_narratives:
        for n in bullish_narratives:
            render_narrative_card(n, "#28a745") # Green
    else:
        st.info("No significant bullish drivers detected.")

with col_bear:
    st.markdown("### 🐻 Bearish Narratives")
    if bearish_narratives:
        for n in bearish_narratives:
            render_narrative_card(n, "#dc3545") # Red
    else:
        st.success("No significant bearish risks detected.")
        
if neutral_narratives:
    st.markdown("### ⚖️ Neutral / Mixed Factors")
    for n in neutral_narratives:
        render_narrative_card(n, "#6c757d") # Grey

# 4. EMERGING NARRATIVES
st.subheader("🌱 Emerging Narratives")
emerging = data.get("emerging_narratives", [])

if emerging:
    for idx, e in enumerate(emerging):
        # Determine color-coded priority
        priority = e.get("monitoring_priority", "medium").lower()
        p_color = "red" if priority == "high" else "orange" if priority == "medium" else "green"
        
        with st.container():
            st.markdown(f"#### {idx+1}. {e.get('theme')}")
            c1, c2, c3 = st.columns([1,1,2])
            c1.markdown(f"**Confidence:** {e.get('confidence_score')}")
            c2.markdown(f"**Risk:** {e.get('risk_level').upper()}")
            c3.markdown(f"<span style='color:{p_color}; font-weight:bold'>Priority: {priority.upper()}</span>", unsafe_allow_html=True)
            
            st.info(f"**Why it matters:** {e.get('why_it_matters')}")
            
            with st.expander("Early Signals"):
                for s in e.get("early_signals", []):
                    st.markdown(f"- {s}")
        st.markdown("---")
else:
    st.info("No emerging narratives detected currently.")

# 5. PRICE CHART (Moved to Footer)
st.markdown("---")
st.subheader("📈 Live Silver Price Action (1 Month)")
price_hist = fetch_price_history()

if price_hist is not None and not price_hist.empty:
    # Create interactive line chart
    fig_price = px.line(
        price_hist, 
        y="Close", 
        title="Silver Futures (SI=F) - Daily Close",
        labels={"Close": "Price (USD)", "Date": "Date"}
    )
    fig_price.update_layout(height=350, showlegend=False)
    st.plotly_chart(fig_price, use_container_width=True)
else:
    st.warning("⚠️ Could not fetch live price data (yfinance connection failed).")

# ---------------- FOOTER ----------------
st.markdown("---")
# Placeholder for Maps if we ever get geospatial data back
# st.subheader("🌍 Global Narrative Spread (Placeholder)")
# st.caption("Geospatial data currently unavailable in this dataset.")


st.caption("⚠ Narrative Intelligence • Powered by n8n • Not Financial Advice")