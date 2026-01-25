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
# Using the standard stable alias for 2026
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. CONNECTIONS
conn = st.connection("gsheets", type=GSheetsConnection)

# 4. UI
st.title("🎴 Whatcha Ya Got")
c1, c2 = st.columns(2)
with c1:
    f_file = st.camera_input("Front", key="f")
with c2:
    b_file = st.camera_input("Back", key="b")

# 5. LOGIC
if f_file and b_file:
    if st.button("Analyze & Save"):
        with st.spinner("AI is scanning..."):
            try:
                img_f = {"mime_type": "image/jpeg", "data": f_file.getvalue()}
                img_b = {"mime_type": "image/jpeg", "data": b_file.getvalue()}
                
                prompt = "Return ONLY a comma-separated list: Name, Sport, Grade, Potential"
                response = model.generate_content([prompt, img_f, img_b])
                
                # Process Data
                raw = response.text.strip().split(",")
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                row = [now] + [item.strip() for item in raw]
                
                # Create Table
                cols = ["Date", "Player", "Sport", "Grade", "Potential"]
                df_new = pd.DataFrame([row], columns=cols)
                st.table(df_new)
                
                # 6. SAVE
                old_df = conn.read(spreadsheet=URL)
                up_df = pd.concat([old_df, df_new], ignore_index=True)
                conn.update(spreadsheet=URL, data=up_df)
                st.success("Saved!")
                st.balloons()

            except Exception as e:
                st.error(f"Error: {e}")
