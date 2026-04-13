import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Seattle Crime Interactive Visualization", layout="wide")

st.title("Seattle Crime Interactive Visualization")

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

# 侧边栏交互
st.sidebar.header("Filters")

top_crime_types = df["Offense Category"].value_counts().head(10).index.tolist()
selected_type = st.sidebar.selectbox("Select Crime Type", top_crime_types)

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

# 问题说明
st.subheader("Question")
st.write("How do crime patterns vary across different areas and over time in Seattle?")

# 地图
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
fig_map.update_layout(mapbox_style="carto-positron", margin=dict(l=0, r=0, t=50, b=0))

st.plotly_chart(fig_map, use_container_width=True)

# 两列布局
col1, col2 = st.columns(2)

# 趋势图
with col1:
    st.subheader("Trend Over Time")

    trend_df = (
        df[df["Offense Category"] == selected_type]
        .groupby("Year")
        .size()
        .reset_index(name="Count")
    )

    fig_line = px.line(
        trend_df,
        x="Year",
        y="Count",
        markers=True,
        title=f"Trend of {selected_type} Over Time"
    )
    fig_line.update_layout(margin=dict(l=0, r=0, t=50, b=0))

    st.plotly_chart(fig_line, use_container_width=True)

# Top crimes
with col2:
    st.subheader("Top Crime Types")

    top_crime_df = df["Offense Category"].value_counts().head(10).reset_index()
    top_crime_df.columns = ["Crime", "Count"]

    fig_bar = px.bar(
        top_crime_df,
        x="Crime",
        y="Count",
        title="Top 10 Crime Types in the Dataset"
    )
    fig_bar.update_layout(xaxis_tickangle=-35, margin=dict(l=0, r=0, t=50, b=0))

    st.plotly_chart(fig_bar, use_container_width=True)

# Write-up
st.subheader("Design Rationale")
st.write(
    "A map was used to show the geographic distribution of crimes because location is one of the most important aspects of this dataset. "
    "Interactive filters were added so users can explore different crime categories and year ranges. "
    "A line chart was used to show change over time, and a bar chart was used to summarize the most common offense categories."
)

st.subheader("Data Source")
st.write("Seattle Open Data: SPD Crime Data")

st.subheader("Development Reflection")
st.write(
    "This project took approximately ___ hours to complete. "
    "The most time-consuming part was cleaning the dataset and preparing the selected variables for interactive visualization."
)
