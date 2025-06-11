import pandas as pd
from patterns import candlestick, chart
from visualization.plotter import plot_patterns
from analysis import indicators
from analysis.indicators import compute_atr, compute_macd, compute_bollinger_bands, compute_stochastic

# 1. Загрузка данных
df = pd.read_csv('data/df_high.csv', parse_dates=['datetime'])

# 2. Добавляем индикаторы (EMA20, EMA50, SMA, RSI, средний объём и др.)
df = indicators.add_basic_indicators(df, ema_periods=[20, 50], sma_periods=[20, 50], rsi_period=14)

# === ATR 14 ===
df['atr_14'] = compute_atr(df)

# === MACD ===
df['macd'], df['macd_signal'], df['macd_hist'] = compute_macd(df)

# === Bollinger Bands ===
df['bb_upper'], df['bb_ma'], df['bb_lower'] = compute_bollinger_bands(df)

# === Stochastic Oscillator ===
df['stoch_k'], df['stoch_d'] = compute_stochastic(df)

# 3. Поиск паттернов
candle_patterns = candlestick.find_all_patterns(df)
chart_patterns = chart.find_all_patterns(df)

# 4. Подтверждение паттернов (по классике, по уровням)
confirmed_candles = candlestick.confirm_candlestick_patterns(df, candle_patterns)
confirmed_chart = chart.confirm_chart_patterns(df, chart_patterns)

# 5. Фильтрация свечных паттернов по объёму, RSI и тренду (TA-правила)
filtered_candle_patterns = []
for p in confirmed_candles:
    idx = p['index'] if isinstance(p['index'], int) else df.index.get_loc(p['index'])
    row = df.iloc[idx]
    if p['direction'] == 'bullish':
        # TA: нисходящий тренд, высокий объем, RSI < 35
        trend_down = row['close'] < row['ema_20'] and row['ema_20'] < row['ema_50']
        high_volume = indicators.is_high_volume(row, factor=1.3)
        rsi_ok = indicators.is_bullish_rsi(row, threshold=35)
        if trend_down and high_volume and rsi_ok:
            filtered_candle_patterns.append(p)
    elif p['direction'] == 'bearish':
        # TA: восходящий тренд, высокий объем, RSI > 65
        trend_up = row['close'] > row['ema_20'] and row['ema_20'] > row['ema_50']
        high_volume = indicators.is_high_volume(row, factor=1.3)
        rsi_ok = indicators.is_bearish_rsi(row, threshold=65)
        if trend_up and high_volume and rsi_ok:
            filtered_candle_patterns.append(p)

# 6. Фильтрация фигурных паттернов по объёму и RSI (по желанию — можно сложнее!)
filtered_chart_patterns = []
for p in confirmed_chart:
    idx = p['indices'][-1]  # подтверждение по последней точке фигуры
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
        # Для остальных фигур фильтруем только по объёму (или дополни по своему правилу)
        high_volume = indicators.is_high_volume(row, factor=1.3)
        if high_volume:
            filtered_chart_patterns.append(p)

# 7. Визуализация только сильных сигналов!
plot_patterns(df, filtered_candle_patterns, filtered_chart_patterns)
