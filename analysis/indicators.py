import numpy as np
import pandas as pd


def add_basic_indicators(df, ema_periods=[20, 50], sma_periods=[20, 50], rsi_period=14):
    """
    Добавляет в DataFrame EMA, SMA и RSI (можно расширять под свои нужды)
    """
    for period in ema_periods:
        df[f"ema_{period}"] = df["close"].ewm(span=period, adjust=False).mean()
    for period in sma_periods:
        df[f"sma_{period}"] = df["close"].rolling(window=period).mean()
    df["rsi"] = compute_rsi(df["close"], window=rsi_period)
    df["volume_ma_20"] = df["volume"].rolling(window=20).mean()
    return df


def compute_rsi(series, window=14):
    """
    Быстрый RSI на numpy (без сторонних библиотек)
    """
    delta = series.diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(window=window).mean()
    avg_loss = pd.Series(loss).rolling(window=window).mean()
    rs = avg_gain / (avg_loss + 1e-10)
    rsi = 100 - (100 / (1 + rs))
    return rsi


def is_high_volume(row, volume_col="volume", ma_col="volume_ma_20", factor=1.3):
    """
    True, если объем выше скользящего среднего в X раз (по умолчанию 1.3)
    """
    return row[volume_col] > factor * row[ma_col]


def is_bullish_rsi(row, rsi_col="rsi", threshold=35):
    """
    True, если RSI указывает на перепроданность (бычий сигнал)
    """
    return row[rsi_col] < threshold


def is_bearish_rsi(row, rsi_col="rsi", threshold=65):
    """
    True, если RSI указывает на перекупленность (медвежий сигнал)
    """
    return row[rsi_col] > threshold


def is_above_ema(row, price_col="close", ema_col="ema_20"):
    """
    True, если цена выше EMA
    """
    return row[price_col] > row[ema_col]


def is_below_ema(row, price_col="close", ema_col="ema_20"):
    """
    True, если цена ниже EMA
    """
    return row[price_col] < row[ema_col]


# --- ATR (Average True Range) ---
def compute_atr(df, period=14):
    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift()).abs()
    low_close = (df["low"] - df["close"].shift()).abs()
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    atr = true_range.rolling(window=period).mean()
    return atr


# --- MACD (Moving Average Convergence Divergence) ---
def compute_macd(df, fast=12, slow=26, signal=9):
    exp1 = df["close"].ewm(span=fast, adjust=False).mean()
    exp2 = df["close"].ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    hist = macd - signal_line
    return macd, signal_line, hist


# --- Bollinger Bands ---
def compute_bollinger_bands(df, n=20, k=2):
    ma = df["close"].rolling(n).mean()
    std = df["close"].rolling(n).std()
    upper = ma + k * std
    lower = ma - k * std
    return upper, ma, lower


# --- Stochastic Oscillator ---
def compute_stochastic(df, k_period=14, d_period=3):
    low_min = df["low"].rolling(window=k_period).min()
    high_max = df["high"].rolling(window=k_period).max()
    k_fast = 100 * (df["close"] - low_min) / (high_max - low_min)
    d_slow = k_fast.rolling(window=d_period).mean()
    return k_fast, d_slow
