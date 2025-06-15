import numpy as np
from scipy.signal import argrelextrema


def confirm_chart_patterns(df, patterns, lookahead=1):
    """
    Подтверждение ВСЕХ фигурных паттернов (канонично для ТА).
    Показывает только те фигуры, где был пробой и закрытие за ключевой линией!
    """
    confirmed = []
    for p in patterns:
        name = p["type"].lower()
        idxs = p["indices"]
        last_idx = idxs[-1]
        if last_idx + lookahead >= len(df):
            continue
        next_close = df["close"].iloc[last_idx + lookahead]

        # --- Double Top ---
        if name == "doubletop":
            neckline = df["low"].iloc[idxs[1]]
            if next_close < neckline:
                confirmed.append(p)
        # --- Double Bottom ---
        elif name == "doublebottom":
            neckline = df["high"].iloc[idxs[1]]
            if next_close > neckline:
                confirmed.append(p)
        # --- Triple Top ---
        elif name == "tripletop":
            neckline = df["low"].iloc[idxs[1]]
            if next_close < neckline:
                confirmed.append(p)
        # --- Triple Bottom ---
        elif name == "triplebottom":
            neckline = df["high"].iloc[idxs[1]]
            if next_close > neckline:
                confirmed.append(p)
        # --- Head & Shoulders ---
        elif name == "headandshoulders":
            l_shoulder, head, r_shoulder = idxs
            left_low = df["low"].iloc[l_shoulder]
            right_low = df["low"].iloc[r_shoulder]
            neckline = (left_low + right_low) / 2
            if next_close < neckline:
                confirmed.append(p)
        # --- Inverse Head & Shoulders ---
        elif name == "inverseheadandshoulders":
            l_shoulder, head, r_shoulder = idxs
            left_high = df["high"].iloc[l_shoulder]
            right_high = df["high"].iloc[r_shoulder]
            neckline = (left_high + right_high) / 2
            if next_close > neckline:
                confirmed.append(p)
        # --- Ascending Triangle ---
        elif name == "ascendingtriangle":
            # Пробой горизонтального сопротивления — максимум двух high вершин
            highs = [df["high"].iloc[i] for i in idxs]
            resistance = max(highs)
            if next_close > resistance:
                confirmed.append(p)
        # --- Descending Triangle ---
        elif name == "descendingtriangle":
            # Пробой поддержки — минимум двух low
            lows = [df["low"].iloc[i] for i in idxs]
            support = min(lows)
            if next_close < support:
                confirmed.append(p)
        # --- Symmetrical Triangle ---
        elif name == "symmetricaltriangle":
            # Пробой любой из сторон — закрытие выше max(highs) или ниже min(lows)
            highs = [df["high"].iloc[i] for i in idxs]
            lows = [df["low"].iloc[i] for i in idxs]
            if next_close > max(highs) or next_close < min(lows):
                confirmed.append(p)
        # --- Channel ---
        elif name == "channel":
            # Пробой верхней или нижней границы (up/down направление)
            highs = [df["high"].iloc[i] for i in idxs[:2]]
            lows = [df["low"].iloc[i] for i in idxs[2:]]
            if p.get("direction") == "up" and next_close > max(highs):
                confirmed.append(p)
            elif p.get("direction") == "down" and next_close < min(lows):
                confirmed.append(p)
        # --- Rectangle (боковик) ---
        elif name == "rectangle":
            highs = [df["high"].iloc[i] for i in idxs]
            lows = [df["low"].iloc[i] for i in idxs]
            upper = max(highs)
            lower = min(lows)
            if next_close > upper or next_close < lower:
                confirmed.append(p)
        # --- Wedge (клин) ---
        elif "wedge" in name:
            highs = [df["high"].iloc[i] for i in idxs]
            lows = [df["low"].iloc[i] for i in idxs]
            if p.get("direction") == "bullish" and next_close > max(highs):
                confirmed.append(p)
            elif p.get("direction") == "bearish" and next_close < min(lows):
                confirmed.append(p)
        # --- Flag/Pennant (флаг/вымпел) ---
        elif "flag" in name or "pennant" in name:
            highs = [df["high"].iloc[i] for i in idxs]
            lows = [df["low"].iloc[i] for i in idxs]
            if p.get("direction") == "bullish" and next_close > max(highs):
                confirmed.append(p)
            elif p.get("direction") == "bearish" and next_close < min(lows):
                confirmed.append(p)
        # --- Cup and Handle ---
        elif name == "cupandhandle":
            highs = [df["high"].iloc[i] for i in idxs]
            resistance = max(highs)
            if next_close > resistance:
                confirmed.append(p)
        # --- Rounding Bottom ---
        elif name == "roundingbottom":
            highs = [df["high"].iloc[i] for i in idxs]
            if next_close > max(highs):
                confirmed.append(p)
        # --- Любая другая фигура: пробой high/low последней точки ---
        else:
            high = df["high"].iloc[last_idx]
            low = df["low"].iloc[last_idx]
            if p.get("direction") == "bullish" and next_close > high:
                confirmed.append(p)
            elif p.get("direction") == "bearish" and next_close < low:
                confirmed.append(p)
    return confirmed


