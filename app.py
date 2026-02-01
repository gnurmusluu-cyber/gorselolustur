import streamlit as st
import requests
import io
import os
from PIL import Image

# --- GÜVENLİK: API ANAHTARI YÖNETİMİ ---
# 1. Önce Streamlit Cloud Secrets (İnternet ortamı) kontrol edilir
# 2. Eğer orada yoksa yerel ortam değişkenlerine bakılır
if "HF_TOKEN" in st.secrets:
    HF_TOKEN = st.secrets["HF_TOKEN"]
else:
    # Yerel çalışma için .env desteği (Opsiyonel)
    try:
        from dotenv import load_dotenv
        load_dotenv()
        HF_TOKEN = os.getenv("HF_TOKEN")
    except ImportError:
        HF_TOKEN = os.getenv("HF_TOKEN")

# --- MODELLER ---
MODELS = [
    "black-forest-labs/FLUX.1-schnell",
    "stabilityai/stable-diffusion-xl-base-1.0",
    "runwayml/stable-diffusion-v1-5",
    "prompthero/openjourney"
]

# Sayfa Yapılandırması
st.set_page_config(page_title="BT Tasarım Atölyesi", page_icon="🎨", layout="centered")

# Görsel Arayüz Düzenlemeleri
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; background-color: #2E86C1; color: white; font-weight: bold; }
    .stTextArea>div>div>textarea { border: 2px solid #2E86C1; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎨 Yapay Zeka Görsel Fabrikası")
st.write("Nusaybin Süleyman Bölünmez Anadolu Lisesi - Bilişim Teknolojileri Uygulaması")

# Resim Oluşturma Fonksiyonu
def query_ai(model_id, prompt_text):
    api_url = f"https://api-inference.huggingface.co/models/{model_id}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    response = requests.post(api_url, headers=headers, json={"inputs": prompt_text})
    
    if response.status_code == 200:
        return response.content, 200
    return None, response.status_code

# Kullanıcı Arayüzü
prompt = st.text_area("Ne çizmemi istersin? (İngilizce daha iyi sonuç verir):", 
                      placeholder="A futuristic robot, cybernetic details, high resolution...")

if st.button("🚀 Görseli Oluştur"):
    if not HF_TOKEN:
        st.error("Hata: API Anahtarı bulunamadı! Lütfen Streamlit Secrets veya .env dosyasını kontrol edin.")
    elif not prompt:
        st.warning("Lütfen bir açıklama cümlesi girin.")
    else:
        success = False
        with st.status("🔍 Yapay zeka modelleri kontrol ediliyor...", expanded=True) as status:
            for model in MODELS:
                status.write(f"📡 {model} deneniyor...")
                img_data, status_code = query_ai(model, prompt)
                
                if status_code == 200:
                    image = Image.open(io.BytesIO(img_data))
                    st.image(image, caption=f"Çizim Tamamlandı! Model: {model}", use_container_width=True)
                    
                    # İndirme Butonu
                    buf = io.BytesIO()
                    image.save(buf, format="PNG")
                    st.download_button(label="🖼️ Görseli Kaydet", data=buf.getvalue(), file_name="ai_cikti.png", mime="image/png")
                    
                    status.update(label="✅ Başarılı!", state="complete")
                    success = True
                    break
                elif status_code == 503:
                    status.write(f"⏳ {model} şu an meşgul, sıradakine geçiliyor...")
            
            if not success:
                st.error("Maalesef şu an tüm modeller yoğun. Birkaç dakika sonra tekrar deneyin.")

st.divider()
st.caption("Eğitim amaçlı geliştirilmiştir. | 2026")