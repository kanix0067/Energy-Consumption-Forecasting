import streamlit as st

class UIConfig:
    # --- Backgrounds & Borders ---
    DARK_BG = "#0B111E"      # Deep Navy
    CARD_BG = "#151C2C"      # Slightly Lighter Navy
    BORDER_COLOR = "#334155" # Muted Slate Grey

    # --- Vibrant Text Palette ---
    TEXT_MAIN = "#FFFFFF"      # Pure White (Main content contrast)
    TEXT_MUTED = "#94A3B8"     # Soft Slate Grey (Secondary info)
    
    # --- Brand Accents (Vibrant) ---
    ACCENT_GREEN = "#10B981"   
    ACCENT_BLUE = "#3B82F6"   
    ACCENT_PURPLE = "#8B5CF6"  
    ACCENT_ORANGE = "#F59E0B"
    ACCENT_RED = "#EF4444"     
    
    @staticmethod
    def inject_theme():
        st.markdown(
            f"""
            <style>
            /* Global Font, Background & Main Text Color Override */
            .stApp {{
                background-color: {UIConfig.DARK_BG};
                color: #FFFFFF !important; 
                font-family: 'Inter', sans-serif;
            }}
            
            /* Main Dashboard Title with Green-Blue Gradient */
            .main-title {{
                font-size: 2.5rem;
                font-weight: 800;
                background: linear-gradient(90deg, {UIConfig.ACCENT_GREEN}, {UIConfig.ACCENT_BLUE});
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 1rem;
            }}
            
            /* KPI Cards & Sidebar Config Boxes (Expanding generic expander style) */
            .ev-card {{
                background-color: {UIConfig.CARD_BG};
                border: 1px solid {UIConfig.BORDER_COLOR};
                border-radius: 12px;
                padding: 1.5rem;
                margin-bottom: 1rem;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
            }}
            
            /* Metric Titles (Muted) */
            .ev-metric-title {{
                color: {UIConfig.TEXT_MUTED};
                font-size: 0.85rem;
                text-transform: uppercase;
                letter-spacing: 0.1em;
                margin-bottom: 6px;
            }}
            
            /* Metric Values (Vibrant Pure White) */
            .ev-metric-value {{
                color: #FFFFFF;
                font-size: 2.2rem;
                font-weight: 800;
                margin-bottom: 4px;
            }}
            
            /* Metric Delta Color Overrides */
            .delta-up {{ color: {UIConfig.ACCENT_RED} !important; }}
            .delta-down {{ color: {UIConfig.ACCENT_GREEN} !important; }}
            
            /* Generic expander background & border */
            div[data-testid="stExpander"] {{
                background-color: {UIConfig.CARD_BG};
                border: 1px solid {UIConfig.BORDER_COLOR};
                border-radius: 8px;
            }}

            /* --- Sidebar Styling & Text Correction --- */
            
            /* Sidebar background and right border */
            section[data-testid="stSidebar"] {{
                background-color: #070B14 !important;
                border-right: 1px solid {UIConfig.BORDER_COLOR};
            }}
            
            /* FIX: White on Black Sidebar elements. Force text to grey/muted */
            [data-testid="stSidebar"] label {{
                color: #94A3B8 !important;
                font-size: 0.85rem !important;
                font-weight: 500 !important;
            }}
            
            /* Target generic p, span, summary p, summary span inside sidebar to be white */
            [data-testid="stSidebar"] p, 
            [data-testid="stSidebar"] span, 
            [data-testid="stSidebar"] summary p, 
            [data-testid="stSidebar"] summary span {{
                color: #FFFFFF !important;
            }}
            
            /* Ensure h3 headers in sidebar stay white */
            [data-testid="stSidebar"] h1, 
            [data-testid="stSidebar"] h2, 
            [data-testid="stSidebar"] h3 {{
                color: #FFFFFF !important;
            }}

            /* --- Inputs & Selectboxes - Fix the 'White Dropdown Box' Bug --- */
            
            /* Direct targeting of the Selectbox box to ensure DARK background */
            div[data-baseweb="select"] > div {{
                background-color: {UIConfig.CARD_BG} !important;
                border: 1px solid {UIConfig.BORDER_COLOR} !important;
                color: {UIConfig.TEXT_MAIN} !important;
            }}
            
            /* Input Box Text Color */
            div[data-baseweb="select"] span {{
                color: {UIConfig.TEXT_MAIN} !important;
            }}
            
            /* Text Color for generic input labels */
            div[data-baseweb="input"] label, div[data-baseweb="slider"] label {{
                color: {UIConfig.TEXT_MAIN} !important;
            }}
            
            /* Fixing the popup list of options */
            div[role="listbox"], div[role="option"] {{
                background-color: {UIConfig.CARD_BG} !important;
                color: {UIConfig.TEXT_MAIN} !important;
            }}
            
            /* Styling on hover */
            div[role="option"]:hover {{
                background-color: {UIConfig.BORDER_COLOR} !important;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
        
    @staticmethod
    def render_kpi(title: str, value: str, delta: str, direction: str, context: str = "vs Last Week"):
        # Explicitly use the accent colors for delta within the kpi card
        delta_class = "delta-down" if direction == "down" else "delta-up"
        delta_color = UIConfig.ACCENT_GREEN if direction == "down" else UIConfig.ACCENT_RED
        delta_arrow = "↓" if direction == "down" else "↑"
        
        return f"""
        <div class="ev-card">
            <div class="ev-metric-title">{title}</div>
            <div class="ev-metric-value">{value}</div>
            <div class="ev-metric-delta {delta_class}">
                {delta_arrow} {delta} <span style="color: "White"; font-weight: 400; padding-left: 5px;">{context}</span>
            </div>
        </div>
        """