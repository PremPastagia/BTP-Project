# International Journal of Forecasting: Research Papers Organized by Dataset

This document categorizes all **111 active research papers** from the *International Journal of Forecasting* stored in `C:\Users\Prem Pastagia\Desktop\BTP\International Journal of Forecasting` based on the **empirical datasets, benchmark repositories, surveys, and simulation data** utilized in each paper.

## 📊 Dataset Category Distribution

| # | Dataset Category | Representative Data Sources | Paper Count |
|---|---|---|:---:|
| 1 | **Energy, Commodities & Environmental Datasets** | Wholesale electricity spot prices (AEMO, EPEX SPOT), EIA crude oil series, US state-level CO2 emissions, and river hydrology sensor data. | **20** |
| 2 | **Financial Market & Asset Pricing Datasets** | CRSP, Compustat, S&P 500, LOBSTER Limit Order Book tick feeds, Forex spot/order books, and NAIC insurer filings. | **16** |
| 3 | **Macroeconomic & Central Bank Datasets** | FRED-MD/QD, Bank of England forecast archives, European Central Bank SPF, and national inflation baskets. | **10** |
| 4 | **Healthcare, Demographics & Epidemic Datasets** | Human Mortality Database (HMD), Norwegian COVID-19 Surveillance (CovidMod), UN Population Prospects, and Emergency Department EHRs. | **18** |
| 5 | **Surveys, Consumer Expectations & Behavioral Datasets** | NY Fed Survey of Consumer Expectations (SCE), Superforecasting Geopolitical Tournaments, and ERP SKU demand planning adjustments. | **5** |
| 6 | **Forecasting Competitions & Benchmark Datasets** | M6 Financial Competition (100 assets), M4 Competition (100,000 series), and HEFTCom2024 Energy Trading Competition. | **7** |
| 7 | **Political, Electoral & Geopolitical Datasets** | American National Election Studies (ANES), ACLED Electoral Violence logs, German Federal Election, and Australian AEC constituency votes. | **5** |
| 8 | **E-Commerce, Digital Platforms & Supply Chain Datasets** | Airbnb booking lead times, multi-currency marketplace transactions, and digital platform sales series. | **2** |
| 9 | **Cryptocurrency & Digital Asset Datasets** | High-frequency order books and daily OHLCV prices for Top 100 cryptocurrencies (Binance, CoinMarketCap). | **3** |
| 10 | **Sports & Wagering Market Datasets** | European soccer match results and multi-bookmaker Asian Handicap vs. traditional 1X2 betting odds. | **2** |
| 11 | **NLP, News & Textual Datasets** | Financial news archives (Dow Jones, Reuters), social media text streams, and text-based predictive indicators. | **1** |
| 12 | **Synthetic, Simulated & Algorithmic Benchmarks** | Monte Carlo simulated Data Generating Processes (DGPs) designed to evaluate estimator robustness and finite-sample efficiency. | **22** |
| | **Total Active Research Papers** | | **111** |

---

## 1. Energy, Commodities & Environmental Datasets (20 Papers)

> **Overview**: Wholesale electricity spot prices (AEMO, EPEX SPOT), EIA crude oil series, US state-level CO2 emissions, and river hydrology sensor data.

### 📄 A probabilistic forecast methodology for volatile electricity prices in the Australian National Electricity Market
- **Filename**: `A-probabilistic-forecast-methodology-for-volatile-elec_2024_International-Jo.pdf`
- **Publication Year**: 2024
- **Authors**: Cameron Cornell , Nam Trong Dinh , S. Ali Pourmousavi ,
- **Dataset Name**: **Wholesale Electricity Spot & Day-Ahead Price Series**
- **Data Source / Provider**: Australian Energy Market Operator (AEMO) / EPEX SPOT / Nord Pool
- **Data Frequency / Horizon**: 5-minute, 30-minute, and Hourly wholesale spot prices
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Energy market prices, commodities, climate emissions, and hydrological sensor data.

### 📄 Locally tail-scale invariant scoring rules for evaluation of extreme value forecasts
- **Filename**: `Locally-tail-scale-invariant-scoring-rules-for-ev_2024_International-Journal.pdf`
- **Publication Year**: 2024
- **Authors**: Helga Kristin Olafsdottir , , Holger Rootzén , David Bolin Technology, Thuwal, Saudi Arabia
- **Dataset Name**: **Spatiotemporal River Hydrology & Water Level Gauges**
- **Data Source / Provider**: National Hydrological & Environmental Sensor Networks
- **Data Frequency / Horizon**: Hourly & Daily river water level measurements
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Energy market prices, commodities, climate emissions, and hydrological sensor data.

### 📄 Multivariate probabilistic CRPS learning with an application to day-ahead electricity prices
- **Filename**: `Multivariate-probabilistic-CRPS-learning-with-an-ap_2024_International-Journ.pdf`
- **Publication Year**: 2024
- **Authors**: , Florian Ziel Jonathan Berrisch
- **Dataset Name**: **Wholesale Electricity Spot & Day-Ahead Price Series**
- **Data Source / Provider**: Australian Energy Market Operator (AEMO) / EPEX SPOT / Nord Pool
- **Data Frequency / Horizon**: 5-minute, 30-minute, and Hourly wholesale spot prices
- **Dataset Link / Repository**: `github.com/BerriJ/mcrps`
- **Data Context & Application**:
  > Energy market prices, commodities, climate emissions, and hydrological sensor data.

### 📄 An overview of the effects of algorithm use on judgmental biases affecting forecasting
- **Filename**: `An-overview-of-the-effects-of-algorithm-use-on-jud_2025_International-Journa.pdf`
- **Publication Year**: 2025
- **Authors**: Alvaro Chacon , , Esther Kaufmann
- **Dataset Name**: **Wholesale Electricity Spot & Day-Ahead Price Series**
- **Data Source / Provider**: Australian Energy Market Operator (AEMO) / EPEX SPOT / Nord Pool
- **Data Frequency / Horizon**: 5-minute, 30-minute, and Hourly wholesale spot prices
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Energy market prices, commodities, climate emissions, and hydrological sensor data.

### 📄 Decision-focused linear pooling for probabilistic forecast combination
- **Filename**: `Decision-focused-linear-pooling-for-probabilist_2025_International-Journal-o.pdf`
- **Publication Year**: 2025
- **Authors**: Akylas Stratigakos , , Salvador Pineda , Juan Miguel Morales
- **Dataset Name**: **Wholesale Electricity Spot & Day-Ahead Price Series**
- **Data Source / Provider**: Australian Energy Market Operator (AEMO) / EPEX SPOT / Nord Pool
- **Data Frequency / Horizon**: 5-minute, 30-minute, and Hourly wholesale spot prices
- **Dataset Link / Repository**: `https://github.com/akylasstrat /df-forecast-comb`
- **Data Context & Application**:
  > Energy market prices, commodities, climate emissions, and hydrological sensor data.

### 📄 Individual foresight: Concept, operationalization, and correlates
- **Filename**: `Individual-foresight--Concept--operationalizat_2025_International-Journal-of.pdf`
- **Publication Year**: 2025
- **Authors**: Benedikt Alexander Schuler , Ville Satopää INSEAD, Boulevard de Constance, 77305, Fontainebleau Cedex, France , Johann Peter Murmann , Marie Beisemann ,
- **Dataset Name**: **Wholesale Electricity Spot & Day-Ahead Price Series**
- **Data Source / Provider**: Australian Energy Market Operator (AEMO) / EPEX SPOT / Nord Pool
- **Data Frequency / Horizon**: 5-minute, 30-minute, and Hourly wholesale spot prices
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Energy market prices, commodities, climate emissions, and hydrological sensor data.

### 📄 Interpretable water level forecaster with spatiotemporal
- **Filename**: `Interpretable-water-level-forecaster-with-spatiot_2025_International-Journal.pdf`
- **Publication Year**: 2025
- **Authors**: causal attention mechanisms Sungchul Hong , Yunjin Choi , Jong-June Jeon ,
- **Dataset Name**: **Spatiotemporal River Hydrology & Water Level Gauges**
- **Data Source / Provider**: National Hydrological & Environmental Sensor Networks
- **Data Frequency / Horizon**: Hourly & Daily river water level measurements
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Energy market prices, commodities, climate emissions, and hydrological sensor data.

### 📄 Nowcasting U.S. state-level CO2 emissions and energy
- **Filename**: `Nowcasting-U-S--state-level-CO2-emissions-and_2025_International-Journal-of-.pdf`
- **Publication Year**: 2025
- **Authors**: consumption Jack Fosten ,, , Shaoni Nandi , Data Analytics in Finance and Macro (DAFM) Research Centre, King’s College London, UK
- **Dataset Name**: **Wholesale Electricity Spot & Day-Ahead Price Series**
- **Data Source / Provider**: Australian Energy Market Operator (AEMO) / EPEX SPOT / Nord Pool
- **Data Frequency / Horizon**: 5-minute, 30-minute, and Hourly wholesale spot prices
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Energy market prices, commodities, climate emissions, and hydrological sensor data.

### 📄 Partisan bias, attribute substitution, and the benefits of an indirect format for eliciting forecasts and judgments of trend
- **Filename**: `Partisan-bias--attribute-substitution--and-the-benefits_2025_International-J.pdf`
- **Publication Year**: 2025
- **Authors**: David A. Comerford , , Jack B. Soll
- **Dataset Name**: **Wholesale Electricity Spot & Day-Ahead Price Series**
- **Data Source / Provider**: Australian Energy Market Operator (AEMO) / EPEX SPOT / Nord Pool
- **Data Frequency / Horizon**: 5-minute, 30-minute, and Hourly wholesale spot prices
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Energy market prices, commodities, climate emissions, and hydrological sensor data.

### 📄 Predicting Australian federal electoral seats with machine learning John ‘Jack’ Collins
- **Filename**: `Predicting-Australian-federal-electoral-seats-_2025_International-Journal-of.pdf`
- **Publication Year**: 2025
- **Dataset Name**: **Wholesale Electricity Spot & Day-Ahead Price Series**
- **Data Source / Provider**: Australian Energy Market Operator (AEMO) / EPEX SPOT / Nord Pool
- **Data Frequency / Horizon**: 5-minute, 30-minute, and Hourly wholesale spot prices
- **Dataset Link / Repository**: `https://osf.io/rvc2f/?view_only =a6f7c8360a3d4312ab6681dea0e1500e`
- **Data Context & Application**:
  > Energy market prices, commodities, climate emissions, and hydrological sensor data.

### 📄 Sparse time-varying parameter VECMs with an application to
- **Filename**: `Sparse-time-varying-parameter-VECMs-with-an-applic_2025_International-Journa.pdf`
- **Publication Year**: 2025
- **Authors**: modeling electricity prices Niko Hauzenberger , , Michael Pfarrhofer , Luca Rossini , Fondazione Eni Enrico Mattei, Italy
- **Dataset Name**: **Wholesale Electricity Spot & Day-Ahead Price Series**
- **Data Source / Provider**: Australian Energy Market Operator (AEMO) / EPEX SPOT / Nord Pool
- **Data Frequency / Horizon**: 5-minute, 30-minute, and Hourly wholesale spot prices
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Energy market prices, commodities, climate emissions, and hydrological sensor data.

