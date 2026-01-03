import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import random
import math

# --- SİSTEM ÇEKİRDEĞİ ---
API_KEY = "AIzaSyB_hvx-hxwJvl8s2E167TQyHWTRroDHxEE"
try:
    genai.configure(api_key=API_KEY)
    AGENT_MIND = "Sen DOST OS Doğa Mentorüsün. Analizlerini bilgece ve profesyonel sun."
except:
    pass

st.set_page_config(page_title="DOST OMEGA", page_icon="🌳", layout="wide", initial_sidebar_state="expanded")

# --- SİSTEM HAFIZASI ---
if "dost_final_v10" not in st.session_state:
    st.session_state.dost_final_v10 = True
    st.session_state.p_color = "#2d6a4f" # Canlı Orman Yeşili
    st.session_state.s_color = "#432818" # Toprak Kahvesi
    st.session_state.u_name = "Şampiyon"
    st.session_state.u_weight = 78.0
    st.session_state.u_height = 180
    st.session_state.u_age = 24
    st.session_state.u_feeling = "Dengeli 🌿"
    st.session_state.user_notes = ""
    st.session_state.ui_blur = 35
    st.session_state.font_size = 1.15
    st.session_state.bg_opacity = 0.5
    st.session_state.chat_history = []
    st.session_state.tasks = {
        "Sabah Topraklanması": True, "Su Hedefi (4L)": False, 
        "Protein Sentezi": True, "Doğa Yürüyüşü": True, 
        "Mobilite Seansı": False, "Dijital Detoks": True
    }
    st.session_state.workout_db = pd.DataFrame({
        "GÜN": ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"],
        "EFOR %": [80, 90, 70, 20, 95, 85, 45],
        "ENERJİ %": [85, 75, 90, 100, 75, 70, 95]
    })
    st.session_state.meal_db = pd.DataFrame({
        "ÖĞÜN": ["Kahvaltı", "Öğle", "Ara Öğün", "Akşam", "Gece"],
        "İÇERİK": ["Yumurta + Avokado", "Tavuk + Kinoa", "Ceviz + Meyve", "Balık + Salata", "Bitki Çayı"],
        "PROTEİN (g)": [35, 55, 5, 45, 10]
    })

# --- HATA ÖNLEYİCİ HESAPLAMALAR ---
def get_bmi():
    return round(st.session_state.u_weight / ((st.session_state.u_height/100)**2), 2)

def hex_to_rgba_safe(h, a):
    h = h.lstrip('#')
    r, g, b = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    return f'rgba({r},{g},{b},{a})'

# --- SUPREME GREEN UI TASARIMI ---
def apply_master_theme():
    pr, sc = st.session_state.p_color, st.session_state.s_color
    st.markdown(f"""
        <style>
        .stApp {{
            background: linear-gradient(rgba(0,0,0,{st.session_state.bg_opacity}), rgba(0,0,0,{st.session_state.bg_opacity + 0.1})), 
                        url("https://images.unsplash.com/photo-1513836279014-a89f7a76ae86?ixlib=rb-1.2.1&auto=format&fit=crop&w=1920&q=80");
            background-size: cover; background-attachment: fixed;
        }}
        @import url('https://fonts.googleapis.com/css2?family=Syncopate:wght@700&family=Outfit:wght@100;400;900&display=swap');
        html, body, [class*="css"] {{ 
            color: #fdf0d5; 
            font-family: 'Outfit', sans-serif; 
            font-size: {st.session_state.font_size}rem;
        }}
        .glass-panel {{
            background: rgba(45, 30, 20, 0.45); border: 1px solid {pr}aa;
            border-radius: 40px; padding: 40px; backdrop-filter: blur({st.session_state.ui_blur}px);
            margin-bottom: 30px; box-shadow: 0 25px 60px rgba(0,0,0,0.7);
        }}
        .hero-h1 {{
            font-family: 'Syncopate'; font-size: 5.5rem; text-align: center;
            background: linear-gradient(180deg, #fdf0d5, {pr}); -webkit-background-clip: text;
            -webkit-text-fill-color: transparent; letter-spacing: 25px; margin: 0; line-height: 1.2;
        }}
        [data-testid="stSidebar"] {{ background: rgba(15, 20, 10, 0.99) !important; border-right: 2px solid {sc}66; }}
        .stMetric {{ background: rgba(67, 40, 24, 0.25); border-radius: 20px; border-bottom: 4px solid {pr}; }}
        .stButton>button {{
            background: linear-gradient(90deg, {pr}, {sc}); color: #fdf0d5; border-radius: 25px;
            height: 5.5rem; font-family: 'Syncopate'; border: none; font-weight: 900;
        }}
        .stTextInput input {{ background: rgba(0,0,0,0.4) !important; color: {pr} !important; border-radius: 15px !important; }}
        </style>
    """, unsafe_allow_html=True)

apply_master_theme()
current_bmi = get_bmi()
current_bmr = 10 * st.session_state.u_weight + 6.25 * st.session_state.u_height - 5 * st.session_state.u_age + 5

