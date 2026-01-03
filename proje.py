import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import random
import math

# --- SİSTEM ÇEKİRDEĞİ ---
# API Key'ini buraya tanımlıyoruz
API_KEY = "AIzaSyB_hvx-hxwJvl8s2E167TQyHWTRroDHxEE"
try:
    genai.configure(api_key=API_KEY)
    SYSTEM_PROMPT = "Sen DOST OS Bilge Mentorüsün. Analizlerini bilimsel ve doğacı bir dille sun."
except:
    pass

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="DOST OMEGA | ETERNAL NATURE", page_icon="🌳", layout="wide", initial_sidebar_state="expanded")

# --- SİSTEM HAFIZASI (SESSION STATE) ---
if "dost_final_v10" not in st.session_state:
    st.session_state.dost_final_v10 = True
    st.session_state.p_color = "#00FF88" # Canlı Neon Yeşil
    st.session_state.s_color = "#432818" # Toprak Kahvesi
    st.session_state.u_name = "Şampiyon"
    st.session_state.u_weight = 78.0
    st.session_state.u_height = 180
    st.session_state.u_age = 24
    st.session_state.u_feeling = "Dengeli 🌿"
    st.session_state.u_water = 3.5
    st.session_state.u_sleep = 8.0
    st.session_state.user_notes = ""
    st.session_state.chat_history = []
    st.session_state.ui_blur = 30
    st.session_state.font_size = 1.15
    st.session_state.bg_opacity = 0.4
    st.session_state.tasks = {
        "Sabah Topraklanması": True, "Su Hedefi (4L)": False, 
        "Protein Sentezi": True, "Sirkadiyen Ayar": True, 
        "Mobilite Seansı": False, "Dijital Detoks": True
    }
    st.session_state.workout_db = pd.DataFrame({
        "GÜN": ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"],
        "EFOR %": [85, 95, 75, 20, 90, 85, 40],
        "ENERJİ %": [80, 70, 85, 100, 75, 65, 95]
    })
    st.session_state.meal_db = pd.DataFrame({
        "ÖĞÜN": ["Kahvaltı", "Öğle", "Ara Öğün", "Akşam", "Gece"],
        "İÇERİK": ["Yumurta + Avokado", "Tavuk + Kinoa", "Meyve + Ceviz", "Balık + Salata", "Lor Peyniri"],
        "PROTEİN": [35, 55, 5, 45, 25]
    })

# --- GLOBAL HESAPLAMALAR (Hata Önleyici) ---
bmi_val = round(st.session_state.u_weight / ((st.session_state.u_height/100)**2), 2)
bmr_val = 10 * st.session_state.u_weight + 6.25 * st.session_state.u_height - 5 * st.session_state.u_age + 5

# --- RENK VE TEMA MOTORU ---
def hex_to_rgba(h, a):
    h = h.lstrip('#')
    rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    return f'rgba({rgb[0]},{rgb[1]},{rgb[2]},{a})'

