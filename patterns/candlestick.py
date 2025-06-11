import pandas as pd
import numpy as np

def confirm_candlestick_patterns(df, patterns, lookahead=1):
    """
    Подтверждение свечных паттернов:
    - bullish: следующая свеча закрытие > high сигнальной
    - bearish: следующая свеча закрытие < low сигнальной
    """
    confirmed = []
    for p in patterns:
        idx = p['index'] if isinstance(p['index'], int) else df.index.get_loc(p['index'])
        if idx + lookahead >= len(df):
            continue  # Нет следующей свечи
        next_row = df.iloc[idx + lookahead]
        row = df.iloc[idx]
        if p['direction'] == 'bullish':
            if next_row['close'] > row['high']:
                confirmed.append(p)
        elif p['direction'] == 'bearish':
            if next_row['close'] < row['low']:
                confirmed.append(p)
        elif p['direction'] == 'neutral':
            # Можно не подтверждать, либо своё правило
            pass
    return confirmed

def find_all_patterns(df):
    patterns = []
    patterns += detect_hammer(df)
    patterns += detect_inverted_hammer(df)
    patterns += detect_engulfing(df)
    patterns += detect_doji(df)
    patterns += detect_morning_star(df)
    patterns += detect_evening_star(df)
    patterns += detect_shooting_star(df)
    patterns += detect_hanging_man(df)
    patterns += detect_harami(df)
    patterns += detect_three_white_soldiers(df)
    patterns += detect_three_black_crows(df)
    patterns += detect_piercing_line(df)
    patterns += detect_dark_cloud_cover(df)
    patterns += detect_spinning_top(df)
    patterns += detect_marubozu(df)
    patterns += detect_tweezer_top(df)
    patterns += detect_tweezer_bottom(df)
    return patterns

def detect_hammer(df, body_ratio=0.33, shadow_ratio=2):
    patterns = []
    for i, row in df.iterrows():
        o, h, l, c = row['open'], row['high'], row['low'], row['close']
        body = abs(c - o)
        lower_shadow = min(o, c) - l
        upper_shadow = h - max(o, c)
        if body > 0 and lower_shadow > shadow_ratio * body and upper_shadow < body_ratio * body:
            patterns.append({'type': 'Hammer', 'index': i, 'direction': 'bullish'})
    return patterns

def detect_inverted_hammer(df, body_ratio=0.33, shadow_ratio=2):
    patterns = []
    for i, row in df.iterrows():
        o, h, l, c = row['open'], row['high'], row['low'], row['close']
        body = abs(c - o)
        upper_shadow = h - max(o, c)
        lower_shadow = min(o, c) - l
        if body > 0 and upper_shadow > shadow_ratio * body and lower_shadow < body_ratio * body:
            patterns.append({'type': 'InvertedHammer', 'index': i, 'direction': 'bullish'})
    return patterns

def detect_engulfing(df):
    patterns = []
    for i in range(1, len(df)):
        prev = df.iloc[i-1]
        curr = df.iloc[i]
        prev_body = prev['close'] - prev['open']
        curr_body = curr['close'] - curr['open']
        # Bullish engulfing
        if prev_body < 0 and curr_body > 0:
            if curr['open'] < prev['close'] and curr['close'] > prev['open']:
                patterns.append({'type': 'Engulfing', 'index': df.index[i], 'direction': 'bullish'})
        # Bearish engulfing
        if prev_body > 0 and curr_body < 0:
            if curr['open'] > prev['close'] and curr['close'] < prev['open']:
                patterns.append({'type': 'Engulfing', 'index': df.index[i], 'direction': 'bearish'})
    return patterns

def detect_doji(df, body_to_range=0.05):
    patterns = []
    for i, row in df.iterrows():
        o, c, h, l = row['open'], row['close'], row['high'], row['low']
        body = abs(c - o)
        rng = h - l
        if rng > 0 and body / rng < body_to_range:
            patterns.append({'type': 'Doji', 'index': i, 'direction': 'neutral'})
    return patterns

def detect_morning_star(df):
    patterns = []
    for i in range(2, len(df)):
        o1, c1 = df.iloc[i-2][['open', 'close']]
        o2, c2 = df.iloc[i-1][['open', 'close']]
        o3, c3 = df.iloc[i][['open', 'close']]
        if (c1 < o1) and (abs(c2 - o2) < abs(c1 - o1)) and (c3 > o3) and (c3 > (o1 + c1)/2):
            patterns.append({'type': 'MorningStar', 'index': df.index[i], 'direction': 'bullish'})
    return patterns

def detect_evening_star(df):
    patterns = []
    for i in range(2, len(df)):
        o1, c1 = df.iloc[i-2][['open', 'close']]
        o2, c2 = df.iloc[i-1][['open', 'close']]
        o3, c3 = df.iloc[i][['open', 'close']]
        if (c1 > o1) and (abs(c2 - o2) < abs(c1 - o1)) and (c3 < o3) and (c3 < (o1 + c1)/2):
            patterns.append({'type': 'EveningStar', 'index': df.index[i], 'direction': 'bearish'})
    return patterns

def detect_shooting_star(df, body_ratio=0.33, shadow_ratio=2):
    patterns = []
    for i, row in df.iterrows():
        o, h, l, c = row['open'], row['high'], row['low'], row['close']
        body = abs(c - o)
        upper_shadow = h - max(o, c)
        lower_shadow = min(o, c) - l
        if body > 0 and upper_shadow > shadow_ratio * body and lower_shadow < body_ratio * body:
            patterns.append({'type': 'ShootingStar', 'index': i, 'direction': 'bearish'})
    return patterns

