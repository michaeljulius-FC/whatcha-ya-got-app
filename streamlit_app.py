import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
from datetime import datetime
import pandas as pd
from PIL import Image
import io

# 1. SECRETS
KEY = st.secrets["GEMINI_API_KEY"]
URL = st.secrets["connections"]["gsheets"]["spreadsheet"]

# 2. AI CONFIG
genai.configure(api_key=KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# NEW: Function to shrink images to save quota (Tokens)
def process_image(uploaded_file):
    img = Image.open(uploaded_file)
    # Resize while maintaining aspect ratio (Max 800px)
    img.thumbnail((800, 800))
    # Convert back to bytes for the API
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()

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
        with st.spinner("Optimizing images & scanning..."):
            try:
                # Process and shrink images before sending to AI
                img_f_data = process_image(f_file)
                img_b_data = process_image(b_file)
                
                img_f = {"mime_type": "image/jpeg", "data": img_f_data}
                img_b = {"mime_type": "image/jpeg", "data": img_b_data}
                
                prompt = "Return ONLY a comma-separated list: Name, Sport, Grade, Potential"

                # AI Request
                res = model.generate_content([prompt, img_f, img_b])
                
                if res.text:
                    raw = res.text.strip().split(",")
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    row = [now] + [item.strip() for item in raw]
                    
                    cols = ["Date", "Player", "Sport", "Grade", "Growth"]
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
                        st.error(f"AI returned {len(row)} items, but we expected 5. Output: {res.text}")

            except Exception as e:
                if "429" in str(e):
                    st.error("Quota Exceeded: Please wait 60 seconds or check your daily limit in Google AI Studio.")
                else:
                    st.error(f"Error: {e}")
