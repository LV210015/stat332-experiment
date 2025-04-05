import streamlit as st
import os
import random
import time
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# Open your Google Sheet by name or URL key
sheet = client.open_by_key("14gEZ_Y5j9f8XFWnqVuHfFmM831KUJexTeHe3cccddi0").sheet1

# Streamlit settings
st.set_page_config(page_title="STAT 332 Survey", layout="centered")

group_prefixes = ["MCCD", "MCND", "MCSD", "NCCD", "NCND", "NCSD"]
valid_answers = {
    "MCND": ["R5UM", "X4GE", "H2KD", "P7CQ", "6TVA", "D8YR"],
    "MCSD": ["N8QJ", "S4VA", "E9DX", "T3KM", "J5NZ", "V6RC"],
    "MCCD": ["Q2BT", "G7MW", "U8FX", "A9CJ", "M4KP", "X6DN"],
    "NCND": ["A7KQ", "M9TX", "8ZRD", "V3NC", "F6JP", "2WBY"],
    "NCSD": ["K3BN", "Z9MU", "B5FX", "Y2GW", "C6TR", "W7HP"],
    "NCCD": ["F3YV", "B7QA", "Z5HW", "H6GT", "R2NX", "Y8PC"]
}

def load_images():
    image_dir = "images"
    all_images = []
    for prefix in group_prefixes:
        group_imgs = [f"{prefix}{i}.jpg" for i in range(1, 7)]
        selected = random.sample(group_imgs, 2)
        all_images.extend([os.path.join(image_dir, img) for img in selected])
    random.shuffle(all_images)
    return all_images

if "nickname" not in st.session_state:
    st.session_state.nickname = ""
if "step" not in st.session_state:
    st.session_state.step = "start"
if "images" not in st.session_state:
    st.session_state.images = []
if "responses" not in st.session_state:
    st.session_state.responses = []
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "start_time" not in st.session_state:
    st.session_state.start_time = 0

if st.session_state.step == "start":
    st.title("STAT 332 Experiment")
    st.subheader("The Impact of Color & Distortion on Code Recognition")
    st.write("Please enter a nickname or username to begin:")
    nickname = st.text_input("Nickname", value=st.session_state.nickname)
    if st.button("Start Survey"):
        if nickname.strip() == "":
            st.warning("Please enter a valid nickname.")
        else:
            st.session_state.nickname = nickname.strip()
            st.session_state.step = "instructions"
            st.rerun()

elif st.session_state.step == "instructions":
    st.title("Instructions")
    st.markdown("""
    1. You’ll see 12 images of verification codes — just recognize and type what you see.

    2. For each image, click 'I Recognized It!' before entering your answer.

    3. There will NOT be codes like '0' (zero) or 'O' (letter O), so don’t worry about confusing characters.

    4. Just relax, type naturally, and have fun with it — it’s not a test!
    """)
    if st.button("Begin Survey"):
        st.session_state.images = load_images()
        st.session_state.step = "survey"
        st.rerun()

elif st.session_state.step == "survey":
    images = st.session_state.images
    index = st.session_state.current_index
    if index >= len(images):
        st.session_state.step = "thankyou"
        st.rerun()
    image_path = images[index]
    st.image(image_path, width=350, caption=f"Image {index + 1} of 12")
    if "show_input" not in st.session_state:
        st.session_state.show_input = False
    if not st.session_state.show_input:
        if st.button("I Recognized It!"):
            st.session_state.start_time = time.time()
            st.session_state.show_input = True
            st.rerun()
    else:
        answer = st.text_input("What did you see?").strip()
        if st.button("Submit Answer"):
            end_time = time.time()
            duration = round(end_time - st.session_state.start_time, 2)
            filename = os.path.basename(image_path)
            group = filename[:4]
            color = "Color" if group[0] == "M" else "NoColor"
            dist_code = group[2:]
            distortion_map = {"ND": "None", "SD": "Simple", "CD": "Complex"}
            distortion = distortion_map.get(dist_code, "Unknown")
            normalized = answer.upper().replace(" ", "")
            correct = normalized in valid_answers.get(group, [])
            response = [
                st.session_state.nickname,
                index + 1,
                color,
                distortion,
                duration,
                answer,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                str(correct)
            ]
            sheet.append_row(response)
            st.session_state.current_index += 1
            st.session_state.show_input = False
            st.rerun()

elif st.session_state.step == "thankyou":
    st.title("Thank You")
    st.write("Your responses have been recorded successfully.")