def detect_hanging_man(df, body_ratio=0.33, shadow_ratio=2):
    patterns = []
    for i, row in df.iterrows():
        o, h, l, c = row['open'], row['high'], row['low'], row['close']
        body = abs(c - o)
        lower_shadow = min(o, c) - l
        upper_shadow = h - max(o, c)
        if body > 0 and lower_shadow > shadow_ratio * body and upper_shadow < body_ratio * body:
            patterns.append({'type': 'HangingMan', 'index': i, 'direction': 'bearish'})
    return patterns

def detect_harami(df):
    patterns = []
    for i in range(1, len(df)):
        prev = df.iloc[i-1]
        curr = df.iloc[i]
        prev_body = prev['close'] - prev['open']
        curr_body = curr['close'] - curr['open']
        # Bullish Harami
        if prev_body < 0 and curr_body > 0:
            if curr['open'] > prev['close'] and curr['close'] < prev['open']:
                patterns.append({'type': 'Harami', 'index': df.index[i], 'direction': 'bullish'})
        # Bearish Harami
        if prev_body > 0 and curr_body < 0:
            if curr['open'] < prev['close'] and curr['close'] > prev['open']:
                patterns.append({'type': 'Harami', 'index': df.index[i], 'direction': 'bearish'})
    return patterns

def detect_three_white_soldiers(df):
    patterns = []
    for i in range(2, len(df)):
        c1, o1 = df.iloc[i-2][['close', 'open']]
        c2, o2 = df.iloc[i-1][['close', 'open']]
        c3, o3 = df.iloc[i][['close', 'open']]
        if (c1 > o1) and (c2 > o2) and (c3 > o3):
            if (c2 > c1) and (c3 > c2):
                patterns.append({'type': 'ThreeWhiteSoldiers', 'index': df.index[i], 'direction': 'bullish'})
    return patterns

def detect_three_black_crows(df):
    patterns = []
    for i in range(2, len(df)):
        c1, o1 = df.iloc[i-2][['close', 'open']]
        c2, o2 = df.iloc[i-1][['close', 'open']]
        c3, o3 = df.iloc[i][['close', 'open']]
        if (c1 < o1) and (c2 < o2) and (c3 < o3):
            if (c2 < c1) and (c3 < c2):
                patterns.append({'type': 'ThreeBlackCrows', 'index': df.index[i], 'direction': 'bearish'})
    return patterns

def detect_piercing_line(df):
    patterns = []
    for i in range(1, len(df)):
        prev = df.iloc[i-1]
        curr = df.iloc[i]
        prev_body = prev['close'] - prev['open']
        curr_body = curr['close'] - curr['open']
        if prev_body < 0 and curr_body > 0:
            midpoint = (prev['open'] + prev['close']) / 2
            if curr['open'] < prev['close'] and curr['close'] > midpoint and curr['close'] < prev['open']:
                patterns.append({'type': 'PiercingLine', 'index': df.index[i], 'direction': 'bullish'})
    return patterns

def detect_dark_cloud_cover(df):
    patterns = []
    for i in range(1, len(df)):
        prev = df.iloc[i-1]
        curr = df.iloc[i]
        prev_body = prev['close'] - prev['open']
        curr_body = curr['close'] - curr['open']
        if prev_body > 0 and curr_body < 0:
            midpoint = (prev['open'] + prev['close']) / 2
            if curr['open'] > prev['close'] and curr['close'] < midpoint and curr['close'] > prev['open']:
                patterns.append({'type': 'DarkCloudCover', 'index': df.index[i], 'direction': 'bearish'})
    return patterns

def detect_spinning_top(df, min_body=0.2, max_body=0.5):
    patterns = []
    for i, row in df.iterrows():
        o, c, h, l = row['open'], row['close'], row['high'], row['low']
        rng = h - l
        body = abs(c - o)
        upper = h - max(o, c)
        lower = min(o, c) - l
        if rng > 0:
            rel_body = body / rng
            rel_upper = upper / rng
            rel_lower = lower / rng
            if min_body < rel_body < max_body and rel_upper > 0.2 and rel_lower > 0.2:
                patterns.append({'type': 'SpinningTop', 'index': i, 'direction': 'neutral'})
    return patterns

def detect_marubozu(df, shadow_ratio=0.03):
    patterns = []
    for i, row in df.iterrows():
        o, c, h, l = row['open'], row['close'], row['high'], row['low']
        body = abs(c - o)
        upper_shadow = h - max(o, c)
        lower_shadow = min(o, c) - l
        rng = h - l
        if rng > 0 and upper_shadow / rng < shadow_ratio and lower_shadow / rng < shadow_ratio:
            direction = 'bullish' if c > o else 'bearish'
            patterns.append({'type': 'Marubozu', 'index': i, 'direction': direction})
    return patterns

def detect_tweezer_top(df, lookback=1):
    patterns = []
    for i in range(lookback, len(df)):
        prev = df.iloc[i - lookback]
        curr = df.iloc[i]
        if abs(prev['high'] - curr['high']) < 1e-8:
            patterns.append({'type': 'TweezerTop', 'index': df.index[i], 'direction': 'bearish'})
    return patterns

def detect_tweezer_bottom(df, lookback=1):
    patterns = []
    for i in range(lookback, len(df)):
        prev = df.iloc[i - lookback]
        curr = df.iloc[i]
        if abs(prev['low'] - curr['low']) < 1e-8:
            patterns.append({'type': 'TweezerBottom', 'index': df.index[i], 'direction': 'bullish'})
    return patterns
