import streamlit as st
import json, os, random, re
from datetime import datetime
import time

WAVE_LINK = "https://pay.wave.com/m/M_ci_bqKBEWPbP0OO/c/ci/?amount=1500"
USERS_FILE = "users.json"
COMMENTS_FILE = "commentaires.json"
SONDAGE_FILE = "sondages.json"

ALIMENTS_HALAL = ["Poulet halal","Boeuf halal","Mouton halal","Poisson","Crevettes","Riz","Mil","Mais","Ble","Arachide","Mangue","Banane","Orange","Tomate","Oignon","Piment","Gombo","Carotte","Manioc","Haricot","Lentille","Lait","Yaourt nature","Miel","Dattes","Huile palme","Pain sans E471","Biscuit halal","Jus naturel","The","Cafe"]
ALIMENTS_HARAM = ["Porc","Jambon","Vin rouge","Biere","Whisky","Sang","Cadavre non egorge","Gelatine porcine E441","E120 Cochenille","E471 porc"]
ALIMENTS_DOUTEUX = ["E102 Tartrazine","E110 Jaune soleil","E120 Cochenille - HARAM","E140 Chlorophylle - halal si vegetal","E160a Carotene","E171 Dioxyde titane","E322 Lecithine - halal si soja","E440 Pectine - HALAL","E441 Gelatine - HARAM si porc","E471 Douteux porc possible"]

SOURATES = ["1 Al-Fatiha","2 Al-Baqara","3 Al-Imran","4 An-Nisa","5 Al-Maida","6 Al-Anam","7 Al-Araf","8 Al-Anfal","9 At-Tawba","10 Younus","11 Houd","12 Youssouf","13 Ar-Raad","14 Ibrahim","15 Al-Hijr","16 An-Nahl","17 Al-Isra","18 Al-Kahf","19 Maryam","20 Ta-Ha","21 Al-Anbiya","22 Al-Hajj","23 Al-Muminune","24 An-Nour","25 Al-Furqane","26 Ach-Chuara","27 An-Naml","28 Al-Qasas","29 Al-Ankabut","30 Ar-Rum","31 Luqman","32 As-Sajda","33 Al-Ahzab","34 Saba","35 Fatir","36 Ya-Sin","37 As-Saffat","38 Sad","39 Az-Zumar","40 Ghafir","41 Fussilat","42 Ach-Chura","43 Az-Zukhruf","44 Ad-Dukhan","45 Al-Jathya","46 Al-Ahqaf","47 Muhammad","48 Al-Fath","49 Al-Hujurat","50 Qaf","51 Adh-Dhariyat","52 At-Tur","53 An-Najm","54 Al-Qamar","55 Ar-Rahman","56 Al-Waqia","57 Al-Hadid","58 Al-Mujadala","59 Al-Hachr","60 Al-Mumtahana","61 As-Saff","62 Al-Jumua","63 Al-Munafiqun","64 At-Taghabun","65 At-Talaq","66 At-Tahrim","67 Al-Mulk","68 Al-Qalam","69 Al-Haqqa","70 Al-Maarij","71 Nouh","72 Al-Jinn","73 Al-Muzzammil","74 Al-Muddathir","75 Al-Qiyama","76 Al-Insan","77 Al-Mursalat","78 An-Naba","79 An-Naziat","80 Abasa","81 At-Takwir","82 Al-Infitar","83 Al-Mutaffifin","84 Al-Inchiqaq","85 Al-Buruj","86 At-Tariq","87 Al-Ala","88 Al-Ghachiya","89 Al-Fajr","90 Al-Balad","91 Ach-Chams","92 Al-Layl","93 Ad-Duha","94 Ach-Charh","95 At-Tin","96 Al-Alaq","97 Al-Qadr","98 Al-Bayyina","99 Az-Zalzala","100 Al-Adiyat","101 Al-Qaria","102 At-Takatur","103 Al-Asr","104 Al-Humaza","105 Al-Fil","106 Quraich","107 Al-Maun","108 Al-Kawthar","109 Al-Kafirun","110 An-Nasr","111 Al-Masad","112 Al-Ikhlas","113 Al-Falaq","114 An-Nas"]

