# Quant Fund Practices: AQR, WorldQuant, Millennium & Beyond

Documented research and methodology from major systematic hedge funds — focused on medium-frequency strategies (daily to monthly rebalancing). Not HFT or market making.

---

## AQR Capital Management

### Core Published Papers

**"Value and Momentum Everywhere" — Asness, Moskowitz, Pedersen (JF 2013)**

The most important AQR paper for a multi-asset systematic researcher. Central finding: both value and momentum work across eight asset classes simultaneously — US equities, UK equities, European equities, Japanese equities, equity index futures, government bonds, currencies, and commodities.

**For currencies specifically:**
- **Value**: 5-year real exchange rate deviation from PPP (how far spot rate deviates from long-run real fair value). Constructed as 5-year spot rate change relative to CPI differential between countries.
- **Momentum**: 12-1 month trailing return (skip most recent month to avoid reversal contamination).
- Carry alone SR **0.84**; Momentum alone SR **0.95**; Value alone SR **0.41**; Combined SR **0.96** with dramatically improved tail risk.
- Carry-momentum correlation ≈ +0.05; carry-value ≈ −0.30; momentum-value ≈ −0.15. The negative value-momentum correlation is structural and persistent — combining them diversifies without sacrificing expected return.

**Key insight for this repo.** Your 2Y rate-differential signal is the carry component. Adding 12-1M cross-sectional momentum across pairs and PPP-value would complete the AQR triplet. Value and momentum are adversarial by construction — value bets on mean reversion, momentum on continuation — creating powerful diversification.

**AQR public dataset.** The "Value and Momentum Everywhere" monthly factor return data is publicly available at aqr.com/Insights/Datasets — FX, equities, bonds, commodities from 1972 onwards.

---

**"Time Series Momentum" — Moskowitz, Ooi, Pedersen (JFE 2012)**

Foundation of AQR's managed futures franchise. Signal: long an asset if its past 12-month excess return is positive; short if negative. Tested across 58 futures contracts including G10 FX currencies.

**Key findings:**
- Positive TSMOM profits for every single one of 58 instruments across 25+ years.
- Vol-targeting (scale each position to equal risk contribution) is essential — without it, high-vol assets dominate returns and the Sharpe improvement is masked.
- **Crisis alpha**: TSMOM generates positive returns during the worst equity drawdowns (2000–2002, 2008–2009) because trends persist through crises.

**FX application.** For each G10 pair individually: if trailing 12-month return is positive, hold long; if negative, hold short. Size proportional to `1/RealVol_pair`. This is distinct from your cross-sectional rate-diff signal — it asks "has EURUSD been trending up for 12 months?" rather than "has the EUR-USD rate diff moved today?"

---

**"Carry" — Koijen, Moskowitz, Pedersen, Vrugt (JFE 2018)**

Most comprehensive treatment of carry as a unified cross-asset factor.

**Unified definition.** Carry = an asset's expected return if prices stay unchanged (forward-looking, model-free). For FX this is the interest rate differential; for bonds it's the term spread; for equities it's the dividend yield; for commodities it's the roll return.

**Key results:**
- Carry predicts returns cross-sectionally and in time series for every asset class.
- Diversified cross-asset carry portfolio SR ≈ **1.2** — well above any single-asset carry.
- Carry strategies in FX exhibit negative skewness — the crash risk premium is real and priced.
- Carry-momentum correlation in FX: approximately +0.3 to +0.5 — less diversifying than value-momentum, but all three together produce a superior portfolio.

---

**"Betting Against Beta" — Frazzini, Pedersen (JFE 2014)**

Low-beta assets earn higher risk-adjusted returns than high-beta assets — direct violation of CAPM.

**Mechanism.** Leverage-constrained investors (pension funds, mutual funds) tilt toward high-beta to achieve desired expected returns, overpricing high-beta and underpricing low-beta. The BAB factor exploits this by going long low-beta (levered to unit beta) and short high-beta.

**Application to Indian equities.** Indian retail investors exhibit this pattern strongly — they tilt toward high-beta, high-volatility stocks. Low-volatility/low-beta stocks are structurally underpriced → the low-vol anomaly in India.

