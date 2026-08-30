import streamlit as st
import json, os, random, re
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

def is_valid_pwd(pwd):
    return len(pwd)>=6 and re.search(r"[A-Za-z]", pwd) and re.search(r"[0-9]", pwd)

users = load_json(USERS_FILE, {})
comments = load_json(COMMENTS_FILE, [])

st.set_page_config(page_title="Scanner Halal VIP", page_icon="logo.jpeg", layout="centered")

st.markdown(f"""
<style>
.block-container{{padding-bottom:80px}}
.pub-zone{{position:fixed;bottom:0;left:0;right:0;background:#000;color:white;text-align:center;padding:12px;z-index:9999;font-weight:bold;font-size:13px}}
.pub-zone a{{color:#00D1FF;text-decoration:none}}
.card{{background:white;padding:15px;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,0.1);margin-bottom:10px;border:1px solid #eee}}
.card-vip{{background:linear-gradient(135deg,#0a2a6b,#1a4bb8);color:white;padding:20px;border-radius:15px;margin-bottom:15px}}
.card-pub{{background:#f5f5f5;border:2px dashed #ff9800;padding:15px;border-radius:12px;margin-top:15px}}
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
    st.markdown("<h2 style='text-align:center;color:#0a2a6b;'>Inscription Scanner-Halal</h2>", unsafe_allow_html=True)
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
        nom = st.text_input("Nom utilisateur", key="nom_insc")
        col_p1, col_p2 = st.columns([2,3])
        with col_p1:
            pays = st.selectbox("Choix du pays", ["🇨🇮 +225 (CI)", "🇸🇳 +221 (SN)", "🇲🇱 +223 (ML)", "🇬🇳 +224 (GN)", "🇧🇫 +226 (BF)", "🇧🇯 +229 (BJ)", "🇹🇬 +228 (TG)", "🇳🇪 +227 (NE)", "🇨🇲 +237 (CM)", "🇫🇷 +33 (FR)"], key="pays_code")
            code_pays = "+"+pays.split("+")[1].split(" ")[0]
        with col_p2:
            numero = st.text_input("Numéro", placeholder="07 71 84 57 66", key="num_wave")
        email_r = st.text_input("Email Inscription", key="email_insc")
        pwd1 = st.text_input("Mot de passe (lettres + chiffres)", type="password", key="pwd1")
        pwd2 = st.text_input("Confirmer mot de passe", type="password", key="pwd2")
        if st.button("Créer mon compte", type="primary", use_container_width=True):
            wave_complet = f"{code_pays} {numero}".strip()
            if not nom or not numero or not email_r or not pwd1 or not pwd2:
                st.error("Remplis tous les champs")
            elif not is_valid_pwd(pwd1):
                st.error("Mot de passe doit contenir lettres ET chiffres (ex: Idrissa2000)")
            elif pwd1!=pwd2:
                st.error("Mots de passe différents")
            elif email_r in users:
                st.error("Email déjà utilisé")
            else:
                users[email_r]={'nom':nom,'wave':wave_complet,'pays':pays,'pwd':pwd1,'scans':0,'is_vip':False,'history':[],'bonus_scans':0}
                save_json(USERS_FILE, users)
                st.success("Compte créé! Va dans Connexion")
    with tab3:
        email_f = st.text_input("Email", key="email_forgot")
        if st.button("Envoyer code réinitialisation"):
            if email_f in users:
                code = str(random.randint(100000,999999))
                st.session_state.reset_code=code
                st.session_state.reset_email=email_f
                st.success(f"Code envoyé à {email_f} (Démo): {code}")
            else: st.error("Email non trouvé")
        if st.session_state.reset_code:
            c_in = st.text_input("Code reçu", key="code_in")
            npwd = st.text_input("Nouveau mot de passe (lettres + chiffres)", type="password", key="newpwd")
            if st.button("Réinitialiser"):
                if c_in==st.session_state.reset_code:
                    if not is_valid_pwd(npwd): st.error("Doit avoir lettres + chiffres")
                    else:
                        users[st.session_state.reset_email]['pwd']=npwd
                        save_json(USERS_FILE, users)
                        st.success("Mot de passe changé")
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
    if user['is_vip']: st.markdown('<span class="vip-badge">VIP Illimité</span>', unsafe_allow_html=True)
    else: st.caption(f"Essai {user['scans']+1}/05")
    menu = st.selectbox("MENU", ["📸 Scanner","🎮 Zone de Jeux","👤 Mon Profil","⚙️ Paramètres","🍎 Aliments","📋 Ma Liste","💬 Aide & Commentaires","📖 Notice","🌐 Langue","🎧 Coran - Imam Matroud","📜 Hadiths","🤲 Douas du Jour"])
    if st.button("Déconnexion"):
        st.session_state.user=None
        st.session_state.page="auth"
        st.rerun()

if menu=="📸 Scanner":
    st.title("Scanner Halal")
    scans_used = user['scans'] - user.get('bonus_scans',0)
    if not user['is_vip'] and scans_used>=5:
        st.error("🚫 Tu as utilisé tes 5 essais gratuits")
        st.markdown(f"""
        <div class="card-vip">
            <h3 style="margin:0;color:gold;">👑 Deviens VIP - 1500F</h3>
            <p style="margin:10px 0;">✅ Scans illimités à vie<br>✅ Sans pub<br>✅ Support prioritaire<br><br><b>Paiement sécurisé par Wave</b></p>
        </div>
        """, unsafe_allow_html=True)
        st.link_button("💳 PAYER 1500F AVEC WAVE - VIP", WAVE_LINK, type="primary", use_container_width=True)
        if st.button("✅ J'ai payé - Activer mon VIP", use_container_width=True):
            users[user_email]['is_vip']=True
            save_json(USERS_FILE, users)
            st.balloons()
            st.success("VIP activé!")
            st.rerun()
        st.markdown("---")
        st.markdown("""
        <div class="card-pub">
            <h4 style="margin:0;color:#ff9800;">🎁 Option Gratuite</h4>
            <p style="margin:5px 0;font-size:13px;">Pas d'argent? Regarde une courte pub pour gagner 1 scan gratuit.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("▶️ Regarder une pub (30s) pour 1 scan gratuit", use_container_width=True):
            st.info("Pub regardée! +1 scan offert")
            users[user_email]['bonus_scans']=users[user_email].get('bonus_scans',0)+1
            save_json(USERS_FILE, users)
            st.rerun()
        st.stop()
    st.caption(f"Essai {user['scans']+1}/05" if not user['is_vip'] else "VIP Illimité")
    uploaded = st.file_uploader("Photo ingrédients", type=['jpg','jpeg','png'])
    if uploaded:
        st.image(uploaded, use_container_width=True)
        if st.button("Analyser", type="primary", use_container_width=True):
            if not user['is_vip']: users[user_email]['scans']+=1
            result = random.choice(["HALAL ✅","HARAM ❌","DOUTEUX ⚠️"])
            detail = "Aucun ingrédient haram" if "HALAL" in result else "Gélatine porcine / Alcool suspect"
            st.success(result+" - "+detail)
            users[user_email]['history'].append({'date':datetime.now().strftime("%d/%m %H:%M"),'result':result,'detail':detail})
            save_json(USERS_FILE, users)
else:
    if st.button("⬅️ Retour Scanner"): st.rerun()
    if menu=="🎮 Zone de Jeux": st.title("🎮 Jeux"); st.info("18/20 = 2 scans offerts")
    elif menu=="👤 Mon Profil": st.title("Mon Profil"); st.write(user.get('nom')); st.write(user.get('wave')); st.write(user_email)
    elif menu=="💬 Aide & Commentaires":
        st.title("Aide"); m=st.text_area("Message")
        if st.button("Envoyer"): comments.append({'email':user_email,'msg':m,'date':datetime.now().isoformat()}); save_json(COMMENTS_FILE, comments); st.success("Envoyé")
    else: st.title(menu); st.write("Contenu de "+menu)
