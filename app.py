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
    data = pd.read_csv('seattle_crime_small.csv')
    # 清理列名空格
    data.columns = data.columns.str.strip() 
    # 转换时间列 (对应你 CSV 里的 REPORT_DATETIME)
    data['REPORT_DATETIME'] = pd.to_datetime(data['REPORT_DATETIME'])
    data['Year'] = data['REPORT_DATETIME'].dt.year
    return data

df = load_data()

# 3. Sidebar Controls
st.sidebar.header("Filter Controls")

# 年份选择
years = sorted(df['Year'].unique())
selected_year = st.sidebar.select_slider("Select Year", options=years, value=max(years))

# 【关键点】犯罪类别列名改为 OFFENSE_CATEGORY
target_col = 'OFFENSE_CATEGORY' 

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
    # 注意：plotly 的 x 和 y 也要对应新列名
    fig_bar = px.bar(
        counts, x=target_col, y='count', color=target_col,
        template="plotly_white"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.subheader("Geographical Distribution")
    # 【关键点】坐标列名改为 LATITUDE 和 LONGITUDE
    fig_map = px.scatter_mapbox(
        filtered_df, 
        lat="LATITUDE", 
        lon="LONGITUDE",
        color=target_col, 
        hover_name="OFFENSE", 
        mapbox_style="carto-positron", 
        zoom=10,
        height=500
    )
    st.plotly_chart(fig_map, use_container_width=True)

# 7. Raw Data Table
with st.expander("View Filtered Raw Data"):
    st.dataframe(filtered_df.sort_values('REPORT_DATETIME', ascending=False))
