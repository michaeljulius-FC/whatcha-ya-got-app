import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
from datetime import datetime
from PIL import Image
import pandas as pd

# 1. SECRETS & CONFIGURATION
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
SHEET_URL = st.secrets["connections"]["gsheets"]["spreadsheet"]

# 2. AI INITIALIZATION
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash-latest')

# 3. GOOGLE SHEETS CONNECTION
conn = st.connection("gsheets", type=GSheetsConnection)

# 4. USER INTERFACE
st.set_page_config(page_title="Whatcha Ya Got", page_icon="🎴")
st.title("🎴 Whatcha Ya Got")
st.markdown("Scan the front and back of your card to analyze.")

col1, col2 = st.columns(2)
with col1:
    front_file = st.camera_input("Scan Card Front", key="front")
with col2:
    back_file = st.camera_input("Scan Card Back", key="back")

# 5. ANALYSIS & SAVING LOGIC
if front_file and back_file:
    if st.button("Analyze & Save to Sheet"):
        with st.spinner("AI is examining the card..."):
            try:
                # Prepare images
                img_f = {"mime_type": "image/jpeg", "data": front_file.getvalue()}
                img_b = {"mime_type": "image/jpeg", "data": back_file.getvalue()}
                
                prompt = (
                    "Identify: Player Name, Sport, PSA Grade (1-10), Growth Potential. "
                    "Return ONLY as a comma-separated list."
                )

                # Get AI Response
                response = model.generate_content([prompt, img_f, img_b])
                ai_data = response.text.strip().split(",")
                
                # Create Data Row
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                new_row = [now] + [item.strip() for item in ai_data]
                
                # Define Columns clearly to avoid string errors
                cols = ["Timestamp", "Player", "Sport", "Grade", "Potential"]
                df_new = pd.DataFrame([new_row], columns=cols)
                
                st.subheader("Results")
                st.table(df_new)
                
                # 6. SAVE TO GOOGLE SHEETS
                existing_df = conn.read(spreadsheet=SHEET_URL)
                updated_df = pd.concat([existing_df, df_new], ignore_index=True)
                conn.update(spreadsheet=SHEET_URL, data=updated_df)
                
                st.success("Saved to Whatcha Ya Got!")
                st.balloons()

            except Exception as e:
                st.error(f"Error: {e}")
