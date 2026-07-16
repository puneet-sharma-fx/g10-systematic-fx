# Systematic Fixed Income Strategies: A Comprehensive Reference for Quantitative Traders

**Author:** Senior Quant Researcher  
**Date:** July 2026  
**Audience:** Experienced discretionary macro/FX traders transitioning to systematic approaches  
**Status:** Reference document for NotebookLM — comprehensive textbook-level treatment

---

## Table of Contents

1. [The Fixed Income Universe for Systematic Traders](#section-1)
2. [Fixed Income Return Decomposition](#section-2)
3. [Yield Curve Strategies](#section-3)
4. [Fixed Income Carry — The Factor](#section-4)
5. [Fixed Income Momentum](#section-5)
6. [Fixed Income Value](#section-6)
7. [Inflation-Linked Bond Strategies](#section-7)
8. [Corporate Bond / Credit Spread Systematic Strategies](#section-8)
9. [Fixed Income Risk Management](#section-9)
10. [Building a Multi-Signal Fixed Income Strategy for G10](#section-10)

---

## Section 1: The Fixed Income Universe for Systematic Traders {#section-1}

### 1.1 Why Fixed Income Is Different — and Better — for Systematic Trading

Fixed income is arguably the most systematic-friendly asset class in existence. The reasons are structural. Unlike equities, where valuation involves judgment about future earnings streams that can be fabricated or mispriced by management accounting, a bond has a contractually specified cash flow: you know exactly what you will receive and when. This mechanistic clarity generates a richer set of analytical relationships than any other asset class: the yield curve, duration, convexity, carry, roll-down, and term premia all have precise mathematical definitions. These relationships become the raw inputs for systematic signals.

For a discretionary macro/FX trader, many of the concepts are already intuitive — rate differentials drive FX, yield curves signal recession or expansion, credit spreads widen in stress. The challenge in going systematic is to make these relationships precise, measurable, and tradable across time and geography, with defined position sizing and risk limits.

The other reason fixed income is attractive: it is the largest financial market on earth. The US Treasury market alone trades approximately $900 billion per day (SIFMA 2024 data), making it near-frictionless for institutional position sizes. Even mid-tier G10 markets like Australian Commonwealth Government Bonds (ACGBs) or Canadian Government Bonds trade hundreds of millions daily, with futures providing leveraged exposure at minimal cost.

### 1.2 Asset Classes

**Government Bonds (G10).** The core universe for macro systematic strategies. Key markets:

| Country | Market Name | 10Y Futures Ticker | Typical Daily ADV |
|---|---|---|---|
| United States | US Treasuries | TY (10Y), TU (2Y), US (30Y) on CME | ~$900B cash + $200B futures |
| Germany | Bunds | FGBL (Bund 10Y), FGBS (Schatz 2Y) on Eurex | ~€120B |
| United Kingdom | Gilts | G (Long Gilt) on ICE | ~£50B |
| Japan | JGBs | JGB futures on TSE | ~¥4T |
| Australia | ACGBs | XT (10Y) on ASX | ~A$20B |
| Canada | GoCs | CGB (10Y) on MX | ~C$20B |
| France | OATs | FOAT (OAT 10Y) on Eurex | ~€50B |
| Sweden | SGBs | Swedish Government Bond futures | ~SEK 15B |
| Norway | NRBs | Norwegian Government bonds | ~NOK 5B |
| New Zealand | NZGBs | NZ Government Bond futures | ~NZ$3B |

**Corporate Bonds.** Investment grade (IG) and high yield (HY) US and European corporate bonds. Less liquid than govvies, but systematic exposure is achieved through CDX and iTraxx indices. IG corporate bonds typically have investment-grade credit ratings (BBB- and above); HY bonds are rated BB+ and below.

**Agency MBS (Mortgage-Backed Securities).** US Fannie Mae, Freddie Mac, and Ginnie Mae pass-through securities. The TBA (To-Be-Announced) market provides standardized systematic exposure. Significant embedded optionality (prepayment risk) means MBS carry is more complex than straight bond carry.

**Emerging Market Debt.** Hard-currency EM sovereign bonds (JPMorgan EMBI) and local-currency EM bonds (JPMorgan GBI-EM). These provide higher carry but embed FX risk, sovereign credit risk, and lower liquidity. Systematic EM bond strategies are typically run separately from G10 due to structurally different dynamics.

**Inflation-Linked Bonds.** US TIPS, UK index-linked gilts, German Bunds indexed to HICPx, French OATi. These instruments provide direct systematic exposure to inflation expectations and real yields (Section 7).

### 1.3 Instruments for Systematic Exposure

**Futures.** The cleanest instrument for systematic strategies. Standardized, exchange-traded, excellent liquidity for the front three contracts, minimal counterparty risk, direct leverage, simple rolling mechanics. The roll yield on bond futures is explicit and calculable. Futures embed the cheapest-to-deliver (CTD) dynamic: the short side delivers the bond that is cheapest given the conversion factor, creating a subtle but manageable pricing wrinkle.

**Cash Bonds.** Required for carry strategies that need the actual coupon and repo. Also required for specific on-the-run / off-the-run relative value trades. More operationally complex: settlement, custody, repo financing required.

**Interest Rate Swaps (IRS).** Fixed-for-floating rate exchanges. A 10Y USD swap — pay fixed at 4.5%, receive SOFR — is economically similar to shorting a 10Y Treasury but without the CTD optionality. Swaps are OTC and require ISDA agreements. The swap spread (swap rate minus Treasury yield) is itself a systematic signal (discussed in Section 8).

**Overnight Index Swaps (OIS).** Swaps referencing overnight rates (SOFR in USD, ESTR in EUR, SONIA in GBP, TONA in JPY). These are the cleanest measure of rate expectations since they contain no term premium and minimal credit risk. The difference between OIS rates and bond yields isolates the term premium.

**Credit Default Swaps (CDS).** Protection on a single name or index. The buyer pays a premium (the spread, in bps) and receives par in the event of default. CDX indices (investment-grade: CDX.NA.IG, high-yield: CDX.NA.HY) provide systematic liquid exposure to credit spreads. iTraxx is the European equivalent.

**Swaptions.** Options on interest rate swaps. These provide exposure to interest rate volatility (swaption vol). The swaption vol surface — across expiry and tenor — is a rich source of information about the market's uncertainty around the rate path. Swaption strategies are more complex but used by sophisticated systematic shops for carry in volatility.

### 1.4 The Central Bank Problem: QE/QT Regimes

The single most important regime variable in fixed income systematic strategies is the central bank balance sheet stance. Quantitative Easing (QE) — large-scale asset purchases by central banks — distorts nearly every fixed income signal:

1. **Duration carry is suppressed.** When the Fed or ECB owns 30-40% of the market, term premia collapse toward zero or negative. The carry signal says "hold duration" but the source of carry has been artificially compressed.

2. **Momentum is truncated.** Rate trends that would normally persist are truncated by central bank intervention. The 2010-2021 period saw structurally suppressed volatility in rates as QE anchored the front end.

3. **Cross-country rate differentials compress.** Global QE programs drove convergence in G10 yields, reducing the dispersion that cross-country carry signals depend on.

4. **Roll-down is distorted.** Flat yield curves (QE tends to flatten curves) reduce roll-down income.

**How to handle this:**

- **Regime detection:** Use the central bank balance sheet as a % of GDP as a regime variable. Above 30-35% (Fed peak was ~36%), dampen carry and momentum signals by 30-50%.
- **Volatility conditioning:** During QE regimes, realized vol is lower, so vol-scaling naturally reduces position size.
- **Slope conditioning:** Treat the 2s10s slope as a carry quality indicator. Slopes below 50bps suppress carry signals.
- **Model the spread, not the level:** Cross-country spreads are less distorted than absolute yield levels during global QE (different QE magnitudes create dispersion).

The 2022-2024 Quantitative Tightening (QT) period partially restored the pre-GFC dynamics: steeper curves, higher carry, stronger momentum, and wider cross-country dispersion. This "regime normalization" substantially improved systematic FI strategy performance in 2022-2024 relative to 2015-2021.

---

## Section 2: Fixed Income Return Decomposition {#section-2}

### 2.1 Total Return on a Bond

The total return on a bond over a holding period $[t, t+\Delta t]$ has three components:

$$
TR = \underbrace{\text{Coupon Income}}_{\text{carry}} + \underbrace{\Delta P}_{\text{capital gain/loss}} + \underbrace{\text{Roll-down}}_{\text{curve income}}
$$

For a bond with face value $F$, coupon $c$, yield $y$, and modified duration $D^*$:

$$
TR \approx c \cdot \Delta t - D^* \cdot \Delta y + \text{Convexity} \cdot (\Delta y)^2 + \text{Roll-down}
$$

Each term has a distinct systematic signal implication.

### 2.2 Duration and Modified Duration

**Macaulay Duration** ($D$): the weighted average time to receipt of cash flows, where weights are the present values of each cash flow:

$$
D = \frac{\sum_{t=1}^{T} t \cdot \frac{CF_t}{(1+y)^t}}{\sum_{t=1}^{T} \frac{CF_t}{(1+y)^t}} = \frac{\sum_{t=1}^{T} t \cdot PV(CF_t)}{P}
$$

**Modified Duration** ($D^*$): the sensitivity of bond price to a change in yield, annualized:

$$
D^* = \frac{D}{1 + y/m}
$$

where $m$ is the number of coupon payments per year. For a zero-coupon bond, $D = T$ and $D^* = T/(1+y)$.

The first-order price-yield relationship:

$$
\frac{dP}{dy} = -D^* \cdot P
\quad \Rightarrow \quad
\frac{\Delta P}{P} \approx -D^* \cdot \Delta y
$$

**Practical examples:**
- A 10Y on-the-run Treasury with 4.5% coupon has approximately $D^* \approx 8.0$ years
- A 30Y Treasury bond: $D^* \approx 18$–19 years
- A 2Y Treasury note: $D^* \approx 1.9$ years

### 2.3 Convexity

Duration is a linear approximation. For large yield moves, the second-order correction (convexity) matters:

$$
\frac{\Delta P}{P} \approx -D^* \cdot \Delta y + \frac{1}{2} \cdot C \cdot (\Delta y)^2
$$

where convexity $C$ is:

$$
C = \frac{1}{P \cdot (1+y)^2} \sum_{t=1}^{T} t(t+1) \cdot \frac{CF_t}{(1+y)^t}
$$

Convexity is always positive for straight bonds: this means bonds gain more in price when yields fall than they lose when yields rise by the same amount. Long bond positions are always "long convexity" — a valuable property in tail scenarios. Mortgage bonds have negative convexity due to prepayment: they lose duration when rates fall (homeowners refinance), creating a significant systematic complication.

**For systematic traders:** In a volatility-scaled portfolio, convexity means your actual P&L will outperform the linear duration approximation in large moves. This is a positive asymmetry. However, for options and swaptions written on rates, the reverse applies.

### 2.4 DV01: The Core Risk Metric

**Dollar Value of a Basis Point (DV01)** is the change in the dollar value of a position for a 1bp (0.01%) move in yield:

$$
DV01 = -\frac{dP}{dy} \cdot \frac{1}{10000} = D^* \cdot P \cdot \frac{1}{10000}
$$

For a $1M position in a 10Y Treasury with $D^* = 8$ and price = $100:

$$
DV01 = 8 \times \$1{,}000{,}000 \times 0.0001 = \$800
$$

This means a 1bp move in the 10Y yield generates ±$800 of P&L on that $1M position.

DV01 is the universal currency of fixed income risk management. All positions across maturities and countries are expressed in DV01 equivalents for aggregation. A $1M position in a 2Y note ($D^* \approx 1.9$) has DV01 ≈ $190 — much smaller risk than the same dollar amount in the 10Y.

### 2.5 Carry in Fixed Income

**Carry** for a bond is the expected return if yields remain unchanged. It has three components:

$$
\text{Carry} = \underbrace{y_{10Y}}_{\text{yield income}} - \underbrace{r_{repo}}_{\text{financing cost}} + \underbrace{\text{Roll-down}}_{\text{curve income}}
$$

**Roll-down** arises because as time passes, a bond moves to a shorter point on the yield curve. If the curve is upward-sloping and stable, the bond "rolls down" to a lower yield, generating a price gain. For a 10Y bond:

$$
\text{Roll-down} \approx (y_{10Y} - y_{9Y}) \cdot D^*_{10Y}
$$

In a steep curve environment (e.g., 10Y at 4.5%, 9Y at 4.3%), the roll-down adds approximately 20bps × 8 = 160bps/year to total return.

**Why FI carry is more complex than FX carry:**

- **Repo rates vary by collateral.** On-the-run Treasuries trade "special" in repo — they can be financed at rates 50-100bps below the GC (general collateral) repo rate because they are in high demand as collateral. This creates a negative carry surprise if you're funding at GC but the bond goes "on special."
- **Term premium.** FX carry captures the interest rate differential directly. FI carry also depends on the term premium embedded in the yield — part of the carry may reflect compensation for duration risk, not purely rate expectations. The realized carry may differ from the expected carry if the term premium changes.
- **Supply dynamics.** Heavy issuance (Treasury auctions) can temporarily cheapen specific points on the curve, creating apparent carry that reverses post-auction.
- **Cross-country repo rates.** In a cross-country carry strategy, you must compare financing costs in each jurisdiction (SOFR in USD, ESTR in EUR, SONIA in GBP, TONA in JPY).

### 2.6 Python: Computing Carry and Roll-Down for a 10Y Treasury

```python
import numpy as np
import pandas as pd

def bond_carry_rolldown(
    yield_10y: float,   # 10Y yield (decimal, e.g. 0.045)
    yield_9y: float,    # 9Y yield for roll-down calculation
    repo_rate: float,   # Repo rate (decimal, e.g. 0.053)
    modified_duration_10y: float = 8.0,
    holding_period_years: float = 1/12,  # 1 month
) -> dict:
    """
    Compute the carry and roll-down for a 10Y Treasury position.
    
    Returns annualized carry components in bps.
    """
    # Annualized coupon income net of financing
    net_carry_bps = (yield_10y - repo_rate) * 100 * 100  # in bps
    
    # Roll-down: movement along the yield curve over the holding period
    # As the 10Y bond ages by 'holding_period_years', it becomes a (10-h)Y bond
    # Approximation: use the slope between 9Y and 10Y
    yield_slope_per_year = (yield_10y - yield_9y)  # bps per year of maturity
    roll_down_yield_change = yield_slope_per_year * holding_period_years
    
    # Roll-down price return = -Duration * yield_change (but yield decreases as we roll down)
    roll_down_price_return = modified_duration_10y * roll_down_yield_change
    roll_down_bps = roll_down_price_return * 100 * 100  # annualized bps
    roll_down_bps_annualized = roll_down_bps / holding_period_years
    
    # Total carry (annualized, bps)
    total_carry_bps = net_carry_bps + roll_down_bps_annualized
    
    return {
        "yield_income_bps": yield_10y * 10000,
        "repo_cost_bps": repo_rate * 10000,
        "net_carry_bps": net_carry_bps,
        "roll_down_bps_annualized": roll_down_bps_annualized,
        "total_carry_bps_annualized": total_carry_bps,
        "dv01_per_million": modified_duration_10y * 1_000_000 / 10000,
    }


# Example: US Treasury 10Y in mid-2024 environment
result = bond_carry_rolldown(
    yield_10y=0.0440,   # 10Y at 4.40%
    yield_9y=0.0430,    # 9Y at 4.30% (slight upslope at long end)
    repo_rate=0.0530,   # GC repo at 5.30% (Fed Funds at 5.25-5.50%)
    modified_duration_10y=8.1,
)

print("=== US Treasury 10Y Carry Analysis ===")
for k, v in result.items():
    print(f"  {k}: {v:.1f}")

# Output:
# yield_income_bps: 440.0
# repo_cost_bps: 530.0
# net_carry_bps: -90.0  <-- NEGATIVE: inverted curve, carry is negative!
# roll_down_bps_annualized: 81.0
# total_carry_bps_annualized: -9.0  <-- Near-zero carry in 2024 10Y
# dv01_per_million: 810.0
```

This example illustrates a crucial point: in an inverted yield curve environment (2023-2024), 10Y bonds had negative carry versus repo. The roll-down partially offset this, but total carry was near zero or negative — the signal was to be short duration or at least underweight.

---

## Section 3: Yield Curve Strategies {#section-3}

### 3.1 Level Strategies: Duration Bets

The most basic systematic FI strategy bets on the overall level of interest rates — i.e., it takes a long or short position in duration. A long duration position gains when yields fall; a short duration position gains when yields rise.

**Signal 1: Taylor Rule Deviation**

The Taylor Rule provides a fundamental-value anchor for short-term rates:

$$
r^* = r_{neutral} + \pi + a_\pi(\pi - \pi^*) + a_y(y_{output} - y^*)
$$

Standard Taylor (1993) coefficients: $a_\pi = 0.5$, $a_y = 0.5$, $r_{neutral} = 2\%$, $\pi^* = 2\%$.

When actual rates are significantly below the Taylor rate, rates are "too low" — short duration. When actual rates are above the Taylor rate, rates are "too high" — long duration. This signal works best on a 6-12 month horizon as the market slowly incorporates fundamental mispricing.

**Signal 2: Growth-Inflation Composite**

$$
z_{carry} = \alpha \cdot z(\text{ISM New Orders}) + \beta \cdot z(\text{Core CPI YoY}) - \gamma \cdot z(\text{10Y yield})
$$

When growth is slowing and inflation is falling (negative composite), rate cuts are likely — long duration. When growth is strong and inflation is rising, rate hikes are likely — short duration.

**Evidence: Ilmanen (1995)**

Antti Ilmanen's seminal paper "Time-Varying Expected Returns in International Bond Markets" (Journal of Finance, 50(2), 1995, pp. 481-506) showed that a small set of global instruments can forecast 4-12% of monthly variation in excess bond returns across six countries. The key predictors are:
1. The term spread (steep curve → higher future returns)
2. The real short rate
3. Global (US) bond market return

This evidence is foundational: yield curve slope is a systematic predictor of bond market returns, not just an indicator of monetary policy expectations.

**The "Riding the Yield Curve" Strategy**

If the yield curve is upward-sloping and you believe it will remain stable, you can enhance returns by:
1. Buying a longer maturity than your target holding period
2. Selling it after a holding period as a shorter maturity instrument at a lower yield

A 5Y investor who buys a 10Y bond (yielding 4.4%) and sells it as a 9Y bond (yielding 4.3%) earns the 4.4% coupon but also gains the 10bp yield decline × duration ≈ 80bps price appreciation. Total return: ~5.2% vs. 4.3% for simply buying a 5Y bond. This is the institutionalized form of roll-down carry.

### 3.2 Slope Strategies: 2s10s and 5s30s

**The Yield Curve Steepener/Flattener Trade**

A steepener is long the short end (2Y, receives fixed) and short the long end (10Y, pays fixed), DV01-neutral. It profits when the 2s10s spread widens. A flattener is the reverse.

A DV01-neutral 2s10s steepener for $10M notional:
- Long $10M 2Y notes: DV01 ≈ $1,900
- Short $X 10Y notes such that DV01 matches: X = 1,900 / 810 ≈ $2.35M of 10Y

Position sizing is based on matching DV01, not notional.

**Key Signals for Curve Slope:**

| Signal | Steep Curve Direction | Flat/Inverted Direction |
|---|---|---|
| Economic cycle position | Early expansion | Late cycle / recession imminent |
| Fed stance | Easing (cutting FF rate) | Hiking (FF rate rises faster than 10Y) |
| Fiscal deficit size | Large deficits → term premium | Fiscal contraction |
| Current slope vs. historical | At the 10th percentile of history | At the 90th percentile |
| Recession probability | Low (steep) | High (flat/inverted) |
| Inflation expectations | Low | Rising unexpectedly |

**Bull vs. Bear Steepening — Why the Mechanism Matters**

A critical distinction for systematic traders:

- **Bull steepening:** 2Y yields fall faster than 10Y yields. Occurs when the market expects rate cuts. Both ends of the position profit, but the 2Y move is larger in bps. This is the most tradable and consistent form.
- **Bear steepening:** 10Y yields rise faster than 2Y yields. Occurs when the market fears fiscal problems, rising term premium, or hawkish policy. The 2Y stays anchored while the 10Y sells off. In a DV01-neutral steepener, the short 10Y position profits more than the long 2Y position loses.
- **Bull flattening:** 10Y falls faster than 2Y. Classic late-cycle recession fear. The 10Y rally dominates.
- **Bear flattening:** 2Y rises faster than 10Y (the Fed hikes aggressively while long-end remains anchored). This was the dominant 2022 dynamic.

**Case Studies:**

*2019 Inversion:* The 2s10s spread inverted in August 2019 (first time since 2007), reaching -50bps. A systematic steepener signal (buy 2Y, sell 10Y) triggered by the deeply inverted curve. The curve fully re-steepened from -50bps to +70bps by early 2021 — a 120bp move generating substantial P&L in the DV01-neutral trade.

*2022-2023 Bear Flattener:* The Fed hiked from 0.25% to 5.25-5.50% in the fastest hiking cycle since 1980. The 2Y yield rose from 0.73% (Jan 2022) to 5.1% (Oct 2023), a 438bp move. The 10Y moved from 1.5% to 5.0%, a 350bp move. The 2Y moved more — a bear flattener, then briefly inverted (2s10s at -108bps in July 2023, the deepest inversion since 1981). Duration positions were severely punished; curve positions with proper hedge ratios were more manageable.

### 3.3 Curvature Strategies: Butterflies

A butterfly trade is a position that is simultaneously long in two tenors and short in a third (or vice versa), structured to be both DV01-neutral and duration-neutral.

**Standard 2Y-5Y-10Y Butterfly (long wings, short belly):**
- Long 2Y: DV01 = X
- Short 5Y: DV01 = 2X (body — doubled so the two wings balance it)
- Long 10Y: DV01 = X

Net DV01 = X - 2X + X = 0. Net duration = approximately zero. The position profits when the 5Y point cheapens relative to the interpolation between 2Y and 10Y — i.e., when the curve becomes more "humped" at the belly, or when the belly richens beyond fair value.

**The Butterfly Signal: Relative Richness**

Define the 5Y "butterfly value" as:

$$
\text{BFY}_{5Y} = y_{5Y} - \left[\frac{y_{2Y} \cdot (10-5) + y_{10Y} \cdot (5-2)}{10-2}\right]
$$

A negative BFY (5Y yield below the linear interpolation) means the belly is "rich" (expensive) — the signal is to short the belly (pay fixed in 5Y swap) and long the wings. A positive BFY means the belly is "cheap" — long the belly.

The z-score of BFY over a 1-2 year rolling window is the systematic signal: enter when |z| > 1.5, exit when |z| < 0.5.

**Flight-to-Quality Effect on the Belly**

In risk-off episodes, investors disproportionately buy 5Y and 10Y Treasuries (the most liquid on-the-run points). This can temporarily compress the belly. The systematic signal correctly identifies this as richness and positions for mean reversion — but this mean reversion can take 6-12 months in sustained risk-off environments, requiring careful position sizing.

### 3.4 Cross-Country Yield Curve Strategies

**The US-Germany 2Y Spread as EURUSD Predictor**

The 2Y US-Germany yield spread is one of the most robust systematic predictors of EURUSD. When the 2Y US yield rises relative to the 2Y German Schatz yield (spread widens), the USD strengthens versus EUR. This mechanism is:

1. The 2Y spread reflects expected Fed-ECB rate differential over the next 2 years
2. Covered interest rate parity (CIP) anchors the relationship mechanically
3. Deviations from CIP in the short run (driven by risk appetite) create systematic trading opportunities

The mathematical relationship:

$$
\Delta EURUSD_t \approx -\beta \cdot (y^{US}_{2Y,t} - y^{DE}_{2Y,t}) + \varepsilon_t
$$

where $\beta \approx 0.3$-$0.5$ (each 100bp of 2Y spread favoring USD corresponds to roughly 3-5% USD appreciation at 3-6M horizon).

**G10 Rate Differential Matrix**

A systematic approach constructs the full pairwise rate differential matrix across G10 countries. The z-score of each bilateral spread (relative to its 2-year rolling history) becomes a signal for the corresponding FX cross:

| Country | USD | EUR | GBP | JPY | CHF | AUD | CAD | NOK | SEK | NZD |
|---|---|---|---|---|---|---|---|---|---|---|
| USD | — | 2Y spread | 2Y spread | 2Y spread | 2Y spread | 2Y spread | 2Y spread | 2Y spread | 2Y spread | 2Y spread |
| EUR | 2Y spread | — | 2Y spread | 2Y spread | 2Y spread | 2Y spread | 2Y spread | ... | ... | ... |

Each cell represents the bilateral 2Y yield spread and its z-score signal for the corresponding FX pair. This matrix approach naturally combines with the FX carry and momentum signals in a multi-signal framework.

**Cross-Country Carry in Rates: Bund vs. Treasury Relative Value**

The Bund-Treasury spread (10Y) has historically oscillated in a range determined by:
- Relative inflation expectations (US higher inflation → wider spread)
- Relative QE programs (ECB QE > Fed QE → Bund yields artificially low → wider spread)
- Safe-haven premium (Bund has European safe-haven premium; Treasury has global safe-haven premium)
- Fiscal deficit differentials (US larger deficits → higher term premium → wider spread)

A z-score of the 10Y US-Germany spread beyond ±1.5 standard deviations generates a mean-reversion signal. Entry with a DV01-neutral position: long Bund futures, short Treasury futures (or vice versa), hedged for currency exposure.

---

## Section 4: Fixed Income Carry — The Factor {#section-4}

### 4.1 The Carry Factor: Definition

The carry of a financial asset is the expected return if market prices stay constant. For a government bond, carry is:

$$
\text{Carry}_{country} = y_{10Y} - r_{repo} + \text{Roll-down}
$$

In the cross-country setting, carry is computed for each G10 government bond market relative to its local financing rate, then sorted. The strategy: long the highest-carry bond markets, short the lowest-carry bond markets, currency-hedged to isolate the rates signal from FX risk.

**The Koijen-Moskowitz-Pedersen-Vrugt (2018) Framework**

The seminal paper "Carry" (Journal of Financial Economics, 127(2), 2018, pp. 197-225) by Ralph Koijen, Tobias Moskowitz, Lasse Pedersen, and Evert Vrugt established a unified framework for carry across asset classes. Their key findings for fixed income:

- Global fixed income carry (long high-carry bond markets, short low-carry) generates a Sharpe ratio of approximately 0.6-0.9 gross of transaction costs
- The global carry strategy (combining equities, FX, commodities, fixed income) achieves a Sharpe of ~0.9 through diversification
- Fixed income carry has low correlation with equity carry and commodity carry, providing genuine diversification
- Carry timing (scaling carry exposure by the expected carry level) further improves the Sharpe by ~30%

### 4.2 Carry Return Decomposition

$$
\text{Return}_{bond, t} = \underbrace{(y_{10Y,t} - r_{repo,t})}_{\text{net carry}} + \underbrace{\Delta\text{Roll-down}_t}_{\text{curve income}} - \underbrace{D^* \cdot \Delta y_{unexp}}_{\text{surprise yield change}}
$$

The carry component is known ex-ante. The surprise yield change is the risk that the carry trader bears. The expected Sharpe ratio from carry is approximately:

$$
SR_{carry} \approx \frac{E[\text{Carry}]}{\sigma(\Delta y) \cdot D^*}
$$

For a typical 10Y bond: $E[\text{Carry}] \approx 80bps$, $\sigma(\Delta y) \approx 60bps/year$, $D^* \approx 8$. This gives:

$$
SR_{carry} \approx \frac{0.80\%}{0.60\% \times 8} = \frac{0.80\%}{4.80\%} \approx 0.17
$$

This is a low Sharpe on a single bond. The power comes from diversification across 10 G10 markets and signal aggregation with momentum and value.

### 4.3 Cross-Country Carry: Implementation

```python
import pandas as pd
import numpy as np

def fi_carry_signal(
    yields_10y: pd.DataFrame,    # shape: (T, N) — N countries, T time periods
    repo_rates: pd.DataFrame,    # shape: (T, N) — local overnight rates
    rolldown_10y_9y: pd.DataFrame = None,  # optional: 10Y - 9Y yield slope
    modified_duration: float = 8.0,
    z_score_window: int = 252,
    cross_sectional: bool = True,
) -> pd.DataFrame:
    """
    Compute cross-country fixed income carry signal.
    
    For each country, carry = yield - repo + roll_down
    Signal = cross-sectional z-score if cross_sectional=True,
             else time-series z-score
    
    Returns: signal DataFrame (T, N) with values roughly in [-3, +3]
    """
    # Net carry
    net_carry = yields_10y - repo_rates
    
    # Add roll-down if provided (annualized)
    if rolldown_10y_9y is not None:
        roll_down = rolldown_10y_9y * modified_duration
        total_carry = net_carry + roll_down
    else:
        total_carry = net_carry
    
    if cross_sectional:
        # Cross-sectional z-score: rank each country vs all others at time t
        cs_mean = total_carry.mean(axis=1)
        cs_std = total_carry.std(axis=1)
        signal = total_carry.sub(cs_mean, axis=0).div(cs_std, axis=0)
    else:
        # Time-series z-score: rank carry vs its own history
        ts_mean = total_carry.rolling(z_score_window).mean()
        ts_std = total_carry.rolling(z_score_window).std()
        signal = (total_carry - ts_mean) / ts_std
    
    # Clip to avoid extreme positions
    return signal.clip(-3, 3)


def compute_carry_returns(
    signal: pd.DataFrame,          # (T, N) signal
    bond_excess_returns: pd.DataFrame,  # (T, N) 1-month excess returns
    target_vol: float = 0.10,      # 10% annualized target vol
    rebal_freq: int = 21,          # monthly rebalancing
) -> pd.Series:
    """Combine carry signal with vol-scaling to produce strategy returns."""
    # Vol-scale the signal
    strat_vol = signal.shift(1).mul(bond_excess_returns).rolling(63).std() * np.sqrt(252)
    avg_strat_vol = strat_vol.mean(axis=1)
    vol_scale = (target_vol / avg_strat_vol).clip(0.5, 3.0)
    
    # Monthly rebalancing: only update signal every rebal_freq days
    signal_rebal = signal.copy()
    rows_to_keep = range(0, len(signal), rebal_freq)
    signal_rebal = signal_rebal.iloc[list(rows_to_keep)].reindex(signal.index, method='ffill')
    
    # Weighted portfolio: signal determines weights, vol-scaled
    weights = signal_rebal.div(signal_rebal.abs().sum(axis=1), axis=0)
    strategy_returns = weights.shift(1).mul(bond_excess_returns).sum(axis=1)
    
    return strategy_returns.mul(vol_scale.shift(1))
```

### 4.4 Conditional Carry: When Carry Works Best

The carry factor is not constant in quality. Carry works best when:

1. **Yield curves are steep.** A steep curve means high roll-down, which augments net carry. Signal quality improves when 2s10s > 100bps.
2. **Macro is growing at trend.** Carry fails when central banks rapidly reprice (hiking cycles, cutting cycles). During stable macro, yield shocks are small relative to carry income.
3. **Volatility is low.** The Sharpe of carry is inversely proportional to rate volatility. MOVE index below 100 → carry is productive. MOVE above 150 → carry is destruction-prone.
4. **Positioning is not crowded.** Speculative positioning data (COT reports on bond futures) can proxy for crowding.

### 4.5 Crowding Risk and the 2022 Carry Collapse

The 2022 experience is the most important case study in modern FI carry risk. Entering 2022, the FI carry trade was:
- Long high-yield G10 bond markets (Australia, New Zealand, Canada — all running higher rates post-COVID)
- Short low-yield markets (Japan, Switzerland, Germany — still near zero)
- The strategy had accumulated three years of positive carry (2019-2021)

Then central banks globally hiked aggressively. The key errors:
1. Carry was positive but the magnitude of the rate shock (10Y UST from 1.5% to 4.2% in 12 months) obliterated years of carry income
2. Crowding meant all players exited simultaneously, amplifying losses
3. Currency hedges didn't compensate — rate vol and FX vol rose together

**How to hedge FI carry:**

```python
def fi_carry_with_hedges(
    carry_signal: pd.DataFrame,
    move_index: pd.Series,        # MOVE = implied bond vol (bbg MOVE Index)
    slope_2s10s: pd.DataFrame,    # 2s10s slope per country
    cot_net_speculative: pd.DataFrame,  # CFTC CoT net position, normalized
    base_vol_target: float = 0.08,
) -> pd.DataFrame:
    """
    Carry signal with three hedges:
    1. Volatility scaling (MOVE-based)
    2. Slope conditioning (suppress when curve flat/inverted)
    3. Crowding discount (suppress when positioned too long)
    """
    # 1. Vol scalar: reduce exposure when bond implied vol is elevated
    move_norm = (move_index / move_index.rolling(252).mean()).clip(0.5, 2.5)
    vol_scalar = (1 / move_norm).clip(0.4, 1.5)
    
    # 2. Slope conditioning: reduce carry when curves are flat
    slope_scalar = (slope_2s10s / 100).clip(0, 2.0)  # suppress below 0bps, full above 200bps
    
    # 3. Crowding: reduce when net long is at extremes
    crowd_scalar = 1.0 - (cot_net_speculative.clip(0, 1) * 0.4)  # max 40% reduction
    
    # Combine scalars
    combined_scalar = vol_scalar.multiply(slope_scalar).multiply(crowd_scalar)
    
    return carry_signal.multiply(combined_scalar, axis=0)
```

---

## Section 5: Fixed Income Momentum {#section-5}

### 5.1 Time Series Momentum in Bond Futures

The same TSMOM framework that works in FX and commodities applies robustly to bond futures. The seminal paper is Moskowitz, Ooi, and Pedersen "Time Series Momentum" (Journal of Financial Economics, 104(2), 2012, pp. 228-250). The authors studied 58 liquid instruments across equities, currencies, commodities, and bonds. Bond futures were included: US Treasury (10Y, 30Y), German Bund, UK Gilt, Japanese JGB, and others.

Key findings:
- The past 12-month excess return of each instrument is a positive predictor of its future 1-month return
- The trend effect persists approximately 12 months and then partially reverses over 2-5 years (mean reversion)
- A diversified TSMOM portfolio across all 58 instruments achieved a gross Sharpe ratio of approximately 1.28
- Bond futures specifically show significant TSMOM, driven by the slow incorporation of monetary policy changes into long-end yields

**Why momentum exists in bonds:**

1. **Monetary policy inertia.** Central banks move in gradual cycles. A rate hiking cycle typically unfolds over 12-24 months. Each successive hike validates the prior move and drives further yield increases — a momentum cascade.

2. **Institutional anchoring.** Large fixed income investors (pension funds, insurance companies) with liability benchmarks are slow to adjust duration. Their inertia creates momentum.

3. **Inflation dynamics.** Inflation is highly autocorrelated. Rising inflation drives rising yields drives momentum in the short bond position.

4. **Herding in the long end.** Risk-off episodes drive large flows into long government bonds, creating momentum in both directions.

### 5.2 The TSMOM Signal for Bond Futures

```python
def tsmom_fi_signal(
    bond_futures_prices: pd.DataFrame,  # (T, N): N bond futures, T daily prices
    lookback_months: int = 12,
    signal_months: int = 1,             # holding period
    vol_scale: bool = True,
    vol_lookback_days: int = 63,        # vol estimation window
    vol_target_annual: float = 0.40,    # per-instrument vol target
) -> pd.DataFrame:
    """
    Time-series momentum signal for bond futures.
    
    Signal = sign(12-month return) for each bond future
    Vol-scaled to equalize risk contribution across instruments.
    """
    lookback_days = lookback_months * 21
    signal_days = signal_months * 21
    
    # 12-month returns
    returns_12m = bond_futures_prices.pct_change(lookback_days)
    
    # Sign of 12-month return = raw TSMOM signal
    raw_signal = np.sign(returns_12m)
    
    if vol_scale:
        # Daily returns for vol estimation
        daily_returns = bond_futures_prices.pct_change()
        
        # Realized vol (63-day rolling)
        realized_vol = daily_returns.rolling(vol_lookback_days).std() * np.sqrt(252)
        
        # Scale signal: position size = target_vol / realized_vol
        vol_scalar = (vol_target_annual / realized_vol).clip(0.5, 5.0)
        scaled_signal = raw_signal * vol_scalar
    else:
        scaled_signal = raw_signal
    
    return scaled_signal


# Example usage with actual market data (schematic)
countries = ['US_10Y', 'US_30Y', 'DE_BUND', 'GB_GILT', 'JP_JGB', 'AU_10Y', 'CA_10Y']

# Expected signal in different macro environments:
example_signals = {
    'early_2022_hiking': {
        'US_10Y': -1,   # Short: hiking cycle, momentum short bonds
        'US_30Y': -1,   # Short: same
        'DE_BUND': -1,  # Short: ECB also hiking eventually
        'GB_GILT': -1,  # Short: BoE hiking
        'JP_JGB': +1,   # Long: BoJ holding YCC, no hiking → bonds stable/rising
        'AU_10Y': -1,   # Short: RBA hiking
        'CA_10Y': -1,   # Short: BoC hiking
    },
    'late_2023_peak_rates': {
        'US_10Y': -1,   # Short: still rising yields through Oct 2023
        'DE_BUND': -1,  # Short: ECB near peak
        'JP_JGB': -1,   # Short: BoJ starting to move YCC
        'AU_10Y': +1,   # Long: rate expectations stabilizing
        'CA_10Y': +1,   # Long: BoC near peak
    }
}
```

### 5.3 The Optimal Lookback for Bond Momentum

Empirically, the 12-month lookback dominates for bond futures, consistent with other asset classes. This is not coincidental — monetary policy cycles typically unfold over 12-18 months, and the 12-month lookback captures the bulk of a complete hiking/cutting phase.

Shorter lookbacks (1-3 months) capture more noise and have higher turnover costs. Longer lookbacks (24-36 months) work but have slower signal decay and lower Sharpe. A blended approach (equal weight 3M, 6M, 12M signals) provides some robustness:

```python
def blended_tsmom(prices, lookbacks=[63, 126, 252], weights=[0.2, 0.3, 0.5]):
    """Blend multiple lookback TSMOM signals, weighted toward longer lookbacks."""
    signals = []
    for lb, w in zip(lookbacks, weights):
        ret = prices.pct_change(lb)
        daily_vol = prices.pct_change().rolling(63).std() * np.sqrt(252)
        sig = np.sign(ret) / daily_vol.clip(0.05, 0.50)
        signals.append(sig * w)
    return sum(signals)
```

### 5.4 When Fixed Income Momentum Fails: Momentum Crashes

Bond momentum has two primary failure modes:

**1. Sharp Policy Reversals.** When a central bank pivots unexpectedly, the momentum signal (e.g., short bonds in a hiking cycle) gets caught wrong-footed. The March 2019 Fed pivot (from hiking to cutting) caused a sharp bond rally that hit short-duration momentum positions. The 2019 experience illustrates that pivots happen faster than the 12-month lookback can adapt.

**2. Geopolitical Flight-to-Quality.** Sudden risk-off episodes (COVID March 2020, GFC 2008) generate massive bond rallies that contradict bearish momentum signals.

**Barroso and Santa-Clara (2015) — Crisis Management**

Pedro Barroso and Pedro Santa-Clara's paper "Momentum Has Its Moments" (Journal of Financial Economics, 116(1), 2015, pp. 111-120) showed that momentum risk is highly time-varying and predictable. The key insight: momentum crashes are concentrated in periods of high ex-ante volatility.

The fix: vol-scale momentum positions using recent realized volatility. Targeting constant realized volatility:
- Nearly eliminates momentum crashes
- Roughly doubles the Sharpe ratio of the raw momentum strategy
- The improvement is large because raw momentum is size-invariant (just a sign), while the losses in crashes are driven by large underlying volatility

This is already embedded in the code above via `vol_scale=True`. For bond futures, the MOVE index (implied vol) can further augment the realized vol scalar.

### 5.5 Cross-Sectional Momentum in Bonds

Beyond TSMOM, cross-sectional momentum ranks bond futures by their 12-month return and takes long positions in the top quintile and short positions in the bottom quintile. For a 7-country G10 bond universe:
- Long top 2 performers over 12M (DV01-normalized)
- Short bottom 2 performers over 12M (DV01-normalized)

This strategy has lower capacity than TSMOM (requires more turnover, smaller universe) but adds diversification.

**Combining FI Momentum with FX Momentum:**

Bond futures momentum and currency momentum are naturally diversifying. The correlation between TSMOM on G10 bond futures and TSMOM on G10 FX is historically 0.2-0.3. When rate trends are strong (bond momentum works well), FX is often driven by those same rate dynamics (FX momentum works too, but differently). In risk-off bond rallies, FX momentum may be in conflict (strong USD vs. bearish bond signal). This low correlation is exactly what multi-asset systematic strategies exploit.

---

## Section 6: Fixed Income Value {#section-6}

### 6.1 What Is "Fair Value" for a Bond Yield?

Unlike equities, where fair value involves predicting multi-decade cash flows, bond fair value has cleaner anchors:

1. **Expected short rates over the bond's life** (the expectations component)
2. **Term premium** — compensation for bearing duration risk

$$
y_{10Y} = \underbrace{\frac{1}{10}\sum_{i=0}^{9} E_t[r_{t+i}]}_{\text{expected short rates}} + \underbrace{TP_{10Y}}_{\text{term premium}}
$$

Each component provides a separate signal.

### 6.2 Taylor Rule Implied Rates

The Taylor Rule provides the fundamental anchor for expected short rates:

$$
r^*_t = 2\% + \pi_t + 0.5(\pi_t - 2\%) + 0.5(y_{output,t})
$$

For the expected short rate path, project GDP growth and inflation over 10 years using simple trend models, apply the Taylor Rule at each horizon, and discount the path into a fair-value 10Y yield. A simplified approach:

```python
def taylor_implied_10y(
    cpi_yoy: float,           # current CPI inflation, %
    gdp_output_gap: float,    # output gap estimate, %
    neutral_rate: float = 2.5,  # r* estimate
    pi_target: float = 2.0,
    alpha_pi: float = 0.5,
    alpha_y: float = 0.5,
    term_premium: float = 0.5,  # add 50bps for duration risk
) -> float:
    """
    Compute Taylor-implied 10Y yield.
    Returns fair value 10Y yield in percent.
    """
    taylor_short_rate = (neutral_rate + cpi_yoy 
                         + alpha_pi * (cpi_yoy - pi_target) 
                         + alpha_y * gdp_output_gap)
    
    # The 10Y yield ≈ Taylor short rate (assuming gradual convergence to neutral)
    # Plus term premium
    implied_10y = 0.5 * taylor_short_rate + 0.5 * neutral_rate + term_premium
    
    return implied_10y


# Cross-G10 value signal
def fi_value_signal(
    actual_yields_10y: pd.Series,   # current 10Y yields, indexed by country
    taylor_implied: pd.Series,       # Taylor-implied 10Y yields, indexed by country
) -> pd.Series:
    """
    Value z-score: z-score of (actual - implied) across countries.
    Positive z = yields too high (bond cheap) → long signal.
    Negative z = yields too low (bond rich) → short signal.
    """
    deviation = taylor_implied - actual_yields_10y  # positive = yields too low = bond rich
    z_score = (deviation - deviation.mean()) / deviation.std()
    return z_score  # long where z is most negative (actual >> implied = cheap bonds)
```

### 6.3 Term Premium Models

**The ACM Model (Adrian-Crump-Moench, NY Fed)**

The Adrian-Crump-Moench model (2013) is a five-factor, no-arbitrage affine term structure model estimated on US Treasury yields from 1961 to present. It decomposes the 10Y Treasury yield into:
- Expected average short rate over 10 years (the "pure expectations" component)
- Term premium: the residual compensation for bearing duration risk

The NY Fed publishes daily updates at: [https://www.newyorkfed.org/research/data_indicators/term-premia-tabs](https://www.newyorkfed.org/research/data_indicators/term-premia-tabs)

The ACMTP10 series (10Y term premium) is available for free on FRED (series: ACMTP10). This has become the reference measure cited in FOMC communications since 2020.

**Systematic use of term premium:**

- When term premium is at historical lows (near zero or negative, as in 2020-2021), carry is suppressed and mean-reversion in term premium is a risk signal
- When term premium rises rapidly (as in Sep-Oct 2023, the "Treasury Tantrum"), it creates a mean-reversion signal toward long duration
- A z-score of term premium over its 3-year rolling history, when below -1.5 standard deviations, predicts above-average subsequent bond returns

**The Kim-Wright Model**

The Kim-Wright model (Board of Governors, 2005) is an alternative affine term structure model also published by the Fed. It tends to produce lower term premium estimates than ACM. Using both as a committee — averaging ACM and Kim-Wright term premium estimates — provides a more robust signal.

### 6.4 TIPS Breakeven Inflation as Value Signal

$$
\text{Breakeven Inflation}_{10Y} = y^{nominal}_{10Y} - y^{TIPS}_{10Y}
$$

The breakeven represents the market's expected average CPI over 10 years, plus a small inflation risk premium. When breakeven inflation diverges significantly from survey expectations (e.g., University of Michigan 5-10Y inflation expectations, Cleveland Fed CPI estimates), it signals a value opportunity:

- **Breakeven too high vs. surveys:** Nominal bonds are cheap relative to TIPS — short breakeven (long nominal, short TIPS)
- **Breakeven too low vs. surveys:** TIPS are cheap — long breakeven (long TIPS, short nominal)

FRED data codes: DFII10 (10Y TIPS yield), T10YIE (10Y breakeven), T5YIFR (5Y5Y forward inflation).

---

## Section 7: Inflation-Linked Bond Strategies {#section-7}

### 7.1 What TIPS Are

Treasury Inflation-Protected Securities (TIPS) pay a fixed real coupon on an inflation-indexed principal. If CPI rises by 3%, the principal adjusts upward by 3%, and the fixed coupon is applied to this larger principal. At maturity, the holder receives the greater of par or the inflation-adjusted principal.

Key formula:

$$
\text{TIPS total return} = r_{real} + \pi_{realized} + (r_{real, t} - r_{real, t+1}) \cdot D^*_{real}
$$

The first term is the known real yield income. The second term is realized inflation (the indexation return). The third term is the capital gain/loss from changes in real yields.

**UK Index-Linked Gilts** are indexed to RPI (Retail Price Index, now CPIH transitioning). **German Bunds indexed to HICPx** (Harmonised Index ex-tobacco) work identically but for EUR inflation.

### 7.2 The Inflation Carry Trade

The carry of a TIPS position relative to a nominal bond is:

$$
\text{Inflation Carry} = r_{nominal} - r_{real} - E[\pi] = \text{BEI} - E[\pi]
$$

Where BEI is the breakeven inflation rate and $E[\pi]$ is the market's consensus inflation forecast.

When BEI < survey expectations: TIPS are undervalued; expected inflation exceeds the breakeven. **Long TIPS, short nominal Treasuries** extracts the mispricing.

When BEI > survey expectations by more than the risk premium (~30bps): Nominal bonds are cheap. **Short TIPS, long nominal.**

### 7.3 The Inflation Regime Signal

A robust systematic signal: compare 5Y CPI breakeven (FRED: T5YIE) to 12M trailing realized CPI:

```python
def inflation_regime_signal(
    breakeven_5y: pd.Series,     # FRED T5YIE
    cpi_realized_yoy: pd.Series, # 12M trailing CPI YoY (CPIAUCSL)
    survey_inflation: pd.Series, # e.g., Univ. Michigan 5-10Y expectations
    vol_window: int = 126,
) -> pd.Series:
    """
    Long TIPS (short nominal) when BEI < realized CPI or survey expectations.
    Short TIPS (long nominal) when BEI > survey by > 50bps (inflation risk premium).
    
    Returns: signal in [-1, +1] for TIPS vs nominal spread.
    Positive = long TIPS / short nominal
    Negative = short TIPS / long nominal
    """
    # Primary signal: BEI relative to realized CPI
    bei_vs_realized = cpi_realized_yoy - breakeven_5y  # positive = BEI too low = long TIPS
    
    # Secondary signal: BEI relative to survey expectations
    bei_vs_survey = survey_inflation - breakeven_5y - 0.30  # 30bps inflation risk premium
    
    # Composite (equal weight)
    composite = 0.5 * bei_vs_realized + 0.5 * bei_vs_survey
    
    # Z-score normalize
    z = (composite - composite.rolling(vol_window).mean()) / composite.rolling(vol_window).std()
    
    return z.clip(-2, 2)
```

**Historical performance of the inflation regime signal:**
- 2021: BEI was 2.3% while realized CPI printed 7% — strong long TIPS signal generated huge outperformance
- 2023: BEI at 2.4% while realized CPI moderated to 3.5% — signal moved toward neutral
- 2024-2025: BEI at 2.5-2.8%, CPI sticky above 3% → mildly positive TIPS signal persisted

### 7.4 Volatility Risk Premium in Inflation

The inflation market also exhibits a volatility risk premium. Implied inflation volatility (from options on CPI or swaptions on inflation swaps) exceeds realized inflation volatility on average. This is the systematic basis for selling inflation vol:

- Sell inflation options / inflation caps
- Collect vol risk premium
- Hedge the inflation direction with offsetting TIPS position

This strategy is more complex and typically available only to institutions with inflation derivatives capabilities.

### 7.5 Data Sources

| Series | FRED Code | Description |
|---|---|---|
| 10Y TIPS Yield | DFII10 | Real yield, 10Y constant maturity |
| 10Y Breakeven | T10YIE | 10Y nominal minus TIPS |
| 5Y Breakeven | T5YIE | 5Y nominal minus TIPS |
| 5Y5Y Forward BEI | T5YIFR | Forward 5Y inflation in 5Y |
| Cleveland Fed CPI | — | [Cleveland Fed website](https://www.clevelandfed.org/indicators-and-data/inflation-expectations) |
| Realized CPI | CPIAUCSL | All Urban, seasonally adjusted |

---

## Section 8: Corporate Bond / Credit Spread Systematic Strategies {#section-8}

### 8.1 What Credit Spreads Represent

A credit spread is the additional yield a corporate bond pays over a risk-free government bond of the same maturity. This spread compensates investors for:

1. **Expected default losses:** Probability of default × Loss given default
2. **Unexpected default risk premium:** Extra compensation for the uncertainty of default timing
3. **Liquidity premium:** Corporate bonds are less liquid than Treasuries; investors demand compensation
4. **Convexity difference:** Callable bonds have negative convexity — the spread includes compensation for the embedded option

$$
\text{Credit Spread} = y_{corporate} - y_{Treasury} = \text{EL} + \text{Default Risk Premium} + \text{Liquidity Premium} + \text{Optionality}
$$

The Gilchrist-Zakrajsek "Excess Bond Premium" (EBP) decomposes this: EBP = total spread minus the actuarially fair expected default loss, leaving the pure risk premium component. Their paper "Credit Spreads and Business Cycle Fluctuations" (American Economic Review, 102(4), 2012, pp. 1692-1720) showed that EBP is a powerful leading indicator of economic activity — when EBP rises (not just due to increased default risk but due to tightening financial conditions), economic activity falls 6-12 months later.

### 8.2 Investment Grade vs. High Yield

| Characteristic | Investment Grade (IG) | High Yield (HY) |
|---|---|---|
| Rating | BBB- and above | BB+ and below |
| Typical spread range | 60-250bps | 250-1000bps |
| Duration | 5-8 years | 3-5 years (more callable bonds) |
| Correlation with equities | 0.3-0.5 | 0.6-0.8 |
| Systematic exposure | CDX.NA.IG, iTraxx Main | CDX.NA.HY, iTraxx Xover |
| Primary risk driver | Duration + spread | Equity-like default risk |
| Best systematic signal | Carry (spread vs. history) | Momentum + carry |

### 8.3 CDX Indices: Systematic Credit Exposure

CDX indices provide standardized, liquid, systematic exposure to credit spreads:

- **CDX.NA.IG:** 125 investment-grade North American names. 5Y and 10Y tenors. Trading volume ~$10B/day.
- **CDX.NA.HY:** 100 high-yield North American names. 5Y tenor. Trading volume ~$3B/day.
- **iTraxx Europe Main:** 125 European IG names. Analogous to CDX.NA.IG.
- **iTraxx Europe Xover:** 75 European sub-IG names. Analogous to CDX.NA.HY.

Selling CDX protection (selling CDS = receiving the spread = being "long credit") generates credit carry. The annualized carry from selling CDX.NA.IG 5Y when spreads are at 100bps:

$$
\text{Credit Carry}_{annualized} = 100bps \times \text{DTS} / 10000
$$

where DTS (Duration Times Spread) ≈ 5Y × 100bps = 500bps-years.

### 8.4 Systematic Credit Strategies

**Credit Carry:**

The systematic credit carry strategy is conceptually simple: sell CDX protection (go long credit risk) when spreads are wide versus historical norms; buy protection (go short credit risk) when spreads are tight.

```python
def credit_carry_signal(
    cdx_ig_spread: pd.Series,    # CDX IG 5Y OTR spread (bps)
    cdx_hy_spread: pd.Series,    # CDX HY 5Y OTR spread (bps)
    ig_long_run_avg: float = 90,  # Long-run IG spread average
    hy_long_run_avg: float = 400, # Long-run HY spread average
    z_window: int = 252,
) -> dict:
    """
    Credit carry signal: long credit when spreads wide vs. history.
    Returns DTS-normalized position signal.
    """
    # Z-score of current spread vs. history
    ig_z = (cdx_ig_spread - cdx_ig_spread.rolling(z_window).mean()) / \
            cdx_ig_spread.rolling(z_window).std()
    hy_z = (cdx_hy_spread - cdx_hy_spread.rolling(z_window).mean()) / \
            cdx_hy_spread.rolling(z_window).std()
    
    # Signal: positive z = spreads wide = favorable to be long credit
    # DTS = Duration × Spread for position sizing
    ig_dts = 5.0 * cdx_ig_spread  # 5Y duration × spread
    hy_dts = 4.5 * cdx_hy_spread  # 4.5Y duration × HY spread
    
    return {
        'ig_signal': ig_z,          # +ve = long IG
        'hy_signal': hy_z,          # +ve = long HY
        'ig_dts': ig_dts,           # DTS for position sizing
        'hy_dts': hy_dts,
    }
```

**Momentum in Credit Spreads:**

Credit spreads trend. When CDX IG spreads begin widening (e.g., due to deteriorating fundamentals or risk-off), the widening tends to persist for 3-6 months. The TSMOM framework applies: sign of 6-month spread change → position in CDS. Short credit (buy protection, pay CDX spread) when the 6M spread change is positive (widening); long credit when the 6M change is negative (tightening).

**Cross-Asset Credit Signal:**

IG credit spreads and equity market returns are cross-predictive:
- Widening IG spreads → negative equity market returns (6-week lag)
- Strong equity market → IG spreads tightening (confirming credit rally signal)

This creates a composite cross-asset signal: when equity momentum and credit spread momentum are aligned, signal strength doubles.

### 8.5 The Gilchrist-Zakrajsek Excess Bond Premium as a Signal

The EBP (Gilchrist-Zakrajsek, 2012) is available from the Fed's website and FRED. The EBP is the component of credit spreads that is orthogonal to expected default losses — it measures the pure financial sector risk premium.

**Systematic use:**

- EBP at extreme highs (>150bps, e.g., GFC 2008, COVID March 2020): Exceptional long credit entry. Risk premium is elevated beyond fundamentals.
- EBP rapidly rising: Sell risky assets, hedge with credit protection. EBP leads equity drawdowns by 2-6 months.
- EBP at historical lows (<0bps, e.g., 2021): Credit is priced for perfection; reduce long credit exposure.

```python
# FRED: GZ_EBP (Gilchrist-Zakrajsek Excess Bond Premium)
# Available at: https://www.federalreserve.gov/econres/notes/feds-notes/
# Free download as CSV

def ebp_signal(ebp_series: pd.Series, threshold_hi=1.5, threshold_lo=-0.5) -> pd.Series:
    """
    EBP-based credit signal.
    EBP > threshold_hi → strong long credit (spreads excessive)
    EBP < threshold_lo → reduce/short credit (spreads too tight)
    """
    signal = pd.Series(0.0, index=ebp_series.index)
    signal[ebp_series > threshold_hi] = 1.0   # long credit
    signal[ebp_series < threshold_lo] = -1.0   # short credit
    # Interpolate for intermediate values
    mid_range = ebp_series.clip(threshold_lo, threshold_hi)
    signal = (mid_range - threshold_lo) / (threshold_hi - threshold_lo) * 2 - 1
    return signal
```

### 8.6 Data Sources for Credit

| Series | FRED Code | Description |
|---|---|---|
| US HY OAS | BAMLH0A0HYM2 | ICE BofA US High Yield Option-Adjusted Spread |
| US IG OAS | BAMLC0A0CM | ICE BofA US Corporate Option-Adjusted Spread |
| Euro HY OAS | BAMLHE00EHY | ICE BofA Euro High Yield OAS |
| Euro IG OAS | BAMLHE4WEHE | ICE BofA Euro Corporate OAS |
| GZ Excess Bond Premium | WLEMUINDXD | Fed's Gilchrist-Zakrajsek EBP proxy |

---

## Section 9: Fixed Income Risk Management {#section-9}

### 9.1 Duration Risk: Measuring and Limiting Aggregate DV01

The primary risk metric in any fixed income systematic portfolio is aggregate DV01 — the total exposure to a parallel shift in all yield curves.

**DV01 budget for a $100M fund:**

| Risk Appetite | DV01 per $100M AUM | Equivalent to |
|---|---|---|
| Conservative | $25,000 | ~$3.1M 10Y Treasury position |
| Moderate | $50,000 | ~$6.2M 10Y Treasury position |
| Aggressive | $100,000 | ~$12.3M 10Y Treasury position |
| Macro hedge fund | $200,000+ | ~$25M 10Y Treasury equivalent |

A DV01 of $50,000 per $100M means the portfolio loses $50,000 for each 1bp parallel shift in global rates — or $500,000 for a 10bp move, or $2.5M for a 50bp shock. This needs to be calibrated against the fund's risk budget (typically 10-15% annualized volatility target).

### 9.2 Curve Risk: Separating Duration from Slope and Curvature

Total curve risk is decomposed into:

1. **Duration (Level):** Sensitivity to a parallel shift across all maturities
2. **Slope:** Sensitivity to a steepening/flattening (e.g., 2s10s change, holding level constant)
3. **Curvature:** Sensitivity to butterfly movement in the belly

**PCA decomposition:**

In practice, 90%+ of G10 yield curve variance is explained by three principal components:
- PC1 (Level): ~80% of variance, all maturities moving together
- PC2 (Slope): ~15% of variance, short end moving vs. long end
- PC3 (Curvature): ~5% of variance, belly vs. wings

```python
from sklearn.decomposition import PCA
import numpy as np

def yield_curve_pca(
    yield_matrix: np.ndarray,  # shape (T, M): T time periods, M maturities
    n_components: int = 3,
) -> dict:
    """
    Decompose yield curve changes into level, slope, curvature factors.
    
    Input: matrix of yield curve snapshots
    Output: factor loadings and time series of factor returns
    """
    changes = np.diff(yield_matrix, axis=0)
    
    pca = PCA(n_components=n_components)
    factors = pca.fit_transform(changes)
    
    return {
        'factor_returns': factors,        # (T-1, 3): level, slope, curvature daily changes
        'loadings': pca.components_,      # (3, M): how each factor loads on each maturity
        'explained_variance': pca.explained_variance_ratio_,
        'level_factor': factors[:, 0],    # PC1: level (parallel shift)
        'slope_factor': factors[:, 1],    # PC2: slope (twist)
        'curvature_factor': factors[:, 2], # PC3: curvature (butterfly)
    }
```

For risk management: compute the portfolio's sensitivity to each PC. A portfolio that is long 2Y and short 10Y (steepener) has near-zero PC1 (level) risk but positive PC2 (slope) risk. The risk budget should be set separately for each PC.

### 9.3 Credit Risk: DTS — the Credit Equivalent of DV01

**Duration Times Spread (DTS)** is the credit analog of DV01:

$$
DTS = \text{Modified Duration} \times \text{Credit Spread (bps)}
$$

When spreads widen by 1%, the price change is approximately $-\text{DTS}/10000$. DTS allows comparing the risk of different credits:

- A 5Y BBB corporate at 150bps OAS: DTS = 5 × 150 = 750
- A 3Y BB corporate at 400bps OAS: DTS = 3 × 400 = 1200 — riskier

DTS normalization allows consistent position sizing across credit segments.

### 9.4 Country Risk: Cross-G10 Bond Correlations

G10 government bond markets are highly correlated in risk-off episodes. During the COVID shock (March 2020), US Treasuries and German Bunds both rallied simultaneously — the global flight-to-quality overcame all carry and momentum signals. Understanding this joint behavior is critical:

```python
# Typical cross-G10 bond 10Y return correlations (daily, normal market conditions)
correlation_matrix_normal = {
    'US-DE': 0.55, 'US-GB': 0.60, 'US-JP': 0.25,
    'US-AU': 0.65, 'US-CA': 0.72, 'DE-GB': 0.75,
    'DE-JP': 0.30, 'AU-CA': 0.70,
}

# During risk-off episodes (correlation rises toward 1.0 for safe havens)
correlation_matrix_risk_off = {
    'US-DE': 0.80, 'US-GB': 0.80, 'US-JP': 0.50,
    'US-AU': 0.55, 'US-CA': 0.82,
}
```

In a cross-country carry strategy, when all bond markets rally together (risk-off), the "long high-carry / short low-carry" position doesn't help — all positions rise together. This is why currency hedging, not just duration hedging, is critical: the FX leg of the carry trade can generate losses even when bonds rally.

### 9.5 Stress Scenarios: Major Fixed Income Drawdowns

| Scenario | Date | 10Y UST Yield Change | 10Y Bund Yield Change | TSMOM P&L | Carry P&L | Value P&L |
|---|---|---|---|---|---|---|
| Taper Tantrum | May-Sep 2013 | +136bps | +90bps | Negative (long bonds) | Negative | Positive (rates too low) |
| 2018 Q4 | Sep-Dec 2018 | -40bps (rally) | -20bps | Positive (short bonds reversed) | Near zero | Neutral |
| COVID shock | Feb-Mar 2020 | -145bps (crash rally) | -40bps | Positive (long bonds) | Positive | Negative |
| 2022 Rate Shock | Jan-Dec 2022 | +236bps | +255bps | Positive (short bonds) | Deeply negative | Positive |
| Oct 2023 Tantrum | Aug-Oct 2023 | +120bps | +90bps | Positive (short) | Negative | Positive |

Key lessons:
- In 2013: Carry failed. Momentum (long bonds) also failed. Only value (Taylor rule said rates too low) won.
- In 2022: Momentum eventually adapted (turned short) and value signaled correctly. Carry was the major loser.
- Diversification across signals (carry + momentum + value) significantly dampens drawdowns.

### 9.6 Convexity Risk in Tail Scenarios

Long government bond positions always carry positive convexity — in large yield moves, you lose less than duration predicts on the downside, and gain more than duration predicts on the upside. This positive asymmetry is valuable in stress.

**The position risk management implication:** For a systematic strategy that uses futures (where you're delta-equivalent to a bond position), you have approximately the same convexity as the underlying bond. The mark-to-market in a 50bp shock will be better than the duration estimate suggests.

However, short bond positions have negative convexity from your perspective: you lose more than duration estimates in a sharp rally. Position limits for short-duration systematic strategies should account for this.

---

## Section 10: Building a Multi-Signal Fixed Income Strategy for G10 {#section-10}

### 10.1 Strategy Overview

The multi-signal approach combines carry, momentum, and value signals with independent information content. Evidence from major systematic managers (AQR, Man Group, Winton, Campbell) confirms that these three factors are robust across G10 bond markets and through time.

**Target universe:**
- US (10Y: TY futures, 2Y: TU futures, 30Y: US futures)
- Germany (Bund 10Y: FGBL, Schatz 2Y: FGBS)
- UK (Long Gilt: G)
- Japan (JGB: JB)
- Australia (10Y: XT)
- Canada (10Y: CGB)
- France (OAT 10Y: FOAT)
- Sweden (2Y/10Y SGBs)

**Risk budget:** 10% annualized portfolio volatility target.

### 10.2 Signal 1: Cross-Country Carry

```python
import pandas as pd
import numpy as np

def fi_carry_signal(
    yields_10y: pd.DataFrame,     # (T, N) — daily 10Y yields for N countries
    repo_rates: pd.DataFrame,     # (T, N) — local overnight rates
    slope_10y_9y: pd.DataFrame = None,  # (T, N) — roll-down component
    panel: bool = True,
) -> pd.DataFrame:
    """
    Cross-country fixed income carry signal.
    
    Signal: yield minus repo (plus roll-down if available), cross-sectionally z-scored.
    Expected Sharpe gross: ~0.6-0.8
    Holding period: 1 month
    """
    carry = yields_10y.sub(repo_rates)
    if slope_10y_9y is not None:
        carry = carry.add(slope_10y_9y * 8.0)  # roll-down augmentation
    
    if panel:
        # Cross-sectional z-score (long high-carry, short low-carry)
        cs_mean = carry.mean(axis=1)
        cs_std = carry.std(axis=1)
        return carry.sub(cs_mean, axis=0).div(cs_std, axis=0).clip(-2.5, 2.5)
    else:
        # Time-series z-score (relative to own history)
        return ((carry - carry.rolling(252).mean())
                / carry.rolling(252).std()).clip(-2.5, 2.5)
```

**Signal characteristics:**
- Expected Sharpe: 0.6-0.8 gross (Koijen et al. 2018)
- Typical drawdown duration: 6-18 months
- Correlation with FX carry: 0.35-0.50
- Most damaging scenario: synchronized global rate hike cycle (2022)

### 10.3 Signal 2: Yield Curve Slope as Value/Carry Quality Signal

```python
def curve_slope_signal(
    yields_10y: pd.DataFrame,     # (T, N)
    yields_2y: pd.DataFrame,      # (T, N)
    z_window: int = 504,          # 2-year rolling z-score
) -> pd.DataFrame:
    """
    Curve slope signal for each country.
    
    A steep curve (high 2s10s z-score) signals:
    1. High carry quality (roll-down is rich)
    2. Economic early-cycle (good for duration)
    Signal: z-score of 10Y-2Y slope vs. 2-year history.
    Expected Sharpe gross: ~0.4-0.6
    Holding period: 1-3 months
    """
    slope_2s10s = yields_10y.sub(yields_2y)
    ts_mean = slope_2s10s.rolling(z_window).mean()
    ts_std = slope_2s10s.rolling(z_window).std()
    z_slope = ((slope_2s10s - ts_mean) / ts_std).clip(-2.5, 2.5)
    
    # Cross-sectional: which country has the steepest curve relative to its own history?
    cs_mean = z_slope.mean(axis=1)
    cs_std = z_slope.std(axis=1)
    return z_slope.sub(cs_mean, axis=0).div(cs_std, axis=0).clip(-2.5, 2.5)
```

### 10.4 Signal 3: TSMOM in Bond Futures

```python
def tsmom_bonds(
    bond_futures_prices: pd.DataFrame,  # (T, N)
    lookback_days: int = 252,
    vol_window: int = 63,
) -> pd.DataFrame:
    """
    12-month time-series momentum in bond futures.
    Vol-scaled to equalize risk per instrument.
    Expected Sharpe gross: ~0.5-0.8
    Holding period: 1 month, rolled monthly
    """
    returns_12m = bond_futures_prices.pct_change(lookback_days)
    daily_returns = bond_futures_prices.pct_change()
    realized_vol = daily_returns.rolling(vol_window).std() * np.sqrt(252)
    
    # TSMOM signal: sign of return, scaled by inverse vol
    raw_signal = np.sign(returns_12m)
    vol_scalar = (0.40 / realized_vol).clip(0.5, 4.0)  # target 40% per-instrument vol
    
    return (raw_signal * vol_scalar).clip(-3, 3)
```

### 10.5 Signal 4: Taylor Rule Deviation (Value)

```python
def taylor_value_signal(
    yields_10y: pd.DataFrame,      # (T, N)
    cpi_yoy: pd.DataFrame,         # (T, N) — country-level CPI YoY
    output_gap: pd.DataFrame,      # (T, N) — IMF/OECD output gap estimates
    neutral_rates: pd.Series = None,  # (N,) — country-specific neutral rates
    z_window: int = 504,
) -> pd.DataFrame:
    """
    Taylor rule deviation as cross-country value signal.
    
    Taylor_10Y = neutral_rate + CPI + 0.5*(CPI-2%) + 0.5*output_gap + term_premium
    Signal = z-score of (Taylor_10Y - actual_10Y) across countries
    Positive signal = yields below Taylor implied = bond cheap = short signal
    Expected Sharpe gross: ~0.4-0.5
    Holding period: 3-6 months
    """
    if neutral_rates is None:
        neutral_rates = pd.Series(2.5, index=yields_10y.columns)
    
    term_premium = 0.50  # 50bps average term premium estimate
    
    taylor_implied = (
        neutral_rates
        + cpi_yoy
        + 0.5 * (cpi_yoy - 2.0)
        + 0.5 * output_gap
        + term_premium
    )
    
    # Deviation: positive = yields below Taylor = bond rich = short signal
    deviation = yields_10y - taylor_implied
    
    # Cross-sectional z-score
    cs_mean = deviation.mean(axis=1)
    cs_std = deviation.std(axis=1)
    # Negative z = yields too low relative to peers = rich bond = short
    raw_z = deviation.sub(cs_mean, axis=0).div(cs_std, axis=0)
    
    # Flip sign: positive signal = long bond (yields too high = cheap bond)
    return (-raw_z).clip(-2.5, 2.5)
```

### 10.6 Combined Model: Multi-Signal Portfolio

```python
def combined_fi_strategy(
    carry_signal: pd.DataFrame,
    slope_signal: pd.DataFrame,
    momentum_signal: pd.DataFrame,
    taylor_signal: pd.DataFrame,
    weights: dict = None,
    portfolio_vol_target: float = 0.10,
) -> dict:
    """
    Combine four FI signals into a single portfolio.
    
    Default weights calibrated to maximize diversification while
    respecting empirical Sharpe ratios of each component.
    """
    if weights is None:
        # Weighted by expected Sharpe ratio
        weights = {
            'carry': 0.35,      # SR ~0.7, highest Sharpe
            'slope': 0.20,      # SR ~0.5, carry quality filter
            'momentum': 0.30,   # SR ~0.65, independent from carry
            'taylor': 0.15,     # SR ~0.45, slowest signal (3-6M)
        }
    
    # Composite signal
    composite = (
        weights['carry'] * carry_signal
        + weights['slope'] * slope_signal
        + weights['momentum'] * momentum_signal
        + weights['taylor'] * taylor_signal
    )
    
    # Normalize to unit signal
    composite_norm = composite.div(composite.abs().sum(axis=1), axis=0)
    
    # Portfolio-level vol-scaling
    daily_pnl_estimate = composite_norm.rolling(21).std() * np.sqrt(252)
    avg_vol = daily_pnl_estimate.mean(axis=1)
    vol_scalar = (portfolio_vol_target / avg_vol).clip(0.3, 3.0)
    
    # Final weights
    final_weights = composite_norm.multiply(vol_scalar, axis=0)
    
    return {
        'weights': final_weights,
        'composite_signal': composite_norm,
        'vol_scalar': vol_scalar,
        'signal_components': {
            'carry': carry_signal,
            'slope': slope_signal,
            'momentum': momentum_signal,
            'taylor': taylor_signal,
        }
    }
```

### 10.7 Expected Performance and Correlations

Based on the academic literature and empirical evidence from systematic managers:

| Signal | Gross Sharpe | Annual Turnover | Max Drawdown (hist) | Key Risk |
|---|---|---|---|---|
| Cross-country carry | 0.65 | 12x/year | 25-30% | Rate shock (2022) |
| Curve slope (value) | 0.50 | 6x/year | 20-25% | Prolonged flat curve |
| TSMOM bond futures | 0.65 | 12x/year | 20-30% | Policy pivot (2019) |
| Taylor rule value | 0.45 | 4x/year | 15-20% | Taylor breaks down |
| **Combined (equal risk)** | **0.85-1.0** | **10x/year** | **15-20%** | Correlated failure |

Pairwise correlation of signal returns:
- Carry vs. Momentum: ~0.15-0.25 (near-zero — best diversifier pair)
- Carry vs. Slope: ~0.35-0.45 (partially correlated — slope is a carry quality filter)
- Carry vs. Taylor: ~0.10-0.20 (largely independent — different time horizons)
- Momentum vs. Taylor: ~0.20-0.30 (some alignment in sustained trending markets)

The combined Sharpe benefit is approximately $\sqrt{4} = 2$ in the theoretical uncorrelated case; in practice, with the moderate correlations above, the combined Sharpe of ~0.85-1.0 versus individual Sharpes of 0.45-0.65 represents a meaningful diversification benefit.

### 10.8 Data Sources for Implementation

```python
# Data acquisition reference for practitioners

DATA_SOURCES = {
    # 10Y Government Bond Yields (FRED codes)
    'gov_yields_10y': {
        'US':  'DGS10',      # US 10Y Constant Maturity Treasury
        'DE':  'IRLTLT01DEM156N',  # Germany 10Y
        'GB':  'IRLTLT01GBM156N',  # UK 10Y
        'JP':  'IRLTLT01JPM156N',  # Japan 10Y
        'AU':  'IRLTLT01AUM156N',  # Australia 10Y
        'CA':  'IRLTLT01CAM156N',  # Canada 10Y
        'FR':  'IRLTLT01FRM156N',  # France 10Y
        'SE':  'IRLTLT01SEM156N',  # Sweden 10Y
        'NO':  'IRLTLT01NOM156N',  # Norway 10Y
        'NZ':  'IRLTLT01NZM156N',  # New Zealand 10Y
    },
    # 2Y Government Bond Yields (FRED codes)
    'gov_yields_2y': {
        'US':  'DGS2',        # US 2Y
        'DE':  'IRLTLT01DEM156N',  # approximate with ECB rates
        # For most non-US, use ECB/national bank databases
    },
    # Overnight / Repo Rates (FRED codes)
    'repo_rates': {
        'US':  'SOFR',        # Secured Overnight Financing Rate (post-2018)
               # or 'DFF' (Fed Funds Effective Rate) as proxy
        'EUR': 'ECBESTRVOLWGTTRR',  # ECB ESTR (EUR overnight rate)
        'GB':  'IUDSOIA',    # SONIA (use BoE data)
        'JP':  'IRSTCI01JPM156N',   # Japan call rate proxy
        'AU':  'IRSTCI01AUM156N',   # Australia Cash Rate
        'CA':  'IRSTCI01CAM156N',   # Canada overnight rate
    },
    # TIPS / Breakeven Inflation
    'tips_and_breakeven': {
        '10y_tips_yield':      'DFII10',      # Real 10Y yield
        '10y_breakeven':       'T10YIE',      # 10Y inflation breakeven
        '5y_breakeven':        'T5YIE',       # 5Y inflation breakeven
        '5y5y_forward_bei':    'T5YIFR',      # 5Y5Y forward BEI
        '10y_tips_5y':         'DFII5',       # Real 5Y yield
    },
    # Credit Spreads
    'credit_spreads': {
        'us_hy_oas':           'BAMLH0A0HYM2',   # ICE BofA US HY OAS
        'us_ig_oas':           'BAMLC0A0CM',      # ICE BofA US IG OAS
        'euro_hy_oas':         'BAMLHE00EHY',     # Euro HY OAS
        'euro_ig_oas':         'BAMLHE4WEHE',     # Euro IG OAS
        'us_hy_yield':         'BAMLH0A0HYM2EY',  # HY effective yield
    },
    # Term Premium
    'term_premium': {
        'acm_10y':             'ACMTP10',     # ACM 10Y term premium (NY Fed)
        # ACM full dataset: https://www.newyorkfed.org/research/data_indicators/term-premia-tabs
    },
    # Bond Futures (Yahoo Finance / Interactive Brokers / Bloomberg)
    'bond_futures': {
        'us_10y':   '^TNX via FRED, or TY1 Bloomberg',
        'us_30y':   'US1 Bloomberg / CBOT US futures',
        'bund_10y': 'FGBL Bloomberg / Eurex',
        'gilt':     'G Bloomberg / ICE',
        'jgb':      'JB Bloomberg / TSE',
        'au_10y':   'XT Bloomberg / ASX',
        'ca_10y':   'CGB Bloomberg / MX',
    },
}
```

### 10.9 Transaction Costs and Capacity

Fixed income systematic strategies are among the most scalable strategies available:

| Instrument | Bid-Ask Spread | Round-Trip Cost ($100M DV01) | Daily ADV |
|---|---|---|---|
| UST 10Y futures (TY) | 0.5 tick = $15.6 | ~$31 per contract | >1M contracts |
| Bund futures (FGBL) | 0.5bp | ~€25 per contract | 400K contracts |
| Cash 10Y UST | 0.1-0.3bp | ~$100/M notional | $900B |
| CDX.NA.IG 5Y | 0.25bp running | ~$25K per $100M notional | $10B/day |
| CDX.NA.HY 5Y | 1bp running | ~$100K per $100M | $3B/day |

For a $100M AUM fund with 10% vol target and 12x annual turnover:
- Annual transaction cost ≈ 10-30bps of AUM = $100K-$300K/year
- This represents 0.1-0.3% of AUM in implementation drag
- Net Sharpe ≈ Gross Sharpe - 0.1 to 0.2 (very modest impact)

Capacity for government bond systematic strategies: typically $2-10B before market impact becomes significant for a monthly-rebalancing strategy. This compares very favorably to equity long-short (capacity ~$500M-$2B for mid-cap).

### 10.10 Implementation Timeline and Setup

For a practitioner building this from scratch:

**Month 1-2: Data infrastructure**
- Pull all FRED yield series via `fredapi` Python library
- Set up bond futures historical data (Yahoo Finance for longer history, Interactive Brokers for live)
- Establish repo rate proxies (SOFR for USD, ESTR for EUR, SONIA for GBP)

**Month 3: Signal testing**
- Backtest each of four signals independently (2005-present)
- Verify Sharpe ratios match literature benchmarks (within 20%)
- Check signal correlations against expected values

**Month 4: Portfolio construction**
- Combine signals with correlation-adjusted weights
- Add vol-targeting layer (rolling 63-day realized vol scaling)
- Add the slope conditioning filter (suppress carry when curve flat/inverted)
- Stress-test against 2013, 2018, 2022 scenarios

**Month 5: Paper trading and risk audit**
- Run paper portfolio for 30-60 days
- Verify DV01 calculations match broker risk systems
- Establish position limit framework (max DV01 per country, max aggregate DV01)

```python
# Minimal working example: signal-to-trade pipeline

import pandas_datareader.data as web
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def build_fi_signals(start='2005-01-01', end=None):
    """
    Pull data from FRED and build the four core FI signals.
    """
    if end is None:
        end = datetime.today().strftime('%Y-%m-%d')
    
    # Pull yields
    yields = {
        'US': web.DataReader('DGS10', 'fred', start, end)['DGS10'],
        'DE': web.DataReader('IRLTLT01DEM156N', 'fred', start, end).iloc[:, 0],
        'GB': web.DataReader('IRLTLT01GBM156N', 'fred', start, end).iloc[:, 0],
        'JP': web.DataReader('IRLTLT01JPM156N', 'fred', start, end).iloc[:, 0],
        'AU': web.DataReader('IRLTLT01AUM156N', 'fred', start, end).iloc[:, 0],
        'CA': web.DataReader('IRLTLT01CAM156N', 'fred', start, end).iloc[:, 0],
    }
    yields_10y = pd.DataFrame(yields).dropna()
    
    # Pull overnight rates
    repo = {
        'US': web.DataReader('DFF', 'fred', start, end)['DFF'] / 100,
        # Others: approximate from ECB/BoJ/RBA policy rates
    }
    
    # Pull ACM term premium
    term_prem = web.DataReader('ACMTP10', 'fred', start, end)['ACMTP10']
    
    # Pull breakevens
    breakeven_10y = web.DataReader('T10YIE', 'fred', start, end)['T10YIE']
    tips_10y = web.DataReader('DFII10', 'fred', start, end)['DFII10']
    
    return {
        'yields_10y': yields_10y,
        'term_premium': term_prem,
        'breakeven_10y': breakeven_10y,
        'tips_yield': tips_10y,
    }
```

---

## Appendix A: Key Academic References

| Paper | Authors | Year | Journal | Key Finding |
|---|---|---|---|---|
| Time-Varying Expected Returns in International Bond Markets | Ilmanen | 1995 | Journal of Finance 50(2) | Yield slope predicts bond excess returns in 6 countries; 4-12% monthly $R^2$ |
| Time Series Momentum | Moskowitz, Ooi, Pedersen | 2012 | Journal of Financial Economics 104(2) | TSMOM in 58 instruments including bond futures; combined SR 1.28 gross |
| Momentum Has Its Moments | Barroso, Santa-Clara | 2015 | Journal of Financial Economics 116(1) | Vol-scaling momentum nearly eliminates crashes; doubles SR |
| Carry | Koijen, Moskowitz, Pedersen, Vrugt | 2018 | Journal of Financial Economics 127(2) | Unified carry framework; FI carry SR ~0.6-0.8 gross; global carry SR ~0.9 |
| Credit Spreads and Business Cycle Fluctuations | Gilchrist, Zakrajšek | 2012 | American Economic Review 102(4) | Excess bond premium predicts GDP 6-12M ahead; pure risk premium in credit |
| Treasury Term Premia: 1961-Present | Adrian, Crump, Moench | 2013/2014 | NY Fed Liberty Street Economics | Five-factor no-arbitrage term structure model; daily term premium estimates |
| Predicting Bond Returns: 70 Years of International Evidence | Ilmanen et al. | 2021 | Financial Analysts Journal | Updates Ilmanen 1995; confirms slope predicts bonds over 70+ years |

---

## Appendix B: Key Risk Metrics Reference Sheet

| Metric | Formula | Typical Value (10Y UST) | When It Matters |
|---|---|---|---|
| Modified Duration | $D / (1 + y/m)$ | 8.0 years | Always — core duration risk |
| DV01 | $D^* \times P \times 0.0001$ | ~$800 per $1M | Position sizing and aggregation |
| Convexity | See Section 2.3 | ~70 | Large yield moves (>50bps) |
| Carry (net) | $y - r_{repo}$ | -90bps in 2024 (inverted curve) | Strategy allocation |
| Roll-down | $(y_{10Y} - y_{9Y}) \times D^*$ | +80bps (mildly steep long end) | Carry augmentation |
| DTS (credit) | $D^* \times \text{spread}$ | 750 for BBB 5Y at 150bps | Credit position sizing |
| Term Premium | ACM model residual | -50bps to +200bps (cycles) | Duration value signal |
| Breakeven Inflation | $y_{nominal} - y_{TIPS}$ | 220-240bps (2024-2025) | TIPS allocation |

---

## Appendix C: The Yield Curve and Macro Cycle Map

```
Macro Phase         Yield Curve Shape    Duration Signal    Carry Signal    Curve Signal
─────────────────────────────────────────────────────────────────────────────────────────
Early expansion     Steep & steepening   Long duration      High carry      Long belly
Mid-cycle growth    Steep & stable       Neutral duration   Moderate carry  Neutral
Late cycle          Flattening rapidly   Short duration     Declining carry Short belly
Pre-recession       Inverted             Slightly long      Near-zero/neg   Avoid carry
Recession           Sharply steepening   Long duration      Rebuilding      Long belly
Post-recession QE   Flat at zero bound   Neutral            Suppressed      Distorted
QT normalization    Steepening           Neutral-long       Recovering      Long belly
```

This macro cycle map is the strategic overlay that systematizes the intuition experienced discretionary macro traders already use. The difference in systematic execution: the signals are computed objectively at defined frequencies, with explicit position sizing, rather than relying on real-time judgment.

The most important transition to internalize: systematic FI is not about being "smarter" than the market on rates — it is about **being more disciplined** in applying known return premia (carry, momentum, value) across a diversified G10 universe, with robust risk management that prevents any single scenario (2022 rate shock, 2020 COVID rally) from being catastrophic.

---

*Document end. Version 1.0 — July 2026.*
*For NotebookLM ingestion: This document covers the complete systematic fixed income framework from foundational concepts through live implementation. All Python code is illustrative of actual trading system architecture.*
