import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
from datetime import datetime
from PIL import Image
import pandas as pd

# 1. SECRETS & CONFIGURATION
# Accessing the "Vault" we set up in Streamlit Cloud
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
SHEET_URL = st.secrets["connections"]["gsheets"]["spreadsheet"]

# 2. AI INITIALIZATION
genai.configure(api_key=GEMINI_API_KEY)

# Using 'latest' to ensure collaborative fidelity with Google's newest stable endpoint
model = genai.GenerativeModel('gemini-1.5-flash-latest')

# 3. GOOGLE SHEETS CONNECTION
conn = st.connection("gsheets", type=GSheetsConnection)

# 4. USER INTERFACE
st.set_page_config(page_title="Whatcha Ya Got", page_icon="🎴")
st.title("🎴 Whatcha Ya Got")
st.markdown("Scan the front and back of your card to analyze and save to your collection.")

col1, col2 = st.columns(2)
with col1:
    front_file = st.camera_input("Scan Card Front", key="front")
with col2:
    back_file = st.camera_input("Scan Card Back", key="back")

# 5. ANALYSIS & SAVING LOGIC
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

                # Sending the request to the AI
                response = model.generate_content([prompt, img_front, img_back])
                
                # Process the AI response
                ai_data = response.text.strip().split(",")
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Construct the new row (cleaning any extra whitespace)
                new_row = [timestamp] + [item.strip() for item in ai_data]
                
                # Create a temporary DataFrame for display
                cols = ["Timestamp", "Player Name", "
