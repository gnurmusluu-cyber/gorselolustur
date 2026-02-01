import streamlit as st
import requests
import io
import random
import time
from PIL import Image

st.set_page_config(page_title="BT Profesyonel Tasarım", layout="centered")

# --- SABİT AYARLAR ---
# Bu liste, bozuk yüzlerin ve vücutların oluşmasını engeller.
NEGATIVE_PROMPT = "ugly, deformed, noisy, blurry, distorted, out of focus, bad anatomy, extra limbs, poorly drawn face, poorly drawn hands, missing fingers, mutated, disfigured"

# --- FONKSİYOMLAR ---

def translate_to_english(text):
    """Türkçe metni İngilizceye çevirir."""
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=tr&tl=en&dt=t&q={text}"
        r = requests.get(url, timeout=5)
        return "".join([s[0] for s in r.json()[0]]).strip()
    except:
        return text

def generate_with_negative_prompt(positive_prompt):
    """Negatif prompt desteği ile profesyonel istek atar."""
    # Pollinations'ın gelişmiş POST servisi
    url = "https://image.pollinations.ai/p"
    seed = random.randint(0, 999999)
    
    # Yapay zekaya gönderilen profesyonel paket
    payload = {
        "prompt": positive_prompt,      # Ne istiyoruz?
        "negative_prompt": NEGATIVE_PROMPT, # Ne İSTEMİYORUZ? (Düzgün yüzler için kritik)
        "model": "flux",                # En kaliteli model
        "width": 1024,
        "height": 1024,
        "seed": seed,
        "nologo": True
    }
    
    try:
        # Daha sağlam bir bağlantı yöntemi (POST)
        response = requests.post(url, json=payload, timeout=90)
        if response.status_code == 200:
            return response.content, seed
        else:
            st.error(f"Sunucu hatası: {response.status_code}")
            return None, None
    except Exception as e:
        st.error(f"Bağlantı sorunu: {e}")
        return None, None

# --- ARAYÜZ ---
st.title("🎨 BT Sınıfı - Hatasız Görsel Motoru")
st.info("Bu versiyon, bozuk yüzleri ve hatalı çizimleri otomatik olarak engeller.")

user_input = st.text_area("Ne çizmek istiyorsun?", placeholder="Örn: Parkta oynayan mutlu bir çocuk...")

if st.button("✨ Hatasız Oluştur"):
    if not user_input:
        st.warning("Lütfen bir açıklama yazın.")
    else:
        with st.status("🛠️ Çizim yapılıyor (Yüzler düzeltiliyor)...", expanded=True) as status:
            # 1. Çeviri
            eng_prompt = translate_to_english(user_input)
            # Kaliteyi artıracak ek terimler
            full_prompt = f"{eng_prompt}, masterpiece, highly detailed, sharp focus"
            status.write(f"🌍 İşlenen Komut: {full_prompt}")
            
            # 2. Üretim (Negatif Promptlu)
            img_content, seed = generate_with_negative_prompt(full_prompt)
            
            if img_content:
                image = Image.open(io.BytesIO(img_content))
                st.image(image, caption="Düzeltilmiş Sonuç", use_container_width=True)
                
                # İndirme
                st.download_button("🖼️ Kaydet", img_content, f"temiz_gorsel_{seed}.png", "image/png")
                status.update(label="✅ Tamamlandı!", state="complete")
            else:
                status.update(label="❌ Başarısız Oldu", state="error")

st.divider()
st.caption("Nusaybin Süleyman Bölünmez Anadolu Lisesi")