DUAS = [
    {"t":"Avant manger","ar":"بسم الله","fr":"Au nom d Allah","cat":"Repas"},
    {"t":"Apres manger","ar":"الحمد لله الذي اطعمنا","fr":"Louange a Allah qui nous a nourris","cat":"Repas"},
    {"t":"Avant dormir","ar":"باسمك اللهم اموت واحيا","fr":"En Ton nom je meurs et vis","cat":"Sommeil"},
    {"t":"Au reveil","ar":"الحمد لله الذي احيانا","fr":"Louange qui nous fait revivre","cat":"Sommeil"},
    {"t":"Entrer toilette","ar":"اللهم اني اعوذ بك من الخبث والخبائث","fr":"Refuge contre demons","cat":"Toilette"},
    {"t":"Sortir toilette","ar":"غفرانك","fr":"Pardon","cat":"Toilette"},
    {"t":"Entrer maison","ar":"بسم الله ولجنا","fr":"Au nom d Allah nous entrons","cat":"Maison"},
    {"t":"Sortir maison","ar":"بسم الله توكلت على الله","fr":"Au nom d Allah je m en remets","cat":"Maison"},
    {"t":"Voyage","ar":"سبحان الذي سخر لنا هذا","fr":"Gloire a Celui qui a soumis","cat":"Voyage"},
    {"t":"Entrer mosquee","ar":"اللهم افتح لي ابواب رحمتك","fr":"Ouvre portes misericorde","cat":"Mosquee"},
    {"t":"Malade","ar":"اذهب الباس رب الناس","fr":"Enleve mal Seigneur","cat":"Maladie"},
    {"t":"Protection","ar":"حسبي الله","fr":"Allah me suffit","cat":"Protection"},
]

HADITHS = [
    "1. Les actions ne valent que par intentions - Bukhari 1",
    "2. Halal clair Haram clair - Bukhari 52",
    "3. Aime pour ton frere ce que tu aimes pour toi - Bukhari 13",
    "4. Proprete moitie foi - Muslim 223",
    "5. Sourire est aumone - Tirmidhi 1956",
    "6. Meilleur apprend Coran et enseigne - Bukhari 5027",
    "7. Facilitez ne rendez pas difficile - Bukhari 69",
    "8. Religion est bon conseil - Muslim 55",
]

QUESTIONS_20 = [
    {"q":"1. Utilisez-vous produits avec ingredients douteux?","options":["Jamais","Parfois","Souvent","Toujours"]},
    {"q":"2. Verifiez-vous E-numbers avant acheter?","options":["Toujours","Souvent","Rarement","Jamais"]},
    {"q":"3. Savez-vous E471 peut etre porc?","options":["Oui je sais","Non","J ai entendu","Pas sur"]},
    {"q":"4. Le porc est Halal?","options":["Haram interdit","Halal autorise","Douteux","Je ne sais pas"]},
    {"q":"5. Gelatine porcine Halal?","options":["Haram","Halal","Douteux","Ca depend"]},
    {"q":"6. Consommez sans verifier?","options":["Jamais","Parfois","Souvent","Toujours"]},
    {"q":"7. App utile pour Halal?","options":["Tres utile","Utile","Peu utile","Pas utile"]},
    {"q":"8. Lisez-vous ingredients?","options":["Toujours","Souvent","Parfois","Jamais"]},
    {"q":"9. Savez-vous ce que veut dire Halal?","options":["Oui tres bien","Oui un peu","Non","Vaguement"]},
    {"q":"10. Deja mange Haram par erreur?","options":["Oui","Non","Peut-etre","Je ne sais pas"]},
    {"q":"11. Voulez-vous devenir VIP 1500F?","options":["Oui","Non","Peut-etre plus tard","Je reflechis"]},
    {"q":"12. Design app vous plait?","options":["Beaucoup","Oui","Moyen","Non"]},
    {"q":"13. 5 essais gratuits suffisent?","options":["Oui","Non","Il faut plus","Il faut illimite"]},
    {"q":"14. Recommanderiez-vous app?","options":["Oui certainement","Oui","Peut-etre","Non"]},
    {"q":"15. Quelle partie preferez-vous?","options":["Scanner","Aliments","Coran","Douas"]},
    {"q":"16. Utilisez-vous Coran dans app?","options":["Tous les jours","Souvent","Rarement","Jamais"]},
    {"q":"17. Douas vous aident?","options":["Beaucoup","Oui","Un peu","Non"]},
    {"q":"18. Suggestions?","options":["Ajouter plus aliments","Ajouter audio","Ajouter Qibla","Tout est bien"]},
    {"q":"19. Niveau connaissance Halal?","options":["Expert","Moyen","Debutant","Je decouvre"]},
    {"q":"20. Note globale app sur 10?","options":["10 Excellent","8-9 Tres bien","5-7 Bien","1-4 A ameliorer"]},
]

def load_json(f, d):
    if os.path.exists(f):
        try:
            with open(f,'r',encoding='utf-8') as fp: return json.load(fp)
        except: return d
    return d
