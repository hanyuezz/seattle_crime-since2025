import streamlit as st
import plotly.express as px
import pandas as pd

# 1. 基础配置
st.set_page_config(page_title="Seattle Crime Explorer", layout="wide")
st.title("Seattle Crime Data Interactive Explorer (2025-Present)")

# 2. 数据加载
@st.cache_data
def load_data():
    data = pd.read_csv('seattle_crime_small.csv')
    data.columns = data.columns.str.strip()
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
selected_crimes = st.sidebar.multiselect("Select Crime Categories", options=crime_options, default=crime_options[:5])

# 4. 过滤数据
mask = (df['Year'] == selected_year) & (df[target_col].isin(selected_crimes))
filtered_df = df[mask].copy() # 使用 .copy() 确保数据独立

# 5. 顶部数字指标
m1, m2, m3 = st.columns(3)
m1.metric("Total Incidents", len(filtered_df))
m2.metric("Neighborhoods", filtered_df['Neighborhood'].nunique())
m3.metric("Selected Year", selected_year)

st.divider()

# 6. 图表展示
col_left, col_right = st.columns([1, 1.2])

with col_left:
    st.subheader("Crime Frequency")
    # 先在本地数好数，再传给 Plotly，这样它绝对不会报 KeyError
    chart_data = filtered_df[target_col].value_counts().reset_index()
    chart_data.columns = ['Category', 'Count'] # 强制重命名列，消除歧义
    
    fig_bar = px.bar(
        chart_data, 
        x='Category', 
        y='Count', 
        color='Category',
        template="plotly_white"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.subheader("Geographical Distribution")
    # 地图最怕空数据，加个简单的判断
    if not filtered_df.empty:
        fig_map = px.scatter_mapbox(
            filtered_df, 
            lat="Latitude", 
            lon="Longitude",
            color=target_col, 
            hover_name="Offense", 
            mapbox_style="carto-positron", 
            zoom=10, height=550
        )
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning("No data found for the selected filters.")

# 7. 数据底表
with st.expander("View Raw Data"):
    st.dataframe(filtered_df.sort_values('Report DateTime', ascending=False))
