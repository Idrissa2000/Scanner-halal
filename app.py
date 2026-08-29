import streamlit as st
import random
from datetime import datetime

st.set_page_config(page_title="Scanner Halal VIP", page_icon="🌙", layout="centered")

st.markdown("""
<style>
.vip-badge{background:gold;color:black;padding:5px 12px;border-radius:12px;font-weight:bold}
.pub-zone{background:#0d1b4a;color:white;padding:12px;text-align:center;border-radius:8px;margin-top:20px}
.scan-counter{background:#0d1b4a;color:white;padding:8px;border-radius:10px;text-align:center}
</style>
""", unsafe_allow_html=True)

if 'users' not in st.session_state: st.session_state.users={}
if 'current_user' not in st.session_state: st.session_state.current_user=None
if 'reset_codes' not in st.session_state: st.session_state.reset_codes={}
if 'all_comments' not in st.session_state: st.session_state.all_comments=[]
if 'lang' not in st.session_state: st.session_state.lang="Français"

def get_user(): return st.session_state.users.get(st.session_state.current_user)

try: st.image("logo.png", width=130)
except: st.markdown("<h1 style='color:#0d1b4a'>🌙 Scanner Halal</h1>", unsafe_allow_html=True)

def pub_zone(): st.markdown('<div class="pub-zone">📢 PUB - Deviens VIP 1500F pour retirer pub | Wave: 07 07 07 07 07</div>', unsafe_allow_html=True)

# AUTH
if st.session_state.current_user is None:
    st.title("🔐 Inscription Obligatoire")
    st.session_state.lang = st.selectbox("Langue", ["Français","English","العربية"])
    t1,t2,t3 = st.tabs(["S'inscrire","Se connecter","Mot de passe oublié"])
    with t1:
        username=st.text_input("Nom utilisateur*")
        c1,c2=st.columns([1,2])
        with c1: code_pays=st.selectbox("Code pays", ["+225 🇨🇮","+33 🇫🇷","+212 🇲🇦","+221 🇸🇳","+223 🇲🇱","+226 🇧🇫"])
        with c2: wave=st.text_input("Numéro Wave*")
        email=st.text_input("Email* pour récupération")
        pwd=st.text_input("Mot de passe*",type="password")
        pwd2=st.text_input("Confirmer*",type="password")
        if st.button("Créer compte",type="primary",use_container_width=True):
            if not all([username,wave,pwd,email]): st.error("Remplis *")
            elif pwd!=pwd2: st.error("Mdp différents")
            elif username in st.session_state.users: st.error("Nom pris")
            else:
                st.session_state.users[username]={"username":username,"wave":code_pays+" "+wave,"email":email,"pwd":pwd,"photo":None,"scans_used":0,"scans_bonus":0,"is_vip":False,"my_list":[]}
                st.success("Compte créé! Connecte-toi")
    with t2:
        lu=st.text_input("Nom utilisateur",key="lu")
        lp=st.text_input("Mot de passe",type="password",key="lp")
        if st.button("Se connecter",use_container_width=True):
            u=st.session_state.users.get(lu)
            if u and u['pwd']==lp:
                st.session_state.current_user=lu
                st.rerun()
            else: st.error("Faux identifiants")
    with t3:
        em=st.text_input("Ton email")
        if st.button("Envoyer code"):
            found=None
            for k,v in st.session_state.users.items():
                if v['email']==em: found=k
            if found:
                code=str(random.randint(100000,999999))
                st.session_state.reset_codes[em]=(code,found)
                st.warning(f"CODE DEMO: {code}")
            else: st.error("Email non trouvé")
        c1=st.text_input("Code reçu")
        c2=st.text_input("Nouveau mdp",type="password")
        if st.button("Réinitialiser"):
            if em in st.session_state.reset_codes and st.session_state.reset_codes[em][0]==c1:
                st.session_state.users[st.session_state.reset_codes[em][1]]['pwd']=c2
                st.success("Changé!")
    pub_zone()
    st.stop()

user=get_user()

