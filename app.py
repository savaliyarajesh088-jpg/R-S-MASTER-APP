import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Page Config
st.set_page_config(page_title="R S MASTER APP - Breakout & Swing", layout="wide", page_icon="📈")

# Custom UI Styling
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .exit-card {
        background-color: #1e2430;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #2d3748;
        margin-bottom: 20px;
    }
    .badge-add { background-color: #10B981; color: white; padding: 6px 14px; border-radius: 6px; font-weight: bold; }
    .badge-hold { background-color: #3B82F6; color: white; padding: 6px 14px; border-radius: 6px; font-weight: bold; }
    .badge-replace { background-color: #F59E0B; color: white; padding: 6px 14px; border-radius: 6px; font-weight: bold; }
    .badge-exit { background-color: #EF4444; color: white; padding: 6px 14px; border-radius: 6px; font-weight: bold; }
    .breakout-badge { background-color: #8B5CF6; color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("📈 R S MASTER APP - Swing Breakout & ExitMantra")

# Default Watchlist
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = [
        "RELIANCE.NS", "TATAMOTORS.NS", "TCS.NS", "INFY.NS", 
        "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "BHARTIARTL.NS"
    ]

# Sidebar Manager
st.sidebar.header("⚙️ Watchlist Manager")
new_stock = st.sidebar.text_input("Add Stock Ticker (e.g. WIPRO.NS):")
if st.sidebar.button("➕ Add Stock"):
    if new_stock and new_stock.upper() not in st.session_state.watchlist:
        st.session_state.watchlist.append(new_stock.upper())
        st.sidebar.success(f"{new_stock.upper()} Added!")
        st.rerun()

stock_to_remove = st.sidebar.selectbox("Remove Stock:", st.session_state.watchlist)
if st.sidebar.button("🗑️ Delete Stock"):
    if stock_to_remove in st.session_state.watchlist:
        st.session_state.watchlist.remove(stock_to_remove)
        st.sidebar.warning(f"{stock_to_remove} Removed!")
        st.rerun()

selected_stock = st.selectbox("🎯 Select Stock for Breakout & Swing Analysis:", st.session_state.watchlist)

if selected_stock:
    df = yf.download(selected_stock, period="1y", interval="1d", progress=False)
    
    if not df.empty:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        current_price = float(df['Close'].iloc[-1])
        prev_close = float(df['Close'].iloc[-2])
        high_20 = float(df['High'].iloc[-21:-1].max()) # 20 Days High
        high_52 = float(df['High'].max())               # 52 Week High
        
        # Moving Averages & Volume
        ema_20 = float(df['Close'].ewm(span=20, adjust=False).mean().iloc[-1])
        ema_50 = float(df['Close'].ewm(span=50, adjust=False).mean().iloc[-1])
        vol_avg_20 = float(df['Volume'].iloc[-21:-1].mean())
        curr_vol = float(df['Volume'].iloc[-1])

        # --- Breakout & Momentum Logic ---
        is_breakout_20d = current_price > high_20
        is_vol_breakout = curr_vol > vol_avg_20
        is_near_52w_high = (current_price / high_52) >= 0.95

        # Swing Targets (6% to 15%)
        target_6pct = current_price * 1.06
        target_10pct = current_price * 1.10
        target_15pct = current_price * 1.15
        stop_loss = round(min(ema_20, current_price * 0.95), 2) # 5% SL or EMA20 Support

        # --- ExitMantra 3 Pillars Logic ---
        pillar1_breakout = True if (is_breakout_20d or is_near_52w_high) else False
        pillar2_momentum = True if (current_price > ema_50 and is_vol_breakout) else False
        pillar3_exitprice = True if (current_price > stop_loss) else False

        score = sum([pillar1_breakout, pillar2_momentum, pillar3_exitprice])

        # Signal & Rating Setup
        if score == 3:
            zone = "Bull Zone"
            signal = "ADD (STRONG BUY)"
            badge_class = "badge-add"
        elif score == 2:
            zone = "Bull Zone"
            signal = "HOLD / WATCH"
            badge_class = "badge-hold"
        elif score == 1:
            zone = "Pig Zone"
            signal = "REPLACE"
            badge_class = "badge-replace"
        else:
            zone = "Bear Zone"
            signal = "EXIT / AVOID"
            badge_class = "badge-exit"

        # --- DISPLAY BREAKOUT & EXITMANTRA CARD ---
        st.markdown("---")
        
        # Breakout Banner
        if is_breakout_20d and is_vol_breakout:
            st.success("🔥 **STRONG BREAKOUT DETECTED!** Price crossed 20-day High with High Volume.")
        elif is_breakout_20d:
            st.info("⚡ **PRICE BREAKOUT:** Price crossed 20-day High level.")

        st.markdown(f"""
        <div class="exit-card">
            <h2>{selected_stock.replace('.NS', '')} 
                {'<span class="breakout-badge">🚀 BREAKOUT</span>' if is_breakout_20d else ''}
            </h2>
            <h3>Current Price: ₹{current_price:.2f} | Stop Loss (SL): ₹{stop_loss:.2f}</h3>
            <p><b>ZONE:</b> {zone} | <b>SCORE:</b> {score} / 3 | <b>RATING:</b> <span class="{badge_class}">{signal}</span></p>
            <hr style="border-color:#374151;">
            <p>{'✅' if pillar1_breakout else '❌'} <b>Breakout / ATH Strength:</b> {'Yes (Breakout / Near High)' if pillar1_breakout else 'No'}</p>
            <p>{'✅' if pillar2_momentum else '❌'} <b>Outperformance & Volume Momentum:</b> {'Yes (Volume Surge & Above EMA50)' if pillar2_momentum else 'No'}</p>
            <p>{'✅' if pillar3_exitprice else '❌'} <b>Above Exit Price (Technicals):</b> {'Yes (Above Support Level)' if pillar3_exitprice else 'No'}</p>
        </div>
        """, unsafe_allow_html=True)

        # --- SWING TARGETS DISPLAY BOARD ---
        st.subheader("🎯 Swing Trade Targets (6% to 15%)")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🛑 Stop Loss (5%)", f"₹{stop_loss:.2f}")
        c2.metric("🎯 Target 1 (6%)", f"₹{target_6pct:.2f}")
        c3.metric("🎯 Target 2 (10%)", f"₹{target_10pct:.2f}")
        c4.metric("🚀 Target 3 (15%)", f"₹{target_15pct:.2f}")

        # Charts
        st.markdown("### 📊 Price & Volume Chart")
        st.line_chart(df[['Close']])

st.markdown("---")
st.caption("Powered by R S MASTER APP | Swing Breakout & ExitMantra Engine")
