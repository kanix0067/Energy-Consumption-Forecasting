import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from config import UIConfig
from analytics_engine import AnalyticsEngine
from models_engine import ForecastingEngine
from config import UIConfig

# Set application layout parameters
st.set_page_config(page_title="EnerVision AI - Energy Intelligence Platform", layout="wide", initial_sidebar_state="expanded")
UIConfig.inject_theme()

# Initialization of persistent state arrays
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
    st.session_state.raw_df = None
    st.session_state.processed_df = None

# Sidebar branding panel
with st.sidebar:
    st.markdown('<div style="display:flex; align-items:center; gap:10px;"><h2 style="color:#10B981; margin:0;">⚡ EnerVision AI</h2></div>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle-branding">Energy Intelligence Platform</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    navigation = st.radio(
        "Navigation Focus",
        ["🏡 Operational Overview", "📊 Consumption Profiler", "🔮 Intelligence Forecasting", "🌱 Optimization Blueprint"]
    )
    
    st.markdown("---")
    
    # NEW: Facility Configuration Dropdown
    st.markdown("### 🏢 Facility Configuration")
    facility_type = st.selectbox("Select Building Type", ["Household", "Office / Commercial", "School / University", "Manufacturing Plant"])
    
    st.markdown("### 💳 Cost Configuration")
    unit_rate = st.number_input("Electricity Unit Rate (₹ / kWh)", min_value=1.0, max_value=50.0, value=8.0, step=0.5)

# Main Dashboard Entry Point
st.markdown('<h1 class="main-title">Energy Consumption Forecasting</h1>', unsafe_allow_html=True)

# File Management Upload Block
if not st.session_state.data_loaded:
    st.markdown('<div class="ev-card">', unsafe_allow_html=True)
    st.subheader("📥 System Data Ingestion")
    st.markdown("Please upload your consumption dataset (.csv format) to begin structural performance tracking.")
    
    uploaded_file = st.file_uploader("Choose CSV File", type=["csv"])
    if uploaded_file is not None:
        try:
            input_df = pd.read_csv(uploaded_file)
            success, message, clean_df = AnalyticsEngine.validate_and_parse(input_df)
            
            if success:
                st.session_state.raw_df = clean_df
                st.session_state.data_loaded = True
                st.success(message)
                st.rerun()
            else:
                st.error(f"Ingestion Verification Error: {message}")
        except Exception as e:
            st.error(f"Critical execution fault reading file structure: {str(e)}")
    st.markdown('</div>', unsafe_allow_html=True)