def find_all_patterns(df):
    patterns = []
    patterns += detect_double_top(df)
    patterns += detect_double_bottom(df)
    patterns += detect_head_and_shoulders(df)
    patterns += detect_inverse_head_and_shoulders(df)
    patterns += detect_triple_top(df)
    patterns += detect_triple_bottom(df)
    patterns += detect_ascending_triangle(df)
    patterns += detect_descending_triangle(df)
    patterns += detect_symmetrical_triangle(df)
    patterns += detect_channel(df)
    # patterns += detect_flag_pennant(df)   # Можно добавить по желанию
    # patterns += detect_wedge(df)
    # patterns += detect_rectangle(df)
    # patterns += detect_cup_and_handle(df)
    # patterns += detect_rounding_bottom(df)
    return patterns


# --- Double Top ---
def detect_double_top(df, order=5, threshold=0.005):
    highs = df["high"].values
    indices = argrelextrema(highs, np.greater, order=order)[0]
    patterns = []
    for i in range(len(indices) - 1):
        idx1, idx2 = indices[i], indices[i + 1]
        price1, price2 = highs[idx1], highs[idx2]
        if abs(price1 - price2) / price1 < threshold:
            # Находим локальный минимум между двумя вершинами
            min_idx = np.argmin(df["low"].values[idx1 : idx2 + 1]) + idx1
            patterns.append(
                {
                    "type": "DoubleTop",
                    "indices": [idx1, min_idx, idx2],
                    "direction": "bearish",
                }
            )
    return patterns


# --- Double Bottom ---
def detect_double_bottom(df, order=5, threshold=0.005):
    lows = df["low"].values
    indices = argrelextrema(lows, np.less, order=order)[0]
    patterns = []
    for i in range(len(indices) - 1):
        idx1, idx2 = indices[i], indices[i + 1]
        price1, price2 = lows[idx1], lows[idx2]
        if abs(price1 - price2) / price1 < threshold:
            max_idx = np.argmax(df["high"].values[idx1 : idx2 + 1]) + idx1
            patterns.append(
                {
                    "type": "DoubleBottom",
                    "indices": [idx1, max_idx, idx2],
                    "direction": "bullish",
                }
            )
    return patterns


# --- Head & Shoulders ---
def detect_head_and_shoulders(df, order=5, threshold=0.02):
    highs = df["high"].values
    indices = argrelextrema(highs, np.greater, order=order)[0]
    patterns = []
    for i in range(len(indices) - 2):
        low, high, radius = (
            highs[indices[i]],
            highs[indices[i + 1]],
            highs[indices[i + 2]],
        )
        if high > low and high > radius and abs(low - radius) / high < threshold:
            patterns.append(
                {
                    "type": "HeadAndShoulders",
                    "indices": [indices[i], indices[i + 1], indices[i + 2]],
                    "direction": "bearish",
                }
            )
    return patterns


# --- Inverse Head & Shoulders ---
def detect_inverse_head_and_shoulders(df, order=5, threshold=0.02):
    lows = df["low"].values
    indices = argrelextrema(lows, np.less, order=order)[0]
    patterns = []
    for i in range(len(indices) - 2):
        low, high, radius = lows[indices[i]], lows[indices[i + 1]], lows[indices[i + 2]]
        if high < low and high < radius and abs(low - radius) / high < threshold:
            patterns.append(
                {
                    "type": "InverseHeadAndShoulders",
                    "indices": [indices[i], indices[i + 1], indices[i + 2]],
                    "direction": "bullish",
                }
            )
    return patterns


# --- Triple Top ---
def detect_triple_top(df, order=5, threshold=0.01):
    highs = df["high"].values
    indices = argrelextrema(highs, np.greater, order=order)[0]
    patterns = []
    for i in range(len(indices) - 2):
        p1, p2, p3 = highs[indices[i]], highs[indices[i + 1]], highs[indices[i + 2]]
        avg = np.mean([p1, p2, p3])
        if max(abs(p1 - avg), abs(p2 - avg), abs(p3 - avg)) / avg < threshold:
            patterns.append(
                {
                    "type": "TripleTop",
                    "indices": [indices[i], indices[i + 1], indices[i + 2]],
                    "direction": "bearish",
                }
            )
    return patterns


