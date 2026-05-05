"""
Performance metrics: Sharpe, Sortino, max drawdown, Calmar, hit rate.
All annualised assuming weekly returns (52 periods/year).
"""

import numpy as np
import pandas as pd

PERIODS_PER_YEAR = 52  # weekly strategy


def sharpe(returns: pd.Series, rf: float = 0.0) -> float:
    excess = returns - rf / PERIODS_PER_YEAR
    if excess.std() == 0:
        return 0.0
    return float(excess.mean() / excess.std() * np.sqrt(PERIODS_PER_YEAR))


def sortino(returns: pd.Series, rf: float = 0.0) -> float:
    excess = returns - rf / PERIODS_PER_YEAR
    downside = excess[excess < 0]
    if len(downside) == 0 or downside.std() == 0:
        return float("inf")
    return float(excess.mean() / downside.std() * np.sqrt(PERIODS_PER_YEAR))


def max_drawdown(returns: pd.Series) -> float:
    cum = (1 + returns).cumprod()
    rolling_max = cum.cummax()
    dd = (cum - rolling_max) / rolling_max
    return float(dd.min())


def calmar(returns: pd.Series) -> float:
    ann_return = float((1 + returns).prod() ** (PERIODS_PER_YEAR / len(returns)) - 1)
    mdd = abs(max_drawdown(returns))
    return ann_return / mdd if mdd > 0 else float("inf")


def hit_rate(returns: pd.Series) -> float:
    return float((returns > 0).mean())


def annualised_return(returns: pd.Series) -> float:
    return float((1 + returns).prod() ** (PERIODS_PER_YEAR / len(returns)) - 1)


def annualised_vol(returns: pd.Series) -> float:
    return float(returns.std() * np.sqrt(PERIODS_PER_YEAR))


def summary(returns: pd.Series, label: str = "Strategy") -> dict:
    return {
        "label": label,
        "ann_return": annualised_return(returns),
        "ann_vol": annualised_vol(returns),
        "sharpe": sharpe(returns),
        "sortino": sortino(returns),
        "max_drawdown": max_drawdown(returns),
        "calmar": calmar(returns),
        "hit_rate": hit_rate(returns),
        "n_periods": len(returns),
    }


def print_summary(returns: pd.Series, label: str = "Strategy") -> None:
    s = summary(returns, label)
    print(f"\n{'─'*40}")
    print(f"  {s['label']}")
    print(f"{'─'*40}")
    print(f"  Ann. Return   : {s['ann_return']:>8.2%}")
    print(f"  Ann. Vol      : {s['ann_vol']:>8.2%}")
    print(f"  Sharpe        : {s['sharpe']:>8.2f}")
    print(f"  Sortino       : {s['sortino']:>8.2f}")
    print(f"  Max Drawdown  : {s['max_drawdown']:>8.2%}")
    print(f"  Calmar        : {s['calmar']:>8.2f}")
    print(f"  Hit Rate      : {s['hit_rate']:>8.2%}")
    print(f"  Periods       : {s['n_periods']:>8d}")
    print(f"{'─'*40}\n")
