import streamlit as st
from google import genai
from google.genai import types
import json
import os
import uuid

# --- SAYFA VE TASARIM AYARLARI ---
st.set_page_config(page_title="Aetheris - Advanced AI", page_icon="⚡", layout="centered")

# --- VERİ KAYDI (DATA SAVING) FONKSİYONLARI ---
DATA_FILE = "aetheris_chats.json"

def load_all_chats():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_all_chats(chats_dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(chats_dict, f, ensure_ascii=False, indent=4)

# Verileri yükle
all_chats = load_all_chats()

# --- OTURUM YÖNETİMİ ---
if "current_chat_id" not in st.session_state:
    if all_chats:
        st.session_state.current_chat_id = list(all_chats.keys())[0]
    else:
        new_id = str(uuid.uuid4())[:8]
        all_chats[new_id] = {
            "title": "Sohbet 1",
            "messages": [{"role": "assistant", "content": "Selam usta! Aetheris aktif ve emre amade. Nasıl yardımcı olabilirim? 🚀"}]
        }
        st.session_state.current_chat_id = new_id
        save_all_chats(all_chats)

current_id = st.session_state.current_chat_id

if current_id not in all_chats:
    all_chats[current_id] = {
        "title": "Yeni Sohbet",
        "messages": [{"role": "assistant", "content": "Selam usta! Yeni sohbet açıldı. Nasıl yardımcı olabilirim? 🚀"}]
    }
    save_all_chats(all_chats)

# --- API AYARI ---
try:
    API_KEY = st.secrets["API_KEY"]
except Exception:
    API_KEY = ""

if not API_KEY or API_KEY.strip() == "":
    st.warning("⚠️ Usta, Streamlit Secrets içine `API_KEY` eklenmemiş!")

# --- YAN MENÜ: ÇOKLU SOHBET YÖNETİMİ ---
with st.sidebar:
    st.title("⚡ Aetheris Kontrol")
    
    if st.button("➕ Yeni Sohbet Başlat", use_container_width=True):
        new_id = str(uuid.uuid4())[:8]
        chat_count = len(all_chats) + 1
        all_chats[new_id] = {
            "title": f"Sohbet {chat_count}",
            "messages": [{"role": "assistant", "content": "Selam usta! Yepyeni bir sayfa açtık. Nasıl yardımcı olabilirim? 🚀"}]
        }
        save_all_chats(all_chats)
        st.session_state.current_chat_id = new_id
        st.rerun()

    st.markdown("### Geçmiş Sohbetler")
    for cid, chat_data in list(all_chats.items()):
        if st.button(chat_data["title"], key=cid, use_container_width=True):
            st.session_state.current_chat_id = cid
            st.rerun()

st.title("⚡ Aetheris")

# --- AKTİF SOHBETİ GETİR ---
messages = all_chats[current_id]["messages"]

# Geçmiş mesajları ekrana bas
for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- ALT KISIM: "+" BUTONU, ÖNİZLEME VE GİRİŞ ---
# Sol tarafta "+" açılır menüsü
col_btn, col_input_area = st.columns([0.1, 0.9])

uploaded_file = None
with col_btn:
    with st.popover("➕", help="Görsel Yükle"):
        uploaded_file = st.file_uploader("Görsel seç", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

# İstediğin gibi görsel seçildiyse hemen üstte bildirim gösterelim
if uploaded_file:
    st.info(f"📷 **{uploaded_file.name} seçildi...**")

prompt = st.chat_input("Aetheris'e bir şeyler yaz usta...")

if prompt or uploaded_file:
    user_text = prompt if prompt else "Bu görseli analiz et usta."
    display_text = user_text
    if uploaded_file:
        display_text += f"\n\n*[Eklenen Görsel: {uploaded_file.name}]*"
        
    messages.append({"role": "user", "content": display_text})
    all_chats[current_id]["messages"] = messages
    
    # İlk mesajdan başlık otomatik güncellensin
    if len(messages) == 2:
        all_chats[current_id]["title"] = user_text[:20] + "..."
        
    save_all_chats(all_chats)

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

                formatted_history = []
                for m in messages[:-1]:
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

                contents = [user_text]
                if uploaded_file:
                    bytes_data = uploaded_file.getvalue()
                    contents.append(types.Part.from_data(data=bytes_data, mime_type=uploaded_file.type))

                response_stream = chat_session.send_message_stream(contents)
                
                def stream_generator():
                    for chunk in response_stream:
                        if chunk.text:
                            yield chunk.text
                            
                full_response = st.write_stream(stream_generator())
                
                messages.append({"role": "assistant", "content": full_response})
                all_chats[current_id]["messages"] = messages
                save_all_chats(all_chats)
                
            except Exception as e:
                st.error(f"Sistem Hatası: {e}")
