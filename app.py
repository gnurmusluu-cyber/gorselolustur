import streamlit as st
import requests
import io
import os
from PIL import Image

# --- GÜVENLİK VE AYARLAR ---
if "HF_TOKEN" in st.secrets:
    HF_TOKEN = st.secrets["HF_TOKEN"]
else:
    try:
        from dotenv import load_dotenv
        load_dotenv()
        HF_TOKEN = os.getenv("HF_TOKEN")
    except:
        HF_TOKEN = os.getenv("HF_TOKEN")

# YENİ API ADRESİ (Hata mesajındaki router adresi)
API_BASE_URL = "https://router.huggingface.co/hf-inference/models/"

MODELS = [
    "black-forest-labs/FLUX.1-schnell",
    "stabilityai/stable-diffusion-xl-base-1.0",
    "runwayml/stable-diffusion-v1-5"
]

st.set_page_config(page_title="BT Sınıfı AI Tasarım", page_icon="🎨")

st.title("🎨 Yapay Zeka Görsel Üretim Paneli")
st.info("Hata Giderildi: Hugging Face Router API Yapılandırması Aktif.")

def generate_image(model_id, prompt_text):
    # Yeni router endpoint yapısı
    api_url = f"{API_BASE_URL}{model_id}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    try:
        response = requests.post(api_url, headers=headers, json={"inputs": prompt_text}, timeout=30)
        return response.content, response.status_code, response.text
    except Exception as e:
        return None, 500, str(e)

# --- ANAHTARSIZ YEDEK MODEL (Pollinations AI) ---
def generate_backup_image(prompt_text):
    # Bu model anahtar istemez, dersin kurtarıcısıdır.
    url = f"https://image.pollinations.ai/prompt/{prompt_text}?width=1024&height=1024&nologo=true"
    response = requests.get(url)
    return response.content

prompt = st.text_area("Hayalindekini İngilizce yaz:", placeholder="A futuristic classroom in Mardin...")

col1, col2 = st.columns(2)

with col1:
    main_button = st.button("🚀 Ana Modellerle Üret")
with col2:
    backup_button = st.button("🆘 Yedek Model (Hızlı)")

if main_button:
    if not HF_TOKEN:
        st.error("🔑 Token bulunamadı!")
    else:
        success = False
        with st.status("📡 Yeni Router üzerinden bağlanılıyor...") as status:
            for model in MODELS:
                img_data, status_code, error_msg = generate_image(model, prompt)
                if status_code == 200:
                    st.image(Image.open(io.BytesIO(img_data)), caption=f"Model: {model}")
                    success = True
                    status.update(label="✅ Başarılı!", state="complete")
                    break
            if not success:
                st.error("Hugging Face hala meşgul. Lütfen 'Yedek Model' butonunu deneyin.")

if backup_button:
    with st.spinner("Yedek motor çalışıyor..."):
        img_data = generate_backup_image(prompt)
        st.image(img_data, caption="Yedek Model (Pollinations AI) ile üretildi.")
        st.success("Ders devam ediyor! Yedek model başarıyla çalıştı.")

st.divider()
st.caption("Nusaybin Süleyman Bölünmez Anadolu Lisesi | Bilişim Teknolojileri")