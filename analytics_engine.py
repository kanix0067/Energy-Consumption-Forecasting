import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any

class AnalyticsEngine:
    @staticmethod
    def validate_and_parse(df: pd.DataFrame) -> Tuple[bool, str, pd.DataFrame]:
        """Cleans and normalizes incoming datasets to ensure robust pipeline behavior."""
        df_clean = df.copy()
        
        # Column matching logic (case-insensitive adjustment)
        cols_map = {col.lower().replace(" ", "_"): col for col in df_clean.columns}
        
        datetime_col = None
        for candidate in ['datetime', 'date', 'timestamp', 'time']:
            if candidate in cols_map:
                datetime_col = cols_map[candidate]
                break
                
        if not datetime_col and 'date' in cols_map and 'time' in cols_map:
            try:
                df_clean['Datetime'] = pd.to_datetime(df_clean[cols_map['date']].astype(str) + ' ' + df_clean[cols_map['time']].astype(str))
                datetime_col = 'Datetime'
            except:
                return False, "Failed to combine separate Date and Time markers.", df
        elif datetime_col:
            df_clean['Datetime'] = pd.to_datetime(df_clean[datetime_col])
            datetime_col = 'Datetime'
        else:
            return False, "Could not locate standard Date, Time, or Datetime columns.", df
            
        df_clean = df_clean.sort_values('Datetime').reset_index(drop=True)
        
        # Map primary target tracking dimension
        target_candidates = ['global_active_power', 'active_power', 'consumption', 'energy', 'kw', 'kwh']
        found_target = None
        for tc in target_candidates:
            if tc in cols_map:
                found_target = cols_map[tc]
                df_clean = df_clean.rename(columns={found_target: 'Global_active_power'})
                found_target = 'Global_active_power'
                break
                
        if not found_target:
            numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                df_clean = df_clean.rename(columns={numeric_cols[0]: 'Global_active_power'})
            else:
                return False, "No numeric energy measurement metrics were detected.", df
                
        df_clean['Global_active_power'] = pd.to_numeric(df_clean['Global_active_power'], errors='coerce').clip(lower=0)
        
        null_count = df_clean['Global_active_power'].isnull().sum()
        if null_count > 0:
            df_clean['Global_active_power'] = df_clean['Global_active_power'].ffill().bfill()
            
        # Structure submeter designations if missing
        for sub in ['Sub_metering_1', 'Sub_metering_2', 'Sub_metering_3', 'Sub_metering_4']:
            matched = [cols_map[c] for c in cols_map if sub.lower() in c]
            if matched:
                df_clean = df_clean.rename(columns={matched[0]: sub})
                df_clean[sub] = pd.to_numeric(df_clean[sub], errors='coerce').clip(lower=0).ffill().bfill()
        
        # Feature Engineering Pipeline
        df_clean['Hour'] = df_clean['Datetime'].dt.hour
        df_clean['Day'] = df_clean['Datetime'].dt.day
        df_clean['Month'] = df_clean['Datetime'].dt.month
        df_clean['Year'] = df_clean['Datetime'].dt.year
        df_clean['DayOfWeek'] = df_clean['Datetime'].dt.dayofweek
        df_clean['Is_Weekend'] = df_clean['DayOfWeek'].apply(lambda x: 1 if x >= 5 else 0)
        
        df_clean['Season'] = df_clean['Month'].apply(
            lambda m: 'Winter' if m in [12, 1, 2] else ('Spring' if m in [3, 4, 5] else ('Summer' if m in [6, 7, 8] else 'Autumn'))
        )
        
        msg = f"Data verified. Successfully processed {len(df_clean)} records cleanly."
        if null_count > 0:
            msg += f" Filled {null_count} missing entries safely using chronological trends."
            
        return True, msg, df_clean

    @staticmethod
    def extract_patterns(df: pd.DataFrame) -> Dict[str, Any]:
        """Calculates macro-level operational summaries."""
        daily_group = df.groupby(df['Datetime'].dt.date)['Global_active_power'].sum()
        monthly_group = df.groupby('Month')['Global_active_power'].mean()
        yearly_group = df.groupby('Year')['Global_active_power'].mean() # Your custom addition
        hourly_group = df.groupby('Hour')['Global_active_power'].mean()
        weekend_group = df.groupby('Is_Weekend')['Global_active_power'].mean()
        
        peak_hour = hourly_group.idxmax()
        low_hour = hourly_group.idxmin()
        
        ampm_peak = f"{peak_hour % 12 or 12} {'PM' if peak_hour >= 12 else 'AM'}"
        ampm_low = f"{low_hour % 12 or 12} {'PM' if low_hour >= 12 else 'AM'}"
        
        return {
            "avg_daily_usage": daily_group.mean(),
            "highest_day_value": daily_group.max(),
            "highest_day_date": daily_group.idxmax().strftime('%B %d, %Y'),
            "lowest_day_value": daily_group.min(),
            "lowest_day_date": daily_group.idxmin().strftime('%B %d, %Y'),
            "peak_hour_str": ampm_peak,
            "low_hour_str": ampm_low,
            "weekend_vs_weekday_pct": ((weekend_group.get(1, 0) - weekend_group.get(0, 1)) / (weekend_group.get(0, 1) + 1e-5)) * 100
        }

    @staticmethod
    def disaggregate_appliances(df: pd.DataFrame, facility_type: str = "Household") -> Dict[str, float]:
        """Performs energy submetering partitioning dynamically based on facility type."""
        total = df['Global_active_power'].sum() + 1e-5
        
        # 1. Household Logic (with your Sub_metering_4 addition)
        if 'Sub_metering_1' in df.columns and facility_type == "Household":
            s1 = df['Sub_metering_1'].sum()
            s2 = df['Sub_metering_2'].sum()
            s3 = df['Sub_metering_3'].sum()
            s4 = df['Sub_metering_4'].sum() if 'Sub_metering_4' in df.columns else 0
            remainder = max(0, total - (s1 + s2 + s3 + s4))
            
            return {
                "Kitchen Appliances": (s1 / total) * 100,
                "Laundry & Cleaning": (s2 / total) * 100,
                "Climate Control & Heating": (s3 / total) * 100,
                "Other Electronics & Lighting": (remainder / total) * 100,
                "is_estimated": False
            }
            
        # 2. AI Rule-based Dynamic Estimations for different domains
        base_draw = df.groupby('Hour')['Global_active_power'].min().sum()
        peak_draw = total - base_draw
        
        peak_pct = (peak_draw / total) * 100
        base_pct = (base_draw / total) * 100
        
        # Commercial / Office Logic
        if facility_type == "Office / Commercial":
            return {
                "HVAC & Central AC": max(40.0, peak_pct * 0.6),
                "IT Servers & Computers": max(30.0, base_pct * 0.7),
                "Lighting & Desk Power": max(20.0, peak_pct * 0.4),
                "Pantry & Misc": 10.0,
                "is_estimated": True
            }
            
        # Education / School Logic
        elif facility_type == "School / University":
            return {
                "Lighting & Classroom Fans": max(35.0, peak_pct * 0.5),
                "Computer Labs & Equipment": max(30.0, base_pct * 0.6),
                "Central Air & Heating": max(25.0, peak_pct * 0.4),
                "Cafeteria & Misc": 10.0,
                "is_estimated": True
            }
            
        # Industrial / Manufacturing Logic
        elif facility_type == "Manufacturing Plant":
            return {
                "Heavy Machinery & Assembly Lines": max(50.0, peak_pct * 0.7),
                "HVAC & Cooling Systems": max(20.0, peak_pct * 0.3),
                "Lighting & Logistics": max(15.0, base_pct * 0.4),
                "Admin Offices & Servers": 15.0,
                "is_estimated": True
            }
            
        # Default Household Fallback
        else:
            return {
                "Kitchen Appliances": 28.5,
                "Laundry & Cleaning": 18.2,
                "Climate Control & Heating": max(15.0, peak_pct),
                "Other Electronics & Lighting": max(10.0, base_pct),
                "is_estimated": True
            }