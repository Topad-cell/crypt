import dash
from dash import dcc, html
import pandas as pd

from patterns import candlestick, chart
from visualization.plotter import plot_patterns
from analysis import indicators

# 1. Загрузка и обработка данных (копия твоего pipeline)
df = pd.read_csv('data/df_high.csv', parse_dates=['datetime'])
df = indicators.add_basic_indicators(df, ema_periods=[20, 50], sma_periods=[20, 50], rsi_period=14)
from analysis.indicators import compute_atr, compute_macd, compute_bollinger_bands, compute_stochastic

df['atr_14'] = compute_atr(df)
df['macd'], df['macd_signal'], df['macd_hist'] = compute_macd(df)
df['bb_upper'], df['bb_ma'], df['bb_lower'] = compute_bollinger_bands(df)
df['stoch_k'], df['stoch_d'] = compute_stochastic(df)

candle_patterns = candlestick.find_all_patterns(df)
chart_patterns = chart.find_all_patterns(df)
confirmed_candles = candlestick.confirm_candlestick_patterns(df, candle_patterns)
confirmed_chart = chart.confirm_chart_patterns(df, chart_patterns)

# Фильтрация как раньше (по желанию: можешь добавить интерактивность позже!)
filtered_candle_patterns = []
for p in confirmed_candles:
    idx = p['index'] if isinstance(p['index'], int) else df.index.get_loc(p['index'])
    row = df.iloc[idx]
    macd_ok = row['macd'] > row['macd_signal'] if p['direction'] == 'bullish' else row['macd'] < row['macd_signal']
    boll_ok = (row['close'] < row['bb_lower']) if p['direction'] == 'bullish' else (row['close'] > row['bb_upper'])
    stoch_ok = (row['stoch_k'] < 20) if p['direction'] == 'bullish' else (row['stoch_k'] > 80)
    if p['direction'] == 'bullish':
        trend_down = row['close'] < row['ema_20'] and row['ema_20'] < row['ema_50']
        high_volume = indicators.is_high_volume(row, factor=1.3)
        rsi_ok = indicators.is_bullish_rsi(row, threshold=35)
        if trend_down and high_volume and rsi_ok and macd_ok and boll_ok and stoch_ok:
            filtered_candle_patterns.append(p)
    elif p['direction'] == 'bearish':
        trend_up = row['close'] > row['ema_20'] and row['ema_20'] > row['ema_50']
        high_volume = indicators.is_high_volume(row, factor=1.3)
        rsi_ok = indicators.is_bearish_rsi(row, threshold=65)
        if trend_up and high_volume and rsi_ok and macd_ok and boll_ok and stoch_ok:
            filtered_candle_patterns.append(p)

filtered_chart_patterns = []
for p in confirmed_chart:
    idx = p['indices'][-1]
    row = df.iloc[idx]
    t = p['type'].lower()
    if t == 'doublebottom':
        high_volume = indicators.is_high_volume(row, factor=1.3)
        rsi_ok = row['rsi'] < 40
        if high_volume and rsi_ok:
            filtered_chart_patterns.append(p)
    elif t == 'doubletop':
        high_volume = indicators.is_high_volume(row, factor=1.3)
        rsi_ok = row['rsi'] > 60
        if high_volume and rsi_ok:
            filtered_chart_patterns.append(p)
    else:
        high_volume = indicators.is_high_volume(row, factor=1.3)
        if high_volume:
            filtered_chart_patterns.append(p)

# --- График: plot_patterns (новая опция: return_fig=True) ---
fig = plot_patterns(df, filtered_candle_patterns, filtered_chart_patterns, return_fig=True)

# === Dash App ===
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('Crypto TA Dashboard', style={"textAlign": "center", "color": "#fff"}),
    dcc.Graph(
        id='main-graph',
        figure=fig,
        style={"height": "1000px", "background": "#1c1e2c"},
        config={"displayModeBar": True, "displaylogo": False}
    ),
    html.Div("v0.1 demo", style={"color": "#888", "textAlign": "center", "paddingTop": "8px"})
], style={"background": "#151720", "padding": "30px"})

if __name__ == "__main__":
    app.run(debug=True)

