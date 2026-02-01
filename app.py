import streamlit as st
import requests
import io
import random
import time
from PIL import Image

# Sayfa Yapılandırması
st.set_page_config(page_title="BT Masal Atölyesi (Güvenli Mod)", layout="centered")

# --- FONKSİYOMLAR ---

def make_it_cute_and_safe(text):
    """Metni çevirir ve KORKUTUCU OLMAYAN, sevimli bir çizim stiline zorlar."""
    try:
        # 1. Çeviri
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=tr&tl=en&dt=t&q={text}"
        r = requests.get(url, timeout=5)
        translated = "".join([s[0] for s in r.json()[0]]).strip()
        
        # 2. GÜVENLİK VE STİL FİLTRESİ (Kritik Kısım)
        # Gerçekçiliği yasaklıyoruz, sevimli illüstrasyon stilini zorluyoruz.
        safe_style = (
            ", children's book illustration style, cute, friendly faces, "
            "whimsical, watercolor and ink, gentle colors, Studio Ghibli vibe, "
            "no photorealism, not realistic, cartoon style"
        )
        return f"{translated} {safe_style}"
    except:
        return text

# --- ARAYÜZ ---
st.title("🎨 BT Masal Çizim Atölyesi")
st.write("Çocuklar için güvenli, sevimli masal kitabı tarzında çizimler.")

# Hata yönetimi için oturum durumu
if 'button_disabled' not in st.session_state:
    st.session_state.button_disabled = False

user_input = st.text_area("Hayalini anlat (Örn: Uçan balonla gezen mutlu bir kedi):", 
                          placeholder="Buraya yazılan her şey sevimli bir çizime dönüşecek...")

if st.button("✨ Sevimli Çizimi Başlat", disabled=st.session_state.button_disabled):
    if user_input:
        st.session_state.button_disabled = True
        
        with st.status("🎨 Masal kitabı sayfası hazırlanıyor...", expanded=True) as status:
            # 1. Hazırlık ve Stil Uygulama
            friendly_prompt = make_it_cute_and_safe(user_input)
            seed = random.randint(1, 999999)
            status.write("🌍 Komut sevimli hale getirildi.")
            
            # 2. Üretim (Yine FLUX kullanıyoruz ama stilini değiştirdik)
            # 'nologo=true' ile filigranları da kaldırıyoruz ki temiz görünsün.
            image_url = f"https://image.pollinations.ai/prompt/{friendly_prompt}?width=1024&height=1024&seed={seed}&model=flux&nologo=true"
            
            try:
                time.sleep(1) # Sunucuya nefes aldır
                response = requests.get(image_url, timeout=60)
                
                if response.status_code == 200:
                    image = Image.open(io.BytesIO(response.content))
                    st.image(image, caption="Sevimli Masal Çizimi", use_container_width=True)
                    
                    st.download_button("🖼️ Bu Resmi Kaydet", response.content, f"masal_{seed}.png", "image/png")
                    status.update(label="✅ Çizim Bitti!", state="complete")
                else:
                    st.error("Sunucu şu an yoğun, birazdan tekrar deneyelim.")
                    status.update(label="⚠️ Geçici Yoğunluk", state="error")
            except Exception as e:
                st.error("İnternet bağlantısında bir sorun oldu.")
                status.update(label="❌ Bağlantı Hatası", state="error")
            
            st.session_state.button_disabled = False
    else:
        st.warning("Lütfen bir şeyler yazın.")

st.divider()
st.caption("Nusaybin Süleyman Bölünmez Anadolu Lisesi | Güvenli BT Sınıfı")