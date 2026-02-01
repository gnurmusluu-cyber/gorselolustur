import streamlit as st
import requests
import io
import os
import random
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

# YENİ ROUTER ADRESİ (Zorunlu Güncelleme)
# Not: Modeli URL'nin sonuna ekliyoruz
API_URL_BASE = "https://router.huggingface.co/hf-inference/models/"
MODEL_ID = "black-forest-labs/FLUX.1-schnell"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json",
    "X-Use-Cache": "false" # Her seferinde yeni görsel için önbelleği kapat
}

st.set_page_config(page_title="BT Görsel Atölyesi v7", layout="centered")

# --- FONKSİYOMLAR ---

def translate_and_fix(text):
    """Metni çevirir ve cümleleri modelin anlayacağı tekil yapıya sokar."""
    try:
        base_url = "https://translate.googleapis.com/translate_a/single"
        params = {"client": "gtx", "sl": "tr", "tl": "en", "dt": "t", "q": text}
        r = requests.get(base_url, params=params, timeout=5)
        full_text = "".join([s[0] for s in r.json()[0]])
        # Noktaları virgüle çevirerek modelin tüm cümleyi okumasını sağlıyoruz
        return full_text.replace(".", ",").strip()
    except:
        return text

def query_flux(payload):
    """Hugging Face Router API üzerinden istek atar."""
    endpoint = f"{API_URL_BASE}{MODEL_ID}"
    response = requests.post(endpoint, headers=headers, json=payload, timeout=60)
    return response

# --- ARAYÜZ ---
st.title("🎨 Profesyonel Görsel Tasarım v7")
st.info("Hata Giderildi: Hugging Face Router API (410 Hatası Çözümü)")

user_input = st.text_area("Ne çizelim? (Türkçe detaylı yazabilirsiniz):", 
                          placeholder="Örn: Mavi bir gökyüzü altında, denizde yüzen bir robot...")

if st.button("✨ Görseli Oluştur"):
    if not HF_TOKEN:
        st.error("🔑 API Token bulunamadı! Lütfen ayarlardan HF_TOKEN'ı tanımlayın.")
    elif not user_input:
        st.warning("⚠️ Lütfen bir açıklama girin.")
    else:
        with st.status("🔮 Yapay zeka detayları analiz ediyor...") as status:
            # 1. Çeviri ve Hazırlık
            eng_prompt = translate_and_fix(user_input)
            seed = random.randint(0, 999999)
            
            # 2. İstek Paketi (Payload)
            payload = {
                "inputs": eng_prompt,
                "parameters": {
                    "seed": seed,
                    "target_size": {"width": 1024, "height": 1024}
                }
            }
            
            status.write(f"🌍 Çeviri: {eng_prompt}")
            status.write(f"🎲 Seed: {seed}")
            
            # 3. API Çağrısı
            response = query_flux(payload)
            
            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content))
                st.image(image, caption=f"Başarıyla Üretildi (Seed: {seed})", use_container_width=True)
                
                # İndirme Butonu
                buf = io.BytesIO()
                image.save(buf, format="PNG")
                st.download_button("🖼️ Görseli Bilgisayara Kaydet", buf.getvalue(), f"ai_gorsel_{seed}.png", "image/png")
                status.update(label="✅ İşlem Tamam!", state="complete")
            
            elif response.status_code == 503:
                st.warning("⏳ Model uyanıyor... Lütfen 10 saniye bekleyip tekrar basın.")
            else:
                st.error(f"❌ API Hatası: {response.status_code}")
                st.code(response.text)

st.divider()
st.caption("Nusaybin Süleyman Bölünmez Anadolu Lisesi - Bilişim Teknolojileri")