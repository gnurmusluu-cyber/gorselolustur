import streamlit as st
import requests
import io
import os
import random  # Rastgelelik için eklendi
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

API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "X-Use-Cache": "false"  # Önbelleği devre dışı bırakarak yeni üretim zorlar
}

st.set_page_config(page_title="BT Görsel Atölyesi v6", layout="centered")

# --- YARDIMCI FONKSİYOMLAR ---

def translate_and_clean(text):
    try:
        base_url = "https://translate.googleapis.com/translate_a/single"
        params = {"client": "gtx", "sl": "tr", "tl": "en", "dt": "t", "q": text}
        r = requests.get(base_url, params=params, timeout=5)
        # Tüm parçaları birleştir ve noktaları virgüle çevir
        full_text = "".join([s[0] for s in r.json()[0]])
        return full_text.replace(".", ",").strip()
    except:
        return text

def query_ai(payload):
    response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
    return response

# --- ARAYÜZ ---
st.title("🎨 Dinamik AI Görsel Atölyesi")
st.write("Her 'Oluştur' dediğinde farklı bir sonuç alacaksın.")

user_input = st.text_area("Hayalini yaz:", placeholder="Örn: Karlar içinde bir kedi...")

if st.button("🚀 Yeniden Oluştur"):
    if not HF_TOKEN:
        st.error("🔑 API Token eksik!")
    elif not user_input:
        st.warning("⚠️ Lütfen bir açıklama girin.")
    else:
        with st.status("🔮 Yapay zeka hayal ediyor...") as status:
            # 1. Çeviri
            eng_prompt = translate_and_clean(user_input)
            
            # 2. RASTGELE SEED ÜRETİMİ (Farklılık yaratan anahtar burası)
            random_seed = random.randint(0, 999999999)
            
            # 3. Üretim İsteği
            payload = {
                "inputs": eng_prompt,
                "parameters": {
                    "seed": random_seed,  # Her seferinde farklı bir matematiksel başlangıç
                    "guidance_scale": 7.5
                }
            }
            
            status.write(f"🌍 Çeviri: {eng_prompt}")
            status.write(f"🎲 Rastgelelik Kodu: {random_seed}")
            
            response = query_ai(payload)
            
            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content))
                st.image(image, caption=f"Seed: {random_seed}", use_container_width=True)
                
                # İndirme
                buf = io.BytesIO()
                image.save(buf, format="PNG")
                st.download_button("🖼️ İndir", buf.getvalue(), f"gorsel_{random_seed}.png", "image/png")
                status.update(label="✅ Yeni Görsel Hazır!", state="complete")
            else:
                st.error(f"❌ Hata: {response.status_code}")
                st.write(response.text)

st.divider()
st.caption("Not: Aynı komutla farklı sonuçlar almak için 'Seed' değerini her seferinde değiştiriyoruz.")