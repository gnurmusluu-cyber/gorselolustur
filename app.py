import streamlit as st
import requests
import io
import random
from PIL import Image

# Sayfa Yapılandırması
st.set_page_config(page_title="BT Tasarım Atölyesi v10", page_icon="🎨", layout="centered")

# --- YARDIMCI FONKSİYOMLAR ---

def translate_to_english(text):
    """Google Translate altyapısı ile temiz çeviri yapar."""
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=tr&tl=en&dt=t&q={text}"
        r = requests.get(url, timeout=5)
        return "".join([s[0] for s in r.json()[0]]).strip()
    except:
        return text

# --- ARAYÜZ ---
st.title("🎨 Yüksek Kaliteli Tasarım Atölyesi")
st.write("Detayları kaybetmeyen, yüksek çözünürlüklü yeni nesil motor.")

user_input = st.text_area("Hayalindeki sahneyi anlat:", placeholder="Örn: Mardin'in tarihi sokaklarında yürüyen siber bir şövalye, gün batımı...")

# Stil Seçenekleri (Görseli Güçlendirir)
style_choice = st.selectbox("Görsel Tarzı:", ["Foto-Gerçekçi", "Sanatsal Çizim", "3D Render", "Pixel Art"])
styles = {
    "Foto-Gerçekçi": "photorealistic, 8k, highly detailed, realistic skin, cinematic lighting",
    "Sanatsal Çizim": "oil painting style, vibrant colors, artistic brush strokes, masterpiece",
    "3D Render": "unreal engine 5 render, octane render, 3d isometric, high detail",
    "Pixel Art": "high quality pixel art, 128 bit, retro game style"
}

if st.button("🚀 Yüksek Kalitede Oluştur"):
    if not user_input:
        st.warning("⚠️ Lütfen bir açıklama yazın.")
    else:
        with st.status("💎 Görsel kalitesi optimize ediliyor...") as status:
            # 1. Çeviri ve Kalite Arttırıcı Kelimeler
            eng_prompt = translate_to_english(user_input)
            full_prompt = f"{eng_prompt}, {styles[style_choice]}"
            seed = random.randint(0, 999999)
            
            status.write(f"🌍 İşlenen Komut: {eng_prompt}")
            
            # 2. Yeni Nesil Yüksek Kaliteli API (Flux Pro/Realism tabanlı)
            # Bu link doğrudan en kaliteli görsel motoruna bağlanır
            image_url = f"https://image.pollinations.ai/prompt/{full_prompt}?width=1024&height=1024&seed={seed}&model=flux&nologo=true"
            
            try:
                response = requests.get(image_url, timeout=60)
                if response.status_code == 200:
                    image = Image.open(io.BytesIO(response.content))
                    st.image(image, caption=f"Sonuç: {user_input}", use_container_width=True)
                    
                    # İndirme
                    buf = io.BytesIO()
                    image.save(buf, format="PNG")
                    st.download_button("🖼️ Yüksek Çözünürlüklü Kaydet", buf.getvalue(), f"ai_kalite_{seed}.png", "image/png")
                    status.update(label="✅ Tasarım Başarıyla Tamamlandı!", state="complete")
                else:
                    st.error("Görsel oluşturulurken bir hata oluştu.")
            except Exception as e:
                st.error(f"Bağlantı hatası: {e}")

st.divider()
st.caption("Nusaybin Süleyman Bölünmez Anadolu Lisesi | BT Sınıfı Uygulaması")