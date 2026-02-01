import streamlit as st
import requests
import io
import os
from PIL import Image

# --- AYARLAR VE GÜVENLİK ---
if "HF_TOKEN" in st.secrets:
    HF_TOKEN = st.secrets["HF_TOKEN"]
else:
    try:
        from dotenv import load_dotenv
        load_dotenv()
        HF_TOKEN = os.getenv("HF_TOKEN")
    except:
        HF_TOKEN = os.getenv("HF_TOKEN")

API_BASE_URL = "https://router.huggingface.co/hf-inference/models/"
MODELS = ["black-forest-labs/FLUX.1-schnell", "stabilityai/stable-diffusion-xl-base-1.0"]

st.set_page_config(page_title="BT Tasarım Akademisi", layout="wide")

# --- YARDIMCI FONKSİYOMLAR ---

# 1. OTOMATİK ÇEVİRİ DESTEĞİ (Google Translate API - Ücretsiz)
def translate_to_english(text):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=tr&tl=en&dt=t&q={text}"
        response = requests.get(url)
        return response.json()[0][0][0]
    except:
        return text # Hata olursa orijinali gönder

# 2. ANA MODEL (Hugging Face)
def generate_hf(model_id, prompt_text):
    api_url = f"{API_BASE_URL}{model_id}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    response = requests.post(api_url, headers=headers, json={"inputs": prompt_text}, timeout=30)
    return response.content, response.status_code

# 3. YENİ YEDEK MODEL (Daha Stabil)
def generate_backup(prompt_text):
    # Prodia veya Pollinations alternatif (v2)
    url = f"https://image.pollinations.ai/prompt/{prompt_text}?width=1024&height=1024&model=flux&nologo=true"
    response = requests.get(url)
    return response.content

# --- ARAYÜZ ---
st.title("🎨 Akıllı Görsel Tasarım Atölyesi")
st.write("Türkçe yazabilirsiniz, sistem otomatik olarak İngilizceye çevirecektir.")

user_input = st.text_area("Ne hayal ediyorsun? (Örn: Ormanda koşan mavi bir robot)", height=100)

# Stil Seçenekleri
style = st.selectbox("Görsel Stili Seç:", ["Gerçekçi", "Pixel Art", "Dijital Sanat", "Siberpunk", "Anime"])
style_prompts = {
    "Gerçekçi": "high resolution, photorealistic, 8k, cinematic lighting",
    "Pixel Art": "pixel art, 8-bit style, retro gaming aesthetic",
    "Dijital Sanat": "digital art, concept art, vibrant colors, trending on artstation",
    "Siberpunk": "cyberpunk style, neon lights, futuristic, dark atmosphere",
    "Anime": "anime style, studio ghibli aesthetic, clean lines"
}

if st.button("🚀 Tasarımı Oluştur"):
    if not user_input:
        st.warning("Lütfen bir açıklama yazın.")
    else:
        # OTOMATİK ÇEVİRİ VE PROMPT GÜÇLENDİRME
        with st.status("🔄 İşlemler yapılıyor...") as status:
            status.write("📝 Türkçe metin İngilizceye çevriliyor...")
            english_prompt = translate_to_english(user_input)
            full_prompt = f"{english_prompt}, {style_prompts[style]}"
            status.write(f"🌍 Çeviri: {english_prompt}")
            
            # ANA MODEL DENEMESİ
            status.write("📡 Ana modellerle bağlantı kuruluyor...")
            img_data, status_code = generate_hf(MODELS[0], full_prompt)
            
            if status_code == 200:
                st.image(Image.open(io.BytesIO(img_data)), caption=f"Tasarım: {user_input}")
                status.update(label="✅ Başarılı!", state="complete")
            else:
                # YEDEK MODEL DEVREYE GİRER
                status.write("⚠️ Ana modeller yoğun, yedek motor çalıştırılıyor...")
                backup_data = generate_backup(full_prompt)
                st.image(backup_data, caption=f"Yedek Model ile üretildi: {user_input}")
                status.update(label="✅ Yedek Model ile Tamamlandı!", state="complete")

st.divider()
st.info(f"💡 **Öğrenciler için not:** Senin yazdığın '{user_input}' ifadesi, yapay zekaya daha iyi anlaması için otomatik olarak çevrildi.")