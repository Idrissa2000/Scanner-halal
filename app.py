import streamlit as st
import json, os, time, random, hashlib
from datetime import datetime

st.set_page_config(page_title="Scanner Halal Pro", page_icon="🕌", layout="centered")
USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            try: return json.load(f)
            except: return {}
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def hash_pwd(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

users = load_users()
if "user" not in st.session_state: st.session_state.user = None
if "reset_code" not in st.session_state: st.session_state.reset_code = None
if "reset_user" not in st.session_state: st.session_state.reset_user = None

# SIDEBAR MENU
if st.session_state.user:
    u = users.get(st.session_state.user, {})
    is_vip = u.get("is_vip", False)
    st.sidebar.write(f"### 👤 {st.session_state.user} {'👑 VIP' if is_vip else ''}")
    if is_vip: st.sidebar.success("VIP Illimité")
    else: st.sidebar.info(f"Essais: {u.get('scans_used',0)}/10")
    menu = st.sidebar.radio("MENU", ["📷 Scanner","🎮 Zone de Jeu","👤 Mon Profil","⚙️ Paramètres","🥩 Aliments","📋 Ma Liste","💬 Aide","🌐 Langue"])
    if st.sidebar.button("Déconnexion"):
        st.session_state.user=None
        st.rerun()
else:
    menu=None

if not st.session_state.user:
    st.title("🕌 Scanner Halal Pro")
    tab1, tab2, tab3 = st.tabs(["Connexion","Inscription","Mot de passe oublié"])
    with tab1:
        st.subheader("Connexion")
        username = st.text_input("Nom d'utilisateur", key="login_user")
        pwd = st.text_input("Mot de passe", type="password", key="login_pwd")
        if st.button("Se connecter", use_container_width=True):
            if username in users and users[username]["pwd"] == hash_pwd(pwd):
                st.session_state.user = username
                st.rerun()
            else: st.error("Nom ou mot de passe incorrect")
    with tab2:
        st.subheader("Inscription obligatoire")
        new_user = st.text_input("Nom d'utilisateur *")
        wave_num = st.text_input("Numéro Wave *")
        email = st.text_input("Email (pour récupération) *")
        pwd1 = st.text_input("Mot de passe *", type="password")
        pwd2 = st.text_input("Confirmer mot de passe *", type="password")
        if st.button("S'inscrire", use_container_width=True, type="primary"):
            if not new_user or not wave_num or not email or not pwd1: st.error("Remplis tous les champs")
            elif pwd1!= pwd2: st.error("Mots de passe différents")
            elif new_user in users: st.error("Utilisateur existe déjà")
            else:
                users[new_user] = {"wave":wave_num,"email":email,"pwd":hash_pwd(pwd1),"scans_used":0,"is_vip":False,"my_list":[]}
                save_users(users)
                st.success("Compte créé! Va te connecter.")
    with tab3:
        st.subheader("Mot de passe oublié")
        email_recup = st.text_input("Entre ton email")
        if st.button("Envoyer code"):
            found=None
            for k,v in users.items():
                if v.get("email")==email_recup: found=k
            if found:
                code=str(random.randint(100000,999999))
                st.session_state.reset_code=code
                st.session_state.reset_user=found
                st.info(f"CODE DEMO: {code}")
            else: st.error("Email non trouvé")
        if st.session_state.reset_code:
            code_in=st.text_input("Entre le code reçu")
            new_pwd=st.text_input("Nouveau mot de passe", type="password", key="newpwd")
            if st.button("Réinitialiser"):
                if code_in==st.session_state.reset_code:
                    users[st.session_state.reset_user]["pwd"]=hash_pwd(new_pwd)
                    save_users(users)
                    st.success("Mot de passe changé!")
                    st.session_state.reset_code=None
                else: st.error("Code incorrect")
else:
    current = users[st.session_state.user]
    if menu=="📷 Scanner":
        st.title("📷 Scanner Halal Pro")
        used=current.get("scans_used",0)
        is_vip=current.get("is_vip",False)
        if not is_vip: st.progress(used/10, text=f"Essai {used}/10 gratuit")
        if not is_vip and used>=10:
            st.error("⛔ 10 essais utilisés!")
            c1,c2=st.columns(2)
            with c1:
                st.markdown("### 👑 Devenez VIP")
                st.link_button("💳 PAYER 1500F WAVE", "https://pay.wave.com/", use_container_width=True, type="primary")
                code_vip=st.text_input("Code VIP reçu (tape VIP)")
                if code_vip.upper()=="VIP" or code_vip=="1500":
                    users[st.session_state.user]["is_vip"]=True
                    save_users(users)
                    st.success("Tu es VIP 👑")
                    time.sleep(1)
                    st.rerun()
            with c2:
                st.markdown("### 📺 Pub pour 1 scan")
                if st.button("▶️ Regarder pub 30s", use_container_width=True):
                    bar=st.progress(0)
                    for i in range(100):
                        time.sleep(0.03)
                        bar.progress(i+1)
                    users[st.session_state.user]["scans_used"]-=1
                    if users[st.session_state.user]["scans_used"]<0: users[st.session_state.user]["scans_used"]=0
                    save_users(users)
                    st.success("+1 scan!")
                    st.rerun()
        else:
            st.success(f"✅ {'VIP Illimité 👑' if is_vip else f'Reste {10-used} essais'}")
            src=st.radio("Source", ["📷 Caméra","🖼️ Galerie"], horizontal=True)
            img=st.camera_input("Prends étiquette") if src=="📷 Caméra" else st.file_uploader("Upload étiquette", type=["jpg","png","jpeg"])
            if img:
                if not is_vip:
                    users[st.session_state.user]["scans_used"]=used+1
                    users[st.session_state.user]["my_list"].append({"date":str(datetime.now())[:19],"result":"HALAL ✅"})
                    save_users(users)
                st.image(img)
                st.markdown("### Résultat: **HALAL ✅** (Démo)")
    elif menu=="🎮 Zone de Jeu":
        st.title("🎮 Zone de Jeu")
        game=st.selectbox("Jeu", ["Quiz Halal/Haram","Trouve ingrédient Haram","Memory Halal"])
        if game=="Quiz Halal/Haram":
            q=st.radio("Gélatine de porc Halal?", ["Haram","Halal"])
            if st.button("Valider"): st.write("Bravo Haram!" if q=="Haram" else "Faux c'est Haram")
        elif game=="Trouve ingrédient Haram":
            st.write("Eau, Sucre, E120, Arôme")
            rep=st.text_input("Ingrédient Haram?")
            if st.button("Vérifier"): st.success("Oui E120!") if "120" in rep else st.error("Cherche encore")
        else: st.write("Memory Halal - à venir")
    elif menu=="👤 Mon Profil":
        st.title("👤 Mon Profil")
        st.write(f"User: {st.session_state.user}")
        st.write(f"Wave: {current['wave']}")
        photo=st.file_uploader("Ajouter photo profil", type=["jpg","png"])
        if photo: st.image(photo, width=200)
    elif menu=="⚙️ Paramètres":
        st.title("⚙️ Paramètres")
        new_wave=st.text_input("Wave", value=current['wave'])
        new_email=st.text_input("Email", value=current['email'])
        new_pwd=st.text_input("Nouveau mdp", type="password")
        if st.button("Sauvegarder"):
            users[st.session_state.user]["wave"]=new_wave
            users[st.session_state.user]["email"]=new_email
            if new_pwd: users[st.session_state.user]["pwd"]=hash_pwd(new_pwd)
            save_users(users)
            st.success("MAJ OK")
    elif menu=="🥩 Aliments":
        st.title("🥩 Aliments")
        t1,t2=st.tabs(["✅ Halal","❌ Haram"])
        with t1: st.write("- Poulet Halal\n- Boeuf Halal\n- Poisson")
        with t2: st.write("- Porc\n- Alcool\n- E120")
    elif menu=="📋 Ma Liste":
        st.title("📋 Ma Liste")
        for item in current.get("my_list",[]): st.write(f"{item['date']} - {item['result']}")
    elif menu=="💬 Aide":
        st.title("Aide & Commentaires")
        st.text_area("Ton message")
        if st.button("Envoyer"): st.success("Merci!")
    elif menu=="🌐 Langue":
        st.title("Langue")
        st.selectbox("Langue", ["Français","English","العربية"])
