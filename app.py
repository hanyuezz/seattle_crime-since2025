import streamlit as st
import plotly.express as px
import pandas as pd

# 1. 页面配置
st.set_page_config(page_title="Seattle Crime Explorer", layout="wide")
st.title("Seattle Crime Data Interactive Explorer (2025-Present)")

# 2. 数据加载
@st.cache_data
def load_data():
    # 读取 CSV
    data = pd.read_csv('seattle_crime_small.csv')
    # 强制清理列名空格，防止认错列
    data.columns = data.columns.str.strip()
    # 转换时间并提取年份
    data['Report DateTime'] = pd.to_datetime(data['Report DateTime'])
    data['Year'] = data['Report DateTime'].dt.year
    return data

df = load_data()

# 3. 侧边栏
st.sidebar.header("Filter Controls")
years = sorted(df['Year'].unique())
selected_year = st.sidebar.select_slider("Select Year", options=years, value=max(years))

# 核心列名：Offense Category
target_col = 'Offense Category' 
crime_options = sorted(df[target_col].unique())
selected_crimes = st.sidebar.multiselect("Select Categories", options=crime_options, default=crime_options[:5])

# 4. 数据过滤
mask = (df['Year'] == selected_year) & (df[target_col].isin(selected_crimes))
filtered_df = df[mask].copy()

# 5. 顶部数字指标
m1, m2, m3 = st.columns(3)
m1.metric("Total Incidents", f"{len(filtered_df):,}")
m2.metric("Active Neighborhoods", filtered_df['Neighborhood'].nunique())
m3.metric("Selected Year", selected_year)

st.divider()

# 6. 图表展示
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("Crime Frequency")
    # 使用 histogram 是最稳的，它不需要手动重命名列，绝对不会报 KeyError
    fig_bar = px.histogram(
        filtered_df, 
        x=target_col, 
        color=target_col,
        template="plotly_white"
    )
    # 隐藏侧边图例，让画面干净
    fig_bar.update_layout(showlegend=False)
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.subheader("Geographical Distribution")
    # 地图核心修正：使用 open-street-map，这个样式 100% 不需要 Token
    if not filtered_df.empty:
        fig_map = px.scatter_mapbox(
            filtered_df, 
            lat="Latitude", 
            lon="Longitude",
            color=target_col, 
            hover_name="Offense", 
            mapbox_style="open-street-map", # 必须是这个样式
            zoom=10, 
            height=500
        )
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.write("No data found.")

# 7. 数据底表
with st.expander("View Data Table"):
    st.dataframe(filtered_df)
