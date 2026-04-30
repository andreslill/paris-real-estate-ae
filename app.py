import streamlit as st
from data_loader import load_dvf, load_rent, load_green, load_planned

st.set_page_config(
    page_title="Paris Real Estate",
    layout="wide",
)

# ── Load data for KPIs ────────────────────────────────────────────────────────
dvf     = load_dvf()
rent    = load_rent()
green   = load_green()
planned = load_planned()

dvf_clean        = dvf[dvf["data_quality_flag"] == "ok"]
total_transactions = len(dvf_clean)
median_price     = dvf_clean["price_per_sqm"].median()
avg_ref_rent     = rent["reference_rent"].mean()
n_green_spaces   = len(green)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("Real Estate in Paris 2025")

st.markdown("---")

# ── KPIs ──────────────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Transactions", f"{total_transactions:,}")
col2.metric("Median Price / m²",         f"€{median_price:,.0f}")
col3.metric("Avg. Reference Rent",       f"€{avg_ref_rent:.2f} /m²")
col4.metric("Existing Green Spaces",     f"{n_green_spaces:,}")

st.markdown("---")

# ── Context ───────────────────────────────────────────────────────────────────
st.subheader("Project Context")

col_left, col_right = st.columns([3, 2])

with col_left:
    st.markdown("""
Fluctuations in the housing market can have major social, economic, and political impacts.
In recent years, organisations like the World Economic Forum and the European Parliament
have spoken of a wide-sweeping **housing crisis**. Leading up to Paris's mayoral election
in March 2026, France24 reported that the *"capital's housing crisis could determine the
city's next mayor."*

Historically, rent caps have been one intervention for ensuring fair access to affordable
housing. In Paris they were reinstated most recently in 2019. This project examines the
relationship between property transaction prices, rent-control benchmarks, and urban
green-space availability across Paris's 20 arrondissements.
    """)

with col_right:
    st.markdown(
        """
        <div style="background:#f0f4ff; border-left:5px solid #3b6fd4; padding:16px 20px; border-radius:6px;">
        <strong>Project Objective</strong><br><br>
        <span style="font-size:0.95rem; color:#1f2937;">
        Lay the technical foundation for monitoring property values and rent-cap data provided
        by the City of Paris, including a robust database schema, an efficient ETL pipeline,
        and analytical visualisations tracking key metrics and patterns.
        </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# ── Research questions ────────────────────────────────────────────────────────
st.subheader("Research Questions")

q1, q2 = st.columns(2)
with q1:
    st.markdown(
        """
        <div style="background:#f8f9fa; border-radius:8px; padding:14px 18px; margin-bottom:12px;">
        <strong>Price vs. Rent Control</strong><br>
        How do actual transaction prices per m² compare to the legal rent-control reference
        values across Paris's quartiers?
        </div>
        <div style="background:#f8f9fa; border-radius:8px; padding:14px 18px;">
        <strong>Geographic Variation</strong><br>
        Which arrondissements show the largest gap between market prices and rent benchmarks?
        </div>
        """,
        unsafe_allow_html=True,
    )
with q2:
    st.markdown(
        """
        <div style="background:#f8f9fa; border-radius:8px; padding:14px 18px; margin-bottom:12px;">
        <strong>Green Space & Property Values</strong><br>
        Is there a measurable relationship between green-space coverage and property prices
        at the arrondissement level?
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# ── Dashboard pages ───────────────────────────────────────────────────────────
st.subheader("Dashboard Pages")

r1c1, r1c2 = st.columns(2)
r2c1, r2c2 = st.columns(2)

with r1c1:
    st.markdown(
        """
        <div style="border:1px solid #e5e7eb; border-radius:8px; padding:16px;">
        <strong>Data Sources</strong><br>
        <span style="color:#6b7280; font-size:0.9rem;">
        Four public datasets from the French government and the City of Paris. Scope, limitations,
        and pre-processing decisions.
        </span>
        </div>
        """, unsafe_allow_html=True,
    )
with r1c2:
    st.markdown(
        """
        <div style="border:1px solid #e5e7eb; border-radius:8px; padding:16px;">
        <strong>Data Modeling</strong><br>
        <span style="color:#6b7280; font-size:0.9rem;">
        From 3NF to Star Schema — schema design decisions, the full ER diagram, and key
        trade-offs made for analytical usability.
        </span>
        </div>
        """, unsafe_allow_html=True,
    )
with r2c1:
    st.markdown(
        """
        <div style="border:1px solid #e5e7eb; border-radius:8px; padding:16px; margin-top:12px;">
        <strong>ETL / ELT Pipeline</strong><br>
        <span style="color:#6b7280; font-size:0.9rem;">
        End-to-end pipeline from raw CSVs to a Snowflake Star Schema — extraction, transformation,
        loading, and lessons learned.
        </span>
        </div>
        """, unsafe_allow_html=True,
    )
with r2c2:
    st.markdown(
        """
        <div style="border:1px solid #e5e7eb; border-radius:8px; padding:16px; margin-top:12px;">
        <strong>Analysis</strong><br>
        <span style="color:#6b7280; font-size:0.9rem;">
        Interactive map of sale prices and rent-control zones. Price distributions, arrondissement
        comparisons, and green-space relationships.
        </span>
        </div>
        """, unsafe_allow_html=True,
    )

st.markdown("---")
st.caption("Paris Real Estate • Stefania Licciardi • Victoria Ford • Andrés Lill • May 2026")
