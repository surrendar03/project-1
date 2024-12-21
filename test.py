import streamlit as st
import pandas as pd
import pymysql
from datetime import time

# Streamlit app title
st.set_page_config(page_title="Redbus Ticket Booking", layout="wide")

# Background color and header customization
st.markdown(
    """
    <style>
    body {
        background-color: #f0f0f5;
    }
    .title {
        color: #d32f2f;
        font-size: 36px;
        font-family: 'Helvetica', sans-serif;
        font-weight: bold;
    }
    .subtitle {
        color: #1976d2;
        font-size: 24px;
        font-family: 'Arial', sans-serif;
    }
    .stButton>button {
        background-color: #1976d2;
        color: white;
        font-size: 18px;
        padding: 10px 20px;
        border-radius: 5px;
    }
    .stSelectbox>div>div>input {
        font-size: 16px;
    }
    .stSlider>div>div>div {
        font-size: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Title and description
st.image('C:/Users/M.SUDHARASAN/Downloads/220px-Redbus_logo.jpg', width=200)
st.markdown('<p class="title">BOOK BUS TICKETS ANYWHERE IN THE WORLD WITH <b>REDBUS</b></p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Find buses based on your preferences</p>', unsafe_allow_html=True)
st.markdown("[Click here to visit Redbus](https://www.redbus.in/)", unsafe_allow_html=True)

# Database connection
try:
    connection = pymysql.connect(
        host="localhost",
        user="root",
        password="@surrendar2003",
        database="red_bus",
        autocommit=True
    )
    st.success("Connected to the database successfully!", icon="✅")
except Exception as e:
    st.error(f"Failed to connect to the database: {e}", icon="❌")
    st.stop()

# Create a cursor
cursor = connection.cursor()

# User input for state name, bus fare, ratings, and starting time
state_name = st.selectbox("Enter State Name:", [
    "andhra", "assam", "bihar", "chandigarh", "himachalpradesh", "jammukashmir",
    "punjab", "rajasthan", "southbengal", "westbengal"
])

if state_name:
    sql = "SELECT DISTINCT name FROM redbus WHERE state_name = %s"
    cursor.execute(sql, (state_name,))
    route_name = cursor.fetchall()

    # Convert the list of tuples into a list of strings (route names)
    route_names_list = [route[0] for route in route_name]

    # Ensure that the list is not empty before displaying the selectbox
    if route_names_list:
        name_route = st.selectbox("Select a Route", route_names_list)
    else:
        st.warning("No routes found for the selected state.", icon="⚠️")

Bus_fare = st.slider("Select Maximum Fare:", min_value=60, max_value=10000, step=50)
Ratings = st.slider("Select Minimum Ratings:", min_value=1.1, max_value=5.0, step=0.1)

# Using time objects to set the starting and ending times
start_time = time(0, 5)  # 00:05:00
end_time = time(23, 59)  # 23:59:00

Starting_time = st.slider(
    "Starting Time:",
    min_value=start_time,
    max_value=end_time,
    value=start_time
)

# Convert starting time to string format (HH:MM:SS)
starting_time_str = Starting_time.strftime('%H:%M:%S')

# Check if input is provided
if st.button("Search"):
    # Modify the SQL query to include Bus_fare, Ratings, and Starting_time as filters
    query = """
        SELECT * 
        FROM redbus 
        WHERE state_name = %s 
        AND name = %s
        AND Bus_fare <= %s 
        AND Ratings >= %s 
        AND TIME(Starting_time) >= %s
        ORDER BY Bus_fare ASC
    """

    try:
        # Execute the query with user inputs
        cursor.execute(query, (state_name, name_route, Bus_fare, Ratings, starting_time_str))
        results = cursor.fetchall()

        # Display results in a table format
        if results:
            # Create a DataFrame to display in Streamlit
            df = pd.DataFrame(results, columns=[desc[0] for desc in cursor.description])
            st.dataframe(df)
        else:
            st.warning("No results found for the given criteria.", icon="⚠️")
    except Exception as e:
        st.error(f"An error occurred while fetching data: {e}", icon="❌")

# Close the cursor and connection
cursor.close()
connection.close()


