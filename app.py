import streamlit as st
import yfinance as yf
import google.generativeai as genai

# Page Configuration
st.set_page_config(page_title="R S MASTER APP", page_icon="📈")

# App Title
st.title("📈 R S MASTER APP")
st.write("ભારતીય સ્ટોક માર્કેટ એનાલિસિસ")

# Get API Key from Streamlit Secrets or User Input
api_key = st.secrets.get("GEMINI_API_KEY", "")

if not api_key:
    api_key = st.text_input("તમારી Gemini API Key નાખો:", type="password")

symbol = st.text_input("સ્ટોક સિમ્બોલ લખો (જેમ કે TATASTEEL.NS, RELIANCE.NS):", value="TATASTEEL.NS")

if st.button("Analyse Stock"):
    if not api_key:
        st.error("મહેરબાની કરીને સાચી Gemini API Key પ્રદાન કરો.")
    elif not symbol:
        st.error("મહેરબાની કરીને સ્ટોક સિમ્બોલ લખો.")
    else:
        with st.spinner("ડેટા ફેચ થઈ રહ્યો છે અને એનાલિસિસ ચાલુ છે..."):
            try:
                # Fetch 1-year stock data for accurate Moving Averages
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

                    # Calculate Exponential Moving Averages (EMA 10, 20, 50, 100, 200)
                    ema_10 = close_series.ewm(span=10, adjust=False).mean().iloc[-1] if len(close_series) >= 10 else 'N/A'
                    ema_20 = close_series.ewm(span=20, adjust=False).mean().iloc[-1] if len(close_series) >= 20 else 'N/A'
                    ema_50 = close_series.ewm(span=50, adjust=False).mean().iloc[-1] if len(close_series) >= 50 else 'N/A'
                    ema_100 = close_series.ewm(span=100, adjust=False).mean().iloc[-1] if len(close_series) >= 100 else 'N/A'
                    ema_200 = close_series.ewm(span=200, adjust=False).mean().iloc[-1] if len(close_series) >= 200 else 'N/A'

                    # Display Clean Metrics
                    col1, col2, col3 = st.columns(3)
                    col1.metric("હાલનો ભાવ", f"₹{current_price:.2f}")
                    col2.metric("૫૨ સપ્તાહ હાઈ", f"₹{high_52:.2f}")
                    col3.metric("૫૨ સપ્તાહ લો", f"₹{low_52:.2f}")

                    st.markdown("---")

                    # Formatting EMA for Prompt
                    ema_text = f"""
                    - 10 દિવસની એક્સપોનેન્શિયલ મૂવિંગ એવરેજ (EMA 10): {f'₹{ema_10:.2f}' if isinstance(ema_10, float) else ema_10}
                    - 20 દિવસની એક્સપોનેન્શિયલ મૂવિંગ એવરેજ (EMA 20): {f'₹{ema_20:.2f}' if isinstance(ema_20, float) else ema_20}
                    - 50 દિવસની એક્સપોનેન્શિયલ મૂવિંગ એવરેજ (EMA 50): {f'₹{ema_50:.2f}' if isinstance(ema_50, float) else ema_50}
                    - 100 દિવસની એક્સપોનેન્શિયલ મૂવિંગ એવરેજ (EMA 100): {f'₹{ema_100:.2f}' if isinstance(ema_100, float) else ema_100}
                    - 200 દિવસની એક્સપોનેન્શિયલ મૂવિંગ એવરેજ (EMA 200): {f'₹{ema_200:.2f}' if isinstance(ema_200, float) else ema_200}
                    """

                    prompt_text = f"""
                    તમે એક એક્સપર્ટ સ્ટોક માર્કેટ એનાલિસ્ટ છો.
                    નીચે આપેલા સ્ટોક ડેટા અને ટેક્નિકલ EMA (Exponential Moving Averages) નું વિશ્લેષણ કરો અને ગુજરાતી ભાષામાં વિગતવાર રિપોર્ટ આપો:

                    સ્ટોકનું નામ: {company_name} ({symbol})
                    હાલનો ભાવ (Current Price): ₹{current_price:.2f}
                    P/E રેશિયો: {pe_ratio}
                    ૫૨ સપ્તાહ હાઈ/લો: ₹{high_52:.2f} / ₹{low_52:.2f}

                    ટેક્નિકલ EMA ડેટા:
                    {ema_text}

                    મહેરબાની કરીને નીચે મુજબ જવાબો આપો:
                    1. સ્ટોકનું સામાન્ય વિશ્લેષણ અને EMA આધારે ટ્રેન્ડ (General & Trend Analysis)
                    2. હાલના ભાવ અને EMA પ્રમાણે શોર્ટ/મિડ ટર્મ દ્રષ્ટિકોણ (Short & Mid-term Outlook)
                    3. રોકાણકારો માટે મહત્વની ટિપ્સ, સપોર્ટ/રેઝિસ્ટન્સ અને રિસ્ક ફેક્ટર્સ
                    """

                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-3.6-flash')
                    response = model.generate_content(prompt_text)

                    if response and response.text:
                        st.success("એનાલિસિસ સફળતાપૂર્વક પૂર્ણ થયું!")
                        st.subheader(f"📊 {company_name} રિપોર્ટ:")
                        st.write(response.text)
                    else:
                        st.error("એનાલિસિસ જનરેટ કરવામાં સમસ્યા આવી.")

            except Exception as e:
                st.error(f"એરર આવી છે: {str(e)}")
