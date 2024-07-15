import streamlit as st
import pandas as pd
import plotly.express as px
from pymongo import MongoClient
from datetime import datetime
from streamlit_option_menu import option_menu

# MongoDB connection
client = MongoClient('mongodb+srv://ayushsinghbhilai29:Ayush2002@ayush29.itlapyc.mongodb.net/?retryWrites=true&w=majority&appName=Ayush29')
db = client['db']



# Streamlit app layout
st.set_page_config(layout="wide")

# Custom CSS for dark blue background
st.markdown(
    """
    <style>
    .stApp {
        background-color: #001f3f;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

with st.sidebar:
    selected = option_menu(
        menu_title="User Analytics Dashboard",
        options=["Add Organization", "Add Record", "Charts"],
        icons=["building", "file-earmark", "bar-chart"],
        menu_icon="cast",
        default_index=0,
    )

if selected == "Add Organization":
    st.title("Add Organization")
    orgID = st.text_input("Organization ID")
    joinDate = st.date_input("Join Date")
    last_login = st.date_input("Last Login Date")

    if st.button("Add Organization"):
        if orgID:
            org_data = {
                "orgID": orgID,
                "joinDate": joinDate.strftime('%Y-%m-%d %H:%M:%S'),
                "last_login": last_login.strftime('%Y-%m-%d %H:%M:%S')
            }
            db.organizations.insert_one(org_data)
            st.success(f"Organization {orgID} added successfully!")
        else:
            st.error("Organization ID is required!")

elif selected == "Add Record":
    st.title("Add Record")
    recordID = st.text_input("Record ID")
    record_orgID = st.text_input("Organization ID for Record")
    timestamp = st.date_input("Timestamp")
    status = st.selectbox("Status", ["ERROR", "SUCCESS", "PROCESSING"])

    if st.button("Add Record"):
        if recordID and record_orgID:
            rec_data = {
                "recordID": recordID,
                "orgID": record_orgID,
                "timestamp": timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                "status": status
            }
            db.records.insert_one(rec_data)
            st.success(f"Record {recordID} added successfully!")
        else:
            st.error("Record ID and Organization ID are required!")

elif selected == "Charts":
    st.title("Charts")

     # Fetch data from MongoDB for Records and Organizations
    records = db.records.find()
    rec_df = pd.DataFrame(list(records))
    organizations = db.organizations.find()
    org_df = pd.DataFrame(list(organizations))

    # Ensure the timestamp fields are in datetime format for records
    rec_df['timestamp'] = pd.to_datetime(rec_df['timestamp'])

    # Data Transformation for Daily Total Files Processed
    daily_files = rec_df.groupby(rec_df['timestamp'].dt.date).size().reset_index(name='daily_total')

    # Create line chart with Plotly
    fig_line = px.line(daily_files, x='timestamp', y='daily_total', title='Daily Total Files Processed')

    # Data Transformation for Periodic Record Status
    rec_df['date'] = rec_df['timestamp'].dt.date
    status_counts = rec_df.groupby(['date', 'status']).size().unstack(fill_value=0).reset_index()

    # Ensure all status types are included
    status_counts = status_counts.reindex(columns=['date', 'ERROR', 'SUCCESS', 'PROCESSING'], fill_value=0)

    # Melt the DataFrame for Plotly
    melted_periodic_status = status_counts.melt(id_vars='date', value_vars=['ERROR', 'SUCCESS', 'PROCESSING'], var_name='status', value_name='count')

    # Create stacked bar chart with Plotly
    fig_bar = px.bar(melted_periodic_status, x='date', y='count', color='status', title='Periodic Record Status', labels={'date': 'Date', 'count': 'Record Count'})

    # Ensure the last_login fields are in datetime format for organizations
    org_df['last_login'] = pd.to_datetime(org_df['last_login'])

    # Data Transformation for User Activity
    user_activity = org_df.groupby(org_df['last_login'].dt.date).size().reset_index(name='login_count')

    # Create user activity graph with Plotly
    fig_user_activity = px.line(user_activity, x='last_login', y='login_count', title='User Activity (Logins)', labels={'last_login': 'Date', 'login_count': 'Login Count'})

    # Display the charts
    st.plotly_chart(fig_line)
    st.plotly_chart(fig_bar)
    st.plotly_chart(fig_user_activity)
