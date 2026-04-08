import streamlit as st
import plotly.express as px
import pandas as pd

# 1. 基础设置
st.set_page_config(page_title="Seattle Crime Explorer", layout="wide")
st.title("Seattle Crime Data Interactive Explorer (2025-Present)")
st.markdown("This dashboard focuses on recent crime patterns in Seattle (2025-2026).")

# 2. 读取数据 (核心修正：对齐你的 CSV 列名)
@st.cache_data
def load_data():
    data = pd.read_csv('seattle_crime_small.csv')
    data.columns = data.columns.str.strip() # 去掉列名空格
    data['Report DateTime'] = pd.to_datetime(data['Report DateTime'])
    data['Year'] = data['Report DateTime'].dt.year
    return data

df = load_data()

# 3. 侧边栏控制 (侧边年份和类型选择)
st.sidebar.header("Filter Controls")
years = sorted(df['Year'].unique())
selected_year = st.sidebar.select_slider("Select Year", options=years, value=max(years))

# 这里使用你 CSV 里的真实名字 'Offense Category'
target_col = 'Offense Category' 

crime_options = sorted(df[target_col].unique())
selected_crimes = st.sidebar.multiselect(
    "Select Crime Categories",
    options=crime_options,
    default=crime_options[:5]
)

# 4. 过滤数据
mask = (df['Year'] == selected_year) & (df[target_col].isin(selected_crimes))
filtered_df = df[mask]

# 5. 顶部数字指标
m1, m2, m3 = st.columns(3)
m1.metric("Total Incidents", f"{len(filtered_df):,}")
m2.metric("Active Neighborhoods", filtered_df['Neighborhood'].nunique())
m3.metric("Selected Year", selected_year)

st.divider()

# 6. 图表部分
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("Incident Frequency")
    counts = filtered_df[target_col].value_counts().reset_index()
    fig_bar = px.bar(counts, x=target_col, y='count', color=target_col)
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.subheader("Geographical Distribution")
    fig_map = px.scatter_mapbox(
        filtered_df, 
        lat="Latitude", 
        lon="Longitude",
        color=target_col, 
        hover_name="Offense", # 这里决定了地图点开显示什么
        mapbox_style="carto-positron", 
        zoom=10,
        height=500
    )
    st.plotly_chart(fig_map, use_container_width=True)

# 7. 底层原始数据预览
with st.expander("View Filtered Raw Data"):
    st.dataframe(filtered_df.sort_values('Report DateTime', ascending=False))