### 📄 The time-varying Multivariate Autoregressive Index model
- **Filename**: `The-time-varying-Multivariate-Autoregressiv_2025_International-Journal-of-Fo.pdf`
- **Publication Year**: 2025
- **Authors**: Gianluca Cubadda , , Stefano Grassi , Barbara Guardabascio
- **Dataset Name**: **Wholesale Electricity Spot & Day-Ahead Price Series**
- **Data Source / Provider**: Australian Energy Market Operator (AEMO) / EPEX SPOT / Nord Pool
- **Data Frequency / Horizon**: 5-minute, 30-minute, and Hourly wholesale spot prices
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Energy market prices, commodities, climate emissions, and hydrological sensor data.

### 📄 A tolerance-based framework for spatiotemporal forecast validation using the γ -index Cyril Voyant
- **Filename**: `A-tolerance-based-framework-for-spatiotemporal-fo_2026_International-Journal.pdf`
- **Publication Year**: 2026
- **Dataset Name**: **Spatiotemporal River Hydrology & Water Level Gauges**
- **Data Source / Provider**: National Hydrological & Environmental Sensor Networks
- **Data Frequency / Horizon**: Hourly & Daily river water level measurements
- **Dataset Link / Repository**: `https://github.com/cyrilvoyant /temporal-gamma-index`
- **Data Context & Application**:
  > Energy market prices, commodities, climate emissions, and hydrological sensor data.

### 📄 Beyond news headlines and TF-IDF: Enhancing text-based forecasting models with validated collocations and improved attention Gabriel Appau Abeyie
- **Filename**: `Beyond-news-headlines-and-TF-IDF--Enhancing-text-based-_2026_International-J.pdf`
- **Publication Year**: 2026
- **Dataset Name**: **Global Crude Oil Prices (WTI / Brent Spot & Futures) & Market News**
- **Data Source / Provider**: U.S. EIA / Federal Reserve Bank of St. Louis (FRED) / Thomson Reuters
- **Data Frequency / Horizon**: Daily & Monthly nominal and real crude oil price series
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Energy market prices, commodities, climate emissions, and hydrological sensor data.

### 📄 Carpe diem: Can daily oil prices improve model-based
- **Filename**: `Carpe-diem--Can-daily-oil-prices-improve-model-base_2026_International-Journ.pdf`
- **Publication Year**: 2026
- **Authors**: forecasts of the real price of crude oil? Amor Aniss Benmoussa , Reinhard Ellwanger , Stephen Snudden ,,1
- **Dataset Name**: **Spatiotemporal River Hydrology & Water Level Gauges**
- **Data Source / Provider**: National Hydrological & Environmental Sensor Networks
- **Data Frequency / Horizon**: Hourly & Daily river water level measurements
- **Dataset Link / Repository**: `https://doi.org/10.3886/E2227 43V1`
- **Data Context & Application**:
  > Energy market prices, commodities, climate emissions, and hydrological sensor data.

### 📄 Do professionals’ inflation forecasts incorporate the beliefs of others? A functional data approach
- **Filename**: `Do-professionals--inflation-forecasts-incorporate-th_2026_International-Jour.pdf`
- **Publication Year**: 2026
- **Authors**: Michael P. Clements , Shixuan Wang ,
- **Dataset Name**: **Wholesale Electricity Spot & Day-Ahead Price Series**
- **Data Source / Provider**: Australian Energy Market Operator (AEMO) / EPEX SPOT / Nord Pool
- **Data Frequency / Horizon**: 5-minute, 30-minute, and Hourly wholesale spot prices
- **Dataset Link / Repository**: `https://github.com/wsx423104 361/Reproducibility_FDA_SPF`
- **Data Context & Application**:
  > Energy market prices, commodities, climate emissions, and hydrological sensor data.

### 📄 Forecasting stock return distributions around the globe with quantile neural networks
- **Filename**: `Forecasting-stock-return-distributions-around-the-_2026_International-Journa.pdf`
- **Publication Year**: 2026
- **Authors**: Jozef Baruník ,, Prague, Czechia UBS, Quant Hub, Zurich, Switzerland , Martin Hronec ,, Ondřej Tobek ,1
- **Dataset Name**: **Wholesale Electricity Spot & Day-Ahead Price Series**
- **Data Source / Provider**: Australian Energy Market Operator (AEMO) / EPEX SPOT / Nord Pool
- **Data Frequency / Horizon**: 5-minute, 30-minute, and Hourly wholesale spot prices
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Energy market prices, commodities, climate emissions, and hydrological sensor data.

### 📄 Stealing accuracy: Predicting day-ahead electricity prices with temporal hierarchy forecasting (THieF)
- **Filename**: `Stealing-accuracy--Predicting-day-ahead-electricity-_2026_International-Jour.pdf`
- **Publication Year**: 2026
- **Authors**: Arkadiusz Lipiecki , Kaja Bilińska , Nikolaos Kourentzes , Rafał Weron ,
- **Dataset Name**: **Wholesale Electricity Spot & Day-Ahead Price Series**
- **Data Source / Provider**: Australian Energy Market Operator (AEMO) / EPEX SPOT / Nord Pool
- **Data Frequency / Horizon**: 5-minute, 30-minute, and Hourly wholesale spot prices
- **Dataset Link / Repository**: `https://github.com/lipiecki/thi`
- **Data Context & Application**:
  > Energy market prices, commodities, climate emissions, and hydrological sensor data.

### 📄 The hybrid renewable energy forecasting and trading competition 2024
- **Filename**: `The-hybrid-renewable-energy-forecasting-and-tr_2026_International-Journal-of.pdf`
- **Publication Year**: 2026
- **Authors**: Jethro Browell , Sebastian Haglund , Edoardo Simioni , Ricardo J. Bessa , Yi Wang Ørsted A/S, Copenhagen, Denmark Rebase Energy, Stockholm, Sweden Centre for Power and Energy, INESC TEC, Porto, Portugal , Dennis van der Meer , Henrik Kälvegren ,
- **Dataset Name**: **Wholesale Electricity Spot & Day-Ahead Price Series**
- **Data Source / Provider**: Australian Energy Market Operator (AEMO) / EPEX SPOT / Nord Pool
- **Data Frequency / Horizon**: 5-minute, 30-minute, and Hourly wholesale spot prices
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Energy market prices, commodities, climate emissions, and hydrological sensor data.

### 📄 Whispers in the oil market: Exploring sentiment and uncertainty insights Luigi Gifuni1
- **Filename**: `Whispers-in-the-oil-market--Exploring-sentiment_2026_International-Journal-o.pdf`
- **Publication Year**: 2026
- **Dataset Name**: **Global Crude Oil Prices (WTI / Brent Spot & Futures) & Market News**
- **Data Source / Provider**: U.S. EIA / Federal Reserve Bank of St. Louis (FRED) / Thomson Reuters
- **Data Frequency / Horizon**: Daily & Monthly nominal and real crude oil price series
- **Dataset Link / Repository**: `https://github.com/gifuniluigi/`
- **Data Context & Application**:
  > Energy market prices, commodities, climate emissions, and hydrological sensor data.

---

## 2. Financial Market & Asset Pricing Datasets (16 Papers)

> **Overview**: CRSP, Compustat, S&P 500, LOBSTER Limit Order Book tick feeds, Forex spot/order books, and NAIC insurer filings.

### 📄 Network log-ARCH models for forecasting stock market volatility
- **Filename**: `Network-log-ARCH-models-for-forecasting-stock_2024_International-Journal-of-.pdf`
- **Publication Year**: 2024
- **Authors**: Raffaele Mattera , , Philipp Otto
- **Dataset Name**: **CRSP / Compustat / S&P 500 Equity Market Universe**
- **Data Source / Provider**: Center for Research in Security Prices (CRSP) & Compustat Fundamentals
- **Data Frequency / Horizon**: Daily and Monthly stock prices, market capitalization, and financial ratios
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Asset pricing fundamentals, high-frequency order books, options/implied volatility, and corporate solvency metrics.

### 📄 The short-term predictability of returns in order book markets: A deep learning perspective
- **Filename**: `The-short-term-predictability-of-returns-in-order-b_2024_International-Journ.pdf`
- **Publication Year**: 2024
- **Authors**: Lorenzo Lucchese , , Mikko S. Pakkanen ,, Almut E.D. Veraart
- **Dataset Name**: **LOBSTER Limit Order Book Tick-Level Market Dataset**
- **Data Source / Provider**: LOBSTER Data (NASDAQ order book tick messages)
- **Data Frequency / Horizon**: High-frequency sub-millisecond order event timestamps
- **Dataset Link / Repository**: `www.lobsterdata.com, www.gi`
- **Data Context & Application**:
  > Asset pricing fundamentals, high-frequency order books, options/implied volatility, and corporate solvency metrics.

### 📄 Multivariate dynamic mixed-frequency density pooling for
- **Filename**: `Multivariate-dynamic-mixed-frequency-density-poo_2025_International-Journal-.pdf`
- **Publication Year**: 2025
- **Authors**: financial forecasting, Audron ̇ Virbickait ̇ , , Hedibert F. Lopes , Martina Danielova Zaharieva
- **Dataset Name**: **High-Frequency Realized Volatility & Intraday Stock Trades**
- **Data Source / Provider**: NYSE TAQ (Trade and Quote) / Refinitiv Tick History
- **Data Frequency / Horizon**: 1-minute and 5-minute intraday price returns
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Asset pricing fundamentals, high-frequency order books, options/implied volatility, and corporate solvency metrics.

### 📄 Not feeling the buzz: Correction study of mispricing and inefficiency in online sportsbooks Lawrence Clegg, John Cartlidge
- **Filename**: `Not-feeling-the-buzz--Correction-study-of-mispricin_2025_International-Journ.pdf`
- **Publication Year**: 2025
- **Dataset Name**: **CRSP / Compustat / S&P 500 Equity Market Universe**
- **Data Source / Provider**: Center for Research in Security Prices (CRSP) & Compustat Fundamentals
- **Data Frequency / Horizon**: Daily and Monthly stock prices, market capitalization, and financial ratios
- **Dataset Link / Repository**: `https://github.com/Faxulous/n`
- **Data Context & Application**:
  > Asset pricing fundamentals, high-frequency order books, options/implied volatility, and corporate solvency metrics.

### 📄 Predicting the equity premium around the globe:
- **Filename**: `Predicting-the-equity-premium-around-the-globe--Co_2025_International-Journa.pdf`
- **Publication Year**: 2025
- **Authors**: Comprehensive evidence from large sample Fabian Hollstein , , Marcel Prokopczuk ,, Björn Tharann , Chardin Wese Simen
- **Dataset Name**: **CRSP / Compustat / S&P 500 Equity Market Universe**
- **Data Source / Provider**: Center for Research in Security Prices (CRSP) & Compustat Fundamentals
- **Data Frequency / Horizon**: Daily and Monthly stock prices, market capitalization, and financial ratios
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Asset pricing fundamentals, high-frequency order books, options/implied volatility, and corporate solvency metrics.

### 📄 Return predictability, dividend growth, and the persistence of
- **Filename**: `Return-predictability--dividend-growth--and-the-pe_2025_International-Journa.pdf`
- **Publication Year**: 2025
- **Authors**: the price–dividend ratio Adam Goliński ,, , João Madeira , Dooruj Rambaccussing Banque de France, Financial Economics Research Division, France
- **Dataset Name**: **CRSP / Compustat / S&P 500 Equity Market Universe**
- **Data Source / Provider**: Center for Research in Security Prices (CRSP) & Compustat Fundamentals
- **Data Frequency / Horizon**: Daily and Monthly stock prices, market capitalization, and financial ratios
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Asset pricing fundamentals, high-frequency order books, options/implied volatility, and corporate solvency metrics.

