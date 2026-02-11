import streamlit as st
import pandas as pd
import time
import pydeck as pdk
import yfinance as yf

# =========================================================
# ===================== BACKEND ===========================
# =========================================================

def backend_login(name, email):
    return email.endswith("@gmail.com")

def backend_get_narratives():
    return pd.DataFrame({
        "Agent": ["SN-01", "SN-02", "SN-03"],
        "Category": ["Industrial Demand", "Tech & EV Trends", "Jewellery"],
        "Coordination Score": [78, 66, 71]
    })

def backend_get_geo_world():
    return pd.DataFrame({
        "Country": ["India","USA","China","Germany","UK"],
        "lat": [20.6,37.1,35.8,51.1,55.3],
        "lon": [78.9,-95.7,104.1,10.4,-3.4],
        "Growth": ["Fast","Fast","Slow","Organic","Slow"],
        "Intensity": [90,80,65,45,55]
    })

def backend_get_geo_india():
    return pd.DataFrame({
        "Region":["Mumbai","Delhi","Ahmedabad","Chennai"],
        "lat":[19.07,28.61,23.02,13.08],
        "lon":[72.87,77.20,72.57,80.27],
        "Intensity":[85,75,65,55],
        "Growth":["Fast","Fast","Slow","Organic"]
    })

@st.cache_data(ttl=300)
def backend_get_market_data():
    ticker = yf.Ticker("SI=F")
    hist = ticker.history(period="7d", interval="30m")

    if hist.empty:
        return None

    latest = hist.iloc[-1]
    previous = hist.iloc[-2]

    price = round(latest["Close"], 2)
    change_pct = round(((price - previous["Close"]) / previous["Close"]) * 100, 2)
    trend = "Bullish 📈" if change_pct >= 0 else "Bearish 📉"

    return {
        "price": price,
        "change_pct": change_pct,
        "trend": trend,
        "history": hist[["Close"]].rename(columns={"Close":"Silver Price"})
    }

def backend_get_forecast():
    return pd.DataFrame({
        "Sentiment": ["Bullish 📈", "Bearish 📉"],
        "Probability": [72, 28]
    }).set_index("Sentiment")

# =========================================================
# ===================== FRONTEND ==========================
# =========================================================

st.set_page_config(
    page_title="Silver Narrative Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.profile-circle {
    background-color: #f0f2f6;
    color: #000;
    border-radius: 50%;
    width: 42px;
    height: 42px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    font-weight: bold;
    border: 1px solid #ccc;
}
</style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------------- LOGIN ----------------
if not st.session_state.logged_in:
    st.title("🔐 Login")

    name = st.text_input("Your Name")
    email = st.text_input("Gmail ID")

    if st.button("Login"):
        if backend_login(name, email):
            st.session_state.logged_in = True
            st.session_state.user_name = name
            st.experimental_rerun()
        else:
            st.error("Invalid Gmail ID")

    st.stop()

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("## 🧠 About")
    st.markdown("""
    Narrative-driven intelligence system analyzing
    global silver market stories and sentiment.
    """)
    st.caption("Hackathon Prototype")

# ---------------- HEADER ----------------
l, r = st.columns([8,1])
with l:
    st.title("🧠 Silver Market Narrative Intelligence")
with r:
    st.markdown(
        f"<div class='profile-circle'>{st.session_state.user_name[0]}</div>",
        unsafe_allow_html=True
    )

st.markdown("---")

# ---------------- DATA ----------------
narratives = backend_get_narratives()
geo_world = backend_get_geo_world()
india_regions = backend_get_geo_india()
market = backend_get_market_data()

# ---------------- KPIs ----------------
k1, k2, k3, k4 = st.columns(4)
k1.metric("🧠 Narratives", len(narratives))
k2.metric("🌍 Countries", len(geo_world))
k3.metric("📈 Trend", market["trend"])
k4.metric("⚡ Volatility", "High")

# ---------------- MARKET ----------------
st.subheader("📡 Live Silver Market Snapshot")

c1, c2, c3 = st.columns(3)
c1.metric("Silver Price", f"${market['price']}")
c2.metric("Change (%)", market["change_pct"])
c3.metric("Trend", market["trend"])

st.line_chart(market["history"])

# ---------------- NARRATIVES ----------------
st.markdown("---")
left, right = st.columns([2,1])

with left:
    st.subheader("📊 Narrative Agents")
    st.dataframe(narratives, use_container_width=True)

with right:
    st.subheader("📦 Narrative Categories")
    st.radio("Category", narratives["Category"].unique())

# ---------------- MAPS ----------------
color_map = {"Fast":[255,0,0],"Slow":[255,165,0],"Organic":[0,200,0]}
geo_world["color"] = geo_world["Growth"].map(color_map)
india_regions["color"] = india_regions["Growth"].map(color_map)

st.markdown("---")
st.subheader("🌍 Global → India Narrative Spread")

m1, m2 = st.columns([3,1])

with m1:
    st.pydeck_chart(pdk.Deck(
        layers=[pdk.Layer(
            "ScatterplotLayer",
            data=geo_world,
            get_position="[lon, lat]",
            get_radius="Intensity * 12000",
            get_fill_color="color",
            pickable=True
        )],
        initial_view_state=pdk.ViewState(latitude=25, longitude=10, zoom=1.2),
    ))

with m2:
    st.pydeck_chart(pdk.Deck(
        layers=[pdk.Layer(
            "ScatterplotLayer",
            data=india_regions,
            get_position="[lon, lat]",
            get_radius="Intensity * 2000",
            get_fill_color="color",
            pickable=True
        )],
        initial_view_state=pdk.ViewState(latitude=21, longitude=78, zoom=4),
    ))

# ---------------- FORECAST ----------------
st.markdown("---")
if st.button("🚀 Generate Market Sentiment Forecast"):
    with st.spinner("Analyzing narratives..."):
        time.sleep(1)
    st.bar_chart(backend_get_forecast())


st.caption("⚠ Narrative Intelligence • Demo System • Not Financial Advice")