import streamlit as st
import requests
API_URL = "http://localhost:8000/predict"

st.title("Insurance Premium category Predictior")

st.markdown("Enter your details below to predict your insurance premium category:")

# Input Fields

age = st.number_input("Age", min_value=18, max_value=119, value=30)
height = st.number_input("Height (in cm)", min_value=50.0, value=250.0)
weight = st.number_input("Weight (in kgs)", min_value=20.0, value=70.0)
income = st.number_input("Annual Income (in LPA)", min_value=0.1, value=10.0)
smoker = st.selectbox("Do you smoke?", options=["True", "False"]) 
city = st.text_input("City", value="Mumbai")
occupation = st.selectbox("Occupation", options=[
    'Business Owner', 'Police Officer', 'Student', 'Engineer',
    'Accountant', 'Lawyer'])

if st.button("Predict Premium Category"):
    input_data = {
        "age": age,
        "weight": weight,
        "height": height / 100,  # converting cm to meters
        "income": income,
        "smoker": smoker,
        "city": city,
        "occupation": occupation
    }

    try:
        response = requests.post(API_URL, json=input_data)
        if response.status_code == 200:
            result = response.json()
            st.success(f"Predicted Insurance Premium Category: **{result['predicted_category']}**")
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the FastAPI server. Make sure it's running on port 8000.")
        