# --- SIDEBAR: ÖZELLEŞMİŞ MENÜ & ARAMA ---
with st.sidebar:
    st.markdown(f"<h1 style='text-align:center; font-family:Syncopate; color:#fdf0d5;'>DOST OS</h1>", unsafe_allow_html=True)
    
    # Arama Butonu
    q = st.text_input("🔍 Menüde Ara...", placeholder="Örn: Ayarlar, Strateji...").lower()
    
    nav_map = {
        "🏠 Yaşam Paneli": "ana sayfa dash panel biyometri",
        "🕵️ Strateji Ajanı": "analiz rapor mentor strateji",
        "🤖 Nöral Link": "sohbet chat ai yapay zeka",
        "🥗 Beslenme Planı": "besin yemek öğün nutrisyon",
        "🦾 Performans Lab": "spor efor hareket lab",
        "⚙️ Gelişmiş Ayarlar": "tema renk boyut bulanıklık reset"
    }
    
    filtered_menu = [k for k, v in nav_map.items() if q in k.lower() or q in v]
    menu = st.radio("SİSTEM KATMANLARI", filtered_menu if filtered_menu else ["🏠 Yaşam Paneli"])
    
    st.markdown("---")
    
    # Ruh Hali Slider'ı
    st.session_state.u_feeling = st.select_slider("🌿 Bugün Nasıl Hissediyorsun?", options=["Bitkin", "Sakin", "Dengeli", "Enerjik", "Zinde"])
    
    with st.expander("👤 BİYO-MATRİS", expanded=False):
        st.session_state.u_name = st.text_input("Adın:", st.session_state.u_name)
        st.session_state.u_weight = st.number_input("Kütle (kg):", value=st.session_state.u_weight)
        st.session_state.u_height = st.number_input("Boy (cm):", value=st.session_state.u_height)

    # Not Matrisi
    with st.expander("📝 HAFIZA NOTLARI", expanded=True):
        st.session_state.user_notes = st.text_area("Stratejik Notlar:", value=st.session_state.user_notes, height=200)

# --- SAYFA MANTIKLARI ---
if menu == "🏠 Yaşam Paneli":
    st.markdown('<h1 class="hero-h1">DOST OS</h1>', unsafe_allow_html=True)
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("VKI (BMI)", current_bmi)
    m2.metric("MOD", st.session_state.u_feeling)
    m3.metric("BMR", f"{int(current_bmr)} kcal")
    m4.metric("DURUM", "OPTİMİZE")

    st.markdown("---")
    cl, cm, cr = st.columns([1.3, 2.6, 1.3])
    
    with cl:
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        st.subheader("🎯 Görevler")
        for k, v in st.session_state.tasks.items(): st.session_state.tasks[k] = st.checkbox(k, value=v)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with cm:
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        st.subheader("🧬 Biyo-Dinamik Spektrum")
        r_cats = ['Beslenme', 'Uyku', 'Hidrasyon', 'Efor', 'Enerji']
        r_vals = [90, 80, 85, 75, 95]
        fig = go.Figure(data=go.Scatterpolar(r=r_vals, theta=r_cats, fill='toself', line_color=st.session_state.p_color, fillcolor=hex_to_rgba_safe(st.session_state.p_color, 0.2)))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100], gridcolor="#444")), paper_bgcolor='rgba(0,0,0,0)', font_color="#fdf0d5", height=480)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with cr:
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        st.subheader("🕰️ Biyo-Veri")
        st.write(f"**Su İhtiyacı:** {round(st.session_state.u_weight * 0.045, 1)} L")
        st.success(f"Analiz: {st.session_state.u_name}, sistemlerin hazır.")
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "🕵️ Strateji Ajanı":
    st.header("🕵️ OTONOM STRATEJİ MERKEZİ")
    if st.button("ANALİZİ BAŞLAT"):
        with st.status("Veriler sorgulanıyor..."):
            model = genai.GenerativeModel('gemini-2.5-flash')
            res = model.generate_content(f"{AGENT_MIND}\nBMI: {current_bmi}, Notlar: {st.session_state.user_notes}. Analiz sun.")
            st.markdown(f'<div style="background:rgba(0,0,0,0.8); padding:30px; border-radius:20px;">{res.text}</div>', unsafe_allow_html=True)

elif menu == "🤖 Nöral Link":
    st.header("🧠 NÖRAL LINK SOHBET")
    for m in st.session_state.chat_history:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    if pr := st.chat_input("Dost'a bağlan..."):
        st.session_state.chat_history.append({"role": "user", "content": pr})
        with st.chat_message("user"): st.markdown(pr)
        with st.chat_message("assistant"):
            r = genai.GenerativeModel('gemini-2.5-flash').generate_content(pr)
            st.markdown(r.text)
            st.session_state.chat_history.append({"role": "assistant", "content": r.text})

elif menu == "⚙️ Gelişmiş Ayarlar":
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.header("⚙️ SİSTEM KONFİGÜRASYONU")
    c1, c2 = st.columns(2)
    with c1:
        st.session_state.p_color = st.color_picker("Vurgu Rengi", st.session_state.p_color)
        st.session_state.ui_blur = st.slider("Cam Blur", 0, 100, st.session_state.ui_blur)
    with c2:
        st.session_state.font_size = st.slider("Yazı Ölçeği", 0.8, 1.5, st.session_state.font_size)
        st.session_state.bg_opacity = st.slider("Arka Plan Karanlığı", 0.1, 0.9, st.session_state.bg_opacity)
    if st.button("SİSTEMİ REBOOT ET"): st.session_state.clear(); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.caption(f"DOST OS | ETERNAL ZEN ULTIMA | {datetime.now().year}")
