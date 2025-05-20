import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
from datetime import datetime
import glob
import os
# Set page config must be the first Streamlit command
st.set_page_config(page_title="Booking.com Crawler", layout="wide")


def clean_price(price_series):
    """Helper function to clean price data"""
    return (
        price_series
        .str.replace(r'[^\d.]', '', regex=True)
        .replace('', np.nan)
        .dropna()
        .astype(float)
    )


def clean_score(score_series):
    """Helper function to clean score data"""
    return (
        score_series
        .str.extract(r'(\d+\.\d+)')[0]
        .replace('', np.nan)
        .dropna()
        .astype(float)
    )


# Replace the load_latest_data function in app.py with:
def load_latest_data():
    """Load the most recent hotels data file with proper error handling"""
    try:
        # Find all matching files
        files = glob.glob("hotels_data_*.csv")
        if not files:
            st.warning("No hotel data files found. Please run the crawler first.")
            return None

        # Get the most recent file by modification time
        latest_file = max(files, key=os.path.getmtime)
        st.info(f"Loading data from: {latest_file}")

        # Try different encodings if needed
        try:
            df = pd.read_csv(latest_file, encoding='utf-8')
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(latest_file, encoding='latin1')
            except Exception as e:
                st.error(f"Failed to read CSV file: {str(e)}")
                return None

        # Ensure required columns exist
        if 'price' in df.columns and 'price_numeric' not in df.columns:
            df['price_numeric'] = clean_price(df['price'])
        if 'score' in df.columns and 'score_clean' not in df.columns:
            df['score_clean'] = clean_score(df['score'])

        # Check if facilities column exists
        if 'facilities' not in df.columns:
            st.warning("Facilities data not found in the CSV file. The scraper may need to be updated.")
            df['facilities'] = "No data available"  # Add placeholder

        return df

    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None