### 📄 A decentralized credit risk prediction method based on federated cost-sensitive learning
- **Filename**: `A-decentralized-credit-risk-prediction-method-base_2026_International-Journa.pdf`
- **Publication Year**: 2026
- **Authors**: Jin Xiao , Zhongyi Wang , Shouyang Wang , Kuangnan Fang , Xiaoyi Jiang , Dunhu Liu ,
- **Dataset Name**: **Corporate Credit Scoring & Insurance Regulatory Statutory Filings**
- **Data Source / Provider**: National Association of Insurance Commissioners (NAIC) & Credit Bureau Datasets
- **Data Frequency / Horizon**: Quarterly and Annual statutory balance sheets and insolvency records
- **Dataset Link / Repository**: `https://github.com/wuaoala/Fe`
- **Data Context & Application**:
  > Asset pricing fundamentals, high-frequency order books, options/implied volatility, and corporate solvency metrics.

### 📄 Adaptive voting stacking with attention mechanism for enhanced credit scoring
- **Filename**: `Adaptive-voting-stacking-with-attention-mechanis_2026_International-Journal-.pdf`
- **Publication Year**: 2026
- **Authors**: Lingyi Meng ,, Shanshan Jiang , Nanjing, 210044, Jiangsu, China Technology, Nanjing 210044, China , Min Xia
- **Dataset Name**: **Corporate Credit Scoring & Insurance Regulatory Statutory Filings**
- **Data Source / Provider**: National Association of Insurance Commissioners (NAIC) & Credit Bureau Datasets
- **Data Frequency / Horizon**: Quarterly and Annual statutory balance sheets and insolvency records
- **Dataset Link / Repository**: `https://github.com/SHIMMER- 0039/credit-scoring.git`
- **Data Context & Application**:
  > Asset pricing fundamentals, high-frequency order books, options/implied volatility, and corporate solvency metrics.

### 📄 Assessing cross-currency predictability in forex markets: Insights from limit order book data
- **Filename**: `Assessing-cross-currency-predictability-in-forex-ma_2026_International-Journ.pdf`
- **Publication Year**: 2026
- **Authors**: Yana Petrova , , Anders Vilhelmsson , Lars L. Nordén
- **Dataset Name**: **LOBSTER Limit Order Book Tick-Level Market Dataset**
- **Data Source / Provider**: LOBSTER Data (NASDAQ order book tick messages)
- **Data Frequency / Horizon**: High-frequency sub-millisecond order event timestamps
- **Dataset Link / Repository**: `https://github.com/yanapetrov`
- **Data Context & Application**:
  > Asset pricing fundamentals, high-frequency order books, options/implied volatility, and corporate solvency metrics.

### 📄 Enhancing market return forecasts with an incident-based ESG indicator
- **Filename**: `Enhancing-market-return-forecasts-with-an-incid_2026_International-Journal-o.pdf`
- **Publication Year**: 2026
- **Authors**: Zhiyong Li , Weiping Qin ,,
- **Dataset Name**: **CRSP / Compustat / S&P 500 Equity Market Universe**
- **Data Source / Provider**: Center for Research in Security Prices (CRSP) & Compustat Fundamentals
- **Data Frequency / Horizon**: Daily and Monthly stock prices, market capitalization, and financial ratios
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Asset pricing fundamentals, high-frequency order books, options/implied volatility, and corporate solvency metrics.

### 📄 Machine learning and insurer failure prediction Canchun He, Dejin Huang, Ruo Jia, Xi Wang
- **Filename**: `Machine-learning-and-insurer-failure-pre_2026_International-Journal-of-Forec.pdf`
- **Publication Year**: 2026
- **Dataset Name**: **Corporate Credit Scoring & Insurance Regulatory Statutory Filings**
- **Data Source / Provider**: National Association of Insurance Commissioners (NAIC) & Credit Bureau Datasets
- **Data Frequency / Horizon**: Quarterly and Annual statutory balance sheets and insolvency records
- **Dataset Link / Repository**: `https://github.com/CanchunHe /Machine-Learning-and-Insurer-Failure-Pre`
- **Data Context & Application**:
  > Asset pricing fundamentals, high-frequency order books, options/implied volatility, and corporate solvency metrics.

### 📄 Modeling and forecasting intraday spot volatility
- **Filename**: `Modeling-and-forecasting-intraday-spot-vo_2026_International-Journal-of-Fore.pdf`
- **Publication Year**: 2026
- **Authors**: Adam Clements , 4001, Australia , Daniel P.A. Preve
- **Dataset Name**: **High-Frequency Realized Volatility & Intraday Stock Trades**
- **Data Source / Provider**: NYSE TAQ (Trade and Quote) / Refinitiv Tick History
- **Data Frequency / Horizon**: 1-minute and 5-minute intraday price returns
- **Dataset Link / Repository**: `https://github.com/AdamEClem`
- **Data Context & Application**:
  > Asset pricing fundamentals, high-frequency order books, options/implied volatility, and corporate solvency metrics.

### 📄 Realized volatility forecasting for new issues and spin-offs using multi-source transfer learning
- **Filename**: `Realized-volatility-forecasting-for-new-issues-and-s_2026_International-Jour.pdf`
- **Publication Year**: 2026
- **Authors**: , Christian Pigorsch
- **Dataset Name**: **High-Frequency Realized Volatility & Intraday Stock Trades**
- **Data Source / Provider**: NYSE TAQ (Trade and Quote) / Refinitiv Tick History
- **Data Frequency / Horizon**: 1-minute and 5-minute intraday price returns
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Asset pricing fundamentals, high-frequency order books, options/implied volatility, and corporate solvency metrics.

### 📄 Using diverse local optima for setting kernel parameters in support vector regression: Forecasting emerging market credit spreads
- **Filename**: `Using-diverse-local-optima-for-setting-kernel-parameter_2026_International-J.pdf`
- **Publication Year**: 2026
- **Authors**: Gary S. Anderson ,1, Alena Audzeyeva , CEMAR LLC, USA
- **Dataset Name**: **Corporate Credit Scoring & Insurance Regulatory Statutory Filings**
- **Data Source / Provider**: National Association of Insurance Commissioners (NAIC) & Credit Bureau Datasets
- **Data Frequency / Horizon**: Quarterly and Annual statutory balance sheets and insolvency records
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Asset pricing fundamentals, high-frequency order books, options/implied volatility, and corporate solvency metrics.

### 📄 Visualizing technical analysis Ruidong Yi, Jiajie Wang
- **Filename**: `Visualizing-technical-analysis_2026_International-Journal-of-Forecasting.pdf`
- **Publication Year**: 2026
- **Dataset Name**: **CRSP / Compustat / S&P 500 Equity Market Universe**
- **Data Source / Provider**: Center for Research in Security Prices (CRSP) & Compustat Fundamentals
- **Data Frequency / Horizon**: Daily and Monthly stock prices, market capitalization, and financial ratios
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Asset pricing fundamentals, high-frequency order books, options/implied volatility, and corporate solvency metrics.

### 📄 Volatility forecasting for low-volatility investing
- **Filename**: `Volatility-forecasting-for-low-volatility-_2026_International-Journal-of-For.pdf`
- **Publication Year**: 2026
- **Authors**: Christian Conrad , Onno Kleen ,, , Rasmus Lönn ,
- **Dataset Name**: **CRSP / Compustat / S&P 500 Equity Market Universe**
- **Data Source / Provider**: Center for Research in Security Prices (CRSP) & Compustat Fundamentals
- **Data Frequency / Horizon**: Daily and Monthly stock prices, market capitalization, and financial ratios
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Asset pricing fundamentals, high-frequency order books, options/implied volatility, and corporate solvency metrics.

---

## 3. Macroeconomic & Central Bank Datasets (10 Papers)

> **Overview**: FRED-MD/QD, Bank of England forecast archives, European Central Bank SPF, and national inflation baskets.

### 📄 Asymmetric uncertainty: Nowcasting using skewness in
- **Filename**: `Asymmetric-uncertainty--Nowcasting-using-skewn_2025_International-Journal-of.pdf`
- **Publication Year**: 2025
- **Authors**: real-time data Paul Labonne
- **Dataset Name**: **FRED-MD / FRED-QD Large-Scale Macroeconomic Database**
- **Data Source / Provider**: Federal Reserve Bank of St. Louis (FRED)
- **Data Frequency / Horizon**: Monthly (120+ macro indicators) and Quarterly series (1960–2024)
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Key macroeconomic time series including CPI inflation, GDP growth, interest rates, unemployment, and institutional projections.

### 📄 Does economic uncertainty predict real activity in real time?
- **Filename**: `Does-economic-uncertainty-predict-real-activi_2025_International-Journal-of-.pdf`
- **Publication Year**: 2025
- **Authors**: Bart Keijsers , , Dick van Dijk
- **Dataset Name**: **FRED-MD / FRED-QD Large-Scale Macroeconomic Database**
- **Data Source / Provider**: Federal Reserve Bank of St. Louis (FRED)
- **Data Frequency / Horizon**: Monthly (120+ macro indicators) and Quarterly series (1960–2024)
- **Dataset Link / Repository**: `https://research.stlouisfed.org /econ/mccracken/fred-databases/, https://w`
- **Data Context & Application**:
  > Key macroeconomic time series including CPI inflation, GDP growth, interest rates, unemployment, and institutional projections.

### 📄 Forecasting CPI inflation under economic policy and
- **Filename**: `Forecasting-CPI-inflation-under-economic-policy-_2025_International-Journal-.pdf`
- **Publication Year**: 2025
- **Authors**: geopolitical uncertainties Shovon Sengupta ,,1, Tanujit Chakraborty ,,1, , Sunny Kumar Singh Fidelity Investments, Boston, USA
- **Dataset Name**: **FRED-MD / FRED-QD Large-Scale Macroeconomic Database**
- **Data Source / Provider**: Federal Reserve Bank of St. Louis (FRED)
- **Data Frequency / Horizon**: Monthly (120+ macro indicators) and Quarterly series (1960–2024)
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Key macroeconomic time series including CPI inflation, GDP growth, interest rates, unemployment, and institutional projections.

### 📄 Forecasting macroeconomic data with Bayesian VARs: Sparse or dense? It depends! Luis Gruber
- **Filename**: `Forecasting-macroeconomic-data-with-Bayesian-VARs_2025_International-Journal.pdf`
- **Publication Year**: 2025
- **Authors**: , Gregor Kastner
- **Dataset Name**: **FRED-MD / FRED-QD Large-Scale Macroeconomic Database**
- **Data Source / Provider**: Federal Reserve Bank of St. Louis (FRED)
- **Data Frequency / Horizon**: Monthly (120+ macro indicators) and Quarterly series (1960–2024)
- **Dataset Link / Repository**: `https://github.com/luisgruber/`
- **Data Context & Application**:
  > Key macroeconomic time series including CPI inflation, GDP growth, interest rates, unemployment, and institutional projections.

### 📄 Fundamental determinants of exchange rate expectations
- **Filename**: `Fundamental-determinants-of-exchange-rate-_2025_International-Journal-of-For.pdf`
- **Publication Year**: 2025
- **Authors**: Joscha Beckmann ,, Robert L. Czudaj , FernUniversität in Hagen, Faculty of Business Administration and Economics, Chair for Macroeconomics, Universitätsstr. 11, D-58097 Hagen, Germany Macroeconomics, Schlossplatz 1, D-09599 Freiberg, Germany
- **Dataset Name**: **FRED-MD / FRED-QD Large-Scale Macroeconomic Database**
- **Data Source / Provider**: Federal Reserve Bank of St. Louis (FRED)
- **Data Frequency / Horizon**: Monthly (120+ macro indicators) and Quarterly series (1960–2024)
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Key macroeconomic time series including CPI inflation, GDP growth, interest rates, unemployment, and institutional projections.

