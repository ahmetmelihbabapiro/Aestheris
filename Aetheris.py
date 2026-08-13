import streamlit as st
from google import genai
from google.genai import types
import json
import os

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Aetheris - Advanced", page_icon="⚡", layout="centered")
st.title("⚡ Aetheris - Advanced AI")

# --- API AYARI ---
API_KEY = st.secrets["API_KEY"]
client = genai.Client(api_key=API_KEY)

# --- VERİ KAYDI (DATA SAVING) ---
def save_chat(messages):
    with open("chat_history.json", "w", encoding="utf-8") as f:
        json.dump(messages, f)

def load_chat():
    if os.path.exists("chat_history.json"):
        with open("chat_history.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return [{"role": "assistant", "content": "Selam usta! Aetheris aktif. Görsel analize ve veri kaydına hazırım! 🚀"}]

if "messages" not in st.session_state:
    st.session_state.messages = load_chat()

# --- SOHBET ARAYÜZÜ ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- GÖRSEL YÜKLEME VE ANALİZ ---
uploaded_file = st.file_uploader("Bir görsel yükle usta, analiz edeyim...", type=["jpg", "png"])

if prompt := st.chat_input("Bir şeyler yaz veya görseli analiz ettir..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Görsel varsa Gemini'a gönder
            contents = [prompt]
            if uploaded_file:
                bytes_data = uploaded_file.getvalue()
                contents.append(types.Part.from_data(data=bytes_data, mime_type="image/jpeg"))

            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=contents
            )
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            save_chat(st.session_state.messages) # Kaydet usta!
        except Exception as e:
            st.error(f"Sistem Hatası: {e}")
