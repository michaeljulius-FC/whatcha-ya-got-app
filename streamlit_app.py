import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
from datetime import datetime
import pandas as pd

# 1. SETUP
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# UPGRADED MODEL: Using the specific path from your diagnostic list
MODEL_NAME = 'models/gemini-3-flash-preview'
model = genai.GenerativeModel(MODEL_NAME)
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. UI
st.set_page_config(page_title="Whatcha Ya Got", page_icon="🎴")
st.title("🎴 Whatcha Ya Got")
st.markdown("Analyzing with Gemini 3.0 Flash Technology")

c1, c2 = st.columns(2)
with c1:
    f_img = st.camera_input("Front", key="f")
with c2:
    b_img = st.camera_input("Back", key="b")

# 3. LOGIC
if f_img and b_img:
    if st.button("Analyze & Save to Sheet"):
        with st.spinner("Gemini 3.0 is examining the card..."):
            try:
                # Prepare AI content
                content = [
                    "Identify: Player, Sport, PSA Grade (1-10), Potential. Return ONLY a comma-separated list.",
                    {"mime_type": "image/jpeg", "data": f_img.getvalue()},
                    {"mime_type": "image/jpeg", "data": b_img.getvalue()}
                ]
                
                # AI Request
                res = model.generate_content(content)
                data = res.text.strip().split(",")
                
                # Create Row
                now = datetime.now().strftime("%Y-%m-%d %H:%M")
                row = [now] + [item.strip() for item in data]
                
                # Display Result
                df_new = pd.DataFrame([row], columns=["Date", "Player", "Sport", "Grade", "Potential"])
                st.table(df_new)
                
                # 4. SAVE TO GOOGLE SHEETS
                url = st.secrets["connections"]["gsheets"]["spreadsheet"]
                existing_df = conn.read(spreadsheet=url)
                
                # Handle empty sheets or new sheets gracefully
                if existing_df is not None and not existing_df.empty:
                    updated_df = pd.concat([existing_df, df_new], ignore_index=True)
                else:
                    updated_df = df_new
                    
                conn.update(spreadsheet=url, data=updated_df)
                
                st.success("Successfully Saved to Collection!")
                st.balloons()

            except Exception as e:
                st.error(f"Analysis Error: {e}")