---

**"Quality Minus Junk" — Asness, Frazzini, Pedersen (RAS 2019)**

Quality defined as composite of profitability (gross profits/assets, ROE, low accruals), growth (5Y profitability growth), and safety (low beta, low leverage, low earnings volatility).

**Key finding.** High-quality stocks earn significant positive risk-adjusted returns globally in 24+ countries. High-quality stocks are priced higher on P/B but not enough to offset their fundamentals — they remain cheap relative to quality. The QARP (quality at a reasonable price) anomaly underlies the Buffett-style insight.

**India application.** Quality is particularly relevant in India where corporate governance is weaker and the quality spread between companies is wider than in developed markets.

---

**"Factor Momentum Everywhere" — Gupta, Kelly (JPM 2019)**

Individual equity factors exhibit time-series momentum: factors that performed well over the past year continue to outperform in the near future. A factor momentum portfolio (overweight recently-working factors) earns SR **0.84** independently, not subsumed by stock-level momentum.

**Practical implication.** Among your signal set, allocating more to recently-working signals has empirical support. This is different from valuation-based factor timing (which AQR discourages).

---

### AQR's Cross-Cutting Methodology

**Signal combination.** AQR uses **equal-weight** combination of cross-sectionally z-scored signals. Not IC-optimised, not covariance-matrix-weighted. Rationale: estimation error in IC/covariance matrices over short windows typically destroys more value than the theoretical gain. The z-score architecture in your `signals/_base.py` (`cross_section_zscore()`) is correct.

**Vol-targeting.** Standard across all AQR strategies. Scale each position to target equal risk contribution. For FX: `w_i = (σ_target / σ_i) × signal_i`. This is what your `VolRegimeFilter` in Track 1 approximates.

**Factor timing.** AQR's official position: "extremely challenging" and adds "minimal value" based on valuation-spread timing over a century of data. The "venial sin" episode (2019): AQR modestly tilted toward value (25% → 40% allocation) based on historically wide value spreads; immediately punished with −6.4% relative drawdown in Q1 2020. The carve-out: **factor momentum** (trailing factor returns as timing signal) does have empirical support.

**Alpha vs. risk premium.** AQR treats carry, momentum, value as systematic risk premia — not mispricings. The premium is compensation for bearing real economic risks (liquidity, crash, recession). Implication: hold these factors through multi-year drawdowns with conviction that the risk hasn't disappeared.

---

## WorldQuant

### "101 Formulaic Alphas" — Kakushadze, Lauprete, Tulchinsky (Wilmott, 2016)

The most transparent public disclosure of a working quant fund's actual alpha production. 101 explicit mathematical formulas live in production at WorldQuant at time of publication.

**Data inputs.** Most alphas use only five fields: Open, High, Low, Close, Volume (OHLCV). A minority use fundamental data. This means the alphas are directly applicable to any liquid instrument with OHLCV data — including G10 FX futures.

**The operator algebra.** All 101 alphas are built from a small set of operations:
- `rank()` — cross-sectional percentile rank
- `delta(x, d)` — N-day change
- `correlation(x, y, d)` — rolling d-day correlation
- `ts_rank(x, d)` — time-series rank (percentile in past N days)
- `decay_linear(x, d)` — linearly decayed weighted average
- `indneutralize()` — industry/sector neutralisation (FX: not applicable)

**Key statistics:**
- Average holding period: **0.6 to 6.4 days** — these are short-horizon signals.
- Average pairwise correlation between alphas: **15.9%** — weakly correlated, meaning 101 signals combined in a portfolio is far superior to any single signal.

**The diversification math.** Combined Sharpe of N signals with individual Sharpe s and average pairwise correlation ρ ≈ `s × √N / √(1 + (N−1)×ρ)`. With N=101, s=0.3, ρ=0.16: combined SR ≈ **2.0**. This is why WorldQuant runs millions of alphas.

