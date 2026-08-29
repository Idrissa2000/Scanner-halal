import streamlit as st
import json, os, random
from datetime import datetime

WAVE_LINK = "https://pay.wave.com/m/M_ci_bqKBEWPbP0OO/c/ci/?amount=1500"
USERS_FILE = "users.json"
COMMENTS_FILE = "commentaires.json"

def load_json(f, default):
    if os.path.exists(f):
        try:
            with open(f,'r',encoding='utf-8') as fp: return json.load(fp)
        except: return default
    return default

def save_json(f, data):
    with open(f,'w',encoding='utf-8') as fp:
        json.dump(data,fp,ensure_ascii=False,indent=2)

users = load_json(USERS_FILE, {})
comments = load_json(COMMENTS_FILE, [])

# LOGO = logo.jpeg
st.set_page_config(page_title="Scanner Halal VIP", page_icon="logo.jpeg", layout="centered")

st.markdown(f"""
<style>
.block-container{{padding-bottom:80px}}
.pub-zone{{position:fixed;bottom:0;left:0;right:0;background:#000;color:white;text-align:center;padding:12px;z-index:9999;font-weight:bold;font-size:13px}}
.pub-zone a{{color:#00D1FF;text-decoration:none}}
.card{{background:white;padding:15px;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,0.1);margin-bottom:10px}}
.vip-badge{{background:gold;color:black;padding:4px 10px;border-radius:20px;font-weight:bold}}
</style>
<div class="pub-zone">📢 PUB - <a href="{WAVE_LINK}" target="_blank">Deviens VIP 1500F - Payer Wave</a></div>
""", unsafe_allow_html=True)

if 'user' not in st.session_state: st.session_state.user=None
if 'page' not in st.session_state: st.session_state.page="auth"
if 'reset_code' not in st.session_state: st.session_state.reset_code=None