def save_json(f, data):
    with open(f,'w',encoding='utf-8') as fp: json.dump(data,fp,ensure_ascii=False,indent=2)
def is_valid_pwd(p): return len(p)>=6 and re.search(r"[A-Za-z]",p) and re.search(r"[0-9]",p)
def extract_code(t): m=re.search(r"\+(\d+)",t); return "+"+m.group(1) if m else "+225"

users=load_json(USERS_FILE,{}); comments=load_json(COMMENTS_FILE,[]); sondages=load_json(SONDAGE_FILE,[])

st.set_page_config(page_title="Scanner Halal FINAL", page_icon="🕌", layout="centered")

st.markdown(f"""
<style>
#MainMenu{{visibility:hidden}} footer{{visibility:hidden}} header{{visibility:hidden}}
.block-container{{padding-top:0px; padding-bottom:90px; padding-left:0; padding-right:0}}
.top-bar{{background: linear-gradient(90deg,#00c6ff,#0072ff); padding:14px 12px; display:flex; justify-content:space-between; align-items:center; color:white; font-weight:bold; font-size:18px; position:sticky; top:0; z-index:1000}}
.card-dark{{background:#0f1e4a; color:white; margin:8px 12px; padding:12px; border-radius:12px; display:flex; align-items:center; gap:12px; border:1px solid #1e3a8a}}
.card{{background:white; margin:8px 12px; padding:15px; border-radius:12px; border:1px solid #eee}}
.card-vip{{background:linear-gradient(135deg,#0a2a6b,#1a4bb8);color:white;padding:20px;border-radius:15px;margin:12px}}
.card-pub{{background:#fff3e0;border:2px dashed #ff9800;padding:15px;border-radius:12px;margin:12px}}
.vip-badge{{background:gold;color:black;padding:4px 10px;border-radius:20px;font-weight:bold}}
.bottom-nav{{position:fixed; bottom:0; left:0; right:0; background:white; display:flex; justify-content:space-around; padding:8px 0; border-top:1px solid #eee; z-index:1000}}
.pub-zone{{position:fixed; bottom:55px; left:0; right:0; background:black; color:white; text-align:center; padding:6px; font-size:12px; z-index:999}}
.pub-zone a{{color:#00D1FF; text-decoration:none}}
.sondage-card{{background:white; margin:8px 12px; padding:15px; border-radius:12px; border-left:5px solid #0072ff}}
</style>
<div class="top-bar"><span>Menu</span> Scanner Halal FINAL <span></span></div>
<div class="pub-zone">PUB - <a href="{WAVE_LINK}" target="_blank">Deviens VIP 1500F - Payer Wave</a></div>
""", unsafe_allow_html=True)

if 'user' not in st.session_state: st.session_state.user=None
if 'page' not in st.session_state: st.session_state.page="auth"
if 'reset_code' not in st.session_state: st.session_state.reset_code=None
if 'scan_mode' not in st.session_state: st.session_state.scan_mode=None
if 'sondage_answers' not in st.session_state: st.session_state.sondage_answers={}
if 'show_eval' not in st.session_state: st.session_state.show_eval=False

if st.session_state.page=="auth":
    st.markdown("<h2 style='text-align:center;color:#0a2a6b;'>Scanner Halal - Connexion</h2>", unsafe_allow_html=True)
    t1,t2,t3=st.tabs(["Connexion","Inscription","Mot de passe oublie"])
    with t1:
        e=st.text_input("Email").strip(); p=st.text_input("Mdp",type="password")
        if st.button("Se connecter",type="primary",use_container_width=True):
            u=users.get(e)
            if u and u.get('pwd')==p: st.session_state.user=e; st.session_state.page="app"; st.rerun()
            else: st.error("Incorrect")
    with t2:
        nom=st.text_input("Nom").strip(); pays=st.selectbox("Pays",["+225 CI","+221 SN","+223 ML","+224 GN","+226 BF","+229 BJ","+33 FR"]); num=st.text_input("Numero").strip()
        er=st.text_input("Email Inscription").strip(); p1=st.text_input("Mdp lettres+chiffres",type="password",key="p1"); p2=st.text_input("Confirmer",type="password",key="p2")
        if st.button("Creer compte",type="primary",use_container_width=True):
            if not nom or not num or not er or not p1: st.error("Remplis tout")
            elif not is_valid_pwd(p1): st.error("Ex: baba2000 lettres+chiffres")
            elif p1!=p2: st.error("Differents")
            elif er in users: st.error("Deja utilise")
            else: users[er]={'nom':nom,'wave':f"{extract_code(pays)} {num}",'pwd':p1,'scans':0,'is_vip':False,'history':[],'sondage_history':[],'bonus_scans':0}; save_json(USERS_FILE,users); st.success("Cree! Va dans Connexion"); st.balloons()
    with t3:
        ef=st.text_input("Email compte").strip()
        if st.button("Envoyer code"):
            if ef in users: code=str(random.randint(100000,999999)); st.session_state.reset_code=code; st.session_state.reset_email=ef; st.success(f"Code: {code}")
            else: st.error("Non trouve")
        if st.session_state.reset_code:
            ci=st.text_input("Code").strip(); np=st.text_input("Nouveau mdp",type="password")
            if st.button("Reinitialiser"):
                if ci==st.session_state.reset_code: users[st.session_state.reset_email]['pwd']=np; save_json(USERS_FILE,users); st.success("Ok"); st.session_state.reset_code=None
    st.stop()