**FX applicability.** OHLCV-based alphas that don't use `indneutralize()` or fundamental data are directly portable to G10 FX. Specifically, momentum/mean-reversion constructions like:
- `rank(ts_rank(close, 20) - ts_rank(open, 20))` — intraday price persistence
- `correlation(close, volume, 10)` — price-volume relationship (replace volume with rate-diff for FX)
- `decay_linear(delta(close, 5), 5)` — decayed 5-day momentum

---

### "Finding Alphas" — Tulchinsky (WorldQuant, 2020)

**The core philosophy.** An alpha is not a signal — it's a complete expression of expected excess return across the universe. WorldQuant targets IC = 5%+ as a viability threshold; combines millions of alphas with average pairwise correlation ~15% to produce a strong aggregate.

**Triple axis plan.** New alphas must be novel along at least one of three axes: (1) idea origin (momentum, mean reversion, fundamental), (2) data universe (equity, futures, FX), (3) holding frequency (intraday to monthly). This maps directly to how you should think about extending this repo's strategy set.

**IC = 0.05 is meaningful at scale.** With 3,000+ stocks, an IC of 5% is statistically highly significant and economically useful when aggregated across many positions. For G10 FX with only 9 pairs, you need much higher IC (>0.10) for individual signals to be meaningful.

---

## Millennium Management

### Pod Structure (from investor letters and regulatory filings)

Millennium is the archetypal multi-PM "pod shop." Key features:

**Structure.** ~330+ independent pods, each allocated ~$100–200M, operating as near-autonomous mini-funds. Pods measured on Sharpe ratio. Capital dynamically reallocated to higher-performing pods.

**Risk limits.** A pod losing ~5–7% of capital faces mandatory capital reduction or termination. This bounds firm-wide drawdown by construction — no single strategy can blow up the firm.

**Factor exposure management.** Central risk management monitors factor exposures across all pods. A pod running "stock-specific alpha" that inadvertently loads on the same factor as 30 other pods creates concentrated firm-wide risk. Common factor exposures are stripped out; only idiosyncratic pod returns are priced. This is the key structural risk control not easily replicated at smaller scale.

**Four strategy pillars.** (1) Relative value fundamental equity, (2) equity arbitrage (merger arb, convertible arb), (3) fixed income and commodities, (4) quantitative strategies (including the WorldQuant partnership managing ~$7B).

---

## Transaction Costs and the Replication Crisis

### Frazzini, Israel, Moskowitz — "Trading Costs of Asset Pricing Anomalies" (AQR, 2015)

**Central finding.** Using nearly $1 trillion of live institutional trading across 19 developed equity markets (1998–2011): real transaction costs are **an order of magnitude smaller** than prior academic estimates (which used quoted bid-ask spreads).

**Why prior estimates overstated costs.** Academic models assume buy at ask, sell at bid. A patient institutional investor using limit orders and algorithmic execution faces effective spreads far below quoted spreads. For momentum specifically: effective spread = 12.7 bps vs academic estimates of 50–100+ bps.

**The buy/hold spread technique.** The single most impactful cost reduction: require signal to exceed threshold T to enter, but only exit when it falls below a lower threshold t < T. Dramatically reduces turnover with minimal sacrifice of expected alpha, because signals are autocorrelated.

**Implication for G10 FX.** G10 spot FX is among the most liquid instruments globally. Your 2.5-pip RT cost per unit assumption is appropriate and conservative for EURUSD/USDCAD. The main cost risk is over-trading (daily signal flips on noise). The 1-day hold period in Track 2 is supported given the high net Sharpe.

---

### Novy-Marx, Velikov — "A Taxonomy of Anomalies and Their Trading Costs" (RFS, 2016)

**Key finding.** Anomalies with **< 50% monthly turnover** generally survive costs and generate significant net-of-cost returns. Anomalies with > 50% monthly turnover generally fail.

**Survivor set.** Size, value, profitability, and momentum (at monthly rebalance with buy/hold spread) survive. For Indian equities: low-vol (annual rebalance) is well below the 50% turnover threshold; monthly momentum rebalancing is borderline — semi-annual rebalancing reduces costs while retaining most of the signal.

---

