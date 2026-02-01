import streamlit as st
import requests
import io
import random
from PIL import Image

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="BT Tasarım Atölyesi (Orijinal Kalite)", layout="centered")

# API Ayarı (Hugging Face Token'ınızı buraya veya Secrets'a ekleyin)
if "HF_TOKEN" in st.secrets:
    HF_TOKEN = st.secrets["HF_TOKEN"]
else:
    HF_TOKEN = "BURAYA_TOKEN_YAZIN" # GitHub'a yüklerken Secrets kullanın!

# Sizin beğendiğiniz o efsane modelin adresi
API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

# --- FONKSİYOMLAR ---

def translate_it(text):
    """En sade çeviri, modeli yormaz."""
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=tr&tl=en&dt=t&q={text}"
        r = requests.get(url, timeout=10)
        return "".join([s[0] for s in r.json()[0]]).strip()
    except:
        return text

def query(payload):
    """Doğrudan modele en kaliteli haliyle bağlanır."""
    response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
    return response

# --- ARAYÜZ ---
st.title("🎨 Orijinal AI Görsel Atölyesi")
st.write("İlk versiyonun o çok sevilen yüksek kaliteli motoruna geri dönüldü.")

user_input = st.text_input("Görsel fikrini yazın:", placeholder="Örn: Mardin Kalesi üzerinde uçan bir robot...")

if st.button("🚀 Eskisi Gibi Üret"):
    if not user_input:
        st.warning("⚠️ Bir şeyler yazmalısın.")
    elif HF_TOKEN == "BURAYA_TOKEN_YAZIN":
        st.error("🔑 Lütfen Streamlit Secrets'a HF_TOKEN ekleyin.")
    else:
        with st.status("💎 Yüksek kaliteli çizim yapılıyor...", expanded=True) as status:
            # 1. Çeviri
            eng_text = translate_it(user_input)
            status.write(f"🌍 İngilizceye çevrildi: {eng_text}")
            
            # 2. Üretim (En sade ve güçlü hali)
            seed = random.randint(0, 999999)
            payload = {
                "inputs": eng_text,
                "parameters": {"seed": seed}
            }
            
            response = query(payload)
            
            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content))
                st.image(image, caption=f"Efsane Geri Döndü! (Seed: {seed})", use_container_width=True)
                
                # İndirme
                st.download_button("🖼️ Görseli Kaydet", response.content, f"ai_original_{seed}.png", "image/png")
                status.update(label="✅ İşte Bu!", state="complete")
            
            elif response.status_code == 503:
                st.warning("⏳ Model şu an yükleniyor (uyandırılıyor), lütfen 20 saniye sonra tekrar basın.")
            else:
                st.error(f"❌ Bağlantı Hatası: {response.status_code}")
                st.code(response.text)

st.divider()
st.caption("Nusaybin Süleyman Bölünmez Anadolu Lisesi - Orijinal FLUX Versiyonu")