import pandas as pd
import streamlit as st
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

@st.cache_data
def load_dvf():
    return pd.read_csv(DATA_DIR / "dvf_paris_2025_aggregated.csv")

@st.cache_data
def load_rent():
    return pd.read_csv(DATA_DIR / "api_rent_control_2025.csv")

@st.cache_data
def load_green():
    return pd.read_csv(DATA_DIR / "green_spaces.csv")

@st.cache_data
def load_planned():
    return pd.read_csv(DATA_DIR / "planned_green_spaces.csv")
