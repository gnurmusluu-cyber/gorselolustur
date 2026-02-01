import streamlit as st
import requests
import io
import os
from PIL import Image

# --- GÜVENLİK VE AYARLAR ---
# Streamlit Secrets veya Yerel Ortamdan Token'ı al
if "HF_TOKEN" in st.secrets:
    HF_TOKEN = st.secrets["HF_TOKEN"]
else:
    try:
        from dotenv import load_dotenv
        load_dotenv()
        HF_TOKEN = os.getenv("HF_TOKEN")
    except ImportError:
        HF_TOKEN = os.getenv("HF_TOKEN")

# Ücretsiz katmanda en stabil çalışan güncel modeller
MODELS = [
    "black-forest-labs/FLUX.1-schnell",  # Çok hızlı ve kaliteli
    "stabilityai/stable-diffusion-2-1",  # Stabil ve erişilebilir
    "runwayml/stable-diffusion-v1-5",    # Klasik ve hızlı
    "Lykon/AnyLoRA"                      # Alternatif hızlı model
]

st.set_page_config(page_title="BT Sınıfı AI Tasarım", page_icon="🎨")

# Arayüz Tasarımı
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 15px; height: 3em; background-color: #FF4B4B; color: white; }
    .reportview-container { background: #f0f2f6; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎨 Yapay Zeka Görsel Üretim Paneli")
st.info("Nusaybin Süleyman Bölünmez Anadolu Lisesi BT Sınıfı Projesi")

# Görsel Oluşturma Fonksiyonu (Hata Ayıklama Destekli)
def generate_image(model_id, prompt_text):
    api_url = f"https://api-inference.huggingface.co/models/{model_id}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    try:
        response = requests.post(api_url, headers=headers, json={"inputs": prompt_text}, timeout=30)
        
        # Eğer model yükleniyorsa (503), kullanıcıya bildirmek için status_code döndür
        return response.content, response.status_code, response.text
    except Exception as e:
        return None, 500, str(e)

# Kullanıcı Girişi
prompt = st.text_area("Hayalindekini buraya yaz (İngilizce önerilir):", 
                      placeholder="A futuristic city in Mesopotamia, 4k, cinematic lighting...")

if st.button("✨ Tasarımı Başlat"):
    if not HF_TOKEN or HF_TOKEN == "":
        st.error("❌ HATA: API Anahtarı bulunamadı! Lütfen Secrets ayarlarına HF_TOKEN ekleyin.")
    elif not prompt:
        st.warning("⚠️ Lütfen bir açıklama girin.")
    else:
        success = False
        with st.status("🚀 Yapay zeka motorları çalışıyor...", expanded=True) as status:
            for model in MODELS:
                status.write(f"📡 {model} deneniyor...")
                img_data, status_code, error_msg = generate_image(model, prompt)
                
                if status_code == 200:
                    image = Image.open(io.BytesIO(img_data))
                    st.image(image, caption=f"Başarıyla üretildi! (Model: {model})", use_container_width=True)
                    
                    # İndirme Butonu
                    buf = io.BytesIO()
                    image.save(buf, format="PNG")
                    st.download_button("🖼️ Görseli Kaydet", buf.getvalue(), "ai_tasarim.png", "image/png")
                    
                    status.update(label="✅ Başarılı!", state="complete")
                    success = True
                    break
                
                elif status_code == 503:
                    status.write(f"⏳ {model} şu an uyanıyor (yükleniyor), sıradakine geçiliyor...")
                elif status_code == 401 or status_code == 403:
                    st.error(f"🔑 Yetkilendirme Hatası! Token'ınızı kontrol edin. (Hata: {status_code})")
                    break
                else:
                    status.write(f"❌ {model} meşgul veya hata verdi. (Kod: {status_code})")
            
            if not success:
                st.error("❌ Şu an tüm modeller yoğun veya Token hatası var. Lütfen 1 dakika bekleyip tekrar deneyin.")
                st.expander("Teknik Hata Detayı").write(error_msg)

st.divider()
st.caption("Bilişim Teknolojileri Öğretmenliği - Yapay Zeka Uygulamaları")