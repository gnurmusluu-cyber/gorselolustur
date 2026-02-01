import streamlit as st
import requests
import io
import random
from PIL import Image

# Sayfa tasarımı
st.set_page_config(page_title="BT Görsel Atölyesi", layout="centered")

# --- FONKSİYOMLAR ---

def translate_to_english(text):
    """Türkçe yazılanı arka planda İngilizceye çevirir."""
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=tr&tl=en&dt=t&q={text}"
        r = requests.get(url, timeout=5)
        return "".join([s[0] for s in r.json()[0]]).strip()
    except:
        return text

def generate_image(prompt_text):
    """Güvenilir ve anahtarsız bir yüksek kalite motoru kullanır."""
    seed = random.randint(0, 999999)
    # Pollinations'ın en güncel ve kaliteli motoru (v-turbo)
    url = f"https://image.pollinations.ai/prompt/{prompt_text}?width=1024&height=1024&seed={seed}&nologo=true&enhance=true"
    response = requests.get(url, timeout=60)
    return response.content, seed

# --- ARAYÜZ ---
st.title("🎨 Yapay Zeka Tasarım Atölyesi")
st.write("Nusaybin Süleyman Bölünmez Anadolu Lisesi | BT Sınıfı")

user_input = st.text_input("Ne çizmek istersin?", placeholder="Örn: Uzayda piknik yapan bir robot ailesi...")

if st.button("🚀 Görseli Oluştur"):
    if user_input:
        with st.spinner("Çiziliyor, lütfen bekleyin..."):
            # 1. Çeviri
            eng_prompt = translate_to_english(user_input)
            # 2. Üretim
            img_content, current_seed = generate_image(eng_prompt)
            
            # 3. Gösterim
            image = Image.open(io.BytesIO(img_content))
            st.image(image, caption=f"Sonuç: {user_input}", use_container_width=True)
            
            # İndirme butonu
            st.download_button(
                label="🖼️ Resmi Bilgisayara Kaydet",
                data=img_content,
                file_name=f"tasarim_{current_seed}.png",
                mime="image/png"
            )
    else:
        st.warning("Lütfen bir açıklama yazın.")

st.divider()
st.caption("Not: Görsel beklediğiniz gibi değilse, daha fazla detay ekleyerek tekrar deneyin.")