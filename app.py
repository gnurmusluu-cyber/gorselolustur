import streamlit as st
import requests
import io
import random
from PIL import Image

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="BT Tasarım Merkezi v19", layout="centered")

# Yeni Router Adresi (Hata almamak için güncellendi)
API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"

if "HF_TOKEN" in st.secrets:
    HF_TOKEN = st.secrets["HF_TOKEN"]
else:
    HF_TOKEN = "" # Buraya tokeninizi geçici olarak yazabilirsiniz

headers = {"Authorization": f"Bearer {HF_TOKEN}"}

# --- YARDIMCI FONKSİYOMLAR ---

def translate_it(text):
    """Metni en temiz haliyle İngilizceye çevirir."""
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=tr&tl=en&dt=t&q={text}"
        r = requests.get(url, timeout=10)
        # Tüm parçaları birleştirir, sadece ilk cümleyi almaz
        return "".join([s[0] for s in r.json()[0]]).strip()
    except:
        return text

def query_model(payload):
    """Yeni Router üzerinden modele istek atar."""
    response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
    return response

# --- ARAYÜZ ---
st.title("🎨 Profesyonel Görsel Atölyesi v19")
st.write("Hugging Face Router API üzerinden orijinal FLUX kalitesi.")

user_input = st.text_area("Hayalindeki sahneyi anlat:", placeholder="Örn: Okul bahçesinde bayrak töreni yapan mutlu çocuklar...")

if st.button("🚀 Eskisi Gibi Üret"):
    if not HF_TOKEN:
        st.error("🔑 Lütfen Streamlit Secrets kısmına HF_TOKEN anahtarınızı ekleyin.")
    elif not user_input:
        st.warning("⚠️ Lütfen bir tasarım fikri yazın.")
    else:
        with st.status("💎 Yüksek kaliteli çizim yapılıyor...", expanded=True) as status:
            # 1. Çeviri
            eng_text = translate_it(user_input)
            status.write(f"🌍 Çeviri: {eng_text}")
            
            # 2. Üretim
            seed = random.randint(0, 99999999)
            payload = {
                "inputs": eng_text,
                "parameters": {"seed": seed}
            }
            
            response = query_model(payload)
            
            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content))
                st.image(image, caption="Orijinal Kalite Sonucu", use_container_width=True)
                
                # İndirme Butonu
                st.download_button("🖼️ Tasarımı Kaydet", response.content, f"ai_tasarim_{seed}.png", "image/png")
                status.update(label="✅ Çizim Hazır!", state="complete")
            
            elif response.status_code == 401:
                st.error("❌ Token Hatası: Lütfen API anahtarınızı kontrol edin.")
            elif response.status_code == 503:
                st.warning("⏳ Model şu an hazırlanıyor, lütfen 15-20 saniye sonra tekrar basın.")
            else:
                st.error(f"❌ API Hatası: {response.status_code}")
                st.write(response.text)

st.divider()
st.caption("Nusaybin Süleyman Bölünmez Anadolu Lisesi | Bilişim Teknolojileri")