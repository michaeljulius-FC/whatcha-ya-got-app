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
# UPDATED: Changed from gemini-1.5-flash to the stable 2.0 release
model = genai.GenerativeModel('gemini-2.0-flash')

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
                
                # Handling potential empty or malformed responses
                if res.text:
                    raw = res.text.strip().split(",")
                    
                    # Create Row
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    row = [now] + [item.strip() for item in raw]
                    
                    # Show Result
                    cols = ["Date", "Player", "Sport", "Grade", "Growth"]
                    # Ensure the AI returned exactly 4 items to match our 5 columns (Date + 4 items)
                    if len(row) == len(cols):
                        df_new = pd.DataFrame([row], columns=cols)
                        st.table(df_new)
                        
                        # 6. SAVE TO SHEET
                        old_df = conn.read(spreadsheet=URL)
                        up_df = pd.concat([old_df, df_new], ignore_index=True)
                        conn.update(spreadsheet=URL, data=up_df)
                        st.success("Successfully Saved!")
                        st.balloons()
                    else:
                        st.error("AI output format was unexpected. Please try scanning again.")
                
            except Exception as e:
                # This will now catch specific API issues if the 404 persists
                st.error(f"Error: {e}")
