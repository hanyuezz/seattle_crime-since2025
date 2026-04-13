import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Seattle Crime Interactive Visualization",
    layout="wide"
)

st.title("Seattle Crime Interactive Visualization Since 2025")

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

# 提取年份
df["Year"] = df["Offense Date"].dt.year

# 只保留合理年份（与你现在的数据一致）
df = df[(df["Year"] >= 2025) & (df["Year"] <= 2026)]

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
]

# Question
st.subheader("Question")
st.write("How do crime patterns vary across different areas of Seattle since 2025?")

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
    title=f"Seattle Crime Map - {selected_type}",
    height=500
)

fig_map.update_traces(marker={"size": 5})
fig_map.update_layout(
    mapbox_style="carto-positron",
    margin=dict(l=0, r=0, t=50, b=0)
)

st.plotly_chart(fig_map, use_container_width=True)

# 两列布局
col1, col2 = st.columns(2)

# Trend
with col1:
    st.subheader("Trend Over Time")

    trend_df = (
        filtered_df.groupby("Year")
        .size()
        .reset_index(name="Count")
    )

    fig_line = px.line(
        trend_df,
        x="Year",
        y="Count",
        markers=True,
        title=f"Trend of {selected_type} Since 2025"
    )

    fig_line.update_layout(margin=dict(l=0, r=0, t=50, b=0))
    st.plotly_chart(fig_line, use_container_width=True)

# Top Crime Types
with col2:
    st.subheader("Top Crime Types")

    top_crime_df = (
        df[
            (df["Year"] >= selected_years[0]) &
            (df["Year"] <= selected_years[1])
        ]["Offense Category"]
        .value_counts()
        .head(10)
        .reset_index()
    )

    top_crime_df.columns = ["Crime", "Count"]

    fig_bar = px.bar(
        top_crime_df,
        x="Crime",
       
