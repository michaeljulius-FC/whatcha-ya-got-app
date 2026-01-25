import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
from datetime import datetime
from PIL import Image
import pandas as pd

# 1. SECRETS & CONFIGURATION
# Ensure these match exactly what you have in Streamlit 'Advanced Settings'
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
SHEET_URL = st.secrets["connections"]["gsheets"]["spreadsheet"]

# 2. AI INITIALIZATION
genai.configure(api_key=GEMINI_API_KEY)

# In 2026, 'gemini-1.5-flash-latest' is the most stable alias for this task.
# This avoids the 'NotFound' error by pointing to the current production version.
model = genai.GenerativeModel('gemini-1.5-flash-latest')

# 3. GOOGLE SHEETS CONNECTION
conn = st.connection("gsheets", type=GSheetsConnection)

# 4. USER INTERFACE
st.set_page_config(page_title="Whatcha Ya Got", page_icon="🎴")
st.title("🎴 Whatcha Ya Got")
st.markdown("Scan the front and back of your card to analyze and save.")

col1, col2 = st.columns(2)
with col1:
    front_file = st.camera_input("Scan Card Front", key="front")
with col2:
    back_file = st.camera_input("Scan Card Back", key="back")

# 5. ANALYSIS LOGIC
if front_file and back_file:
    if st.button("Analyze & Save to Sheet"):
        with st.spinner("AI is examining the card fidelity..."):
            try:
                # Prepare images for the API
                img_front = {"mime_type": "image/jpeg", "data": front_file.getvalue()}
                img_back = {"mime_type": "image/jpeg", "data": back_file.getvalue()}
                
                prompt = (
                    "Identify the following from these card images: "
                    "Player Name, Sport, PSA Grade (1-10), and Growth Potential. "
                    "Return the data ONLY as a comma-separated list in that exact order."
                )

                # Sending the request to the stable model alias
                response = model.generate_content([prompt, img_front, img_back])
                
                # Process the AI response
                ai_data = response.text.strip().split(",")
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Construct the new row
                new_row = [timestamp] + [item.strip() for item in ai_data]
                
                # Create a temporary DataFrame to show the user
                cols = ["Timestamp", "Player Name", "Sport", "PSA Grade", "Growth Potential"]
                df_new = pd.DataFrame([new_row], columns=cols)
                
                st.subheader("Analysis Results")
                st.table(df_new)
                
                # 6. SAVE TO GOOGLE SHEETS
                # Read existing data, combine with new row, and update the sheet
                existing_df = conn.read(spreadsheet=SHEET_URL)
                updated_df = pd.concat([existing_df, df_new], ignore_index=True)
