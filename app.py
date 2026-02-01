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

# En güçlü ve detaylara en çok dikkat eden model: FLUX.1-schnell
API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

st.set_page_config(page_title="BT Görsel Atölyesi v5", layout="centered")

# --- GELİŞMİŞ YARDIMCI FONKSİYOMLAR ---

def advanced_translate_and_clean(text):
    """Metni çevirir, cümleleri birleştirir ve modelin anlayacağı tek bir yapıya sokar."""
    try:
        # Google Translate üzerinden çeviri
        base_url = "https://translate.googleapis.com/translate_a/single"
        params = {"client": "gtx", "sl": "tr", "tl": "en", "dt": "t", "q": text}
        r = requests.get(base_url, params=params, timeout=5)
        raw_translation = "".join([sentence[0] for sentence in r.json()[0]])
        
        # MODEL İÇİN ÖZEL TEMİZLİK: Noktaları virgüle çevirerek modelin 'durmasını' engelliyoruz
        cleaned_text = raw_translation.replace(".", ",").strip()
        if cleaned_text.endswith(","):
            cleaned_text = cleaned_text[:-1]
        return cleaned_text
    except:
        return text

def query_ai(payload):
    """Zenginleştirilmiş payload ile istek atar."""
    response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
    return response

# --- ARAYÜZ ---
st.title("🎨 Detay Odaklı AI Atölyesi")
st.write("Yazdığınız tüm detayları dikkate alan geliştirilmiş versiyon.")

user_input = st.text_area("Tüm detaylarıyla hayalini yaz:", 
                          placeholder="Örn: Ormanda koşan mavi bir robot, arkasında mor ağaçlar var, gökyüzünde iki tane güneş görünüyor...")

if st.button("🚀 Detaylı Görsel Üret"):
    if not HF_TOKEN:
        st.error("🔑 API Token eksik!")
    elif not user_input:
        st.warning("⚠️ Lütfen detaylı bir açıklama girin.")
    else:
        with st.status("🔍 Komut İşleniyor...") as status:
            # 1. Çeviri ve Cümle Birleştirme
            full_prompt = advanced_translate_and_clean(user_input)
            status.write(f"🌍 İşlenmiş İngilizce Komut: **{full_prompt}**")
            
            # 2. Üretim
            status.write("📡 Derinlemesine analiz ve çizim yapılıyor...")
            # 'parameters' kısmını çıkarıp en ham ve güçlü haliyle 'inputs' içine veriyoruz
            response = query_ai({"inputs": full_prompt})
            
            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content))
                st.image(image, caption="Tüm detaylar işlendi.", use_container_width=True)
                
                # İndirme
                buf = io.BytesIO()
                image.save(buf, format="PNG")
                st.download_button("🖼️ İndir", buf.getvalue(), "detayli_gorsel.png", "image/png")
                status.update(label="✅ Çizim Tamamlandı!", state="complete")
            else:
                st.error(f"❌ Hata: {response.status_code}")
                st.write(response.text)

st.divider()
st.caption("İpucu: Cümleleri 've, ile' gibi bağlaçlarla bağlamak modelin odağını korur.")