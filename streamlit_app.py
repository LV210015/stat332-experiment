import streamlit as st
import random
import os
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# Load credentials from Streamlit secrets
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"])
client = gspread.authorize(creds)

# Open the Google Sheet
spreadsheet = client.open_by_url("https://docs.google.com/spreadsheets/d/14gEZ_Y5j9f8XFWnqVuHfFmM831KUJexTeHe3cccddi0/edit#gid=0")
worksheet = spreadsheet.sheet1

# Image grouping logic
image_folder = "images"
groups = {
    "MCCD": [f"MCCD{i}.jpg" for i in range(1, 7)],
    "MCND": [f"MCND{i}.jpg" for i in range(1, 7)],
    "MLCD": [f"MLCD{i}.jpg" for i in range(1, 7)],
    "MLND": [f"MLND{i}.jpg" for i in range(1, 7)],
    "MPCD": [f"MPCD{i}.jpg" for i in range(1, 7)],
    "MPND": [f"MPND{i}.jpg" for i in range(1, 7)],
}

# Predefined valid codes
valid_codes = {
    "MCCD": ["MCCD1", "MCCD2", "MCCD3", "MCCD4", "MCCD5", "MCCD6"],
    "MCND": ["MCND1", "MCND2", "MCND3", "MCND4", "MCND5", "MCND6"],
    "MLCD": ["MLCD1", "MLCD2", "MLCD3", "MLCD4", "MLCD5", "MLCD6"],
    "MLND": ["MLND1", "MLND2", "MLND3", "MLND4", "MLND5", "MLND6"],
    "MPCD": ["MPCD1", "MPCD2", "MPCD3", "MPCD4", "MPCD5", "MPCD6"],
    "MPND": ["MPND1", "MPND2", "MPND3", "MPND4", "MPND5", "MPND6"]
}

st.title("The Impact of Color & Distortion on Code Recognition")

# Start page
nickname = st.text_input("Please enter a nickname or username to begin:", key="nickname")
if st.button("Start Survey") and nickname:
    st.session_state.page = "survey"

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "start"
if "questions" not in st.session_state:
    st.session_state.questions = []
    for group, images in groups.items():
        st.session_state.questions.extend(
            [{"group": group, "image": img} for img in random.sample(images, 2)]
        )
    random.shuffle(st.session_state.questions)
    st.session_state.answers = []

# Survey page
if st.session_state.page == "survey":
    current_q = len(st.session_state.answers)
    if current_q < len(st.session_state.questions):
        q = st.session_state.questions[current_q]
        image_path = os.path.join(image_folder, q["image"])
        st.image(image_path, caption="Please enter the code you see.")
        response = st.text_input("Code:", key=f"response_{current_q}")

        if st.button("Submit"):
            is_valid = response.upper() in [code.upper() for code in valid_codes[q["group"]]]
            st.session_state.answers.append({
                "nickname": nickname,
                "image": q["image"],
                "group": q["group"],
                "response": response,
                "valid": is_valid
            })
            st.experimental_rerun()
    else:
        st.write("Thank you for participating. Your responses have been recorded.")

        # Save to Google Sheet
        df = pd.DataFrame(st.session_state.answers)
        worksheet.append_rows(df.values.tolist())
        st.success("Responses successfully submitted.")
        st.session_state.page = "done"
