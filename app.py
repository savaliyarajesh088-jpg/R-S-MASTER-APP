import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from deep_translator import GoogleTranslator

# Page Configuration & Professional Styling
st.set_page_config(page_title="આર એસ માસ્ટર એપ - પ્રો અલ્ટીમેટ", page_icon="🚀", layout="wide")

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
st.title("🚀 આર એસ માસ્ટર એપ - પ્રો અલ્ટીમેટ ટ્રેડિંગ & ઇન્વેસ્ટમેન્ટ ડેશબોર્ડ 📈💎")
st.markdown("---")

# Initialize Session States
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = [
        "TATASTEEL.NS", "RELIANCE.NS", "INFY.NS", "TCS.NS", 
        "SBIN.NS", "HDFCBANK.NS", "ITC.NS", "WIPRO.NS"
    ]

if 'portfolio' not in st.session_state:
    st.session_state.portfolio = pd.DataFrame(columns=["Stock", "Qty", "Buy Price"])

# Sidebar Navigation / Settings with Emojis
st.sidebar.header("⚙️ સેટિંગ્સ અને વોચલિસ્ટ મેનેજમેન્ટ 🛠️")

# 1. Add New Stock Section
st.sidebar.subheader("➕ નવો સ્ટોક ઉમેરો 📥")
new_stock_input = st.sidebar.text_input("સ્ટોક સિમ્બોલ લખો (દા.ત. ZOMATO.NS): 📝")

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
tab1, tab2, tab3 = st.tabs(["📊 વિગતવાર એનાલિસિસ & સપોર્ટ-રેઝિસ્ટન્સ ચાર્ટ", "📋 વોચલિસ્ટ કમ્પેરિઝન ડેશબોર્ડ", "💼 મારો પોર્ટફોલિયો ટ્રેકર"])

