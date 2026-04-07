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
    # 读取文件
    data = pd.read_csv('seattle_crime_small.csv')
    
    # 【核心修复 1】强制清理所有列名的空格，防止 KeyError
    data.columns = data.columns.str.strip() 
    
    # 转换时间
    data['Report DateTime'] = pd.to_datetime(data['Report DateTime'])
    data['Year'] = data['Report DateTime'].dt.year
    return data

# 【核心修复 2】在函数外部执行，确保变量 df 被定义
df = load_data()

# --- 调试工具：如果在网页看到这行，请告诉我括号里具体显示了什么 ---
# st.write("Current Columns:", df.columns.tolist())

# 3. Sidebar Controls
st.sidebar.header("Filter Controls")

# Year Slider
years = sorted(df['Year'].unique())
selected_year = st.sidebar.select_slider(
    "Select Year", 
    options=years, 
    value=max(years)
)

# 【核心修复 3】使用更健壮的方式获取犯罪类型列
# 如果列名不对，这里会报错，请根据调试工具显示的名称修改
target_col = 'Offense Parent Group' 

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
    fig_bar = px.bar(
        counts, x=target_col, y='count', color=target_col,
        template="plotly_white"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.subheader("Geographical Distribution")
    fig_map = px.scatter_mapbox(
        filtered_df, lat="Latitude", lon="Longitude",
        color=target_col, hover_name="Offense", 
        mapbox_style="carto-positron", zoom=10
    )
    st.plotly_chart(fig_map, use_container_width=True)

# 7. Raw Data Table
with st.expander("View Filtered Raw Data"):
    st.dataframe(filtered_df.sort_values('Report DateTime', ascending=False))
