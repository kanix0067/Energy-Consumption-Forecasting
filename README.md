# ⚡ EnerVision AI — Energy Intelligence Platform

> **A data-driven Streamlit application for energy consumption analysis, predictive forecasting, and actionable sustainability optimization across residential and commercial facilities.**

---

## 📌 Project Overview

**EnerVision AI** is an end-to-end energy intelligence dashboard built with Python and Streamlit. It enables facility managers, households, and organizations to upload their electricity consumption data and instantly receive deep analytical insights, demand forecasts, appliance-level breakdowns, and tailored cost-reduction strategies — all within an elegant, dark-themed UI.

The platform is designed to be facility-agnostic, supporting households, offices, schools/universities, and manufacturing plants with dynamic, context-aware analysis.

---

## 🚀 Key Features

| Feature | Description |
|---|---|
| **Operational Overview** | KPI dashboard showing total consumption, average daily usage, estimated cost (₹), and carbon footprint |
| **Consumption Profiler** | Hourly, weekly, and appliance-level energy breakdown with interactive Plotly charts |
| **Intelligence Forecasting** | Seasonal time-series forecasting (1 Day / 1 Week / 1 Month / 1 Year) with confidence intervals |
| **Optimization Blueprint** | What-if simulation sandbox for modeling savings goals and generating actionable efficiency recommendations |
| **Facility Configuration** | Dynamic appliance disaggregation tailored to building type (Household, Office, School, Manufacturing Plant) |
| **Cost Modelling** | Configurable per-unit electricity rate (₹/kWh) applied across all financial projections |

---

## 🗂️ Repository Structure

```
Energy-Consumption-Forecasting/
│
├── app.py                  # Main Streamlit application — routing, UI, page logic
├── analytics_engine.py     # Data ingestion, validation, feature engineering & pattern extraction
├── models_engine.py        # Seasonal forecasting engine with confidence intervals
└── config.py               # UIConfig class — dark theme tokens, KPI card renderer, CSS injection
```

### Module Responsibilities

**`app.py`** — The application entry point. Handles file uploads, session state management, sidebar navigation, and renders all four dashboard pages using components from the other modules.

**`analytics_engine.py`** — Contains the `AnalyticsEngine` class with three static methods:
- `validate_and_parse()` — Flexible CSV ingestion with case-insensitive column detection, automatic datetime parsing (including separate Date/Time columns), missing value imputation, and feature engineering (Hour, DayOfWeek, Season, Is_Weekend).
- `extract_patterns()` — Computes macro-level stats: daily averages, peak/low hours, peak/low consumption days, and weekend-vs-weekday percentage delta.
- `disaggregate_appliances()` — Rules-based appliance load disaggregation, using submeter data where available, or dynamic peak/base load heuristics by facility type otherwise.

**`models_engine.py`** — Contains the `ForecastingEngine` class:
- `generate_forecast()` — Resamples data to hourly frequency, computes hour-of-day and day-of-week effect vectors from historical data, and generates future predictions with Gaussian noise. Outputs forecast DataFrame with `yhat`, `yhat_lower`, and `yhat_upper` columns, plus summary metrics (MAE, RMSE, MAPE).

**`config.py`** — Contains the `UIConfig` class:
- Design token constants (colour palette, card backgrounds, accent colours).
- `inject_theme()` — Injects a comprehensive custom CSS block via `st.markdown` for the deep-navy dark theme.
- `render_kpi()` — Generates styled KPI card HTML with directional delta indicators.

---

## 🛠️ Technology Stack