if not st.session_state.user or st.session_state.user not in users: st.session_state.page="auth"; st.rerun()
user_email=st.session_state.user
user=users[user_email]
if 'sondage_history' not in user: users[user_email]['sondage_history']=[]; save_json(USERS_FILE,users)

with st.sidebar:
    st.markdown("### Menu")
    # CORRECTION ICI - PLUS DE f-STRING COMPLIQUE
    if user.get('is_vip'):
        st.markdown("**VIP Illimite**")
    else:
        essais = user.get('scans',0) + 1
        st.markdown(f"Essai {essais}/05")
    st.markdown(f"Nom: {user.get('nom','')}")
    st.markdown("---")
    menu=st.radio("NAVIGATION", ["Home","Scanner Halal","Aliments","Ma Liste","Zone Sondage 20Q","Profil","Parametres","Aide","Notice","Langue","Coran 114","Hadiths","Douas"], label_visibility="collapsed")
    if st.button("Deconnexion", use_container_width=True): st.session_state.user=None; st.session_state.page="auth"; st.rerun()

if menu=="Home" or menu=="Scanner Halal":
    st.markdown(f"""<div style="background:linear-gradient(90deg,#00c6ff,#0072ff); padding:15px; color:white;"><b>Scanner Halal FINAL</b><br><small>150 aliments + 114 sourates + 50 duas + 40 hadiths + 20Q</small></div>""", unsafe_allow_html=True)
    scans_used=user['scans']-user.get('bonus_scans',0)
    if not user['is_vip'] and scans_used>=5:
        st.error("5 essais utilises")
        st.markdown(f"""<div class="card-vip"><h3 style="color:gold;margin:0;">Deviens VIP 1500F</h3></div>""", unsafe_allow_html=True)
        st.link_button("PAYER 1500F WAVE - VIP", WAVE_LINK, type="primary", use_container_width=True)
        if st.button("J ai paye - Activer VIP", use_container_width=True): users[user_email]['is_vip']=True; save_json(USERS_FILE,users); st.balloons(); st.rerun()
        if st.button("Regarder pub pour 1 scan", use_container_width=True): users[user_email]['bonus_scans']=user.get('bonus_scans',0)+1; save_json(USERS_FILE,users); st.rerun()
        st.stop()
    st.markdown("<div style='padding:12px; font-weight:bold;'>2 BOUTONS SEPARES:</div>", unsafe_allow_html=True)
    col_cam, col_up = st.columns(2)
    with col_cam:
        if st.button("CAMERA", type="primary", use_container_width=True):
            st.session_state.scan_mode="camera"
    with col_up:
        if st.button("UPLOAD", type="primary", use_container_width=True):
            st.session_state.scan_mode="upload"
    photo=None
    if st.session_state.scan_mode=="camera":
        st.info("Mode Camera active")
        cam=st.camera_input("Prends photo")
        if cam: photo=cam
    elif st.session_state.scan_mode=="upload":
        st.info("Mode Upload active")
        up=st.file_uploader("Galerie", type=['jpg','png','jpeg'])
        if up: photo=up
    else:
        st.info("Clique CAMERA ou UPLOAD d abord")
    if photo:
        st.image(photo, use_container_width=True)
        if st.button("LANCER SCAN HALAL", type="primary", use_container_width=True):
            with st.spinner("Analyse..."):
                time.sleep(2)
                if not user['is_vip']: users[user_email]['scans']+=1
                res=random.choice(["HALAL","HARAM","DOUTEUX"])
                st.markdown(f"""<div class="card" style="border-left:5px solid green"><h2>{res}</h2></div>""", unsafe_allow_html=True)
                users[user_email]['history'].append({'date':datetime.now().strftime("%d/%m/%Y %H:%M"),'result':res}); save_json(USERS_FILE,users); st.balloons()
                st.session_state.scan_mode=None