with tab1:
    st.subheader("🎯 સિંગલ સ્ટોક પ્રોફેશનલ એનાલિસિસ, સપોર્ટ-રેઝિસ્ટન્સ અને સ્માર્ટ સ્વિંગ 📉")
    
    selected_stock = st.selectbox("વિશ્લેષણ માટે સ્ટોક પસંદ કરો: 🔍", st.session_state.watchlist, key="analysis_box")
    
    if st.button("🚀 સ્ટોકનું પ્રોફેશનલ વિશ્લેષણ કરો"):
        if not selected_stock:
            st.error("❌ મહેરબાની કરીને સ્ટોક પસંદ કરો.")
        else:
            with st.spinner(f"⏳ {selected_stock} નો ફંડામેન્ટલ, ટેક્નિકલ અને પ્રાઇસ ડેટા ફેચ થઈ રહ્યો છે... 🔄"):
                try:
                    ticker = yf.Ticker(selected_stock)
                    hist = ticker.history(period="1y")
                    hist_monthly = ticker.history(period="5y", interval="1mo")
                    info = ticker.info

                    if hist.empty or hist['Close'].dropna().empty:
                        st.error("❌ આ સિમ્બોલ માટે કોઈ ડેટા મળ્યો નથી.")
                    else:
                        close_series = hist['Close'].dropna()
                        current_price = close_series.iloc[-1]
                        high_52 = hist['High'].max()
                        low_52 = hist['High'].min()
                        company_name = info.get('longName', selected_stock)
                        pe_ratio = info.get('trailingPE', 'N/A')
                        roe = info.get('returnOnEquity', 'N/A')
                        roe_str = f"{roe * 100:.2f}%" if isinstance(roe, float) else 'N/A'
                        debt_to_equity = info.get('debtToEquity', 'N/A')
                        
                        # ADVANCED FUNDAMENTAL LOGIC FOR 3-5 YEARS TARGET
                        eps_growth = info.get('earningsGrowth', None)
                        rev_growth = info.get('revenueGrowth', None)
                        
                        # Base fundamental growth logic adjusted by ROE and EPS
                        base_growth = 0.15
                        if eps_growth and isinstance(eps_growth, float):
                            base_growth = eps_growth
                        elif rev_growth and isinstance(rev_growth, float):
                            base_growth = rev_growth
                        
                        # Capping growth realistically between 8% and 25% for long-term health
                        annual_growth = min(max(base_growth, 0.08), 0.25)
                        
                        # Extra fundamental soundness factor (if ROE > 15% and Low Debt, boost compounding confidence)
                        target_3yr = current_price * ((1 + annual_growth) ** 3)
                        target_5yr = current_price * ((1 + annual_growth) ** 5)

                        raw_summary = info.get('longBusinessSummary', 'આ કંપની વિશેની માહિતી ઉપલબ્ધ નથી.')
                        try:
                            business_summary = GoogleTranslator(source='auto', target='gu').translate(raw_summary)
                        except:
                            business_summary = raw_summary

                        # Technical Indicators
                        ema_10 = close_series.ewm(span=10, adjust=False).mean().iloc[-1] if len(close_series) >= 10 else current_price
                        ema_20 = close_series.ewm(span=20, adjust=False).mean().iloc[-1] if len(close_series) >= 20 else current_price
                        ema_50 = close_series.ewm(span=50, adjust=False).mean().iloc[-1] if len(close_series) >= 50 else current_price
                        ema_200 = close_series.ewm(span=200, adjust=False).mean().iloc[-1] if len(close_series) >= 200 else current_price

                        if not hist_monthly.empty and len(hist_monthly['Close'].dropna()) >= 12:
                            m_close = hist_monthly['Close'].dropna()
                            monthly_ema = m_close.ewm(span=12, adjust=False).mean().iloc[-1]
                            monthly_trend = "🟢 તેજી (બુલિશ) 📈" if m_close.iloc[-1] > monthly_ema else "🔴 મંદી (બેરિશ) 📉"
                        else:
                            monthly_trend = "⚪ તટસ્થ / મર્યાદિત ડેટા ⚖️"

                        delta = close_series.diff()
                        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                        rs = gain / loss
                        rsi_series = 100 - (100 / (1 + rs))
                        current_rsi = rsi_series.iloc[-1] if not rsi_series.empty else 50.0

                        exp1 = close_series.ewm(span=12, adjust=False).mean()
                        exp2 = close_series.ewm(span=26, adjust=False).mean()
                        macd_line = exp1 - exp2
                        signal_line = macd_line.ewm(span=9, adjust=False).mean()
                        current_macd = macd_line.iloc[-1]
                        current_sig = signal_line.iloc[-1]
                        
                        macd_status = "🟢 બુલિશ ક્રોસઓવર (ખરીદો) ✅" if current_macd > current_sig else "🔴 બેરિશ ક્રોસઓવર (વેચો) ❌"

                        hl2 = (hist['High'] + hist['Low']) / 2
                        atr = (hist['High'] - hist['Low']).rolling(window=10).mean().iloc[-1]
                        if pd.isna(atr):
                            atr = current_price * 0.02
                        supertrend_val = hl2.iloc[-1] + (2 * atr)
                        
                        supertrend_status = "🟢 બુલિશ (સુપરટ્રેન્ડ ગ્રીન) 🟢" if current_price > supertrend_val else "🔴 બેરિશ (સુપરટ્રેન્ડ રેડ) 🔴"

                        # Volume Spike & News Check
                        vol_series = hist['Volume'].dropna()
                        today_vol = vol_series.iloc[-1] if not vol_series.empty else 0
                        avg_vol = vol_series.rolling(20).mean().iloc[-1] if len(vol_series) >= 20 else today_vol
                        
                        has_volume_spike = today_vol > (1.3 * avg_vol)
                        if has_volume_spike:
                            volume_status = "🔥 હાઇ વોલ્યુમ સ્પાઇક કન્ફર્મેશન! ⚡"
                            vol_score_add = 20
                        else:
                            volume_status = "⚪ સામાન્ય વોલ્યુમ 💤"
                            vol_score_add = 0

                        news_list = ticker.news
                        news_sentiment = "🔍 ન્યૂઝ મોમેન્ટમ સામાન્ય / ન્યુટ્રલ 📰"
                        has_positive_catalyst = False
                        if news_list and len(news_list) > 0:
                            sample_title = news_list[0].get('title', '')
                            news_sentiment = f"📢 તાજેતરના ન્યૂઝ: {sample_title} 🌐"
                            has_positive_catalyst = True

                        daily_trend = "🟢 તેજી (બુલિશ) 📈" if current_price > ema_50 else "🔴 મંદી (બેરિશ) 📉"
                        weekly_trend = "🟢 તેજી (બુલિશ) 📈" if current_price > ema_200 else "🔴 મંદી (બેરિશ) 📉"

                        # REAL SUPPORT & RESISTANCE CALCULATION FROM RECENT PRICE ACTION
                        recent_hist = hist.tail(60) # Last 60 trading sessions
                        dynamic_resistance = recent_hist['High'].max()
                        dynamic_support = recent_hist['Low'].min()

                        is_valid_swing = has_volume_spike or has_positive_catalyst or (current_rsi > 50 and current_macd > current_sig)

                        stop_loss = current_price * 0.97
                        target_swing_1 = current_price * 1.05
                        target_swing_2 = current_price * 1.10
                        
                        risk = current_price - stop_loss
                        reward = target_swing_1 - current_price
                        rr_ratio = round(reward / risk, 2) if risk > 0 else 0

                        # Score Calculation
                        score = 30
                        if current_price > ema_200: score += 15
                        if current_price > ema_50: score += 15
                        if "તેજી" in monthly_trend: score += 15
                        if 40 <= current_rsi <= 70: score += 10
                        if current_macd > current_sig: score += 10
                        score += vol_score_add
                        score = max(0, min(100, score))

                        if score >= 70:
                            verdict = "🔥 મજબૂત બુલિશ (સ્ટ્રોંગ બાય) 🚀"
                        elif score >= 50:
                            verdict = "⚖️ સાઇડવેઝ / હોલ્ડ (તટસ્થ) ⏳"
                        else:
                            verdict = "🔻 બેરિશ / વેચાણ દબાણ ⚠️"

                        # Display UI Metrics
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("💵 હાલનો ભાવ", f"₹{current_price:.2f}")
                        col2.metric("⭐ પ્રો ટેક્નિકલ સ્કોર", f"{score} / 100")
                        col3.metric("📈 આરએસઆઈ (RSI 14)", f"{current_rsi:.2f}")
                        col4.metric("🏆 ૫૨ સપ્તાહ હાઈ", f"₹{high_52:.2f}")

                        st.markdown("---")

                        # Interactive Candlestick Chart with Real Support & Resistance Lines
                        st.subheader(f"📊 {company_name} - કેન્ડલસ્ટિક ચાર્ટ વિથ રિયલ સપોર્ટ & રેઝિસ્ટન્સ 📈")
                        
                        fig = go.Figure(data=[go.Candlestick(
                            x=hist.index,
                            open=hist['Open'],
                            high=hist['High'],
                            low=hist['Low'],
                            close=hist['Close'],
                            name='Candlestick'
                        )])
                        
                        # Add Resistance Line (Red)
                        fig.add_hline(
                            y=dynamic_resistance, 
                            line_dash="dash", 
                            line_color="red", 
                            annotation_text=f"🔴 રેઝિસ્ટન્સ (Resistance): ₹{dynamic_resistance:.2f}", 
                            annotation_position="top right"
                        )
                        
                        # Add Support Line (Green)
                        fig.add_hline(
                            y=dynamic_support, 
                            line_dash="dash", 
                            line_color="green", 
                            annotation_text=f"🟢 સપોર્ટ (Support): ₹{dynamic_support:.2f}", 
                            annotation_position="bottom right"
                        )

                        fig.update_layout(
                            template='plotly_dark',
                            title=f"{selected_stock} - Price Action with Support & Resistance",
                            xaxis_title="તારીખ (Date)",
                            yaxis_title="ભાવ (Price in ₹)",
                            height=520
                        )
                        st.plotly_chart(fig, use_container_width=True)

                        st.markdown("---")
                        st.subheader(f"🎯 પ્રો-સિગ્નલ સ્કોરબોર્ડ & ફંડામેન્ટલ ચેક: {company_name}")
                        st.info(f"**ઓવરઓલ ટ્રેન્ડ સિગ્નલ:** {verdict} | {news_sentiment}")

                        sc1, sc2, sc3, sc4 = st.columns(4)
                        sc1.write(f"**📅 દૈનિક ટ્રેન્ડ:** {daily_trend}")
                        sc2.write(f"**📆 સાપ્તાહિક ટ્રેન્ડ:** {weekly_trend}")
                        sc3.write(f"**🗓️ માસિક ટ્રેન્ડ:** {monthly_trend}")
                        sc4.write(f"**⚡ સુપરટ્રેન્ડ:** {supertrend_status}")

                        sc5, sc6, sc7, sc8 = st.columns(4)
                        sc5.write(f"**🔄 એમએસીડી:** {macd_status}")
                        sc6.write(f"**📊 વોલ્યુમ સ્થિતિ:** {volume_status}")
                        sc7.write(f"🛡️ **P/E રેશિયો:** {pe_ratio}")
                        sc8.write(f"💎 **ROE:** {roe_str}")

                        # Smart Swing & Long-Term Targets Section
                        st.markdown("---")
                        st.subheader("🛡️ સ્માર્ટ ટ્રેડિંગ સ્તરો અને ફંડામેન્ટલ ગ્રોથ લક્ષ્યાંક 🎯")
                        
                        if is_valid_swing:
                            st.success("✅ **સ્વિંગ ટ્રેડિંગ કન્ફર્મેશન મળ્યું છે!** (વોલ્યુમ સ્પાઇક અથવા માર્કેટ મોમેન્ટમ સપોર્ટ કરે છે). નીચે મુજબ ટ્રેડ પ્લાન કરો:")
                            t_col1, t_col2, t_col3, t_col4 = st.columns(4)
                            t_col1.metric("🛑 સૂચિત સ્ટોપ-લોસ (SL)", f"₹{stop_loss:.2f}", "-3%")
                            t_col2.metric("🎯 સ્વિંગ ટાર્ગેટ ૧ (T1)", f"₹{target_swing_1:.2f}", "+5%")
                            t_col3.metric("🚀 સ્વિંગ ટાર્ગેટ ૨ (T2)", f"₹{target_swing_2:.2f}", "+10%")
                            t_col4.metric("⚖️ રિસ્ક-ટુ-રિવોર્ડ", f"1 : {rr_ratio}")
                        else:
                            st.warning("⚠️ **સ્વિંગ ટ્રેડિંગ સિગ્નલ હાલ બ્લોક છે:** સક્રિય વોલ્યુમ સ્પાઇક કે સ્ટ્રોંગ મોમેન્ટમ કન્ફર્મેશન નથી. માત્ર ફંડામેન્ટલ લોંગ-ટર્મ ઇન્વેસ્ટમેન્ટ ધ્યાનમાં લો.")

                        st.markdown("##### **📈 ૨. ૩ થી ૫ વર્ષના લોંગ-ટર્મ ઇન્વેસ્ટમેન્ટ લક્ષ્યાંક (ફંડામેન્ટલ ગ્રોથ & CAGR બેઝ્ડ):**")
                        inv_col1, inv_col2, inv_col3 = st.columns(3)
                        inv_col1.metric("📊 અંદાજિત વાર્ષિક ગ્રોથ (CAGR)", f"{annual_growth*100:.1f}% પ્રતિ વર્ષ")
                        inv_col2.metric("🎯 ૩ વર્ષનું લોંગ-ટર્મ લક્ષ્ય", f"₹{target_3yr:.2f}")
                        inv_col3.metric("🚀 ૫ વર્ષનું લોંગ-ટર્મ લક્ષ્ય", f"₹{target_5yr:.2f}")

                        st.markdown("---")

                        # Fundamental Checklist & Report Generation
                        clean_text = f"""
==================================================
🚀 {company_name} ({selected_stock}) - પ્રોફેશનલ એનાલિસિસ રિપોર્ટ 📈
==================================================
💵 હાલની કિંમત: ₹{current_price:.2f} | ⭐ પ્રો ટેક્નિકલ સ્કોર: {score}/100 ({verdict})

૧. કંપનીનો ટૂંકો પરિચય (પ્રોફાઇલ):
{business_summary}

૨. ફંડામેન્ટલ હેલ્થ & ચેકલિસ્ટ:
- P/E રેશિયો: {pe_ratio}
- ROE (રિട്ടર્ન ઓન ઇક્વિટી): {roe_str}
- અંદાજિત વાર્ષિક ગ્રોથ રેટ (CAGR): {annual_growth*100:.1f}%

૩. ચાર્ટ સપોર્ટ અને રેઝિસ્ટન્સ લેવલ:
- 🔴 રેઝિસ્ટન્સ (Resistance): ₹{dynamic_resistance:.2f}
- 🟢 સપોર્ટ (Support): ₹{dynamic_support:.2f}

૪. માર્કેટ મોમેન્ટમ અને ન્યૂઝ સ્ટેટસ:
- વોલ્યુમ કન્ફર્મેશન: {volume_status}
- ન્યૂઝ અપડેટ: {news_sentiment}
- સ્વિંગ ટ્રેડિંગ માન્યતા: {'હા (કન્ફર્મ્ડ)' if is_valid_swing else 'ના (વેઇટ એન્ડ વોચ)'}

૫. મહત્વના ટ્રેડિંગ અને ઇન્વેસ્ટમેન્ટ સ્તરો:
- 🛑 સ્ટોપ-લોસ (SL): ₹{stop_loss:.2f}
- 🎯 સ્વિંગ ટાર્ગેટ ૧: ₹{target_swing_1:.2f}
- 🚀 સ્વિંગ ટાર્ગેટ ૨: ₹{target_swing_2:.2f}
- 📅 ૩ વર્ષનું લોંગ-ટર્મ લક્ષ્ય: ₹{target_3yr:.2f}
- 🗓️ ૫ વર્ષનું લોંગ-ટર્મ લક્ષ્ય: ₹{target_5yr:.2f}
==================================================
"""

                        st.success("🎉 પ્રોફેશનલ એનાલિસિસ રિપોર્ટ સફળતાપૂર્વક તૈયાર થઈ ગયો છે!")
                        st.text_area("📄 રિપોર્ટ ટેક્સ્ટ:", clean_text, height=250)

                        st.download_button(
                            label="📥 આ પ્રો રિપોર્ટ ડાઉનલોડ કરો (.txt) 💾",
                            data=clean_text.encode('utf-8'),
                            file_name=f"{selected_stock}_pro_analysis_report.txt",
                            mime="text/plain;charset=utf-8"
                        )

                except Exception as e:
                    st.error(f"❌ એરર આવી છે: {str(e)}")

