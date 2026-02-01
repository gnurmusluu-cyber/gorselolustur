import streamlit as st
import requests
import io
import os
from PIL import Image

# --- API AYARLARI ---
if "HF_TOKEN" in st.secrets:
    HF_TOKEN = st.secrets["HF_TOKEN"]
else:
    try:
        from dotenv import load_dotenv
        load_dotenv()
        HF_TOKEN = os.getenv("HF_TOKEN")
    except:
        HF_TOKEN = os.getenv("HF_TOKEN")

# En yüksek doğruluk oranlı model
API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

st.set_page_config(page_title="BT Görsel Atölyesi", layout="centered")

# --- FONKSİYOMLAR ---

def translate_me(text):
    """Google Translate altyapısını kullanarak en net çeviriyi yapar."""
    try:
        base_url = "https://translate.googleapis.com/translate_a/single"
        params = {"client": "gtx", "sl": "tr", "tl": "en", "dt": "t", "q": text}
        r = requests.get(base_url, params=params, timeout=5)
        return r.json()[0][0][0]
    except:
        return text

def query(payload):
    """Hugging Face'e en sade haliyle istek atar."""
    response = requests.post(API_URL, headers=headers, json=payload, timeout=40)
    return response

# --- ARAYÜZ ---
st.title("🎨 Akıllı Görsel Oluşturucu v4")
st.write("Nusaybin BT Sınıfı Özel Versiyon")

user_input = st.text_input("Görsel açıklamasını yazın:", placeholder="Örn: Kırmızı elma tutan bir robot")

if st.button("🚀 Oluştur"):
    if not HF_TOKEN:
        st.error("🔑 Token hatası!")
    elif not user_input:
        st.warning("⚠️ Bir şeyler yazmalısın.")
    else:
        with st.status("⏳ İşleniyor...") as status:
            # 1. Çeviri yap ve ekranda göster (Kontrol amaçlı)
            english_text = translate_me(user_input)
            status.write(f"🌍 Çeviri: {english_text}")
            
            # 2. Görseli iste
            status.write("📡 Model yanıt veriyor...")
            response = query({"inputs": english_text})
            
            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content))
                st.image(image, caption=f"Sonuç: {user_input}", use_container_width=True)
                
                # İndirme butonu
                buf = io.BytesIO()
                image.save(buf, format="PNG")
                st.download_button("🖼️ Kaydet", buf.getvalue(), "ai_gorsel.png", "image/png")
                status.update(label="✅ Tamamlandı!", state="complete")
            
            elif response.status_code == 503:
                st.error("⏳ Model şu an uyanıyor, lütfen 15 saniye sonra tekrar basın.")
            else:
                st.error(f"❌ Hata oluştu (Kod: {response.status_code})")
                st.write(response.text)

st.divider()
st.caption("Eğer görsel alakasızsa, çevirinin doğru olup olmadığını kontrol edin.")