def apply_theme():
    pr, sc = st.session_state.p_color, st.session_state.s_color
    st.markdown(f"""
        <style>
        .stApp {{
            background: linear-gradient(rgba(0,0,0,{st.session_state.bg_opacity}), rgba(0,0,0,{st.session_state.bg_opacity + 0.1})), 
                        url("https://images.unsplash.com/photo-1542273917363-3b1817f69a2d?auto=format&fit=crop&w=1920&q=80");
            background-size: cover; background-attachment: fixed;
        }}
        @import url('https://fonts.googleapis.com/css2?family=Syncopate:wght@700&family=Outfit:wght@100;400;900&display=swap');
        html, body, [class*="css"] {{ color: #fdf0d5; font-family: 'Outfit', sans-serif; font-size: {st.session_state.font_size}rem; }}
        .glass-panel {{
            background: rgba(45, 30, 20, 0.45); border: 1px solid {pr}88;
            border-radius: 40px; padding: 40px; backdrop-filter: blur({st.session_state.ui_blur}px);
            margin-bottom: 25px; box-shadow: 0 20px 60px rgba(0,0,0,0.6);
        }}
        .hero-title {{
            font-family: 'Syncopate'; font-size: 5.5rem; text-align: center;
            background: linear-gradient(180deg, #fdf0d5, {pr}); -webkit-background-clip: text;
            -webkit-text-fill-color: transparent; letter-spacing: 20px; margin-bottom: 30px; line-height: 1.1;
        }}
        [data-testid="stSidebar"] {{ background: rgba(10, 15, 10, 0.99) !important; border-right: 2px solid {sc}66; }}
        .stMetric {{ background: rgba(67, 40, 24, 0.25); border-radius: 20px; border-bottom: 4px solid {pr}; }}
        .stButton>button {{
            background: linear-gradient(90deg, {pr}, {sc}); color: #fdf0d5; border-radius: 25px;
            height: 5.5rem; font-family: 'Syncopate'; border: none; font-weight: 900;
        }}
        .terminal-box {{
            background: rgba(0,0,0,0.85); border-left: 10px solid {sc}; border-radius: 25px;
            padding: 40px; color: #fdf0d5; font-family: 'Courier New', monospace; font-size: 1.1rem;
        }}
        .stTextInput input {{ background: rgba(0,0,0,0.4) !important; color: {pr} !important; border-radius: 15px !important; }}
        </style>
    """, unsafe_allow_html=True)

apply_theme()

# --- SIDEBAR & NAVİGASYON ---
with st.sidebar:
    st.markdown(f"<h1 style='text-align:center; font-family:Syncopate; color:#fdf0d5;'>DOST OS</h1>", unsafe_allow_html=True)
    
    # Menü Arama
    q = st.text_input("🔍 Menüde Ara...", placeholder="Örn: Ayarlar, Strateji...").lower()
    nav_map = {
        "🏠 Ana Kontrol": "dash panel biyometri durum",
        "🕵️ Strateji Ajanı": "analiz mentor rapor strateji otonom",
        "🤖 Nöral Link": "sohbet chat ai yapay zeka",
        "🥗 Beslenme Planı": "nutrisyon yemek öğün diyet",
        "🦾 Performans Lab": "spor efor hareket antrenman",
        "⚙️ Gelişmiş Ayarlar": "tema renk boyut bulanıklık"
    }
    filtered = [k for k, v in nav_map.items() if q in k.lower() or q in v]
    menu = st.radio("NAVİGASYON", filtered if filtered else ["🏠 Ana Kontrol"])
    
    st.markdown("---")
    st.session_state.u_feeling = st.select_slider("🌿 Bugün Nasıl Hissediyorsun?", options=["Yorgun", "Sakin", "Dengeli", "Enerjik", "Zinde"])
    
    with st.expander("👤 KİMLİK MATRİSİ", expanded=False):
        st.session_state.u_name = st.text_input("Adın:", st.session_state.u_name)
        st.session_state.u_weight = st.number_input("Kütle (kg):", value=st.session_state.u_weight)
        st.session_state.u_height = st.number_input("Boy (cm):", value=st.session_state.u_height)

    with st.expander("📝 HAFIZA NOTLARI", expanded=True):
        st.session_state.user_notes = st.text_area("Hafıza:", value=st.session_state.user_notes, height=180)

# --- MODÜL 1: ANA KONTROL ---
if menu == "🏠 Ana Kontrol":
    st.markdown('<h1 class="hero-title">DOST OS</h1>', unsafe_allow_html=True)
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("VKI (BMI)", bmi_val)
    m2.metric("MOD", st.session_state.u_feeling)
    m3.metric("BMR", f"{int(bmr_val)} kcal")
    m4.metric("DURUM", "OPTİMİZE")

    st.markdown("---")
    c1, c2, c3 = st.columns([1.5, 2.5, 1.5])
    
    with c1:
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        st.subheader("🎯 Görevler")
        for k, v in st.session_state.tasks.items():
            st.session_state.tasks[k] = st.checkbox(k, value=v)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        st.subheader("🧬 Biyo-Dinamik Analiz")
        cats = ['Beslenme', 'Uyku', 'Hidrasyon', 'Efor', 'Enerji', 'Mod']
        vals = [90, (st.session_state.u_sleep/9)*100, (st.session_state.u_water/4)*100, 80, 85, 95]
        fig = go.Figure(data=go.Scatterpolar(r=vals, theta=cats, fill='toself', line_color=st.session_state.p_color, fillcolor=hex_to_rgba(st.session_state.p_color, 0.2)))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100], gridcolor="#444")), paper_bgcolor='rgba(0,0,0,0)', font_color="#fdf0d5", height=450)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c3:
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        st.subheader("🕰️ Biyo-İstatistik")
        st.write(f"**Su İhtiyacı:** {round(st.session_state.u_weight * 0.045, 1)} L")
        st.write(f"**Vücut Alanı:** {round(math.sqrt((st.session_state.u_height * st.session_state.u_weight) / 3600), 2)} m²")
        st.progress(85, text="Sistem Verimliliği")
        st.success(f"{st.session_state.u_name}, sistemlerin hazır.")
        st.markdown('</div>', unsafe_allow_html=True)

