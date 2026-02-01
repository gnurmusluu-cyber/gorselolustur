import streamlit as st
import requests
import io
import os
from PIL import Image

# --- AYARLAR ---
if "HF_TOKEN" in st.secrets:
    HF_TOKEN = st.secrets["HF_TOKEN"]
else:
    try:
        from dotenv import load_dotenv
        load_dotenv()
        HF_TOKEN = os.getenv("HF_TOKEN")
    except:
        HF_TOKEN = os.getenv("HF_TOKEN")

# Hugging Face Yeni Router URL'si
API_BASE_URL = "https://router.huggingface.co/hf-inference/models/"

# Sadece EN İYİ sonuç veren ana modeller
MODELS = [
    "black-forest-labs/FLUX.1-schnell", 
    "stabilityai/stable-diffusion-xl-base-1.0"
]

st.set_page_config(page_title="BT Tasarım Atölyesi", page_icon="🎨")

# --- YARDIMCI FONKSİYOMLAR ---

def translate_to_english(text):
    """Türkçe komutu İngilizceye çevirir."""
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=tr&tl=en&dt=t&q={text}"
        response = requests.get(url, timeout=5)
        return response.json()[0][0][0]
    except:
        return text

def query_main_model(model_id, prompt_text):
    """Ana Hugging Face modellerine istek atar."""
    api_url = f"{API_BASE_URL}{model_id}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    # Görsel kalitesini artırmak için parametreler eklenebilir
    payload = {
        "inputs": prompt_text,
        "parameters": {"negative_prompt": "blurry, distorted, low quality, bad anatomy"}
    }
    response = requests.post(api_url, headers=headers, json=payload, timeout=40)
    return response

# --- ARAYÜZ ---
st.title("🎨 Profesyonel AI Görsel Atölyesi")
st.markdown("---")

user_input = st.text_input("Ne hayal ediyorsun? (Türkçe yazabilirsin):", 
                           placeholder="Örn: Uzayda futbol oynayan çocuklar...")

if st.button("🚀 Yüksek Kaliteli Görsel Üret"):
    if not HF_TOKEN:
        st.error("🔑 API Anahtarı (Token) eksik!")
    elif not user_input:
        st.warning("⚠️ Lütfen bir açıklama yazın.")
    else:
        with st.status("🛠️ İşleniyor...") as status:
            # 1. Adım: Çeviri
            status.write("🌍 Türkçe komut İngilizceye çevriliyor...")
            eng_prompt = translate_to_english(user_input)
            status.write(f"📝 İngilizce Komut: {eng_prompt}")

            # 2. Adım: Ana Modelleri Dene
            success = False
            for model in MODELS:
                status.write(f"📡 {model} üzerinden yüksek kaliteli üretim yapılıyor...")
                response = query_main_model(model, eng_prompt)
                
                if response.status_code == 200:
                    image = Image.open(io.BytesIO(response.content))
                    st.image(image, caption=f"Sonuç: {user_input}", use_container_width=True)
                    
                    # İndirme butonu
                    buf = io.BytesIO()
                    image.save(buf, format="PNG")
                    st.download_button("🖼️ Görseli Kaydet", buf.getvalue(), "ai_tasarim.png", "image/png")
                    
                    status.update(label="✅ Başarıyla Üretildi!", state="complete")
                    success = True
                    break
                elif response.status_code == 503:
                    status.write(f"⏳ {model} uyanıyor, bekleyiniz...")
                else:
                    status.write(f"❌ {model} hata verdi. Kod: {response.status_code}")
            
            if not success:
                st.error("Üzgünüm, şu an ana modeller çok yoğun. Lütfen 30 saniye sonra tekrar deneyin.")

st.markdown("---")
st.caption("Not: Bu uygulama Hugging Face'in en güçlü modellerini (FLUX/SDXL) kullanır.")