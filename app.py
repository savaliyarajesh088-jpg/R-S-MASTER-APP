import streamlit as st
import yfinance as yf
import google.generativeai as genai

# Page Configuration
st.set_page_config(page_title="R S MASTER APP", page_icon="📈")

# અહી નવું નામ આપેલ છે
st.title("📈 R.S STOCK MASTER")
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

                if hist.empty:
                    st.error("આ સિમ્બોલ માટે કોઈ ડેટા મળ્યો નથી. કૃપા કરીને સાચો સિમ્બોલ નાખો (ઉદા. TATASTEEL.NS).")
                else:
                    # Current Stock Details
                    current_price = hist['Close'].iloc[-1]
                    high_price = hist['High'].max()
                    low_price = hist['Low'].min()
                    company_name = info.get('longName', symbol)

                    # Configure Gemini API
                    genai.configure(api_key=api_key)
                    
                    # Using recommended gemini-3.6-flash model
                    model = genai.GenerativeModel('gemini-3.6-flash')

                    prompt = f"""
                    તમે એક એક્સપર્ટ સ્ટોક માર્કેટ એનાલિસ્ટ છો.
                    નીચે આપેલા સ્ટોક ડેટાનું વિશ્લેષણ કરો અને ગુજરાતી ભાષામાં વિગતવાર રિપોર્ટ આપો:

                    સ્ટોકનું નામ: {company_name} ({symbol})
                    હાલનો ભાવ (Current Price): ₹{current_price:.2f}
                    છેલ્લા 1 મહિનાનો હાઈ (1 Month High): ₹{high_price:.2f}
                    છેલ્લા 1 મહિનાનો લો (1 Month Low): ₹{low_price:.2f}

                    મહેરબાની કરીને નીચે મુજબ જવાબો આપો:
                    1. સ્ટોકનું સામાન્ય વિશ્લેષણ (General Analysis)
                    2. હાલના ભાવ પ્રમાણે શોર્ટ ટર્મ દ્રષ્ટિકોણ (Short-term Outlook)
                    3. રોકાણકારો માટે મહત્વની ટિપ્સ અને રિસ્ક ફેક્ટર્સ
                    """

                    # Generate response
                    response = model.generate_content(prompt)

                    # Display Output
                    st.success("એનાલિસિસ સફળતાપૂર્વક પૂર્ણ થયું!")
                    st.subheader(f"📊 {company_name} રિપોર્ટ:")
                    st.write(response.text)

            except Exception as e:
                st.error(f"એરર આવી છે: {str(e)}")