with st.sidebar:
    if user.get('photo'): st.image(user['photo'],width=100)
    st.write(f"**{user['username']}**")
    if user['is_vip']: st.markdown('<span class="vip-badge">👑 VIP ILLIMITE</span>',unsafe_allow_html=True)
    else:
        total=5+user['scans_bonus']
        st.markdown(f'<div class="scan-counter">Essai {user["scans_used"]}/{total}</div>',unsafe_allow_html=True)
    menu=st.radio("MENU", ["🔍 SCANNER (Page 2)","🎮 Zone de Jeu","👤 Profil","⚙️ Paramètres","🥗 Aliments","📜 Ma Liste","💬 Aide & Commentaires","📖 Notice","🎧 Coran Audio","📚 Hadiths","🤲 Douas du jour","🌐 Langue","Déconnexion"])

if menu=="🔍 SCANNER (Page 2)":
    st.header("Page 2 - Scanner")
    can_scan=user['is_vip'] or (user['scans_used'] < 5+user['scans_bonus'])
    if not can_scan:
        st.error("⛔ 5 essais terminés")
        colA,colB=st.columns(2)
        with colA:
            if st.button("💳 Devenir VIP 1500F",type="primary",use_container_width=True): st.session_state.show_pay=True
        with colB:
            if st.button("▶️ Regarder pub (+1 scan)",use_container_width=True):
                user['scans_bonus']+=1
                st.rerun()
        if st.session_state.get('show_pay'):
            st.info("Wave 1500F au 07 07 XX XX")
            if st.button("J'ai payé - Activer VIP"):
                user['is_vip']=True
                st.balloons()
                st.rerun()
    else:
        prod=st.text_input("Produit / ingrédients")
        if st.button("Scanner",type="primary",use_container_width=True):
            if prod:
                if not user['is_vip']: user['scans_used']+=1
                hl=prod.lower()
                if any(x in hl for x in ["porc","jambon","bacon","saindoux","sang","alcool","vin","bière"]): res="❌ HARAM"
                elif any(x in hl for x in ["gélatine","e471","e472","arôme","e120","e441"]): res="⚠️ DOUTEUX (Mushbooh)"
                else: res="✅ HALAL"
                if "HARAM" in res: st.error(res)
                elif "DOUTEUX" in res: st.warning(res)
                else: st.success(res)
                user['my_list'].append({"date":datetime.now().strftime("%d/%m %H:%M"),"produit":prod,"resultat":res})
                if not user['is_vip']: st.rerun()
    pub_zone()

elif menu=="🎮 Zone de Jeu":
    st.header("Zone de Jeu - 18/20 = +2 scans")
    if st.button("⬅️ Retour au Scanner"): st.rerun()
    j1,j2,j3=st.tabs(["Quiz Halal","Mémoire","Calcul"])
    with j1:
        q=st.radio("Le bœuf non halal est?",["Halal","Haram","Douteux"])
        if st.button("Valider Quiz",key="q1"):
            if q=="Haram":
                st.success("20/20 +2 scans")
                user['scans_bonus']+=2
            else: st.error("10/20")
    with j2:
        st.code("Porc, Sang, Alcool")
        ans=st.text_input("Recopie")
        if st.button("Valider Mémoire",key="q2"):
            if "porc" in ans.lower():
                st.success("18/20 +2 scans")
                user['scans_bonus']+=2
    with j3:
        a,b=random.randint(1,10),random.randint(1,10)
        r=st.number_input(f"{a}+{b} =?",step=1)
        if st.button("Valider Calcul",key="q3"):
            if r==a+b:
                st.success("20/20 +2 scans")
                user['scans_bonus']+=2

elif menu=="👤 Profil":
    st.header("Profil - Page 3")
    if st.button("⬅️ Retour"): st.rerun()
    photo=st.file_uploader("Ajouter photo profil",type=["png","jpg"])
    if photo: user['photo']=photo
    st.write(user)

elif menu=="⚙️ Paramètres":
    st.header("Paramètres")
    if st.button("⬅️ Retour"): st.rerun()
    new_pwd=st.text_input("Nouveau mot de passe",type="password")
    if st.button("Sauvegarder"):
        if new_pwd: user['pwd']=new_pwd
        st.success("Sauvegardé")