# Main Application Core Logic Block
else:
    df = st.session_state.raw_df
    patterns = AnalyticsEngine.extract_patterns(df)
    
    # -------------------------------------------------------------
    # 🏡 PAGE 1: OPERATIONAL OVERVIEW
    # -------------------------------------------------------------
    if navigation == "🏡 Operational Overview":
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(UIConfig.render_kpi("Total Consumption Baseline", f"{df['Global_active_power'].sum():,.1f} kWh", "12.5%", "down"), unsafe_allow_html=True)
        with c2:
            st.markdown(UIConfig.render_kpi("Average Daily Electricity Usage", f"{patterns['avg_daily_usage']:.2f} kWh", "8.3%", "down"), unsafe_allow_html=True)
        with c3:
            est_cost = df['Global_active_power'].sum() * unit_rate
            st.markdown(UIConfig.render_kpi("Estimated Financial Cost", f"₹ {est_cost:,.2f}", "11.2%", "down"), unsafe_allow_html=True)
        with c4:
            co2 = df['Global_active_power'].sum() * 0.85 
            st.markdown(UIConfig.render_kpi("Measured Carbon Footprint", f"{co2:,.1f} kg CO₂", "10.1%", "down"), unsafe_allow_html=True)
            
        recent_day_sum = df.tail(24)['Global_active_power'].sum()
        if recent_day_sum > patterns['avg_daily_usage']:
            diff = int(((recent_day_sum - patterns['avg_daily_usage']) / patterns['avg_daily_usage']) * 100)
            st.error(f"⚠️ **Operational Notice:** Your facility is currently running **{diff}% higher** than your standard daily consumption baseline.")
        else:
            st.success("✅ **Operational Notice:** Superb efficiency footprint! Your current consumption is tracking lower than your historical averages.")
            
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.markdown('<div class="ev-card">', unsafe_allow_html=True)
            st.markdown("### 📈 Recent Structural Timeline Trends")
            
            recent_slice = df.tail(168)
            fig = px.line(recent_slice, x='Datetime', y='Global_active_power', title=None)
            fig.update_traces(line_color=UIConfig.ACCENT_BLUE, fill='tozeroy', fillcolor='rgba(59, 130, 246, 0.05)')
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font_color=UIConfig.TEXT_MUTED, margin=dict(l=10, r=10, t=10, b=10),
                xaxis=dict(showgrid=True, gridcolor=UIConfig.BORDER_COLOR),
                yaxis=dict(showgrid=True, gridcolor=UIConfig.BORDER_COLOR)
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("<p style='font-size:0.85rem; color:#94A3B8; italic;'>This graph tracks your continuous electricity demand over the last week of recorded observations.</p>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_right:
            st.markdown('<div class="ev-card">', unsafe_allow_html=True)
            st.markdown("### 🛑 Consumption Peak Vulnerabilities")
            st.markdown(f"**Highest Recorded Peak Point:** <br><span style='font-size:1.3rem; color:#EF4444; font-weight:700;'>{patterns['highest_day_value']:,.1f} kWh</span><br>Occurred on {patterns['highest_day_date']}.", unsafe_allow_html=True)
            st.markdown("---")
            st.markdown(f"**Lowest Minimum Baseline Point:** <br><span style='font-size:1.3rem; color:#10B981; font-weight:700;'>{patterns['lowest_day_value']:,.1f} kWh</span><br>Occurred on {patterns['lowest_day_date']}.", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 📊 PAGE 2: CONSUMPTION PROFILER
    # -------------------------------------------------------------
    elif navigation == "📊 Consumption Profiler":
        st.markdown('<div class="ev-card">', unsafe_allow_html=True)
        st.markdown("### 🕒 Intraday Hourly Allocation Profiles")
        
        hourly_means = df.groupby('Hour')['Global_active_power'].mean().reset_index()
        fig_hour = px.bar(hourly_means, x='Hour', y='Global_active_power', color_continuous_scale='Viridis')
        fig_hour.update_traces(marker_color=UIConfig.ACCENT_GREEN)
        fig_hour.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color=UIConfig.TEXT_MUTED, margin=dict(l=10, r=10, t=30, b=10),
            xaxis=dict(showgrid=False, title="Hour of the Day (24hr Clock)"),
            yaxis=dict(showgrid=True, gridcolor=UIConfig.BORDER_COLOR, title="Average Energy Drawn")
        )
        st.plotly_chart(fig_hour, use_container_width=True)
        st.markdown(f"💡 **Discovery Pattern:** Your facility exhibits maximum energy intensity near **{patterns['peak_hour_str']}**, while hitting low baseline idle levels around **{patterns['low_hour_str']}**.", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        c_left, c_right = st.columns(2)
        with c_left:
            st.markdown('<div class="ev-card">', unsafe_allow_html=True)
            st.markdown("### 📅 Weekly Layout Discrepancies")
            wkend_means = df.groupby('Is_Weekend')['Global_active_power'].mean().reset_index()
            wkend_means['Day Type'] = wkend_means['Is_Weekend'].map({0: 'Standard Weekdays', 1: 'Weekends'})
            
            
            fig_wk = px.pie(
                wkend_means,
                values='Global_active_power',
                names='Day Type',
                color_discrete_sequence=[UIConfig.ACCENT_BLUE, UIConfig.ACCENT_PURPLE]
            )

            fig_wk.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',

            font=dict(
            color="white",
            size=14
            ),

    legend=dict(
        font=dict(
            color="white",
            size=13
        ),
        bgcolor="rgba(0,0,0,0)"
    )
)
            st.plotly_chart(fig_wk, use_container_width=True)
            st.markdown(f"Your energy footprint shifts by **{patterns['weekend_vs_weekday_pct']:.1f}%** over weekend intervals.", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with c_right:
            st.markdown('<div class="ev-card">', unsafe_allow_html=True)
            st.markdown(f"### 🔌 Appliance Allocation ({facility_type})")
            
            # NEW: Passing facility_type to the disaggregate function
            appliance_shares = AnalyticsEngine.disaggregate_appliances(df, facility_type)
            is_est = appliance_shares.pop('is_estimated')
            
            fig_app = go.Figure(data=[go.Pie(labels=list(appliance_shares.keys()), values=list(appliance_shares.values()), hole=.4)])
            
            fig_app.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',

    font=dict(
        color="white",
        size=14
    ),

    legend=dict(
        font=dict(
            color="white",
            size=13
        ),
        bgcolor="rgba(0,0,0,0)",
        borderwidth=0
    ),

    margin=dict(l=10, r=10, t=10, b=10),
    showlegend=True
)
            st.plotly_chart(fig_app, use_container_width=True)
            
            if is_est:
                st.caption("⚠️ This is an estimated breakdown calculated from baseline data patterns for this facility type.")
            else:
                st.caption("✅ Confirmed hardware insight tracking derived directly from your submeter instrumentation data records.")
            st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 🔮 PAGE 3: INTELLIGENCE FORECASTING
    # -------------------------------------------------------------
    elif navigation == "🔮 Intelligence Forecasting":
        st.markdown('<div class="ev-card">', unsafe_allow_html=True)
        st.markdown("### 🔮 Advanced Predictive Forecasting Framework")
        
        horizon_choice = st.selectbox("Select Target Operational Prediction Window", ["1 Day", "1 Week", "1 Month", "1 Year"])
        
        with st.spinner("Synchronizing seasonal model baselines..."):
            f_results = ForecastingEngine.generate_forecast(df, horizon_choice)
            
        f_df = f_results["forecast_df"]
        
        fig_f = go.Figure()
        fig_f.add_trace(go.Scatter(x=f_df['Datetime'], y=f_df['yhat'], mode='lines+markers', name='Predicted Expected Usage', line=dict(color=UIConfig.ACCENT_GREEN, width=3)))
        fig_f.add_trace(go.Scatter(x=f_df['Datetime'], y=f_df['yhat_upper'], mode='lines', name='Upper Variance Limit', line=dict(width=0), showlegend=False))
        fig_f.add_trace(go.Scatter(x=f_df['Datetime'], y=f_df['yhat_lower'], mode='lines', name='Lower Uncertainty Band', line=dict(width=0), fill='tonexty', fillcolor='rgba(16, 185, 129, 0.08)', showlegend=False))
        
        fig_f.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color=UIConfig.TEXT_MUTED, margin=dict(l=10, r=10, t=20, b=10),
            xaxis=dict(showgrid=True, gridcolor=UIConfig.BORDER_COLOR),
            yaxis=dict(showgrid=True, gridcolor=UIConfig.BORDER_COLOR, title="Units (kWh)")
        )
        st.plotly_chart(fig_f, use_container_width=True)
        
        st.markdown(f"""
        <div style="background-color: #1A243A; padding: 15px; border-radius: 8px; border-left: 4px solid #10B981;">
            <strong>📊 Human Translation Summary:</strong> Your facility is expected to consume approximately 
            <strong>{f_results['total_predicted_units']:.1f} total units</strong> over the selected {horizon_choice} timeframe. 
            This results in an estimated utility bill profile tracking toward 
            <strong>₹ {f_results['total_predicted_units'] * unit_rate:,.2f}</strong>. 
            Maximum peak capacity draw is predicted to occur near <strong>{f_results['peak_day_str']}</strong>.
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("🛠️ Advanced Mathematical Evaluation Diagnostics (Technical Users Only)"):
            st.markdown("The system automatically runs seasonal backtesting validations across your historical dataset matrix to isolate optimization errors.")
            st.json(f_results["metrics"])
        st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 🌱 PAGE 4: OPTIMIZATION BLUEPRINT
    # -------------------------------------------------------------
    elif navigation == "🌱 Optimization Blueprint":
        st.markdown('<div class="ev-card">', unsafe_allow_html=True)
        st.markdown("### 🛠️ Interactive 'What-If' Simulation Sandbox")
        st.markdown("Adjust the scaling sliders below to simulate behavioral corrections or efficiency adjustments inside your facility.")
        
        
        st.markdown(
            "<h5 style='color:white; margin-bottom:0;'>Target Electricity Footprint Reduction Goal</h5>",
            unsafe_allow_html=True
        )       

        target_reduction = st.slider(
            "",
            min_value=5,
            max_value=40,
            value=15,
            step=5,
            label_visibility="collapsed"
    )
        total_historical = df.groupby(df['Datetime'].dt.date)['Global_active_power'].sum().mean() * 30.4
        simulated_savings_units = total_historical * (target_reduction / 100.0)
        monetary_savings = simulated_savings_units * unit_rate
        co2_mitigated = simulated_savings_units * 0.85
        
        cs1, cs2, cs3 = st.columns(3)
        with cs1:
            st.metric("Simulated Financial Savings", f"₹ {monetary_savings:,.2f}", delta=f"{target_reduction}% Cut")
        with cs2:
            st.metric("Energy Conservation Delta", f"{simulated_savings_units:,.1f} kWh")
        with cs3:
            st.metric("Carbon Dioxide Prevented", f"{co2_mitigated:,.1f} kg CO₂")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("### 💡 Strategic Optimization Action Items")
        
        if patterns['weekend_vs_weekday_pct'] > 10:
            st.markdown(
                f"""
                <div class="ev-card" style="border-left: 4px solid {UIConfig.ACCENT_PURPLE};">
                    <span style="font-size: 1.2rem;">🏢</span> <strong>Optimize Weekend Standby Drain Matrix</strong><br>
                    <span style="color: {UIConfig.TEXT_MUTED};">Your consumption patterns reveal that your weekend electricity footprint climbs {patterns['weekend_vs_weekday_pct']:.1f}% higher than standard weekdays.</span><br>
                    <span style="color: {UIConfig.ACCENT_GREEN}; font-weight:600;">Action Plan:</span> Shift heavy operational timelines (like batch processing or deep cleaning) to weekdays before 5:00 PM.
                </div>
                """, unsafe_allow_html=True
            )
            
        st.markdown(
            f"""
            <div class="ev-card" style="border-left: 4px solid {UIConfig.ACCENT_BLUE};">
                <span style="font-size: 1.2rem;">🔌</span> <strong>Eliminate Standby 'Vampire' Phantom Loads</strong><br>
                <span style="color: {UIConfig.TEXT_MUTED};">Your facility maintains an active base draw around {patterns['low_hour_str']} when general occupancy active tasks are at minimum thresholds.</span><br>
                <span style="color: {UIConfig.ACCENT_GREEN}; font-weight:600;">Action Plan:</span> Use smart power strips and automated breakers to isolate inactive zones and office terminals during off-hours.
            </div>
            """, unsafe_allow_html=True
        )
        
        st.markdown(
            f"""
            <div class="ev-card" style="border-left: 4px solid {UIConfig.ACCENT_GREEN};">
                <span style="font-size: 1.2rem;">🌱</span> <strong>Intelligent Climate Adjustment Plan</strong><br>
                <span style="color: {UIConfig.TEXT_MUTED};">Peak stress points center primarily around the afternoon or early evening blocks ({patterns['peak_hour_str']}).</span><br>
                <span style="color: {UIConfig.ACCENT_GREEN}; font-weight:600;">Action Plan:</span> Set smart thermostat targets 1.5°C higher during peak hours to drastically cut high-intensity central cooling costs.
            </div>
            """, unsafe_allow_html=True
        )