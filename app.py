import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates

# Load dataset
@st.cache_data
def load_data():
    df = pd.read_csv("worldometer_coronavirus_daily_data.csv")
    return df

df = load_data()

# Convert date column once
df["date"] = pd.to_datetime(df["date"], errors="coerce")

# Sidebar options
st.sidebar.title("COVID-19 Dashboard")
view_option = st.sidebar.radio(
    "Select View",
    ["Daily Records", "Country Summary"]
)

st.title("🌍 COVID-19 Data Visualization Dashboard")

# Daily Records View
if view_option == "Daily Records":

    st.subheader("Daily Trends by Country")

    # Country selector
    country = st.sidebar.selectbox(
        "Select Country",
        sorted(df["country"].dropna().unique())
    )

    # Filter country data
    country_data = df[df["country"] == country].copy()

    # Create year column
    country_data["year"] = country_data["date"].dt.year

    # Yearly summary
    yearly_data = (
        country_data.groupby("year")[["daily_new_cases", "daily_new_deaths"]]
        .sum()
        .reset_index()
    )

    # Yearly chart
    st.subheader("Yearly Cases & Deaths")
    yearly_chart_data = (
        yearly_data.sort_values("year")
        .set_index("year")[["daily_new_cases", "daily_new_deaths"]]
    )
    st.line_chart(yearly_chart_data)

    # Daily chart
    st.subheader("Daily Cases & Deaths")
    daily_chart_data = (
        country_data.sort_values("date")
        .set_index("date")[["daily_new_cases", "daily_new_deaths"]]
    )
    st.line_chart(daily_chart_data)

    # Bar chart for last 30 days
    st.subheader("Last 30 Days - Daily New Cases")
    last_30 = country_data.sort_values("date").tail(30)
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.barplot(
        x=last_30["date"].dt.strftime("%Y-%m-%d"),
        y=last_30["daily_new_cases"],
        ax=ax,
        palette="Blues_d"
    )
    plt.xticks(rotation=45)
    plt.xlabel("Date")
    plt.ylabel("Daily New Cases")
    st.pyplot(fig)

    # Stacked bar chart (cases vs deaths per year)
    st.subheader("Stacked Bar Chart - Yearly Cases vs Deaths")
    fig, ax = plt.subplots(figsize=(8, 5))
    yearly_data.set_index("year").plot(kind="bar", stacked=True, ax=ax, color=["skyblue", "salmon"])
    plt.ylabel("Total Count")
    st.pyplot(fig)

    # Pie chart (proportion of cases vs deaths in selected country)
    st.subheader("Pie Chart - Cases vs Deaths")
    totals = [
        country_data["daily_new_cases"].sum(),
        country_data["daily_new_deaths"].sum()
    ]
    labels = ["Cases", "Deaths"]
    fig, ax = plt.subplots()
    ax.pie(totals, labels=labels, autopct="%1.1f%%", colors=["lightblue", "red"])
    st.pyplot(fig)

    # Heatmap of monthly cases by year
    st.subheader("Heatmap - Monthly Cases")
    country_data["month"] = country_data["date"].dt.month
    monthly_data = (
        country_data.groupby(["year", "month"])["daily_new_cases"]
        .sum()
        .unstack(fill_value=0)
    )
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(monthly_data, cmap="YlGnBu", annot=True, fmt=".0f", ax=ax)
    plt.xlabel("Month")
    plt.ylabel("Year")
    st.pyplot(fig)

    # Scatter plot (cases vs deaths)
    st.subheader("Scatter Plot - Cases vs Deaths")
    fig, ax = plt.subplots()
    sns.scatterplot(
        x=country_data["daily_new_cases"],
        y=country_data["daily_new_deaths"],
        alpha=0.5,
        ax=ax
    )
    plt.xlabel("Daily New Cases")
    plt.ylabel("Daily New Deaths")
    st.pyplot(fig)

    # Raw data preview (only selected country)
    st.subheader("Raw Data Preview")
    st.dataframe(country_data.head(20))

