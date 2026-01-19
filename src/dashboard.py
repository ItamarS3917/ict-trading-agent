"""
Streamlit Dashboard for ICT Trading Agent

Interactive web-based dashboard for visualizing trading signals,
market analysis, and backtesting results.
"""

import logging
import sys
from datetime import datetime, timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

# Add src to path
sys.path.insert(0, ".")

from backtester import Backtester
from data_handler import DataHandler
from ict_agent import ICTTradingAgent
from utils.config_loader import ConfigLoader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="ICT Trading Agent | Professional Analysis Suite",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Professional CSS for Trading Terminal Aesthetic
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --bg-main: #0e1117;
        --bg-secondary: #161b22;
        --border-color: #30363d;
        --text-primary: #e6edf3;
        --text-secondary: #8b949e;
        --trading-green: #26a69a;
        --trading-red: #ef5350;
        --accent-blue: #58a6ff;
    }

    .stApp {
        background-color: var(--bg-main);
        color: var(--text-primary);
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: var(--bg-secondary);
        border-right: 1px solid var(--border-color);
    }

    /* Header Styling */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.5px;
    }

    /* Professional Metric Cards */
    [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 600 !important;
        font-size: 1.8rem !important;
    }

    [data-testid="stMetricLabel"] {
        text-transform: uppercase;
        letter-spacing: 1px;
        color: var(--text-secondary) !important;
        font-size: 0.75rem !important;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        border-bottom: 1px solid var(--border-color);
    }

    .stTabs [data-baseweb="tab"] {
        color: var(--text-secondary);
        padding: 0.75rem 1.5rem;
    }

    .stTabs [aria-selected="true"] {
        color: var(--accent-blue) !important;
        border-bottom: 2px solid var(--accent-blue) !important;
    }

    /* Signal Containers */
    .signal-container {
        border: 1px solid var(--border-color);
        border-radius: 6px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        background-color: var(--bg-secondary);
    }

    .status-badge {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 500;
    }

    /* Hide Streamlit elements */
    footer {visibility: hidden;}
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource
def load_config():
    """Load configuration."""
    config_loader = ConfigLoader()
    return config_loader.load()


@st.cache_data(ttl=300)
def load_data(symbol: str, period: str, interval: str):
    """Load market data with caching."""
    data_handler = DataHandler()
    df = data_handler.get_price_data(symbol, period=period, interval=interval)
    return df


def plot_price_chart(df: pd.DataFrame, fvgs=None, order_blocks=None):
    """Create professional price chart with ICT patterns."""
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        row_heights=[0.8, 0.2],
    )

    # Professional Trading Layout
    trading_layout = {
        "plot_bgcolor": "#161b22",
        "paper_bgcolor": "#0e1117",
        "font": {"color": "#e6edf3", "family": "Inter"},
        "xaxis": {"gridcolor": "#30363d", "showline": True, "linecolor": "#30363d"},
        "yaxis": {
            "gridcolor": "#30363d",
            "showline": True,
            "linecolor": "#30363d",
            "side": "right",
        },
        "xaxis2": {"gridcolor": "#30363d", "showline": True, "linecolor": "#30363d"},
        "yaxis2": {
            "gridcolor": "#30363d",
            "showline": True,
            "linecolor": "#30363d",
            "side": "right",
        },
    }

    # Candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Price",
            increasing_line_color="#26a69a",
            decreasing_line_color="#ef5350",
            increasing_fillcolor="#26a69a",
            decreasing_fillcolor="#ef5350",
        ),
        row=1,
        col=1,
    )

    # Fair Value Gaps - Semi-transparent zones
    if fvgs:
        for fvg in fvgs[:10]:
            is_bullish = fvg["direction"] == "BULLISH"
            color = "#26a69a" if is_bullish else "#ef5350"
            fig.add_hrect(
                y0=fvg["gap_low"],
                y1=fvg["gap_high"],
                fillcolor=color,
                opacity=0.1,
                line_width=0,
                row=1,
                col=1,
            )

    # Order Blocks - Distinguished zones
    if order_blocks:
        for ob in order_blocks[:10]:
            is_bullish = ob["direction"] == "BULLISH"
            color = "#58a6ff" if is_bullish else "#bc85ff"
            fig.add_hrect(
                y0=ob["block_low"],
                y1=ob["block_high"],
                fillcolor=color,
                opacity=0.15,
                line_width=1,
                line_color=color,
                line_dash="dash",
                row=1,
                col=1,
            )

    # Volume bars
    colors = [
        "#ef5350" if df["Close"].iloc[i] < df["Open"].iloc[i] else "#26a69a" for i in range(len(df))
    ]

    fig.add_trace(
        go.Bar(x=df.index, y=df["Volume"], name="Volume", marker_color=colors, opacity=0.7),
        row=2,
        col=1,
    )

    fig.update_layout(
        **trading_layout,
        height=750,
        xaxis_rangeslider_visible=False,
        showlegend=False,
        margin={"l": 0, "r": 50, "t": 10, "b": 0},
        hovermode="x unified",
    )

    return fig


