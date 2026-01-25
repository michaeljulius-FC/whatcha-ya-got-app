import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
from datetime import datetime
import pandas as pd

# 1. SECRETS
KEY = st.secrets["GEMINI_API_KEY"]
URL = st.secrets["connections"]["gsheets"]["spreadsheet"]

# 2. AI CONFIG
genai.configure(api_key=KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. SHEET CONNECTION
conn = st.connection("gsheets", type=GSheetsConnection)

# 4. USER INTERFACE
st.set_page_config(page_title="Whatcha Ya Got", page_icon="🎴")
st.title("🎴 Whatcha Ya Got")

c1, c2 = st.columns(2)
with c1:
    f_file = st.camera_input("Front Scan", key="f")
with c2:
    b_file = st.camera_input("Back Scan", key="b")

# 5. ANALYSIS LOGIC
if f_file and b_file:
    if st.button("Analyze & Save"):
        with st.spinner("AI is scanning..."):
            try:
                # Prepare data
                img_f = {"mime_type": "image/jpeg", "data": f_file.getvalue()}
                img_b = {"mime_type": "image/jpeg", "data": b_file.getvalue()}
                prompt = "Return ONLY a comma-separated list: Name, Sport, Grade, Potential"

                # AI Request
                res = model.generate_content([prompt, img_f, img_b])
                raw = res.text.strip().split(",")
                
                # Create Row
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                row = [now] + [item.strip() for item in raw]
                
                # Show Result
                cols = ["Date", "Player", "Sport", "Grade", "Growth"]
                df_new = pd.DataFrame([row], columns=cols)
                st.table(df_new)
                
                # 6. SAVE TO SHEET
                old_df = conn.read(spreadsheet=URL)
                up_df = pd.concat([old_df, df_new], ignore_index=True)
                conn.update(spreadsheet=URL, data=up_df)
                st.success("Successfully Saved!")
                st.balloons()

            except Exception as e:
                st.error(f"Error: {e}")
