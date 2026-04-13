import streamlit as st
import plotly.express as px
import pandas as pd

# 1. 页面设置
st.set_page_config(page_title="Seattle Crime Explorer", layout="wide")
st.title("Seattle Crime Data Interactive Explorer (2025-Present)")

# 2. 数据加载
@st.cache_data
def load_data():
    data = pd.read_csv('seattle_crime_small.csv')
    data.columns = data.columns.str.strip() # 杀掉空格
    data['Report DateTime'] = pd.to_datetime(data['Report DateTime'])
    data['Year'] = data['Report DateTime'].dt.year
    return data

df = load_data()

# 3. 侧边栏
st.sidebar.header("Filter Controls")
years = sorted(df['Year'].unique())
selected_year = st.sidebar.select_slider("Select Year", options=years, value=max(years))

target_col = 'Offense Category' 
crime_options = sorted(df[target_col].unique())
selected_crimes = st.sidebar.multiselect("Select Categories", options=crime_options, default=crime_options[:5])

# 4. 过滤
mask = (df['Year'] == selected_year) & (df[target_col].isin(selected_crimes))
filtered_df = df[mask]

# 5. 顶部数字 (这些是对的，保留)
m1, m2, m3 = st.columns(3)
m1.metric("Total Incidents", len(filtered_df))
m2.metric("Neighborhoods", filtered_df['Neighborhood'].nunique())
m3.metric("Selected Year", selected_year)

st.divider()

# 6. 图表展示
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("Incident Frequency")
    # 使用 histogram，它会自动计算数量，绝对不会报 KeyError: 'count' 或 'Category'
    fig_bar = px.histogram(filtered_df, x=target_col, color=target_col)
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.subheader("Geographical Distribution")
    # 这一版地图样式改成了 'stamen-terrain' 或 'open-street-map'，不需要任何 Token
    fig_map = px.scatter_mapbox(
        filtered_df, 
        lat="Latitude", 
        lon="Longitude",
        color=target_col,
        mapbox_style="open-street-map", # 核心修改：确保不需要 Token
        zoom=10, 
        height=500
    )
    st.plotly_chart(fig_map, use_container_width=True)

# 7. 原始数据表格
with st.expander("View Data Table"):
    st.dataframe(filtered_df)
