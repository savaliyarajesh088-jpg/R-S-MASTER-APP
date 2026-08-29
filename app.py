import streamlit as st
import yfinance as yf
import requests
import plotly.graph_objects as go

# Page Configuration
st.set_page_config(page_title="R S MASTER APP", page_icon="📈", layout="wide")

# App Title
st.title("📈 R S MASTER APP")
st.write("ભારતીય સ્ટોક માર્કેટ એનાલિસિસ એન્ડ ડેશબોર્ડ")

# Sidebar for Inputs
st.sidebar.header("સેટિંગ્સ")
api_key = st.secrets.get("GEMINI_API_KEY", "")

if not api_key:
    api_key = st.sidebar.text_input("તમારી Gemini API Key નાખો:", type="password")

symbol = st.sidebar.text_input("સ્ટોક સિમ્બોલ લખો:", value="TATASTEEL.NS")
timeframe = st.sidebar.selectbox("ટાઈમફ્રેમ પસંદ કરો:", ["1mo", "3mo", "6mo", "1y"])

if st.sidebar.button("Analyse Stock"):
    if not api_key:
        st.error("મહેરબાની કરીને સાચી Gemini API Key પ્રદાન કરો.")
    elif not symbol:
        st.error("મહેરબાની કરીને સ્ટોક સિમ્બોલ લખો.")
    else:
        with st.spinner("ડેટા ફેચ થઈ રહ્યો છે અને એનાલિસિસ ચાલુ છે..."):
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=timeframe)
                info = ticker.info

                if hist.empty:
                    st.error("આ સિમ્બોલ માટે કોઈ ડેટા મળ્યો નથી.")
                else:
                    # Current Stock Details & Metrics
                    current_price = hist['Close'].iloc[-1]
                    prev_close = hist['Close'].iloc[-2]
                    change = current_price - prev_close
                    pct_change = (change / prev_close) * 100
                    
                    company_name = info.get('longName', symbol)
                    market_cap = info.get('marketCap', 'N/A')
                    pe_ratio = info.get('trailingPE', 'N/A')
                    high_52 = info.get('fiftyTwoWeekHigh', 'N/A')
                    low_52 = info.get('fiftyTwoWeekLow', 'N/A')

                    # Display Metrics
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("હાલનો ભાવ", f"₹{current_price:.2f}", f"{pct_change:.2f}%")
                    col2.metric("మార్કેટ કેપ", f"{market_cap:,}" if isinstance(market_cap, int) else market_cap)
                    col3.metric("P/E રેશિયો", f"{pe_ratio}")
                    col4.metric("૫૨ સપ્તાહ હાઈ", f"₹{high_52}")

                    # Plotly Chart
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], mode='lines', name='Close Price', line=dict(color='blue', width=2)))
                    fig.update_layout(title=f"{company_name} - પ્રાઇસ ચાર્ટ", xaxis_title="તારીખ", yaxis_title="ભાવ (₹)", template="plotly_white")
                    st.plotly_chart(fig, use_container_width=True)

                    # Gemini Prompt
                    prompt_text = f"""
                    તમે એક એક્સપર્ટ સ્ટોક માર્કેટ એનાલિસ્ટ છો.
                    નીચે આપેલા સ્ટોક ડેટાનું વિશ્લેષણ કરો અને ગુજરાતી ભાષામાં વિગતવાર રિપોર્ટ આપો:

                    સ્ટોકનું નામ: {company_name} ({symbol})
                    હાલનો ભાવ: ₹{current_price:.2f}
                    માર્કેટ કેપ: {market_cap}
                    P/E રેશિયો: {pe_ratio}
                    ૫૨ સપ્તાહ હાઈ/લો: ₹{high_52} / ₹{low_52}

                    મહેરબાની કરીને નીચે મુજબ જવાબો આપો:
                    1. સ્ટોકનું સામાન્ય વિશ્લેષણ (General Analysis)
                    2. હાલના ભાવ પ્રમાણે શોર્ટ ટર્મ દ્રષ્ટિકોણ (Short-term Outlook)
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
                            st.subheader(f"📊 {company_name} એનાલિસિસ રિપોર્ટ:")
                            st.write(analysis_text)
                            success = True
                            break

                    if not success:
                        st.error("સર્વર પર અત્યારે વધુ ટ્રાફિક છે. થોડીવાર પછી ટ્રાય કરો.")

            except Exception as e:
                st.error(f"એરર આવી છે: {str(e)}")
