import streamlit as st
import yfinance as yf
import pandas as pd

# Page Configuration
st.set_page_config(page_title="R S MASTER APP", page_icon="📈", layout="wide")

# App Title
st.title("📈 R S MASTER APP")
st.write("ભારતીય સ્ટોક માર્કેટ એડવાન્સ્ડ એનાલિસિસ એન્ડ ઓટો-સિગ્નલ ડેશબોર્ડ")

# Sidebar Elements
st.sidebar.header("⚙️ સેટિંગ્સ અને વોચલિસ્ટ")

# Watchlist Dropdown
popular_stocks = ["TATASTEEL.NS", "RELIANCE.NS", "INFY.NS", "TCS.NS", "SBIN.NS", "HDFCBANK.NS", "ITC.NS", "WIPRO.NS"]
selected_stock = st.sidebar.selectbox("વોચલિસ્ટમાંથી સ્ટોક પસંદ કરો:", popular_stocks)

# Custom Symbol Input
symbol = st.sidebar.text_input("અથવા કસ્ટમ સિમ્બોલ લખો:", value=selected_stock)

# Analyse Button in Sidebar
if st.sidebar.button("Analyse Stock"):
    if not symbol:
        st.error("મહેરબાની કરીને સ્ટોક સિમ્બોલ લખો.")
    else:
        with st.spinner("ડેટા ફેચ થઈ રહ્યો છે, ટેક્નિકલ ઇન્ડિકેટર્સ અને રિપોર્ટ તૈયાર થઈ રહ્યા છે..."):
            try:
                # Fetch 1-year stock data
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1y")
                info = ticker.info

                if hist.empty or hist['Close'].dropna().empty:
                    st.error("આ સિમ્બોલ માટે કોઈ ડેટા મળ્યો નથી. કૃપા કરીને સાચો સિમ્બોલ નાખો.")
                else:
                    close_series = hist['Close'].dropna()
                    current_price = close_series.iloc[-1]
                    high_52 = hist['High'].max()
                    low_52 = hist['Low'].min()
                    company_name = info.get('longName', symbol)
                    pe_ratio = info.get('trailingPE', 'N/A')
                    roe = info.get('returnOnEquity', 'N/A')
                    roe_str = f"{roe * 100:.2f}%" if isinstance(roe, float) else 'N/A'
                    
                    # Company Business Summary
                    business_summary = info.get('longBusinessSummary', 'આ કંપની વિશેની વિગતવાર માહિતી ઉપલબ્ધ નથી.')

                    # 1. Calculate EMAs
                    ema_10 = close_series.ewm(span=10, adjust=False).mean().iloc[-1] if len(close_series) >= 10 else current_price
                    ema_20 = close_series.ewm(span=20, adjust=False).mean().iloc[-1] if len(close_series) >= 20 else current_price
                    ema_50 = close_series.ewm(span=50, adjust=False).mean().iloc[-1] if len(close_series) >= 50 else current_price
                    ema_200 = close_series.ewm(span=200, adjust=False).mean().iloc[-1] if len(close_series) >= 200 else current_price

                    # 2. Calculate RSI (14)
                    delta = close_series.diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                    rs = gain / loss
                    rsi_series = 100 - (100 / (1 + rs))
                    current_rsi = rsi_series.iloc[-1] if not rsi_series.empty else 50.0

                    # 3. Calculate MACD (12, 26, 9)
                    exp1 = close_series.ewm(span=12, adjust=False).mean()
                    exp2 = close_series.ewm(span=26, adjust=False).mean()
                    macd_line = exp1 - exp2
                    signal_line = macd_line.ewm(span=9, adjust=False).mean()
                    current_macd = macd_line.iloc[-1]
                    current_sig = signal_line.iloc[-1]
                    
                    macd_status = "🟢 બુલિશ ક્રોસઓવર (Buy)" if current_macd > current_sig else "🔴 બેરિશ ક્રોસઓવર (Sell)"

                    # 4. Supertrend Logic
                    hl2 = (hist['High'] + hist['Low']) / 2
                    atr = (hist['High'] - hist['Low']).rolling(window=10).mean().iloc[-1]
                    if pd.isna(atr):
                        atr = current_price * 0.02
                    supertrend_val = hl2.iloc[-1] + (2 * atr)
                    
                    supertrend_status = "🟢 બુલિશ (Supertrend Green)" if current_price > supertrend_val else "🔴 બેરિશ (Supertrend Red)"

                    # 5. Volume Spike Check
                    vol_series = hist['Volume'].dropna()
                    today_vol = vol_series.iloc[-1] if not vol_series.empty else 0
                    avg_vol = vol_series.rolling(20).mean().iloc[-1] if len(vol_series) >= 20 else today_vol
                    
                    if today_vol > (1.5 * avg_vol):
                        volume_status = "🟢 હાઇ વોલ્યુમ સ્પાઇક (High Buying/Selling)"
                        vol_score_add = 15
                    else:
                        volume_status = "⚪ સામાન્ય વોલ્યુમ (Normal Volume)"
                        vol_score_add = 0

                    # 6. Multi-Timeframe Trends
                    daily_trend = "🟢 તેજી (Bullish)" if current_price > ema_50 else "🔴 મંદી (Bearish)"
                    weekly_trend = "🟢 તેજી (Bullish)" if current_price > ema_200 else "🔴 મંદી (Bearish)"

                    # 7. Stop-Loss, Targets & Risk-to-Reward Ratio Calculator
                    stop_loss = current_price * 0.97
                    target_1 = current_price * 1.05
                    target_2 = current_price * 1.10
                    
                    risk = current_price - stop_loss
                    reward = target_1 - current_price
                    rr_ratio = round(reward / risk, 2) if risk > 0 else 0

                    # 8. Automatic Dynamic Score Calculation (Out of 100)
                    score = 40  # Base Score
                    if current_price > ema_200: score += 15
                    else: score -= 10
                    if current_price > ema_50: score += 15
                    else: score -= 10
                    if 40 <= current_rsi <= 70: score += 15
                    elif current_rsi > 70: score += 5
                    else: score -= 10
                    if current_macd > current_sig: score += 10
                    else: score -= 10
                    score += vol_score_add
                    
                    score = max(0, min(100, score))

                    if score >= 70:
                        verdict = "🔥 મજબૂત બુલિશ (Strong Buy)"
                    elif score >= 50:
                        verdict = "⚖️ સાઇડવેઝ / હોલ્ડ (Sideways / Hold)"
                    else:
                        verdict = "🔻 બેરિશ / વેચાણ દબાણ (Weak / Sell)"

                    # Display UI Metrics
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("હાલનો ભાવ", f"₹{current_price:.2f}")
                    col2.metric("ઓટો-ટેક્નિકલ સ્કોર", f"{score} / 100")
                    col3.metric("RSI (૧૪)", f"{current_rsi:.2f}")
                    col4.metric("૫૨ સપ્તાહ હાઈ", f"₹{high_52:.2f}")

                    st.markdown("---")

                    # Scoreboard & Indicators Display
                    st.subheader(f"🎯 ઓટો-પ્રો સિગ્નल સ્કોરબોર્ડ: {company_name}")
                    st.info(f"**ઓવરઓલ ટ્રેન્ડ સિગ્નલ:** {verdict}")

                    sc1, sc2, sc3 = st.columns(3)
                    sc1.write(f"**ડેઇલી ટ્રેન્ડ:** {daily_trend}")
                    sc2.write(f"**વીકલી ટ્રેન્ડ:** {weekly_trend}")
                    sc3.write(f"**સુપરટ્રેન્ડ:** {supertrend_status}")

                    sc4, sc5, sc6 = st.columns(3)
                    sc4.write(f"**MACD સ્ટેટસ:** {macd_status}")
                    sc5.write(f"**વોલ્યુમ સ્ટેટસ:** {volume_status}")
                    sc6.write(f"📊 **૫૨ સપ્તાહ લો:** ₹{low_52:.2f}")

                    # Swing Trading Levels & Risk-Reward
                    st.markdown("---")
                    st.subheader("🛡️ સ્વિંગ ટ્રેડિંગ અને રિસ્ક-ટુ-રિવોર્ડ લેવલ્સ")
                    t_col1, t_col2, t_col3, t_col4 = st.columns(4)
                    t_col1.metric("સૂચિત સ્ટોપ-લોస్ (SL)", f"₹{stop_loss:.2f}", "-3%")
                    t_col2.metric("પ્રથમ ટાર્ગેટ (T1)", f"₹{target_1:.2f}", "+5%")
                    t_col3.metric("બીજો ટાર્ગેટ (T2)", f"₹{target_2:.2f}", "+10%")
                    t_col4.metric("રિસ્ક-ટુ-રિવોર્ડ રેશિયો", f"1 : {rr_ratio}")

                    st.markdown("---")

                    # Generate Clean Professional Local Report in Gujarati
                    clean_text = f"""
==================================================
📊 {company_name} ({symbol}) - પ્રોફેશનલ એનાલિસિસ રિપોર્ટ
==================================================
હાલની કિંમત: ₹{current_price:.2f} | ટેક્નિકલ સ્કોર: {score}/100 ({verdict})

૧. કંપનીનો ટૂંકો પરિચય (Company Profile):
{business_summary}

૨. ટેક્નિકલ સ્કોર અને ઇન્ડિકેટર્સ (Technical Indicators):
- ઓટો-ટેક્નિકલ સ્કોર: {score}/100 - {verdict}
- ડેઇલી ટ્રેન્ડ (50-EMA): {daily_trend}
- વીકલી ટ્રેન્ડ (200-EMA): {weekly_trend}
- સુપરટ્રેન્ડ સ્ટેટસ: {supertrend_status}
- MACD ક્રોસઓવર: {macd_status}
- વોલ્યુમ સ્ટેટસ: {volume_status}
- RSI (14 દિવસ): {current_rsi:.2f}
- મૂવિંગ એવરેજ: 10-EMA (₹{ema_10:.2f}), 20-EMA (₹{ema_20:.2f}), 50-EMA (₹{ema_50:.2f}), 200-EMA (₹{ema_200:.2f})
- ફંડામેન્ટલ્સ: P/E રેશિયો ({pe_ratio}), ROE ({roe_str})

૩. શોર્ટ અને મિડ-ટર્મ આઉટલુક (Market Outlook):
- ૫૨ સપ્તાહની ઊંચાઈ (52W High): ₹{high_52:.2f}
- ૫૨ સપ્તાહનું તળિયું (52W Low): ₹{low_52:.2f}
- ટ્રેન્ડ વિશ્લેષણ: હાલમાં સ્ટોકનો ઓવરઓલ સ્કોર {score}/100 છે. જો ભાવ મુખ્ય મૂવિંગ એવરેજથી ઉપર ટ્રેડ થતો હોય તો તેજી જળવાઈ રહે છે, જ્યારે નીચે હોય તો વેચાણનું દબાણ જોવા મળે છે.

૪. મહત્વના ટ્રેડિંગ સ્તરો અને વ્યૂહરચના (Trading Strategy & Levels):
- સૂચિત સ્ટોપ-લોસ (SL): ₹{stop_loss:.2f} (-3% રિસ્ક)
- પ્રથમ ટાર્ગેટ (T1): ₹{target_1:.2f} (+5% પ્રોફિટ)
- બીજો ટાર્ગેટ (T2): ₹{target_2:.2f} (+10% પ્રોફિટ)
- રિસ્ક-ટુ-રિવોર્ડ રેશિયો: 1 : {rr_ratio}
- ટ્રેડિંગ સલાહ: સ્વિંગ ટ્રેડર્સ માટે સૂચિત સ્ટોપ-લોસ અનિવાર્ય છે. રિસ્ક-રિવોર્ડ રેશિયો ધ્યાનમાં રાખીને જ પોઝિશન બનાવવી યોગ્ય રહે છે.
==================================================
"""

                    st.success("એનાલિસિસ રિપોર્ટ સફળતાપૂર્વક તૈયાર થઈ ગયો છે!")
                    st.subheader(f"📊 {company_name} એનાલિસિસ રિપોર્ટ:")
                    st.write(clean_text)

                    # Download Button
                    st.download_button(
                        label="📥 આ રિપોર્ટ ડાઉનલોડ કરો (.txt)",
                        data=clean_text.encode('utf-8'),
                        file_name=f"{symbol}_analysis_report.txt",
                        mime="text/plain;charset=utf-8"
                    )

            except Exception as e:
                st.error(f"એરર આવી છે: {str(e)}")
