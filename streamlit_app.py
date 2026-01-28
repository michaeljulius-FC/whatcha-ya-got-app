import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
from datetime import datetime
import pandas as pd

# 1. AI CONFIGURATION
# We use 'gemini-1.5-flash' for maximum compatibility with your new project
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. GOOGLE SHEETS SETUP
conn = st.connection("gsheets", type=GSheetsConnection)
SHEET_URL = st.secrets["connections"]["gsheets"]["spreadsheet"]

# 3. USER INTERFACE
st.set_page_config(page_title="Whatcha Ya Got", page_icon="🎴")
st.title("🎴 Whatcha Ya Got")
st.markdown("Scan your card's front and back to analyze and save.")

col1, col2 = st.columns(2)
with col1:
    f_file = st.camera_input("Front", key="front")
with col2:
    b_file = st.camera_input("Back", key="back")

# 4. ANALYSIS & SAVING
if f_file and b_file:
    if st.button("Analyze & Save to Sheet"):
        with st.spinner("AI is examining the card..."):
            try:
                # Prepare images for Gemini
                img_f = {"mime_type": "image/jpeg", "data": f_file.getvalue()}
                img_b = {"mime_type": "image/jpeg", "data": b_file.getvalue()}
                
                prompt = "Return ONLY a comma-separated list: Name, Sport, Grade, Potential"
                
                # Get AI Response
                response = model.generate_content([prompt, img_f, img_b])
                ai_data = response.text.strip().split(",")
                
                # Format Data for Table
                now = datetime.now().strftime("%Y-%m-%d %H:%M")
                new_row = [now] + [item.strip() for item in ai_data]
                
                cols = ["Date", "Player", "Sport", "Grade", "Potential"]
                df_new = pd.DataFrame([new_row], columns=cols)
                
                # Show results in app
                st.subheader("Analysis Results")
                st.table(df_new)
                
                # 5. DATA SYNC (Sheet Handshake)
                existing_df = conn.read(spreadsheet=SHEET_URL)
                updated_df = pd.concat([existing_df, df_new], ignore_index=True)
                conn.update(spreadsheet=SHEET_URL, data=updated_df)
                
                st.success("Successfully saved to your sheet!")
                st.balloons()

            except Exception as e:
                # This catches API issues, sheet issues, or formatting errors
                st.error(f"Analysis Error: {e}")
                st.info("Check your API key and ensure your Sheet is shared as 'Editor'.")
                