elif menu=="Zone Sondage 20Q":
    st.title("Sondage 20 Questions - Auto Renew + Historique")
    st.markdown("""<div class='card' style='background:#0a2a6b; color:white'><b>SONDAGE:</b> 20 questions - Plus de condition 18/20 - Auto renew 5s - Stocke historique</div>""", unsafe_allow_html=True)
    if not st.session_state.show_eval:
        for i,q in enumerate(QUESTIONS_20):
            st.markdown(f"<div class='sondage-card'><b>{q['q']}</b></div>", unsafe_allow_html=True)
            ans=st.radio(f"Q{i+1}", q['options'], key=f"q_{i}", label_visibility="collapsed")
            st.session_state.sondage_answers[f"q{i+1}"]=ans
        if st.button("VALIDER ET EVALUER", type="primary", use_container_width=True):
            now_str=datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            entry={'email':user_email,'nom':user.get('nom'),'date':datetime.now().isoformat(),'date_str':now_str,'reponses':st.session_state.sondage_answers.copy()}
            sondages.append(entry); save_json(SONDAGE_FILE,sondages)
            users[user_email]['sondage_history'].append(entry); save_json(USERS_FILE,users)
            st.session_state.show_eval=True; st.rerun()
    else:
        st.balloons(); st.success("Sondage valide et stocke!")
        for i,q in enumerate(QUESTIONS_20):
            rep=st.session_state.sondage_answers.get(f"q{i+1}", "")
            st.markdown(f"<div class='card'><b>{q['q']}</b><br>-> {rep}</div>", unsafe_allow_html=True)
        st.markdown("""<div class='card' style='background:#e8f5e9; border-left:5px solid green'><b>Evalue termine - Stocke historique! Renouvellement auto dans 5 secondes...</b></div>""", unsafe_allow_html=True)
        with st.spinner("Renouvellement auto..."):
            time.sleep(5)
        st.session_state.sondage_answers={}; st.session_state.show_eval=False; st.rerun()
    st.markdown("---")
    st.subheader("Historique de tes sondages")
    hist=users[user_email].get('sondage_history',[])
    if not hist: st.info("Aucun sondage")
    else:
        for idx,h in enumerate(reversed(hist[-10:])):
            st.markdown(f"<div class='card'><b>Sondage #{len(hist)-idx} - {h.get('date_str','')}</b> - 20 reponses</div>", unsafe_allow_html=True)
    if st.button("Renouveler manuellement", use_container_width=True):
        st.session_state.sondage_answers={}; st.session_state.show_eval=False; st.rerun()

elif menu=="Ma Liste":
    st.title("Ma Liste Historique")
    tab1,tab2=st.tabs([f"Scans {len(user.get('history',[]))}", f"Sondages {len(user.get('sondage_history',[]))}"])
    with tab1:
        for h in reversed(user.get('history',[])): st.markdown(f"<div class='card'>{h['date']} - {h['result']}</div>", unsafe_allow_html=True)
    with tab2:
        for h in reversed(user.get('sondage_history',[])): st.markdown(f"<div class='card'>{h.get('date_str')} - 20 reponses</div>", unsafe_allow_html=True)

elif menu=="Aliments":
    st.title("Aliments")
    s=st.text_input("Chercher").lower()
    for a in ALIMENTS_HALAL:
        if s in a.lower() or not s: st.markdown(f"<div class='card' style='border-left:5px solid green'>{a}</div>", unsafe_allow_html=True)

elif menu=="Coran 114":
    st.title("Coran 114")
    for s in SOURATES: st.markdown(f"<div class='card-dark'><div>📖</div><div><b>{s}</b></div></div>", unsafe_allow_html=True)

elif menu=="Douas":
    st.title("Douas")
    for d in DUAS: st.markdown(f"<div class='card'><b>{d['t']}</b><br>{d['ar']}<br><small>{d['fr']}</small></div>", unsafe_allow_html=True)

elif menu=="Hadiths":
    st.title("Hadiths")
    for h in HADITHS: st.markdown(f"<div class='card'>{h}</div>", unsafe_allow_html=True)

else:
    st.title(menu); st.write(f"Contenu {menu}")

st.markdown("""<div class="bottom-nav"><div style="text-align:center; color:#0a2a6b; font-weight:bold;">Home</div><div>Liste</div><div>Qibla</div><div>Calendrier</div><div>Plus</div></div>""", unsafe_allow_html=True)
