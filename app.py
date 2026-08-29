import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
from datetime import datetime

# Page Configuration & Mobile Responsive Layout
st.set_page_config(
    page_title="R S MASTER APP - Pro Tracker",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Mobile-Friendly Custom CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 0.5rem;
        padding-right: 0.5rem;
    }
    .stMetric { background-color: #1f2937; padding: 10px; border-radius: 8px; }
    .exit-card {
        background-color: #1e2430;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #2d3748;
        margin-bottom: 15px;
    }
    .badge-add { background-color: #10B981; color: white; padding: 4px 10px; border-radius: 6px; font-weight: bold; }
    .badge-hold { background-color: #3B82F6; color: white; padding: 4px 10px; border-radius: 6px; font-weight: bold; }
    .badge-replace { background-color: #F59E0B; color: white; padding: 4px 10px; border-radius: 6px; font-weight: bold; }
    .badge-exit { background-color: #EF4444; color: white; padding: 4px 10px; border-radius: 6px; font-weight: bold; }
    .breakout-badge { background-color: #8B5CF6; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; }
    .stat-box {
        background-color: #111827;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #374151;
        margin-top: 10px;
        line-height: 1.8;
    }
    .stDataFrame, .stTable { width: 100% !important; overflow-x: auto; }
    .stButton>button { width: 100%; border-radius: 6px; height: 2.8em; }
    </style>
""", unsafe_allow_html=True)

st.title("📈 R S MASTER APP")
st.caption("સંપૂર્ણ ગુજરાતી એક્ઝિટમંત્રા, પોર્ટફોલિયો અને AI એનાલિસિસ ટ્રેકર")

# Session State Initializations
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = [
        "RELIANCE.NS", "TATAMOTORS.NS", "TCS.NS", "INFY.NS", 
        "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "RATNAVEER.NS"
    ]

if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}

if 'signal_history' not in st.session_state:
    st.session_state.signal_history = {}

# --- SECTION 1: WATCHLIST & PORTFOLIO CONTROL ---
with st.expander("⚙️ વોચલિસ્ટ અને પોર્ટફોલિયો કંટ્રોલ (ક્લિક કરો)", expanded=False):
    col_w, col_p = st.columns([1, 1])
    
    with col_w:
        st.subheader("📌 વોચલિસ્ટ મેનેજમેન્ટ")
        new_stock = st.text_input("નવો સ્ટોક ઉમેરો (દા.ત. WIPRO.NS):", key="add_wl_input")
        if st.button("➕ વોચલિસ્ટમાં ઉમેરો"):
            if new_stock and new_stock.upper().strip() not in st.session_state.watchlist:
                st.session_state.watchlist.append(new_stock.upper().strip())
                st.success(f"{new_stock.upper().strip()} ઉમેરાઈ ગયો!")
                st.rerun()

        if st.session_state.watchlist:
            stock_to_remove = st.selectbox("વોચલિસ્ટમાંથી હટાવો:", st.session_state.watchlist)
            if st.button("🗑️ વોચલિસ્ટ સ્ટોક ડીલીટ કરો"):
                st.session_state.watchlist.remove(stock_to_remove)
                st.warning(f"{stock_to_remove} ડીલીટ થયો!")
                st.rerun()

    with col_p:
        st.subheader("💼 પોર્ટફોલિયો મેનેજમેન્ટ (P&L)")
        port_symbol = st.text_input("સ્ટોક સિમ્બોલ (દા.ત. RELIANCE.NS):", key="port_sym").upper().strip()
        port_price = st.number_input("ખરીદ કિંમત (Buy Price ₹):", min_value=0.0, step=1.0)
        port_qty = st.number_input("શેરની સંખ્યા (Quantity):", min_value=1, step=1)

        if st.button("💼 પોર્ટફોલિયોમાં સેવ કરો"):
            if port_symbol and port_price > 0:
                st.session_state.portfolio[port_symbol] = {"buy_price": port_price, "qty": port_qty}
                st.success(f"{port_symbol} પોર્ટફોલિયોમાં ઉમેરાઈ ગયો!")
                st.rerun()

        if st.session_state.portfolio:
            port_remove = st.selectbox("પોર્ટફોલિયોમાંથી હટાવો:", list(st.session_state.portfolio.keys()))
            if st.button("🗑️ પોર્ટફોલિયો સ્ટોક ડીલીટ કરો"):
                del st.session_state.portfolio[port_remove]
                st.warning(f"{port_remove} ડીલીટ થયો!")
                st.rerun()

# --- SECTION 2: PORTFOLIO LIVE P&L TRACKER ---
if st.session_state.portfolio:
    st.subheader("💼 મારો પોર્ટફોલિયો - લાઈવ P&L")
    port_data = []
    total_invested = 0.0
    total_current = 0.0

    for sym, details in st.session_state.portfolio.items():
        try:
            t = yf.Ticker(sym)
            live_p = float(t.fast_info['lastPrice'])
            invested = details['buy_price'] * details['qty']
            current_val = live_p * details['qty']
            pnl_val = current_val - invested
            pnl_pct = (pnl_val / invested) * 100

            total_invested += invested
            total_current += current_val

            port_data.append({
                "સ્ટોક": sym,
                "ખરીદ ભાવ (₹)": f"₹{details['buy_price']:.2f}",
                "લાઈવ ભાવ (₹)": f"₹{live_p:.2f}",
                "જથ્થો": details['qty'],
                "કુલ રોકાણ (₹)": f"₹{invested:.2f}",
                "હાલનું મૂલ્ય (₹)": f"₹{current_val:.2f}",
                "P&L (₹)": f"{pnl_val:+.2f}",
                "P&L (%)": f"{pnl_pct:+.2f}%"
            })
        except Exception:
            pass

    if port_data:
        st.dataframe(pd.DataFrame(port_data), hide_index=True, use_container_width=True)
        total_pnl = total_current - total_invested
        total_pnl_pct = (total_pnl / total_invested) * 100 if total_invested > 0 else 0.0
        
        m1, m2, m3 = st.columns(3)
        m1.metric("📊 કુલ રોકાણ", f"₹{total_invested:.2f}")
        m2.metric("📈 હાલનું મૂલ્ય", f"₹{total_current:.2f}")
        m3.metric("💰 લાઈવ P&L", f"₹{total_pnl:.2f}", f"{total_pnl_pct:+.2f}%")

st.markdown("---")

# --- SECTION 3: WATCHLIST LIVE OVERVIEW ---
st.subheader("📋 વોચલિસ્ટ - લાઈવ ભાવ")
watchlist_data = []
for symbol in st.session_state.watchlist:
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.fast_info
        price = float(info['lastPrice'])
        prev_close = float(info['previousClose'])
        change = price - prev_close
        pct_change = (change / prev_close) * 100
        
        watchlist_data.append({
            "સ્ટોકનું નામ": symbol,
            "લાઈવ ભાવ (₹)": f"₹{price:.2f}",
            "ફેરફાર (₹)": f"{change:+.2f}",
            "ફેરફાર (%)": f"{pct_change:+.2f}%"
        })
    except Exception:
        pass

if watchlist_data:
    st.dataframe(pd.DataFrame(watchlist_data), hide_index=True, use_container_width=True)

st.markdown("---")

# --- SECTION 4: SEARCH & TECHNICAL ANALYSIS ---
st.subheader("🔍 સ્ટોક શોધો અને ટેકનિકલ એનાલિસિસ કરો")
search_stock = st.text_input("NSE સ્ટોક સિમ્બોલ લખો (દા.ત. ADANIENT.NS, RATNAVEER.NS):", value="RATNAVEER.NS")

if search_stock:
    selected_stock = search_stock.upper().strip()

    if selected_stock not in st.session_state.watchlist:
        if st.button(f"➕ {selected_stock} વોચલિસ્ટમાં ઉમેરો"):
            st.session_state.watchlist.append(selected_stock)
            st.success("વોચલિસ્ટમાં ઉમેરાઈ ગયો!")
            st.rerun()

    # Data Fetching
    df_daily = yf.download(selected_stock, period="1y", interval="1d", progress=False)
    df_weekly = yf.download(selected_stock, period="2y", interval="1wk", progress=False)
    df_monthly = yf.download(selected_stock, period="5y", interval="1mo", progress=False)

    def clean_df(data):
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        return data

    df = clean_df(df_daily)
    df_weekly = clean_df(df_weekly)
    df_monthly = clean_df(df_monthly)

    if not df.empty:
        # Technical Calculations
        df['EMA_10'] = df['Close'].ewm(span=10, adjust=False).mean()
        df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
        df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
        df['EMA_100'] = df['Close'].ewm(span=100, adjust=False).mean()
        df['EMA_200'] = df['Close'].ewm(span=200, adjust=False).mean()

        # CPR
        prev_high = float(df['High'].iloc[-2])
        prev_low = float(df['Low'].iloc[-2])
        prev_close = float(df['Close'].iloc[-2])
        pivot = (prev_high + prev_low + prev_close) / 3
        bc = (prev_high + prev_low) / 2
        tc = (pivot - bc) + pivot

        current_price = float(df['Close'].iloc[-1])
        high_20 = float(df['High'].iloc[-21:-1].max())
        high_52 = float(df['High'].max())
        vol_avg_20 = float(df['Volume'].iloc[-21:-1].mean())
        curr_vol = float(df['Volume'].iloc[-1])

        is_breakout_20d = current_price > high_20
        is_vol_breakout = curr_vol > vol_avg_20
        is_near_52w_high = (current_price / high_52) >= 0.90

        target_6pct = current_price * 1.06
        target_10pct = current_price * 1.10
        target_15pct = current_price * 1.15
        stop_loss = round(min(float(df['EMA_20'].iloc[-1]), current_price * 0.95), 2)

        # EXITMANTRA LOGIC
        pillar1_breakout = True if (is_breakout_20d or is_near_52w_high) else False
        pillar2_momentum = True if (current_price > float(df['EMA_50'].iloc[-1]) and is_vol_breakout) else False
        pillar3_exitprice = True if (current_price > stop_loss) else False

        score = sum([pillar1_breakout, pillar2_momentum, pillar3_exitprice])

        if score == 3:
            zone = "Bull Zone"
            signal = "ADD"
            badge_class = "badge-add"
            summary_txt = "અપગ્રેડ સિગ્નલ! ૩ માંથી ૩ સ્તંભ પાસ. સ્ટોક મજબૂત તેજીમાં છે."
        elif score == 2:
            zone = "Bull Zone"
            signal = "HOLD"
            badge_class = "badge-hold"
            summary_txt = "૩ માંથી ૨ સ્તંભ પાસ. સ્ટોક સારો છે, ખરીદેલો હોય તો જાળવી રાખો."
        elif score == 1:
            zone = "Pig Zone"
            signal = "REPLACE"
            badge_class = "badge-replace"
            summary_txt = "ડાઉનગ્રેડ ચેતવણી! મોમેન્ટમ નબળું પડ્યું છે. આને વેચી બીજો સારો સ્ટોક શોધો."
        else:
            zone = "Bear Zone"
            signal = "EXIT"
            badge_class = "badge-exit"
            summary_txt = "એક્ઝિટ સિગ્નલ! સ્ટોક મંદીમાં છે, નુકસાન અટકાવવા વેચી દો."

        # TRACKER HISTORY LOGIC
        today_str = datetime.now().strftime("%d/%m/%Y")
        if selected_stock not in st.session_state.signal_history:
            st.session_state.signal_history[selected_stock] = {
                "signal": signal, "signal_date": today_str, "signal_price": current_price,
                "zone": zone, "zone_date": today_str, "sl": stop_loss, "sl_date": today_str
            }
        else:
            hist_state = st.session_state.signal_history[selected_stock]
            if hist_state["signal"] != signal:
                hist_state["signal"] = signal
                hist_state["signal_date"] = today_str
                hist_state["signal_price"] = current_price
            if hist_state["zone"] != zone:
                hist_state["zone"] = zone
                hist_state["zone_date"] = today_str
            if hist_state["sl"] != stop_loss:
                hist_state["sl"] = stop_loss
                hist_state["sl_date"] = today_str

        stock_hist = st.session_state.signal_history[selected_stock]
        sig_price = stock_hist["signal_price"]
        diff_pct = ((current_price - sig_price) / sig_price) * 100
        
        try:
            d1 = datetime.strptime(stock_hist["signal_date"], "%d/%m/%Y")
            days_count = (datetime.now() - d1).days
        except Exception:
            days_count = 0

        # SECTION 5: EXITMANTRA & ADVANCED TRACKER CARD
        st.subheader("🎯 એક્ઝિટમંત્રા અને ટ્રેકર સિગ્નલ બોર્ડ")
        
        if is_breakout_20d and is_vol_breakout:
            st.success("🔥 **મજબૂત બ્રેકઆઉટ મળ્યો!** સારો વોલ્યુમ + ૨૦ દિવસનો હાઈ તોડ્યો.")

        st.markdown(f"""
        <div class="exit-card">
            <h2>{selected_stock.replace('.NS', '')} <span style="font-size:14px; color:#9CA3AF;">NSE</span>
                {'<span class="breakout-badge">🚀 BREAKOUT</span>' if is_breakout_20d else ''}
            </h2>
            <h3>હાજર ભાવ: ₹{current_price:.2f}</h3>
            
            <div class="stat-box">
                <p>🟢 <b>ZONE:</b> {zone} | <span style="color:#9CA3AF;">Changed Since: {stock_hist['zone_date']}</span></p>
                <p>🛡️ <b>EXIT PRICE (STOP LOSS):</b> ₹{stop_loss:.2f} | <span style="color:#9CA3AF;">Changed Since: {stock_hist['sl_date']}</span></p>
                <p>🎯 <b>RATING:</b> SCORE {score} - <span class="{badge_class}">{signal}</span> | <span style="color:#9CA3AF;">Changed Since: {stock_hist['signal_date']} @ ₹{sig_price:.2f}</span></p>
                <p>📈 <b>OUTCOME (DIFFERENCE):</b> <span style="color:{'#10B981' if diff_pct>=0 else '#EF4444'}; font-weight:bold;">{diff_pct:+.2f}%</span> ({days_count} DAYS) | <span style="color:#9CA3AF;">Changed Since: {stock_hist['signal_date']}</span></p>
            </div>
            
            <p style="margin-top:10px;"><i>💡 {summary_txt}</i></p>
            <hr style="border-color:#374151;">
            <p>{'✅' if pillar1_breakout else '❌'} <b>૧. ટ્રેન્ડ અને બ્રેકઆઉટ:</b> {'હા' if pillar1_breakout else 'ના'}</p>
            <p>{'✅' if pillar2_momentum else '❌'} <b>૨. વોલ્યુમ અને મોમેન્ટમ:</b> {'હા' if pillar2_momentum else 'ના'}</p>
            <p>{'✅' if pillar3_exitprice else '❌'} <b>૩. ટેકનિકલ સપોર્ટ:</b> {'હા' if pillar3_exitprice else 'ના'}</p>
        </div>
        """, unsafe_allow_html=True)

        # SECTION 6: SWING TARGETS & DWM TREND
        st.markdown("---")
        st.subheader("🎯 સ્વિંગ ટ્રેડ ટાર્ગેટ (૬% થી ૧૫%)")
        c1, c2 = st.columns(2)
        c1.metric("🛑 મૂળ સ્ટોપ લોસ (SL)", f"₹{stop_loss:.2f}")
        c2.metric("🎯 ટાર્ગેટ ૧ (૬%)", f"₹{target_6pct:.2f}")
        
        c3, c4 = st.columns(2)
        c3.metric("🎯 ટાર્ગેટ ૨ (૧૦%)", f"₹{target_10pct:.2f}")
        c4.metric("🚀 ટાર્ગેટ ૩ (૧૫%)", f"₹{target_15pct:.2f}")

        st.markdown("---")
        st.subheader("🗓️ DWM (ડેઇલી, વીકલી, મંથલી) ટ્રેન્ડ સ્ટેટસ")
        d_col, w_col, m_col = st.columns(3)

        d_trend = "તેજી 🟢" if current_price > float(df['EMA_50'].iloc[-1]) else "મંદી 🔴"
        w_trend = "તેજી 🟢" if float(df_weekly['Close'].iloc[-1]) > float(df_weekly['Close'].iloc[-4]) else "મંદી 🔴"
        m_trend = "તેજી 🟢" if float(df_monthly['Close'].iloc[-1]) > float(df_monthly['Close'].iloc[-2]) else "મંદી 🔴"

        d_col.metric("📅 ડેઇલી ટ્રેન્ડ", d_trend)
        w_col.metric("🗓️ વીકલી ટ્રેન્ડ", w_trend)
        m_col.metric("📊 મંથલી ટ્રેન્ડ", m_trend)

        # SECTION 7: EMA & CPR INDICATORS
        st.markdown("---")
        st.subheader("📊 ટેકનિકલ ઈન્ડિકેટર્સ (EMA) અને CPR")
        
        ema_data = pd.DataFrame({
            "Moving Average": ["EMA 10", "EMA 20", "EMA 50", "EMA 100", "EMA 200"],
            "કિંમત (₹)": [
                f"₹{df['EMA_10'].iloc[-1]:.2f}",
                f"₹{df['EMA_20'].iloc[-1]:.2f}",
                f"₹{df['EMA_50'].iloc[-1]:.2f}",
                f"₹{df['EMA_100'].iloc[-1]:.2f}",
                f"₹{df['EMA_200'].iloc[-1]:.2f}"
            ]
        })
        st.dataframe(ema_data, hide_index=True, use_container_width=True)

        st.markdown("#### 🎯 દૈનિક CPR (Central Pivot Range)")
        cpr_data = pd.DataFrame({
            "CPR લેવલ": ["Top Central (TC)", "Pivot Point (P)", "Bottom Central (BC)"],
            "કિંમત (₹)": [f"₹{max(tc, bc):.2f}", f"₹{pivot:.2f}", f"₹{min(tc, bc):.2f}"]
        })
        st.dataframe(cpr_data, hide_index=True, use_container_width=True)

        # SECTION 8: PRICE CHART
        st.markdown("---")
        st.subheader("📉 પ્રાઈસ ચાર્ટ અને EMA લાઈનો")
        st.line_chart(df[['Close', 'EMA_10', 'EMA_20', 'EMA_50', 'EMA_100', 'EMA_200']])

        # SECTION 9: GEMINI AI STOCK ANALYSIS REPORT (From your old code)
        st.markdown("---")
        st.subheader("🤖 Gemini AI સ્ટોક એનાલિસિસ રિપોર્ટ")
        
        api_key = st.secrets.get("GEMINI_API_KEY", "")
        if not api_key:
            api_key = st.text_input("તમારી Gemini API Key નાખો:", type="password", key="gemini_key_input")

        if st.button("🤖 Gemini AI પાસે રિપોર્ટ મંગાવો"):
            if not api_key:
                st.error("મહેરબાની કરીને સાચી Gemini API Key પ્રદાન કરો.")
            else:
                with st.spinner("AI એનાલિસિસ કરી રહ્યું છે..."):
                    try:
                        ticker_obj = yf.Ticker(selected_stock)
                        info = ticker_obj.info
                        company_name = info.get('longName', selected_stock)
                        high_1m = float(df['High'].max())
                        low_1m = float(df['Low'].min())

                        prompt_text = f"""
                        તમે એક એક્સપર્ટ સ્ટોક માર્કેટ એનાલિસ્ટ છો.
                        નીચે આપેલા સ્ટોક ડેટાનું વિશ્લેષણ કરો અને ગુજરાતી ભાષામાં વિગતવાર રિપોર્ટ આપો:

                        સ્ટોકનું નામ: {company_name} ({selected_stock})
                        હાલનો ભાવ (Current Price): ₹{current_price:.2f}
                        છેલ્લા ૧ મહિનાનો હાઈ (1 Month High): ₹{high_1m:.2f}
                        છેલ્લા ૧ મહિનાનો લો (1 Month Low): ₹{low_1m:.2f}
                        ટેકનિકલ સ્કોર (Exitmantra Score): {score}/3 ({signal})

                        મહેરબાની કરીને નીચે મુજબ જવાબો આપો:
                        1. સ્ટોકનું સામાન્ય વિશ્લેષણ (General Analysis)
                        2. હાલના ભાવ અને ટ્રેન્ડ પ્રમાણે શોર્ટ ટર્મ દ્રષ્ટિકોણ (Short-term Outlook)
                        3. રોકાણકારો માટે મહત્વની ટિપ્સ અને રિસ્ક ફેક્ટર્સ
                        """

                        models_to_try = ["gemini-3.6-flash", "gemini-1.5-flash-latest"]
                        success = False

                        for model_name in models_to_try:
                            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
                            payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
                            headers = {'Content-Type': 'application/json'}
                            
                            response = requests.post(url, json=payload, headers=headers)
                            res_json = response.json()

                            if response.status_code == 200 and 'candidates' in res_json:
                                analysis_text = res_json['candidates'][0]['content']['parts'][0]['text']
                                st.success("એનાલિસિસ સફળતાપૂર્વક પૂર્ણ થયું!")
                                st.write(analysis_text)
                                success = True
                                break

                        if not success:
                            st.error("સર્વર પર અત્યારે વધુ ટ્રાફિક છે. થોડી સેકન્ડ પછી ફરી પ્રયાસ કરો.")
                    except Exception as e:
                        st.error(f"એરર આવી છે: {str(e)}")

st.markdown("---")
st.caption("Powered by R S MASTER APP | સંપૂર્ણ ગુજરાતી પોર્ટફોલિયો અને AI એનાલિસિસ ટ્રેકર")