| Layer | Library / Tool |
|---|---|
| **Framework** | [Streamlit](https://streamlit.io/) |
| **Data Processing** | [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/) |
| **Visualisation** | [Plotly Express](https://plotly.com/python/plotly-express/), [Plotly Graph Objects](https://plotly.com/python/) |
| **Language** | Python 3.8+ |

---

## 📦 Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip

### 1. Clone the Repository

```bash
git clone https://github.com/kanix0067/Energy-Consumption-Forecasting.git
cd Energy-Consumption-Forecasting
```

### 2. Install Dependencies

```bash
pip install streamlit pandas numpy plotly
```

### 3. Run the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`.

---

## 📄 Data Format

EnerVision AI accepts any `.csv` file with at minimum:

- A **datetime column** — named `Datetime`, `Date`, `Timestamp`, or a combination of `Date` + `Time` columns.
- A **numeric energy column** — named `Global_active_power`, `active_power`, `consumption`, `energy`, `kw`, or `kwh`. If none of these are detected, the first available numeric column is used.

**Optional submeter columns** (`Sub_metering_1`, `Sub_metering_2`, `Sub_metering_3`, `Sub_metering_4`) enable real appliance disaggregation for Household mode.

### Recommended Dataset

The application is designed to work well with the [UCI Individual Household Electric Power Consumption Dataset](https://archive.ics.uci.edu/ml/datasets/Individual+household+electric+power+consumption), which provides minute-level readings over ~4 years.

### Example CSV Structure

```
Date,Time,Global_active_power,Sub_metering_1,Sub_metering_2,Sub_metering_3
16/12/2006,17:24:00,4.216,0.0,1.0,17.0
16/12/2006,17:25:00,5.360,0.0,1.0,16.0
```

---

## 🖥️ Application Walkthrough

### 🏡 Operational Overview
Provides a high-level snapshot of facility performance — total consumption baseline, daily average, estimated electricity bill, and CO₂ footprint. Includes a real-time alert if recent usage exceeds the historical daily average, alongside a 7-day timeline trend chart.

### 📊 Consumption Profiler
Breaks down energy usage by hour-of-day (bar chart), weekday vs. weekend split (pie chart), and appliance category allocation (donut chart). Facility type selection dynamically adapts the appliance breakdown.

### 🔮 Intelligence Forecasting
Generates demand forecasts for 1 Day, 1 Week, 1 Month, or 1 Year horizons. The forecasting model applies hour-of-day and day-of-week seasonal effects derived from historical data, with ±15% (short-term) or ±25% (long-term) confidence intervals rendered as a shaded band. Outputs include predicted total units, estimated cost, and predicted peak day. Technical diagnostics (MAE, RMSE, MAPE) are available in an expandable panel.

### 🌱 Optimization Blueprint
Interactive what-if simulator allowing users to model 5–40% consumption reduction targets. Instantly calculates projected financial savings, energy units conserved, and CO₂ emissions prevented. Accompanied by three AI-generated, pattern-driven efficiency action items specific to the facility's observed consumption behaviour.

---

## ⚙️ Configuration

The electricity unit rate defaults to **₹8.00/kWh** and can be adjusted from ₹1 to ₹50 in the sidebar under **Cost Configuration**. All financial projections throughout the application update dynamically based on this value.

---

## 🌱 Sustainability Metrics

Carbon emissions are estimated at **0.85 kg CO₂ per kWh**, consistent with the average Indian grid emission factor. This drives the carbon footprint KPI on the overview page and the CO₂ mitigation metric in the optimization simulator.

---

## 📈 Forecasting Methodology

The `ForecastingEngine` uses a **decomposition-inspired statistical approach**:

1. Resamples raw data to a continuous hourly time series (forward-filling gaps).
2. Computes a rolling **recent mean** from the last 168 hours (7 days) as the base level.
3. Derives **hour-of-day effects** and **day-of-week effects** as mean deviations from the global average.
4. Sums base + hour effect + day effect + small Gaussian noise for each future timestamp.
5. Applies asymmetric confidence bands: ±15% for short horizons (1 Day, 1 Week), ±25% for longer horizons (1 Month, 1 Year).

This approach is lightweight, requires no external ML libraries, and generalises well across different dataset sizes and sampling frequencies.

---

## 🎨 UI Design

The application features a custom dark theme with a deep-navy (`#0B111E`) background, implemented entirely via Streamlit's `st.markdown` CSS injection. Key design tokens:

| Token | Value | Use |
|---|---|---|
| `DARK_BG` | `#0B111E` | Page background |
| `CARD_BG` | `#151C2C` | Card / panel backgrounds |
| `ACCENT_GREEN` | `#10B981` | Positive metrics, savings |
| `ACCENT_BLUE` | `#3B82F6` | Primary charts, trends |
| `ACCENT_PURPLE` | `#8B5CF6` | Weekend/secondary highlights |
| `ACCENT_RED` | `#EF4444` | Alerts, peak warnings |

---

## 🔭 Roadmap & Potential Enhancements

- [ ] Integration of Prophet or LSTM models for higher-accuracy long-horizon forecasting
- [ ] Multi-file / multi-facility comparison mode
- [ ] Exportable PDF reports from the dashboard
- [ ] Tariff tier modelling (time-of-use pricing)
- [ ] Solar generation offset integration
- [ ] Anomaly detection alerts for sudden consumption spikes

---

## 🤝 Contributing

Contributions are welcome. Please open an issue to discuss proposed changes before submitting a pull request.

---

## 📃 License

This project is open source. See the repository for licensing details.

---

## 👤 Author
Kaniga K

kanix0067— [GitHub Profile](https://github.com/kanix0067)
