import streamlit as st
import requests
import io
import os
import random
from PIL import Image

# --- GÜVENLİK ---
if "HF_TOKEN" in st.secrets:
    HF_TOKEN = st.secrets["HF_TOKEN"]
else:
    try:
        from dotenv import load_dotenv
        load_dotenv()
        HF_TOKEN = os.getenv("HF_TOKEN")
    except:
        HF_TOKEN = os.getenv("HF_TOKEN")

# YENİ VE KALICI ROUTER URL YAPISI
API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

st.set_page_config(page_title="BT Tasarım v9 - Router Güncel", layout="centered")

# --- FONKSİYOMLAR ---

def translate_to_english(text):
    """Google Translate altyapısı ile temiz çeviri yapar."""
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=tr&tl=en&dt=t&q={text}"
        r = requests.get(url, timeout=5)
        # Tüm parçaları birleştirerek anlam kaybını önler
        return "".join([s[0] for s in r.json()[0]]).strip()
    except:
        return text

def query(payload):
    # Yeni router endpoint'ine istek atar
    response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
    return response

# --- ARAYÜZ ---
st.title("🎨 Profesyonel AI Atölyesi (v9)")
st.info("Hugging Face Router API bağlantısı başarıyla güncellendi.")

user_input = st.text_area("Hayalini tüm detaylarıyla yaz:", placeholder="Örn: Mardin kalesinin üzerinde uçan siberpunk bir ejderha...")

if st.button("🚀 Yüksek Kaliteli Üretim"):
    if not HF_TOKEN:
        st.error("🔑 API Anahtarı eksik! Lütfen Secrets kısmına HF_TOKEN ekleyin.")
    elif not user_input:
        st.warning("⚠️ Lütfen bir açıklama girin.")
    else:
        with st.status("💎 Yeni nesil motor ile çizim yapılıyor...") as status:
            eng_prompt = translate_to_english(user_input)
            seed = random.randint(0, 999999999)
            
            # Kaliteyi korumak için en sade payload yapısı
            payload = {
                "inputs": eng_prompt,
                "parameters": {"seed": seed}
            }
            
            status.write(f"🌍 Çeviri: {eng_prompt}")
            
            response = query(payload)
            
            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content))
                st.image(image, caption=f"Üretilen Görsel (Seed: {seed})", use_container_width=True)
                
                # İndirme
                buf = io.BytesIO()
                image.save(buf, format="PNG")
                st.download_button("🖼️ Bilgisayara Kaydet", buf.getvalue(), f"ai_{seed}.png", "image/png")
                status.update(label="✅ Başarıyla Tamamlandı!", state="complete")
            else:
                st.error(f"❌ Bağlantı Hatası: {response.status_code}")
                st.code(response.text)

st.divider()
st.caption("Nusaybin Süleyman Bölünmez Anadolu Lisesi | Bilişim Teknolojileri")