### Hou, Xue, Zhang — "Replicating Anomalies" (RFS, 2020)

**Scale.** Tests 452 anomalies published in top finance journals.

**The devastating finding.** **65% of 452 anomalies fail** to clear t > 1.96 using proper methodology (NYSE breakpoints, value-weighted returns, no microcap stocks). 82% fail at t > 2.78 (multiple-testing correction).

**What was causing false discoveries:**
1. Microcap dominance (equal-weighting lets tiny illiquid stocks drive returns)
2. Equal vs value weighting (equal-weighted returns much higher; value-weighting is what matters for implementation)
3. Multiple testing (452 anomalies at 5% significance = ~22 spurious discoveries by chance)

**The genuine survivors.** ~18% clear t > 1.96. Most are explained by the q-factor model (profitability + investment factors). The four robustly documented effects: **profitability/quality, investment/asset growth, momentum, value (book-to-market)**.

**Scepticism filter for new factors.** Is your signal: (a) discovered pre-1990 with long history? (b) Positive with value-weighted returns? (c) Positive excluding micro-cap? (d) Low turnover? If yes to all four, it likely survives. Your 2Y rate-differential signal is a daily FX factor — different universe (FX not equities) so these filters don't directly apply, but the principle does: test with transaction costs, over multiple regimes, not just in-sample.

---

### Stambaugh, Yu, Yuan — "The Short of It" (JFE, 2012)

**Mechanism.** When investor sentiment is high, overpricing is more prevalent than underpricing (short-selling constraints prevent arbitrageurs from fully correcting overpricing). Anomalies — which mostly profit from the short leg — should be stronger after high-sentiment periods.

**Key finding.** For 11 anomalies, each is stronger following high sentiment. The short leg is more profitable after high sentiment. The long leg is not significantly affected.

**India implication.** With short-selling constrained in India, overpriced stocks remain overpriced longer. Long-only factor strategies (momentum, quality, low-vol) capture more of the premium in India than in markets with frictionless shorting — because the short-leg correction is impeded, the anomaly persists longer, giving the long leg more time to profit.

---

## Cross-Cutting Methodology Summary

### Signal Combination: Best Practice Ranking

| Method | Out-of-Sample Performance | When to Use |
|---|---|---|
| Equal-weight z-scores | Strong baseline; rarely beaten OOS | Always — start here |
| IC-IR weighted | Modest improvement | After 3+ years of live signal IC data |
| IC-mean weighted | Inconsistent improvement | Not recommended over equal-weight |
| Max-IR optimised | Best in-sample; usually worst OOS | Only with heavy constraints; avoid |

**The z-score architecture is correct.** Converting each signal to cross-sectional z-score before combining ensures each signal contributes equally to composite variance. Your `cross_section_zscore()` in `signals/_base.py` implements this correctly.

---

### Signal Half-Lives

| Signal Type | Half-Life | Notes |
|---|---|---|
| Short-term mean reversion (1–5 days) | Hours to 1–2 days | Traded out by HFT; inaccessible to daily strategies |
| Rate-diff change (your Track 2) | 1 day | Very short; high turnover; must have strong IC to survive costs |
| Cross-sectional momentum (12-1M) | 3–12 months | Peak at 1M holding; decays over 6–18M; reverses at 3–5Y |
| Carry (rate differential level) | Months | Central bank cycles drive changes; fits monthly rebalance |
| Value (PPP deviation) | Years | Very slow signal; years to decades for mean reversion |
| Quality (profitability) | Years | High-quality companies remain high-quality for years |

---

### Factor Timing — The Industry Verdict

**Based on valuation spreads (e.g., "value is cheap relative to history — overweight it"):**
- AQR explicitly: "extremely challenging"; "minimal value over a century of data"
- Empirical evidence: After the 2019 "venial sin" (modestly timing toward value), punished immediately by −6.4% relative drawdown in Q1 2020
- Consensus: Do not time factors based on how "cheap" or "expensive" they appear

