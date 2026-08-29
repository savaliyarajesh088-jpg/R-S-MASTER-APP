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
                # Fetch stock data using yfinance
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1mo")
                info = ticker.info

                if hist.empty or hist['Close'].dropna().empty:
                    st.error("આ સિમ્બોલ માટે કોઈ ડેટા મળ્યો નથી. કૃપા કરીને સાચો સિમ્બોલ નાખો (ઉદા. TATASTEEL.NS).")
                else:
                    # Current Stock Details
                    close_series = hist['Close'].dropna()
                    current_price = close_series.iloc[-1]
                    high_price = hist['High'].max()
                    low_price = hist['Low'].min()
                    company_name = info.get('longName', symbol)
                    pe_ratio = info.get('trailingPE', 'N/A')

                    # Display Clean Metrics
                    col1, col2, col3 = st.columns(3)
                    col1.metric("હાલનો ભાવ", f"₹{current_price:.2f}")
                    col2.metric("૧ મહિનાનો હાઈ", f"₹{high_price:.2f}")
                    col3.metric("૧ મહિનાનો લો", f"₹{low_price:.2f}")

                    st.markdown("---")

                    prompt_text = f"""
                    તમે એક એક્સપર્ટ સ્ટોક માર્કેટ એનાલિસ્ટ છો.
                    નીચે આપેલા સ્ટોક ડેટાનું વિશ્લેષણ કરો અને ગુજરાતી ભાષામાં વિગતવાર રિપોર્ટ આપો:

                    સ્ટોકનું નામ: {company_name} ({symbol})
                    હાલનો ભાવ (Current Price): ₹{current_price:.2f}
                    છેલ્લા 1 મહિનાનો હાઈ (1 Month High): ₹{high_price:.2f}
                    છેલ્લા 1 મહિનાનો લો (1 Month Low): ₹{low_price:.2f}
                    P/E રેશિયો: {pe_ratio}

                    મહેરબાની કરીને નીચે મુજબ જવાબો આપો:
                    1. સ્ટોકનું સામાન્ય વિશ્લેષણ (General Analysis)
                    2. હાલના ભાવ પ્રમાણે શોર્ટ ટર્મ દ્રષ્ટિકોણ (Short-term Outlook)
                    3. રોકાણકારો માટે મહત્વની ટિપ્સ અને રિસ્ક ફેક્ટર્સ
                    """

                    # Configure and call official Gemini API with supported model
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    response = model.generate_content(prompt_text)

                    if response and response.text:
                        st.success("એનાલિસિસ સફળતાપૂર્વક પૂર્ણ થયું!")
                        st.subheader(f"📊 {company_name} રિપોર્ટ:")
                        st.write(response.text)
                    else:
                        st.error("એનાલિસિસ જનરેટ કરવામાં સમસ્યા આવી.")

            except Exception as e:
                st.error(f"એરર આવી છે: {str(e)}")
