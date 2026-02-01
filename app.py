import streamlit as st
import requests
import io
import random
import time
from PIL import Image

# Sayfa Yapılandırması
st.set_page_config(page_title="BT Dijital Sanat (Lise Modu)", page_icon="🎨", layout="centered")

# --- FONKSİYOMLAR ---

def anime_style_transfer(text):
    """Metni çevirir ve lise seviyesine uygun 'Stilize Dijital Sanat' formatına sokar."""
    try:
        # 1. Çeviri
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=tr&tl=en&dt=t&q={text}"
        r = requests.get(url, timeout=10)
        translated = "".join([s[0] for s in r.json()[0]]).strip()
        
        # 2. STİL FİLTRESİ: Lise için uygun, temiz ve estetik
        # Gerçekçiliği (photorealism) yasaklıyoruz. Anime/Dijital Sanat'ı zorluyoruz.
        style_prompt = (
            ", anime art style, digital illustration, clean lines, vibrant colors, "
            "detailed background, Makoto Shinkai style, vivid atmosphere, highly polished, "
            "no photorealism, not realistic portraits"
        )
        return f"{translated}{style_prompt}"
    except:
        return text

# --- ARAYÜZ ---
st.title("🎨 Dijital İllüstrasyon Atölyesi")
st.markdown("**Lise Bilişim Sınıfı İçin Özel Sürüm**")
st.write("Modern, temiz çizgiler ve canlı renklerle dijital sanat üretimi.")

# Hata yönetimi için
if 'button_disabled' not in st.session_state:
    st.session_state.button_disabled = False

user_input = st.text_area("Konuyu yazın (Örn: Okulun çatısında siberpunk bir öğrenci):", 
                          placeholder="Fikirlerini buraya yaz, dijital sanata dönüşsün...")

if st.button("✨ Dijital Sanat Oluştur", disabled=st.session_state.button_disabled):
    if user_input:
        st.session_state.button_disabled = True
        
        with st.status("🎨 İllüstrasyon çiziliyor...", expanded=True) as status:
            # 1. Hazırlık
            stylized_prompt = anime_style_transfer(user_input)
            seed = random.randint(1, 999999)
            status.write("🌍 Komut, dijital sanat stiline uyarlandı.")
            
            # 2. Üretim (Yine FLUX, ama prompt ile stilize edilmiş)
            # enhance=true parametresi renkleri ve detayları canlandırır
            image_url = f"https://image.pollinations.ai/prompt/{stylized_prompt}?width=1024&height=1024&seed={seed}&model=flux&nologo=true&enhance=true"
            
            try:
                time.sleep(1.5) # Sunucu yoğunluğuna karşı bekleme
                response = requests.get(image_url, timeout=75)
                
                if response.status_code == 200:
                    image = Image.open(io.BytesIO(response.content))
                    st.image(image, caption="Dijital İllüstrasyon Sonucu", use_container_width=True)
                    
                    st.download_button("💾 Çalışmayı Kaydet", response.content, f"dijital_sanat_{seed}.png", "image/png")
                    status.update(label="✅ Tamamlandı!", state="complete")
                else:
                    st.error(f"Sunucu şu an çok yoğun (Hata: {response.status_code}). Lütfen 10-15 saniye sonra tekrar deneyin.")
                    status.update(label="⚠️ Geçici Yoğunluk", state="error")
            except Exception as e:
                st.error("Bağlantı zaman aşımına uğradı. İnternet hızından kaynaklı olabilir.")
                status.update(label="❌ Bağlantı Hatası", state="error")
            
            st.session_state.button_disabled = False
    else:
        st.warning("Lütfen bir konu girin.")

st.divider()
st.caption("Not: Bu mod, korkutucu gerçekçilik yerine estetik çizimlere odaklanır.")