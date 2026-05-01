# Import libraries
# Import libraries
import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd
import json
from shapely.geometry import shape
import plotly.express as px
import plotly.io as pio

from data_loader import load_dvf, load_rent

# Global plot style
pio.templates.default = "plotly_white"

# Page config
st.set_page_config(
    page_title="Rent Control Analysis",
    page_icon="📊",
    layout="wide",
)

# Header
st.title("Rent Control Analysis")
st.caption(
    "This page explores the relationship between property prices and rent control zones in Paris (2025). "
    "Each property is assigned to a zone using a spatial point-in-polygon join."
)
st.markdown("---")

# -------------------------
# Load data
# -------------------------
dvf_raw = load_dvf()
rent_raw = load_rent()

# -------------------------
# Prepare DVF (points)
# -------------------------
dvf = dvf_raw[
    (dvf_raw["data_quality_flag"] == "ok") &
    (dvf_raw["price_per_sqm"].notna()) &
    (dvf_raw["lat"].notna()) &
    (dvf_raw["lon"].notna())
].copy()

dvf_gdf = gpd.GeoDataFrame(
    dvf,
    geometry=gpd.points_from_xy(dvf["lon"], dvf["lat"]),
    crs="EPSG:4326"
)

# -------------------------
# Prepare rent polygons
# -------------------------
rent_unique = rent_raw.drop_duplicates("quarter_id").copy()

geoms = [
    shape(json.loads(row["geo_shape"])["geometry"])
    for _, row in rent_unique.iterrows()
]

rent_gdf = gpd.GeoDataFrame(
    rent_unique,
    geometry=geoms,
    crs="EPSG:4326"
)

# -------------------------
# Spatial join
# -------------------------
joined = gpd.sjoin(
    dvf_gdf,
    rent_gdf[["quarter_id", "geometry"]],
    how="inner",
    predicate="within"
)

# -------------------------
# Aggregate DVF by zone
# -------------------------
dvf_grouped = (
    joined.groupby("quarter_id")
    .agg(
        median_price=("price_per_sqm", "median"),
        n_tx=("price_per_sqm", "count")
    )
    .reset_index()
)

# -------------------------
# Merge with rent data
# -------------------------
rent = rent_raw[rent_raw["room_count"] == 2].copy()

df = pd.merge(rent, dvf_grouped, on="quarter_id", how="inner")
df = df.dropna(subset=["reference_rent", "median_price"])

# -------------------------
# KPI row
# -------------------------
c1, c2, c3 = st.columns(3)

c1.metric("Zones analyzed", len(rent_raw['zone_id'].unique()))
c2.metric("Avg. property price (€/m²)", f"{dvf['price_per_sqm'].mean():,.0f}")
c3.metric("Avg. reference rent (€/m²)", f"{rent_raw['reference_rent'].mean():.1f}")

st.markdown("---")

# -------------------------
# Description
# -------------------------
st.markdown("""
This analysis focuses on four key areas:
1. Relationship between rent controls and property prices  
2. Distribution of property prices across rent control levels  
3. Average property prices by rent control category
4. Transaction volume across different rent control zones
""")

# -----------------------
# Scatter plot
# -------------------------
fig1 = px.scatter(
    df,
    x="reference_rent",
    y="median_price",
    size="n_tx",
    color="median_price",
    color_continuous_scale="Viridis",
    title="Property Prices vs Reference Rent",
    labels={
        "reference_rent": "Reference Rent (€/m²)",
        "median_price": "Median Price (€/m²)",
        "n_tx": "Transactions",
    },
)


# -------------------------
# Boxplot
# -------------------------
df["rent_bin"] = pd.qcut(
    df["reference_rent"],
    q=4,
    labels=["Low", "Mid-Low", "Mid-High", "High"]
)

fig2 = px.box(
    df,
    x="rent_bin",
    y="median_price",
    color="rent_bin",
    title="What is the range of property prices across rent control levels?",
    labels={
        "rent_bin": "Reference Rent Category",
        "median_price": "Median Price (€/m²)",
    },
)
fig2.update_layout(showlegend=False)

st.markdown("---")

# -------------------------
# Bar chart
# -------------------------
bar_df = df.groupby("rent_bin")["median_price"].mean().reset_index()

fig3 = px.bar(
    bar_df,
    x="rent_bin",
    y="median_price",
    color="median_price",
    color_continuous_scale="Blues",
    title="Average Price by Rent Category",
    labels={
        "rent_bin": "Reference Rent Category",
        "median_price": "Average Price (€/m²)",
    },
)

fig3.update_xaxes(type="category")

# -------------------------
# Layout (side-by-side like example)
# -------------------------
st.plotly_chart(fig1, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig2, use_container_width=True)
    st.caption(
        "This chart shows how property price distributions shift across rent control levels."
    )

with col2:
    st.plotly_chart(fig3, use_container_width=True)
    st.caption(
        "Average property prices increase across higher rent control categories."
    )

st.markdown("---")

# -------------------------
# No. Transactions vs Rent
# -------------------------

# Group df by zone_id, counting transactions and averaging reference rent
tx_df = df.groupby("zone_id").agg(
    n_tx=("n_tx", "sum"),
    reference_rent=("reference_rent", "mean")
).reset_index()

tx_df["zone_id"] = tx_df["zone_id"].astype(str)
tx_df = tx_df.sort_values("n_tx", ascending=False)

# Define sort order
zone_order = tx_df.sort_values("n_tx", ascending=False)["zone_id"].tolist()

# Plot bar chart
fig4 = px.bar(
    tx_df,
    x="zone_id",
    y="n_tx",
    color="reference_rent",
    title="Are there more transactions in certain rent control zones?",
    labels={
        "zone_id": "Zone",
        "n_tx": "Number of Transactions",
    },
    color_continuous_scale="Blues",
    category_orders={'zone_id':zone_order}
)

# Show all labels + rotate
fig4.update_xaxes(
    tickmode="linear"
)

# Update colorscale
fig4.update_layout(
    coloraxis_colorbar=dict(
        title="Reference Rent (€/m²)"
    )
)

# Update hover template (tooltoip) to show all info
fig4.update_traces(
    hovertemplate=
    "<b>Zone:</b> %{x}<br>" +
    "<b>Transactions:</b> %{y:,.0f}<br>" +
    "<b>Reference Rent:</b> %{marker.color:.2f} €/m²<br>" +
    "<extra></extra>")

# Remove legend (color is self-explanatory in this case)
fig4.update_layout(showlegend=False)

# Set height to avoid cutting off labels
st.plotly_chart(fig4, width='content')


st.caption(
    "Preliminary insight: areas with higher rent caps tend to align with higher property values, "
    "suggesting that rent regulation **reflects underlying market attractiveness rather than determining it**."
)

# -------------------------
#  Insights
# -------------------------

st.markdown("---")

st.header("Insights:")
st.info("""
    **Insight 1**\n
    **Insight 2**\n
    **Insight 3**\n
    """)