import streamlit as st
import yfinance as yf
from anthropic import Anthropic

st.set_page_config(page_title="AI Stock Analyst", page_icon="📈", layout="centered")

# Hide Streamlit header & footer for native app look
st.markdown("""<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>""", unsafe_allow_html=True)

st.title("📈 AI Stock Analyst")

ticker = st.text_input("સ્ટોક સિમ્બોલ લખો (જેમ કે TATASTEEL.NS, RELIANCE.NS):", "TATASTEEL.NS")
api_key = st.text_input("તમારી Claude API Key નાખો:", type="password")

if st.button("Analyse Stock"):
    if not api_key:
        st.error("મહેરબાની કરીને તમારી Claude API Key લખો.")
    else:
        with st.spinner('ડેટા ફેચ થઈ રહ્યો છે...'):
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1mo")
            info = stock.info
            
            st.subheader(f"{ticker} ચાર્ટ")
            st.line_chart(hist['Close'])
            
            prompt_data = f"""
            Stock: {ticker}
            P/E Ratio: {info.get('trailingPE', 'N/A')}
            52 Week High: {info.get('fiftyTwoWeekHigh', 'N/A')}
            52 Week Low: {info.get('fiftyTwoWeekLow', 'N/A')}
            Recent Prices: {hist['Close'].tail(5).to_dict()}
            
            કૃપા કરીને ગુજરાતીમાં 3 પોઈન્ટ્સમાં એનાલિસિસ આપો:
            1. ફંડામેન્ટલ સ્થિતિ
            2. ટ્રેન્ડ
            3. રિસ્ક ફેક્ટર
            """

            client = Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=400,
                messages=[{"role": "user", "content": prompt_data}]
            )
            
            st.subheader("💡 AI એનાલિસિસ રિપોર્ટ:")
            st.write(response.content[0].text)
