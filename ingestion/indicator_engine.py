import pandas as pd
import numpy as np


def compute_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute all technical indicators from daily OHLCV DataFrame.
    Input columns: date, open, high, low, close, volume, vwap
    Returns DataFrame with all indicators added.
    """
    df = df.copy().sort_values("date").reset_index(drop=True)
    df["date"] = pd.to_datetime(df["date"])

    # ── Moving Averages ────────────────────────────────────────────────
    for period in [20, 50, 200]:
        df[f"sma_{period}"] = df["close"].rolling(window=period).mean()
    for period in [12, 26, 50]:
        df[f"ema_{period}"] = df["close"].ewm(span=period,
                                               adjust=False).mean()

    # ── MACD ──────────────────────────────────────────────────────────
    df["macd_line"]      = df["ema_12"] - df["ema_26"]
    df["macd_signal"]    = df["macd_line"].ewm(span=9, adjust=False).mean()
    df["macd_histogram"] = df["macd_line"] - df["macd_signal"]

    # ── RSI (14) ──────────────────────────────────────────────────────
    df["rsi_14"] = _compute_rsi(df["close"], 14)

    # ── Stochastic %K / %D ────────────────────────────────────────────
    low_14  = df["low"].rolling(14).min()
    high_14 = df["high"].rolling(14).max()
    df["stoch_k"] = 100 * (df["close"] - low_14) / (high_14 - low_14 + 1e-10)
    df["stoch_d"] = df["stoch_k"].rolling(3).mean()

    # ── Williams %R ───────────────────────────────────────────────────
    df["williams_r"] = -100 * (high_14 - df["close"]) / (
        high_14 - low_14 + 1e-10)

    # ── CCI (20) ──────────────────────────────────────────────────────
    tp = (df["high"] + df["low"] + df["close"]) / 3
    df["cci_20"] = (tp - tp.rolling(20).mean()) / (
        0.015 * tp.rolling(20).apply(
            lambda x: np.mean(np.abs(x - x.mean())), raw=True))

    # ── MFI (14) ──────────────────────────────────────────────────────
    df["mfi_14"] = _compute_mfi(df, 14)

    # ── Bollinger Bands (20, 2σ) ──────────────────────────────────────
    sma_20 = df["close"].rolling(20).mean()
    std_20 = df["close"].rolling(20).std()
    df["bb_upper"]  = sma_20 + 2 * std_20
    df["bb_middle"] = sma_20
    df["bb_lower"]  = sma_20 - 2 * std_20
    df["bb_width"]  = (df["bb_upper"] - df["bb_lower"]) / (
        df["bb_middle"] + 1e-10)

    # ── ATR (14) ──────────────────────────────────────────────────────
    df["atr_14"]   = _compute_atr(df, 14)
    df["atr_pct"]  = df["atr_14"] / (df["close"] + 1e-10)

    # ── OBV ───────────────────────────────────────────────────────────
    df["obv"] = (np.sign(df["close"].diff()) * df["volume"]).fillna(0).cumsum()

    # ── VWAP (20-day rolling) ──────────────────────────────────────────
    df["vwap_20"] = (df["close"] * df["volume"]).rolling(20).sum() / (
        df["volume"].rolling(20).sum() + 1e-10)

    # ── A/D Line ──────────────────────────────────────────────────────
    clv = ((df["close"] - df["low"]) - (df["high"] - df["close"])) / (
        df["high"] - df["low"] + 1e-10)
    df["ad_line"] = (clv * df["volume"]).cumsum()

    # ── CMF (20) ──────────────────────────────────────────────────────
    df["cmf_20"] = (clv * df["volume"]).rolling(20).sum() / (
        df["volume"].rolling(20).sum() + 1e-10)

    # ── Returns & Volatility ──────────────────────────────────────────
    df["daily_return"] = df["close"].pct_change()
    df["rolling_vol_20"] = df["daily_return"].rolling(20).std() * np.sqrt(252)
    df["rolling_vol_60"] = df["daily_return"].rolling(60).std() * np.sqrt(252)

    return df


def _compute_rsi(series: pd.Series, period: int) -> pd.Series:
    delta = series.diff()
    gain  = delta.clip(lower=0).rolling(period).mean()
    loss  = (-delta.clip(upper=0)).rolling(period).mean()
    rs    = gain / (loss + 1e-10)
    return 100 - (100 / (1 + rs))


def _compute_mfi(df: pd.DataFrame, period: int) -> pd.Series:
    tp  = (df["high"] + df["low"] + df["close"]) / 3
    rmf = tp * df["volume"]
    pos = rmf.where(tp > tp.shift(1), 0)
    neg = rmf.where(tp < tp.shift(1), 0)
    mfr = pos.rolling(period).sum() / (neg.rolling(period).sum() + 1e-10)
    return 100 - (100 / (1 + mfr))


def _compute_atr(df: pd.DataFrame, period: int) -> pd.Series:
    hl  = df["high"] - df["low"]
    hpc = (df["high"] - df["close"].shift(1)).abs()
    lpc = (df["low"]  - df["close"].shift(1)).abs()
    tr  = pd.concat([hl, hpc, lpc], axis=1).max(axis=1)
    return tr.rolling(period).mean()
