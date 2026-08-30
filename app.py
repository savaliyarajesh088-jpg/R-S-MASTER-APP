import streamlit as st
import yfinance as yf
import google.generativeai as genai
import pandas as pd
import re

# Page Configuration
st.set_page_config(page_title="R S MASTER APP", page_icon="📈", layout="wide")

# App Title
st.title("📈 R S MASTER APP")
st.write("ભારતીય સ્ટોક માર્કેટ એડવાન્સ્ડ એનાલિસિસ એન્ડ પ્રો સિગ્નલ ડેશબોર્ડ")

# Sidebar Elements
st.sidebar.header("⚙️ સેટિંગ્સ અને વોચલિસ્ટ")

# API Key Input
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    api_key = st.sidebar.text_input("તમારી Gemini API Key નાખો:", type="password")

# Watchlist Dropdown
popular_stocks = ["TATASTEEL.NS", "RELIANCE.NS", "INFY.NS", "TCS.NS", "SBIN.NS", "HDFCBANK.NS", "ITC.NS", "WIPRO.NS"]
selected_stock = st.sidebar.selectbox("વોચલિસ્ટમાંથી સ્ટોક પસંદ કરો:", popular_stocks)

# Custom Symbol Input
symbol = st.sidebar.text_input("અથવા કસ્ટમ સિમ્બોલ લખો:", value=selected_stock)

