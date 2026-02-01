import streamlit as st
import requests
import io
import random
from PIL import Image

# Sayfa ayarları
st.set_page_config(page_title="BT Tasarım Atölyesi", layout="centered")

def translate_to_english(text):
    """Metni en temiz şekilde çevirir ve talimatları ayıklar."""
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=tr&tl=en&dt=t&q={text}"
        r = requests.get(url, timeout=10)
        return "".join([s[0] for s in r.json()[0]]).strip()
    except:
        return text

# --- ARAYÜZ ---
st.title("🎨 Profesyonel Görsel Üretim v12")
st.write("Nusaybin Süleyman Bölünmez Anadolu Lisesi | Kalite ve Hız Odaklı")

user_input = st.text_area("Ne çizmek istiyorsun?", 
                          placeholder="Örn: Okul bahçesinde bayrak töreni yapan çocuklar...")

if st.button("🚀 Hatasız Üret"):
    if user_input:
        with st.status("💎 Görsel Kalitesi Optimize Ediliyor...", expanded=True) as status:
            # 1. Çeviri
            eng_prompt = translate_to_english(user_input)
            
            # 2. PROMPT MÜHENDİSLİĞİ (Yüzleri düzelten sihirli kelimeler)
            # Karmaşık cümleler yerine net görsel tanımları ekliyoruz
            magic_tags = "professional photography, hyper-realistic, 8k, highly detailed faces, clear eyes, cinematic lighting, masterpiece, sharp focus, vibrant colors"
            final_prompt = f"{eng_prompt}, {magic_tags}"
            
            # 3. GÜVENLİ BAĞLANTI (404 Hatasını engelleyen direkt yol)
            seed = random.randint(0, 999999)
            # 'model=flux' sayesinde en kaliteli çizimi zorunlu kılıyoruz
            image_url = f"https://image.pollinations.ai/prompt/{final_prompt}?width=1024&height=1024&seed={seed}&model=flux&nologo=true"
            
            try:
                response = requests.get(image_url, timeout=90)
                if response.status_code == 200:
                    image = Image.open(io.BytesIO(response.content))
                    st.image(image, caption="Yapay Zeka Tasarımı Tamamlandı", use_container_width=True)
                    
                    # İndirme
                    st.download_button("🖼️ Görseli Bilgisayara Kaydet", response.content, f"ai_tasarim_{seed}.png", "image/png")
                    status.update(label="✅ Çizim Hazır!", state="complete")
                else:
                    st.error(f"⚠️ Sunucu yanıt vermedi. Hata kodu: {response.status_code}")
            except Exception as e:
                st.error(f"Bağlantı kesildi: {e}")
    else:
        st.warning("Lütfen bir açıklama yazın.")

st.divider()
st.caption("Not: Yüzlerin daha net olması için FLUX motoru aktif edildi.")