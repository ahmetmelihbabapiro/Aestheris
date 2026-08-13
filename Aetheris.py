import threading
import customtkinter as ctk
from google import genai
from google.genai import types

# Arayüz tema ayarları
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class AetherisApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Aetheris - AI Companion")
        self.geometry("700x550")
        self.minsize(600, 450)

        # API Anahtarını buraya yapıştır
        self.API_KEY = ""  # <-- Kendi Gemini API key'ini buraya yaz
        self.chat_session = None
        self.setup_ai()

        # --- ARAYÜZ TASARIMI ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=0)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Sohbet Ekranı
        self.chat_display = ctk.CTkTextbox(self.main_frame, wrap="word", font=("Arial", 14))
        self.chat_display.grid(row=0, column=0, padx=10, pady=(10, 10), sticky="nsew")
        self.chat_display.configure(state="disabled")

        # Girdi Paneli
        self.input_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.input_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.msg_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Aetheris'e bir şeyler yaz usta...",
                                      font=("Arial", 14), height=40)
        self.msg_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.msg_entry.bind("<Return>", lambda event: self.send_message())

        self.send_btn = ctk.CTkButton(self.input_frame, text="Gönder", font=("Arial", 14, "bold"), width=100, height=40,
                                      command=self.send_message)
        self.send_btn.grid(row=0, column=1, sticky="e")

        self.append_chat("Aetheris", "Selam usta! Aetheris aktif ve emre amade. Nasıl yardımcı olabilirim? 🚀\n")

    def setup_ai(self):
        try:
            if not self.API_KEY or self.API_KEY.strip() == "":
                raise ValueError("API_KEY boş! Lütfen Gemini API anahtarını gir.")

            self.client = genai.Client(api_key=self.API_KEY)

            system_instruction = (
                "Sen Aetheris adında, Python tabanlı, zeki, havalı ve son derece yetenekli bir yapay zekasın. "
                "Kullanıcıya 'usta' olarak hitap ediyorsun. Kodlama projelerinde, fikir üretiminde ve teknik konularda "
                "en üst düzeyde yardımcı oluyorsun. Cevapların net, karizmatik ve çözüm odaklı. Kısa ve öz cevap ver."
            )

            # Güncel ve en hızlı model
            self.chat_session = self.client.chats.create(
                model="gemini-3.5-flash-lite",
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7,
                )
            )
            print("AI oturumu başarıyla oluşturuldu (gemini-3.5-flash-lite).")
        except Exception as e:
            print(f"API Kurulum Hatası: {e}")
            self.chat_session = None
            self.after(100, lambda: self.append_chat("Sistem", f"Kurulum hatası: {e}\nAPI key'ini kontrol et.\n"))

    def append_chat(self, sender, text):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"{sender}: {text}\n")
        self.chat_display.see("end")
        self.chat_display.configure(state="disabled")

    def send_message(self):
        user_text = self.msg_entry.get().strip()
        if not user_text:
            return

        self.msg_entry.delete(0, "end")
        self.append_chat("Usta", user_text)

        self.send_btn.configure(state="disabled")
        threading.Thread(target=self.generate_ai_response, args=(user_text,), daemon=True).start()

    def generate_ai_response(self, user_text):
        error_msg = None

        try:
            if self.chat_session is None:
                raise Exception("AI oturumu yok. API key'ini kontrol et ve uygulamayı yeniden başlat.")

            # Streaming ile anında yazmaya başlar
            response_stream = self.chat_session.send_message_stream(user_text)

            self.after(0, lambda: self._start_streaming_response())

            for chunk in response_stream:
                if chunk.text:
                    self.after(0, lambda t=chunk.text: self._append_stream_chunk(t))

            self.after(0, lambda: self._finish_streaming())

        except Exception as e:
            error_msg = str(e)
            self.after(0, lambda: self.append_chat("Sistem", f"Hata oluştu: {error_msg}\n"))
        finally:
            self.after(0, lambda: self.send_btn.configure(state="normal"))

    def _start_streaming_response(self):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", "Aetheris: ")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

    def _append_stream_chunk(self, text):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", text)
        self.chat_display.see("end")
        self.chat_display.configure(state="disabled")

    def _finish_streaming(self):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", "\n\n")
        self.chat_display.see("end")
        self.chat_display.configure(state="disabled")


if __name__ == "__main__":
    app = AetherisApp()
    app.mainloop()