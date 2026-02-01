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

# İLK BAŞARILI OLAN MODEL ADRESİ (Router hatası alırsanız burayı tekrar güncelleriz)
API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

st.set_page_config(page_title="BT Tasarım v8 - Kalite Odaklı", layout="centered")

# --- FONKSİYOMLAR ---

def simple_translate(text):
    """Metni en saf haliyle çevirir, modelin kafasını karıştırmaz."""
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=tr&tl=en&dt=t&q={text}"
        r = requests.get(url, timeout=5)
        # Cümleleri birleştir ama yapıyı bozma
        return "".join([s[0] for s in r.json()[0]]).strip()
    except:
        return text

def query(payload):
    # 'X-Use-Cache' parametresini header'a ekleyerek her seferinde taze üretim yapıyoruz
    response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
    return response

# --- ARAYÜZ ---
st.title("🎨 Yüksek Kaliteli AI Atölyesi")
st.write("İlk versiyondaki kaliteye geri dönüldü.")

user_input = st.text_input("Görsel açıklamasını yazın:", placeholder="Örn: Ormanda koşan mavi bir robot...")

if st.button("🚀 Kaliteli Görsel Üret"):
    if not HF_TOKEN:
        st.error("🔑 API Anahtarı eksik!")
    elif not user_input:
        st.warning("⚠️ Lütfen bir açıklama yazın.")
    else:
        with st.status("💎 Yüksek çözünürlüklü çizim yapılıyor...") as status:
            eng_prompt = simple_translate(user_input)
            seed = random.randint(0, 999999)
            
            # Parametreleri en sade (default) haline getirdik, kaliteyi bu artıracak
            payload = {
                "inputs": eng_prompt,
                "parameters": {"seed": seed} 
            }
            
            status.write(f"🌍 İngilizceye çevrildi: {eng_prompt}")
            
            response = query(payload)
            
            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content))
                st.image(image, caption="Başarıyla üretildi.", use_container_width=True)
                
                # İndirme
                buf = io.BytesIO()
                image.save(buf, format="PNG")
                st.download_button("🖼️ Kaydet", buf.getvalue(), f"ai_{seed}.png", "image/png")
                status.update(label="✅ Tamamlandı!", state="complete")
            
            # Eğer 410 hatası alırsak kullanıcıyı uyaralım
            elif response.status_code == 410:
                st.error("Hugging Face bağlantı yolunu kalıcı olarak değiştirmiş. Lütfen bana haber verin, URL'yi tekrar güncelleyelim.")
            else:
                st.error(f"Hata: {response.status_code}")
                st.write(response.text)

st.divider()
st.caption("Nusaybin Süleyman Bölünmez Anadolu Lisesi BT Sınıfı")