# --- MODÜL 2: STRATEJİ AJANI ---
elif menu == "🕵️ Strateji Ajanı":
    st.header("🕵️ OTONOM STRATEJİ MERKEZİ")
    if st.button("ANALİZİ BAŞLAT"):
        with st.status("Veriler işleniyor..."):
            try:
                model = genai.GenerativeModel('gemini-2.5-flash')
                res = model.generate_content(f"{SYSTEM_PROMPT}\nBMI:{bmi_val}, Notlar:{st.session_state.user_notes}. Analiz yap.")
                st.markdown(f'<div class="terminal-box">{res.text}</div>', unsafe_allow_html=True)
            except:
                st.error("API Bağlantısı başarısız. Lütfen Key'i kontrol et.")

# --- MODÜL 3: NÖRAL LINK (SOHBET) ---
elif menu == "🤖 Nöral Link":
    st.header("🧠 NÖRAL LINK SOHBET")
    for m in st.session_state.chat_history:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    
    if prompt := st.chat_input("Mentorunla konuş..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            try:
                response = genai.GenerativeModel('gemini-2.5-flash').generate_content(prompt)
                st.markdown(response.text)
                st.session_state.chat_history.append({"role": "assistant", "content": response.text})
            except:
                st.error("Bağlantı koptu.")

# --- MODÜL 4: BESLENME ---
elif menu == "🥗 Beslenme Planı":
    st.header("🥗 NUTRISYON MATRİSİ")
    st.dataframe(st.session_state.meal_db, use_container_width=True)
    st.plotly_chart(px.pie(st.session_state.meal_db, values="PROTEİN", names="ÖĞÜN", hole=0.5, color_discrete_sequence=[st.session_state.p_color, st.session_state.s_color]))

# --- MODÜL 5: PERFORMANS ---
elif menu == "🦾 Performans Lab":
    st.header("🦾 PERFORMANS VERİ ANALİZİ")
    st.session_state.workout_db = st.data_editor(st.session_state.workout_db, use_container_width=True)
    fig_line = px.line(st.session_state.workout_db, x="GÜN", y=["EFOR %", "ENERJİ %"], markers=True)
    fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#fdf0d5")
    st.plotly_chart(fig_line, use_container_width=True)

# --- MODÜL 6: AYARLAR ---
elif menu == "⚙️ Gelişmiş Ayarlar":
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.header("⚙️ SİSTEM KONFİGÜRASYONU")
    c1, c2 = st.columns(2)
    with c1:
        st.session_state.p_color = st.color_picker("Vurgu Rengi", st.session_state.p_color)
        st.session_state.ui_blur = st.slider("Cam Efekti (Blur)", 0, 100, st.session_state.ui_blur)
    with c2:
        st.session_state.font_size = st.slider("Yazı Ölçeği", 0.8, 1.5, st.session_state.font_size)
        st.session_state.bg_opacity = st.slider("Arka Plan Karanlığı", 0.1, 0.9, st.session_state.bg_opacity)
    if st.button("SİSTEMİ SIFIRLA"):
        st.session_state.clear()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.caption(f"DOST OS | ETERNAL NATURE | {datetime.now().year}")
