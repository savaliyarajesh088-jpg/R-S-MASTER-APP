import streamlit as st
import yfinance as yf
import google.generativeai as genai
import pandas as pd

# Page Configuration
st.set_page_config(page_title="R S MASTER APP", page_icon="📈", layout="wide")

# App Title
st.title("📈 R S MASTER APP")
st.write("ભારતીય સ્ટોક માર્કેટ એડવાન્સ્ડ એનાલિસિસ, સ્કોરબોર્ડ એન્ડ ટ્રેડિંગ ટૂલ")

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
        with st.spinner("ડેટા ફેચ થઈ રહ્યો છે, સ્કોર અને લેવલ ગણાઈ રહ્યા છે..."):
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
                    if isinstance(roe, float):
                        roe_str = f"{roe * 100:.2f}%"
                    else:
                        roe_str = 'N/A'

                    # 1. Calculate EMAs
                    ema_10 = close_series.ewm(span=10, adjust=False).mean().iloc[-1] if len(close_series) >= 10 else current_price
                    ema_20 = close_series.ewm(span=20, adjust=False).mean().iloc[-1] if len(close_series) >= 20 else current_price
                    ema_50 = close_series.ewm(span=50, adjust=False).mean().iloc[-1] if len(close_series) >= 50 else current_price
                    ema_200 = close_series.ewm(span=200, adjust=False).mean().iloc[-1] if len(close_series) >= 200 else current_price

                    # 2. Calculate RSI
                    delta = close_series.diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                    rs = gain / loss
                    rsi_series = 100 - (100 / (1 + rs))
                    current_rsi = rsi_series.iloc[-1] if not rsi_series.empty else 50.0

                    # 3. Stop-Loss and Target Levels (Swing Trading Logic)
                    stop_loss = current_price * 0.97  # 3% Stop Loss
                    target_1 = current_price * 1.05   # 5% Target
                    target_2 = current_price * 1.10   # 10% Target

                    # 4. Automatic Score & Signal Calculation (Out of 100)
                    score = 50  
                    signals = []

                    if current_price > ema_200:
                        score += 15
                        signals.append("✅ ભાવ ૨૦૦ EMA ની ઉપર છે (લોંગ-ટર્મ તેજી)")
                    else:
                        score -= 15
                        signals.append("❌ ભાવ ૨૦૦ EMA ની નીચે છે (લોંગ-ટર્મ નબળાઈ)")

                    if current_price > ema_50:
                        score += 15
                        signals.append("✅ ભાવ ૫૦ EMA ની ઉપર છે (મિડ-ટર્મ મજબૂતાઈ)")
                    else:
                        score -= 15
                        signals.append("❌ ભાવ ૫૦ EMA ની નીચે છે (મિડ-ટર્મ દબાણ)")

                    if 40 <= current_rsi <= 60:
                        score += 10
                        signals.append("⚖️ RSI ન્યુટ્રલ ઝોનમાં છે (સ્ટેબલ માર્કેટ)")
                    elif 60 < current_rsi <= 75:
                        score += 20
                        signals.append("🚀 RSI બુલિશ મોમેન્ટમમાં છે")
                    elif current_rsi > 75:
                        score += 5
                        signals.append("⚠️ RSI ઓવરબૉટ ઝોનમાં છે (સાવચેતી જરૂરી)")
                    else:
                        score -= 15
                        signals.append("⚠️ RSI ઓવરસોલ્ડ ઝોનમાં છે")

                    score = max(0, min(100, score))

                    if score >= 70:
                        verdict = "🔥 મજબૂત બુલિશ (Strong Buy / Positive)"
                    elif score >= 50:
                        verdict = "⚖️ સાઇડવેઝ / ન્યુટ્રલ (Sideways / Hold)"
                    else:
                        verdict = "🔻 બેરિશ / નબળો ટ્રેન્ડ (Weak / Sell Pressure)"

                    # Display Metrics Dashboard
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("હાલનો ભાવ", f"₹{current_price:.2f}")
                    col2.metric("ટેક્નિકલ સ્કોર", f"{score} / 100")
                    col3.metric("RSI (૧૪)", f"{current_rsi:.2f}")
                    col4.metric("૫૨ સપ્તાહ હાઈ", f"₹{high_52:.2f}")

                    st.markdown("---")

                    # Display Signals & Scorecard Box
                    st.subheader(f"🎯 કિંમત અને સિગ્નલ સ્કોરબોર્ડ: {company_name}")
                    st.info(f"**ઓવરઓલ ટ્રેન્ડ સિગ્નલ:** {verdict}")

                    for sig in signals:
                        st.write(sig)

                    # Display Calculated Stop-Loss & Targets for Swing Traders
                    st.markdown("---")
                    st.subheader("🛡️ સ્વિંગ ટ્રેડિંગ લેવલ્સ (Stop-Loss & Targets)")
                    t_col1, t_col2, t_col3 = st.columns(3)
                    t_col1.metric("સૂચિત સ્ટોપ-લોસ (SL)", f"₹{stop_loss:.2f}", "-3%")
                    t_col2.metric("પ્રથમ ટાર્ગેટ (T1)", f"₹{target_1:.2f}", "+5%")
                    t_col3.metric("બીજો ટાર્ગેટ (T2)", f"₹{target_2:.2f}", "+10%")

                    st.markdown("---")

                    # Formatting Technical & Fundamental Data for AI Prompt
                    tech_text = f"""
                    - ટ્રેડિંગ સ્કોર: {score}/100 ({verdict})
                    - 10 દિવસની EMA: ₹{ema_10:.2f}
                    - 20 દિવસની EMA: ₹{ema_20:.2f}
                    - 50 દિવસની EMA: ₹{ema_50:.2f}
                    - 200 દિવસની EMA: ₹{ema_200:.2f}
                    - RSI (14): {current_rsi:.2f}
                    - સૂચિત સ્ટોપ-લોસ: ₹{stop_loss:.2f} | ટાર્ગેટ: ₹{target_1:.2f} / ₹{target_2:.2f}
                    - P/E રેશિયો: {pe_ratio} | ROE: {roe_str}
                    """

                    prompt_text = f"""
                    તમે એક એક્સપર્ટ સ્ટોક માર્કેટ એનાલિસ્ટ છો.
                    નીચે આપેલા સ્ટોક ડેટા અને ટેક્નિકલ સ્કોરનું વિશ્લેષણ કરો અને ગુજરાતી ભાષામાં વિગતવાર રિપોર્ટ આપો:

                    સ્ટોકનું નામ: {company_name} ({symbol})
                    હાલનો ભાવ (Current Price): ₹{current_price:.2f}
                    ટેક્નિકલ સ્કોર: {score}/100 ({verdict})
                    P/E રેશિયો: {pe_ratio}
                    ROE: {roe_str}
                    ૫૨ સપ્તાહ હાઈ/લો: ₹{high_52:.2f} / ₹{low_52:.2f}

                    ટેક્નિકલ ડેટા:
                    {tech_text}

                    મહેરબાની કરીને નીચે મુજબ જવાબો આપો:
                    1. સ્કોર અને ટ્રેન્ડનું વિશ્લેષણ (Trend & Score Breakdown)
                    2. શોર્ટ અને મિડ ટર્મ દ્રષ્ટિકોણ (Short & Mid-term Outlook)
                    3. રોકાણકારો માટે મહત્વની ટિપ્સ, સપોર્ટ/રેઝિસ્ટન્સ, સ્ટોપલોસ અને એન્ટ્રી પોઇન્ટ્સ
                    """

                    # Configure and call official Gemini API
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-3.6-flash')
                    response = model.generate_content(prompt_text)

                    if response and response.text:
                        st.success("એનાલિસિસ સફળતાપૂર્વક પૂર્ણ થયું!")
                        st.subheader(f"📊 {company_name} એનાલિસિસ રિપોર્ટ:")
                        st.write(response.text)

                        # Download Report Button
                        st.download_button(
                            label="📥 આ રિપોર્ટ ડાઉનલોડ કરો (.txt)",
                            data=response.text,
                            file_name=f"{symbol}_complete_report.txt",
                            mime="text/plain"
                        )
                    else:
                        st.error("એનાલિસિસ જનરેટ કરવામાં સમસ્યા આવી.")

            except Exception as e:
                st.error(f"એરર આવી છે: {str(e)}")