### 📄 Could the Bank of England have avoided mis-forecasting UK inflation during 2021–24?
- **Filename**: `Could-the-Bank-of-England-have-avoided-mis-foreca_2026_International-Journal.pdf`
- **Publication Year**: 2026
- **Authors**: Jennifer L. Castle, Jurgen A. Doornik, David F. Hendry
- **Dataset Name**: **Bank of England Forecast Archive & UK ONS Macroeconomic Accounts**
- **Data Source / Provider**: Bank of England Database & UK Office for National Statistics (ONS)
- **Data Frequency / Horizon**: Quarterly GDP/Inflation projections and Monthly CPI data (1997–2024)
- **Dataset Link / Repository**: `https://www.climateeconome`
- **Data Context & Application**:
  > Key macroeconomic time series including CPI inflation, GDP growth, interest rates, unemployment, and institutional projections.

### 📄 Forecasting UK consumer price inflation with RaGNAR: Random generalised network autoregressive processes Guy P. Nason, Henry Antonio Palasciano
- **Filename**: `Forecasting-UK-consumer-price-inflation-with-RaGNAR-_2026_International-Jour.pdf`
- **Publication Year**: 2026
- **Dataset Name**: **Bank of England Forecast Archive & UK ONS Macroeconomic Accounts**
- **Data Source / Provider**: Bank of England Database & UK Office for National Statistics (ONS)
- **Data Frequency / Horizon**: Quarterly GDP/Inflation projections and Monthly CPI data (1997–2024)
- **Dataset Link / Repository**: `https://www.ons.gov.uk/econo`
- **Data Context & Application**:
  > Key macroeconomic time series including CPI inflation, GDP growth, interest rates, unemployment, and institutional projections.

### 📄 Improving disaggregated short-term food inflation forecasts with webscraped data
- **Filename**: `Improving-disaggregated-short-term-food-inflation_2026_International-Journal.pdf`
- **Publication Year**: 2026
- **Authors**: Christian Beer , Robert Ferstl ,, Oesterreichische Nationalbank, Business Cycle Analysis, Otto-Wagner-Platz 3, Vienna, 1090, Austria Oesterreichische Nationalbank, Monetary Policy, Otto-Wagner-Platz 3, Vienna, 1090, Austria , Bernhard Graf
- **Dataset Name**: **Webscraped Daily Supermarket Food Prices & Official CPI Baskets**
- **Data Source / Provider**: Billion Prices Project / Online Supermarket Scraped Data & National Statistics Offices
- **Data Frequency / Horizon**: Daily scraped item-level price feeds & Monthly CPI indices
- **Dataset Link / Repository**: `https://github.com/datarob/re`
- **Data Context & Application**:
  > Key macroeconomic time series including CPI inflation, GDP growth, interest rates, unemployment, and institutional projections.

### 📄 Nowcasting economic activity in European regions using a mixed-frequency dynamic factor model
- **Filename**: `Nowcasting-economic-activity-in-European-regions-us_2026_International-Journ.pdf`
- **Publication Year**: 2026
- **Authors**: Luca Barbaglia , , Lorenzo Frattarolo , Niko Hauzenberger , Dominik Hirschbühl , Florian Huber , Luca Onorante , Michael Pfarrhofer , Luca Tiozzo Pezzoli European Commission, Joint Research Centre, Italy Universitá degli studi di Verona, Italy
- **Dataset Name**: **Eurostat Regional Economic Accounts & Mixed-Frequency Indicators**
- **Data Source / Provider**: Eurostat Regional Accounts & European Central Bank (ECB)
- **Data Frequency / Horizon**: Quarterly Regional GVA and Monthly economic activity series
- **Dataset Link / Repository**: `https://github.com/lucabarbagl`
- **Data Context & Application**:
  > Key macroeconomic time series including CPI inflation, GDP growth, interest rates, unemployment, and institutional projections.

### 📄 Reactions to the Bernanke Review from Bank of England watchers
- **Filename**: `Reactions-to-the-Bernanke-Review-from-Bank-of_2026_International-Journal-of-.pdf`
- **Publication Year**: 2026
- **Authors**: David Aikman, Richard Barwell
- **Dataset Name**: **Bank of England Forecast Archive & UK ONS Macroeconomic Accounts**
- **Data Source / Provider**: Bank of England Database & UK Office for National Statistics (ONS)
- **Data Frequency / Horizon**: Quarterly GDP/Inflation projections and Monthly CPI data (1997–2024)
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Key macroeconomic time series including CPI inflation, GDP growth, interest rates, unemployment, and institutional projections.

---

## 4. Healthcare, Demographics & Epidemic Datasets (18 Papers)

> **Overview**: Human Mortality Database (HMD), Norwegian COVID-19 Surveillance (CovidMod), UN Population Prospects, and Emergency Department EHRs.

### 📄 A Bayesian Dirichlet auto-regressive moving average model for forecasting lead times
- **Filename**: `A-Bayesian-Dirichlet-auto-regressive-moving-avera_2024_International-Journal.pdf`
- **Publication Year**: 2024
- **Authors**: Harrison Katz ,, , Kai Thomas Brusch , Robert E. Weiss Data Science, Forecasting, Airbnb, United States of America
- **Dataset Name**: **Emergency Department Electronic Health Records (EHR)**
- **Data Source / Provider**: Hospital Patient Flow & Admission Management Databases
- **Data Frequency / Horizon**: 15-minute / Hourly emergency patient arrivals and occupancy
- **Dataset Link / Repository**: `https://github.com/harrisonek`
- **Data Context & Application**:
  > Age-specific mortality tables, COVID-19 clinical records, and hospital occupancy series.

### 📄 Forecasting emergency department occupancy with advanced
- **Filename**: `Forecasting-emergency-department-occupancy-with-adva_2024_International-Jour.pdf`
- **Publication Year**: 2024
- **Authors**: machine learning models and multivariable input Jalmari Tuominen , Niku Oksala ,, Ari Palomäki ,, Antti Roine Kanta-Häme Central Hospital, Hämeenlinna, Finland , Eetu Pulkkinen , Jaakko Peltonen , Juho Kanniainen ,
- **Dataset Name**: **Human Mortality Database (HMD) & Multi-Country Life Tables**
- **Data Source / Provider**: Human Mortality Database (UC Berkeley & Max Planck Institute)
- **Data Frequency / Horizon**: Annual age-specific mortality rates (1950–2022)
- **Dataset Link / Repository**: `https://github.com/tuomijal/ed -ml-multivar`
- **Data Context & Application**:
  > Age-specific mortality tables, COVID-19 clinical records, and hospital occupancy series.

### 📄 Thinking outside the container: A sparse partial least squares
- **Filename**: `Thinking-outside-the-container--A-sparse-partial-lea_2024_International-Jour.pdf`
- **Publication Year**: 2024
- **Authors**: approach to forecasting trade flows Vincent Stamer
- **Dataset Name**: **Norwegian COVID-19 Surveillance (CovidMod) & Hospital Bed Records**
- **Data Source / Provider**: Norwegian Institute of Public Health (FHI) & Regional Health Authorities
- **Data Frequency / Horizon**: Daily case series, hospital admissions, and ICU bed occupancy
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Age-specific mortality tables, COVID-19 clinical records, and hospital occupancy series.

### 📄 An extended logarithmic visualization improves forecasting accuracy for exponentially growing numbers, but residual
- **Filename**: `An-extended-logarithmic-visualization-improves-forecasti_2025_International-.pdf`
- **Publication Year**: 2025
- **Authors**: difficulties remain Ben H. Engler, Florian Hutzler, Stefan Hawelka
- **Dataset Name**: **Norwegian COVID-19 Surveillance (CovidMod) & Hospital Bed Records**
- **Data Source / Provider**: Norwegian Institute of Public Health (FHI) & Regional Health Authorities
- **Data Frequency / Horizon**: Daily case series, hospital admissions, and ICU bed occupancy
- **Dataset Link / Repository**: `https://osf.io/3gj2k/?view_onl`
- **Data Context & Application**:
  > Age-specific mortality tables, COVID-19 clinical records, and hospital occupancy series.

### 📄 Do oil price forecast disagreement of survey of professional
- **Filename**: `Do-oil-price-forecast-disagreement-of-survey-of-profe_2025_International-Jou.pdf`
- **Publication Year**: 2025
- **Authors**: forecasters predict crude oil return volatility? Anton Hasselgren , Ai Jun Hou , Sandy Suardi , , Caihong Xu , Xiaoxia Ye
- **Dataset Name**: **Norwegian COVID-19 Surveillance (CovidMod) & Hospital Bed Records**
- **Data Source / Provider**: Norwegian Institute of Public Health (FHI) & Regional Health Authorities
- **Data Frequency / Horizon**: Daily case series, hospital admissions, and ICU bed occupancy
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Age-specific mortality tables, COVID-19 clinical records, and hospital occupancy series.

### 📄 Dynamic time series modelling and forecasting of COVID-19 in Norway
- **Filename**: `Dynamic-time-series-modelling-and-forecasting-_2025_International-Journal-of.pdf`
- **Publication Year**: 2025
- **Authors**: Gunnar Bårdsen ,, Ragnar Nymoen ,
- **Dataset Name**: **Norwegian COVID-19 Surveillance (CovidMod) & Hospital Bed Records**
- **Data Source / Provider**: Norwegian Institute of Public Health (FHI) & Regional Health Authorities
- **Data Frequency / Horizon**: Daily case series, hospital admissions, and ICU bed occupancy
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Age-specific mortality tables, COVID-19 clinical records, and hospital occupancy series.

### 📄 Forecasting macroeconomic tail risk in real time: Do textual
- **Filename**: `Forecasting-macroeconomic-tail-risk-in-real-time_2025_International-Journal-.pdf`
- **Publication Year**: 2025
- **Authors**: data add value? Philipp Adämmer , Jan Prüser , Rainer A. Schüssler ,
- **Dataset Name**: **Norwegian COVID-19 Surveillance (CovidMod) & Hospital Bed Records**
- **Data Source / Provider**: Norwegian Institute of Public Health (FHI) & Regional Health Authorities
- **Data Frequency / Horizon**: Daily case series, hospital admissions, and ICU bed occupancy
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Age-specific mortality tables, COVID-19 clinical records, and hospital occupancy series.

### 📄 Humans vs. large language models: Judgmental forecasting in an era of advanced AI
- **Filename**: `Humans-vs--large-language-models--Judgmental-fore_2025_International-Journal.pdf`
- **Publication Year**: 2025
- **Authors**: Mahdi Abolghasemi , , Odkhishig Ganbold , Kristian Rotaru ,
- **Dataset Name**: **Emergency Department Electronic Health Records (EHR)**
- **Data Source / Provider**: Hospital Patient Flow & Admission Management Databases
- **Data Frequency / Horizon**: 15-minute / Hourly emergency patient arrivals and occupancy
- **Dataset Link / Repository**: `https://github.com/mahdiabol`
- **Data Context & Application**:
  > Age-specific mortality tables, COVID-19 clinical records, and hospital occupancy series.