def plot_backtest_results(results: dict):
    """Plot backtest results with professional equity curve."""
    if "equity_curve" not in results or not results["equity_curve"]:
        st.warning("No equity curve data available")
        return

    equity_df = pd.DataFrame(results["equity_curve"])

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=equity_df["date"],
            y=equity_df["equity"],
            mode="lines",
            name="Equity",
            line={"color": "#58a6ff", "width": 2},
            fill="tozeroy",
            fillcolor="rgba(88, 166, 255, 0.05)",
        )
    )

    # Baseline
    fig.add_hline(
        y=results["initial_capital"],
        line_dash="dot",
        line_color="#8b949e",
        annotation_text="Principal",
        annotation_font_color="#8b949e",
    )

    fig.update_layout(
        plot_bgcolor="#161b22",
        paper_bgcolor="#0e1117",
        font={"color": "#e6edf3", "family": "Inter"},
        xaxis={"gridcolor": "#30363d", "title": ""},
        yaxis={"gridcolor": "#30363d", "title": "Capital ($)", "side": "right"},
        height=400,
        margin={"l": 0, "r": 50, "t": 20, "b": 0},
        hovermode="x unified",
    )

    return fig


def main():
    """Main dashboard application - Professional Suite."""

    # Clean Header
    st.markdown(
        """
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 2rem; border-bottom: 1px solid var(--border-color); padding-bottom: 1rem;">
            <div>
                <h1 style="margin: 0; padding: 0; font-size: 2rem;">ICT Trading Agent</h1>
                <p style="margin: 0; padding: 0; color: var(--text-secondary); font-size: 0.85rem; font-weight: 500;">Advanced Algorithmic Analysis Suite</p>
            </div>
            <div style="text-align: right;">
                <div style="color: var(--trading-green); font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; font-weight: 500;">● SYSTEM CONNECTED</div>
                <div style="color: var(--text-secondary); font-size: 0.75rem;">Terminal v1.0.4</div>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # Sidebar
    st.sidebar.title("⚙️ Configuration")

    config = load_config()

    # Symbol selection
    symbol = st.sidebar.text_input(
        "Trading Symbol", value=config.get("trading", {}).get("symbol", "NQ=F")
    )

    # Timeframe selection
    timeframe_options = ["1m", "5m", "15m", "30m", "1h", "4h", "1d"]
    timeframe = st.sidebar.selectbox(
        "Timeframe",
        options=timeframe_options,
        index=timeframe_options.index(config.get("trading", {}).get("timeframe", "1h")),
    )

    # Period selection
    period_options = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y"]
    period = st.sidebar.selectbox(
        "Period",
        options=period_options,
        index=2,  # Default to 1mo
    )

    # Refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

    st.sidebar.markdown("---")

    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📈 Live Analysis", "🧪 Backtesting", "📊 Patterns", "⚙️ Settings"]
    )

    # Tab 1: Live Analysis
    with tab1:
        st.subheader("Market Overview")

        with st.spinner("Fetching market data..."):
            df = load_data(symbol, period, timeframe)

        if df.empty:
            st.error(f"No data available for {symbol}")
            return

        # Market Metrics
        current_price = df["Close"].iloc[-1]
        price_change = df["Close"].iloc[-1] - df["Close"].iloc[-2]
        price_change_pct = (price_change / df["Close"].iloc[-2]) * 100

        m1, m2, m3, m4 = st.columns(4)

        with m1:
            st.metric(
                label="Price",
                value=f"${current_price:,.2f}",
                delta=f"{price_change:+.2f} ({price_change_pct:+.2f}%)",
            )

        with m2:
            st.metric("High (24h)", f"${df['High'].iloc[-24:].max():,.2f}")

        with m3:
            st.metric("Low (24h)", f"${df['Low'].iloc[-24:].min():,.2f}")

        with m4:
            st.metric("Volume", f"{df['Volume'].iloc[-1]:,.0f}")

        # Analysis Logic
        with st.spinner("Analyzing ICT patterns..."):
            agent = ICTTradingAgent(config)
            fvgs = agent.detect_fair_value_gaps(symbol)
            order_blocks = agent.detect_order_blocks(symbol)
            market_structure = agent.analyze_market_structure(symbol)
            signals = agent.generate_signals(symbol)

        # Main Chart Area
        st.plotly_chart(plot_price_chart(df, fvgs, order_blocks), use_container_width=True)

        # Market Information
        st.subheader("Market Intelligence")
        col_info1, col_info2 = st.columns(2)

        with col_info1:
            trend = market_structure.get("trend_direction", "UNKNOWN")
            trend_color = (
                "var(--trading-green)"
                if trend == "UPTREND"
                else "var(--trading-red)"
                if trend == "DOWNTREND"
                else "var(--text-secondary)"
            )
            st.markdown(
                f"""
            <div class="signal-container">
                <div style="color: var(--text-secondary); font-size: 0.7rem; margin-bottom: 0.4rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Market Trend</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: {trend_color};">
                    {trend} {"↑" if trend == "UPTREND" else "↓" if trend == "DOWNTREND" else "→"}
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col_info2:
            st.markdown(
                f"""
            <div class="signal-container">
                <div style="color: var(--text-secondary); font-size: 0.7rem; margin-bottom: 0.4rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Pattern Confluence</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: var(--accent-blue);">
                    {len(fvgs)} FVGs • {len(order_blocks)} Order Blocks
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        # Trading Signals
        st.subheader("Alert Command")

        if signals:
            for signal in signals[:3]:
                is_long = signal["direction"] in ["LONG", "BULLISH"]
                sig_color = "var(--trading-green)" if is_long else "var(--trading-red)"
                sig_bg = "rgba(38, 166, 154, 0.05)" if is_long else "rgba(239, 83, 80, 0.05)"

                st.markdown(
                    f"""
                <div style="background: {sig_bg}; border: 1px solid {sig_color}33; padding: 1.25rem; border-radius: 6px; margin-bottom: 0.75rem; border-left: 4px solid {sig_color};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="color: {sig_color}; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">{signal["type"]}</span>
                            <span style="color: var(--text-secondary); margin-left: 12px; font-size: 0.9rem;">{signal["pattern"]}</span>
                        </div>
                        <div style="font-family: 'JetBrains Mono'; color: {sig_color}; font-weight: 600;">CONFIDENCE: {signal["strength"]:.1%}</div>
                    </div>
                    <div style="margin-top: 15px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px;">
                        <div><div style="color: var(--text-secondary); font-size: 0.7rem; text-transform: uppercase;">Entry</div><div style="font-weight: 600; font-family: 'JetBrains Mono'; font-size: 1.1rem;">${signal["price"]:.2f}</div></div>
                        <div><div style="color: var(--text-secondary); font-size: 0.7rem; text-transform: uppercase;">Stop Loss</div><div style="font-weight: 600; font-family: 'JetBrains Mono'; color: var(--trading-red); font-size: 1.1rem;">${signal["stop_loss"]:.2f}</div></div>
                        <div><div style="color: var(--text-secondary); font-size: 0.7rem; text-transform: uppercase;">Target</div><div style="font-weight: 600; font-family: 'JetBrains Mono'; color: var(--trading-green); font-size: 1.1rem;">${signal["take_profit"]:.2f}</div></div>
                        <div><div style="color: var(--text-secondary); font-size: 0.7rem; text-transform: uppercase;">R/R Ratio</div><div style="font-weight: 600; font-family: 'JetBrains Mono'; font-size: 1.1rem;">{(abs(signal["take_profit"] - signal["price"]) / abs(signal["price"] - signal["stop_loss"]) if abs(signal["price"] - signal["stop_loss"]) > 0 else 0):.2f}</div></div>
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("Market neutral. No high-confidence signals currently detected.")

    # Tab 2: Backtesting
    with tab2:
        st.markdown("### 🧪 Simulation Protocol")

        col1, col2, col3 = st.columns(3)

        with col1:
            start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=365))

        with col2:
            end_date = st.date_input("End Date", value=datetime.now())

        with col3:
            initial_capital = st.number_input(
                "Initial Capital ($)", min_value=1000, max_value=1000000, value=10000, step=1000
            )

        if st.button("🧪 Run Backtest", type="primary"):
            with st.spinner("Running backtest... This may take a while."):
                backtester = Backtester(
                    initial_capital=initial_capital,
                    commission=config.get("backtesting", {}).get("commission", 2.0),
                    slippage=config.get("backtesting", {}).get("slippage", 0.001),
                )

                results = backtester.run_backtest(
                    symbol=symbol,
                    start_date=start_date.strftime("%Y-%m-%d"),
                    end_date=end_date.strftime("%Y-%m-%d"),
                )

                if "error" not in results:
                    st.success("Strategy Simulation Complete")

                    # Professional Metrics Display
                    m_col1, m_col2, m_col3, m_col4 = st.columns(4)

                    with m_col1:
                        st.metric(
                            "Total Return",
                            f"{results['total_return']:.2%}",
                            delta=f"${results['final_capital'] - results['initial_capital']:,.2f}",
                        )

                    with m_col2:
                        st.metric("Win Rate", f"{results['win_rate']:.2%}")

                    with m_col3:
                        st.metric("Sharpe Ratio", f"{results['sharpe_ratio']:.2f}")

                    with m_col4:
                        st.metric("Max Drawdown", f"{results['max_drawdown']:.2%}")

                    # Equity curve
                    st.plotly_chart(plot_backtest_results(results), use_container_width=True)

                    # Trade statistics
                    st.subheader("Trade Statistics")
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Total Trades", results["total_trades"])
                    with col2:
                        st.metric("Winning Trades", results["winning_trades"])
                    with col3:
                        st.metric("Losing Trades", results["losing_trades"])

                    # Full report
                    with st.expander("📄 View Full Report"):
                        report = backtester.generate_report(results)
                        st.text(report)

                    # Trade history
                    if results.get("trades"):
                        st.subheader("Trade History")
                        trades_df = pd.DataFrame(results["trades"])
                        st.dataframe(trades_df, use_container_width=True)
                else:
                    st.error(results["error"])

    # Tab 3: Patterns
    with tab3:
        st.subheader("Pattern Recognition Analysis")

        df = load_data(symbol, period, timeframe)

        if not df.empty:
            agent = ICTTradingAgent(config)

            col_p1, col_p2 = st.columns(2)

            with col_p1:
                st.markdown("#### Fair Value Gaps (FVG)")
                fvgs = agent.detect_fair_value_gaps(symbol)

                if fvgs:
                    for i, fvg in enumerate(fvgs[:10], 1):
                        is_bull = fvg["direction"] == "BULLISH"
                        sig_color = "var(--trading-green)" if is_bull else "var(--trading-red)"
                        st.markdown(
                            f"""
                        <div class="signal-container" style="border-left: 3px solid {sig_color};">
                            <div style="display: flex; justify-content: space-between; align-items: baseline;">
                                <span style="color: {sig_color}; font-weight: 700; font-size: 0.9rem;">FVG NODE #{i:02d}</span>
                                <span style="color: var(--text-secondary); font-size: 0.75rem; font-family: 'JetBrains Mono';">{fvg["timestamp"]}</span>
                            </div>
                            <div style="margin-top: 12px; display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                                <div><div style="color: var(--text-secondary); font-size: 0.65rem; text-transform: uppercase;">Gap Magnitude</div><div style="font-weight: 500; font-family: 'JetBrains Mono';">{fvg["gap_size"]:.4%}</div></div>
                                <div><div style="color: var(--text-secondary); font-size: 0.65rem; text-transform: uppercase;">Confidence Score</div><div style="font-weight: 500; font-family: 'JetBrains Mono'; color: var(--accent-blue);">{fvg["strength"]:.2%}</div></div>
                            </div>
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )
                else:
                    st.info("No ICT Fair Value Gaps identified in the current period.")

            with col_p2:
                st.markdown("#### Order Block Analysis")
                order_blocks = agent.detect_order_blocks(symbol)

                if order_blocks:
                    for i, ob in enumerate(order_blocks[:10], 1):
                        is_bull = ob["direction"] == "BULLISH"
                        sig_color = "var(--accent-blue)" if is_bull else "#bc85ff"
                        st.markdown(
                            f"""
                        <div class="signal-container" style="border-left: 3px solid {sig_color};">
                            <div style="display: flex; justify-content: space-between; align-items: baseline;">
                                <span style="color: {sig_color}; font-weight: 700; font-size: 0.9rem;">ORDER BLOCK #{i:02d}</span>
                                <span style="color: var(--text-secondary); font-size: 0.75rem; font-family: 'JetBrains Mono';">{ob["timestamp"]}</span>
                            </div>
                            <div style="margin-top: 12px; display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                                <div><div style="color: var(--text-secondary); font-size: 0.65rem; text-transform: uppercase;">Price Range</div><div style="font-weight: 500; font-family: 'JetBrains Mono';">${ob["block_low"]:.2f} - ${ob["block_high"]:.2f}</div></div>
                                <div><div style="color: var(--text-secondary); font-size: 0.65rem; text-transform: uppercase;">Efficiency Rating</div><div style="font-weight: 500; font-family: 'JetBrains Mono'; color: var(--accent-blue);">{ob["strength"]:.2%}</div></div>
                            </div>
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )
                else:
                    st.info("No institutional Order Blocks identified in the current period.")

    # Tab 4: Settings
    with tab4:
        st.header("Configuration Settings")

        st.subheader("Trading Parameters")

        col1, col2 = st.columns(2)

        with col1:
            st.number_input(
                "Lookback Period",
                min_value=10,
                max_value=500,
                value=config.get("trading", {}).get("lookback_period", 100),
            )

            st.number_input(
                "FVG Min Size (%)",
                min_value=0.001,
                max_value=1.0,
                value=config.get("patterns", {}).get("fvg_min_size", 0.001),
                format="%.3f",
            )

        with col2:
            st.number_input(
                "Order Block Strength",
                min_value=1,
                max_value=10,
                value=config.get("patterns", {}).get("orderblock_strength", 3),
            )

            st.number_input(
                "Risk Per Trade (%)",
                min_value=0.01,
                max_value=10.0,
                value=config.get("risk", {}).get("risk_per_trade", 0.02) * 100,
                format="%.2f",
            ) / 100

        st.subheader("Notification Settings")

        st.checkbox("Enable Notifications", value=config.get("alerts", {}).get("enabled", True))

        st.text_input(
            "Webhook URL (Discord/Slack)",
            value=config.get("alerts", {}).get("webhook_url", ""),
            type="password",
        )

        st.info("💡 Configure webhook notifications for real-time trading alerts")

    # Footer
    st.markdown(
        """
        <div style="margin-top: 5rem; padding: 2rem 0; border-top: 1px solid var(--border-color); text-align: left; display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <div style="font-weight: 700; color: var(--text-primary); font-size: 0.9rem;">ICT TRADING AGENT</div>
                <div style="color: var(--text-secondary); font-size: 0.75rem; margin-top: 0.25rem;">
                    Advanced Algorithmic Analysis & Strategy Backtesting
                </div>
            </div>
            <div style="text-align: right; color: var(--text-secondary); font-size: 0.7rem;">
                © 2026 PROFESSIONAL SUITE • MIT LICENSE<br>
                BUILT WITH STREAMLIT & PLOTLY
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
