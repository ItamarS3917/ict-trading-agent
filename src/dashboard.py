"""
Streamlit Dashboard for ICT Trading Agent

Interactive web-based dashboard for visualizing trading signals,
market analysis, and backtesting results.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from datetime import datetime, timedelta
import logging

# Add src to path
sys.path.insert(0, '.')

from ict_agent import ICTTradingAgent
from data_handler import DataHandler
from backtester import Backtester
from utils.config_loader import ConfigLoader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="ICT Trading Agent Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stAlert {
        padding: 1rem;
        margin: 1rem 0;
    }
    h1 {
        color: #1f77b4;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


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
    """Create interactive price chart with patterns."""
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=('Price Chart', 'Volume'),
        row_heights=[0.7, 0.3]
    )
    
    # Candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Price'
        ),
        row=1, col=1
    )
    
    # Fair Value Gaps
    if fvgs:
        for fvg in fvgs[:5]:  # Show top 5 FVGs
            color = 'green' if fvg['direction'] == 'BULLISH' else 'red'
            fig.add_hrect(
                y0=fvg['gap_low'],
                y1=fvg['gap_high'],
                fillcolor=color,
                opacity=0.2,
                line_width=0,
                row=1, col=1
            )
    
    # Order Blocks
    if order_blocks:
        for ob in order_blocks[:5]:  # Show top 5 OBs
            color = 'lightgreen' if ob['direction'] == 'BULLISH' else 'lightcoral'
            fig.add_hrect(
                y0=ob['block_low'],
                y1=ob['block_high'],
                fillcolor=color,
                opacity=0.3,
                line_width=1,
                row=1, col=1
            )
    
    # Volume bars
    colors = ['red' if df['Close'].iloc[i] < df['Open'].iloc[i] else 'green' 
              for i in range(len(df))]
    
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df['Volume'],
            name='Volume',
            marker_color=colors,
            showlegend=False
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        title='Market Analysis',
        yaxis_title='Price',
        xaxis_rangeslider_visible=False,
        height=600,
        showlegend=True,
        hovermode='x unified'
    )
    
    return fig


def plot_backtest_results(results: dict):
    """Plot backtest results."""
    if 'equity_curve' not in results or not results['equity_curve']:
        st.warning("No equity curve data available")
        return
    
    equity_df = pd.DataFrame(results['equity_curve'])
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=equity_df['date'],
        y=equity_df['equity'],
        mode='lines',
        name='Equity',
        line=dict(color='blue', width=2)
    ))
    
    # Add initial capital line
    fig.add_hline(
        y=results['initial_capital'],
        line_dash="dash",
        line_color="gray",
        annotation_text="Initial Capital"
    )
    
    fig.update_layout(
        title='Equity Curve',
        xaxis_title='Date',
        yaxis_title='Equity ($)',
        height=400,
        hovermode='x unified'
    )
    
    return fig


def main():
    """Main dashboard application."""
    
    # Header
    st.title("📊 ICT Trading Agent Dashboard")
    st.markdown("---")
    
    # Sidebar
    st.sidebar.title("⚙️ Configuration")
    
    config = load_config()
    
    # Symbol selection
    symbol = st.sidebar.text_input(
        "Trading Symbol",
        value=config.get('trading', {}).get('symbol', 'NQ=F')
    )
    
    # Timeframe selection
    timeframe_options = ['1m', '5m', '15m', '30m', '1h', '4h', '1d']
    timeframe = st.sidebar.selectbox(
        "Timeframe",
        options=timeframe_options,
        index=timeframe_options.index(config.get('trading', {}).get('timeframe', '1h'))
    )
    
    # Period selection
    period_options = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y']
    period = st.sidebar.selectbox(
        "Period",
        options=period_options,
        index=2  # Default to 1mo
    )
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Live Analysis", "🧪 Backtesting", "📊 Patterns", "⚙️ Settings"])
    
    # Tab 1: Live Analysis
    with tab1:
        st.header("Live Market Analysis")
        
        with st.spinner("Loading market data..."):
            df = load_data(symbol, period, timeframe)
        
        if df.empty:
            st.error(f"No data available for {symbol}")
            return
        
        # Display current price
        current_price = df['Close'].iloc[-1]
        price_change = df['Close'].iloc[-1] - df['Close'].iloc[-2]
        price_change_pct = (price_change / df['Close'].iloc[-2]) * 100
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Current Price",
                value=f"${current_price:.2f}",
                delta=f"{price_change:.2f} ({price_change_pct:+.2f}%)"
            )
        
        with col2:
            st.metric(
                label="24h High",
                value=f"${df['High'].iloc[-24:].max():.2f}"
            )
        
        with col3:
            st.metric(
                label="24h Low",
                value=f"${df['Low'].iloc[-24:].min():.2f}"
            )
        
        with col4:
            st.metric(
                label="Volume",
                value=f"{df['Volume'].iloc[-1]:,.0f}"
            )
        
        st.markdown("---")
        
        # Generate analysis
        with st.spinner("Analyzing market structure..."):
            agent = ICTTradingAgent(config)
            
            # Get patterns
            fvgs = agent.detect_fair_value_gaps(symbol)
            order_blocks = agent.detect_order_blocks(symbol)
            market_structure = agent.analyze_market_structure(symbol)
            signals = agent.generate_signals(symbol)
        
        # Display chart
        fig = plot_price_chart(df, fvgs, order_blocks)
        st.plotly_chart(fig, use_container_width=True)
        
        # Market Structure
        st.subheader("Market Structure Analysis")
        col1, col2 = st.columns(2)
        
        with col1:
            trend = market_structure.get('trend_direction', 'UNKNOWN')
            trend_emoji = "📈" if trend == "UPTREND" else "📉" if trend == "DOWNTREND" else "➡️"
            st.info(f"{trend_emoji} **Trend Direction:** {trend}")
        
        with col2:
            st.info(f"🔍 **Patterns Detected:** {len(fvgs)} FVGs, {len(order_blocks)} Order Blocks")
        
        # Trading Signals
        st.subheader("🚨 Trading Signals")
        
        if signals:
            for signal in signals[:3]:  # Show top 3 signals
                direction_emoji = "🟢" if signal['direction'] in ['LONG', 'BULLISH'] else "🔴"
                
                with st.expander(f"{direction_emoji} {signal['pattern']} - Strength: {signal['strength']:.2%}"):
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Entry Price", f"${signal['price']:.2f}")
                    with col2:
                        st.metric("Stop Loss", f"${signal['stop_loss']:.2f}")
                    with col3:
                        st.metric("Take Profit", f"${signal['take_profit']:.2f}")
                    with col4:
                        risk = abs(signal['price'] - signal['stop_loss'])
                        reward = abs(signal['take_profit'] - signal['price'])
                        rr = reward / risk if risk > 0 else 0
                        st.metric("R:R Ratio", f"{rr:.2f}")
        else:
            st.info("No trading signals detected at this time.")
    
    # Tab 2: Backtesting
    with tab2:
        st.header("Backtesting Engine")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=datetime.now() - timedelta(days=365)
            )
        
        with col2:
            end_date = st.date_input(
                "End Date",
                value=datetime.now()
            )
        
        with col3:
            initial_capital = st.number_input(
                "Initial Capital ($)",
                min_value=1000,
                max_value=1000000,
                value=10000,
                step=1000
            )
        
        if st.button("🧪 Run Backtest", type="primary"):
            with st.spinner("Running backtest... This may take a while."):
                backtester = Backtester(
                    initial_capital=initial_capital,
                    commission=config.get('backtesting', {}).get('commission', 2.0),
                    slippage=config.get('backtesting', {}).get('slippage', 0.001)
                )
                
                results = backtester.run_backtest(
                    symbol=symbol,
                    start_date=start_date.strftime('%Y-%m-%d'),
                    end_date=end_date.strftime('%Y-%m-%d')
                )
                
                if 'error' not in results:
                    st.success("Backtest completed successfully!")
                    
                    # Display metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(
                            "Total Return",
                            f"{results['total_return']:.2%}",
                            delta=f"${results['final_capital'] - results['initial_capital']:.2f}"
                        )
                    
                    with col2:
                        st.metric("Win Rate", f"{results['win_rate']:.2%}")
                    
                    with col3:
                        st.metric("Sharpe Ratio", f"{results['sharpe_ratio']:.2f}")
                    
                    with col4:
                        st.metric("Max Drawdown", f"{results['max_drawdown']:.2%}")
                    
                    # Equity curve
                    st.subheader("Equity Curve")
                    fig = plot_backtest_results(results)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Trade statistics
                    st.subheader("Trade Statistics")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Trades", results['total_trades'])
                    with col2:
                        st.metric("Winning Trades", results['winning_trades'])
                    with col3:
                        st.metric("Losing Trades", results['losing_trades'])
                    
                    # Full report
                    with st.expander("📄 View Full Report"):
                        report = backtester.generate_report(results)
                        st.text(report)
                    
                    # Trade history
                    if results.get('trades'):
                        st.subheader("Trade History")
                        trades_df = pd.DataFrame(results['trades'])
                        st.dataframe(trades_df, use_container_width=True)
                else:
                    st.error(results['error'])
    
    # Tab 3: Patterns
    with tab3:
        st.header("Pattern Detection")
        
        df = load_data(symbol, period, timeframe)
        
        if not df.empty:
            agent = ICTTradingAgent(config)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Fair Value Gaps")
                fvgs = agent.detect_fair_value_gaps(symbol)
                
                if fvgs:
                    for i, fvg in enumerate(fvgs[:10], 1):
                        direction_color = "🟢" if fvg['direction'] == 'BULLISH' else "🔴"
                        st.write(f"{direction_color} **FVG #{i}**")
                        st.write(f"- Gap Size: {fvg['gap_size']:.4%}")
                        st.write(f"- Strength: {fvg['strength']:.2%}")
                        st.write(f"- Entry: ${fvg['entry_price']:.2f}")
                        st.divider()
                else:
                    st.info("No FVGs detected")
            
            with col2:
                st.subheader("🎯 Order Blocks")
                order_blocks = agent.detect_order_blocks(symbol)
                
                if order_blocks:
                    for i, ob in enumerate(order_blocks[:10], 1):
                        direction_color = "🟢" if ob['direction'] == 'BULLISH' else "🔴"
                        st.write(f"{direction_color} **Order Block #{i}**")
                        st.write(f"- Range: ${ob['block_low']:.2f} - ${ob['block_high']:.2f}")
                        st.write(f"- Strength: {ob['strength']:.2%}")
                        st.write(f"- Entry: ${ob['entry_price']:.2f}")
                        st.divider()
                else:
                    st.info("No Order Blocks detected")
    
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
                value=config.get('trading', {}).get('lookback_period', 100)
            )
            
            st.number_input(
                "FVG Min Size (%)",
                min_value=0.001,
                max_value=1.0,
                value=config.get('patterns', {}).get('fvg_min_size', 0.001),
                format="%.3f"
            )
        
        with col2:
            st.number_input(
                "Order Block Strength",
                min_value=1,
                max_value=10,
                value=config.get('patterns', {}).get('orderblock_strength', 3)
            )
            
            st.number_input(
                "Risk Per Trade (%)",
                min_value=0.01,
                max_value=10.0,
                value=config.get('risk', {}).get('risk_per_trade', 0.02) * 100,
                format="%.2f"
            ) / 100
        
        st.subheader("Notification Settings")
        
        notifications_enabled = st.checkbox(
            "Enable Notifications",
            value=config.get('alerts', {}).get('enabled', True)
        )
        
        webhook_url = st.text_input(
            "Webhook URL (Discord/Slack)",
            value=config.get('alerts', {}).get('webhook_url', ''),
            type="password"
        )
        
        st.info("💡 Configure webhook notifications for real-time trading alerts")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "Built with ❤️ for algorithmic trading enthusiasts | "
        "ICT Trading Agent v1.0"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