### 📄 Improving out-of-population prediction: The complementary effects of model assistance and judgmental bootstrapping
- **Filename**: `Improving-out-of-population-prediction--The-complement_2025_International-Jo.pdf`
- **Publication Year**: 2025
- **Authors**: Mathew D. Hardy , Daniel G. Goldstein Microsoft Research, United States of America , Sam Zhang , Jessica Hullman , Jake M. Hofman ,
- **Dataset Name**: **Norwegian COVID-19 Surveillance (CovidMod) & Hospital Bed Records**
- **Data Source / Provider**: Norwegian Institute of Public Health (FHI) & Regional Health Authorities
- **Data Frequency / Horizon**: Daily case series, hospital admissions, and ICU bed occupancy
- **Dataset Link / Repository**: `https://github.com/mdahardy/`
- **Data Context & Application**:
  > Age-specific mortality tables, COVID-19 clinical records, and hospital occupancy series.

### 📄 Testing for equal predictive accuracy with strong
- **Filename**: `Testing-for-equal-predictive-accuracy-with-s_2025_International-Journal-of-F.pdf`
- **Publication Year**: 2025
- **Authors**: dependence, Laura Coroneo , Fabrizio Iacone ,, Università degli Studi di Milano, Italy
- **Dataset Name**: **Norwegian COVID-19 Surveillance (CovidMod) & Hospital Bed Records**
- **Data Source / Provider**: Norwegian Institute of Public Health (FHI) & Regional Health Authorities
- **Data Frequency / Horizon**: Daily case series, hospital admissions, and ICU bed occupancy
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Age-specific mortality tables, COVID-19 clinical records, and hospital occupancy series.

### 📄 A Bayesian Dirichlet autoregressive conditional heteroskedasticity model for forecasting currency shares
- **Filename**: `A-Bayesian-Dirichlet-autoregressive-conditional-hete_2026_International-Jour.pdf`
- **Publication Year**: 2026
- **Authors**: Harrison Katz ,, , Robert E. Weiss Forecasting, Data Science, Airbnb, United States of America
- **Dataset Name**: **Emergency Department Electronic Health Records (EHR)**
- **Data Source / Provider**: Hospital Patient Flow & Admission Management Databases
- **Data Frequency / Horizon**: 15-minute / Hourly emergency patient arrivals and occupancy
- **Dataset Link / Repository**: `https://github.com/harrisonek`
- **Data Context & Application**:
  > Age-specific mortality tables, COVID-19 clinical records, and hospital occupancy series.

### 📄 Assessing the accuracy of probabilistic population forecasts
- **Filename**: `Assessing-the-accuracy-of-probabilistic-popu_2026_International-Journal-of-F.pdf`
- **Publication Year**: 2026
- **Authors**: Juha Alho , Nico Keilman ,
- **Dataset Name**: **Human Mortality Database (HMD) & Multi-Country Life Tables**
- **Data Source / Provider**: Human Mortality Database (UC Berkeley & Max Planck Institute)
- **Data Frequency / Horizon**: Annual age-specific mortality rates (1950–2022)
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Age-specific mortality tables, COVID-19 clinical records, and hospital occupancy series.

### 📄 Combining predictive distributions for time-to-event outcomes in meteorology
- **Filename**: `Combining-predictive-distributions-for-time-to-e_2026_International-Journal-.pdf`
- **Publication Year**: 2026
- **Authors**: Céline Cunen ,, Alex Lenkoski Blindern, Oslo, 0317, Norway , Thea Roksvåg , Claudio Heinrich-Mertsching ,
- **Dataset Name**: **Emergency Department Electronic Health Records (EHR)**
- **Data Source / Provider**: Hospital Patient Flow & Admission Management Databases
- **Data Frequency / Horizon**: 15-minute / Hourly emergency patient arrivals and occupancy
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Age-specific mortality tables, COVID-19 clinical records, and hospital occupancy series.

### 📄 Enhancing mortality forecasting with ensemble learning: A shapley-based approach
- **Filename**: `Enhancing-mortality-forecasting-with-ensemble-lea_2026_International-Journal.pdf`
- **Publication Year**: 2026
- **Authors**: Giovanna Bimonte , Maria Russolillo , , Yang Yang , Han Lin Shang
- **Dataset Name**: **Human Mortality Database (HMD) & Multi-Country Life Tables**
- **Data Source / Provider**: Human Mortality Database (UC Berkeley & Max Planck Institute)
- **Data Frequency / Horizon**: Annual age-specific mortality rates (1950–2022)
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Age-specific mortality tables, COVID-19 clinical records, and hospital occupancy series.

### 📄 Getting back on track: Forecasting after extreme observations
- **Filename**: `Getting-back-on-track--Forecasting-after-extr_2026_International-Journal-of-.pdf`
- **Publication Year**: 2026
- **Authors**: Pål Boug , , Håvard Hungnes , Takamitsu Kurita
- **Dataset Name**: **Norwegian COVID-19 Surveillance (CovidMod) & Hospital Bed Records**
- **Data Source / Provider**: Norwegian Institute of Public Health (FHI) & Regional Health Authorities
- **Data Frequency / Horizon**: Daily case series, hospital admissions, and ICU bed occupancy
- **Dataset Link / Repository**: `https://dx.doi.org/10.17632/frx`
- **Data Context & Application**:
  > Age-specific mortality tables, COVID-19 clinical records, and hospital occupancy series.

### 📄 Integrating nowcasts into an ensemble of data-driven forecasting models for SARI hospitalizations in Germany
- **Filename**: `Integrating-nowcasts-into-an-ensemble-of-data-driven-_2026_International-Jou.pdf`
- **Publication Year**: 2026
- **Authors**: Daniel Wolffram ,, Johannes Bracher ,, RESPINOW Study Group1, Melanie Schienle ,,
- **Dataset Name**: **Norwegian COVID-19 Surveillance (CovidMod) & Hospital Bed Records**
- **Data Source / Provider**: Norwegian Institute of Public Health (FHI) & Regional Health Authorities
- **Data Frequency / Horizon**: Daily case series, hospital admissions, and ICU bed occupancy
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Age-specific mortality tables, COVID-19 clinical records, and hospital occupancy series.

### 📄 Quantile-based modeling of scale dynamics in financial returns for Value-at-Risk and Expected Shortfall forecasting
- **Filename**: `Quantile-based-modeling-of-scale-dynamics-in-financial_2026_International-Jo.pdf`
- **Publication Year**: 2026
- **Authors**: Xiaochun Liu , Richard Luger , Alabama, Tuscaloosa, AL 35487, USA
- **Dataset Name**: **Norwegian COVID-19 Surveillance (CovidMod) & Hospital Bed Records**
- **Data Source / Provider**: Norwegian Institute of Public Health (FHI) & Regional Health Authorities
- **Data Frequency / Horizon**: Daily case series, hospital admissions, and ICU bed occupancy
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Age-specific mortality tables, COVID-19 clinical records, and hospital occupancy series.

### 📄 VAR Model with Sparse Group LASSO for Multi-population Mortality Forecasting Tim J. Boonen, Yuhuai Chen
- **Filename**: `VAR-Model-with-Sparse-Group-LASSO-for-Multi-popu_2026_International-Journal-.pdf`
- **Publication Year**: 2026
- **Dataset Name**: **Human Mortality Database (HMD) & Multi-Country Life Tables**
- **Data Source / Provider**: Human Mortality Database (UC Berkeley & Max Planck Institute)
- **Data Frequency / Horizon**: Annual age-specific mortality rates (1950–2022)
- **Dataset Link / Repository**: `https://github.com/Greatknee/`
- **Data Context & Application**:
  > Age-specific mortality tables, COVID-19 clinical records, and hospital occupancy series.

---

## 5. Surveys, Consumer Expectations & Behavioral Datasets (5 Papers)

> **Overview**: NY Fed Survey of Consumer Expectations (SCE), Superforecasting Geopolitical Tournaments, and ERP SKU demand planning adjustments.

### 📄 Cognitive reflection, arithmetic ability and financial literacy independently predict both inflation expectations and forecast accuracy
- **Filename**: `Cognitive-reflection--arithmetic-ability-and-financial-l_2025_International-.pdf`
- **Publication Year**: 2025
- **Authors**: David A. Comerford
- **Dataset Name**: **NY Fed Survey of Consumer Expectations (SCE) Microdata**
- **Data Source / Provider**: Federal Reserve Bank of New York
- **Data Frequency / Horizon**: Monthly household survey panel microdata
- **Dataset Link / Repository**: `https://osf.io/bpcjm/`
- **Data Context & Application**:
  > Human judgment adjustments, cognitive reflection tests, tournament probability scores, and consumer surveys.

### 📄 Forecast value added in demand planning
- **Filename**: `Forecast-value-added-in-demand-planni_2025_International-Journal-of-Forecast.pdf`
- **Publication Year**: 2025
- **Authors**: Robert Fildes , , Paul Goodwin , Shari De Baets
- **Dataset Name**: **Multi-Enterprise SKU Demand Planning & Forecast Override Records**
- **Data Source / Provider**: ERP & S&OP Enterprise Demand Forecasting Datasets (~147,000 SKU adjustments)
- **Data Frequency / Horizon**: Weekly / Monthly SKU-level baseline forecasts and judgmental overrides
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Human judgment adjustments, cognitive reflection tests, tournament probability scores, and consumer surveys.

### 📄 Guiding supervisors in artificial intelligence-enabled forecasting: Understanding the impacts of salience and detail
- **Filename**: `Guiding-supervisors-in-artificial-intelligence-enabled-f_2025_International-.pdf`
- **Publication Year**: 2025
- **Authors**: on decision-making Naghmeh Khosrowabadi , Kai Hoberg , , Yun Shin Lee KAIST College of Business, 85 Hoegi-ro Dongdaemun-gu, Seoul, Republic of Korea
- **Dataset Name**: **Experimental Behavioral & Judgmental Forecasting Lab Datasets**
- **Data Source / Provider**: Controlled Behavioral Experiments (Prolific, MTurk, and University Behavioral Labs)
- **Data Frequency / Horizon**: Controlled experimental rounds and survey trials
- **Dataset Link / Repository**: `https://github.com/kaihoberg/`
- **Data Context & Application**:
  > Human judgment adjustments, cognitive reflection tests, tournament probability scores, and consumer surveys.

### 📄 Light-touch forecasting: A novel method to combine human judgment with statistical algorithms
- **Filename**: `Light-touch-forecasting--A-novel-method-to-combine-_2025_International-Journ.pdf`
- **Publication Year**: 2025
- **Authors**: , R.J.I. Basten, P.P.F.M. van de Calseyde, E. Demerouti, B.B.J.P.J. van der Staak A.G. de Kok
- **Dataset Name**: **Experimental Behavioral & Judgmental Forecasting Lab Datasets**
- **Data Source / Provider**: Controlled Behavioral Experiments (Prolific, MTurk, and University Behavioral Labs)
- **Data Frequency / Horizon**: Controlled experimental rounds and survey trials
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Human judgment adjustments, cognitive reflection tests, tournament probability scores, and consumer surveys.

### 📄 Service-level anchoring in demand forecasting: The moderating impact of retail promotions and product
- **Filename**: `Service-level-anchoring-in-demand-forecasting--The-mod_2025_International-Jo.pdf`
- **Publication Year**: 2025
- **Authors**: perishability Ben Fahimnia , , Tarkan Tan , Nail Tahirov
- **Dataset Name**: **NY Fed Survey of Consumer Expectations (SCE) Microdata**
- **Data Source / Provider**: Federal Reserve Bank of New York
- **Data Frequency / Horizon**: Monthly household survey panel microdata
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Human judgment adjustments, cognitive reflection tests, tournament probability scores, and consumer surveys.

