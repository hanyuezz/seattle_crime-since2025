import streamlit as st
import plotly.express as px
import pandas as pd

# 1. 页面配置 (符合作业 Layout 要求)
st.set_page_config(page_title="Seattle Crime Explorer", layout="wide")

st.title("Seattle Crime Data Interactive Explorer (2025-Present)")
st.markdown("This dashboard focuses on recent crime patterns in Seattle (2025-2026).")

# 2. 数据加载 (增加鲁棒性)
@st.cache_data
def load_data():
    data = pd.read_csv('seattle_crime_small.csv')
    # 清理所有列名的首尾空格
    data.columns = data.columns.str.strip() 
    # 转换日期格式
    data['Report DateTime'] = pd.to_datetime(data['Report DateTime'])
    data['Year'] = data['Report DateTime'].dt.year
    return data

df = load_data()

# 3. 侧边栏控制 (符合 Interactive Exploration 要求)
st.sidebar.header("Filter Controls")

# 年份滑动条
years = sorted(df['Year'].unique())
selected_year = st.sidebar.select_slider("Select Year", options=years, value=max(years))

# 犯罪大类筛选 (逻辑：大类用于宏观过滤)
target_col = 'Offense Category' 
crime_options = sorted(df[target_col].unique())
selected_crimes = st.sidebar.multiselect(
    "Select Crime Categories",
    options=crime_options,
    default=crime_options[:5]
)

# 4. 执行过滤
mask = (df['Year'] == selected_year) & (df[target_col].isin(selected_crimes))
filtered_df = df[mask]

# 5. 核心指标 (符合 Metrics 展示要求)
m1, m2, m3 = st.columns(3)
m1.metric("Total Incidents", f"{len(filtered_df):,}")
# 逻辑：展示受影响的社区数量
m2.metric("Active Neighborhoods", filtered_df['Neighborhood'].nunique())
m3.metric("Selected Year", selected_year)

st.divider()

# 6. 图表部分 (符合 Multiple Views 要求)
col_left, col_right = st.columns([1, 1.2])

with col_left:
    st.subheader("Crime Frequency by Category")
    counts = filtered_df[target_col].value_counts().reset_index()
    # 逻辑：柱状图展示各类犯罪的比例
    fig_bar = px.bar(
        counts, x=target_col, y='count', color=target_col,
        template="plotly_white", labels={'count': 'Number of Incidents'}
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.subheader("Geographical Hotspots")
    # 逻辑：地图展示空间分布。颜色代表大类，悬浮显示具体罪名(Offense)
    fig_map = px.scatter_mapbox(
        filtered_df, 
        lat="Latitude", 
        lon="Longitude",
        color=target_col, 
        hover_name="Offense", # 这里决定了细节显示
        hover_data={"Latitude": False, "Longitude": False, "Offense Category": True},
        mapbox_style="carto-positron", 
        zoom=10, height=550
    )
    st.plotly_chart(fig_map, use_container_width=True)

# 7. 原始数据 (符合 Details-on-demand 要求)
with st.expander("Explore Filtered Records (Raw Data)"):
    st.dataframe(filtered_df.sort_values('Report DateTime', ascending=False))
