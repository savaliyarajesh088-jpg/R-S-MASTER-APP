import streamlit as st
import yfinance as yf
import pandas as pd
import requests

# Page Configuration & Mobile Responsive Layout
st.set_page_config(
    page_title="R S MASTER APP",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Clean Mobile-Friendly CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .block-container { padding: 1rem; max-width: 700px; }
    .stMetric { background-color: #1f2937; padding: 10px; border-radius: 8px; }
    .signal-card {
        background-color: #1e2430;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #374151;
        margin-top: 10px;
        margin-bottom: 10px;
    }
    .badge-buy { background-color: #10B981; color: white; padding: 4px 10px; border-radius: 6px; font-weight: bold; }
    .badge-hold { background-color: #3B82F6; color: white; padding: 4px 10px; border-radius: 6px; font-weight: bold; }
    .badge-exit { background-color: #EF4444; color: white; padding: 4px 10px; border-radius: 6px; font-weight: bold; }
    .stButton>button { width: 100%; border-radius: 6px; height: 3em; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("📈 R S MASTER APP")
st.caption("સિગ્નલ, સ્વિંગ/લોંગ ટાર્ગેટ અને AI એનાલિસિસ")

# Session State
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ["RELIANCE.NS", "TATAMOTORS.NS", "TCS.NS", "INFY.NS", "RATNAVEER.NS"]

# --- INPUT SECTION ---
col1, col2 = st.columns([2, 1])
with col1:
    search_stock = st.text_input("સ્ટોક સિમ્બોલ લખો:", value="RATNAVEER.NS").upper().strip()
with col2:
    if st.button("➕ વોચલિસ્ટમાં ઉમેરો"):
        if search_stock and search_stock not in st.session_state.watchlist:
            st.session_state.watchlist.append(search_stock)
            st.success("ઉમેરાઈ ગયો!")

if search_stock:
    try:
        ticker = yf.Ticker(search_stock)
        df = ticker.history(period="1y")
        
        if df.empty:
            st.error("આ સિમ્બોલ માટે કોઈ ડેટા મળ્યો નથી.")
        else:
            current_price = float(df['Close'].iloc[-1])
            prev_close = float(df['Close'].iloc[-2])
            change = current_price - prev_close
            pct_change = (change / prev_close) * 100

            # Technical Indicators
            ema_20 = float(df['Close'].ewm(span=20, adjust=False).mean().iloc[-1])
            ema_50 = float(df['Close'].ewm(span=50, adjust=False).mean().iloc[-1])
            
            # Signal Logic
            if current_price > ema_20 and current_price > ema_50:
                signal = "BUY / ADD"
                badge = "badge-buy"
            elif current_price > ema_50:
                signal = "HOLD"
                badge = "badge-hold"
            else:
                signal = "EXIT / SELL"
                badge = "badge-exit"

            # Stop Loss & Targets
            stop_loss = round(ema_20 * 0.98, 2)
            
            # Swing Targets (Short-term)
            swing_t1 = round(current_price * 1.05, 2)
            swing_t2 = round(current_price * 1.08, 2)
            swing_t3 = round(current_price * 1.12, 2)

            # Long Term Targets
            long_t1 = round(current_price * 1.20, 2)
            long_t2 = round(current_price * 1.35, 2)
            long_t3 = round(current_price * 1.50, 2)

            # --- TOP SECTION: GEMINI AI STOCK ANALYSIS REPORT ---
            st.markdown("---")
            st.subheader("🤖 Gemini AI સ્ટોક એનાલિસિસ રિપોર્ટ")
            
            user_api_key = st.text_input("તમારી Gemini API Key અહીં નાખો:", type="password", key="ai_key")

            if st.button("🚀 AI પાસે રિપોર્ટ મંગાવો"):
                if not user_api_key:
                    st.error("મહેરબાની કરીને તમારી Gemini API Key નાખો.")
                else:
                    with st.spinner("AI એનાલિસિસ કરી રહ્યું છે..."):
                        try:
                            prompt_text = f"""
                            તમે એક એક્સપર્ટ સ્ટોક માર્કેટ એનાલિસ્ટ છો. નીચેના સ્ટોકનું ગુજરાતીમાં ટૂંકું અને સચોટ વિશ્લેષણ આપો:
                            સ્ટોક: {search_stock}
                            હાલનો ભાવ: ₹{current_price:.2f}
                            ટેકનિકલ સિગ્નલ: {signal}
                            
                            મુદ્દાઓ:
                            1. શોર્ટ-ટર્મ ટ્રેન્ડ કેવો છે?
                            2. ખરીદવો કે વેચવો?
                            3. મુખ્ય ધ્યાન રાખવા લાયક બાબત.
                            """
                            
                            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={user_api_key}"
                            payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
                            response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
                            res_json = response.json()

                            if response.status_code == 200 and 'candidates' in res_json:
                                st.success("એનાલિસિસ પૂર્ણ થયું!")
                                st.write(res_json['candidates'][0]['content']['parts'][0]['text'])
                            else:
                                err_msg = res_json.get('error', {}).get('message', 'અજ્ઞાત એરર')
                                st.error(f"એપીઆઈ એરર: {err_msg}")
                        except Exception as e:
                            st.error(f"કનેક્શન એરર: {e}")

            # --- PRICE & SIGNAL BOARD ---
            st.markdown("---")
            st.subheader("🎯 પ્રાઈસ અને સિગ્નલ બોર્ડ")
            
            st.markdown(f"""
            <div class="signal-card">
                <h3>{search_stock}</h3>
                <h2>₹{current_price:.2f} <span style="font-size:16px; color:{'#10B981' if change>=0 else '#EF4444'};">({change:+.2f} / {pct_change:+.2f}%)</span></h2>
                <hr style="border-color:#374151;">
                <p>📌 <b>સિગ્નલ:</b> <span class="{badge}">{signal}</span></p>
                <p>🛑 <b>સ્ટોપ લોસ (SL):</b> ₹{stop_loss}</p>
            </div>
            """, unsafe_allow_html=True)

            # --- SWING TARGETS ---
            st.markdown("#### ⚡ સ્વિંગ ટ્રેડ ટાર્ગેટ્સ (શોર્ટ ટર્મ)")
            col_s1, col_s2, col_s3 = st.columns(3)
            col_s1.metric("સ્વિંગ T1 (૫%)", f"₹{swing_t1}")
            col_s2.metric("સ્વિંગ T2 (૮%)", f"₹{swing_t2}")
            col_s3.metric("સ્વિંગ T3 (૧૨%)", f"₹{swing_t3}")

            # --- LONG TERM TARGETS ---
            st.markdown("#### 🏛️ લોંગ-ટર્મ ટાર્ગેટ્સ (લાંબો ગાળો)")
            col_l1, col_l2, col_l3 = st.columns(3)
            col_l1.metric("લોંગ T1 (૨૦%)", f"₹{long_t1}")
            col_l2.metric("લોંગ T2 (૩૫%)", f"₹{long_t2}")
            col_l3.metric("લોંગ T3 (૫૦%)", f"₹{long_t3}")

    except Exception as e:
        st.error(f"ડેટા લાવવામાં ભૂલ થઈ છે: {e}")

# --- WATCHLIST QUICK VIEW ---
st.markdown("---")
st.subheader("📋 વોચલિસ્ટ ભાવ")
wl_data = []
for sym in st.session_state.watchlist:
    try:
        t = yf.Ticker(sym)
        p = float(t.fast_info['lastPrice'])
        prev = float(t.fast_info['previousClose'])
        chg = p - prev
        pct = (chg / prev) * 100
        wl_data.append({"સ્ટોક": sym, "ભાવ (₹)": f"₹{p:.2f}", "ફેરફાર (%)": f"{pct:+.2f}%"})
    except:
        pass

if wl_data:
    st.dataframe(pd.DataFrame(wl_data), hide_index=True, use_container_width=True)