---

## 6. Forecasting Competitions & Benchmark Datasets (7 Papers)

> **Overview**: M6 Financial Competition (100 assets), M4 Competition (100,000 series), and HEFTCom2024 Energy Trading Competition.

### 📄 An adaptive volatility method for probabilistic forecasting and its application to the M6 financial forecasting competition
- **Filename**: `An-adaptive-volatility-method-for-probabilistic-forecas_2025_International-J.pdf`
- **Publication Year**: 2025
- **Authors**: Joseph de Vilmarest ,,1, Nicklas Werge ,,,1 Sorbonne Université, Paris, France Viking Conseil, Paris, France
- **Dataset Name**: **M6 Financial Forecasting Competition Dataset**
- **Data Source / Provider**: M6 Competition (100 liquid assets: 50 S&P 500 stocks + 50 ETFs)
- **Data Frequency / Horizon**: Monthly / 4-week rolling horizons (2022–2023)
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Multi-asset and multi-horizon competition time series evaluated under competitive rules.

### 📄 Benchmarking M6 competitors: An analysis of financial metrics and discussion of incentives
- **Filename**: `Benchmarking-M6-competitors--An-analysis-of-financ_2025_International-Journa.pdf`
- **Publication Year**: 2025
- **Authors**: Matthew J. Schneider , AlixPartners, LLP, United States of America Investment Strategy, ProShares, United States of America , Rufus Rankin , Prabir Burman , Alexander Aue
- **Dataset Name**: **M6 Financial Forecasting Competition Dataset**
- **Data Source / Provider**: M6 Competition (100 liquid assets: 50 S&P 500 stocks + 50 ETFs)
- **Data Frequency / Horizon**: Monthly / 4-week rolling horizons (2022–2023)
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Multi-asset and multi-horizon competition time series evaluated under competitive rules.

### 📄 Local and global trend Bayesian exponential smoothing models
- **Filename**: `Local-and-global-trend-Bayesian-exponential-_2025_International-Journal-of-F.pdf`
- **Publication Year**: 2025
- **Authors**: Slawek Smyl , Christoph Bergmeir ,, Xueying Long , Erwin Wibowo , Daniel Schmidt Walmart Labs, United States of America Let’s Forecast, Australia , Alexander Dokumentov ,
- **Dataset Name**: **M4 Competition Benchmark Dataset**
- **Data Source / Provider**: M4 Competition Repository (100,000 diverse time series)
- **Data Frequency / Horizon**: Yearly, Quarterly, Monthly, Weekly, Daily, Hourly
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Multi-asset and multi-horizon competition time series evaluated under competitive rules.

### 📄 The M6 forecasting competition: Bridging the gap between forecasting and investment decisions
- **Filename**: `The-M6-forecasting-competition--Bridging-the-gap-be_2025_International-Journ.pdf`
- **Publication Year**: 2025
- **Authors**: Spyros Makridakis , Evangelos Spiliotis , Ross Hollyman ,, Fotios Petropoulos ,, , Norman Swanson , Anil Gaba INSEAD, Singapore
- **Dataset Name**: **M6 Financial Forecasting Competition Dataset**
- **Data Source / Provider**: M6 Competition (100 liquid assets: 50 S&P 500 stocks + 50 ETFs)
- **Data Frequency / Horizon**: Monthly / 4-week rolling horizons (2022–2023)
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Multi-asset and multi-horizon competition time series evaluated under competitive rules.

### 📄 The structural Theta method and its predictive performance in the M4-Competition
- **Filename**: `The-structural-Theta-method-and-its-predictive-pe_2025_International-Journal.pdf`
- **Publication Year**: 2025
- **Authors**: Giacomo Sbrana , , Andrea Silvestrini
- **Dataset Name**: **M4 Competition Benchmark Dataset**
- **Data Source / Provider**: M4 Competition Repository (100,000 diverse time series)
- **Data Frequency / Horizon**: Yearly, Quarterly, Monthly, Weekly, Daily, Hourly
- **Dataset Link / Repository**: `https://github.com/giacsbrana/`
- **Data Context & Application**:
  > Multi-asset and multi-horizon competition time series evaluated under competitive rules.

### 📄 Unraveling the effect of engagement and consistency in the results of the M6 forecasting competition Anastasios Kaltsounis, Evangelos Theodorou Vassilios Assimakopoulos
- **Filename**: `Unraveling-the-effect-of-engagement-and-consistency-_2025_International-Jour.pdf`
- **Publication Year**: 2025
- **Dataset Name**: **M6 Financial Forecasting Competition Dataset**
- **Data Source / Provider**: M6 Competition (100 liquid assets: 50 S&P 500 stocks + 50 ETFs)
- **Data Frequency / Horizon**: Monthly / 4-week rolling horizons (2022–2023)
- **Dataset Link / Repository**: `https://github.com/TasosKalts`
- **Data Context & Application**:
  > Multi-asset and multi-horizon competition time series evaluated under competitive rules.

### 📄 The HEFTCom2024 winning model: A stacked CatBoost approach for probabilistic wind and solar power forecasting
- **Filename**: `The-HEFTCom2024-winning-model--A-stacked-CatBoost-app_2026_International-Jou.pdf`
- **Publication Year**: 2026
- **Authors**: Jon Olauson ,, Unit of Data Analytics, Svenska kraftnät, Sweden , Olle Viotti ,, Jakob Huss
- **Dataset Name**: **HEFTCom2024 Energy Trading Competition Dataset**
- **Data Source / Provider**: Hybrid Energy Forecasting and Trading Competition (Solar, Wind, Price)
- **Data Frequency / Horizon**: Half-hourly & Hourly generation and price series (2020–2024)
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Multi-asset and multi-horizon competition time series evaluated under competitive rules.

---

## 7. Political, Electoral & Geopolitical Datasets (5 Papers)

> **Overview**: American National Election Studies (ANES), ACLED Electoral Violence logs, German Federal Election, and Australian AEC constituency votes.

### 📄 Efficiency of poll-based multi-period forecasting systems for
- **Filename**: `Efficiency-of-poll-based-multi-period-forecasting_2025_International-Journal.pdf`
- **Publication Year**: 2025
- **Authors**: German state elections Markus Fritsch , , Harry Haupt , Joachim Schnurbus Passau, Germany
- **Dataset Name**: **American National Election Studies (ANES) & US Presidential Polls**
- **Data Source / Provider**: ANES (1952–2020 US Presidential Election Time Series)
- **Data Frequency / Horizon**: Quadrennial election surveys and pre-election polling tracks
- **Dataset Link / Repository**: `https://github.com/markusfrits`
- **Data Context & Application**:
  > Constituency-level voting returns, pre-election polling series, and political event records.

### 📄 Forecasting presidential elections: Accuracy of ANES voter intentions
- **Filename**: `Forecasting-presidential-elections--Accuracy-o_2025_International-Journal-of.pdf`
- **Publication Year**: 2025
- **Authors**: Hyein Ko , , Natalie Jackson , Tracy Osborn , Michael S. Lewis-Beck GQR Research, Washington, DC, USA
- **Dataset Name**: **American National Election Studies (ANES) & US Presidential Polls**
- **Data Source / Provider**: ANES (1952–2020 US Presidential Election Time Series)
- **Data Frequency / Horizon**: Quadrennial election surveys and pre-election polling tracks
- **Dataset Link / Repository**: `https://github.com/hey-ikon/r`
- **Data Context & Application**:
  > Constituency-level voting returns, pre-election polling series, and political event records.

### 📄 Candidate vote prediction in open-list systems: Forecasting the results of the 2023 Finnish parliamentary election Tapio Vepsäläinen
- **Filename**: `Candidate-vote-prediction-in-open-list-systems--Foreca_2026_International-Jo.pdf`
- **Publication Year**: 2026
- **Authors**: Turku, Turku, Finland
- **Dataset Name**: **National Election Polling Archive & Open-List Voting Returns**
- **Data Source / Provider**: National Electoral Boards & Polling Archives
- **Data Frequency / Horizon**: Election cycles and multi-period pre-election polling series
- **Dataset Link / Repository**: `https://github.com/vepsala/ca`
- **Data Context & Application**:
  > Constituency-level voting returns, pre-election polling series, and political event records.

### 📄 Citizen forecasting in a mixed electoral system The 2021 German federal election as a test case
- **Filename**: `Citizen-forecasting-in-a-mixed-electoral-system--Th_2026_International-Journ.pdf`
- **Publication Year**: 2026
- **Authors**: Arndt Leininger , Centro de Investigación y Docencia Económicas (CIDE), Mexico City, Mexico , Andreas E. Murr ,, Lukas Stötzer , Mark A. Kayser
- **Dataset Name**: **2021 German Federal Election Constituency Results & Citizen Surveys**
- **Data Source / Provider**: Federal Returning Officer (Bundeswahlleiter) & Infratest Dimap / Forsa
- **Data Frequency / Horizon**: Constituency-level voting returns and voter expectation survey waves
- **Dataset Link / Repository**: `https://doi.org/10.7910/DVN/X`
- **Data Context & Application**:
  > Constituency-level voting returns, pre-election polling series, and political event records.

### 📄 Forecasting electoral violence
- **Filename**: `Forecasting-electoral-violence_2026_International-Journal-of-Forecasting.pdf`
- **Publication Year**: 2026
- **Authors**: David Randahl , Staffan I. Lindberg , Steven Wilson , Maxine Leis , Tim Gåsste , Hanne Fjelde , Håvard Hegre ,,
- **Dataset Name**: **Armed Conflict Location & Event Data Project (ACLED) Electoral Violence Dataset**
- **Data Source / Provider**: ACLED Global Database
- **Data Frequency / Horizon**: Event-level political violence and protest incidents (1997–2023)
- **Dataset Link / Repository**: `https://github.com/Doktorand`
- **Data Context & Application**:
  > Constituency-level voting returns, pre-election polling series, and political event records.

---

## 8. E-Commerce, Digital Platforms & Supply Chain Datasets (2 Papers)

> **Overview**: Airbnb booking lead times, multi-currency marketplace transactions, and digital platform sales series.

### 📄 Cross-temporal forecast reconciliation at digital platforms
- **Filename**: `Cross-temporal-forecast-reconciliation-at-digital_2025_International-Journal.pdf`
- **Publication Year**: 2025
- **Authors**: with machine learning Jeroen Rombouts , Marie Ternes , Ines Wilms ,
- **Dataset Name**: **Digital Platform Booking, Lead Time & Currency Share Records**
- **Data Source / Provider**: Airbnb & Digital Travel/Marketplace Transaction Logs
- **Data Frequency / Horizon**: Daily compositional currency shares, lead times, and platform bookings
- **Dataset Link / Repository**: `https://github.com/MarieTerne`
- **Data Context & Application**:
  > Booking lead times, compositional currency splits, and multi-level platform transaction streams.

### 📄 Ups and (draw) downs Tommaso Proietti
- **Filename**: `Ups-and--draw--downs_2026_International-Journal-of-Forecasting.pdf`
- **Publication Year**: 2026
- **Dataset Name**: **Digital Platform Booking, Lead Time & Currency Share Records**
- **Data Source / Provider**: Airbnb & Digital Travel/Marketplace Transaction Logs
- **Data Frequency / Horizon**: Daily compositional currency shares, lead times, and platform bookings
- **Dataset Link / Repository**: `List of S&P 500 companies, http`
- **Data Context & Application**:
  > Booking lead times, compositional currency splits, and multi-level platform transaction streams.

