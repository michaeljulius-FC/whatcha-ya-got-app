import streamlit as st
import google.generativeai as genai
from datetime import datetime
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# 1. AUTHENTICATION & SETUP
# This manual method is more robust for private_key formatting issues
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('models/gemini-3-flash-preview')

# Manual GSheets Connection
try:
    # Build credentials dictionary from secrets
    creds_dict = {
        "type": st.secrets["connections"]["gsheets"]["type"],
        "project_id": st.secrets["connections"]["gsheets"]["project_id"],
        "private_key_id": st.secrets["connections"]["gsheets"]["private_key_id"],
        # This .replace fix handles the formatting error you were seeing
        "private_key": st.secrets["connections"]["gsheets"]["private_key"].replace("\\n", "\n"),
        "client_email": st.secrets["connections"]["gsheets"]["client_email"],
        "client_id": st.secrets["connections"]["gsheets"]["client_id"],
        "auth_uri": st.secrets["connections"]["gsheets"]["auth_uri"],
        "token_uri": st.secrets["connections"]["gsheets"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["connections"]["gsheets"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["connections"]["gsheets"]["client_x509_cert_url"],
    }
    
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    gc = gspread.authorize(creds)
    
    # Open the sheet by URL
    sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    sh = gc.open_by_url(sheet_url)
    worksheet = sh.get_worksheet(0) # Grabs the first tab
except Exception as e:
    st.error(f"Sheet Connection Error: {e}")

# 2. UI
st.set_page_config(page_title="Whatcha Ya Got", page_icon="🎴")
st.title("🎴 Whatcha Ya Got")

c1, c2 = st.columns(2)
with c1:
    f_img = st.camera_input("Front", key="f")
with c2:
    b_img = st.camera_input("Back", key="b")

# 3. LOGIC
if f_img and b_img:
    if st.button("Analyze & Save to Sheet"):
        with st.spinner("Gemini 3.0 is scanning..."):
            try:
                content = [
                    "Identify: Player, Sport, PSA Grade (1-10), Potential. Return ONLY a comma-separated list.",
                    {"mime_type": "image/jpeg", "data": f_img.getvalue()},
                    {"mime_type": "image/jpeg", "data": b_img.getvalue()}
                ]
                
                res = model.generate_content(content)
                data = res.text.strip().split(",")
                
                now = datetime.now().strftime("%Y-%m-%d %H:%M")
                row = [now] + [item.strip() for item in data]
                
                # Display Result
                st.table(pd.DataFrame([row], columns=["Date", "Player", "Sport", "Grade", "Potential"]))
                
                # SAVE using gspread
                worksheet.append_row(row)
                
                st.success("Successfully Saved to Collection!")
                st.balloons()

            except Exception as e:
                st.error(f"Analysis Error: {e}")
