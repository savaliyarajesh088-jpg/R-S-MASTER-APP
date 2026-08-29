import streamlit as st
import pandas as pd

# ૧. પેજ સેટઅપ (મોબાઈલ લેઆઉટ માટે સપોર્ટ)
st.set_page_config(
    page_title="R S MASTER APP",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ૨. મોબાઈલ રેસ્પmapન્સિવ CSS Customization
st.markdown("""
    <style>
    /* મોબાઈલ માટે પેડિંગ ઓછું કરવું */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 0.5rem;
        padding-right: 0.5rem;
    }
    
    /* કાર્ડ ડિઝાઇન */
    .stat-card {
        background-color: #1F2937;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 10px;
        border: 1px solid #374151;
    }
    
    /* ટેબલ રેસ્પોન્સિવ બનાવવું */
    .stDataFrame, .stTable {
        width: 100% !important;
        overflow-x: auto;
    }
    
    /* બટન્સ મોબાઈલમાં ફુલ-વિડ્થ કરવા */
    .stButton>button {
        width: 100%;
        border-radius: 6px;
        height: 3em;
    }
    </style>
""", unsafe_allow_html=True)

# 📌 હેડર
st.title("📈 R S MASTER APP")
st.caption("એક્ઝિટમંત્રા અને એડવાન્સ્ડ ટ્રેકર")

# ⚙️ વોચલિસ્ટ અને પોર્ટફોલિયો કંટ્રોલ (ક્રોસ એકોર્ડિયન / Collapsible)
with st.expander("⚙️ વોચલિસ્ટ અને પોર્ટફોલિયો કંટ્રોલ", expanded=False):
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("📌 વોચલિસ્ટ")
        new_stock = st.text_input("નવો સ્ટોક ઉમેરો (દા.ત. WIPRO.NS):")
        remove_stock = st.selectbox("હટાવવા માટે પસંદ કરો:", ["કંઈ નહીં", "RELIANCE.NS", "TCS.NS"])
    
    with col2:
        st.subheader("💼 પોર્ટફોલિયો (P&L)")
        portfolio_stock = st.text_input("સ્ટોક સિમ્બોલ:")
        buy_price = st.number_input("ખરીદ કિંમત (₹):", min_value=0.0)
        quantity = st.number_input("શેરની સંખ્યા:", min_value=1)

# 📋 વોચલિસ્ટ લાઈવ ભાવ
st.subheader("📋 વોચલિસ્ટ - લાઈવ ભાવ")
watchlist_data = pd.DataFrame({
    'સ્ટોક': ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'SBIN.NS', 'BHARTIARTL.NS'],
    'લાઈવ ભાવ (₹)': [1287.00, 2342.00, 1144.00, 720.30, 1422.80, 1047.50, 1882.40],
    'ફેરફાર (₹)': [4.80, 93.60, 33.20, 9.30, -20.20, 4.60, 4.10],
    'ફેરફાર (%)': ['+0.37%', '+4.16%', '+2.99%', '+1.31%', '-1.40%', '+0.44%', '+0.22%']
})
st.dataframe(watchlist_data, hide_index=True, use_container_width=True)

# 🔍 સ્ટોક સર્ચ
st.subheader("🔍 સ્ટોક એનાલિસિસ")
search_stock = st.text_input("NSE સ્ટોક સિમ્બોલ લખો:", value="RELIANCE.NS")

# 🎯 સિગ્નલ બોર્ડ (UI/UX માળખું)
st.markdown(f"### 🎯 {search_stock} સિગ્નલ બોર્ડ")
st.markdown("#### હાજર ભાવ: **₹1287.00**")

st.markdown("""
<div class="stat-card">
    <p>🟢 <b>ZONE:</b> Pig Zone | <span style="color:#9CA3AF;">29/08/2026</span></p>
    <p>🛡️ <b>EXIT PRICE:</b> ₹1222.65</p>
    <p>🎯 <b>RATING:</b> SCORE 1 - <span style="background-color:#EF4444; padding:2px 6px; border-radius:4px; color:white;">REPLACE</span></p>
    <p>📈 <b>OUTCOME:</b> <span style="color:#10B981; font-weight:bold;">+0.00%</span> (0 DAYS)</p>
</div>
<p style="color:#F59E0B;">💡 <b>ડાઉનગ્રેડ ચેતવણી!</b> મોમેન્ટમ નબળું પડ્યું છે. આને વેચી બીજો સારો સ્ટોક શોધો.</p>
""", unsafe_allow_html=True)

# 📊 રિસ્પોન્સિવ ટેબ્સ (મોબાઈલ માટે ઉત્તમ)
tab1, tab2, tab3 = st.tabs(["🎯 ટાર્ગેટ અને ટ્રેન્ડ", "📊 EMA & CPR", "📉 ચાર્ટ્સ"])

with tab1:
    st.markdown("#### 🎯 સ્વિંગ ટ્રેડ ટાર્ગેટ")
    target_df = pd.DataFrame({
        "લેવલ": ["🛑 મૂળ SL", "🎯 ટાર્ગેટ ૧ (૬%)", "🎯 ટાર્ગેટ ૨ (૧૦%)", "🚀 ટાર્ગેટ ૩ (૧૫%)"],
        "કિંમત (₹)": [1222.65, 1364.22, 1415.70, 1480.05]
    })
    st.table(target_df)

    st.markdown("#### 🗓️ DWM ટ્રેન્ડ સ્ટેટસ")
    trend_col1, trend_col2, trend_col3 = st.columns(3)
    trend_col1.metric("ડેઇલી", "Bearish 🔴")
    trend_col2.metric("વીકલી", "Bearish 🔴")
    trend_col3.metric("મંથલી", "Bearish 🔴")

with tab2:
    st.markdown("#### 📊 ટેકનિકલ ઈન્ડિકેટર્સ (EMA)")
    ema_df = pd.DataFrame({
        "Indicator": ["EMA 10", "EMA 20", "EMA 50", "EMA 100", "EMA 200"],
        "Value (₹)": [1302.71, 1305.77, 1309.72, 1327.59, 1355.95]
    })
    st.dataframe(ema_df, hide_index=True, use_container_width=True)

    st.markdown("#### 🎯 દૈનિક CPR")
    cpr_df = pd.DataFrame({
        "CPR Level": ["Top Central (TC)", "Pivot Point (P)", "Bottom Central (BC)"],
        "Price (₹)": [1295.30, 1290.93, 1286.57]
    })
    st.dataframe(cpr_df, hide_index=True, use_container_width=True)

with tab3:
    st.info("📉 ચાર્ટ્સ માટે `plotly` નો ઉપયોગ કરવાથી મોબાઈલમાં ચાર્ટ ઝૂમ અને ટચ-ફ્રેન્ડલી બનશે.")
    # Plotly ચાર્ટ માટેનો કોડ અહીં ઉમેરી શકાય છે.
