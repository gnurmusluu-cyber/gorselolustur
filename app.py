import streamlit as st
import requests
import io
import random
import time
from PIL import Image

# Sayfa Yapılandırması
st.set_page_config(page_title="BT Tasarım Merkezi", layout="centered")

# --- FONKSİYOMLAR ---

def translate_text(text):
    """Basit ve hızlı çeviri."""
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=tr&tl=en&dt=t&q={text}"
        r = requests.get(url, timeout=10)
        return "".join([s[0] for s in r.json()[0]]).strip()
    except:
        return text

def get_image_with_retry(prompt_text, retries=3):
    """Zaman aşımına karşı 3 kez deneme yapar."""
    seed = random.randint(0, 999999)
    # Daha hızlı yanıt veren ve kaliteli 'Flux' motorunu zorla seçiyoruz
    url = f"https://image.pollinations.ai/prompt/{prompt_text}?width=1024&height=1024&seed={seed}&model=flux&nologo=true"
    
    for i in range(retries):
        try:
            # Zaman aşımını 120 saniyeye çıkardık
            response = requests.get(url, timeout=120)
            if response.status_code == 200:
                return response.content, seed
        except requests.exceptions.RequestException:
            if i < retries - 1:
                time.sleep(2) # Hata olursa 2 saniye bekle ve tekrar dene
                continue
    return None, None

# --- ARAYÜZ ---
st.title("🎨 Profesyonel Görsel Atölyesi")
st.write("Nusaybin Süleyman Bölünmez Anadolu Lisesi | BT Sınıfı")

user_input = st.text_input("Ne hayal ediyorsun?", placeholder="Örn: Karlı dağların üzerinde uçan görkemli bir ejderha...")

if st.button("🚀 Tasarımı Başlat"):
    if user_input:
        with st.status("📡 Sunucuya bağlanılıyor ve çiziliyor...", expanded=True) as status:
            # 1. Çeviri
            status.write("🌍 Komut İngilizceye çevriliyor...")
            eng_prompt = translate_text(user_input)
            
            # 2. Üretim (Retry mekanizmalı)
            status.write("🎨 Görsel oluşturuluyor (Bu işlem 1 dakika sürebilir)...")
            img_content, current_seed = get_image_with_retry(eng_prompt)
            
            if img_content:
                image = Image.open(io.BytesIO(img_content))
                st.image(image, caption=f"Sonuç: {user_input}", use_container_width=True)
                
                # İndirme
                st.download_button(
                    label="🖼️ Resmi Bilgisayara Kaydet",
                    data=img_content,
                    file_name=f"ai_tasarim_{current_seed}.png",
                    mime="image/png"
                )
                status.update(label="✅ Çizim Hazır!", state="complete")
            else:
                st.error("❌ Sunucu şu an çok yoğun. Lütfen 15 saniye sonra tekrar deneyin.")
                status.update(label="⚠️ Bağlantı Zaman Aşımına Uğradı", state="error")
    else:
        st.warning("Lütfen bir açıklama yazın.")

st.divider()
st.caption("Not: Eğer görsel 'korkunç' gelirse, açıklamanıza 'beautiful, high quality, masterpiece' gibi kelimeler ekleyin.")