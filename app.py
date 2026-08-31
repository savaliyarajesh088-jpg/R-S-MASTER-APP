import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from deep_translator import GoogleTranslator

# Page Configuration & Professional Styling
st.set_page_config(page_title="આર એસ માસ્ટર એપ - પ્રો અલ્ટીમેટ ટ્રેડિંગ ડેશબોર્ડ", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; border: 1px solid #374151; }
    .stMetric label { color: #9ca3af !important; }
    .stMetric div { color: #ffffff !important; }
    .stTextArea textarea { color: #ffffff !important; background-color: #111827 !important; }
    </style>
""", unsafe_allow_html=True)

# App Title & Headers in Gujarati with Emojis
st.title("🚀 આર એસ માસ્ટર એપ - પ્રો અલ્ટીમેટ ટ્રેડિંગ & ગ્રોથ ડેશબોર્ડ 📈💎")
st.markdown("---")

# Initialize Session States (Only once so refresh doesn't overwrite user additions/deletions)
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = [
        "DYCL.NS", "TATASTEEL.NS", "RELIANCE.NS", "INFY.NS", "TCS.NS", 
        "SBIN.NS", "HDFCBANK.NS", "ITC.NS", "ZOMATO.NS", "TATAMOTORS.NS"
    ]

if 'portfolio' not in st.session_state:
    st.session_state.portfolio = pd.DataFrame(columns=["Stock", "Qty", "Buy Price"])

# Sidebar Navigation / Settings with Emojis
st.sidebar.header("⚙️ સેટિંગ્સ અને વોચલિસ્ટ મેનેજમેન્ટ 🛠️")

# 1. Add New Stock Section
st.sidebar.subheader("➕ નવો સ્ટોક ઉમેરો 📥")
new_stock_input = st.sidebar.text_input("સ્ટોક સિમ્બોલ લખો (દા.ત. DYCL.NS): 📝", key="new_stock_txt")

if st.sidebar.button("✨ વોચલિસ્ટમાં ઉમેરો"):
    if new_stock_input:
        cleaned_symbol = new_stock_input.strip().upper()
        if cleaned_symbol not in st.session_state.watchlist:
            st.session_state.watchlist.append(cleaned_symbol)
            st.sidebar.success(f"✅ {cleaned_symbol} સફળતાપૂર્વક ઉમેરાઈ ગયો! 🎉")
            st.rerun()
        else:
            st.sidebar.warning("⚠️ આ સ્ટોક પહેલેથી જ લિસ્ટમાં છે.")
    else:
        st.sidebar.error("❌ કૃપા કરીને સાચો સિમ્બોલ લખો.")

st.sidebar.markdown("---")

# 2. Remove Stock Section
st.sidebar.subheader("🗑️ સ્ટોક દૂર કરો ❌")
if len(st.session_state.watchlist) > 0:
    stock_to_remove = st.sidebar.selectbox("દૂર કરવા માટે સ્ટોક પસંદ કરો: 📋", st.session_state.watchlist, key="remove_box")
    if st.sidebar.button("🔥 પસંદ કરેલ સ્ટોક દૂર કરો"):
        if stock_to_remove in st.session_state.watchlist:
            st.session_state.watchlist.remove(stock_to_remove)
            st.sidebar.success(f"🗑️ {stock_to_remove} સફળતાપૂર્વક દૂર થઈ ગયો!")
            st.rerun()

st.sidebar.markdown("---")

# Main Navigation Tabs with Emojis
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 સિંગલ સ્ટોક ડીપ એનાલિસિસ & સ્વિંગ પ્લાન", 
    "🔍 લાઈવ માર્કેટ સ્કેનર & બાય/હોલ્ડ સિગ્નલ", 
    "📋 વોચલિસ્ટ કમ્પેરિઝન", 
    "💼 મારો પોર્ટફોલિયો ટ્રેકર"
])

with tab1:
    st.subheader("🎯 પ્રોફેશનલ ટ્રેડિંગ એનાલિસિસ, ડ્યુઅલ સપોર્ટ (સ્વિંગ & મેજર) & ટાર્ગેટ 📉")
    
    selected_stock = st.selectbox("વિશ્લેષણ માટે સ્ટોક પસંદ કરો: 🔍", st.session_state.watchlist, key="analysis_box")
    
    if st.button("🚀 પ્રોફેશનલ એનાલિસિસ અને સપોર્ટ પ્લાન રન કરો"):
        if not selected_stock:
            st.error("❌ મહેરબાની કરીને સ્ટોક પસંદ કરો.")
        else:
            with st.spinner(f"⏳ {selected_stock} નો પ્રોફેશનલ ડેટા ફેચ થઈ રહ્યો છે... 🔄"):
                try:
                    ticker = yf.Ticker(selected_stock)
                    hist = ticker.history(period="1y")
                    info = ticker.info

                    if hist.empty or hist['Close'].dropna().empty:
                        st.error("❌ આ સિમ્બોલ માટે કોઈ ડેટા મળ્યો નથી.")
                    else:
                        close_series = hist['Close'].dropna()
                        current_price = close_series.iloc[-1]
                        high_52 = hist['High'].max()
                        company_name = info.get('longName', selected_stock)
                        pe_ratio = info.get('trailingPE', 'N/A')
                        roe = info.get('returnOnEquity', 'N/A')
                        roe_str = f"{roe * 100:.2f}%" if isinstance(roe, float) else 'N/A'
                        
                        # FUNDAMENTAL CAGR TARGETS (3-5 YEARS)
                        eps_growth = info.get('earningsGrowth', None)
                        base_growth = eps_growth if eps_growth and isinstance(eps_growth, float) else 0.15
                        annual_growth = min(max(base_growth, 0.08), 0.25)
                        
                        target_3yr = current_price * ((1 + annual_growth) ** 3)
                        target_5yr = current_price * ((1 + annual_growth) ** 5)

                        # COMPANY BUSINESS SUMMARY (TRANSLATED TO GUJARATI)
                        raw_summary = info.get('longBusinessSummary', 'આ કંપની વિશેની વિગતવાર માહિતી ઉપલબ્ધ નથી.')
                        try:
                            business_summary = GoogleTranslator(source='auto', target='gu').translate(raw_summary)
                        except:
                            business_summary = raw_summary

                        # MULTI-EMA (9, 20, 50, 200)
                        ema_9 = close_series.ewm(span=9, adjust=False).mean().iloc[-1]
                        ema_20 = close_series.ewm(span=20, adjust=False).mean().iloc[-1]
                        ema_50 = close_series.ewm(span=50, adjust=False).mean().iloc[-1]
                        ema_200 = close_series.ewm(span=200, adjust=False).mean().iloc[-1] if len(close_series) >= 200 else current_price

                        ema_9_series = close_series.ewm(span=9, adjust=False).mean()
                        ema_20_series = close_series.ewm(span=20, adjust=False).mean()
                        ema_cross_status = "🟢 9/20 EMA બુલિશ ક્રોસઓવર ✅" if ema_9_series.iloc[-1] > ema_20_series.iloc[-1] else "🔴 9/20 EMA બેરિશ ક્રોસઓવર ❌"

                        # RSI
                        delta = close_series.diff()
                        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                        rs = gain / loss
                        rsi_series = 100 - (100 / (1 + rs))
                        current_rsi = rsi_series.iloc[-1] if not rsi_series.empty else 50.0

                        # MACD Calculation
                        exp1 = close_series.ewm(span=12, adjust=False).mean()
                        exp2 = close_series.ewm(span=26, adjust=False).mean()
                        macd_line = exp1 - exp2
                        signal_line = macd_line.ewm(span=9, adjust=False).mean()
                        current_macd = macd_line.iloc[-1]
                        current_sig = signal_line.iloc[-1]
                        macd_status = "🟢 MACD બુલિશ મોમેન્ટમ 🚀" if current_macd > current_sig else "🔴 MACD બેરિશ મોમેન્ટમ ⚠️"

                        # CPR Calculation
                        recent_h = hist['High'].iloc[-2]
                        recent_l = hist['Low'].iloc[-2]
                        recent_c = hist['Close'].iloc[-2]
                        pivot = (recent_h + recent_l + recent_c) / 3
                        bc = (recent_h + recent_l) / 2
                        tc = (2 * pivot) - bc
                        cpr_width = abs(tc - bc)
                        cpr_status = "સાંકડું CPR (મોટા બ્રેકઆઉટની શક્યતા) ⚡" if cpr_width < (current_price * 0.005) else "પહોળું CPR (સાઇડવેઝ માર્કેટ) ⚖️"

                        # Volume & Fake Breakout Trap Check
                        vol_series = hist['Volume'].dropna()
                        today_vol = vol_series.iloc[-1] if not vol_series.empty else 0
                        avg_vol = vol_series.rolling(20).mean().iloc[-1] if len(vol_series) >= 20 else today_vol
                        has_volume_spike = today_vol > (1.3 * avg_vol)
                        
                        # Resistance (Last 60 sessions)
                        recent_hist = hist.tail(60)
                        dynamic_resistance = recent_hist['High'].max()

                        # --- DUAL SUPPORT LOGIC (SWING vs MAJOR) ---
                        swing_hist = hist.tail(15)
                        swing_support = swing_hist['Low'].min()
                        major_support = hist['Low'].min()

                        is_near_resistance = current_price >= (dynamic_resistance * 0.98)
                        is_fake_breakout = is_near_resistance and not has_volume_spike
                        
                        if is_fake_breakout:
                            trap_status = "⚠️ ચેતવણી: ફેક બ્રેકઆઉટ / ઓપરેટર ટ્રેપ! 🛑"
                        elif has_volume_spike:
                            trap_status = "🔥 જેન્યુઈન વોલ્યુમ બ્રેકઆઉટ કન્ફર્મેશન! ✅"
                        else:
                            trap_status = "⚪ સામાન્ય પ્રાઇસ એક્શન ઝોન 💤"

                        is_near_support = current_price <= (swing_support * 1.03)
                        pullback_status = "🟢 સ્વિંગ સપોર્ટ ઝોન પર પુલબેક (Buy on Dip તક) 🎯" if is_near_support else "⚪ નોર્મલ રેન્જ ⚖️"

                        # Risk-to-Reward Setup (1:3) using Swing Support
                        stop_loss = swing_support * 0.99
                        risk = current_price - stop_loss
                        target_swing_1 = current_price + (risk * 2.0)
                        target_swing_2 = current_price + (risk * 3.0)
                        rr_ratio = 3.0 if risk > 0 else 0

                        is_valid_setup = (has_volume_spike or is_near_support) and not is_fake_breakout and (current_rsi > 45)

                        # Scoring System
                        score = 30
                        if current_price > ema_200: score += 15
                        if current_price > ema_50: score += 15
                        if ema_9 > ema_20: score += 15
                        if 40 <= current_rsi <= 70: score += 10
                        if current_macd > current_sig: score += 10
                        if has_volume_spike and not is_fake_breakout: score += 15
                        score = max(0, min(100, score))

                        if score >= 70 and not is_fake_breakout:
                            verdict = "🔥 સ્ટ્રોંગ બાય / હોલ્ડ (હાઇ ગ્રોથ સેટઅપ) 🚀"
                        elif score >= 50:
                            verdict = "⚖️ સાઇડવેઝ / વેઇટ એન્ડ વોચ (તટસ્થ) ⏳"
                        else:
                            verdict = "🔻 વેચાણ દબાણ / અવોઈડ કરો ⚠️"

                        # Display UI Metrics
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("💵 હાલનો ભાવ", f"₹{current_price:.2f}")
                        col2.metric("⭐ પ્રો ટેક્નિકલ સ્કોર", f"{score} / 100")
                        col3.metric("📈 આરએસઆઈ (RSI 14)", f"{current_rsi:.2f}")
                        col4.metric("🏆 ૫૨ સપ્તાહ હાઈ", f"₹{high_52:.2f}")

                        st.markdown("---")

                        # Company Profile Section
                        st.subheader(f"🏢 કંપની વિશે માહિતી (Company Profile): {company_name}")
                        st.write(business_summary)

                        st.markdown("---")

                        # Candlestick Chart with Both Supports
                        st.subheader(f"📊 {company_name} - કેન્ડલસ્ટિક ચાર્ટ વિથ ડ્યુઅલ સપોર્ટ & રેઝિસ્ટન્સ 📈")
                        fig = go.Figure(data=[go.Candlestick(
                            x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'], name='Candlestick'
                        )])
                        fig.add_hline(y=dynamic_resistance, line_dash="dash", line_color="red", annotation_text=f"🔴 રેઝિસ્ટન્સ: ₹{dynamic_resistance:.2f}", annotation_position="top right")
                        fig.add_hline(y=swing_support, line_dash="dash", line_color="orange", annotation_text=f"🟠 સ્વિંગ સપોર્ટ (ટ્રેડિંગ): ₹{swing_support:.2f}", annotation_position="bottom right")
                        fig.add_hline(y=major_support, line_dash="dash", line_color="green", annotation_text=f"🟢 મેજર બેઝ સપોર્ટ (ઇન્વેસ્ટમેન્ટ): ₹{major_support:.2f}", annotation_position="bottom left")
                        
                        fig.update_layout(template='plotly_dark', title=f"{selected_stock} - Dual Support & Price Action", xaxis_title="તારીખ", yaxis_title="ભાવ (₹)", height=500)
                        st.plotly_chart(fig, use_container_width=True)

                        st.markdown("---")
                        st.subheader(f"🎯 પ્રોફેશનલ ટ્રેડર ઇન્ડિકેટર & સપોર્ટ સ્ટેટસ: {company_name}")
                        st.info(f"**ઓવરઓલ સિગ્નલ:** {verdict} | **ટ્રેપ ચેક:** {trap_status} | **પુલબેક:** {pullback_status}")

                        sc1, sc2, sc3, sc4 = st.columns(4)
                        sc1.write(f"**⚡ 9/20 EMA Cross:** {ema_cross_status}")
                        sc2.write(f"**🔄 MACD Status:** {macd_status}")
                        sc3.write(f"**📐 CPR Width:** {cpr_status}")
                        sc4.write(f"🛡️ **P/E / ROE:** {pe_ratio} / {roe_str}")

                        # Dual Support Info Box
                        st.markdown("---")
                        st.subheader("📌 સપોર્ટ લેવલ માર્ગદર્શિકા (Swing vs Major Support)")
                        sup_c1, sup_c2 = st.columns(2)
                        sup_c1.metric("🟠 સ્વિંગ ટ્રેડ સપોર્ટ (નજીકનો Stop-Loss)", f"₹{swing_support:.2f}", "શોર્ટ-ટર્મ ટ્રેડિંગ માટે")
                        sup_c2.metric("🟢 મેજર બેઝ સપોર્ટ (લોંગ-ટર્મ Base)", f"₹{major_support:.2f}", "લાંબા ગાળાના રોકાણ માટે")

                        # Swing Trading Plan & Risk Management
                        st.markdown("---")
                        st.subheader("🛡️ સ્વિંગ ટ્રેડિંગ રિસ્ક મેનેજમેન્ટ & 1:3 ટાર્ગેટ પ્લાન 🎯")
                        
                        if is_valid_setup:
                            st.success("✅ **પરફેક્ટ સ્વિંગ ટ્રેડ સેટઅપ મળ્યું છે!**")
                            t_col1, t_col2, t_col3, t_col4 = st.columns(4)
                            t_col1.metric("🛑 સ્ટોપ-લોસ (SL)", f"₹{stop_loss:.2f}", "સ્વિંગ સપોર્ટ નીચે")
                            t_col2.metric("🎯 ટાર્ગેટ ૧ (1:2)", f"₹{target_swing_1:.2f}", "પ્રોફિટ બુકિંગ")
                            t_col3.metric("🚀 ટાર્ગેટ ૨ (1:3)", f"₹{target_swing_2:.2f}", "મેક્સિમમ રિવોર્ડ")
                            t_col4.metric("⚖️ રિસ્ક-ટુ-રિવોર્ડ", f"1 : {rr_ratio}")
                        else:
                            st.warning("⚠️ **બ્લાઇન્ડ બાઇંગ વોર્નિંગ:** હાલમાં સેટઅપ ક્લિયર નથી અથવા ઓપરેટર ટ્રેપ ઝોન છે.")

                        st.markdown("##### **📈 લોંગ-ટર્મ ગ્રોથ લક્ષ્યાંક (CAGR બેઝ્ડ ૩ થી ૫ વર્ષ):**")
                        inv_col1, inv_col2, inv_col3 = st.columns(3)
                        inv_col1.metric("📊 અંદાજિત વાર્ષિક ગ્રોથ", f"{annual_growth*100:.1f}% પ્રતિ વર્ષ")
                        inv_col2.metric("🎯 ૩ વર્ષનું લક્ષ્ય", f"₹{target_3yr:.2f}")
                        inv_col3.metric("🚀 ૫ વર્ષનું લક્ષ્ય", f"₹{target_5yr:.2f}")

                except Exception as e:
                    st.error(f"❌ એરર આવી છે: {str(e)}")

with tab2:
    st.subheader("🔍 લાઈવ માર્કેટ સ્કેનર & બાય/હોલ્ડ ગ્રોથ ફિલ્ટર 🚀")
    if st.button("⚡ લાઈવ વોચલિસ્ટ સ્કેનર રન કરો"):
        scanner_results = []
        progress_bar = st.progress(0)
        total_stocks = len(st.session_state.watchlist)
        
        for i, sym in enumerate(st.session_state.watchlist):
            try:
                t = yf.Ticker(sym)
                h = t.history(period="6mo")
                inf = t.info
                if not h.empty and len(h) >= 50:
                    cp = h['Close'].iloc[-1]
                    name = inf.get('longName', sym)
                    
                    ema9 = h['Close'].ewm(span=9).mean().iloc[-1]
                    ema20 = h['Close'].ewm(span=20).mean().iloc[-1]
                    ema200 = h['Close'].ewm(span=200).mean().iloc[-1] if len(h) >= 200 else cp
                    
                    vol_today = h['Volume'].iloc[-1]
                    vol_avg = h['Volume'].rolling(20).mean().iloc[-1]
                    is_vol_good = vol_today > (1.2 * vol_avg)
                    
                    if cp > ema200 and ema9 > ema20 and is_vol_good:
                        action = "🔥 મજબૂત બાય / ગ્રોથ (Strong Buy) ✅"
                    elif cp > ema200:
                        action = "🛡️ હોલ્ડ કરો (Hold / Safe) ⏳"
                    else:
                        action = "⚠️ વેચાણ દબાણ / અવોઈડ (Avoid) ❌"
                        
                    scanner_results.append({
                        "સ્ટોક": sym,
                        "કંપની": name,
                        "હાલનો ભાવ (₹)": round(cp, 2),
                        "200 EMA ઉપર?": "હા" if cp > ema200 else "ના",
                        "વોલ્યુમ સ્પાઇક": "હા 🔥" if is_vol_good else "સામાન્ય",
                        "આપણી ભલામણ": action
                    })
            except:
                pass
            progress_bar.progress((i + 1) / total_stocks)
            
        if scanner_results:
            st.dataframe(pd.DataFrame(scanner_results), use_container_width=True)
            st.success("🎉 સ્કેનર પૂરું થઈ ગયું!")
        else:
            st.warning("⚠️ ડેટા ફેચ કરવામાં કોઈ સમસ્યા છે.")

with tab3:
    st.subheader("📋 વોચલિસ્ટ કમ્પેરિઝન ડેશબોર્ડ 🔍📊")
    if st.button("🔄 વોચલિસ્ટ કમ્પેર કરો"):
        comp_data = []
        for sym in st.session_state.watchlist:
            try:
                t = yf.Ticker(sym)
                h = t.history(period="1mo")
                inf = t.info
                if not h.empty:
                    cp = h['Close'].iloc[-1]
                    chg = ((cp - h['Close'].iloc[0]) / h['Close'].iloc[0]) * 100
                    comp_data.append({
                        "સિમ્બોલ": sym,
                        "નામ": inf.get('longName', sym),
                        "ભાવ (₹)": round(cp, 2),
                        "માસિક રિટર્ન (%)": round(chg, 2),
                        "P/E": inf.get('trailingPE', 'N/A')
                    })
            except:
                pass
        if comp_data:
            st.dataframe(pd.DataFrame(comp_data), use_container_width=True)

with tab4:
    st.subheader("💼 તમારો પર્સનલ પોર્ટફોલિયો ટ્રેકર 📈💰")
    with st.form("portfolio_form"):
        p_stock = st.text_input("સ્ટોક સિમ્બોલ (દા.ત. DYCL.NS): 📝")
        p_qty = st.number_input("શેરની સંખ્યા (Quantity): 🔢", min_value=1, value=10)
        p_price = st.number_input("ખરીદીનો સરેરાશ ભાવ (Buy Price ₹): 💵", min_value=0.1, value=100.0)
        submitted = st.form_submit_button("➕ પોર્ટફોલિયોમાં ઉમેરો")
        
        if submitted and p_stock:
            clean_p_stock = p_stock.strip().upper()
            new_row = pd.DataFrame({"Stock": [clean_p_stock], "Qty": [p_qty], "Buy Price": [p_price]})
            st.session_state.portfolio = pd.concat([st.session_state.portfolio, new_row], ignore_index=True)
            st.success(f"✅ {clean_p_stock} પોર્ટફોલિયોમાં ઉમેરાઈ ગયો!")

    if not st.session_state.portfolio.empty:
        pf_data = []
        tot_inv, tot_val = 0, 0
        for idx, row in st.session_state.portfolio.iterrows():
            stk, q, bp = row["Stock"], row["Qty"], row["Buy Price"]
            try:
                cur_p = yf.Ticker(stk).history(period="1d")['Close'].iloc[-1]
            except:
                cur_p = bp
            inv, val = q * bp, q * cur_p
            pnl = val - inv
            tot_inv += inv
            tot_val += val
            pf_data.append({"સ્ટોક": stk, "Qty": q, "Buy ₹": bp, "Current ₹": round(cur_p, 2), "P&L ₹": round(pnl, 2)})
        st.dataframe(pd.DataFrame(pf_data), use_container_width=True)
        tot_pnl = tot_val - tot_inv
        c1, c2, c3 = st.columns(3)
        c1.metric("કુલ રોકાણ", f"₹{tot_inv:.2f}")
        c2.metric("વર્તમાન કિંમત", f"₹{tot_val:.2f}")
        c3.metric("કુલ પ્રોફિટ/લોસ", f"₹{tot_pnl:.2f}", delta=f"{tot_pnl:.2f}")