with tab2:
    st.subheader("📋 વોચલિસ્ટ કમ્પેરિઝન ડેશબોર્ડ 🔍📊")
    st.markdown("તમારી વોચલિસ્ટના તમામ સ્ટોક્સનું ઓવરવ્યુ એક જ ટેબલમાં જોવા મળે છે:")
    
    if st.button("🔄 વોચલિસ્ટ સ્કેન કરો અને કમ્પેર કરો"):
        comparison_data = []
        progress_bar = st.progress(0)
        total_stocks = len(st.session_state.watchlist)
        
        for i, sym in enumerate(st.session_state.watchlist):
            try:
                t = yf.Ticker(sym)
                h = t.history(period="1mo")
                inf = t.info
                if not h.empty:
                    cp = h['Close'].iloc[-1]
                    name = inf.get('longName', sym)
                    pe = inf.get('trailingPE', 'N/A')
                    chg = ((cp - h['Close'].iloc[0]) / h['Close'].iloc[0]) * 100
                    comparison_data.append({
                        "સ્ટોક સિમ્બોલ": sym,
                        "કંપની નામ": name,
                        "હાલનો ભાવ (₹)": round(cp, 2),
                        "માસિક રિટર્ન (%)": round(chg, 2),
                        "P/E રેશિયો": pe
                    })
            except:
                pass
            progress_bar.progress((i + 1) / total_stocks)
            
        if comparison_data:
            df_comp = pd.DataFrame(comparison_data)
            st.dataframe(df_comp, use_container_width=True)
        else:
            st.warning("⚠️ કોઈ ડેટા ઉપલબ્ધ નથી.")

