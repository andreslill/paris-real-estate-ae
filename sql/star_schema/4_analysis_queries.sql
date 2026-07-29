-- Paris Real Estate: Analytical queries on the star schema
-- Each query joins the fact table to dimensions to answer the project's key questions.

USE DATABASE PARIS_REALESTATE;
USE SCHEMA STAR;


-- 1) Average price per m2 and transaction volume by arrondissement
--    Insight: central districts show the highest prices, and high-value
--    areas tend to have lower transaction volumes.
SELECT
    a.arrondissement_number,
    COUNT(*)                       AS n_transactions,
    ROUND(AVG(f.price_per_sqm))    AS avg_price_per_sqm,
    ROUND(AVG(f.property_value))   AS avg_property_value
FROM FACT_TRANSACTION f
JOIN DIM_ARRONDISSEMENT a
    ON a.arrondissement_id = f.arrondissement_id
GROUP BY a.arrondissement_number
ORDER BY avg_price_per_sqm DESC;


-- 2) Price per m2 by property type
SELECT
    pt.property_type,
    COUNT(*)                       AS n_transactions,
    ROUND(AVG(f.price_per_sqm))    AS avg_price_per_sqm
FROM FACT_TRANSACTION f
JOIN DIM_PROPERTY_TYPE pt
    ON pt.property_type_id = f.property_type_id
GROUP BY pt.property_type
ORDER BY avg_price_per_sqm DESC;


-- 3) Green space provision vs. property prices by arrondissement
--    Insight: green space availability does not necessarily correlate
--    with premium property prices.
SELECT
    a.arrondissement_number,
    a.total_green_area_m2,
    a.planned_projects,
    ROUND(AVG(f.price_per_sqm))    AS avg_price_per_sqm
FROM FACT_TRANSACTION f
JOIN DIM_ARRONDISSEMENT a
    ON a.arrondissement_id = f.arrondissement_id
GROUP BY a.arrondissement_number, a.total_green_area_m2, a.planned_projects
ORDER BY a.total_green_area_m2 DESC;


-- 4) Monthly transaction trend
SELECT
    d.year,
    d.month,
    d.month_name,
    COUNT(*)                       AS n_transactions,
    ROUND(AVG(f.price_per_sqm))    AS avg_price_per_sqm
FROM FACT_TRANSACTION f
JOIN DIM_DATE d
    ON d.date_id = f.date_id
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month;


-- NOTE: Rent-control analysis (joining FACT_TRANSACTION to DIM_QUARTER) is pending.
-- FACT_TRANSACTION.quarter_id is not yet populated because assigning each property
-- to its rent-control quarter requires a point-in-polygon spatial join.
-- DIM_QUARTER is loaded and ready for that link.
