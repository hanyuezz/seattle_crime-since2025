import streamlit as st
import plotly.express as px
import pandas as pd

# 1. 基础配置
st.set_page_config(page_title="Seattle Crime Explorer", layout="wide")
st.title("Seattle Crime Data Interactive Explorer (2025-Present)")

# 2. 增强型数据加载
@st.cache_data
def load_data():
    data = pd.read_csv('seattle_crime_small.csv')
    data.columns = data.columns.str.strip() # 杀掉所有列名空格
    
    # 自动识别时间列
    time_col = [c for c in data.columns if 'Date' in c or 'Time' in c][0]
    data['Report DateTime'] = pd.to_datetime(data[time_col])
    data['Year'] = data['Report DateTime'].dt.year
    return data

df = load_data()

# 3. 自动识别关键列名（解决 KeyError 的大杀器）
# 识别犯罪大类列
cat_col = [c for c in df.columns if 'Category' in c or 'Group' in c][0]
# 识别社区/地区列
hood_col = [c for c in df.columns if c in ['Neighborhood', 'MCPP', 'Precinct', 'Sector']][0]
# 识别具体罪名列
offense_col = [c for c in df.columns if c == 'Offense' or 'Description' in c][0]

# 4. 侧边栏
st.sidebar.header("Filter Controls")
years = sorted(df['Year'].unique())
selected_year = st.sidebar.select_slider("Select Year", options=years, value=max(years))

crime_options = sorted(df[cat_col].unique())
selected_crimes = st.sidebar.multiselect("Select Crime Categories", options=crime_options, default=crime_options[:5])

# 5. 过滤
mask = (df['Year'] == selected_year) & (df[cat_col].isin(selected_crimes))
filtered_df = df[mask]

# 6. 指标展示
m1, m2, m3 = st.columns(3)
m1.metric("Total Incidents", f"{len(filtered_df):,}")
m2.metric("Active Regions", filtered_df[hood_col].nunique())
m3.metric("Selected Year", selected_year)

st.divider()

# 7. 图表部分
col_left, col_right = st.columns([1, 1.2])

with col_left:
    st.subheader("Crime Frequency")
    counts = filtered_df[cat_col].value_counts().reset_index()
    fig_bar = px.bar(counts, x=cat_col, y='count', color=cat_col, template="plotly_white")
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.subheader("Geographical Distribution")
    fig_map = px.scatter_mapbox(
        filtered_df, lat="Latitude", lon="Longitude",
        color=cat_col, hover_name=offense_col,
        mapbox_style="carto-positron", zoom=10, height=550
    )
    st.plotly_chart(fig_map, use_container_width=True)

# 8. 原始数据
with st.expander("View Raw Data"):
    st.dataframe(filtered_df.sort_values('Report DateTime', ascending=False))
