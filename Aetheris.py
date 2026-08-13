import streamlit as st
from google import genai
from google.genai import types

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Aetheris - AI Companion", page_icon="⚡", layout="centered")

st.title("⚡ Aetheris - AI Companion")
st.caption("Aetheris web arayüzüyle aktif, emre amade usta! 🚀")

# --- API YAPILANDIRMASI ---
# Kendi Gemini API anahtarını buraya tırnak içine yapıştır usta
API_KEY = "SECRET_KEY"

# Sohbet geçmişini sayfada tutmak için session_state kullanıyoruz
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Selam usta! Aetheris aktif ve emre amade. Nasıl yardımcı olabilirim? 🚀"}
    ]


# Yapay zeka modelini önbelleğe alıp başlatıyoruz
@st.cache_resource
def get_chat_session(api_key):
    if not api_key or api_key.strip() == "" or api_key == "BURAYA_API_ANAHTARINI_YAPISTIR":
        return None

    client = genai.Client(api_key=api_key)

    system_instruction = (
        "Sen Aetheris adında, Python tabanlı, zeki, havalı ve son derece yetenekli bir yapay zekasın. "
        "Kullanıcıya 'usta' olarak hitap ediyorsun. Kodlama projelerinde, fikir üretiminde ve teknik konularda "
        "en üst düzeyde yardımcı oluyorsun. Cevapların net, karizmatik ve çözüm odaklı. Kısa ve öz cevap ver."
    )

    return client.chats.create(
        model="gemini-3.5-flash-lite",
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.7,
        )
    )


chat_session = get_chat_session(API_KEY)

if not chat_session:
    st.warning("⚠️ Usta, lütfen koddaki API_KEY kısmına kendi Gemini API anahtarını yapıştır!")

# --- SOHBET ARAYÜZÜ ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Aetheris'e bir şeyler yaz usta..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if chat_session:
        with st.chat_message("assistant"):
            try:
                response_stream = chat_session.send_message_stream(prompt)


                def stream_generator():
                    for chunk in response_stream:
                        if chunk.text:
                            yield chunk.text


                full_response = st.write_stream(stream_generator())
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"Sistem Hatası: {e}")
