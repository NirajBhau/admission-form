import streamlit as st
import pyodbc
from datetime import datetime
from twilio.rest import Client
import random
import pandas as pd

# Twilio credentials (replace with your actual credentials)
TWILIO_ACCOUNT_SID = 'AC2c5d74e8b6e15f0a25efc95ec5f9d252'
TWILIO_AUTH_TOKEN = '5f20922f0fbfafd611e6bbbbdaf3125c'
TWILIO_PHONE_NUMBER = '+13344686964'

# Initialize Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Function to send OTP via SMS
def send_otp(phone_number, otp):
    message = client.messages.create(
        body=f"Your OTP code is {otp}",
        from_=TWILIO_PHONE_NUMBER,
        to=phone_number
    )
    return message.sid

# Function to connect to MSSQL database
def get_db_connection():
    conn_str = (
        r'DRIVER={ODBC Driver 17 for SQL Server};'
        r'SERVER=DESKTOP-CEIB8QQ\NIRAJ;'  # Replace with your server name
        r'DATABASE=Admins;'  # Replace with your database name
        r'TRUSTED_CONNECTION=yes;'
    )
    conn = pyodbc.connect(conn_str)
    return conn

# Function to save form data to MSSQL database
def save_to_db(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    insert_query = """
        INSERT INTO AdmissionForm (Name, Email, Phone, DateOfBirth, Gender, Address, Course)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    cursor.execute(insert_query, (data['Name'], data['Email'], data['Phone'], data['Date of Birth'], data['Gender'], data['Address'], data['Course']))
    conn.commit()
    conn.close()


# Function to save form data to an Excel file
def save_to_excel(data):
    # Define the file path
    file_path = 'admission_data.xlsx'
    
    # Create a DataFrame
    df = pd.DataFrame([data])
    
    try:
        # Load existing data if the file exists
        existing_df = pd.read_excel(file_path)
        # Append new data
        df = pd.concat([existing_df, df], ignore_index=True)
    except FileNotFoundError:
        # File does not exist, will be created
        pass

    # Save the DataFrame to Excel
    df.to_excel(file_path, index=False, engine='openpyxl')

# Streamlit application
def main():
    st.title("Admission Form")

    if 'otp_sent' not in st.session_state:
        st.session_state['otp_sent'] = None
        st.session_state['phone_number'] = None

    with st.form(key='admission_form'):
        # Form fields
        name = st.text_input("Full Name")
        email = st.text_input("Email Address")
        phone = st.text_input("Phone Number", max_chars=10)
        dob = st.date_input("Date of Birth", min_value=datetime(1900, 1, 1), max_value=datetime.today())
        gender = st.selectbox("Gender", ["Select", "Male", "Female", "Other"])
        address = st.text_area("Address")
        course = st.selectbox("Course Applying For", ["Select", "Computer Science", "Mathematics", "Physics", "Biology"])
        
        otp_input = st.text_input("Enter OTP (if sent)", "")

        # Button for sending OTP
        send_otp_button = st.form_submit_button("Send OTP")
        # Button for submitting the form
        submit_button = st.form_submit_button("Submit")

        if send_otp_button:
            if not name or not email or not phone or not gender or not address or not course:
                st.error("Please fill in all the fields.")
            elif len(phone) != 10:
                st.error("Please enter a valid 10-digit phone number.")
            else:
                otp = random.randint(1000, 9999)
                st.session_state['otp_sent'] = otp
                st.session_state['phone_number'] = phone
                send_otp(f"+91{phone}", otp)
                st.info("OTP sent to your phone number. Please enter the OTP to complete the submission.")

        if submit_button:
            if st.session_state['otp_sent']:
                if otp_input:
                    if int(otp_input) == st.session_state.get('otp_sent'):
                        form_data = {
                            "Name": name,
                            "Email": email,
                            "Phone": phone,
                            "Date of Birth": dob,
                            "Gender": gender,
                            "Address": address,
                            "Course": course
                        }
                        save_to_db(form_data)
                        st.success("Admission form submitted successfully!")
                    else:
                        st.error("Invalid OTP. Please try again.")
                else:
                    st.error("Please enter the OTP sent to your phone number.")
            else:
                st.error("Please send the OTP first.")

if __name__ == "__main__":
    main()
