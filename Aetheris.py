import streamlit as st
from google import genai
from google.genai import types

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Aetheris - AI Companion", page_icon="⚡", layout="centered")

st.title("⚡ Aetheris - AI Companion")
st.caption("Aetheris web arayüzüyle aktif, emre amade usta! 🚀")

# --- GÜVENLİ API ÇEKME ---
try:
    API_KEY = st.secrets["API_KEY"]
except Exception:
    API_KEY = ""

if not API_KEY or API_KEY.strip() == "":
    st.warning("⚠️ Usta, Streamlit Secrets içine `API_KEY` eklenmemiş! Lütfen panelden ekle.")

# Sohbet geçmişini sayfada tutmak için session_state kullanıyoruz
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Selam usta! Aetheris aktif ve emre amade. Nasıl yardımcı olabilirim? 🚀"}
    ]

# --- SOHBET ARAYÜZÜ ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Aetheris'e bir şeyler yaz usta..."):
    # Kullanıcı mesajını ekrana ve geçmişe ekle
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if API_KEY:
        with st.chat_message("assistant"):
            try:
                client = genai.Client(api_key=API_KEY)
                
                system_instruction = (
                    "Sen Aetheris adında, Python tabanlı, zeki, havalı ve son derece yetenekli bir yapay zekasın. "
                    "Kullanıcıya 'usta' olarak hitap ediyorsun. Kodlama projelerinde, fikir üretiminde ve teknik konularda "
                    "en üst düzeyde yardımcı oluyorsun. Cevapların net, karizmatik ve çözüm odaklı. Kısa ve öz cevap ver."
                )

                # Geçmiş mesajları Gemini formatına dönüştürüyoruz
                formatted_history = []
                for m in st.session_state.messages[:-1]: # Son mesaj hariç geçmiş
                    role = "user" if m["role"] == "user" else "model"
                    formatted_history.append(
                        types.Content(role=role, parts=[types.Part.from_text(text=m["content"])])
                    )

                chat_session = client.chats.create(
                    model="gemini-3.5-flash-lite",
                    history=formatted_history,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.7,
                    )
                )

                response_stream = chat_session.send_message_stream(prompt)
                
                def stream_generator():
                    for chunk in response_stream:
                        if chunk.text:
                            yield chunk.text
                            
                full_response = st.write_stream(stream_generator())
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"Sistem Hatası: {e}")
