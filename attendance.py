import streamlit as st
import datetime

from utils import ScrapeData, ProcessData

st.title("Attendance Scraper")

# Initialize session state variables if not already set
if 'username' not in st.session_state:
    st.session_state.username = None
if 'password' not in st.session_state:
    st.session_state.password = None
if 'internetlevel' not in st.session_state:
    st.session_state.internetlevel = None

# User input fields
temp_username = st.sidebar.text_input("Enter your Username")
temp_pass = st.sidebar.text_input("Enter your password", type="password")
temp_il = st.sidebar.slider("Internet Speed", 0, 5, 5)

# Sign-in button logic
if st.sidebar.button('Sign In'):
    if temp_username and temp_pass and temp_il:
        st.session_state.username = temp_username
        st.session_state.password = temp_pass
        st.session_state.internetlevel = temp_il
        st.sidebar.success("You have successfully signed in")

# Main functionality
if st.session_state.username and st.session_state.password and st.session_state.internetlevel:
    startdate = st.date_input(label="Start Date. Defaults to 2024-01-01", value=datetime.date.today().replace(month=1, day=1))
    enddate = st.date_input(label="End Date. Defaults to latest date")

    if st.button('Scrape Data'):
        try:
            df = ScrapeData(st.session_state.username, st.session_state.password, st.session_state.internetlevel)
            ret = ProcessData(df, startdate, enddate)
            st.success(f"Your average attendance is {ret[0]}")
            st.write("Your subject wise attendance is:")
            st.write(ret[1])
        except Exception as e:
            st.error(f"An error occurred: {e}")
