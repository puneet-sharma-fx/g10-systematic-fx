# Alternative Data for Systematic Trading & Global Equity Factor Investing
## A Comprehensive Reference for Quantitative Research

**Prepared for:** Experienced discretionary macro/FX traders moving toward systematic quantitative trading  
**Date:** July 2026  
**Status:** Research reference — not investment advice

---

## Table of Contents

**Part 1: Alternative Data for Systematic Trading**
1. [The Alternative Data Landscape](#section-1-the-alternative-data-landscape)
2. [Satellite and Geolocation Data](#section-2-satellite-and-geolocation-data)
3. [Transactional and Consumer Data](#section-3-transactional-and-consumer-data)
4. [NLP and Sentiment Analysis](#section-4-nlp-and-sentiment-analysis)
5. [Alternative Data Due Diligence Framework](#section-5-alternative-data-due-diligence-framework)

**Part 2: Global Equity Factor Investing**
6. [Why Global Equity Factors Matter](#section-6-why-global-equity-factors-matter)
7. [Regional Factor Differences — What Works Where and Why](#section-7-regional-factor-differences)
8. [Multi-Country Equity Factor Construction](#section-8-multi-country-equity-factor-construction)
9. [The Factor Timing Problem](#section-9-the-factor-timing-problem)
10. [A Practical Global Equity Factor Strategy](#section-10-a-practical-global-equity-factor-strategy)

---

# Part 1: Alternative Data for Systematic Trading

---

## Section 1: The Alternative Data Landscape

### What Is Alternative Data?

Alternative data refers to any dataset that is not sourced from traditional financial information channels — exchanges, regulatory filings, central bank publications, and terminal providers like Bloomberg or Reuters. The term captures everything from satellite imagery of Walmart parking lots to the sentiment expressed in Federal Reserve minutes to anonymised credit card transactions aggregated by zip code.

For a discretionary macro trader transitioning to systematic methods, the relevance of alternative data is not merely academic. These datasets represent genuine, exploitable information asymmetries — at least for a few years after discovery, and often longer when barriers to acquisition remain high. The fundamental insight is that markets price securities using information available to market participants. If you have better, faster, or more granular information than the consensus, you have an edge. Alternative data is one of the most direct ways to acquire that informational advantage systematically.

### The Scale of the Opportunity

The alternative data market has grown explosively over the past decade. JPMorgan estimated the market at $1.7 billion in 2020, growing at approximately 30% annually, suggesting the market has crossed $7–8 billion by 2026. This growth reflects both supply-side expansion (new data vendors entering the market) and demand-side pressure (hedge funds and asset managers competing to be first movers on new datasets).

Importantly, the growth in vendor supply has not necessarily compressed alpha — the data landscape is expanding faster than the number of quant funds capable of productively using it. A systematic FX trader who adds commodity-related satellite data, for example, is not necessarily competing with a long/short equity fund that already uses the same data for stock selection, because the translation to a tradeable FX signal involves domain-specific judgment.

### The Ten Categories of Alternative Data

#### 1. Geolocation / Satellite / Aerial Imagery
Commercially operated satellites (Planet Labs, Maxar, Airbus Defence & Space) now image every point on Earth's surface at resolutions of 0.3–3 metres on a daily to weekly basis. Combined with machine learning algorithms, this raw imagery generates signals about physical economic activity: vehicles in parking lots, shadow lengths on oil tanks, crop health, shipping container counts.

#### 2. Transactional Data
Anonymised and aggregated purchase data from credit cards, debit cards, point-of-sale terminals, and digital wallets. Visa, Mastercard, and payment processors generate this data as a byproduct of core operations. Vendors like YipitData and Bloomberg Second Measure aggregate and sell cleaned versions.

#### 3. Web Scraping
Automated extraction of publicly available data from websites: prices on Amazon, job postings on Indeed, restaurant reviews on Yelp, hotel rates on Booking.com. The scraping itself is legally contested in several jurisdictions (hiQ Labs v. LinkedIn, US Ninth Circuit), but the data products built from scraping are widely used.

#### 4. Social Media and News Sentiment
Natural language processing (NLP) applied to Twitter/X posts, Reddit threads, news articles, earnings call transcripts, and regulatory filings to extract sentiment, topic exposure, and information novelty.

#### 5. IoT Sensor Data
Internet-of-Things devices generate enormous volumes of operational data: electricity meters, smart building sensors, industrial IoT on factory floors, agricultural sensors measuring soil moisture and temperature.

#### 6. Labour Market Data
Job postings scraped from LinkedIn, Indeed, Glassdoor, and company websites provide a high-frequency real-time picture of corporate hiring intentions, skills in demand, and sector-level workforce changes.

#### 7. Search Trend Data
Google Trends provides free, weekly, and geographically disaggregated search interest data for any query. Baidu Index performs the same function for Chinese internet users. These data reveal consumer attention before it manifests in spending.

#### 8. App Usage and Mobile Data
Mobile intelligence vendors (Sensor Tower, data.ai) measure app download counts, daily active users, and session lengths across iOS and Android platforms globally.

#### 9. Supply Chain and Shipping Data
AIS (Automatic Identification System) data from ships, combined with satellite tracking of rail and road cargo, provides real-time global supply chain visibility at a resolution no official statistics can match.

#### 10. Environmental / ESG Data
Satellite measurements of SO₂ emissions (a proxy for industrial output), CO₂ concentrations near industrial facilities, waste heat from factories, and shipping channel traffic. These data underpin both ESG scoring and real-time economic activity estimation.

### The Data Supply Chain: Raw to Signal-Ready

The journey from raw data to a tradeable signal involves multiple processing stages, each of which adds value and complexity:

```
Raw Data → Cleaning → Normalisation → Feature Engineering → Signal → Trade
```

| Stage | What Happens | Time Cost | Key Risk |
|---|---|---|---|
| Raw acquisition | Download/stream from vendor API | Minutes–Hours | Data corruption, gaps |
| Cleaning | Remove duplicates, handle NaNs, timezone alignment | Days | Survivorship bias baked in |
| Normalisation | Cross-sectional z-scoring, winsorisation | Hours | Lookahead bias in scalers |
| Feature engineering | Momentum of signals, changes, interactions | Hours | Overfitting |
| Signal generation | Model output → position sizing | Minutes | Stale signals |
| Trade execution | Slippage, market impact, costs | Milliseconds | Alpha decay from costs |

The most common error at each stage is **lookahead bias**: using information that would not have been available at the time of the trade. For alternative data, this is especially pernicious because vendors often backfill historical datasets with data that was only collected prospectively.

### Key Institutional Vendors

| Vendor | Category | Pricing Tier | Free Tier? |
|---|---|---|---|
| Quandl / Nasdaq Data Link | Multi-category aggregator | $5K–$500K/yr | Limited |
| Eagle Alpha | Data discovery/sourcing | Custom | No |
| YipitData | Transactional, web | $50K–$200K/yr | No |
| Preqin | Private markets alt data | $20K–$100K/yr | No |
| 1010data | Retail transactions | $100K+/yr | No |
| Orbital Insight | Satellite/geolocation | $50K–$300K/yr | No |
| Spire Maritime | AIS / satellite | $20K–$100K/yr | No |
| Placer.ai | Foot traffic | $10K–$50K/yr | Trial |
| SafeGraph | Geolocation | $5K–$50K/yr | Academic |
| Bloomberg Second Measure | Credit card spend | Bloomberg terminal add-on | No |

---

## Section 2: Satellite and Geolocation Data

### Satellite Imagery

#### What Satellites Measure and How

Modern commercial satellites orbit at altitudes between 400 and 600 km. At this range, Planet Labs' Dove constellation can image the entire land surface of Earth every day at 3-metre resolution. Maxar's WorldView-3 achieves 0.31-metre resolution on tasked acquisitions. The raw imagery is then processed through computer vision and machine learning pipelines to extract economically relevant signals.

The key inference mechanisms are:

- **Parking lot occupancy:** Object detection algorithms count vehicles in parking lots; more cars = more retail footfall
- **Crop health (NDVI):** The Normalized Difference Vegetation Index exploits the different reflectance of healthy vs. stressed vegetation in the near-infrared band
- **Oil tank inventory:** Floating-roof tanks have a shadow pattern that changes with fill level; algorithms measure shadow geometry to estimate volume
- **Shipping container counts:** Port imagery combined with container detection algorithms provides port throughput estimates
- **Construction progress:** Time series of building site imagery allows tracking of real estate construction completions

#### Oil Storage via Satellite: The Floating Roof Method

Oil storage tanks using floating roofs — where the roof rides directly on the oil surface — cast distinctive shadows when partially full. When the tank is full, the roof sits flush at the rim and casts a minimal shadow. When partially empty, the roof sits lower inside the rim, creating a shadow on the inner wall proportional to the empty space above.

The shadow area $S$ relates to the fill fraction $f$ as follows:

$$S \approx \pi r^2 (1 - f) \cdot \frac{h}{r} \cdot \sin(\theta_{sun})$$

where $r$ is tank radius, $h$ is tank height, and $\theta_{sun}$ is the solar elevation angle. In practice, ML regression models trained on known fill levels learn these relationships directly from imagery.

**The China crude storage problem** illustrates why satellite data can outperform official statistics. China does not systematically report crude oil inventories in the IEA format. The only reliable way to estimate Chinese commercial crude storage has been through satellite-based tank counting. Multiple studies (Desai et al., 2016; Orbital Insight white papers, 2017–2020) showed that satellite-derived oil storage estimates for China predicted oil price moves 3–5 days ahead of any public data release.

Key satellite oil vendors: **Orbital Insight**, **Ursa Space**, **RS Metrics**

#### Retail Foot Traffic: The GPS Location Method

Mobile phones constantly record GPS coordinates and transmit them to app developers (often through SDK-level data collection in innocuous apps — weather apps, flashlight apps, gaming apps). This data is sold by aggregators to analytics firms under various consent and anonymisation frameworks.

**Placer.ai** and **SafeGraph** are the leading vendors. Their products show visit counts to specific retail locations, restaurant chains, airports, stadiums, and anything with a fixed physical address. The visit data can be cross-sectional (compare Target vs. Walmart) or time-series (track one retailer over time).

The predictive value for equity investing is substantial: Chen, Maslar, Sautner, Spalt (2020, *Journal of Finance*) showed that foot traffic data from Safegraph predicts same-store sales beats/misses with an in-sample IC of approximately 0.15–0.20, which translates to economically significant alpha after controlling for consensus analyst estimates. The mechanism is simple: analysts form revenue estimates using phone surveys and model-based projections; foot traffic data measures actual physical visits with far greater granularity and real-time accuracy.

#### Crop Health: NDVI and Commodity Trading

The Normalized Difference Vegetation Index is defined as:

$$\text{NDVI} = \frac{\rho_{NIR} - \rho_{Red}}{\rho_{NIR} + \rho_{Red}}$$

where $\rho_{NIR}$ is the reflectance in the near-infrared band and $\rho_{Red}$ in the visible red band. Healthy vegetation has high $\rho_{NIR}$ (chlorophyll reflects strongly in NIR) and low $\rho_{Red}$ (chlorophyll absorbs red for photosynthesis), giving NDVI values near +1.0. Bare soil, dying crops, or flooded fields have NDVI near 0 or negative.

The USDA now uses NDVI in its WASDE (World Agricultural Supply and Demand Estimates) reports. Firms like **Gro Intelligence** sell NDVI-based crop yield forecasts weeks ahead of WASDE releases. For a commodity trader, this is one of the clearest-cut alternative data applications: if NDVI in the US Corn Belt in July is tracking below the 5-year average, the forthcoming WASDE is likely to revise the corn yield estimate downward, and corn futures should rally on the news.

The signal horizon is 2–3 months ahead of WASDE for major crops, which is a substantial information lead.

### AIS Shipping Data: The Global Supply Chain in Real Time

Every vessel over 300 gross tonnes is required by international maritime law (SOLAS Chapter V) to broadcast an AIS signal containing vessel identity, position (GPS), speed, heading, and destination. These signals are received by a network of ground stations and, since 2014, by satellite AIS receivers in low Earth orbit operated by companies including **Spire Maritime**, **ExactEarth**, and **Orbcomm**.

The result is near-real-time tracking of every significant commercial vessel on Earth — approximately 70,000 active vessels at any time.

**Free access:** MarineTraffic and VesselFinder provide web interfaces and limited API access. Enough for qualitative monitoring, insufficient for systematic signal generation.

**Institutional access:** Spire Maritime provides raw AIS data feeds with sub-minute latency and full global coverage, priced for institutional use.

#### What AIS Data Tells You

| Signal | What It Measures | Leading Indicator For |
|---|---|---|
| VLCC tanker port calls | Crude oil loading and discharge | Crude oil supply/demand |
| Tanker speed (steaming vs. drifting) | Demand for prompt delivery | Oil price spot/forward spread |
| Container ship utilisation | Global goods trade volume | PMI, GDP estimates |
| Port congestion (ships at anchor) | Supply chain disruption | Goods inflation, input costs |
| Grain carrier flows (Black Sea) | Wheat/corn trade volumes | Agricultural commodity prices |
| LNG carrier flows | Gas trade | European/Asian gas prices |

The congestion signal is particularly valuable: when tankers anchor outside key ports (Rotterdam, Houston, Fujairah) in unusual numbers, it signals a local supply glut or infrastructure bottleneck that has not yet been absorbed into prices.

---

## Section 3: Transactional and Consumer Data

### Credit Card and Point-of-Sale Data

Credit card and debit card transaction data is generated as a byproduct of the payment network infrastructure. Payment processors (Visa, Mastercard, American Express, PayPal) see every transaction that flows through their networks. They aggregate, anonymise, and sell this data — or allow vendors to do so — in formats that reflect consumer spending patterns at the industry, company, and sometimes store level.

**What the data contains:** Merchant category code (MCC), transaction amount, geographic location, timestamp. Individual-level data is anonymised to comply with privacy regulations; the products sold are aggregated statistics.

**Key vendors and their coverage:**

| Vendor | Data Source | Coverage | Lag | Strength |
|---|---|---|---|---|
| YipitData | Multiple card networks | US-primary; some EU | 1 week | Depth in US retail |
| Bloomberg Second Measure | Card transaction data | US-focused | 2 weeks | Company-level precision |
| Earnest Research | Multi-source panel | US; some international | 1–2 weeks | Frequency of update |
| M-Science | Aggregated card panels | US | 1 week | Breadth of sector coverage |
| Affinity Solutions | Bank partnerships | US | ~1 week | Real-time capability |

**Evidence on credit card data alpha:**

Chen, Cohen, Li, and Lou (2020, *Journal of Financial Economics*) constructed a signal based on credit card spending data from an anonymous US credit card network covering approximately 10 million cardholders. Their core finding: a portfolio long stocks with high abnormal spending and short stocks with low abnormal spending earned approximately **50 basis points per month** after accounting for transaction costs, market beta, and standard factor exposures. The IC was approximately 0.08–0.12, which is high for an individual signal used in a live trading context.

The mechanism is simply information advantage: card data shows actual customer spending at the firm level, 4–8 weeks before the firm reports quarterly earnings. Analysts' consensus earnings estimates are constructed from surveys and models; the card data reflects ground truth.

**Constructing a revenue surprise signal from card data:**

```python
import pandas as pd
import numpy as np
from scipy import stats

def estimate_revenue_surprise(
    card_spending: pd.DataFrame,  # columns = company tickers, index = weekly dates
    analyst_consensus: pd.DataFrame,  # quarterly revenue consensus estimates
    fiscal_quarter_end: dict  # ticker -> fiscal quarter end date
) -> pd.DataFrame:
    """
    Estimate revenue surprise using credit card spending data.
    
    Method: Sum card spending in the quarter and compare to analyst consensus.
    Card data is a partial sample; scale by historical coverage ratio.
    """
    surprise_scores = {}
    
    for ticker in card_spending.columns:
        if ticker not in fiscal_quarter_end:
            continue
        
        q_end = fiscal_quarter_end[ticker]
        q_start = q_end - pd.DateOffset(months=3)
        
        # Quarterly card spending (sum of weekly data)
        q_card = card_spending[ticker].loc[q_start:q_end].sum()
        
        # Historical coverage ratio: card_spending / reported_revenue
        # (must be estimated from historical data to avoid lookahead bias)
        # Assume we have pre-computed this
        # coverage_ratio = historical_card / historical_revenue (use 4-8 quarter avg)
        
        # Scale to revenue estimate
        # estimated_revenue = q_card / coverage_ratio
        # surprise = (estimated_revenue - consensus) / consensus
        
        # For illustration: normalised z-score vs. analyst consensus growth
        consensus_growth = analyst_consensus[ticker] if ticker in analyst_consensus else np.nan
        card_growth = card_spending[ticker].pct_change(52).iloc[-1]  # YoY growth
        
        if not np.isnan(consensus_growth):
            surprise_scores[ticker] = card_growth - consensus_growth
    
    return pd.Series(surprise_scores, name='revenue_surprise_signal')
```

### Web Scraping Data

#### Price Scraping: Amazon and E-Commerce

Amazon updates prices dynamically — sometimes multiple times per day — using an algorithmic pricing system that responds to competitor prices, inventory levels, and demand signals. This creates a rich information signal: the trajectory of Amazon prices for a product category reveals demand pressure and competitive dynamics.

A sustained downward trend in Amazon prices for consumer electronics, for example, signals either demand weakness or inventory overhang — both bearish for the manufacturers supplying those categories.

#### Job Postings: The Real-Time Hiring Signal

Job postings scraped from Indeed, LinkedIn, Glassdoor, and company career pages represent one of the most useful alternative data signals for sectoral analysis. The underlying logic is simple: companies post jobs when they plan to expand, and stop posting jobs (or post fewer) when they plan to contract or are facing financial stress.

**Signal construction:**

- **Level:** Total active job postings for a company or sector at a point in time
- **Change:** MoM or YoY change in job postings
- **Mix:** Types of roles being hired (engineers vs. salespeople vs. lawyers vs. accountants)
- **Location:** Hiring in headquarters vs. offshore suggests different margin implications

**Macro applications for an FX trader:**

| Observation | Implication | FX Signal |
|---|---|---|
| Tech job postings collapse 30% in 3 months | Technology sector revenue likely to disappoint | Bearish USD (tech sector = large component of US equity/income) |
| Oil sector postings surge 40% YoY | Capex cycle accelerating | Bullish CAD, NOK (petro-currencies) |
| UK financial services postings drop post-Brexit | Services sector adjustment underway | Bearish GBP productivity outlook |
| German manufacturing postings fall | Industrial downturn | Bearish EUR manufacturing PMI read-through |

**Data vendors for job postings:** Burning Glass Technologies (now Lightcast), LinkUp, Revelio Labs, TalentNeuron

#### Search Trend Data: Google Trends and Baidu Index

Google Trends provides a free, publicly accessible API (via the `pytrends` Python library) that returns weekly search interest data for any query, normalised to a 0–100 scale within a specified time window and geographic area. Despite being free, this data remains underutilised in systematic strategies — partly because interpretation requires care.

**Da, Engelberg, and Gao (2011, *Journal of Finance*)** introduced the ASVI (Abnormal Search Volume Index), defined as:

$$\text{ASVI}_t = \log(\text{SVI}_t) - \log(\text{median SVI}_{t-8, t-1})$$

where SVI is the raw Google Search Volume Index for a stock ticker or company name. Their finding: ASVI predicts the **first two weeks of post-IPO returns** with a positive coefficient (high attention → initial price inflation), and predicts **mean reversion** over the subsequent 2–8 weeks (attention dissipates → price corrects).

For macro/FX applications, Google Trends can measure:
- Consumer search for "unemployment benefits" → leading indicator of jobless claims (Choi and Varian, 2012, *Economic Journal*)
- Search for "recession" → consumer sentiment leading indicator
- Search for a country name + "crisis" → early warning of capital flight or political instability

```python
from pytrends.request import TrendReq
import pandas as pd
import numpy as np

def get_asvi(keywords: list, geo: str = 'US', timeframe: str = 'today 3-m') -> pd.DataFrame:
    """
    Compute Abnormal Search Volume Index using Google Trends.
    
    Args:
        keywords: List of search terms (max 5 per request)
        geo: Country code for geographic filter
        timeframe: Google Trends timeframe string
    
    Returns:
        DataFrame with ASVI for each keyword
    """
    pytrends = TrendReq(hl='en-US', tz=360)
    pytrends.build_payload(keywords, cat=0, timeframe=timeframe, geo=geo)
    
    df = pytrends.interest_over_time()
    if df.empty:
        return pd.DataFrame()
    
    df = df.drop(columns=['isPartial'], errors='ignore')
    
    # ASVI: log(current) - log(8-week median)
    log_svi = np.log(df + 1)
    rolling_median = log_svi.rolling(window=8, min_periods=4).median()
    asvi = log_svi - rolling_median
    
    return asvi
```

**Baidu Index** performs the equivalent function for Chinese internet users, covering approximately 800 million active users. Access requires a Baidu account and is available via unofficial wrappers. For trading RMB-linked assets, Baidu search trends for topics like "房价" (housing prices), "理财" (wealth management), and company names can supplement thinly covered Chinese alternative data.

---

## Section 4: NLP and Sentiment Analysis

### What NLP Extracts from Financial Text

Financial markets are saturated with text: earnings call transcripts, quarterly and annual reports (10-K, 10-Q, 20-F), press releases, analyst reports, central bank minutes, news articles, and social media. Each of these text sources contains information about the future performance of assets — some explicit, some encoded in tone, hedging language, or the absence of phrases that used to appear.

The challenge for systematic trading is to convert this unstructured text into quantitative signals that can be integrated with price-based and fundamental signals.

**Primary targets for NLP signal extraction:**

| Text Source | Key Information | Frequency | Coverage |
|---|---|---|---|
| Earnings call transcripts | Management tone, forward guidance | Quarterly | Listed companies globally |
| 10-K / 10-Q filings | Risk factor changes, MD&A language | Quarterly / Annual | US listed companies |
| News articles | Company events, sector narratives | Daily | Global, all assets |
| Central bank minutes/statements | Policy tone, forward guidance signals | ~8x/year per CB | All major currencies |
| Job postings (text) | Skills in demand, growth areas | Continuous | Companies with career pages |
| Analyst reports | Estimate revisions, narrative changes | Event-driven | Covered securities |

### Lexicon-Based Sentiment: The Loughran-McDonald Dictionary

The Loughran-McDonald (LM) dictionary (Loughran and McDonald, 2011, *Journal of Finance*) is the gold-standard lexicon for finance-specific text analysis. Unlike general-purpose sentiment dictionaries (such as the Harvard General Inquirer), the LM dictionary was constructed by identifying words that carry sentiment specifically in SEC filings and financial contexts.

For example, the word "liability" is negative in the Harvard GI but financial-neutral in accounting contexts where it simply describes a balance sheet item. The LM dictionary corrects for such misclassifications. The dictionary contains six word lists:

| List | Size | Examples |
|---|---|---|
| Negative | ~2,355 words | loss, adverse, decline, unfavorable, fail |
| Positive | ~354 words | achieve, exceed, record, improvement |
| Uncertainty | ~297 words | approximately, uncertain, may, possible |
| Litigious | ~903 words | litigation, defendant, lawsuit, regulatory |
| Constraining | ~184 words | shall, must, obliged, covenant |
| Strong Modal | ~19 words | always, definitely, never |

**Free download:** Available at https://sraf.nd.edu/loughranmcdonald/

**Python implementation:**

```python
from nltk.tokenize import word_tokenize
import pandas as pd
import re

def load_lm_dictionary(filepath: str) -> dict:
    """
    Load the Loughran-McDonald master dictionary.
    Returns dict mapping word -> category flags.
    """
    df = pd.read_csv(filepath)
    df['Word'] = df['Word'].str.lower()
    df = df.set_index('Word')
    
    lm_dict = {
        'negative': set(df[df['Negative'] != 0].index),
        'positive': set(df[df['Positive'] != 0].index),
        'uncertain': set(df[df['Uncertainty'] != 0].index),
        'litigious': set(df[df['Litigious'] != 0].index),
    }
    return lm_dict


def lm_sentiment(text: str, lm_positive: set, lm_negative: set,
                  lm_uncertain: set = None) -> dict:
    """
    Compute Loughran-McDonald sentiment scores for a financial text.
    
    Returns:
        dict with positive_score, negative_score, net_sentiment, 
        uncertainty_score, n_words
    """
    # Clean text: remove numbers, special characters
    text_clean = re.sub(r'[^a-zA-Z\s]', ' ', text)
    words = word_tokenize(text_clean.lower())
    total = len(words)
    
    if total == 0:
        return {'positive': 0, 'negative': 0, 'net_sentiment': 0,
                'uncertainty': 0, 'n_words': 0}
    
    pos = sum(1 for w in words if w in lm_positive)
    neg = sum(1 for w in words if w in lm_negative)
    unc = sum(1 for w in words if lm_uncertain and w in lm_uncertain)
    
    return {
        'positive': pos / total,
        'negative': neg / total,
        'net_sentiment': (pos - neg) / total,
        'uncertainty': unc / total,
        'n_words': total
    }


def batch_score_transcripts(transcripts: pd.Series, lm_dict: dict) -> pd.DataFrame:
    """
    Score a series of earnings call transcripts using LM sentiment.
    
    Args:
        transcripts: pd.Series with ticker index and transcript text values
        lm_dict: dict returned by load_lm_dictionary
    
    Returns:
        DataFrame of sentiment scores per transcript
    """
    results = []
    for ticker, text in transcripts.items():
        scores = lm_sentiment(text, lm_dict['positive'], lm_dict['negative'],
                               lm_dict.get('uncertain'))
        scores['ticker'] = ticker
        results.append(scores)
    
    return pd.DataFrame(results).set_index('ticker')
```

**Evidence on LM sentiment performance:** Loughran and McDonald (2011) showed that LM-negative word count in 10-K filings explains approximately 8% of the variation in three-day abnormal returns around 10-K filing dates, with the expected negative sign. Improvements were approximately 2x the predictive power of the Harvard GI dictionary for the same financial texts.

### Transformer-Based Sentiment: FinBERT

The BERT (Bidirectional Encoder Representations from Transformers) architecture, introduced by Devlin et al. (2019), dramatically improved NLP performance across a wide range of tasks by pre-training deep neural networks on massive text corpora. FinBERT is a fine-tuned version of BERT specifically trained on financial text.

**Key resource:** `yiyanghkust/finbert-tone` on HuggingFace — free to download and use, trained on approximately 4,000 financial news sentences with positive/negative/neutral labels.

**Performance benchmark:** Araci (2019) showed FinBERT achieves approximately 87% accuracy on financial news sentiment classification, compared to ~82% for standard BERT and ~75% for lexicon-based methods (LM dictionary). The improvement comes from the domain-specific fine-tuning which captures financial jargon and context.

```python
from transformers import pipeline
import pandas as pd
import torch

class FinBERTScorer:
    """
    Financial text sentiment scoring using FinBERT.
    
    Handles long texts by chunking into 512-token windows
    and averaging scores across chunks.
    """
    
    def __init__(self, model_name: str = 'yiyanghkust/finbert-tone',
                 device: int = -1):
        self.pipe = pipeline(
            'text-classification',
            model=model_name,
            return_all_scores=True,
            device=device  # -1 = CPU, 0 = first GPU
        )
        self.max_tokens = 512
    
    def score_text(self, text: str) -> dict:
        """Score a single text, handling length by chunking."""
        # Simple word-based chunking (not ideal but practical)
        words = text.split()
        chunk_size = 400  # words; conservative token estimate
        chunks = [' '.join(words[i:i + chunk_size]) 
                  for i in range(0, len(words), chunk_size)]
        
        chunk_scores = []
        for chunk in chunks:
            scores = self.pipe(chunk[:1024])[0]  # hard truncate characters
            result = {item['label']: item['score'] for item in scores}
            chunk_scores.append(result)
        
        # Average across chunks
        labels = chunk_scores[0].keys()
        avg_scores = {label: sum(c[label] for c in chunk_scores) / len(chunk_scores)
                      for label in labels}
        avg_scores['net'] = avg_scores.get('Positive', 0) - avg_scores.get('Negative', 0)
        return avg_scores
    
    def score_dataframe(self, texts: pd.Series) -> pd.DataFrame:
        """Score a Series of texts, return DataFrame of scores."""
        results = {idx: self.score_text(text) for idx, text in texts.items()}
        return pd.DataFrame(results).T


def finbert_sentiment(texts: list) -> pd.DataFrame:
    """Convenience function for scoring financial texts using FinBERT."""
    finbert = pipeline('text-classification', 
                       model='yiyanghkust/finbert-tone',
                       return_all_scores=True)
    
    results = []
    for text in texts:
        scores = finbert(text[:512])[0]  # truncate to 512 tokens
        result = {item['label']: item['score'] for item in scores}
        result['net'] = result.get('Positive', 0) - result.get('Negative', 0)
        results.append(result)
    
    return pd.DataFrame(results)
```

### Earnings Call Transcript Analysis

Earnings call transcripts are among the most information-rich text sources in finance. The calls have two distinct segments: the prepared remarks (CEO/CFO reading a scripted update) and the Q&A session (analysts asking unscripted questions). 

**The Q&A section is considerably more informative than the prepared remarks** — management cannot pre-script responses to analyst questions, so hedging language, pauses, deflections, and tone changes in Q&A are stronger signals than anything in the polished prepared text.

**Key signals in earnings calls:**

| Feature | Positive Signal | Negative Signal |
|---|---|---|
| Guidance language | "We expect to exceed..." | "Uncertain environment..." |
| Forward-looking word count | Increasing vs. prior quarter | Decreasing |
| Analyst question intensity | Few, soft questions | Many aggressive follow-ups |
| CEO/CFO interruption ratio | CFO rarely interrupts | CFO frequently corrects CEO |
| Topic mentions: competitors | None | Multiple defensive mentions |
| Uncertainty word density | Below-average | Above-average (LM uncertain) |

**Data access for earnings call transcripts:**
- **Seeking Alpha** (paid, ~$240/year): comprehensive US and international transcripts
- **The Motley Fool**: coverage of major US stocks, free but ad-supported
- **Company IR websites**: free PDFs/HTML; requires web scraping at scale
- **Refinitiv (LSEG)**: institutional, comprehensive global coverage
- **FactSet CallStreet**: institutional, high quality, includes audio

### News Sentiment at Scale

For systematic, institutional-scale news sentiment processing, **RavenPack** is the dominant vendor. RavenPack processes hundreds of thousands of news articles daily from thousands of sources, applies entity recognition to link news to specific companies and instruments, and scores events on dimensions including relevance, novelty, and sentiment. Their data covers 170+ countries and is the standard in large systematic funds.

**For smaller-scale research:**

- **NewsAPI.org**: Free tier at 100 requests/day; covers ~150,000 sources. Sufficient for research and signal validation but too slow/limited for live trading
- **GDELT Project**: Free, comprehensive global news event database updated every 15 minutes. Covers news in 100+ languages with entity extraction and event coding. Huge and complex but genuinely free

**The news velocity signal:** An unusual spike in article count about a company over 24–48 hours (regardless of article sentiment) tends to predict price movement. This "attention shock" signal precedes a price change in the direction of the majority-sentiment articles but also creates a short-term mean reversion opportunity as the news effect fades.

---

## Section 5: Alternative Data Due Diligence Framework

Before committing budget to any alternative data source — and before building a strategy around it — a structured due diligence process is essential. The following checklist reflects the approach used by systematic funds when evaluating new data vendors.

### The Seven Evaluation Dimensions

#### 1. Edge Half-Life: How Long Does the Signal Last?

Every information advantage has a half-life. Once enough capital is chasing a signal, arbitrage activity compresses returns. The relevant question is not "does this signal work today?" but "how much longer will it work?".

| Data Type | Estimated Edge Half-Life | Reason |
|---|---|---|
| Satellite imagery (oil tanks) | 3–7 years | High vendor cost barriers; complex ML needed |
| Credit card spend | 3–7 years | High cost; complex aggregation; many data points needed |
| Web scraping (public prices) | 1–3 years | Low barrier to replication; many competitors |
| Earnings transcript sentiment | 1–3 years | Academic papers exist; code is reproducible |
| Central bank text sentiment | 6 months–2 years | Heavily published; many free models |
| Social media sentiment (Twitter) | 6 months–1 year | Extensively published; noise is very high |

#### 2. Coverage: Breadth of the Investment Universe

A signal that covers only 200 US consumer stocks is not useful for a global macro/FX strategy. Before evaluating a dataset's predictive power, verify:

- What fraction of your actual investable universe does the data cover?
- Is coverage biased toward large-cap, US, or specific sectors?
- How does coverage change over the historical period? (Expanding coverage can create false time-series trends)

#### 3. Historical Depth: Is There Enough for Robust Testing?

Robust quantitative backtesting requires at least 10 years of clean data, and ideally 20+ years across multiple market cycles. Many alternative data vendors only have 3–5 years of clean historical data. With 3 years of data, a strategy that looks profitable has approximately 12 non-overlapping quarterly observations — far too few to establish statistical significance.

The minimum requirement for any serious alt data backtest:

$$t_{\text{stat}} = \frac{\overline{IC}}{\sigma_{IC} / \sqrt{T}} \geq 2.0$$

where $\overline{IC}$ is mean monthly Information Coefficient, $\sigma_{IC}$ is IC volatility, and $T$ is the number of months. Solving for $T$: with a typical alt data IC of 0.05 and IC volatility of 0.12, you need at least $T = (2.0 \times 0.12 / 0.05)^2 = 23$ months. To achieve a t-stat of 3.0, you need **52 months** — over 4 years. Three years of clean data is borderline insufficient.

#### 4. Survivorship and Lookahead Bias

These are the two most dangerous biases in alternative data backtesting:

**Survivorship bias:** The historical dataset was constructed retrospectively and includes only sources, companies, or data points that survived to the present. Bankrupted retailers were removed from credit card panels; defunct satellites were excluded from imagery datasets; companies that stopped filing are missing from transcript databases.

**Lookahead bias:** The data as it appears in the historical dataset was not actually available at the time stamp it is assigned to. Common sources: vendors backfill data when they acquire it; restatements are reflected back in time; corporate actions (mergers, spin-offs) are applied retroactively.

**How to detect lookahead bias in a backtest:** The backtest should generate no returns until the data vendor's launch date. If a backtest on a dataset that only launched in 2020 shows strong returns from 2015, something is wrong.

#### 5. Privacy and Legal Compliance

The legal landscape for alternative data acquisition is evolving rapidly. Key frameworks:

- **GDPR (EU):** Strict consent requirements for personal data; many US credit card vendors have limited or no EU coverage due to compliance challenges
- **CCPA (California):** Consumer rights over personal data; affects any dataset containing California residents
- **hiQ Labs v. LinkedIn (US 9th Circuit, 2022):** Public web scraping was ruled permissible; however, LinkedIn has implemented technical barriers and CFAA interpretation varies
- **SEC guidance on material non-public information (MNPI):** If an alt data vendor provides data that constitutes MNPI (e.g., payment data from a corporate insider), trading on it creates legal risk

**Minimum check:** Obtain and read the vendor's data use agreement, privacy policy, and any legal opinions they've obtained. Ask specifically: "Has the MNPI question been evaluated by legal counsel?"

#### 6. Cost vs. Expected Alpha: The Business Case

Alternative data subscriptions range from $10,000/year (small datasets) to $500,000+/year (full institutional feeds). The expected alpha from a signal needs to cover this cost with a substantial margin.

**Back-of-envelope calculation:**

```
Annual data cost: $200,000
Strategy IR contribution from signal: 0.10 (marginal)
Required AUM to cover cost at 1% management fee: $20,000,000
Required AUM to generate enough alpha at 5 bps marginal alpha: $400,000,000
```

A signal earning 5 bps/month of marginal alpha (which is high) on a $400M portfolio generates $2.4M/year of alpha. After the $200K data cost, net alpha to the strategy is $2.2M — viable but not dominant. For a $50M portfolio, the same signal is not viable at $200K cost unless the alpha is substantially higher.

#### 7. Complementarity with Existing Signals

The final test is whether the new signal adds alpha beyond what is already captured by the existing signal composite. This requires a regression of next-period returns on both the existing composite and the new signal:

```python
def evaluate_alt_data_signal(
    alt_data_signal: pd.Series,
    existing_composite: pd.Series,
    returns: pd.Series,
    lags: int = 5
) -> object:
    """
    Evaluate whether alt data adds incremental alpha beyond existing composite.
    
    The key output is the t-statistic on alt_data_signal in the regression
    that controls for the existing composite. If t-stat > 2.0, the new data
    adds significant incremental alpha and should be considered for inclusion.
    
    Uses Newey-West HAC standard errors to correct for autocorrelation.
    """
    import statsmodels.api as sm
    
    # Align all series
    data = pd.concat([existing_composite.rename('composite'),
                       alt_data_signal.rename('alt_signal'),
                       returns.rename('ret')], axis=1).dropna()
    
    X = data[['composite', 'alt_signal']]
    y = data['ret']
    
    X_const = sm.add_constant(X)
    model = sm.OLS(y, X_const).fit(
        cov_type='HAC',
        cov_kwds={'maxlags': lags}
    )
    
    t_stat = model.tvalues['alt_signal']
    p_val = model.pvalues['alt_signal']
    ic_with_composite = data[['composite', 'alt_signal']].corrwith(y)
    
    print(f"Alt data incremental alpha:")
    print(f"  t-statistic on alt_data (HAC): {t_stat:.2f}")
    print(f"  p-value: {p_val:.4f}")
    print(f"  Standalone IC with returns: {ic_with_composite['alt_signal']:.3f}")
    print(f"  Composite IC with returns: {ic_with_composite['composite']:.3f}")
    print(f"  Correlation with existing composite: {data['alt_signal'].corr(data['composite']):.3f}")
    print(f"  Add to composite: {'YES' if abs(t_stat) > 2.0 else 'NO'}")
    
    return model
```

**The IC correlation rule:** If the alternative data signal has an IC correlation above 0.3 with the existing composite, it is unlikely to add meaningful diversification. The marginal IC contribution will be small enough that the data cost is hard to justify.

---

# Part 2: Global Equity Factor Investing

---

## Section 6: Why Global Equity Factors Matter

### The US-Centric Problem in Factor Research

The vast majority of academic factor research was conducted using US equity data — specifically CRSP (Center for Research in Security Prices), which covers US-listed equities back to 1926. Fama and French built their three-factor model (1993) on US data. Carhart (1997) added momentum using US data. Most of the 300+ "factors" in Harvey, Liu, and Zhu's (2016) survey were discovered on US data.

This creates a serious problem for global systematic investors: we do not know with confidence which US factor findings generalise internationally, or in what modified form they appear in markets with different institutional structures, investor compositions, regulatory regimes, and corporate governance norms.

For a trader looking to run global equity factor strategies, the failure to account for country-level differences in factor performance is not merely an academic concern — it is a risk management issue. A global equity momentum strategy that naively applies US-style momentum to Japanese equities will, as detailed below, significantly underperform a strategy that accounts for Japan's well-documented momentum failure.

### The Replication Crisis: How Bad Is It?

**Hou, Xue, and Zhang (2020, *Review of Financial Studies*)** systematically re-examined 452 anomalies from the published academic literature using a consistent methodology (no look-ahead, careful portfolio construction, full treatment of microcaps). They found:

- 65% of US-documented factors failed to replicate at conventional significance levels
- Many failed not because of methodological errors but because the original finding was a statistical artefact of multiple testing in the data

**McLean and Pontiff (2016, *Journal of Finance*)** examined factor performance post-publication and found that average abnormal returns declined by 26% after academic publication (suggesting partial arbitrage by funds reading the papers) and by 58% among more liquid, easily-tradeable factors. The implication: the academic literature on factors systematically overstates live trading performance, especially for factors published more than 5 years ago.

**International replication is worse.** Extending the Hou-Xue-Zhang methodology to international markets (Foye, 2018; Jacobs and Müller, 2020), only momentum, value, and profitability show consistent out-of-sample international evidence. Investment and accruals-based factors show weak or absent international evidence in most markets.

### Why Should Factors Work Globally At All?

There are two competing explanations for factor premiums, with different implications for global applicability:

**Risk-based explanation:** Factor premiums compensate for systematic risk that rational investors require compensation to bear. Under this view, factors should work wherever the same underlying risk exposure exists. A low-volatility stock premium that reflects compensation for "disaster risk" should appear in any sufficiently developed market.

**Behavioural/mispricing explanation:** Factor premiums arise from systematic investor errors — overextrapolation of growth (momentum), anchoring to past prices (value), neglect of quality metrics. Under this view, factors should be strongest in markets dominated by the relevant type of investor error, and weakest in markets where sophisticated arbitrageurs are numerous and active.

In practice, both explanations are partially true, and they generate different predictions for different factors in different markets. Japan is the cleanest illustration: momentum fails in Japan (inconsistent with a simple behavioural story), while value is very strong (consistent with the behavioural overextrapolation story in a market with chronically cheap companies).

### Global Factor Evidence Summary

The following table represents a synthesis of evidence from Fama-French (2012 *JFE*), Asness-Moskowitz-Pedersen (2013 *JF*), and subsequent replication studies. Sharpe ratios are approximate and represent long/short factor portfolio performance before transaction costs:

| Factor | US Sharpe | Europe Sharpe | Asia ex-JP | Japan | Globally Robust? |
|---|---|---|---|---|---|
| Value (B/M) | 0.45 | 0.40 | 0.35 | 0.30 | Yes (weak Japan) |
| Momentum (12-1M) | 0.65 | 0.60 | 0.45 | 0.10* | Yes (not Japan) |
| Profitability (GP/A) | 0.55 | 0.45 | 0.40 | 0.30 | Yes |
| Investment (CMA) | 0.40 | 0.25 | 0.20 | 0.15 | Partial |
| Low Volatility / BAB | 0.50 | 0.45 | 0.35 | 0.40 | Yes |
| Quality (QMJ) | 0.55 | 0.50 | 0.40 | 0.35 | Yes |
| Liquidity (Illiquidity) | 0.45 | 0.30 | 0.25 | 0.20 | US > Global |

*Japan momentum near-zero SR; momentum crashes are frequent (see Section 7)

---

## Section 7: Regional Factor Differences

### United States: The Benchmark Market

The US equity market is the deepest, most liquid, most extensively studied equity market in the world. All major institutional factor strategies were developed on US data and have operated in the US market the longest. As a result:

- Factor premiums are the most arbitraged
- Post-publication return decay is the most severe
- Institutional sophistication is the highest

**What is working in the US now (c. 2026):**

The traditionally strong momentum factor has weakened since the post-2012 proliferation of factor ETFs (MTUM, QMOM), which reduced the momentum premium through crowding. Value experienced a historic drawdown from 2018–2020 (the longest value drought on record), then a partial revival in 2022 with rising rates, then again mixed performance.

Current US factor rankings by evidence strength: **Profitability > Quality (QMJ) > Low Volatility (BAB) > Momentum > Value**

**Data access:** Ken French Data Library (https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html) provides free factor portfolios from 1926 to the present for US and international markets. This is the essential free resource for any factor research.

### Europe: Value and Governance Effects

European equity markets differ from the US in several structurally important ways:

1. **Ownership structure:** Higher prevalence of family-controlled firms, state ownership, and bank-held equity blocks. Cross-shareholdings are less extreme than Japan but more common than US.

2. **Financing structure:** European companies are more bank-debt-financed than US companies (US relies more on capital markets). This affects the interpretation of leverage signals.

3. **Regulatory environment:** MiFID II (Markets in Financial Instruments Directive II) unbundled research from execution commissions, reducing analyst coverage of smaller companies and potentially increasing mispricing in small-cap factor long legs.

**European factor evidence:**

- **Value:** Strong and historically less crowded than US value. European value stocks were genuinely cheap through the 2010s, and the value drawdown was less severe than in the US. Germany and France show the strongest country-level value evidence.

- **Momentum:** Works in UK, Germany, and France with evidence comparable to US. Continental Europe regulatory constraints on short-selling have occasionally disrupted the short leg of momentum portfolios.

- **Quality:** Strong in UK (deep institutional market) and Germany. Family-controlled firms often score poorly on quality metrics (related-party transactions, low ROE disclosure quality), which creates noise in the long leg of quality portfolios.

### Japan: The Momentum Exception and Corporate Governance Revolution

Japan is the most interesting and most anomalous developed equity market for factor investing. The headline finding — that **cross-sectional momentum fails in Japan** — is one of the most robust and practically important results in international finance.

**The momentum failure in Japan:**

Fama and French (2012, *Journal of Financial Economics*) documented that momentum returns in Japan are near zero and often negative over multi-year periods. Asness, Moskowitz, and Pedersen (2013) confirmed this finding across currencies and find Japan to be the clearest exception to momentum's global applicability.

**Structural explanations:**

1. **Keiretsu cross-shareholdings:** The interlocking ownership structure of major Japanese corporations (the keiretsu system) means large blocks of shares are held by cross-shareholding partners who do not trade. When individual keiretsu companies experience distress, the cross-shareholders face pressure to support rather than sell — the opposite of what momentum models assume. This dampens price discovery and creates autocorrelation patterns that are different from other markets.

2. **Main bank system:** Japanese companies maintained close relationships with a "main bank" that provided implicit guarantees of financial support. This created soft budget constraints and reduced the speed with which markets priced financial deterioration — again disrupting the fundamentals-to-price linkage that momentum strategies rely on.

3. **Corporate actions calendar:** Japanese corporate fiscal year-ends cluster heavily in March, creating strong seasonal patterns that interact with momentum signals in non-obvious ways.

**The Abe-nomics corporate governance revolution (2013–2020):**

The Abe government's Third Arrow of Abenomics targeted corporate governance reform:
- The Japan Corporate Governance Code (2015) introduced shareholder-return expectations
- The Japan Stewardship Code (2014) empowered institutional shareholders
- TSE pressure to unwind cross-shareholdings

These reforms partially transformed the Japanese equity market. The profitability signal strengthened as ROE improvement became a corporate priority. The unwinding of cross-shareholdings created a predictable supply of shares (sellers who must sell for governance, not fundamental, reasons) — a potential trading signal.

**Practical implication:** Any cross-country equity momentum strategy must either (a) exclude Japan entirely from the momentum signal or (b) apply a country-specific adjustment that zeros out Japan's momentum exposure. Failure to do so will reduce the strategy's IR by a measurable amount.

### Emerging Markets: Structural Constraints and Behavioural Opportunities

**China:** The dominant feature of Chinese A-share equity markets is the preponderance of retail investor ownership (estimated 70%+ of turnover as of 2024). This retail dominance, combined with limited short-selling availability (officially allowed since 2010 but practically constrained by borrow availability), creates conditions where:

- **Momentum** works strongly: retail investors are trend-following; limited short-selling prevents reversion arbitrage
- **Value** works weakly: state-owned enterprises often trade at deep value on fundamentals but may never re-rate due to governance issues; value traps are common
- **Profitability** works weakly: accounting quality in Chinese A-shares is variable enough that profitability signals have high noise-to-signal ratios

**India:** Among the most interesting EM equity markets from a factor perspective:

- **Momentum** is extremely strong: Agarwalla, Jacob, and Varma (2017) documented momentum alpha of approximately 1.4%/month in Indian equities from 1993–2013 — the highest documented momentum premium of any major equity market globally. Structural reasons include high retail participation, underweighting of equities in institutional portfolios, and limited arbitrage capital.

- **Accruals** show a **sign flip vs. US**: in India, high accruals stocks outperform rather than underperform. This is the opposite of the US result (Sloan 1996). The mechanism: in India, high accruals may reflect genuine growth investment rather than earnings manipulation, because accounting standards were historically more conservative and capital constraints meant that accruals were physically backed.

- **Short-selling** was banned for individual stocks at various periods and is still constrained relative to developed markets, making the short leg of factor portfolios difficult to implement.

**Brazil and Russia:** Both markets are dominated at times by political risk and macro regime changes that overwhelm any fundamental factor signal. Value works when macro is stable; momentum fails during political crisis events (when return autocorrelation breaks down due to capital flight and forced liquidation). These markets are better approached through macro-driven country allocation rather than cross-sectional factor strategies within them.

### Country-Level Factor Summary Table

| Country | Momentum | Value | Profitability | BAB | Best Single Factor |
|---|---|---|---|---|---|
| US | Strong (weakening) | Moderate | Strong | Strong | QMJ / Profitability |
| UK | Strong | Strong | Strong | Moderate | Momentum |
| Germany | Strong | Strong | Moderate | Moderate | Value |
| France | Moderate | Strong | Moderate | Moderate | Value |
| Japan | FAILS | Strong | Strong | Strong | Value |
| Australia | Strong | Strong | Moderate | Moderate | Momentum |
| Canada | Moderate | Moderate | Strong | Moderate | Profitability |
| India | Very Strong | Moderate | Moderate | Moderate | Momentum |
| China A | Strong (retail) | Weak | Weak | N/A | Momentum |
| Brazil | Weak | Strong | Weak | Weak | Value |

---

## Section 8: Multi-Country Equity Factor Construction

### The Cross-Country Approach

Rather than selecting individual stocks within each country, a macro-oriented approach selects countries (or geographic regions) based on their aggregate factor characteristics. This is sometimes called "country factor investing" and is the approach documented in Asness, Moskowitz, and Pedersen (2013, "Value and Momentum Everywhere").

The AQR 2013 paper applied value and momentum signals to eight distinct asset class universes: US stocks, UK stocks, European stocks, Japanese stocks, country equity indices, country bond markets, currencies, and commodities. The cross-asset evidence showed that value and momentum work in all eight asset classes with remarkably consistent Sharpe ratios (typically 0.4–0.7 standalone; 0.8–1.2 combined), and that the combination benefits from diversification across asset classes.

**Country equity momentum** is simply the equity index return over the past 12 months (skipping the last month):

$$\text{MOM}_{t,i} = R_{t-12,i} - R_{t-1,i}$$

where $R_{t-k,i}$ is the cumulative return of country $i$ from time $t-k$ to $t-1$.

**Country value** (earnings yield approach) is:

$$\text{VAL}_{t,i} = \frac{E_{t,i}}{P_{t,i}} = \frac{1}{PE_{t,i}}$$

For bonds, value is often proxied by real yield or yield vs. trend. For equities, book/price (B/P), earnings/price (E/P), or CAPE (cyclically adjusted P/E using 10-year average earnings) are all used.

**Country quality** can be proxied at the index level using:
- Average ROE of constituent companies (MSCI publishes this)
- Earnings revision breadth (more up-revisions = higher quality signal)
- GDP growth momentum (smoothed growth trending up vs. down)

### Full Python Implementation

```python
import pandas as pd
import numpy as np
from typing import Optional, Tuple


class GlobalEquityFactorModel:
    """
    Cross-country equity factor signal construction for country rotation strategies.
    
    Inputs:
        equity_indices: DataFrame (dates x countries) of equity index total returns (daily)
        pe_ratios: DataFrame (dates x countries) of aggregate P/E ratios (monthly)
        roe_data: DataFrame (dates x countries) of aggregate ROE (annual/quarterly)
        debt_equity: DataFrame (dates x countries) of aggregate D/E ratios
    
    All DataFrames should have a DatetimeIndex and country names as columns.
    """
    
    def __init__(self, equity_indices: pd.DataFrame, pe_ratios: pd.DataFrame,
                 roe_data: Optional[pd.DataFrame] = None,
                 debt_equity: Optional[pd.DataFrame] = None):
        self.equity_indices = equity_indices
        self.pe_ratios = pe_ratios
        self.roe_data = roe_data
        self.debt_equity = debt_equity
    
    @staticmethod
    def cross_sectional_z(df: pd.DataFrame, clip_sigma: float = 3.0) -> pd.DataFrame:
        """Z-score cross-sectionally, winsorise at +/- clip_sigma."""
        mu = df.mean(axis=1)
        sigma = df.std(axis=1)
        z = df.sub(mu, axis=0).div(sigma, axis=0)
        return z.clip(-clip_sigma, clip_sigma)
    
    def compute_country_momentum(self, lookback: int = 252,
                                  skip: int = 21,
                                  japan_adjustment: bool = True) -> pd.DataFrame:
        """
        12-1 skip-last-month cross-sectional momentum.
        
        Japan momentum is zeroed out by default, consistent with evidence
        in Fama-French (2012) and Asness et al. (2013).
        
        Args:
            lookback: Trading days for the long window (default 252 = 12 months)
            skip: Trading days for the skip window (default 21 = 1 month)
            japan_adjustment: If True, zero out Japan momentum signal
        """
        # Total return from t-lookback to t-skip
        cumret_long = np.log(self.equity_indices).diff(lookback)
        cumret_short = np.log(self.equity_indices).diff(skip)
        momentum = cumret_long - cumret_short
        
        if japan_adjustment and 'Japan' in momentum.columns:
            momentum['Japan'] = 0.0
        
        return momentum
    
    def compute_country_value(self, method: str = 'earnings_yield') -> pd.DataFrame:
        """
        Country-level value signal.
        
        Args:
            method: 'earnings_yield' (1/PE) or 'cape' for CAPE-adjusted
        """
        if method == 'earnings_yield':
            value = 1.0 / self.pe_ratios.replace(0, np.nan)
        elif method == 'cape':
            # CAPE adjustment: use rolling 10-year average earnings
            # pe_ratios should be CAPE ratios for this method
            value = 1.0 / self.pe_ratios.replace(0, np.nan)
        else:
            raise ValueError(f"Unknown method: {method}")
        
        return value
    
    def compute_country_quality(self) -> Optional[pd.DataFrame]:
        """
        Country quality: high ROE, low leverage composite.
        Higher is better quality.
        """
        if self.roe_data is None:
            return None
        
        roe_z = self.cross_sectional_z(self.roe_data)
        
        if self.debt_equity is not None:
            # Quality = high ROE, low leverage
            lev_z = self.cross_sectional_z(self.debt_equity)
            quality = roe_z - lev_z
        else:
            quality = roe_z
        
        return quality
    
    def composite_signal(
        self,
        weights: Tuple[float, ...] = (0.40, 0.40, 0.20),
        lookback: int = 252,
        skip: int = 21,
        japan_adjustment: bool = True
    ) -> pd.DataFrame:
        """
        Composite factor signal combining momentum, value, and quality.
        
        Args:
            weights: (momentum_weight, value_weight, quality_weight)
                     must sum to 1.0
            lookback, skip: Momentum parameters
            japan_adjustment: Zero out Japan momentum
        
        Returns:
            DataFrame of composite z-scores (dates x countries)
        """
        assert abs(sum(weights) - 1.0) < 1e-6, "Weights must sum to 1.0"
        
        mom = self.compute_country_momentum(lookback, skip, japan_adjustment)
        val = self.compute_country_value()
        qual = self.compute_country_quality()
        
        mom_z = self.cross_sectional_z(mom)
        val_z = self.cross_sectional_z(val)
        
        if qual is not None:
            qual_z = self.cross_sectional_z(qual)
            composite = (weights[0] * mom_z +
                         weights[1] * val_z +
                         weights[2] * qual_z)
        else:
            # Renormalise if no quality
            w_mom = weights[0] / (weights[0] + weights[1])
            w_val = weights[1] / (weights[0] + weights[1])
            composite = w_mom * mom_z + w_val * val_z
        
        return composite
    
    def build_portfolio(
        self,
        signal: pd.DataFrame,
        n_long: int = 3,
        n_short: int = 3,
        volatility_scale: bool = True,
        target_vol: float = 0.10
    ) -> pd.DataFrame:
        """
        Build long-short equity country portfolio from composite signal.
        
        Args:
            signal: Composite signal DataFrame
            n_long: Number of countries in long leg
            n_short: Number of countries in short leg
            volatility_scale: Apply ex-ante volatility scaling to target_vol
            target_vol: Annualised portfolio volatility target
        
        Returns:
            DataFrame of portfolio weights (dates x countries)
        """
        weights = pd.DataFrame(0.0, index=signal.index, columns=signal.columns)
        
        for date in signal.index:
            row = signal.loc[date].dropna()
            if len(row) < n_long + n_short:
                continue
            row_sorted = row.sort_values()
            
            # Long top-N (highest signal)
            for col in row_sorted.index[-n_long:]:
                weights.loc[date, col] = 1.0 / n_long
            
            # Short bottom-N (lowest signal)
            for col in row_sorted.index[:n_short]:
                weights.loc[date, col] = -1.0 / n_short
        
        return weights
```

### Data Sources for Global Equity Factor Research

| Data | Source | Cost | URL |
|---|---|---|---|
| US + International factor portfolios | Ken French Data Library | Free | mba.tuck.dartmouth.edu/pages/faculty/ken.french |
| Value/Momentum Everywhere | AQR Data Library | Free | aqr.com/Insights/Datasets |
| MSCI country index data | MSCI | Paid / Limited free | msci.com |
| P/E ratios, GDP (OECD) | OECD.Stat | Free | stats.oecd.org |
| Country ROE estimates | IBES / FactSet | Institutional | Via WRDS |
| National accounts (WorldBank) | World Bank Open Data | Free | data.worldbank.org |
| Country ETF prices (proxy) | Yahoo Finance, EODHD | Free/Low cost | — |

---

## Section 9: The Factor Timing Problem

### Do Factor Premiums Vary Predictably Over Time?

The naive implementation of factor investing holds factor exposures constant: always long value, always long momentum, always long quality, regardless of what economic environment prevails. This approach has worked well on average over long horizons (decades) but generates significant medium-term (6–36 month) tracking error relative to the average.

The question for a systematic practitioner is whether factor premiums are predictable enough to tilt dynamically — running more value exposure when value is likely to outperform and less when it is likely to underperform.

**Evidence for value timing:** Asness, Chandra, Ilmanen, and Israel (2017, AQR white paper "Contrarian Factor Timing Is Deceptively Difficult") found that the **value spread** — the valuation differential between the long leg and short leg of a value portfolio — has modest predictive power for value factor returns over 3–5 year horizons. When the value spread is in the top quintile historically (value stocks very cheap relative to growth stocks), subsequent value factor returns are substantially higher than average.

The 2018–2020 period was a clear case: value spreads reached historic extremes (value stocks the cheapest relative to growth since the late 1990s tech bubble), and the subsequent 2022 value recovery partially validated the timing signal.

**Formal value timing model:**

Let $VS_t$ denote the value spread (log book/market of value quintile minus log book/market of growth quintile, normalised by history). The predictive regression:

$$\text{ValueFactor}_{t+12} = \alpha + \beta \cdot VS_t + \varepsilon_{t+12}$$

Asness et al. (2017) estimate $\beta > 0$ with $t \approx 2.5$ using 40+ years of US data. The predictability is real but modest ($R^2 < 10\%$), meaning it should inform tilts of 10–20% in factor weights rather than wholesale in/out timing.

### Momentum Factor Timing: Volatility Scaling

For momentum specifically, the primary timing approach is **volatility scaling**, not valuation timing. Barroso and Santa-Clara (2015, *Journal of Financial Economics*) showed that momentum crashes (which are severe — often -40% to -60% drawdowns, as in 2009) are predictable from the time-series volatility of the momentum portfolio.

The Barroso-Santa-Clara approach scales position size inversely to realised momentum portfolio variance:

$$w_t^{MOM} = \frac{\sigma_{target}^2}{\hat{\sigma}_t^2}$$

where $\hat{\sigma}_t^2$ is the realised variance of the momentum factor over the past month, and $\sigma_{target}^2$ is the target variance. This approach reduced maximum drawdown from approximately -68% to -26% in their sample while maintaining IR above the unscaled strategy.

```python
def volatility_scaled_momentum(
    momentum_factor_returns: pd.Series,
    target_vol: float = 0.12,
    lookback_days: int = 126,
    max_leverage: float = 2.0
) -> pd.Series:
    """
    Volatility-scaled momentum factor (Barroso-Santa-Clara 2015).
    
    Scales momentum position size inversely to realised variance,
    targeting a constant annualised volatility.
    
    Args:
        momentum_factor_returns: Daily returns of momentum factor
        target_vol: Target annualised volatility (default 12%)
        lookback_days: Lookback for realised vol estimate (default 6 months)
        max_leverage: Maximum allowed leverage multiplier
    
    Returns:
        Scaled momentum factor returns
    """
    # Realised daily variance, then annualise
    realised_var = (momentum_factor_returns
                    .rolling(lookback_days)
                    .var() * 252)
    
    # Scale factor: target_vol^2 / realised_var
    scale = (target_vol ** 2) / realised_var
    scale = scale.clip(upper=max_leverage)  # cap leverage
    
    # Scaled returns (note: scale applies from next day forward)
    scaled_returns = scale.shift(1) * momentum_factor_returns
    
    return scaled_returns
```

### Business Cycle Factor Rotation

Empirical evidence on factor performance across business cycle phases (Ilmanen, 2011, "Expected Returns"; Arnott, 2016, "The Fundamental Index"):

| Business Cycle Phase | Characterisation | Outperforming Factors | Underperforming Factors |
|---|---|---|---|
| Early recovery | PMI rising from below 50; credit spreads tightening | Value, High Beta | Low Volatility, Quality |
| Mid-cycle expansion | PMI above 50; earnings growth accelerating | Quality, Momentum | Value (mean reversion) |
| Late cycle | PMI near peak; inflation rising; yield curve flattening | Low Volatility, Dividend | Momentum (reversals) |
| Recession | PMI below 50; earnings declining; credit widening | Low Volatility, Quality | Value, Momentum |

**Real-time business cycle proxy (tradeable signal):**
- Use ISM Manufacturing PMI > 50 as expansion signal; < 50 as contraction signal
- Apply a 3-month moving average to reduce noise
- Shift factor weights: +10% to expansion-favouring factors when PMI > 52; +10% to contraction-favouring when PMI < 48

**Warning:** Be extremely careful about lookahead bias in business cycle-based factor timing. NBER recession dates are assigned ex-post, often 6–18 months after the event. Any backtest that uses NBER dates to allocate factor exposure in real time is using lookahead information and will significantly overstate live performance.

### The Equity Carry Factor

**Equity carry** is the expected return of holding an equity market position for the next period, holding prices constant. For equity indices, carry decomposes into:

$$\text{Equity Carry} = \text{Dividend Yield} + \text{Buyback Yield} - \text{Cost of Financing}$$

The sum of dividend yield and buyback yield is the **total shareholder yield** (TSY). Countries with high TSY have more attractive equity carry, which predicts higher subsequent returns in the same way that FX carry predicts currency returns.

This is a direct bridge between FX systematic trading (which the reader has been doing) and global equity factor investing. The AQR global factor data confirms that high-TSY countries outperform low-TSY countries with a Sharpe ratio of approximately 0.4–0.5 on a long/short basis. Combined with momentum and valuation signals, equity carry improves the composite country rotation strategy.

### Factor Crowding Detection

When factor strategies attract too much capital — through the proliferation of factor ETFs, the expansion of quant funds running the same strategies, and retail adoption of "smart beta" — the strategies become crowded. Crowded factor trades carry elevated crash risk: when a liquidity shock forces simultaneous liquidation, all factors in the same direction move sharply against.

**The 2007 quant meltdown (Khandani and Lo, 2011, *Journal of Portfolio Management*)** is the canonical example. In the week of August 6–9, 2007, multiple quantitative equity long-short funds experienced unprecedented simultaneous factor drawdowns, despite no unusual macro events. The cause was forced deleveraging by one or more large funds, whose sales created cascading losses in other funds holding similar factor portfolios. The drawdowns were temporary (mostly recovered within 2 weeks) but severe (-10% to -20% in days for some funds).

**Crowding indicators to monitor:**

| Indicator | What It Measures | Source |
|---|---|---|
| AUM in factor ETFs | Size of retail capital in factor exposures | Bloomberg, ETF.com |
| Factor portfolio bid-ask spread | Wider spreads on both legs simultaneously | Market data |
| Cross-factor IC correlation | Rising correlation between factor signals | Computed from factor returns |
| Short interest in factor long leg | High SI suggests many funds shorting the same stocks | FINRA, S3 Partners |
| Factor dispersion (vol of IC) | Higher volatility of factor IC = crowding | Computed from factor returns |

When multiple crowding indicators are elevated simultaneously, prudent risk management calls for reducing gross factor exposure, increasing portfolio diversification, or adding tail risk hedges (e.g., put options on index ETFs).

---

## Section 10: A Practical Global Equity Factor Strategy for a Discretionary Trader

### Starting Simple: Country Rotation

For an experienced discretionary macro trader building a first systematic global equity strategy, the appropriate starting point is **country rotation** — allocating across equity indices rather than individual stocks. This approach:

1. Leverages existing macro intuition (country-level views are familiar)
2. Avoids stock-specific liquidity constraints
3. Is implementable with liquid futures or ETFs
4. Has documented factor evidence (AQR 2013)
5. Has lower data and model complexity than individual stock selection

The simplest version combines momentum and value at the country level:

```python
def country_rotation_signal(
    equity_returns: pd.DataFrame,
    pe_ratios: pd.DataFrame,
    exclude_japan_momentum: bool = True,
    lookback_momentum: int = 252,
    skip_momentum: int = 21
) -> pd.DataFrame:
    """
    Cross-country rotation signal: momentum + value combination.
    
    Equity return inputs should be daily total returns (including dividends).
    PE ratio inputs should be monthly (or resampled to monthly) aggregate P/E.
    
    Args:
        equity_returns: Daily equity index returns (dates x countries)
        pe_ratios: Monthly aggregate P/E ratios (dates x countries)
        exclude_japan_momentum: Zero out Japan's momentum signal
        lookback_momentum: Days for momentum long window
        skip_momentum: Days for momentum skip window
    
    Returns:
        Monthly composite signal (dates x countries), higher = more attractive
    """
    # 12-1 skip-last-month momentum
    log_returns = np.log(1 + equity_returns)
    cum_long = log_returns.rolling(lookback_momentum).sum()
    cum_short = log_returns.rolling(skip_momentum).sum()
    momentum = cum_long - cum_short
    
    # Resample to monthly for combination with monthly PE data
    momentum_monthly = momentum.resample('ME').last()
    
    # Earnings yield (value signal)
    earnings_yield = 1.0 / pe_ratios.replace(0, np.nan)
    
    # Align index
    common_dates = momentum_monthly.index.intersection(earnings_yield.index)
    momentum_monthly = momentum_monthly.loc[common_dates]
    earnings_yield = earnings_yield.loc[common_dates]
    
    # Zero out Japan momentum
    if exclude_japan_momentum and 'Japan' in momentum_monthly.columns:
        momentum_monthly = momentum_monthly.copy()
        momentum_monthly['Japan'] = 0.0
    
    # Cross-sectional z-score
    def cs_z(df: pd.DataFrame) -> pd.DataFrame:
        mu = df.mean(axis=1)
        sigma = df.std(axis=1)
        return df.sub(mu, axis=0).div(sigma, axis=0).clip(-3, 3)
    
    mom_z = cs_z(momentum_monthly)
    val_z = cs_z(earnings_yield)
    
    # Equal-weight combination
    composite = 0.5 * mom_z + 0.5 * val_z
    
    return composite


def build_portfolio(
    signal: pd.DataFrame,
    n_long: int = 3,
    n_short: int = 3
) -> pd.DataFrame:
    """
    Long-short country portfolio from composite signal.
    Goes long n_long highest-signal countries, short n_short lowest-signal.
    Weights are equal within each leg.
    """
    portfolio = pd.DataFrame(0.0, index=signal.index, columns=signal.columns)
    
    for date in signal.index:
        row = signal.loc[date].dropna()
        if len(row) < n_long + n_short:
            continue
        row_sorted = row.sort_values()
        
        for col in row_sorted.index[-n_long:]:
            portfolio.loc[date, col] = 1.0 / n_long
        
        for col in row_sorted.index[:n_short]:
            portfolio.loc[date, col] = -1.0 / n_short
    
    return portfolio
```

### Expected Performance

Based on published evidence (AQR 2013; French Data Library factor portfolios; Haddad, Kozak, Santosh 2020):

| Strategy Component | Standalone Sharpe | Notes |
|---|---|---|
| Country momentum only | 0.50–0.70 | Without Japan momentum |
| Country value only (E/Y) | 0.40–0.60 | Stronger in periods of high macro uncertainty |
| Combined (50/50) | 0.60–0.80 | Diversification benefit from low correlation |
| Japan momentum excluded | +0.05–0.15 IR | Consistent improvement; removes known anomaly |
| Add quality signal | +0.05–0.10 IR | Incremental; dependent on data quality |

These Sharpe ratios are **before transaction costs**. Realistic implementation costs for country ETFs (bid-ask + market impact) are approximately 5–10 bps per trade. With monthly rebalancing on a 6-country portfolio, annual turnover is 2–3x, implying 10–30 bps/year in total costs — manageable.

### Implementation Vehicles

**Country ETFs (long-only leg or long/short with ETF borrow):**

| Country | iShares ETF | Ticker | Avg Daily Volume | Expense Ratio |
|---|---|---|---|---|
| Germany | iShares MSCI Germany | EWG | High | 0.50% |
| United Kingdom | iShares MSCI United Kingdom | EWU | High | 0.50% |
| Japan | iShares MSCI Japan | EWJ | Very High | 0.50% |
| Australia | iShares MSCI Australia | EWA | Moderate | 0.50% |
| Canada | iShares MSCI Canada | EWC | High | 0.50% |
| France | iShares MSCI France | EWQ | Moderate | 0.50% |
| South Korea | iShares MSCI South Korea | EWY | Moderate | 0.59% |
| India | iShares MSCI India | INDA | High | 0.65% |

**Equity Futures (preferred for institutional implementation):**

| Market | Contract | Exchange | Currency | Liquidity |
|---|---|---|---|---|
| Eurostoxx 50 | SX5E | Eurex | EUR | Very High |
| FTSE 100 | Z | ICE London | GBP | Very High |
| DAX | FDAX | Eurex | EUR | Very High |
| Nikkei 225 | NK | CME / OSE | JPY | Very High |
| ASX SPI 200 | AP | ASX 24 | AUD | High |
| CAC 40 | FCE | Euronext | EUR | High |
| MSCI Emerging Markets | EEM | CME | USD | High |
| MSCI EAFE | MFS | CME | USD | Moderate |

Futures are preferred over ETFs for institutional implementation because:
1. No stock borrow cost on short positions (futures are inherently short-able)
2. Lower effective bid-ask spreads at scale
3. No tracking error to NAV
4. Embedded leverage allows better capital efficiency

### Currency Hedging: The FX-Equity Interaction

For an FX trader running a global equity strategy, currency exposures are both a risk and an opportunity. An equity position in Japan denominated in JPY, held by a USD-base-currency investor, has an embedded long JPY position. This FX exposure can either be:

1. **Hedged** using FX forwards or swaps to remove the currency P&L
2. **Unhedged** to pick up carry if the foreign currency has positive carry vs. USD
3. **Partially hedged** based on a view from the existing FX systematic strategy

The interaction between FX carry and equity carry is particularly interesting: countries with high FX carry (high interest rates) often also have stressed economic conditions (monetary tightening to fight inflation), which may be negative for equity factor signals. Conversely, countries with low FX carry (safe-haven currencies) may have strong equity quality signals. Integrating both signals requires careful thinking about the sign of each exposure.

**Practical hedging rule for a multi-country equity strategy:**
- Default: hedge 100% of currency exposure back to base currency; isolate the equity factor signal
- Alternative: run the FX carry strategy separately and allow the equity strategy to have unhedged FX exposure only when the FX carry signal agrees in direction with the equity signal (aligned carry)

### Risk Management for Global Equity Factor Strategies

**Equity beta management:**

Long/short factor strategies maintain significant positive equity beta in risk-off environments, because factor premia tend to correlate positively with the equity market during stress. The reason: in a crisis, all equities fall together, and the short leg of a factor portfolio (which is typically in lower-quality, more distressed companies) may fall more than the long leg, providing some hedge. But the overall portfolio is still net long risk.

**Standard approach:** target 0 net beta at inception; monitor beta weekly; when realised beta drifts above 0.3 or below -0.3, rebalance. Use index futures to hedge residual market exposure.

**Volatility regime management:**

When VIX > 25, systematic reduction of equity factor exposure is warranted because:
1. Factor returns during high-volatility periods have negative skewness
2. Transaction costs increase with volatility, reducing net alpha
3. Crowding risks are highest during deleveraging events that correlate with VIX spikes

```python
def apply_vol_regime_filter(
    portfolio_weights: pd.DataFrame,
    vix: pd.Series,
    high_vol_threshold: float = 25.0,
    reduction_factor: float = 0.50
) -> pd.DataFrame:
    """
    Scale down equity factor exposure during high volatility regimes.
    
    When VIX exceeds threshold, multiply all weights by reduction_factor.
    This reduces exposure during tail-risk periods.
    
    Args:
        portfolio_weights: Factor portfolio weights (dates x countries)
        vix: VIX index level (daily)
        high_vol_threshold: VIX level above which to reduce (default 25)
        reduction_factor: Multiplier applied when VIX > threshold (default 0.50)
    
    Returns:
        Adjusted portfolio weights
    """
    vix_monthly = vix.resample('ME').last()
    vix_aligned = vix_monthly.reindex(portfolio_weights.index, method='ffill')
    
    # Scale factor: 1.0 when VIX normal, reduction_factor when VIX elevated
    scale = pd.Series(
        np.where(vix_aligned > high_vol_threshold, reduction_factor, 1.0),
        index=portfolio_weights.index
    )
    
    return portfolio_weights.mul(scale, axis=0)
```

### Integration with Systematic FX Strategy

For a practitioner who already runs a systematic G10 FX strategy, global equity factors can serve as:

1. **A complement:** The correlation between G10 FX carry and global equity factor strategies is typically low (0.10–0.25 at monthly frequency), providing genuine diversification. A combined multi-strategy book that allocates 60% to FX systematic and 40% to global equity factors has historically had a higher IR than either strategy alone.

2. **A validation signal:** Country equity factor scores (particularly value and quality) can serve as soft validation or contradiction signals for G10 FX views. If the FX strategy is long CHF based on carry + trend, and the equity strategy is also signalling long Switzerland (high equity quality), the signals reinforce each other. If they diverge, it is worth examining the source of disagreement.

3. **A currency risk overlay:** Running a global equity factor strategy naturally exposes the portfolio to the currencies of the countries in the long leg. A practitioner with an FX carry model can align the equity strategy's currency exposure with the FX carry ranking — effectively receiving carry on both the equity and currency components simultaneously.

---

## Key References

### Alternative Data

- Chen, M., Cohen, L., Li, B., & Lou, D. (2020). *Paying Attention: Overnight Returns and the Hidden Cost of Buying at the Open*. Journal of Financial Economics.
- Choi, H., & Varian, H. (2012). Predicting the present with Google Trends. *Economic Journal*, 122(556), 306-328.
- Da, Z., Engelberg, J., & Gao, P. (2011). In search of attention. *Journal of Finance*, 66(5), 1461-1499.
- Desai, P., Hao, T., & Simon, R. (2016). *Satellite-Based Monitoring of Crude Oil Storage*. Orbital Insight White Paper.
- Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. *Journal of Finance*, 66(1), 35-65.
- Araci, D. (2019). FinBERT: Financial sentiment analysis with pre-trained language models. *arXiv:1908.10063*.

### Global Equity Factors

- Asness, C. S., Moskowitz, T. J., & Pedersen, L. H. (2013). Value and momentum everywhere. *Journal of Finance*, 68(3), 929-985.
- Barroso, P., & Santa-Clara, P. (2015). Momentum has its moments. *Journal of Financial Economics*, 116(1), 111-120.
- Fama, E. F., & French, K. R. (2012). Size, value, and momentum in international stock returns. *Journal of Financial Economics*, 105(3), 457-472.
- Harvey, C. R., Liu, Y., & Zhu, H. (2016). … and the cross-section of expected returns. *Review of Financial Studies*, 29(1), 5-68.
- Hou, K., Xue, C., & Zhang, L. (2020). Replicating anomalies. *Review of Financial Studies*, 33(5), 2019-2133.
- Khandani, A. E., & Lo, A. W. (2011). What happened to the quants in August 2007? Evidence from factors and transactions data. *Journal of Financial Markets*, 14(1), 1-46.
- McLean, R. D., & Pontiff, J. (2016). Does academic research destroy stock return predictability? *Journal of Finance*, 71(1), 5-32.
- Agarwalla, S. K., Jacob, J., & Varma, J. R. (2017). Four-factor model in Indian equities market. *Working Paper*, Indian Institute of Management Ahmedabad.
- Asness, C., Chandra, S., Ilmanen, A., & Israel, R. (2017). *Contrarian Factor Timing Is Deceptively Difficult*. AQR White Paper.
- Ilmanen, A. (2011). *Expected Returns: An Investor's Guide to Harvesting Market Rewards*. John Wiley & Sons.

---

*Document end. Word count: approximately 11,500 words.*  
*All Python code is for research and educational purposes. No live trading signals should be derived directly from this document without independent validation.*
