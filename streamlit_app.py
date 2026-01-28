import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
from datetime import datetime
import pandas as pd

# 1. SETUP
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# We are switching to the explicit 'models/' prefix which is required by some v1beta environments
MODEL_NAME = 'models/gemini-1.5-flash'
model = genai.GenerativeModel(MODEL_NAME)
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
        with st.spinner("AI Scanning..."):
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
                
                # Display
                df_new = pd.DataFrame([row], columns=["Date", "Player", "Sport", "Grade", "Potential"])
                st.table(df_new)
                
                # 4. SAVE
                url = st.secrets["connections"]["gsheets"]["spreadsheet"]
                existing_df = conn.read(spreadsheet=url)
                updated_df = pd.concat([existing_df, df_new], ignore_index=True)
                conn.update(spreadsheet=url, data=updated_df)
                
                st.success("Successfully Saved!")
                st.balloons()

            except Exception as e:
                st.error(f"Analysis Error: {e}")
                # DIAGNOSTIC: This helps us see exactly what your API key is allowed to use
                st.write("Checking available models for your API key...")
                try:
                    available_models = [m.name for m in genai.list_models()]
                    st.write("Your key can see these models:", available_models)
                except:
                    st.write("Could not retrieve model list. Check your API key permissions.")
