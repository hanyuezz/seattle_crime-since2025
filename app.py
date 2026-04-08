import streamlit as st
import plotly.express as px
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="Seattle Crime Explorer", layout="wide")

st.title("Seattle Crime Data Interactive Explorer (2025-Present)")
st.markdown("This dashboard focuses on recent crime patterns in Seattle (2025-2026).")

# 2. Load Data
@st.cache_data
def load_data():
    # 读取 CSV
    data = pd.read_csv('seattle_crime_small.csv')
    
    # 强制清理列名两侧可能存在的不可见空格
    data.columns = data.columns.str.strip() 
    
    # 核心转换：使用你 CSV 里的真实列名 'Report DateTime'
    data['Report DateTime'] = pd.to_datetime(data['Report DateTime'])
    data['Year'] = data['Report DateTime'].dt.year
    return data

# 执行加载
df = load_data()

# 3. Sidebar Controls
st.sidebar.header("Filter Controls")

# 年份滑动条
years = sorted(df['Year'].unique())
selected_year = st.sidebar.select_slider("Select Year", options=years, value=max(years))

# 【修正点】使用你确认的列名 'Offense Category'
target_col = 'Offense Category' 

crime_options = sorted(df[target_col].unique())
selected_crimes = st.sidebar.multiselect(
    "Select Crime Categories",
    options=crime_options,
    default=crime_options[:5]
)

# 4. Apply Filters
mask = (df['Year'] == selected_year) & (df[target_col].isin(selected_crimes))
filtered_df = df[mask]

# 5. Key Metrics
m1, m2, m3 = st.columns(3)
m1.metric("Total Incidents", f"{len(filtered_df):,}")
m2.metric("Active Neighborhoods", filtered_df['MCPP'].nunique() if 'MCPP' in filtered_df.columns else "N/A")
m3.metric("Selected Year", selected_year)

st.divider()

# 6. Interactive Charts
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("Incident Frequency")
    counts = filtered_df[target_col].value_counts().reset_index()
    # 柱状图展示
    fig_bar = px.bar(
        counts, x=target_col, y='count', color=target_col,
        template="plotly_white"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.subheader("Geographical Distribution")
    # 【修正点】坐标列名确保为 'Latitude' 和 'Longitude'
    fig_map = px.scatter_mapbox(
        filtered_df, 
        lat="Latitude", 
        lon="Longitude",
        color=target_col, 
        hover_name="Offense", 
        mapbox_style="carto-positron", 
        zoom=10,
        height=500
    )
    st.plotly_chart(fig_map, use_container_width=True)

# 7. Raw Data Table (Details-on-demand)
with st.expander("View Filtered Raw Data"):
    st.dataframe(filtered_df.sort_values('Report DateTime', ascending=False))