**Based on factor momentum (trailing factor returns as timing signal):**
- Gupta/Kelly (2019): Factor momentum SR = 0.84; not subsumed by stock momentum
- Consensus: Overweighting recently-working factors has empirical support
- Implementation: Among your signal set, apply TSMOM logic — allocate more to signals with positive trailing 12-month performance

---

### Alpha vs. Risk Premium

**Risk premium view (AQR's position):** Carry compensates for crash risk and funding liquidity risk. Momentum compensates for behavioural underreaction. Value compensates for distress/business cycle risk. Premia are sustainable because the risk is real — knowing about them doesn't make the risk go away.

**Post-publication decay is real but modest.** Most major factors retain 40–70% of their pre-publication premium in the decade after publication. The evidence is consistent with partial mispricing that partially survives because of continuing limits to arbitrage.

**Practical implication.** Treat your core signals (rate differential, carry, momentum) as risk premia with structural economic justification. This provides the conviction to hold them through multi-year drawdowns.

---

## Recommended Extensions for This Repo

**Near-term (all public data, low effort):**
1. **Vol-normalised carry**: Divide rate-diff signal by pair realised vol. Documented +0.1–0.3 Sharpe improvement.
2. **TSMOM overlay**: For each pair, scale position by sign of trailing 12-month return. Uses existing Yahoo Finance price data.
3. **Crash filter overlay**: VIX (FRED) + COT crowding (already fetched) as position scalars. Reduces left-tail skewness.

**Medium-term (public data, medium effort):**
4. **AQR triplet completion (FX)**: Add cross-sectional 12-1M momentum + PPP-value to existing rate-diff carry signal. Completes the academically validated FX factor triplet.
5. **Term structure signal**: Add FRED 10Y–2Y slope differential as second signal component.
6. **Dollar factor (DOL)**: Trade aggregate long/short USD based on US 2Y vs G10-average 2Y.

**Indian equities (new track, separate data pipeline):**
7. **Low-volatility long-only**: Annual rebalance, Nifty 500 top-100, equal-weight. Highest evidence quality with lowest cost drag.
8. **12-1 momentum (vol-adjusted)**: Monthly rebalance on Nifty 500 using yfinance.
9. **Quality-Momentum composite**: ROE/ROCE from Screener.in + price momentum from yfinance.

---

## Key Papers Quick Reference

| Paper | Authors | Year | Core Finding |
|---|---|---|---|
| Value and Momentum Everywhere | Asness, Moskowitz, Pedersen | JF 2013 | Carry + momentum + value triplet; combined SR > any single |
| Time Series Momentum | Moskowitz, Ooi, Pedersen | JFE 2012 | TSMOM positive for every futures contract; vol-targeting essential |
| Carry | Koijen, Moskowitz, Pedersen, Vrugt | JFE 2018 | Cross-asset carry unified; SR ~1.2 diversified |
| Betting Against Beta | Frazzini, Pedersen | JFE 2014 | Low-beta outperforms; leverage constraints cause overpricing of high-beta |
| Quality Minus Junk | Asness, Frazzini, Pedersen | RAS 2019 | Quality premium globally; high-quality stocks cheap relative to fundamentals |
| Factor Momentum Everywhere | Gupta, Kelly (AQR) | JPM 2019 | Factor TSMOM SR 0.84; distinct from stock momentum |
| 101 Formulaic Alphas | Kakushadze et al. (WorldQuant) | Wilmott 2016 | 101 OHLCV alphas; avg 15.9% pairwise correlation; combining weak signals works |
| Trading Costs of Anomalies | Frazzini, Israel, Moskowitz | AQR 2015 | Real costs 10× lower than TAQ estimates; major factors survive at institutional scale |
| Taxonomy of Anomalies | Novy-Marx, Velikov | RFS 2016 | < 50% monthly turnover anomalies survive; buy/hold spread crucial |
| Replicating Anomalies | Hou, Xue, Zhang | RFS 2020 | 65% of 452 anomalies fail to replicate; only 4 genuine effects survive |
| The Short of It | Stambaugh, Yu, Yuan | JFE 2012 | Short leg drives anomalies; stronger after high sentiment; India implication |

*Last updated: June 2026*
