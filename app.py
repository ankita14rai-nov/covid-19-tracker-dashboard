import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="COVID-19 Analytics", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for metric styling
st.markdown("""
    <style>
    div[data-testid="metric-container"] {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🦠 Advanced COVID-19 Data Analytics")

@st.cache_data
def load_and_prep_data():
    df = pd.read_csv("data/owid-covid-data.csv")
    df['date'] = pd.to_datetime(df['date'])
    
    # Calculate 7-day rolling averages for smoother trend lines
    df['new_cases_smoothed'] = df.groupby('location')['new_cases'].transform(lambda x: x.rolling(7, min_periods=1).mean())
    df['new_deaths_smoothed'] = df.groupby('location')['new_deaths'].transform(lambda x: x.rolling(7, min_periods=1).mean())
    return df

df = load_and_prep_data()

# Sidebar Controllers
st.sidebar.header("⚙️ Dashboard Controls")
country_list = df[~df['iso_code'].str.startswith('OWID', na=False)]['location'].dropna().unique().tolist()
country_list.sort()
selected_country = st.sidebar.selectbox("Select Target Country", country_list, index=country_list.index("India"))

# Date range controller covering the entire pandemic
min_date = df['date'].min().date()
max_date = df['date'].max().date()
date_range = st.sidebar.slider("Select Timeline", min_value=min_date, max_value=max_date, value=(min_date, max_date))

# Filter data
country_df = df[(df['location'] == selected_country) & (df['date'].dt.date >= date_range[0]) & (df['date'].dt.date <= date_range[1])]

# UI Layout using Tabs
tab1, tab2, tab3 = st.tabs(["📈 Country Deep Dive", "🌍 Global Overview", "📊 Comparative Analysis"])

with tab1:
    st.subheader(f"Pandemic Timeline: {selected_country}")
    
    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Cases", f"{country_df['total_cases'].max():,.0f}")
    c2.metric("Total Deaths", f"{country_df['total_deaths'].max():,.0f}")
    c3.metric("Peak Daily Cases", f"{country_df['new_cases'].max():,.0f}")
    c4.metric("Total Vaccinations", f"{country_df['total_vaccinations'].max():,.0f}")
    
    st.markdown("---")
    
    # Dual Axis-style overlapping area chart for Cases vs Deaths
    fig_trends = go.Figure()
    fig_trends.add_trace(go.Scatter(x=country_df['date'], y=country_df['new_cases_smoothed'], fill='tozeroy', name='Daily Cases (7d Avg)', line=dict(color='#3366CC')))
    fig_trends.add_trace(go.Scatter(x=country_df['date'], y=country_df['new_deaths_smoothed'], fill='tozeroy', name='Daily Deaths (7d Avg)', line=dict(color='#DC3912'), yaxis='y2'))
    
    fig_trends.update_layout(
        title="Infection Rate vs Mortality Rate",
        hovermode="x unified",
        yaxis=dict(title="Daily Cases", color="#3366CC"),
        yaxis2=dict(title="Daily Deaths", color="#DC3912", overlaying="y", side="right"),
        template="plotly_white"
    )
    st.plotly_chart(fig_trends, use_container_width=True)

with tab2:
    st.subheader("Global Cumulative Impact")
    latest_dates = df.groupby('iso_code')['date'].idxmax()
    map_data = df.loc[latest_dates]
    map_data = map_data[~map_data['iso_code'].str.startswith('OWID', na=False)]
    
    # Advanced Scatter Geo Map
    fig_map = px.scatter_geo(
        map_data, 
        locations="iso_code", 
        color="total_cases",
        hover_name="location", 
        size="total_cases",
        projection="natural earth",
        color_continuous_scale="Plasma",
        title="Global Hotspots (Bubble Size = Total Cases)"
    )
    st.plotly_chart(fig_map, use_container_width=True)

with tab3:
    st.subheader("Top 10 Most Affected Countries")
    top_10 = map_data.nlargest(10, 'total_cases').sort_values('total_cases', ascending=True)
    
    fig_bar = px.bar(
        top_10, 
        x='total_cases', 
        y='location', 
        orientation='h',
        color='total_cases',
        color_continuous_scale='Reds',
        text_auto='.2s',
        title="Highest Cumulative Cases"
    )
    fig_bar.update_layout(template="plotly_white", xaxis_title="Total Cases", yaxis_title="")
    st.plotly_chart(fig_bar, use_container_width=True)