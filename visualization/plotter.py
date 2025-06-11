import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_patterns(df, candle_patterns, chart_patterns):
    # --- Создаём subplot: Price+Patterns, Volume, RSI
    fig = make_subplots(
        rows=5, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=[0.65, 0.18, 0.18, 0.17, 0.17],
        specs=[
            [{"secondary_y": True}],  # 1-й ряд — цена+паттерны
            [{"type": "bar"}],  # 1-й ряд — цена+паттерны
            [{"type": "bar"}],  # 2-й ряд — только объём
            [{"type": "xy"}],  # 3-й ряд — RSI
            [{"type": "xy"}],  # 3-й ряд — RSI
        ],
        subplot_titles=("Price & Patterns", "DateTime", "Volume", "RSI", "Stochastic Oscillator")
    )

    # --- 1. Основной свечной график ---
    fig.add_trace(go.Candlestick(
        x=df['datetime'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='Candles'
    ), row=1, col=1)

    # --- EMA/SMA/ATR линии ---
    if 'bb_upper' in df and 'bb_lower' in df and 'bb_ma' in df:
        fig.add_trace(go.Scatter(
            x = df['datetime'], y = df['bb_upper'],
            mode = 'lines', name = 'Bollinger Upper', line = dict(width=1, color='gray', dash='dot')
        ), row = 1, col = 1)
        fig.add_trace(go.Scatter(
            x = df['datetime'], y = df['bb_lower'],
            mode = 'lines', name = 'Bollinger Lower', line = dict(width=1, color='gray', dash='dot')
        ), row = 1, col = 1)
        fig.add_trace(go.Scatter(
            x = df['datetime'], y = df['bb_ma'],
            mode = 'lines', name = 'Bollinger MA', line = dict(width=1, color='gray', dash='dash')
        ), row = 1, col = 1)
    if 'atr_14' in df:
        fig.add_trace(go.Scatter(
            x = df['datetime'], y = df['atr_14'],
            mode = 'lines', name = 'ATR 14', line = dict(width=1, color='green', dash='dash')
        ), row = 3, col = 1)
    if 'macd' in df and 'macd_signal' in df and 'macd_hist' in df:
        fig.add_trace(go.Scatter(
            x = df['datetime'], y = df['macd'],
            mode = 'lines', name = 'MACD', line = dict(width=1.2, color='cyan')
        ), row = 3, col = 1)
        fig.add_trace(go.Scatter(
            x = df['datetime'], y = df['macd_signal'],
            mode = 'lines', name = 'MACD Signal', line = dict(width=1, color='orange', dash='dash')
        ), row = 3, col = 1)
        fig.add_trace(go.Bar(
            x = df['datetime'], y = df['macd_hist'],
            name = 'MACD Hist', marker_color = 'magenta', opacity = 0.4
        ), row = 3, col = 1)
    if 'ema_20' in df:
        fig.add_trace(go.Scatter(
            x=df['datetime'], y=df['ema_20'],
            mode='lines', name='EMA 20', line=dict(width=1.5, color='cyan')
        ), row=1, col=1)
    if 'ema_50' in df:
        fig.add_trace(go.Scatter(
            x=df['datetime'], y=df['ema_50'],
            mode='lines', name='EMA 50', line=dict(width=1.5, color='orange')
        ), row=1, col=1)
    if 'sma_20' in df:
        fig.add_trace(go.Scatter(
            x=df['datetime'], y=df['sma_20'],
            mode='lines', name='SMA 20', line=dict(width=1, dash='dot', color='green')
        ), row=1, col=1)
    if 'sma_50' in df:
        fig.add_trace(go.Scatter(
            x=df['datetime'], y=df['sma_50'],
            mode='lines', name='SMA 50', line=dict(width=1, dash='dot', color='red')
        ), row=1, col=1)

    # --- 2. Свечные паттерны ---
    pattern_colors = {'bullish': 'limegreen', 'bearish': 'orangered', 'neutral': 'dodgerblue'}
    # Добавим стрелки "вверх" для бычьих, "вниз" для медвежьих паттернов
    for p in candle_patterns:
        idx = p['index'] if isinstance(p['index'], int) else df.index.get_loc(p['index'])
        x = df['datetime'].iloc[idx]
    
        if p['direction'] == 'bullish':
            y = df['low'].iloc[idx] * 0.98
            marker_symbol = 'arrow-bar-up'
            marker_color = 'lime'
        elif p['direction'] == 'bearish':
            y = df['high'].iloc[idx] * 1.02
            marker_symbol = 'arrow-bar-down'
            marker_color = 'red'
        else:
            y = (df['low'].iloc[idx] + df['high'].iloc[idx]) / 2
            marker_symbol = 'circle'
            marker_color = 'dodgerblue'
    # Добавляем стрелку
        fig.add_trace(go.Scatter(
            x = [x], y = [y],
            mode = 'markers',
            marker = dict(symbol=marker_symbol, size=22, color=marker_color, line=dict(width=1, color='black')),
            name = f"{p['type']} signal",
            showlegend = False,
            hovertext = f"{p['type']} ({p['direction']})"
        ), row = 1, col = 1)
    pattern_types_in_legend = set()
    for p in candle_patterns:
        idx = p['index'] if isinstance(p['index'], int) else df.index.get_loc(p['index'])
        x = df['datetime'].iloc[idx]
        name = p['type']
        show_legend = name not in pattern_types_in_legend
        pattern_types_in_legend.add(name)
        if p['direction'] == 'bullish':
            y = df['low'].iloc[idx] * 0.98
            color = pattern_colors['bullish']
        elif p['direction'] == 'bearish':
            y = df['high'].iloc[idx] * 1.02
            color = pattern_colors['bearish']
        else:
            y = (df['low'].iloc[idx] + df['high'].iloc[idx]) / 2
            color = pattern_colors['neutral']

        fig.add_trace(go.Scatter(
            x=[x], y=[y],
            mode='markers',
            marker=dict(color=color, size=12, symbol='diamond'),
            name=name,
            legendgroup=name,
            showlegend=show_legend,
            hovertext=f"{p['type']} ({p['direction']})"
        ), row=1, col=1)

    # --- 3. Фигурные паттерны ---
    for pattern in chart_patterns:
        name = pattern['type']
        show_legend = name not in pattern_types_in_legend
        pattern_types_in_legend.add(name)
        indices = pattern['indices']
        direction = pattern.get('direction', 'neutral')
        color = pattern_colors.get(direction, 'dodgerblue')
        x_points = [df['datetime'].iloc[i] for i in indices]
        # Высота для линий
        if name.lower().endswith('top') or name.lower().endswith('shoulders'):
            y_points = [df['high'].iloc[i] for i in indices]
        elif name.lower().endswith('bottom'):
            y_points = [df['low'].iloc[i] for i in indices]
        else:
            n = len(indices)
            y_points = [df['high'].iloc[i] if k < n//2 else df['low'].iloc[i] for k,i in enumerate(indices)]

        fig.add_trace(go.Scatter(
            x=x_points, y=y_points,
            mode='lines+markers',
            marker=dict(color=color, size=9, symbol='circle'),
            line=dict(color=color, width=3, dash='dot'),
            name=name,
            legendgroup=name,
            showlegend=show_legend,
            hovertext=f"{name} ({direction})"
        ), row=1, col=1)

    # --- Стрелки для фигурных паттернов (только для подтверждённых) ---

    for p in chart_patterns:
        name = p['type']
        direction = p.get('direction', 'neutral')
        color = pattern_colors.get(direction, 'dodgerblue')
        indices = p['indices']
        # По умолчанию ставим стрелку в крайней точке фигуры (например, последняя свеча)
        idx = indices[-1]
        x = df['datetime'].iloc[idx]
        # Для “bullish” — стрелка вверх чуть ниже low, для “bearish” — вниз чуть выше high

        if direction == 'bullish':
            y = df['low'].iloc[idx] * 0.985
            marker_symbol = 'arrow-bar-up'
        elif direction == 'bearish':
            y = df['high'].iloc[idx] * 1.015
            marker_symbol = 'arrow-bar-down'
        else:
            y = (df['low'].iloc[idx] + df['high'].iloc[idx]) / 2
            marker_symbol = 'circle'
        fig.add_trace(go.Scatter(
            x = [x], y = [y],
            mode = 'markers',
            marker = dict(symbol=marker_symbol, size=26, color=color, line=dict(width=2, color='black')),
            name = f"{name} signal",
            showlegend = False,
            hovertext = f"{name} ({direction})"
        ), row = 1, col = 1)

    # --- 4. Объём ---
    fig.add_trace(go.Bar(
        x=df['datetime'], y=df['volume'],
        name='Volume',
        marker_color='white', opacity=0.5
    ), row=3, col=1)
    if 'volume_ma_20' in df:
        fig.add_trace(go.Scatter(
            x=df['datetime'], y=df['volume_ma_20'],
            mode='lines', name='Volume MA20', line=dict(width=1, color='magenta')
        ), row=3, col=1)

    # --- 5. RSI ---
    if 'rsi' in df:
        fig.add_trace(go.Scatter(
            x=df['datetime'], y=df['rsi'],
            mode='lines', name='RSI', line=dict(width=1.2, color='dodgerblue')
        ), row=4, col=1)
        # Линии 70/30
        fig.add_hline(y=70, line_dash='dot', line_color='red', row=4, col=1)
        fig.add_hline(y=30, line_dash='dot', line_color='green', row=4, col=1)

    # --- Stochastic Oscillator (ряд 5) ---
    if 'stoch_k' in df and 'stoch_d' in df:
        fig.add_trace(go.Scatter(
            x = df['datetime'], y = df['stoch_k'],
            mode = 'lines', name = '%K', line = dict(width=1.2, color='dodgerblue')
        ), row = 5, col = 1)
        fig.add_trace(go.Scatter(
            x = df['datetime'], y = df['stoch_d'],
            mode = 'lines', name = '%D', line = dict(width=1.2, color='orange', dash='dash')
        ), row = 5, col = 1)
        # Линии перекупленности/перепроданности (обычно 80 и 20)
        fig.add_hline(y=80, line_dash='dot', line_color='red', row=5, col=1)
        fig.add_hline(y=20, line_dash='dot', line_color='green', row=5, col=1)
    # --- Оформление ---
    fig.update_layout(
        title='Crypto Chart with Patterns & Indicators',
        yaxis1=dict(title='Price'),
        yaxis2=dict(title='Datetime'),
        yaxis3=dict(title='Volume'),
        yaxis4=dict(title='RSI'),
        yaxis5=dict(title='Stochastic Oscillator'),
        height=1000,
        template='plotly_dark',
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1)
    )
    fig.show()
