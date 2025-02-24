import pandas as pd
import os
import time
import streamlit as st
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# Ensure Streamlit maintains execution context
st.experimental_set_query_params(refresh="true")

# Get current date and timestamp
ts = time.time()
date = datetime.fromtimestamp(ts).strftime("%d-%m-%Y")

# Auto-refresh every 2 seconds
count = st_autorefresh(interval=2000, key="fizzbuzzcounter")

# Display FizzBuzz Logic
if count % 3 == 0 and count % 5 == 0:
    st.write("FizzBuzz")
elif count % 3 == 0:
    st.write("Fizz")
elif count % 5 == 0:
    st.write("Buzz")
else:
    st.write(f"Count: {count}")

# Attendance CSV File Path
csv_file_path = f"Attendance/Attendance_{date}.csv"

# Ensure CSV exists and read it safely
if os.path.exists(csv_file_path):
    retry = 3  # Number of retry attempts
    for attempt in range(retry):
        try:
            df = pd.read_csv(csv_file_path)

            # Search Filter Input
            search_query = st.text_input("Search Attendance Record:", "")

            # Filter DataFrame based on search query
            if search_query:
                filtered_df = df[df.apply(lambda row: row.astype(str).str.contains(search_query, case=False, na=False).any(), axis=1)]
            else:
                filtered_df = df

            # Display DataFrame
            st.dataframe(filtered_df.style.highlight_max(axis=0))
            break  # Successfully read and displayed the file
        except Exception as e:
            if attempt < retry - 1:
                time.sleep(1)  # Wait and retry
            else:
                st.error(f"Error reading the CSV file: {e}")
else:
    st.warning(f"No attendance record found for {date}.")
