import streamlit as st
import requests
import io
import random
import time
from PIL import Image

st.set_page_config(page_title="BT Tasarım Atölyesi v11", layout="centered")

# --- FONKSİYOMLAR ---

def translate_and_enhance(text):
    """Metni çevirir ve kaliteyi artıracak profesyonel terimler ekler."""
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=tr&tl=en&dt=t&q={text}"
        r = requests.get(url, timeout=10)
        translated = "".join([s[0] for s in r.json()[0]]).strip()
        
        # KALİTE DOPİNGİ: Bu kelimeler görselin 'korkunç' olmasını engeller
        quality_boost = "highly detailed, digital art, masterpiece, cinematic lighting, 8k resolution, trending on artstation, sharp focus"
        return f"{translated}, {quality_boost}"
    except:
        return text

def get_image_with_retry(full_prompt, retries=3):
    seed = random.randint(0, 999999)
    # En güçlü model olan 'flux-pro' seçeneğini deniyoruz
    url = f"https://image.pollinations.ai/prompt/{full_prompt}?width=1024&height=1024&seed={seed}&model=flux&nologo=true"
    
    for i in range(retries):
        try:
            response = requests.get(url, timeout=120)
            if response.status_code == 200:
                return response.content, seed
        except:
            if i < retries - 1:
                time.sleep(3)
                continue
    return None, None

# --- ARAYÜZ ---
st.title("🎨 Profesyonel Görsel Tasarım Merkezi")
st.write("Daha net ve sanatsal sonuçlar için kalite filtreleri eklendi.")

user_input = st.text_input("Hayalindeki sahneyi anlat:", placeholder="Örn: Ormanda yürüyen görkemli bir aslan...")

if st.button("🚀 Yüksek Kalitede Oluştur"):
    if user_input:
        with st.status("💎 Görsel optimize ediliyor ve çiziliyor...", expanded=True) as status:
            # 1. Çeviri ve Kalite Artırma
            enhanced_prompt = translate_and_enhance(user_input)
            status.write(f"🌍 İşlenen Komut: {enhanced_prompt}")
            
            # 2. Üretim
            img_content, current_seed = get_image_with_retry(enhanced_prompt)
            
            if img_content:
                image = Image.open(io.BytesIO(img_content))
                st.image(image, caption="Yüksek Çözünürlüklü Sonuç", use_container_width=True)
                
                # İndirme
                st.download_button("🖼️ Görseli Kaydet", img_content, f"ai_art_{current_seed}.png", "image/png")
                status.update(label="✅ Çizim Tamamlandı!", state="complete")
            else:
                st.error("Sunucu yanıt vermedi, lütfen tekrar deneyin.")
    else:
        st.warning("Lütfen bir açıklama yazın.")

st.divider()
st.caption("Not: Kalite artırıcı filtreler otomatik olarak uygulanmaktadır.")