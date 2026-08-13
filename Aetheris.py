import streamlit as st
from google import genai
from google.genai import types

# --- SAYFA VE TASARIM AYARLARI ---
st.set_page_config(page_title="Aetheris - Advanced AI", page_icon="⚡", layout="centered")

# Özel CSS ile tasarımı fıstık gibi yapıyoruz
st.markdown("""
    <style>
    /* Dosya yükleme butonunu gizle ama işlevini koru */
    .stUploadedFile {display: none;}
    </style>
""", unsafe_allow_html=True)

# --- API AYARI ---
try:
    API_KEY = st.secrets["API_KEY"]
except Exception:
    API_KEY = ""

if not API_KEY or API_KEY.strip() == "":
    st.warning("⚠️ Usta, Streamlit Secrets içine `API_KEY` eklenmemiş!")

# --- YAN MENÜ: SOHBET YÖNETİMİ ---
with st.sidebar:
    st.title("⚡ Aetheris Kontrol")
    if st.button("➕ Yeni Sohbet Başlat", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": "Selam usta! Yepyeni bir sayfa açtık. Nasıl yardımcı olabilirim? 🚀"}
        ]
        st.rerun()
    
    st.markdown("---")
    st.subheader("📸 Görsel Yükle")
    # Görseli şık bir şekilde yan menüye aldık, taşma kirlilik asla yok!
    uploaded_file = st.file_uploader("Analiz edilecek görseli seç", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    if uploaded_file:
        st.success("Görsel hazır usta! Mesajını yaz ve gönder.")

st.title("⚡ Aetheris")

# --- SOHBET GEÇMİŞİ ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Selam usta! Aetheris aktif. Görsel analize ve sohbete hazırım! 🚀"}
    ]

# Geçmiş mesajları ekrana bas
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- MESAJ GİRİŞ ALANI ---
if prompt := st.chat_input("Aetheris'e bir şeyler yaz usta..."):
    user_input_text = prompt
    display_text = prompt
    if uploaded_file:
        display_text += " [📸 Görsel Eklendi]"
        
    st.session_state.messages.append({"role": "user", "content": display_text})
    with st.chat_message("user"):
        st.markdown(display_text)

    if API_KEY:
        with st.chat_message("assistant"):
            try:
                client = genai.Client(api_key=API_KEY)
                
                system_instruction = (
                    "Sen Aetheris adında, Python tabanlı, zeki, havalı ve son derece yetenekli bir yapay zekasın. "
                    "Kullanıcıya 'usta' olarak hitap ediyorsun. Kodlama projelerinde, fikir üretiminde ve teknik konularda "
                    "en üst düzeyde yardımcı oluyorsun. Görsel analizi yapabilirsin. Kısa ve öz cevap ver."
                )

                # Geçmişi hazırla
                formatted_history = []
                for m in st.session_state.messages[:-1]:
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

                # İçerik oluştur (Görsel varsa ekle)
                contents = [user_input_text]
                if uploaded_file:
                    bytes_data = uploaded_file.getvalue()
                    contents.append(types.Part.from_data(data=bytes_data, mime_type=uploaded_file.type))

                response_stream = chat_session.send_message_stream(contents)
                
                def stream_generator():
                    for chunk in response_stream:
                        if chunk.text:
                            yield chunk.text
                            
                full_response = st.write_stream(stream_generator())
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"Sistem Hatası: {e}")
