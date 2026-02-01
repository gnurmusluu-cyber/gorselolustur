import streamlit as st
import requests
import io
import random
from PIL import Image

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="BT Tasarım Merkezi v20", layout="centered")

# Hugging Face Router Adresi (FLUX Modeli)
API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"

# Token Kontrolü
if "HF_TOKEN" in st.secrets:
    HF_TOKEN = st.secrets["HF_TOKEN"]
else:
    HF_TOKEN = "" # Secrets'a eklemeyi unutmayın

headers = {"Authorization": f"Bearer {HF_TOKEN}"}

# --- AKILLI FONKSİYOMLAR ---

def smart_translate(text):
    """Metni çevirir ve belirli nesneler için (örn: bayrak) detaylı tarif ekler."""
    try:
        # 1. Temel Çeviri
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=tr&tl=en&dt=t&q={text}"
        r = requests.get(url, timeout=10)
        translated = "".join([s[0] for s in r.json()[0]]).strip()

        # 2. BAYRAK KORUMA KALKANI (Flag Protection)
        # Eğer kullanıcı "bayrak" dediyse, yapay zekaya tam tarif veriyoruz.
        if "bayrak" in text.lower():
            # Mevcut basit çeviriyi, detaylı ve kesin bir tarifle değiştiriyoruz.
            # "exactly one star" (tam olarak tek yıldız) ifadesi kritiktir.
            flag_description = "Turkish flag (red banner featuring a white crescent moon and exactly one single white star)"
            
            # Eğer çeviride basitçe "Turkish flag" varsa, onu detaylısıyla değiştir.
            if "Turkish flag" in translated:
                translated = translated.replace("Turkish flag", flag_description)
            else:
                # Yoksa, cümlenin sonuna bu tarifi ekle.
                translated += f", showing a correct {flag_description}"
        
        return translated
    except:
        return text

def query_model(payload):
    """Modele, negatif promptları da içeren paketi gönderir."""
    response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
    return response

# --- YASAKLILAR LİSTESİ (Negative Prompt) ---
# Yapay zekanın çizmemesi gereken şeyler.
NEGATIVE_PROMPT = "extra stars, two stars, wrong flag design, mutated flag, incorrect crescent, deformed symbols, ugly, blurry, low quality"


# --- ARAYÜZ ---
st.title("🎨 Profesyonel Görsel Atölyesi v20")
st.write("Orijinal kalite + Akıllı Nesne Koruması (Bayrak vb. hatalar için).")

user_input = st.text_area("Hayalindeki sahneyi anlat:", placeholder="Örn: Okul bahçesinde büyük bir Türk bayrağı dalgalanıyor...")

if st.button("🚀 Hatasız Üret"):
    if not HF_TOKEN:
        st.error("🔑 Lütfen Streamlit Secrets kısmına HF_TOKEN anahtarınızı ekleyin.")
    elif not user_input:
        st.warning("⚠️ Lütfen bir tasarım fikri yazın.")
    else:
        with st.status("🛡️ Komut optimize ediliyor ve çiziliyor...", expanded=True) as status:
            # 1. Akıllı Çeviri ve Tarif Ekleme
            eng_text = smart_translate(user_input)
            status.write(f"🌍 Detaylandırılmış Komut: {eng_text}")
            
            # 2. Üretim (Yasaklılar listesi ile birlikte)
            seed = random.randint(0, 99999999)
            payload = {
                "inputs": eng_text,
                "parameters": {
                    "seed": seed,
                    "negative_prompt": NEGATIVE_PROMPT # Kritik hataları engelle
                }
            }
            
            response = query_model(payload)
            
            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content))
                st.image(image, caption=f"Sonuç (Seed: {seed})", use_container_width=True)
                
                st.download_button("🖼️ Kaydet", response.content, f"ai_korumali_{seed}.png", "image/png")
                status.update(label="✅ Çizim Başarılı!", state="complete")
            
            elif response.status_code == 503:
                st.warning("⏳ Model hazırlanıyor, 20 saniye sonra tekrar deneyin.")
            else:
                st.error(f"❌ Hata: {response.status_code} - {response.text}")

st.divider()
st.caption("Nusaybin Süleyman Bölünmez Anadolu Lisesi | Bilişim Teknolojileri")