elif menu=="🥗 Aliments":
    st.header("Guide Complet")
    if st.button("⬅️ Retour au Scanner"): st.rerun()
    t1,t2,t3=st.tabs(["✅ Halal","❌ Haram","⚠️ Douteux"])
    with t1:
        st.markdown("**Halal:** Fruits/légumes, Lait sans gélatine porc, Oeufs, Viandes bœuf/agneau/mouton/chèvre/volaille/lapin si abattu rituel islamique, Eau, jus non alcoolisés, poissons, miel")
    with t2:
        st.markdown("**Haram:** Porc et dérivés (jambon,bacon,saindoux,gélatine porcine), Sang, Alcool et boissons enivrantes, Animaux carnivores/rapaces, Animaux non abattus rite islamique")
    with t3:
        st.markdown("**Douteux:** Additifs/gélatines/arômes origine non précisée, E471,E472,E120,E441")

elif menu=="📜 Ma Liste":
    st.header("Ma Liste")
    if st.button("⬅️ Retour"): st.rerun()
    for item in user['my_list'][::-1]: st.write(f"{item['date']} - {item['produit']} => {item['resultat']}")

elif menu=="💬 Aide & Commentaires":
    st.header("Aide & Commentaires")
    msg=st.text_area("Ton message")
    if st.button("Envoyer"):
        st.session_state.all_comments.append({"user":user['username'],"msg":msg,"date":datetime.now().strftime("%d/%m %H:%M")})
        st.success("Envoyé!")
    for c in st.session_state.all_comments[::-1]: st.write(f"**{c['user']}** ({c['date']}): {c['msg']}")

elif menu=="📖 Notice":
    st.header("Notice")
    if st.button("⬅️ Retour"): st.rerun()
    st.markdown("1. Inscris-toi Wave+Email 2. 5 essais 3. Scanne 4. Joue 18/20=+2 scans 5. VIP 1500F illimité 6. Pub=+1 scan")

elif menu=="🎧 Coran Audio":
    st.header("🎧 Coran - Imam Matroud")
    st.info("⬇️ Télécharge avant utilisation")
    coran_fatiha = "بسم الله الرحمن الرحيم - Al-Fatiha complète..."
    st.write("**Sourate Al-Fatiha** - بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ")
    st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")
    col1,col2=st.columns(2)
    with col1: st.download_button("📥 Télécharger Texte Arabe", coran_fatiha, file_name="fatiha.txt", type="primary")
    with col2: st.download_button("📥 Télécharger Audio (lien)", "https://example.com/coran.mp3", file_name="audio_coran_lien.txt")
    st.divider()
    st.write("**Sourate Al-Ikhlas** - قُلْ هُوَ اللَّهُ أَحَدٌ")
    st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3")
    st.download_button("📥 Télécharger Ikhlas", "قُلْ هُوَ اللَّهُ أَحَدٌ", file_name="ikhlas.txt")
    if st.button("⬅️ Retour"): st.rerun()

elif menu=="📚 Hadiths":
    st.header("📚 Hadiths")
    st.info("⬇️ Télécharge avant utilisation")
    hadith_fr = "Hadith 1: Les actions ne valent que par les intentions\nHadith 2: Aime pour ton frère ce que tu aimes pour toi"
    hadith_ar = "إنما الأعمال بالنيات"
    st.text_area("FR", hadith_fr, height=100)
    st.text_area("AR", hadith_ar, height=80)
    st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3")
    c1,c2=st.columns(2)
    with c1: st.download_button("📥 Télécharger Hadiths TXT", hadith_fr+"\n"+hadith_ar, file_name="hadiths_complet.txt", type="primary")
    with c2: st.download_button("📥 Télécharger Audio Hadiths", "lien audio", file_name="hadith_audio.txt")
    if st.button("⬅️ Retour"): st.rerun()

elif menu=="🤲 Douas du jour":
    st.header("Douas du jour")
    if st.button("⬅️ Retour"): st.rerun()
    d=st.selectbox("Choisir", ["Au lever","Au coucher","Avant de manger","Après manger"])
    douas={"Au lever":"الحمد لله الذي أحيانا","Au coucher":"باسمك اللهم أموت وأحيا","Avant de manger":"بسم الله","Après manger":"الحمد لله"}
    st.write(douas[d])
    st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3")
    st.download_button("📥 Télécharger Douas", str(douas), file_name="douas.txt")

elif menu=="🌐 Langue":
    st.header("Langue")
    if st.button("⬅️ Retour"): st.rerun()
    l=st.selectbox("Choisir", ["Français","English","العربية"])
    st.session_state.lang=l
    st.success(f"Langue: {l}")

elif menu=="Déconnexion":
    st.session_state.current_user=None
    st.rerun()
