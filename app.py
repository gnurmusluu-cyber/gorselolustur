import streamlit as st
import requests
import io
import random
import time
from PIL import Image

# Sayfa Yapılandırması
st.set_page_config(page_title="BT Tasarım Merkezi v14", layout="centered")

# --- FONKSİYOMLAR ---

def translate_and_clean(text):
    """Metni çevirir ve net odak komutları ekler."""
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=tr&tl=en&dt=t&q={text}"
        r = requests.get(url, timeout=10)
        translated = "".join([s[0] for s in r.json()[0]]).strip()
        
        # ODAK VE DERİNLİK AYARI: Ön planı netleştirir, arka planı bulanıklaştırır (Bokeh)
        # Bu sayede arka plandaki yüzlerin bozulması önlenir.
        focus_tags = (
            "extreme close-up on foreground, blurred background, bokeh, "
            "sharp focus on main subjects, realistic eyes, detailed facial features, "
            "8k resolution, cinematic lighting, masterpiece"
        )
        return f"{translated}, {focus_tags}"
    except:
        return text

# --- ARAYÜZ ---
st.title("🎨 Profesyonel Görsel Atölyesi v14")
st.write("Arka plan hatalarını önleyen 'Derinlik Odaklı' sistem.")

# Session State ile hata yönetimi
if 'button_disabled' not in st.session_state:
    st.session_state.button_disabled = False

user_input = st.text_area("Hayalini anlat (Ön plandaki kişilere odaklan):", 
                          placeholder="Örn: Gülümseyen bir çocuk, elinde Türk bayrağı tutuyor...")

if st.button("🚀 Üretimi Başlat", disabled=st.session_state.button_disabled):
    if user_input:
        st.session_state.button_disabled = True # Çift tıklamayı engelle
        
        with st.status("🔍 Görüntü işleniyor ve stabilize ediliyor...", expanded=True) as status:
            # 1. Hazırlık
            final_prompt = translate_and_clean(user_input)
            seed = random.randint(1, 1000000000)
            status.write(f"🌍 Komut optimize edildi. (Seed: {seed})")
            
            # 2. Üretim (Flux Pro Motoru)
            image_url = f"https://image.pollinations.ai/prompt/{final_prompt}?width=1024&height=1024&seed={seed}&model=flux&nologo=true"
            
            try:
                # API'yi biraz dinlendirmek için çok kısa bir bekleme
                time.sleep(1) 
                response = requests.get(image_url, timeout=90)
                
                if response.status_code == 200:
                    image = Image.open(io.BytesIO(response.content))
                    st.image(image, caption="Stabilize Edilmiş Sonuç", use_container_width=True)
                    
                    # İndirme
                    st.download_button("🖼️ Görseli Bilgisayara Kaydet", response.content, f"ai_v14_{seed}.png", "image/png")
                    status.update(label="✅ Üretim Başarılı!", state="complete")
                else:
                    st.error(f"Sunucu geçici olarak yanıt vermiyor (Kod: {response.status_code}). Lütfen 10 saniye bekleyip tekrar deneyin.")
                    status.update(label="⚠️ Hata Oluştu", state="error")
            except Exception as e:
                st.error(f"Bağlantı kesildi: {e}")
                status.update(label="❌ Bağlantı Hatası", state="error")
            
            st.session_state.button_disabled = False # Butonu tekrar aç
    else:
        st.warning("Lütfen bir açıklama yazın.")

st.divider()
st.caption("Nusaybin Süleyman Bölünmez Anadolu Lisesi | Bilişim Teknolojileri")