# Country Summary View
else:

    # Sidebar components for summary
    selected_countries = st.sidebar.multiselect(
        "Select countries to compare",
        df["country"].unique(),
        default=["India", "USA"]
    )
    show_top = st.sidebar.slider("Number of top countries to display", min_value=5, max_value=20, value=10)
    show_deaths_line = st.sidebar.checkbox("Show Deaths Line in Comparison", value=True)

    st.subheader("Country-wise Summary")

    # Line chart comparing selected countries by total cases (and deaths if checkbox enabled)
    st.subheader("Comparison of Countries - Total Cases")
    fig, ax = plt.subplots(figsize=(12, 6))
    for country in selected_countries:
        subset = df[df["country"] == country].sort_values("date")
        ax.plot(subset["date"], subset["cumulative_total_cases"], label=f"{country} Cases", linewidth=2)
        if show_deaths_line:
            ax.plot(subset["date"], subset["cumulative_total_deaths"], label=f"{country} Deaths", linestyle="--")
    plt.xlabel("Date")
    plt.ylabel("Cumulative Count")
    plt.legend()
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # Top countries by cases (connected to slider, descending order)
    top_cases = (
        df.groupby("country")["cumulative_total_cases"]
        .max()
        .sort_values(ascending=False)   # ensure descending order
        .head(show_top)
    )
    st.subheader(f"Top {show_top} Countries by Cases")
    st.bar_chart(top_cases.to_frame().sort_values("cumulative_total_cases", ascending=False))
    
    # Top countries by deaths (connected to slider, descending order)
    top_deaths = (
        df.groupby("country")["cumulative_total_deaths"]
        .max()
        .sort_values(ascending=False)   # ensure descending order
        .head(show_top)
    )
    st.subheader(f"Top {show_top} Countries by Deaths")
    st.bar_chart(top_deaths.to_frame().sort_values("cumulative_total_deaths", ascending=False))


    # Scatter Plot - Cases vs Deaths (unchanged)
    st.subheader("Scatter Plot - Cases vs Deaths")
    summary_data = df.groupby("country")[["cumulative_total_cases", "cumulative_total_deaths"]].max().reset_index()
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(
        data=summary_data,
        x="cumulative_total_cases",
        y="cumulative_total_deaths",
        color="blue",
        alpha=0.6,
        ax=ax
    )
    plt.xlabel("Total Cases")
    plt.ylabel("Total Deaths")
    st.pyplot(fig)

    # Pie Chart - Proportion of Cases by Top 5 Countries (unchanged)
    st.subheader("Pie Chart - Top 5 Countries by Cases")
    top5_cases = top_cases.head(5)
    fig, ax = plt.subplots()
    ax.pie(top5_cases, labels=top5_cases.index, autopct="%1.1f%%", startangle=90)
    st.pyplot(fig)

    # Continent-level breakdown (unchanged)
    if "continent" in df.columns:
        st.subheader("Continent-wise Cases")
        continent_cases = df.groupby("continent")["cumulative_total_cases"].max().sort_values(ascending=False)
        st.bar_chart(continent_cases)

    # Growth trend (unchanged)
    st.subheader("Growth Trend - Top Country")
    top_country = top_cases.index[0]
    top_country_data = df[df["country"] == top_country].sort_values("date").copy()
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(top_country_data["date"], top_country_data["cumulative_total_cases"], label="Cases", color="blue")
    ax.plot(top_country_data["date"], top_country_data["cumulative_total_deaths"], label="Deaths", color="red")
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.xticks(rotation=45)
    plt.legend()
    st.pyplot(fig)

    # Bubble chart (unchanged)
    if {"population", "cumulative_total_cases", "cumulative_total_deaths"}.issubset(df.columns):
        st.subheader("Bubble Chart - Cases vs Deaths vs Population")
        merged = summary_data.merge(df[["country", "population"]].drop_duplicates(), on="country")
        fig, ax = plt.subplots()
        sns.scatterplot(
            data=merged,
            x="cumulative_total_cases",
            y="cumulative_total_deaths",
            size="population",
            alpha=0.6,
            ax=ax,
            legend=False
        )
        plt.xlabel("Total Cases")
        plt.ylabel("Total Deaths")
        st.pyplot(fig)

    # Map (unchanged)
    if {"Lat", "Long"}.issubset(df.columns):
        map_data = df[["Lat", "Long"]].dropna()
        st.subheader("Map View")
        st.map(map_data)

    # Raw data preview (unchanged)
    st.subheader("Raw Data Preview")
    st.dataframe(df.head(20))