# --- Triple Bottom ---
def detect_triple_bottom(df, order=5, threshold=0.01):
    lows = df["low"].values
    indices = argrelextrema(lows, np.less, order=order)[0]
    patterns = []
    for i in range(len(indices) - 2):
        p1, p2, p3 = lows[indices[i]], lows[indices[i + 1]], lows[indices[i + 2]]
        avg = np.mean([p1, p2, p3])
        if max(abs(p1 - avg), abs(p2 - avg), abs(p3 - avg)) / avg < threshold:
            patterns.append(
                {
                    "type": "TripleBottom",
                    "indices": [indices[i], indices[i + 1], indices[i + 2]],
                    "direction": "bullish",
                }
            )
    return patterns


# --- Ascending Triangle ---
def detect_ascending_triangle(df, order=5, threshold=0.005):
    highs = df["high"].values
    lows = df["low"].values
    max_idx = argrelextrema(highs, np.greater, order=order)[0]
    patterns = []
    # Ищем горизонтальную линию сопротивления + восходящая поддержка
    for i in range(len(max_idx) - 1):
        y1, y2 = highs[max_idx[i]], highs[max_idx[i + 1]]
        if abs(y1 - y2) / y1 < threshold:
            # Линия поддержки: min между max_idx[i] и max_idx[i+1] растёт
            lows_segment = lows[max_idx[i] : max_idx[i + 1] + 1]
            if len(lows_segment) > 2 and lows_segment[0] < lows_segment[-1]:
                patterns.append(
                    {
                        "type": "AscendingTriangle",
                        "indices": [max_idx[i], max_idx[i + 1]],
                        "direction": "bullish",
                    }
                )
    return patterns


# --- Descending Triangle ---
def detect_descending_triangle(df, order=5, threshold=0.005):
    highs = df["high"].values
    lows = df["low"].values
    min_idx = argrelextrema(lows, np.less, order=order)[0]
    patterns = []
    # Ищем горизонтальную поддержку + падающее сопротивление
    for i in range(len(min_idx) - 1):
        y1, y2 = lows[min_idx[i]], lows[min_idx[i + 1]]
        if abs(y1 - y2) / y1 < threshold:
            highs_segment = highs[min_idx[i] : min_idx[i + 1] + 1]
            if len(highs_segment) > 2 and highs_segment[0] > highs_segment[-1]:
                patterns.append(
                    {
                        "type": "DescendingTriangle",
                        "indices": [min_idx[i], min_idx[i + 1]],
                        "direction": "bearish",
                    }
                )
    return patterns


# --- Symmetrical Triangle ---
def detect_symmetrical_triangle(df, order=5, threshold=0.02):
    highs = df["high"].values
    lows = df["low"].values
    max_idx = argrelextrema(highs, np.greater, order=order)[0]
    min_idx = argrelextrema(lows, np.less, order=order)[0]
    patterns = []
    # Для простоты ищем схождение high и low по расстоянию между экстремумами
    for i in range(min(len(max_idx), len(min_idx)) - 1):
        segment_high = highs[max_idx[i] : max_idx[i + 1] + 1]
        segment_low = lows[min_idx[i] : min_idx[i + 1] + 1]
        if len(segment_high) > 1 and len(segment_low) > 1:
            if (segment_high[0] > segment_high[-1]) and (
                segment_low[0] < segment_low[-1]
            ):
                patterns.append(
                    {
                        "type": "SymmetricalTriangle",
                        "indices": [
                            max_idx[i],
                            max_idx[i + 1],
                            min_idx[i],
                            min_idx[i + 1],
                        ],
                        "direction": "neutral",
                    }
                )
    return patterns


# --- Channel (Up/Down) ---
def detect_channel(df, order=5, min_length=10, threshold=0.01):
    highs = df["high"].values
    lows = df["low"].values
    max_idx = argrelextrema(highs, np.greater, order=order)[0]
    min_idx = argrelextrema(lows, np.less, order=order)[0]
    patterns = []
    if len(max_idx) > 1 and len(min_idx) > 1:
        # Прямые линии поддержки и сопротивления (почти параллельны)
        top_slope = (highs[max_idx[-1]] - highs[max_idx[0]]) / (
            max_idx[-1] - max_idx[0]
        )
        bot_slope = (lows[min_idx[-1]] - lows[min_idx[0]]) / (min_idx[-1] - min_idx[0])
        if abs(top_slope - bot_slope) / (abs(top_slope) + 1e-8) < threshold:
            if (
                abs(max_idx[-1] - max_idx[0]) > min_length
                and abs(min_idx[-1] - min_idx[0]) > min_length
            ):
                patterns.append(
                    {
                        "type": "Channel",
                        "indices": [max_idx[0], max_idx[-1], min_idx[0], min_idx[-1]],
                        "direction": "up" if top_slope > 0 else "down",
                    }
                )
    return patterns


# --- Другие паттерны реализовать при необходимости ---
# def detect_flag_pennant(df):
#     return []
# def detect_wedge(df):
#     return []
# def detect_rectangle(df):
#     return []
# def detect_cup_and_handle(df):
#     return []
# def detect_rounding_bottom(df):
#     return []
