import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
from datetime import datetime
import pandas as pd

# 1. SETUP
# Using the full model path to fix the 404 error
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('models/gemini-1.5-flash')
conn = st.connection("gsheets", type=GSheetsConnection)

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
        with st.spinner("AI Scanning Card..."):
            try:
                # Prepare AI content
                content = [
                    "Identify: Player Name, Sport, PSA Grade (1-10), Growth Potential. Return ONLY a comma-separated list.",
                    {"mime_type": "image/jpeg", "data": f_img.getvalue()},
                    {"mime_type": "image/jpeg", "data": b_img.getvalue()}
                ]
                
                # AI Request
                res = model.generate_content(content)
                data = res.text.strip().split(",")
                
                # Create Row
                now = datetime.now().strftime("%Y-%m-%d %H:%M")
                row = [now] + [item.strip() for item in data]
                
                # Table display
                cols = ["Date", "Player", "Sport", "Grade", "Potential"]
                df_new = pd.DataFrame([row], columns=cols)
                st.table(df_new)
                
                # 4. SAVE TO GOOGLE SHEETS
                sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
                existing_df = conn.read(spreadsheet=sheet_url)
                updated_df = pd.concat([existing_df, df_new], ignore_index=True)
                conn.update(spreadsheet=sheet_url, data=updated_df)
                
                st.success("Successfully Saved!")
                st.balloons()

            except Exception as e:
                st.error(f"Analysis Error: {e}")
