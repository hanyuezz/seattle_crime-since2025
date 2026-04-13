import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Recent Seattle Crime Patterns Since 2025",
    layout="wide"
)

st.title("Recent Seattle Crime Patterns Since 2025")

# 读取数据
df = pd.read_csv("seattle_crime_small.csv", low_memory=False)

# 只保留需要的列
df = df[
    [
        "Offense Date",
        "Offense Category",
        "Latitude",
        "Longitude",
        "Precinct",
        "Neighborhood",
        "NIBRS Crime Against Category"
    ]
].copy()

# 数据清理
df["Offense Date"] = pd.to_datetime(df["Offense Date"], errors="coerce")
df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")

df = df.dropna(subset=["Offense Date", "Offense Category", "Latitude", "Longitude"])

df["Year"] = df["Offense Date"].dt.year

# 只保留合理年份，和当前项目主题一致
df = df[df["Year"] >= 2025].copy()

# 侧边栏筛选
st.sidebar.header("Filters")

crime_types = df["Offense Category"].value_counts().head(10).index.tolist()
selected_type = st.sidebar.selectbox("Select Crime Type", crime_types)

year_min = int(df["Year"].min())
year_max = int(df["Year"].max())

selected_years = st.sidebar.slider(
    "Select Year Range",
    min_value=year_min,
    max_value=year_max,
    value=(year_min, year_max)
)

filtered_df = df[
    (df["Offense Category"] == selected_type) &
    (df["Year"] >= selected_years[0]) &
    (df["Year"] <= selected_years[1])
].copy()

# Question
st.subheader("Question")
st.write("What recent spatial and temporal crime patterns can be observed across Seattle since 2025?")

# Map
st.subheader("Crime Map")

fig_map = px.scatter_mapbox(
    filtered_df,
    lat="Latitude",
    lon="Longitude",
    hover_name="Offense Category",
    hover_data={
        "Offense Date": True,
        "Precinct": True,
        "Neighborhood": True,
        "Latitude": False,
        "Longitude": False
    },
    zoom=10,
    title=f"Seattle Crime Map - {selected_type}"
)

fig_map.update_traces(marker={"size": 5, "opacity": 0.5})
fig_map.update_layout(
    mapbox_style="carto-positron",
    margin=dict(l=0, r=0, t=50, b=0)
)

st.plotly_chart(fig_map, use_container_width=True)

# 两列布局
col1, col2 = st.columns(2)

# Trend
with col1:
    st.subheader("Trend Over Time (Monthly)")
    st.caption("Note: 2026 data is partial, so later months may appear lower.")

    # 提取年月
    filtered_df["YearMonth"] = filtered_df["Offense Date"].dt.to_period("M").astype(str)

    trend_df = (
        filtered_df.groupby("YearMonth")
        .size()
        .reset_index(name="Count")
    )

    fig_line = px.line(
        trend_df,
        x="YearMonth",
        y="Count",
        markers=True,
        title=f"Monthly Trend of {selected_type}"
    )

    fig_line.update_layout(
        xaxis_title="Month",
        yaxis_title="Crime Count",
        margin=dict(l=0, r=0, t=50, b=0)
    )

    st.plotly_chart(fig_line, use_container_width=True)

# Top crimes
with col2:
    st.subheader("Top Neighborhoods")

    top_neighborhood_df = (
        filtered_df["Neighborhood"]
        .dropna()
        .value_counts()
        .head(10)
        .reset_index()
    )

    top_neighborhood_df.columns = ["Neighborhood", "Count"]

    fig_bar = px.bar(
        top_neighborhood_df,
        x="Neighborhood",
        y="Count",
        title="Top Neighborhoods for Selected Crime Type"
    )

    fig_bar.update_layout(
        xaxis_tickangle=-35,
        margin=dict(l=0, r=0, t=50, b=0)
    )

    st.plotly_chart(fig_bar, use_container_width=True)

# Write-up
st.subheader("Design Rationale")
st.write(
    "This project focuses on recent crime data since 2025 rather than the full historical datset. "
    "A smaller and more recent subset was selected to keep the web application responsive and to highlight current spatial and temporal patterns. "
    "A map was used to show the geographic distribution of crimes because location is one of the most important aspects of this dataset. "
    "Interactive filters allow users to explore different crime categories and year ranges. "
    "A line chart shows how crime counts change over time, and a bar chart summarizes the most common offense categories in the selected time range."
)

st.subheader("Data Source")
st.write("Seattle Open Data: SPD Crime Data (2008–Present), using a subset from 2025 onward for this project.")
 
st.write(
    "This project took approximately 8 hours to complete. "
    "The most time-consuming part was cleaning the dataset and preparing a focused subset for interactive visualization."
)