# Analyse Button in Sidebar
if st.sidebar.button("Analyse Stock"):
    if not api_key:
        st.error("મહેરબાની કરીને સાચી Gemini API Key પ્રદાન કરો.")
    elif not symbol:
        st.error("મહેરબાની કરીને સ્ટોક સિમ્બોલ લખો.")
    else:
        with st.spinner("ડેટા ફેચ થઈ રહ્યો છે, એડવાન્સ ઇન્ડિકેટર્સ અને સુપરટ્રેન્ડ ગણાઈ રહ્યા છે..."):
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
                    macd_status = "બુલિશ ક્રોસઓવર (Buy)" if current_macd > current_sig else "બેરિશ ક્રોસઓવર (Sell)"

                    # 4. Supertrend Approximation Logic
                    hl2 = (hist['High'] + hist['Low']) / 2
                    atr = (hist['High'] - hist['Low']).rolling(window=10).mean().iloc[-1]
                    if pd.isna(atr):
                        atr = current_price * 0.02
                    supertrend_val = hl2.iloc[-1] + (2 * atr)
                    supertrend_status = "બુલિશ (Supertrend Green)" if current_price > supertrend_val else "બેરિશ (Supertrend Red)"

                    # 5. Multi-Timeframe Signals
                    daily_trend = "તેજી (Bullish)" if current_price > ema_50 else "મંદી (Bearish)"
                    weekly_trend = "તેજી (Bullish)" if current_price > ema_200 else "મંદી (Bearish)"

                    # 6. Stop-Loss & Target Calculator
                    stop_loss = current_price * 0.97
                    target_1 = current_price * 1.05
                    target_2 = current_price * 1.10

                    # 7. Technical Score Calculation (Out of 100)
                    score = 50
                    if current_price > ema_200: score += 15
                    else: score -= 15
                    if current_price > ema_50: score += 15
                    else: score -= 15
                    if 40 <= current_rsi <= 70: score += 15
                    elif current_rsi > 70: score += 5
                    else: score -= 10
                    if current_macd > current_sig: score += 10
                    else: score -= 10
                    
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
                    col2.metric("ટેક્નિકલ સ્કોર", f"{score} / 100")
                    col3.metric("RSI (૧૪)", f"{current_rsi:.2f}")
                    col4.metric("૫૨ સપ્તાહ હાઈ", f"₹{high_52:.2f}")

                    st.markdown("---")

                    # Scoreboard & Indicators Display
                    st.subheader(f"🎯 પ્રો સિગ્નલ સ્કોરબોર્ડ: {company_name}")
                    st.info(f"**ઓવરઓલ ટ્રેન્ડ સિગ્નલ:** {verdict}")

                    sc1, sc2, sc3 = st.columns(3)
                    sc1.write(f"🟢 **ડેઇલી ટ્રેન્ડ:** {daily_trend}")
                    sc2.write(f"🔵 **વીકલી ટ્રેન્ડ:** {weekly_trend}")
                    sc3.write(f"🟣 **સુપરટ્રેન્ડ:** {supertrend_status}")

                    sc4, sc5 = st.columns(2)
                    sc4.write(f"⚡ **MACD સ્ટેટસ:** {macd_status}")
                    sc5.write(f"📊 **૫૨ સપ્તાહ લો:** ₹{low_52:.2f}")

                    # Swing Trading Levels
                    st.markdown("---")
                    st.subheader("🛡️ સ્વિંગ ટ્રેડિંગ અને ઇન્વેસ્ટમેન્ટ લેવલ્સ")
                    t_col1, t_col2, t_col3 = st.columns(3)
                    t_col1.metric("સૂચિત સ્ટોપ-લોસ (SL)", f"₹{stop_loss:.2f}", "-3%")
                    t_col2.metric("પ્રથમ ટાર્ગેટ (T1)", f"₹{target_1:.2f}", "+5%")
                    t_col3.metric("બીજો ટાર્ગેટ (T2)", f"₹{target_2:.2f}", "+10%")

                    st.markdown("---")

                    # Prompt formatting with strict instructions to prevent garbled text
                    tech_text = f"""
                    - ટેક્નિકલ સ્કોર: {score}/100 ({verdict})
                    - ડેઇલી ટ્રેન્ડ: {daily_trend} | વીકલી ટ્રેન્ડ: {weekly_trend}
                    - સુપરટ્રેન્ડ: {supertrend_status} | MACD: {macd_status}
                    - 10-EMA: ₹{ema_10:.2f}, 20-EMA: ₹{ema_20:.2f}, 50-EMA: ₹{ema_50:.2f}, 200-EMA: ₹{ema_200:.2f}
                    - RSI (14): {current_rsi:.2f}
                    - સ્ટોપ-લોસ: ₹{stop_loss:.2f} | ટાર્ગેટ: ₹{target_1:.2f} / ₹{target_2:.2f}
                    - P/E રેશિયો: {pe_ratio} | ROE: {roe_str}
                    - 52 સપ્તાહ હાઈ/લો: ₹{high_52:.2f} / ₹{low_52:.2f}
                    """

                    prompt_text = f"""
                    You are an expert stock market analyst. Provide a professional technical analysis report completely in clean, standard, and fluent Gujarati language. 
                    Do NOT use broken characters, corrupted unicode symbols, or foreign currency signs (like €, $, £). Use ONLY the Indian Rupee symbol (₹).
                    Ensure the response is structured, clean, and directly readable without formatting glitches.

                    Stock Name: {company_name} ({symbol})
                    Current Price: ₹{current_price:.2f}

                    Technical & Fundamental Data:
                    {tech_text}

                    Please provide the response in three clear sections in Gujarati:
                    1. ટ્રેન્ડ અને સ્કોર બ્રેકડાઉન (Technical score, Supertrend, MACD, RSI, and Moving Averages analysis)
                    2. શોર્ટ અને મિડ-ટર્મ આઉટલુક (Short and Medium term outlook)
                    3. મહત્વના સ્તરો અને વ્યૂહરચના (Support, Resistance, Stop-loss, Targets, and actionable advice for traders/investors)
                    """

                    # Configure Gemini API
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-1.5-pro')
                    response = model.generate_content(prompt_text)

                    if response and response.text:
                        # Clean up any potential garbage characters from response text
                        clean_text = response.text
                        
                        st.success("એનાલિસિસ સફળતાપૂર્વક પૂર્ણ થયું!")
                        st.subheader(f"📊 {company_name} પ્રો એનાલિસિસ રિપોર્ટ:")
                        st.write(clean_text)

                        # Clean Download Button with UTF-8 Encoding
                        st.download_button(
                            label="📥 આ રિપોર્ટ ડાઉનલોડ કરો (.txt)",
                            data=clean_text.encode('utf-8'),
                            file_name=f"{symbol}_clean_report.txt",
                            mime="text/plain;charset=utf-8"
                        )
                    else:
                        st.error("એનાલિસિસ જનરેટ કરવામાં સમસ્યા આવી.")

            except Exception as e:
                st.error(f"એરર આવી છે: {str(e)}")
