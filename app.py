import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="COVID-19 Tracker", layout="wide")

# 2. Dashboard Title & Subtitle
st.title("🦠 COVID-19 Global Tracker Dashboard")
st.markdown("This dashboard tracks COVID-19 cases, deaths, and vaccinations across the globe.")

# 3. Load Data (Cached for performance)
@st.cache_data
def load_data():
    df = pd.read_csv("data/owid-covid-data.csv")
    df['date'] = pd.to_datetime(df['date'])
    return df

df = load_data()

# 4. Sidebar for Country Selection
st.sidebar.header("🔍 Filter Data")
country_list = df['location'].dropna().unique().tolist()
country_list.sort()
selected_country = st.sidebar.selectbox("Select a Country", country_list, index=country_list.index("India"))

# Filter data based on selected country
filtered_df = df[df['location'] == selected_country]

# 5. Key Performance Indicators (KPIs)
st.markdown("---")
st.subheader(f"📊 Current Statistics for {selected_country}")

total_cases = filtered_df['total_cases'].fillna(0).max()
total_deaths = filtered_df['total_deaths'].fillna(0).max()
total_vaccines = filtered_df['total_vaccinations'].fillna(0).max()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Cases", f"{total_cases:,.0f}")
with col2:
    st.metric("Total Deaths", f"{total_deaths:,.0f}")
with col3:
    st.metric("Total Vaccinations", f"{total_vaccines:,.0f}")

# 6. Interactive Trend Charts (Side-by-Side)
st.markdown("---")
st.subheader(f"📈 COVID-19 Trends in {selected_country}")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    fig_cases = px.line(
        filtered_df, 
        x='date', 
        y='new_cases', 
        title=f"Daily New Cases in {selected_country}",
        labels={'date': 'Date', 'new_cases': 'New Cases'}
    )
    st.plotly_chart(fig_cases, use_container_width=True)

with chart_col2:
    fig_deaths = px.line(
        filtered_df, 
        x='date', 
        y='new_deaths', 
        title=f"Daily New Deaths in {selected_country}",
        labels={'date': 'Date', 'new_deaths': 'New Deaths'},
        color_discrete_sequence=['#ff4b4b']
    )
    st.plotly_chart(fig_deaths, use_container_width=True)

# 7. Global Heatmap Visualization
st.markdown("---")
st.subheader("🌍 Global COVID-19 Spread (Total Cases)")

# Get the most recent date's data for each country
latest_dates = df.groupby('iso_code')['date'].idxmax()
map_data = df.loc[latest_dates]

# Filter out aggregate regions (like 'World', 'Asia' which start with 'OWID')
# We use na=False to prevent errors if there are missing iso_codes
map_data = map_data[~map_data['iso_code'].str.startswith('OWID', na=False)]

fig_map = px.choropleth(
    map_data,
    locations="iso_code",
    color="total_cases",
    hover_name="location",
    color_continuous_scale="Reds",
    title="Cumulative Total Cases Worldwide"
)

st.plotly_chart(fig_map, use_container_width=True)