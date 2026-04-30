rom __future__ import annotations

import pandas as pd

try:
    import plotly.express as px
    import streamlit as st
except ImportError:
    px = None
    st = None


TRANSACTION_PATH = "dvf_paris_2025_merged.csv"
GREEN_PATH = "green_spaces_updates.csv"
PLANNED_PATH = "Dataset/planned_green_spaces.csv"


def load_transaction_data(path: str = TRANSACTION_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df[df["price_per_sqm"].notna()].copy()
    df = df[df["property_value"].notna()].copy()
    df = df[(df["price_per_sqm"] > 0) & (df["property_value"] > 0)]

    for col in ["price_per_sqm", "property_value"]:
        df = df[df[col] <= df[col].quantile(0.99)]

    return df


def load_green_data(path: str = GREEN_PATH) -> pd.DataFrame:
    green = pd.read_csv(path)
    green["polygon_area"] = pd.to_numeric(green["polygon_area"], errors="coerce")
    green["arrondissement"] = pd.to_numeric(
        green["postal_code"].astype(str).str[-2:], errors="coerce"
    )
    return green


def load_planned_data(path: str = PLANNED_PATH) -> pd.DataFrame:
    planned = pd.read_csv(path)
    planned["arrondissement"] = pd.to_numeric(planned["arrondissement"], errors="coerce")
    planned["added_space_indicator"] = pd.to_numeric(
        planned["added_space_indicator"], errors="coerce"
    )
    return planned


def prepare_arrondissement_level_dataset() -> pd.DataFrame:
    tx = load_transaction_data()
    green = load_green_data()
    planned = load_planned_data()

    tx_agg = (
        tx.groupby("arrondissement", as_index=False)
        .agg(
            median_price_per_sqm=("price_per_sqm", "median"),
            median_property_value=("property_value", "median"),
            transaction_count=("transaction_key", "count"),
            avg_reference_rent=("avg_reference_rent", "median"),
        )
    )

    green_agg = (
        green.groupby("arrondissement", as_index=False)
        .agg(
            green_space_count=("green_space_id", "count"),
            total_green_area_m2=("polygon_area", "sum"),
            avg_green_area_m2=("polygon_area", "mean"),
        )
    )

    planned_agg = (
        planned.groupby("arrondissement", as_index=False)
        .agg(
            planned_projects=("project_name", "count"),
            total_planned_green_m2=("added_space_indicator", "sum"),
        )
    )

    merged = tx_agg.merge(green_agg, on="arrondissement", how="left")
    merged = merged.merge(planned_agg, on="arrondissement", how="left")
    merged = merged.fillna(
        {
            "green_space_count": 0,
            "total_green_area_m2": 0,
            "avg_green_area_m2": 0,
            "planned_projects": 0,
            "total_planned_green_m2": 0,
        }
    )

    merged["arrondissement_label"] = merged["arrondissement"].astype(int).astype(str)
    return merged.sort_values("arrondissement")


def chart_property_price_vs_green_context(df: pd.DataFrame):
    fig = px.scatter(
        df,
        x="total_green_area_m2",
        y="median_price_per_sqm",
        size="transaction_count",
        color="planned_projects",
        hover_data=[
            "arrondissement_label",
            "green_space_count",
            "avg_reference_rent",
            "total_planned_green_m2",
        ],
        title="Median Property Price vs Green Context by Arrondissement",
        labels={
            "total_green_area_m2": "Total existing green area (m²)",
            "median_price_per_sqm": "Median price per sqm (EUR)",
            "planned_projects": "Planned green projects",
            "transaction_count": "Transactions",
            "arrondissement_label": "Arrondissement",
        },
        color_continuous_scale="Greens",
    )

    fig.update_traces(
        marker=dict(line=dict(width=1, color="white")),
    )
    fig.update_layout(height=650)
    return fig


def chart_green_space_count_vs_price(df: pd.DataFrame):
    fig = px.bar(
        df.sort_values("median_price_per_sqm", ascending=False),
        x="arrondissement_label",
        y="green_space_count",
        color="median_price_per_sqm",
        title="Green Space Count by Arrondissement, Colored by Median Price per sqm",
        labels={
            "arrondissement_label": "Arrondissement",
            "green_space_count": "Existing green spaces",
            "median_price_per_sqm": "Median price per sqm (EUR)",
        },
        color_continuous_scale="YlGnBu",
    )
    return fig


def run_streamlit_app():
    st.set_page_config(page_title="Green Context Visuals", layout="wide")
    st.title("Property Price vs Green Context")
    st.caption(
        "Example visuals linking arrondissement-level property prices with existing and planned green-space context."
    )

    df = prepare_arrondissement_level_dataset()

    st.markdown(
        """
        This app works at arrondissement level, which is a safer level of comparison for green context.
        It avoids claiming a direct transaction-to-park relationship and instead asks whether greener areas
        also tend to have different price levels.
        """
    )

    fig1 = chart_property_price_vs_green_context(df)
    fig2 = chart_green_space_count_vs_price(df)

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(
        df[
            [
                "arrondissement_label",
                "median_price_per_sqm",
                "transaction_count",
                "green_space_count",
                "total_green_area_m2",
                "planned_projects",
                "total_planned_green_m2",
            ]
        ],
        use_container_width=True,
    )


if __name__ == "__main__":
    if st is None or px is None:
        print("This file is intended for Streamlit + Plotly.")
        print("Install with: pip install streamlit plotly pandas")
    else:
        run_streamlit_app()