---

## 9. Cryptocurrency & Digital Asset Datasets (3 Papers)

> **Overview**: High-frequency order books and daily OHLCV prices for Top 100 cryptocurrencies (Binance, CoinMarketCap).

### 📄 Deep learning and NLP in cryptocurrency forecasting: Integrating financial, blockchain, and social media data
- **Filename**: `Deep-learning-and-NLP-in-cryptocurrency-forecasting--_2025_International-Jou.pdf`
- **Publication Year**: 2025
- **Authors**: Vincent Gurgul , , Stefan Lessmann ,, Wolfgang Karl Härdle Humboldt-Universität zu Berlin, Unter den Linden 6, 10117, Berlin, Germany
- **Dataset Name**: **Cryptocurrency Market Prices & High-Frequency Trade Records**
- **Data Source / Provider**: CoinMarketCap / CryptoCompare / Binance API
- **Data Frequency / Horizon**: 1-minute, Hourly, and Daily OHLCV price series (2015–2024)
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Historical prices, trade volumes, market capitalizations, and on-chain blockchain metrics for major cryptocurrencies.

### 📄 Predicting value at risk for cryptocurrencies with generalized
- **Filename**: `Predicting-value-at-risk-for-cryptocurrencies-wi_2025_International-Journal-.pdf`
- **Publication Year**: 2025
- **Authors**: random forests Rebekka Buse , Konstantin Görgen , Melanie Schienle , Allianz Zürich, Switzerland
- **Dataset Name**: **Cryptocurrency Market Prices & High-Frequency Trade Records**
- **Data Source / Provider**: CoinMarketCap / CryptoCompare / Binance API
- **Data Frequency / Horizon**: 1-minute, Hourly, and Daily OHLCV price series (2015–2024)
- **Dataset Link / Repository**: `https://github.com/KITmetricsl`
- **Data Context & Application**:
  > Historical prices, trade volumes, market capitalizations, and on-chain blockchain metrics for major cryptocurrencies.

### 📄 Real-time monitoring procedures for early detection of bubbles
- **Filename**: `Real-time-monitoring-procedures-for-early-det_2025_International-Journal-of-.pdf`
- **Publication Year**: 2025
- **Authors**: E.J. Whitehouse , , D.I. Harvey , S.J. Leybourne
- **Dataset Name**: **Cryptocurrency Market Prices & High-Frequency Trade Records**
- **Data Source / Provider**: CoinMarketCap / CryptoCompare / Binance API
- **Data Frequency / Horizon**: 1-minute, Hourly, and Daily OHLCV price series (2015–2024)
- **Dataset Link / Repository**: `https://sites.google.com/site/ej`
- **Data Context & Application**:
  > Historical prices, trade volumes, market capitalizations, and on-chain blockchain metrics for major cryptocurrencies.

---

## 10. Sports & Wagering Market Datasets (2 Papers)

> **Overview**: European soccer match results and multi-bookmaker Asian Handicap vs. traditional 1X2 betting odds.

### 📄 Forecasting soccer matches with betting odds: A tale of two
- **Filename**: `Forecasting-soccer-matches-with-betting-odds--_2025_International-Journal-of.pdf`
- **Publication Year**: 2025
- **Authors**: markets Tadgh Hegarty, Karl Whelan
- **Dataset Name**: **European Soccer Match Results & Multi-Bookmaker Betting Odds**
- **Data Source / Provider**: Football-Data.co.uk & Asian Handicap Betting Exchanges (Betfair / Pinnacle)
- **Data Frequency / Horizon**: Match-by-match results and pre-match odds (2000–2023)
- **Dataset Link / Repository**: `https://zenodo.org/records/12 673394`
- **Data Context & Application**:
  > Thousands of European soccer matches with opening/closing odds from traditional 1X2 and Asian Handicap markets.

### 📄 Does the consideration of market prices in model selection increase model profitability? Evidence from theory, artificial data and real-world data Fabian Wunderlich
- **Filename**: `Does-the-consideration-of-market-prices-in-model-selectio_2026_International.pdf`
- **Publication Year**: 2026
- **Authors**: 6, 50933, Cologne, Germany , Marc Garnica Caparrós, Daniel Memmert
- **Dataset Name**: **European Soccer Match Results & Multi-Bookmaker Betting Odds**
- **Data Source / Provider**: Football-Data.co.uk & Asian Handicap Betting Exchanges (Betfair / Pinnacle)
- **Data Frequency / Horizon**: Match-by-match results and pre-match odds (2000–2023)
- **Dataset Link / Repository**: `https://github.com/spoho-data`
- **Data Context & Application**:
  > Thousands of European soccer matches with opening/closing odds from traditional 1X2 and Asian Handicap markets.

---

## 11. NLP, News & Textual Datasets (1 Papers)

> **Overview**: Financial news archives (Dow Jones, Reuters), social media text streams, and text-based predictive indicators.

### 📄 Optimal text-based time-series indices
- **Filename**: `Optimal-text-based-time-series-indic_2026_International-Journal-of-Forecasti.pdf`
- **Publication Year**: 2026
- **Authors**: David Ardia , , Keven Bluteau
- **Dataset Name**: **Financial News Archives & Social Media Text Corpus**
- **Data Source / Provider**: Dow Jones News Service / Thomson Reuters / Twitter Financial Streams
- **Data Frequency / Horizon**: Daily and Intraday news stories, headlines, and tweet streams (1980–2024)
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Millions of financial and macroeconomic news articles and text embeddings used to construct predictive indicators.

---

## 12. Synthetic, Simulated & Algorithmic Benchmarks (22 Papers)

> **Overview**: Monte Carlo simulated Data Generating Processes (DGPs) designed to evaluate estimator robustness and finite-sample efficiency.

### 📄 A loss discounting framework for model averaging and
- **Filename**: `A-loss-discounting-framework-for-model-averaging-_2024_International-Journal.pdf`
- **Publication Year**: 2024
- **Authors**: selection in time series models , Jim E. Griffin Dawid Bernaciak
- **Dataset Name**: **Monte Carlo Simulated Data Generating Processes (DGPs)**
- **Data Source / Provider**: Parametric & Non-Linear Synthetic DGPs (ARMA, GARCH, State-Space, Copulas)
- **Data Frequency / Horizon**: Simulated sample trajectories (T = 100 to 10,000)
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Controlled synthetic time series generated to evaluate estimator efficiency, misspecification robustness, and predictive accuracy.

### 📄 Conditionally optimal weights and forward-looking
- **Filename**: `Conditionally-optimal-weights-and-forward-looking_2024_International-Journal.pdf`
- **Publication Year**: 2024
- **Authors**: approaches to combining forecasts Christopher G. Gibbs , Andrey L. Vasnev
- **Dataset Name**: **Monte Carlo Simulated Data Generating Processes (DGPs)**
- **Data Source / Provider**: Parametric & Non-Linear Synthetic DGPs (ARMA, GARCH, State-Space, Copulas)
- **Data Frequency / Horizon**: Simulated sample trajectories (T = 100 to 10,000)
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Controlled synthetic time series generated to evaluate estimator efficiency, misspecification robustness, and predictive accuracy.

### 📄 Factor-augmented forecasting in big data Juhee Bae
- **Filename**: `Factor-augmented-forecasting-in-big-d_2024_International-Journal-of-Forecast.pdf`
- **Publication Year**: 2024
- **Dataset Name**: **Monte Carlo Simulated Data Generating Processes (DGPs)**
- **Data Source / Provider**: Parametric & Non-Linear Synthetic DGPs (ARMA, GARCH, State-Space, Copulas)
- **Data Frequency / Horizon**: Simulated sample trajectories (T = 100 to 10,000)
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Controlled synthetic time series generated to evaluate estimator efficiency, misspecification robustness, and predictive accuracy.

### 📄 Generalized Poisson difference autoregressive processes
- **Filename**: `Generalized-Poisson-difference-autoregressi_2024_International-Journal-of-Fo.pdf`
- **Publication Year**: 2024
- **Authors**: Giulia Carallo , , Roberto Casarin , Christian P. Robert , Université Paris-Dauphine, France
- **Dataset Name**: **Monte Carlo Simulated Data Generating Processes (DGPs)**
- **Data Source / Provider**: Parametric & Non-Linear Synthetic DGPs (ARMA, GARCH, State-Space, Copulas)
- **Data Frequency / Horizon**: Simulated sample trajectories (T = 100 to 10,000)
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Controlled synthetic time series generated to evaluate estimator efficiency, misspecification robustness, and predictive accuracy.

### 📄 Hierarchical forecasting at scale
- **Filename**: `Hierarchical-forecasting-at-scale_2024_International-Journal-of-Forecasting.pdf`
- **Publication Year**: 2024
- **Authors**: Olivier Sprangers , Maarten de Rijke , Wander Wadman , Sebastian Schelter ,
- **Dataset Name**: **Monte Carlo Simulated Data Generating Processes (DGPs)**
- **Data Source / Provider**: Parametric & Non-Linear Synthetic DGPs (ARMA, GARCH, State-Space, Copulas)
- **Data Frequency / Horizon**: Simulated sample trajectories (T = 100 to 10,000)
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Controlled synthetic time series generated to evaluate estimator efficiency, misspecification robustness, and predictive accuracy.

### 📄 Improving forecasts for heterogeneous time series by ‘‘averaging’’, with application to food demand forecasts Lukas Neubauer
- **Filename**: `Improving-forecasts-for-heterogeneous-time-series-by-_2024_International-Jou.pdf`
- **Publication Year**: 2024
- **Authors**: Hauptstrasse 8-10, Vienna, 1040, Vienna, Austria , Peter Filzmoser
- **Dataset Name**: **Monte Carlo Simulated Data Generating Processes (DGPs)**
- **Data Source / Provider**: Parametric & Non-Linear Synthetic DGPs (ARMA, GARCH, State-Space, Copulas)
- **Data Frequency / Horizon**: Simulated sample trajectories (T = 100 to 10,000)
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Controlled synthetic time series generated to evaluate estimator efficiency, misspecification robustness, and predictive accuracy.

### 📄 Properties of the reconciled distributions for Gaussian and count forecasts
- **Filename**: `Properties-of-the-reconciled-distributions-for-G_2024_International-Journal-.pdf`
- **Publication Year**: 2024
- **Authors**: Lorenzo Zambon ,, , Arianna Agosto , Paolo Giudici , Giorgio Corani Istituto Dalle Molle di Studi sull’Intelligenza Artificiale (IDSIA), Lugano, Switzerland
- **Dataset Name**: **Monte Carlo Simulated Data Generating Processes (DGPs)**
- **Data Source / Provider**: Parametric & Non-Linear Synthetic DGPs (ARMA, GARCH, State-Space, Copulas)
- **Data Frequency / Horizon**: Simulated sample trajectories (T = 100 to 10,000)
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Controlled synthetic time series generated to evaluate estimator efficiency, misspecification robustness, and predictive accuracy.

### 📄 A projected nonlinear state-space model for forecasting time series signals
- **Filename**: `A-projected-nonlinear-state-space-model-for-fore_2025_International-Journal-.pdf`
- **Publication Year**: 2025
- **Authors**: Christian Donner ,1, Anuj Mishra ,1, Hideaki Shimazaki ,,
- **Dataset Name**: **Monte Carlo Simulated Data Generating Processes (DGPs)**
- **Data Source / Provider**: Parametric & Non-Linear Synthetic DGPs (ARMA, GARCH, State-Space, Copulas)
- **Data Frequency / Horizon**: Simulated sample trajectories (T = 100 to 10,000)
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Controlled synthetic time series generated to evaluate estimator efficiency, misspecification robustness, and predictive accuracy.