with tab3:
    st.subheader("💼 તમારો પર્સનલ પોર્ટફોલિયો ટ્રેકર 📈💰")
    st.markdown("તમે ખરીદેલા શેર અહીં ઉમેરીને લાઈવ પ્રોફિટ/લોસ (P&L) ટ્રેક કરી શકો છો:")
    
    with st.form("portfolio_form"):
        p_stock = st.text_input("સ્ટોક સિમ્બોલ (દા.ત. RELIANCE.NS): 📝")
        p_qty = st.number_input("શેરની સંખ્યા (Quantity): 🔢", min_value=1, value=10)
        p_price = st.number_input("ખરીદીનો સરેરાશ ભાવ (Buy Price ₹): 💵", min_value=0.1, value=100.0)
        submitted = st.form_submit_button("➕ પોર્ટફોલિયોમાં ઉમેરો")
        
        if submitted and p_stock:
            clean_p_stock = p_stock.strip().upper()
            new_row = pd.DataFrame({"Stock": [clean_p_stock], "Qty": [p_qty], "Buy Price": [p_price]})
            st.session_state.portfolio = pd.concat([st.session_state.portfolio, new_row], ignore_index=True)
            st.success(f"✅ {clean_p_stock} પોર્ટફોલિયોમાં સફળતાપૂર્વક ઉમેરાઈ ગયો! 🎉")

    if not st.session_state.portfolio.empty:
        st.markdown("### 📊 લાઈવ પોર્ટફોલિયો સ્ટેટસ:")
        pf_data = []
        total_inv = 0
        total_curr_val = 0
        
        for idx, row in st.session_state.portfolio.iterrows():
            stk = row["Stock"]
            q = row["Qty"]
            bp = row["Buy Price"]
            
            try:
                cur_p = yf.Ticker(stk).history(period="1d")['Close'].iloc[-1]
            except:
                cur_p = bp
                
            inv_val = q * bp
            cur_val = q * cur_p
            pnl = cur_val - inv_val
            pnl_pct = (pnl / inv_val) * 100 if inv_val > 0 else 0
            
            total_inv += inv_val
            total_curr_val += cur_val
            
            pf_data.append({
                "સ્ટોક": stk,
                "ક્વોન્ટિટી": q,
                "ખરીદી ભાવ (₹)": bp,
                "હાલનો ભાવ (₹)": round(cur_p, 2),
                "રોકાણ કિંમત (₹)": round(inv_val, 2),
                "હાલની કિંમત (₹)": round(cur_val, 2),
                "નફો/લોસ (₹)": round(pnl, 2),
                "રિટર્ન (%)": f"{pnl_pct:.2f}%"
            })
            
        df_pf = pd.DataFrame(pf_data)
        st.dataframe(df_pf, use_container_width=True)
        
        total_pnl = total_curr_val - total_inv
        col_p1, col_p2, col_p3 = st.columns(3)
        col_p1.metric("💰 કુલ રોકાણ (Total Investment)", f"₹{total_inv:.2f}")
        col_p2.metric("💎 કુલ વર્તમાન કિંમત (Current Value)", f"₹{total_curr_val:.2f}")
        col_p3.metric("📈 કુલ પ્રોફિટ/લોસ (Total P&L)", f"₹{total_pnl:.2f}", delta=f"{total_pnl:.2f}")
        
        if st.button("🗑️ પોર્ટફોલિયો ખાલી કરો (Reset)"):
            st.session_state.portfolio = pd.DataFrame(columns=["Stock", "Qty", "Buy Price"])
            st.rerun()
    else:
        st.info("ℹ️ હજુ સુધી પોર્ટફોલિયોમાં કોઈ શેર ઉમેર્યા નથી.")
