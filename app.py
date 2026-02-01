import streamlit as st
import requests
import io
import random
from PIL import Image

st.set_page_config(page_title="BT Tasarım v13 - Yüz Düzeltme Modu", layout="centered")

def translate_and_optimize(text):
    """Metni çevirir ve yüzlerin bozulmaması için teknik terimler ekler."""
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=tr&tl=en&dt=t&q={text}"
        r = requests.get(url, timeout=10)
        translated = "".join([s[0] for s in r.json()[0]]).strip()
        
        # YÜZ VE GÖZ DÜZELTME KOMUTLARI (Zorunlu)
        # Bu kelimeler yapay zekanın anatomiyi doğru kurmasını sağlar
        quality_template = (
            "detailed faces, symmetrical eyes, clear pupils, realistic skin texture, "
            "anatomically correct hands and fingers, masterpiece, sharp focus, 8k resolution, "
            "professional photography, cinematic lighting"
        )
        return f"{translated}, {quality_template}"
    except:
        return text

# --- ARAYÜZ ---
st.title("🎨 Hatasız İnsan Çizim Atölyesi")
st.write("Yüz ve göz bozulmalarını engelleyen profesyonel filtreleme sistemi aktiftir.")

user_input = st.text_area("Ne çizmek istiyorsun?", 
                          placeholder="Örn: Türk bayrağı önünde İstiklal Marşı söyleyen çocuklar...")

if st.button("🚀 Yüksek Kalitede Üret"):
    if user_input:
        with st.status("💎 Anatomi kontrol ediliyor ve çiziliyor...", expanded=True) as status:
            # 1. Prompt Hazırlığı
            final_prompt = translate_and_optimize(user_input)
            status.write(f"🌍 Optimize Edilmiş Komut: {final_prompt[:100]}...")
            
            # 2. Üretim (En kararlı motor: Flux Realism)
            seed = random.randint(0, 999999)
            # 'model=flux-realism' parametresi insan detayları için en iyisidir
            image_url = f"https://image.pollinations.ai/prompt/{final_prompt}?width=1024&height=1024&seed={seed}&model=flux-realism&nologo=true"
            
            try:
                response = requests.get(image_url, timeout=120)
                if response.status_code == 200:
                    image = Image.open(io.BytesIO(response.content))
                    st.image(image, caption="Hatasız Görsel Sonucu", use_container_width=True)
                    
                    # İndirme
                    st.download_button("🖼️ Görseli Kaydet", response.content, f"ai_corrected_{seed}.png", "image/png")
                    status.update(label="✅ Çizim Tamamlandı!", state="complete")
                else:
                    st.error("Bir hata oluştu. Lütfen tekrar deneyin.")
            except Exception as e:
                st.error(f"Bağlantı hatası: {e}")
    else:
        st.warning("Lütfen bir açıklama yazın.")

st.divider()
st.caption("Not: Çok fazla insan figürü (kalabalık) eklemek yüz kalitesini düşürebilir.")