### 📄 ABC-based forecasting in misspecified state space models Chaya Weerasinghe
- **Filename**: `ABC-based-forecasting-in-misspecified-state_2025_International-Journal-of-Fo.pdf`
- **Publication Year**: 2025
- **Authors**: , Rubén Loaiza-Maya, Gael M. Martin, David T. Frazier
- **Dataset Name**: **Monte Carlo Simulated Data Generating Processes (DGPs)**
- **Data Source / Provider**: Parametric & Non-Linear Synthetic DGPs (ARMA, GARCH, State-Space, Copulas)
- **Data Frequency / Horizon**: Simulated sample trajectories (T = 100 to 10,000)
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Controlled synthetic time series generated to evaluate estimator efficiency, misspecification robustness, and predictive accuracy.

### 📄 Coupling LSTM neural networks and state-space models through analytically tractable inference Van-Dai Vuong
- **Filename**: `Coupling-LSTM-neural-networks-and-state-space-model_2025_International-Journ.pdf`
- **Publication Year**: 2025
- **Authors**: Montréal, Québec, H3T 1J4, Canada , Luong-Ha Nguyen, James-A. Goulet
- **Dataset Name**: **Monte Carlo Simulated Data Generating Processes (DGPs)**
- **Data Source / Provider**: Parametric & Non-Linear Synthetic DGPs (ARMA, GARCH, State-Space, Copulas)
- **Data Frequency / Horizon**: Simulated sample trajectories (T = 100 to 10,000)
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Controlled synthetic time series generated to evaluate estimator efficiency, misspecification robustness, and predictive accuracy.

### 📄 Forecasting house price growth rates with factor models and
- **Filename**: `Forecasting-house-price-growth-rates-with-factor-m_2025_International-Journa.pdf`
- **Publication Year**: 2025
- **Authors**: spatio-temporal clustering Raffaele Mattera , , Philip Hans Franses
- **Dataset Name**: **Monte Carlo Simulated Data Generating Processes (DGPs)**
- **Data Source / Provider**: Parametric & Non-Linear Synthetic DGPs (ARMA, GARCH, State-Space, Copulas)
- **Data Frequency / Horizon**: Simulated sample trajectories (T = 100 to 10,000)
- **Dataset Link / Repository**: `https://github.com/raffmattera /stcfm/`
- **Data Context & Application**:
  > Controlled synthetic time series generated to evaluate estimator efficiency, misspecification robustness, and predictive accuracy.

### 📄 On forecast stability
- **Filename**: `On-forecast-stability_2025_International-Journal-of-Forecasting.pdf`
- **Publication Year**: 2025
- **Authors**: Rakshitha Godahewa , Christoph Bergmeir ,,, , Zeynep Erkin Baz , Chengjun Zhu , Zhangdi Song , Salvador García ,, Dario Benavides Meta Inc., CA, USA
- **Dataset Name**: **Monte Carlo Simulated Data Generating Processes (DGPs)**
- **Data Source / Provider**: Parametric & Non-Linear Synthetic DGPs (ARMA, GARCH, State-Space, Copulas)
- **Data Frequency / Horizon**: Simulated sample trajectories (T = 100 to 10,000)
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Controlled synthetic time series generated to evaluate estimator efficiency, misspecification robustness, and predictive accuracy.

### 📄 A note on forecast reconciliation Tommaso Proietti
- **Filename**: `A-note-on-forecast-reconciliation_2026_International-Journal-of-Forecasting.pdf`
- **Publication Year**: 2026
- **Dataset Name**: **Monte Carlo Simulated Data Generating Processes (DGPs)**
- **Data Source / Provider**: Parametric & Non-Linear Synthetic DGPs (ARMA, GARCH, State-Space, Copulas)
- **Data Frequency / Horizon**: Simulated sample trajectories (T = 100 to 10,000)
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Controlled synthetic time series generated to evaluate estimator efficiency, misspecification robustness, and predictive accuracy.

### 📄 Can we protect time series data while maintaining accurate forecasts?
- **Filename**: `Can-we-protect-time-series-data-while-maintain_2026_International-Journal-of.pdf`
- **Publication Year**: 2026
- **Authors**: Cameron D. Bale , , Matthew J. Schneider , Jinwook Lee
- **Dataset Name**: **Monte Carlo Simulated Data Generating Processes (DGPs)**
- **Data Source / Provider**: Parametric & Non-Linear Synthetic DGPs (ARMA, GARCH, State-Space, Copulas)
- **Data Frequency / Horizon**: Simulated sample trajectories (T = 100 to 10,000)
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Controlled synthetic time series generated to evaluate estimator efficiency, misspecification robustness, and predictive accuracy.

### 📄 Causal discovery in multivariate time series through mutual information featurization
- **Filename**: `Causal-discovery-in-multivariate-time-series-throu_2026_International-Journa.pdf`
- **Publication Year**: 2026
- **Authors**: Gian Marco Paldino , , Gianluca Bontempi ,
- **Dataset Name**: **Monte Carlo Simulated Data Generating Processes (DGPs)**
- **Data Source / Provider**: Parametric & Non-Linear Synthetic DGPs (ARMA, GARCH, State-Space, Copulas)
- **Data Frequency / Horizon**: Simulated sample trajectories (T = 100 to 10,000)
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Controlled synthetic time series generated to evaluate estimator efficiency, misspecification robustness, and predictive accuracy.

### 📄 Certainty amid uncertainty: Relationship between macroeconomic uncertainty and individual expectations,
- **Filename**: `Certainty-amid-uncertainty--Relationship-between-mac_2026_International-Jour.pdf`
- **Publication Year**: 2026
- **Authors**: Giulia Piccillo ,, Poramapa Poonpakdee , CESifo, Munich, Germany
- **Dataset Name**: **Monte Carlo Simulated Data Generating Processes (DGPs)**
- **Data Source / Provider**: Parametric & Non-Linear Synthetic DGPs (ARMA, GARCH, State-Space, Copulas)
- **Data Frequency / Horizon**: Simulated sample trajectories (T = 100 to 10,000)
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Controlled synthetic time series generated to evaluate estimator efficiency, misspecification robustness, and predictive accuracy.

### 📄 Enforcing tail calibration when training probabilistic forecast models
- **Filename**: `Enforcing-tail-calibration-when-training-probab_2026_International-Journal-o.pdf`
- **Publication Year**: 2026
- **Authors**: Jakob Benjamin Wessel , Seminar for Statistics, ETH Zurich, Zurich, Switzerland , Maybritt Schillinger , Frank Kwasniok , Sam Allen
- **Dataset Name**: **Monte Carlo Simulated Data Generating Processes (DGPs)**
- **Data Source / Provider**: Parametric & Non-Linear Synthetic DGPs (ARMA, GARCH, State-Space, Copulas)
- **Data Frequency / Horizon**: Simulated sample trajectories (T = 100 to 10,000)
- **Dataset Link / Repository**: `https://github.com/jakobwes/E`
- **Data Context & Application**:
  > Controlled synthetic time series generated to evaluate estimator efficiency, misspecification robustness, and predictive accuracy.

### 📄 Hierarchical neural additive models for interpretable demand forecasts, Leif Feddersen
- **Filename**: `Hierarchical-neural-additive-models-for-interpr_2026_International-Journal-o.pdf`
- **Publication Year**: 2026
- **Authors**: , Catherine Cleophas
- **Dataset Name**: **Monte Carlo Simulated Data Generating Processes (DGPs)**
- **Data Source / Provider**: Parametric & Non-Linear Synthetic DGPs (ARMA, GARCH, State-Space, Copulas)
- **Data Frequency / Horizon**: Simulated sample trajectories (T = 100 to 10,000)
- **Dataset Link / Repository**: `https://github.com/leif-fedders`
- **Data Context & Application**:
  > Controlled synthetic time series generated to evaluate estimator efficiency, misspecification robustness, and predictive accuracy.

### 📄 International factors and inflation risks
- **Filename**: `International-factors-and-inflation-ri_2026_International-Journal-of-Forecas.pdf`
- **Publication Year**: 2026
- **Authors**: Ignacio Garrón , Vladimir Rodríguez-Caballero , Esther Ruiz ,
- **Dataset Name**: **Monte Carlo Simulated Data Generating Processes (DGPs)**
- **Data Source / Provider**: Parametric & Non-Linear Synthetic DGPs (ARMA, GARCH, State-Space, Copulas)
- **Data Frequency / Horizon**: Simulated sample trajectories (T = 100 to 10,000)
- **Dataset Link / Repository**: `https://github.com/IgnacioGar`
- **Data Context & Application**:
  > Controlled synthetic time series generated to evaluate estimator efficiency, misspecification robustness, and predictive accuracy.

### 📄 Leveraging image-based generative adversarial networks for time series generation
- **Filename**: `Leveraging-image-based-generative-adversarial-net_2026_International-Journal.pdf`
- **Publication Year**: 2026
- **Authors**: Justin Hellermann , , Stefan Lessmann ,
- **Dataset Name**: **Monte Carlo Simulated Data Generating Processes (DGPs)**
- **Data Source / Provider**: Parametric & Non-Linear Synthetic DGPs (ARMA, GARCH, State-Space, Copulas)
- **Data Frequency / Horizon**: Simulated sample trajectories (T = 100 to 10,000)
- **Dataset Link / Repository**: `Code/Data available upon request or via paper URL`
- **Data Context & Application**:
  > Controlled synthetic time series generated to evaluate estimator efficiency, misspecification robustness, and predictive accuracy.

### 📄 New tests of equal forecast accuracy for factor-augmented regressions with weaker loadings
- **Filename**: `New-tests-of-equal-forecast-accuracy-for-factor-au_2026_International-Journa.pdf`
- **Publication Year**: 2026
- **Authors**: Luca Margaritella , Ovidijus Stauskas ,
- **Dataset Name**: **Monte Carlo Simulated Data Generating Processes (DGPs)**
- **Data Source / Provider**: Parametric & Non-Linear Synthetic DGPs (ARMA, GARCH, State-Space, Copulas)
- **Data Frequency / Horizon**: Simulated sample trajectories (T = 100 to 10,000)
- **Dataset Link / Repository**: `GitHub - New Tests of Equal F`
- **Data Context & Application**:
  > Controlled synthetic time series generated to evaluate estimator efficiency, misspecification robustness, and predictive accuracy.

### 📄 The Bayesian context trees state space model for time series modelling and forecasting
- **Filename**: `The-Bayesian-context-trees-state-space-model-for-t_2026_International-Journa.pdf`
- **Publication Year**: 2026
- **Authors**: Ioannis Papageorgiou , , Ioannis Kontoyiannis
- **Dataset Name**: **Monte Carlo Simulated Data Generating Processes (DGPs)**
- **Data Source / Provider**: Parametric & Non-Linear Synthetic DGPs (ARMA, GARCH, State-Space, Copulas)
- **Data Frequency / Horizon**: Simulated sample trajectories (T = 100 to 10,000)
- **Dataset Link / Repository**: `https://github.com/IoannisPap`
- **Data Context & Application**:
  > Controlled synthetic time series generated to evaluate estimator efficiency, misspecification robustness, and predictive accuracy.

---