if st.session_state.page=="auth":
    c = st.columns([1,2,1])[1]
    with c:
        try: st.image("logo.jpeg", use_container_width=True)
        except: st.title("🕌 Scanner Halal")
    st.markdown("<h2 style='text-align:center;color:#0a2a6b;'>Inscription Obligatoire</h2>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["Connexion","Inscription","Mot de passe oublie"])
    with tab1:
        email = st.text_input("Email", key="login_email")
        pwd = st.text_input("Mot de passe", type="password", key="login_pwd")
        if st.button("Se connecter", type="primary", use_container_width=True):
            u = users.get(email)
            if u and u.get('pwd')==pwd:
                st.session_state.user=email
                st.session_state.page="scanner"
                st.rerun()
            else: st.error("Email ou mot de passe incorrect")
    with tab2:
        nom = st.text_input("Nom utilisateur")
        wave = st.text_input("Numero Wave avec code pays", placeholder="+225 07 XX XX XX XX")
        email_r = st.text_input("Email Inscription")
        pwd1 = st.text_input("Mot de passe", type="password", key="pwd1")
        pwd2 = st.text_input("Confirmer mot de passe", type="password", key="pwd2")
        if st.button("Creer mon compte", type="primary", use_container_width=True):
            if not nom or not wave or not email_r or not pwd1:
                st.error("Remplis tous les champs")
            elif pwd1!=pwd2:
                st.error("Mots de passe differents")
            elif email_r in users:
                st.error("Email deja utilise")
            else:
                users[email_r]={'nom':nom,'wave':wave,'pwd':pwd1,'scans':0,'is_vip':False,'history':[],'bonus_scans':0}
                save_json(USERS_FILE, users)
                st.success("Compte cree! Va dans Connexion")
    with tab3:
        email_f = st.text_input("Ton email pour code")
        if st.button("Envoyer code reinitialisation"):
            if email_f in users:
                code = str(random.randint(100000,999999))
                st.session_state.reset_code=code
                st.session_state.reset_email=email_f
                st.success(f"Code envoye a {email_f} (Demo): {code}")
            else: st.error("Email non trouve")
        if st.session_state.reset_code:
            c_in = st.text_input("Code recu")
            npwd = st.text_input("Nouveau mot de passe", type="password", key="newpwd")
            if st.button("Reinitialiser"):
                if c_in==st.session_state.reset_code:
                    users[st.session_state.reset_email]['pwd']=npwd
                    save_json(USERS_FILE, users)
                    st.success("Mot de passe change")
                    st.session_state.reset_code=None
                else: st.error("Code incorrect")
    st.stop()

if not st.session_state.user or st.session_state.user not in users:
    st.session_state.page="auth"
    st.rerun()

user_email = st.session_state.user
user = users[user_email]

with st.sidebar:
    try: st.image("logo.jpeg", width=90)
    except: pass
    st.write(f"**{user.get('nom','')}**")
    if user['is_vip']: st.markdown('<span class="vip-badge">VIP Illimite</span>', unsafe_allow_html=True)
    else: st.caption(f"Essai {user['scans']+1}/05")
    menu = st.selectbox("MENU", ["📸 Scanner","🎮 Zone de Jeux","👤 Mon Profil","⚙️ Parametres","🍎 Aliments","📋 Ma Liste","💬 Aide & Commentaires","📖 Notice","🌐 Langue","🎧 Coran - Imam Matroud","📜 Hadiths","🤲 Douas du Jour"])
    if st.button("Deconnexion"):
        st.session_state.user=None
        st.session_state.page="auth"
        st.rerun()

if menu=="📸 Scanner":
    st.title("Scanner Halal")
    st.caption(f"Essai {user['scans']+1}/05" if not user['is_vip'] else "VIP Illimite")
    scans_used = user['scans'] - user.get('bonus_scans',0)
    if not user['is_vip'] and scans_used>=5:
        st.error("Tu as utilise tes 5 essais gratuits")
        col1,col2 = st.columns(2)
        with col1:
            st.link_button("💳 Deviens VIP 1500F", WAVE_LINK, type="primary", use_container_width=True)
            if st.button("✅ J'ai paye - Activer VIP", use_container_width=True):
                users[user_email]['is_vip']=True
                save_json(USERS_FILE, users)
                st.balloons()
                st.success("VIP active")
                st.rerun()
        with col2:
            if st.button("▶️ Regarder pub pour 1 scan", use_container_width=True):
                st.info("Pub regardee! +1 scan")
                users[user_email]['bonus_scans']=users[user_email].get('bonus_scans',0)+1
                save_json(USERS_FILE, users)
                st.rerun()
        st.stop()
    uploaded = st.file_uploader("Photo ingredients", type=['jpg','jpeg','png'])
    if uploaded:
        st.image(uploaded, use_container_width=True)
        if st.button("Analyser", type="primary", use_container_width=True):
            if not user['is_vip']:
                users[user_email]['scans']+=1
            result = random.choice(["HALAL ✅","HARAM ❌","DOUTEUX ⚠️"])
            detail = "Aucun haram" if "HALAL" in result else "Gelatine porcine / Alcool suspect"
            st.success(result+" - "+detail)
            users[user_email]['history'].append({'date':datetime.now().strftime("%d/%m %H:%M"),'result':result,'detail':detail})
            save_json(USERS_FILE, users)
else:
    if st.button("⬅️ Retour Scanner"):
        st.rerun()
    if menu=="🎮 Zone de Jeux":
        st.title("🎮 Zone de Jeux")
        st.info("18/20 = 2 scans offerts")
        q1 = st.radio("Le porc est Halal?", ["Non","Oui"], key="q1")
        q2 = st.radio("Gelatine porcine?", ["Haram","Halal"], key="q2")
        if st.button("Valider Quiz"):
            score = (10 if q1=="Non" else 0)+(10 if q2=="Haram" else 0)
            st.write(f"Score {score}/20")
            if score>=18:
                users[user_email]['bonus_scans']=users[user_email].get('bonus_scans',0)+2
                save_json(USERS_FILE, users)
                st.success("+2 scans offerts!")
    elif menu=="👤 Mon Profil":
        st.title("Mon Profil")
        st.write(user.get('nom')); st.write(user.get('wave')); st.write(user_email)
        ph = st.file_uploader("Photo de profil", type=['jpg','png'])
        if ph: st.image(ph,width=120)
    elif menu=="⚙️ Parametres":
        st.title("Parametres")
        nn = st.text_input("Nom", value=user.get('nom',''))
        nw = st.text_input("Wave", value=user.get('wave',''))
        np = st.text_input("Nouveau mdp", type="password")
        if st.button("Sauvegarder"):
            users[user_email]['nom']=nn; users[user_email]['wave']=nw
            if np: users[user_email]['pwd']=np
            save_json(USERS_FILE, users); st.success("Sauve")
    elif menu=="🍎 Aliments":
        st.title("Aliments")
        t1,t2,t3 = st.tabs(["Halal","Haram","Douteux"])
        with t1: st.write("Fruits, legumes, lait, oeufs, viandes boeuf/agneau/poulet abattues halal, eau, jus")
        with t2: st.write("Porc, jambon, bacon, saindoux, gelatine porcine, sang, alcool, vin, biere, rapaces, bete morte non egorgee")
        with t3: st.write("Additifs origine non precisee, gélatines aromes douteux, E471 etc")
    elif menu=="📋 Ma Liste":
        st.title("Ma Liste - Historique")
        for h in reversed(user.get('history',[])):
            st.markdown(f"<div class='card'>{h['date']} - {h['result']} - {h['detail']}</div>", unsafe_allow_html=True)
    elif menu=="💬 Aide & Commentaires":
        st.title("Aide")
        m = st.text_area("Ton message")
        if st.button("Envoyer"):
            comments.append({'email':user_email,'nom':user.get('nom'),'msg':m,'date':datetime.now().isoformat()})
            save_json(COMMENTS_FILE, comments); st.success("Envoye - Je te repondrai")
    elif menu=="📖 Notice":
        st.title("Notice")
        st.write("1. Inscris-toi 2. Scanne 5 fois gratuit 3. VIP ou pub 4. Menu pour tout")
    elif menu=="🌐 Langue":
        st.title("Langue")
        st.selectbox("Langue", ["Francais","English","العربية"])
    elif menu=="🎧 Coran - Imam Matroud":
        st.title("Coran Imam Matroud")
        if st.button("📥 Telecharger Coran"): st.success("Telecharge (simulation)")
        st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")
        st.write("الفاتحة")
    elif menu=="📜 Hadiths":
        st.title("Hadiths")
        if st.button("📥 Telecharger Hadiths"): st.success("Telecharge")
        st.markdown("<div class='card'>Les actions ne valent que par les intentions - Bukhari</div>", unsafe_allow_html=True)
    elif menu=="🤲 Douas du Jour":
        st.title("Douas du Jour")
        st.markdown("Au lever: الحمد لله الذي أحيانا | Avant manger: بسم الله | Au coucher: باسمك اللهم أموت وأحيا")
