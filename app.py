import streamlit as st
import requests
import os
import io
from PIL import Image
from dotenv import load_dotenv
import time

# 1. Güvenlik: .env dosyasındaki değişkenleri yükle
load_dotenv()

# 2. Yapılandırma
# Not: .env dosyanızda HF_TOKEN=hf_... şeklinde tanımlı olmalı
API_TOKEN = os.getenv("HF_TOKEN")
# Daha hızlı sonuç için 'stable-diffusion-v1-5' yerine bazen daha hafif modeller seçilebilir
API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
headers = {"Authorization": f"Bearer {API_TOKEN}"}

st.set_page_config(page_title="Yapay Zeka Görsel Oluşturucu", page_icon="🎨")

st.title("🎨 Bilişim Dersi Görsel Üretim Paneli")
st.write("Hugging Face API kullanarak görsel oluşturun. Sunucu yoğunsa otomatik olarak tekrar denenecektir.")

def query_ai(payload, retries=3):
    """
    Hugging Face API'ye istek atar. 
    Timeout ve meşguliyet (503) durumlarını yönetir.
    """
    for i in range(retries):
        try:
            # timeout=180: Sunucuya 3 dakika süre tanıyoruz
            response = requests.post(API_URL, headers=headers, json=payload, timeout=180)
            
            # Eğer model henüz yükleniyorsa (503 hatası)
            if response.status_code == 503:
                estimated_time = response.json().get('estimated_time', 20)
                st.warning(f"Model yükleniyor... {int(estimated_time)} saniye bekleniyor. (Deneme {i+1}/{retries})")
                time.sleep(estimated_time)
                continue
            
            # Başarılı sonuç
            if response.status_code == 200:
                return response.content
            
            # Hata durumu
            else:
                st.error(f"Hata Kodu: {response.status_code} - {response.text}")
                return None

        except requests.exceptions.ReadTimeout:
            if i < retries - 1:
                st.warning("Bağlantı zaman aşımına uğradı, tekrar deneniyor...")
                time.sleep(5)
            else:
                st.error("Üzgünüm, sunucu çok uzun süre cevap vermedi. Lütfen daha sonra tekrar deneyin.")
        except Exception as e:
            st.error(f"Beklenmedik bir hata oluştu: {e}")
            return None
    return None

# Kullanıcı Arayüzü
prompt = st.text_input("Hayalinizdeki görseli tarif edin (İngilizce daha iyi sonuç verir):", 
                       placeholder="A futuristic school with robots and trees...")

if st.button("Görsel Oluştur"):
    if not API_TOKEN:
        st.error("Hata: .env dosyasında HF_TOKEN bulunamadı!")
    elif prompt:
        with st.spinner("Yapay zeka hayal ediyor... Bu işlem 1-2 dakika sürebilir."):
            image_bytes = query_ai({"inputs": prompt})
            
            if image_bytes:
                image = Image.open(io.BytesIO(image_bytes))
                st.image(image, caption=f"Sonuç: {prompt}", use_container_width=True)
                
                # İndirme butonu
                st.download_button(
                    label="Görseli İndir",
                    data=image_bytes,
                    file_name="ai_gorsel.png",
                    mime="image/png"
                )
    else:
        st.warning("Lütfen bir istem (prompt) girin.")

# Alt Bilgi
st.markdown("---")
st.caption("Bilişim Teknolojileri Dersi - Yapay Zeka Uygulamaları Etkinliği")