def create_dashboard(data):
    def create_dashboard(data):
        st.title("🏨 Booking.com Data Crawler")

        # Debug info
        st.write(f"Data shape: {data.shape}")
        st.write("Columns available:", data.columns.tolist())

        # Check if we have valid data
        if data.empty:
            st.warning("No hotel data available. Please run the crawler first.")
            return

        # Ensure required columns exist
        if 'price_numeric' not in data.columns:
            data['price_numeric'] = clean_price(data['price'])
        if 'score_clean' not in data.columns:
            data['score_clean'] = clean_score(data['score'])
        if 'facilities' not in data.columns:
            data['facilities'] = "No data available"

    # Sidebar filters
    st.sidebar.header("Filters")

    # Get min/max values for filters
    min_price, max_price = float(data['price_numeric'].min()), float(data['price_numeric'].max())
    min_score, max_score = float(data['score_clean'].min()), float(data['score_clean'].max())

    # Create filters
    price_range = st.sidebar.slider(
        "Price Range",
        min_value=min_price,
        max_value=max_price,
        value=(min_price, max_price))

    score_range = st.sidebar.slider(
        "Review Score Range",
        min_value=min_score,
        max_value=max_score,
        value=(min_score, max_score))

    # Apply filters
    filtered_data = data[
        (data['price_numeric'] >= price_range[0]) &
        (data['price_numeric'] <= price_range[1]) &
        (data['score_clean'] >= score_range[0]) &
        (data['score_clean'] <= score_range[1])
        ]

    # Main content - Data Table
    st.header("📊 Hotel Data Table")
    st.dataframe(filtered_data.style.format({
        'price_numeric': '${:.2f}',
        'score_clean': '{:.1f}'
    }), height=600)

    # Visualizations Section
    st.header("📈 Data Visualizations")

    # First row of charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Price Distribution")
        try:
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.hist(filtered_data['price_numeric'], bins=20, color='skyblue', edgecolor='black')
            ax.set_xlabel('Price ($)')
            ax.set_ylabel('Count')
            ax.set_title('Price Distribution')
            st.pyplot(fig)
            plt.close()
        except Exception as e:
            st.error(f"Could not create price distribution: {str(e)}")
            st.write("Price data sample:", filtered_data['price_numeric'].head())

    with col2:
        st.subheader("Review Score Distribution")
        try:
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.hist(filtered_data['score_clean'], bins=np.arange(0, 10.5, 0.5), color='lightgreen', edgecolor='black')
            ax.set_xlabel('Review Score')
            ax.set_ylabel('Count')
            ax.set_title('Review Score Distribution')
            ax.set_xticks(np.arange(0, 10.5, 1))
            st.pyplot(fig)
            plt.close()
        except Exception as e:
            st.error(f"Could not create score distribution: {str(e)}")
            st.write("Score data sample:", filtered_data['score_clean'].head())

    # Second row of charts
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Price vs. Rating")
        try:
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.scatter(filtered_data['price_numeric'], filtered_data['score_clean'], alpha=0.6)
            ax.set_xlabel('Price ($)')
            ax.set_ylabel('Review Score')
            ax.set_title('Price vs. Rating')

            # Add simple linear regression line
            if len(filtered_data) > 1:
                x = filtered_data['price_numeric']
                y = filtered_data['score_clean']
                m, b = np.polyfit(x, y, 1)
                ax.plot(x, m * x + b, color='red')

            st.pyplot(fig)
            plt.close()
        except Exception as e:
            st.error(f"Could not create scatter plot: {str(e)}")
            st.write("Data sample:", filtered_data[['price_numeric', 'score_clean']].head())

    # In the facilities analysis section (around line 150), replace with:
    with col4:
        st.subheader("Facilities Analysis")
        if 'facilities' in filtered_data.columns:
            try:
                # Convert all facilities to string and clean
                filtered_data['facilities'] = filtered_data['facilities'].astype(str)

                # Remove "No facilities listed" and empty entries
                facilities_data = filtered_data[
                    (~filtered_data['facilities'].str.contains('No facilities listed')) &
                    (filtered_data['facilities'] != 'nan') &
                    (filtered_data['facilities'] != '')
                    ]

                if len(facilities_data) > 0:
                    # Split and count facilities
                    all_facilities = facilities_data['facilities'].str.split(',\s*').explode()
                    facility_counts = all_facilities.value_counts().head(10)

                    if len(facility_counts) > 0:
                        fig = px.bar(
                            facility_counts,
                            orientation='h',
                            labels={'index': 'Facility', 'value': 'Count'},
                            title='Top 10 Facilities'
                        )
                        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("No facilities data available after processing")
                else:
                    st.warning("No hotels with listed facilities found")
            except Exception as e:
                st.error(f"Could not create facilities analysis: {str(e)}")
                st.write("Facilities data sample:", filtered_data['facilities'].head())
        else:
            st.warning("Facilities data not available in this dataset")

    # Metrics Section
    st.header("📊 Key Metrics")
    mcol1, mcol2, mcol3, mcol4 = st.columns(4)
    mcol1.metric("Total Hotels", len(filtered_data))
    mcol2.metric("Average Price", f"${filtered_data['price_numeric'].mean():.2f}")
    mcol3.metric("Average Rating", f"{filtered_data['score_clean'].mean():.1f}/10")
    mcol4.metric("Highest Rated", filtered_data.loc[filtered_data['score_clean'].idxmax()]['name'])

    # Download button
    st.download_button(
        label="Download Filtered Data as CSV",
        data=filtered_data.to_csv(index=False),
        file_name=f"filtered_hotels_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )


if __name__ == "__main__":
    # Load the data
    data = load_latest_data()

    if data is None:
        # Create dummy data if no file found
        data = pd.DataFrame({
            'name': ['Hotel A', 'Hotel B', 'Hotel C'],
            'price': ['$100', '$150', '$200'],
            'score': ['8.5/10', '9.0/10', '7.8/10'],
            'location': ['Location A', 'Location B', 'Location C'],
            'price_numeric': [100, 150, 200],
            'score_clean': [8.5, 9.0, 7.8],
            'facilities': ['Free WiFi, Pool', 'Free WiFi, Parking', 'Restaurant, Bar']
        })
        st.warning("No hotel data file found. Showing sample data.")

    # Clean the data if needed
    if not data.empty:
        if 'price' in data.columns and 'price_numeric' not in data.columns:
            data['price_numeric'] = clean_price(data['price'])
        if 'score' in data.columns and 'score_clean' not in data.columns:
            data['score_clean'] = clean_score(data['score'])

    create_dashboard(data)