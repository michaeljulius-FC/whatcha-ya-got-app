import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
from datetime import datetime
from PIL import Image
import pandas as pd

# 1. Access the Secrets you saved in Streamlit Cloud
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
SHEET_URL = st.secrets["connections"]["gsheets"]["spreadsheet"]

# 2. Setup the AI Engine (Gemini 1.5 Flash)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. Setup the Connection to "Whatcha Ya Got"
conn = st.connection("gsheets", type=GSheetsConnection)

st.set_page_config(page_title="Whatcha Ya Got", page_icon="🎴")
st.title("🎴 Whatcha Ya Got")
st.subheader("Card Analyzer & Master Logger")

# 4. The Camera Inputs
col1, col2 = st.columns(2)
with col1:
    front_file = st.camera_input("Scan Front")
with col2:
    back_file = st.camera_input("Scan Back")

if front_file and back_file:
    if st.button("Analyze & Save to Whatcha Ya Got"):
        with st.spinner("AI is examining the card..."):
            # Process Images
            img_front = Image.open(front_file)
            img_back = Image.open(back_file)

            # AI Logic
            prompt = """
            Look at the front and back of this sports card.
            Identify: Player Name, Sport, Potential PSA Grade (1-10), and Growth Potential.
            Format the output exactly like this:
            Player Name, Sport, Grade, Potential
            """
            
            response = model.generate_content([prompt, img_front, img_back])
            ai_data = response.text.strip().split(",")
            
            # Prepare the row for "Whatcha Ya Got"
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Cleaning the AI response to make sure it fits the columns
            row_data = [timestamp] + [item.strip() for item in ai_data[:4]]
            
            # Create a preview table
            df_new = pd.DataFrame([row_data], columns=["Timestamp", "Player Name", "Sport", "PSA Grade", "Growth Potential"])
            st.table(df_new)

            # 5. Push data to the Google Sheet
            try:
                existing_data = conn.read(spreadsheet=SHEET_URL)
                updated_df = pd.concat([existing_data, df_new], ignore_index=True)
                conn.update(spreadsheet=SHEET_URL, data=updated_df)
                st.success("Successfully added to Whatcha Ya Got!")
            except Exception as e:
                st.error(f"Sheet update failed: {e}")
