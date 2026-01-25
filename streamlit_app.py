import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
from datetime import datetime
from PIL import Image
import pandas as pd

# 1. SECRETS
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
SHEET_URL = st.secrets["connections"]["gsheets"]["spreadsheet"]

# 2. AI CONFIG
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. SHEET CONFIG
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🎴 Whatcha Ya Got")

col1, col2 = st.columns(2)
with col1:
    front_file = st.camera_input("Scan Front")
with col2:
    back_file = st.camera_input("Scan Back")

if front_file and back_file:
    if st.button("Analyze & Save"):
        with st.spinner("Analyzing..."):
            img_front = Image.open(front_file)
            img_back = Image.open(back_file)

            prompt = "Identify: Player Name, Sport, PSA Grade (1-10), Growth Potential. Return ONLY as a comma-separated list."
            
            # This 'inline_data' method is the most stable for mobile cameras
            response = model.generate_content([
                prompt,
                {"mime_type": "image/jpeg", "data": front_file.getvalue()},
                {"mime_type": "image/jpeg", "data": back_file.getvalue()}
            ])
            
            ai_data = response.text.strip().split(",")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_row = [timestamp] + [item.strip() for item in ai_data]
            
            # Display & Update
            df_new = pd.DataFrame([new_row], columns=["Timestamp", "Player Name", "Sport", "PSA Grade", "Growth Potential"])
            st.table(df_new)
            
            existing_df = conn.read(spreadsheet=SHEET_URL)
            updated_df = pd.concat([existing_df, df_new], ignore_index=True)
            conn.update(spreadsheet=SHEET_URL, data=updated_df)
            st.success("Saved to Whatcha Ya Got!")
