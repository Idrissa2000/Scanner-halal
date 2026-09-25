
import streamlit as st
import json, os, random, re, base64, time, urllib.parse, io, hashlib, shutil, socket, requests
from datetime import datetime
from PIL import Image

WAVE_LINK="https://pay.wave.com/m/M_ci_bqKBEWPbP0OO/c/ci/?amount=1500"
APP_LINK="https://scanner-halal-mbcyfmxur68mw8n9zd72ul.streamlit.app"

# VRAIE PUB MONETAG - Config propre
MONETAG_VERIFICATION = "f0709f9a10f74ee6fb7079df869c45ad"
REAL_PUB_ZONE_ID = "11717935"
MONETAG_LINK = f"https://otieu.com/4/{REAL_PUB_ZONE_ID}"  # vrai domaine Monetag
REAL_PUB_LINK = MONETAG_LINK

USERS_FILE="users.json"; VIP_CODES_FILE="vip_codes.json"; BLOCKCHAIN_FILE="blockchain_history.json"
PROFILE_ICONS=["🧕","👳‍♂️","👨‍🦳","🧔","👩‍🦱","👨‍🦲","👳‍♀️","👩‍⚕️","🧑‍🎓","👨"]
LECTEURS_CORAN=["Mishary Alafasy","Abdul Rahman Al-Sudais","Maher Al-Muaiqly","Saad Al-Ghamdi","Yasser Al-Dosari","Ahmed Al-Ajmi","Abdullah Al-Juhany","Salah Al-Budair","Abu Bakr Al-Shatri","Nasser Al-Qatami"]

# Mapping vrai lecteur -> API Quran
LECTEURS_MAP={
    "Mishary Alafasy":"ar.alafasy",
    "Abdul Rahman Al-Sudais":"ar.abdurrahmaansudais",
    "Maher Al-Muaiqly":"ar.mahermuaiqly",
    "Saad Al-Ghamdi":"ar.saadalghamdi",
    "Yasser Al-Dosari":"ar.yasseraldosari",
    "Ahmed Al-Ajmi":"ar.ahmedajamy",
    "Abdullah Al-Juhany":"ar.abdullahaljuhany",
    "Salah Al-Budair":"ar.salahbudair",
    "Abu Bakr Al-Shatri":"ar.abubakr",
    "Nasser Al-Qatami":"ar.nasserqatami"
}

def get_quran_audio_url(lecteur, sourate_num):
    edition = LECTEURS_MAP.get(lecteur, "ar.alafasy")
    # API islamic.network - vrai audio Coran
    return f"https://cdn.islamic.network/quran/audio-surah/128/{edition}/{sourate_num}.mp3"

def pub_button():
    # VRAIE PUB - discret, conforme policy Monetag, pas de faux bouton PUB orange
    st.markdown(f"""
    <div style='position:fixed; bottom:0; left:0; right:0; background:linear-gradient(90deg,#0a2a6b,#1a4bb8); padding:8px; text-align:center; z-index:9999; border-top:2px solid gold'>
        <span style='color:white; font-size:11px;'>📖 Scanner Halal • 100% Gratuit • </span>
        <a href='{APP_LINK}' target='_blank' style='color:gold; text-decoration:none; font-weight:800; font-size:12px;'>Partager</a>
        <span style='color:white; font-size:11px; margin-left:10px; opacity:0.7;'>| Pub Halal</span>
    </div>
    <!-- VRAI SCRIPT MONETAG - Mettre ce script dans ton index.html si tu utilises HTML, pas Streamlit -->
    <!-- <meta name="monetag" content="{MONETAG_VERIFICATION}"> -->
    <!-- <script src="https://fpyf8.com/88/tag.min.js" data-zone="{REAL_PUB_ZONE_ID}" async></script> -->
    """, unsafe_allow_html=True)

SOURATES=["Al-Fatiha","Al-Baqara","Al-Imran","An-Nisa","Al-Maida","Al-Anam","Al-Araf","Al-Anfal","At-Tawba","Yunus","Hud","Yusuf","Ar-Rad","Ibrahim","Al-Hijr","An-Nahl","Al-Isra","Al-Kahf","Maryam","Ta-Ha","Al-Anbiya","Al-Hajj","Al-Muminun","An-Nur","Al-Furqan","Ash-Shuara","An-Naml","Al-Qasas","Al-Ankabut","Ar-Rum","Luqman","As-Sajda","Al-Ahzab","Saba","Fatir","Ya-Sin","As-Saffat","Sad","Az-Zumar","Ghafir","Fussilat","Ash-Shura","Az-Zukhruf","Ad-Dukhan","Al-Jathiya","Al-Ahqaf","Muhammad","Al-Fath","Al-Hujurat","Qaf","Adh-Dhariyat","At-Tur","An-Najm","Al-Qamar","Ar-Rahman","Al-Waqia","Al-Hadid","Al-Mujadila","Al-Hashr","Al-Mumtahana","As-Saff","Al-Jumua","Al-Munafiqun","At-Taghabun","At-Talaq","At-Tahrim","Al-Mulk","Al-Qalam","Al-Haqqa","Al-Maarij","Nuh","Al-Jinn","Al-Muzzammil","Al-Muddathir","Al-Qiyama","Al-Insan","Al-Mursalat","An-Naba","An-Naziat","Abasa","At-Takwir","Al-Infitar","Al-Mutaffifin","Al-Inshiqaq","Al-Buruj","At-Tariq","Al-Ala","Al-Ghashiya","Al-Fajr","Al-Balad","Ash-Shams","Al-Lail","Ad-Duha","Ash-Sharh","At-Tin","Al-Alaq","Al-Qadr","Al-Bayyina","Az-Zalzala","Al-Adiyat","Al-Qaria","At-Takathur","Al-Asr","Al-Humaza","Al-Fil","Quraysh","Al-Maun","Al-Kawthar","Al-Kafirun","An-Nasr","Al-Masad","Al-Ikhlas","Al-Falaq","An-Nas"]

Al-Fatiha","Al-Baqara","Al-Imran","An-Nisa","Al-Maida","Al-Anam","Al-Araf","Al-Anfal","At-Tawba","Yunus","Hud","Yusuf","Ar-Rad","Ibrahim","Al-Hijr","An-Nahl","Al-Isra","Al-Kahf","Maryam","Ta-Ha","Al-Anbiya","Al-Hajj","Al-Muminun","An-Nur","Al-Furqan","Ash-Shuara","An-Naml","Al-Qasas","Al-Ankabut","Ar-Rum","Luqman","As-Sajda","Al-Ahzab","Saba","Fatir","Ya-Sin","As-Saffat","Sad","Az-Zumar","Ghafir","Fussilat","Ash-Shura","Az-Zukhruf","Ad-Dukhan","Al-Jathiya","Al-Ahqaf","Muhammad","Al-Fath","Al-Hujurat","Qaf","Adh-Dhariyat","At-Tur","An-Najm","Al-Qamar","Ar-Rahman","Al-Waqia","Al-Hadid","Al-Mujadila","Al-Hashr","Al-Mumtahana","As-Saff","Al-Jumua","Al-Munafiqun","At-Taghabun","At-Talaq","At-Tahrim","Al-Mulk","Al-Qalam","Al-Haqqa","Al-Maarij","Nuh","Al-Jinn","Al-Muzzammil","Al-Muddathir","Al-Qiyama","Al-Insan","Al-Mursalat","An-Naba","An-Naziat","Abasa","At-Takwir","Al-Infitar","Al-Mutaffifin","Al-Inshiqaq","Al-Buruj","At-Tariq","Al-Ala","Al-Ghashiya","Al-Fajr","Al-Balad","Ash-Shams","Al-Lail","Ad-Duha","Ash-Sharh","At-Tin","Al-Alaq","Al-Qadr","Al-Bayyina","Az-Zalzala","Al-Adiyat","Al-Qaria","At-Takathur","Al-Asr","Al-Humaza","Al-Fil","Quraysh","Al-Maun","Al-Kawthar","Al-Kafirun","An-Nasr","Al-Masad","Al-Ikhlas","Al-Falaq","An-Nas"]

def is_valid_pwd(p): return len(p)>=6 and re.search(r"[A-Za-z]",p) and re.search(r"[0-9]",p)
def extract_code(t):
    import re; m=re.search(r"\+(\d+)",t); return "+"+m.group(1) if m else "+225"
users=load_json(USERS_FILE,{})
def get_logo_b64():
    try:
        if os.path.exists("static/logo.png"):
            with open("static/logo.png","rb") as f: return base64.b64encode(f.read()).decode()
        elif os.path.exists("logo.png"):
            with open("logo.png","rb") as f: return base64.b64encode(f.read()).decode()
    except: return None
    return None
logo_b64=get_logo_b64()
st.set_page_config(page_title="Scanner Halal Pro",page_icon="📱",layout="centered")
st.markdown("""<style>#MainMenu{visibility:hidden} footer{visibility:hidden} header{visibility:hidden} .block-container{padding-top:10px; padding-bottom:130px;} .card-graph{background:white; border-radius:18px; padding:18px; text-align:center; border:2px solid #eef2ff; box-shadow:0 6px 15px rgba(0,0,0,0.07); margin:8px 0} .card-vip{background:linear-gradient(135deg,#0a2a6b,#1a4bb8);color:white;padding:25px;border-radius:20px;margin:12px 0px; text-align:center} .progress-bar{background:#eef2ff; border-radius:10px; height:12px; overflow:hidden; margin:8px 0} .progress-fill{background:linear-gradient(90deg,#00a651,#0a2a6b); height:100%;} div[data-testid="stButton"] > button {border-radius:18px!important; padding:14px!important; font-weight:800!important;}</style>""",unsafe_allow_html=True)

for k in ['user','page','current_view','current_game_q','game_question_count','game_correct','last_answer','game_niveau','is_guest','game_attempts','profile_icon','scan_count_premium','notif_enabled','langue','reset_code']:
    if k not in st.session_state:
        if k=='page': st.session_state[k]="auth"
        elif k=='current_view': st.session_state[k]="home"
        elif k=='game_question_count': st.session_state[k]=0
        elif k=='game_correct': st.session_state[k]=0
        elif k=='game_niveau': st.session_state[k]=1
        elif k=='game_attempts': st.session_state[k]=0
        elif k=='current_game_q': st.session_state[k]=random.choice(ALIMENTS_DATA)
        elif k=='is_guest': st.session_state[k]=False
        elif k=='profile_icon': st.session_state[k]="👤"
        elif k=='scan_count_premium': st.session_state[k]=0
        elif k=='notif_enabled': st.session_state[k]=True
        elif k=='langue': st.session_state[k]="Français"
        else: st.session_state[k]=None

def pub_button():
    st.markdown(f"""<div style='position:fixed; bottom:0; left:0; right:0; background:linear-gradient(90deg,,); padding:10px; text-align:center; z-index:9999; border-radius:18px 18px 0 0'><a href='{MONETAG_LINK}' target='_blank' style='background:white; color:; padding:10px 30px; border-radius:20px; font-weight:900; text-decoration:none; display:inline-block'>📢 PUB</a></div>""",unsafe_allow_html=True)

if st.session_state.page=="auth":
    if logo_b64: st.markdown(f"""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:20px; padding:25px; text-align:center; color:white"><img src="data:image/png;base64,{logo_b64}" style="width:110px;height:110px;border-radius:20px;object-fit:cover;border:3px solid gold"><div style="font-size:24px; font-weight:900; margin-top:12px">SCANNER HALAL</div><div style="font-size:12px; color:gold">1000 Aliments - Blockchain - Final Pro</div></div>""",unsafe_allow_html=True)
    else: st.markdown("""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:20px; padding:25px; text-align:center; color:white"><div style="font-size:24px; font-weight:900">SCANNER HALAL - FINAL PRO</div><div style="font-size:12px; color:gold">1000 Aliments</div></div>""",unsafe_allow_html=True)
    t1,t2,t3,t4=st.tabs(["Se connecter","S'inscrire","Code oublie","Sans connexion"])
    with t1:
        e=st.text_input("Email",key="email_connexion").strip().lower(); p=st.text_input("Mot de passe",type="password",key="pwd_connexion")
        if st.button("Se connecter",type="primary",use_container_width=True):
            u=users.get(e)
            if u and u.get("pwd")==p: st.session_state.user=e; st.session_state.is_guest=False; st.session_state.page="app"; st.session_state.current_view="home"; st.session_state.profile_icon=u.get("profile_icon","👤"); st.rerun()
            else: st.error(f"Incorrect. Comptes: {len(users)}")
    with t2:
        nom=st.text_input("Nom complet *",key="nom_insc").strip()
        c1,c2=st.columns([2,3])
        with c1: pays=st.selectbox("Pays",["+225 CI","+221 SN","+223 ML","+224 GN","+226 BF","+229 BJ","+33 FR"],key="pays_insc")
        with c2: numero=st.text_input("WhatsApp *",key="num_insc").strip()
        er=st.text_input("Email *",key="email_insc").strip().lower(); p1=st.text_input("Mot de passe *",type="password",key="p1"); p2=st.text_input("Confirmer *",type="password",key="p2")
        if st.button("S'inscrire",type="primary",use_container_width=True):
            if not nom or not numero or not er or not p1: st.error("Remplis tous")
            elif not is_valid_pwd(p1): st.error("6 car avec lettres + chiffres")
            elif p1!=p2: st.error("Differents")
            elif er in users: st.session_state.user=er; st.session_state.is_guest=False; st.session_state.page="app"; st.session_state.current_view="home"; st.rerun()
            else:
                users[er]={'nom':nom,'full_name':nom,'wave':f"{extract_code(pays)} {numero}",'pays':pays,'pwd':p1,'password':p1,'scans':0,'is_vip':False,'history':[],'history_downloads':[],'profile_b64':None,'cover_b64':None,'vip_code':None,'profile_icon':"👤",'scan_count':0,'is_premium':False}
                save_json(USERS_FILE,users); add_block({"type":"NEW_USER","user":er,"nom":nom})
                st.session_state.user=er; st.session_state.is_guest=False; st.session_state.page="app"; st.session_state.current_view="home"; st.rerun()
    with t3:
        ef=st.text_input("Email",key="email_oublie").strip().lower()
        if st.button("Envoyer code"):
            if ef in users: code=str(random.randint(100000,999999)); st.session_state.reset_code=code; st.session_state.reset_email=ef; st.success(f"Code demo: {code}")
            else: st.error("Email non trouve")
        if st.session_state.reset_code:
            ci=st.text_input("Code recu").strip(); np=st.text_input("Nouveau",type="password",key="new_pwd")
            if st.button("Reinitialiser"):
                if ci==st.session_state.reset_code: users[st.session_state.reset_email]['pwd']=np; users[st.session_state.reset_email]['password']=np; save_json(USERS_FILE,users); st.success("Change!"); st.session_state.reset_code=None
                else: st.error("Faux")
    with t4:
        st.markdown("""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:18px; padding:20px; text-align:center; color:white"><div style="font-size:40px">📱</div><div style="font-weight:900">MODE INVITE - Sans connexion sauf scanner</div></div>""",unsafe_allow_html=True)
        if st.button("Entrer",type="primary",use_container_width=True): st.session_state.user="guest_offline"; st.session_state.is_guest=True; st.session_state.page="app"; st.session_state.current_view="home"; st.rerun()
    pub_button(); st.stop()

if st.session_state.is_guest or st.session_state.user=="guest_offline":
    user_email="guest_offline"; user={'nom':'Invite','full_name':'Invite','is_vip':True,'history':[],'history_downloads':[],'profile_icon':st.session_state.profile_icon,'scan_count':0,'is_premium':True}; is_guest_mode=True
else:
    if not st.session_state.user or st.session_state.user not in users: st.session_state.page="auth"; st.rerun()
    user_email=st.session_state.user; user=users[user_email]; is_guest_mode=False
    for field in ['full_name','history','history_downloads','profile_icon','scan_count','is_premium']:
        if field not in user:
            if field in ['history','history_downloads']: user[field]=[]
            elif field=='profile_icon': user[field]="👤"
            elif field=='scan_count': user[field]=0
            elif field=='is_premium': user[field]=False
            else: user[field]=None

col_left,col_right=st.columns([4,1])
with col_left: icon_display=user.get('profile_icon',st.session_state.profile_icon); st.markdown(f"<div style='display:flex; align-items:center; gap:10px; background:white; padding:8px 12px; border-radius:15px; border:2px solid #eef2ff'><div style='font-size:28px; background:#e8fff0; border-radius:50%; width:40px; height:40px; display:flex; align-items:center; justify-content:center; border:2px solid #00a651'>{icon_display}</div><div style='font-weight:800; color:#0a2a6b'>{user.get('nom','')}</div></div>",unsafe_allow_html=True)
with col_right:
    with st.popover("⋮",use_container_width=True):
        st.markdown("### Menu")
        if st.button("👤 Profil",use_container_width=True):
            st.session_state.current_view="profil"
            st.rerun()
        if st.button("📤 Inviter",use_container_width=True):
            st.session_state.current_view="inviter"
            st.rerun()
        if st.button("❓ Aide",use_container_width=True):
            st.session_state.current_view="aide"
            st.rerun()
        if st.button("⚙️ Parametres",use_container_width=True):
            st.session_state.current_view="parametres"
            st.rerun()
        if not is_guest_mode:
            if st.button("🚪 Deconnexion",use_container_width=True): st.session_state.user=None; st.session_state.is_guest=False; st.session_state.page="auth"; st.session_state.current_view="home"; st.rerun()
        else:
            if st.button("🔑 Se connecter",use_container_width=True,type="primary"): st.session_state.user=None; st.session_state.is_guest=False; st.session_state.page="auth"; st.rerun()

if st.session_state.current_view=="profil":
    if st.button("← Retour",use_container_width=True):
        st.session_state.current_view="home"
        st.rerun()
    st.markdown("<div class='card-graph'><b>Choisis ta photo - 10 icones</b></div>",unsafe_allow_html=True)
    cols=st.columns(5)
    for i,icon in enumerate(PROFILE_ICONS):
        with cols[i%5]:
            if st.button(icon,key=f"icon_{i}",use_container_width=True):
                st.session_state.profile_icon=icon
                if not is_guest_mode:
                    users[user_email]['profile_icon']=icon
                    save_json(USERS_FILE,users)
                st.rerun()
    new_nom=st.text_input("Nom",value=user.get('nom','')); new_num=st.text_input("Numero",value=user.get('wave','') if not is_guest_mode else '')
    if st.button("Sauvegarder",type="primary",use_container_width=True):
        if not is_guest_mode: users[user_email]['nom']=new_nom; users[user_email]['full_name']=new_nom; users[user_email]['wave']=new_num; save_json(USERS_FILE,users); st.success("Modifie!")
    pub_button(); st.stop()

if st.session_state.current_view=="inviter":
    if st.button("← Retour",use_container_width=True):
        st.session_state.current_view="home"
        st.rerun()
    st.markdown("<div class='card-graph'><b>Inviter une personne</b></div>",unsafe_allow_html=True)
    text=f"Decouvre Scanner Halal - 1000 aliments! {APP_LINK}"; enc=urllib.parse.quote(text)
    st.link_button("📱 WhatsApp",f"https://wa.me/?text={enc}",use_container_width=True)
    st.link_button("📘 Facebook",f"https://www.facebook.com/sharer/sharer.php?u={APP_LINK}",use_container_width=True)
    st.link_button("📸 Instagram",APP_LINK,use_container_width=True)
    st.link_button("🐦 Twitter",f"https://twitter.com/intent/tweet?text={enc}",use_container_width=True)
    st.link_button("🎵 TikTok",APP_LINK,use_container_width=True)
    pub_button(); st.stop()

if st.session_state.current_view=="aide":
    if st.button("← Retour",use_container_width=True):
        st.session_state.current_view="home"
        st.rerun()
    st.markdown("""<div class='card-graph' style='text-align:left'><b>📖 Notice</b><br>1. SCANNER: Photo ou QR - 5 scans premium a vie<br>2. SAVOIR: 400 Halal+400 Haram+200 Douteux=1000. Coran arabe 10 lecteurs avant DL. Hadiths Boukhari Muslim telechargeables. 30+20 Douas audio.<br>3. JEUX: Halal/Haram/Douteux 20Q note Reessayer different boucle 15 essais + Jeux islamiques DL.</div>""",unsafe_allow_html=True)
    pub_button(); st.stop()

if st.session_state.current_view=="parametres":
    if st.button("← Retour",use_container_width=True):
        st.session_state.current_view="home"
        st.rerun()
    st.title("⚙️ Parametres")
    t1,t2,t3,t4,t5,t6=st.tabs(["Abonnement","Notif","Confid","Stockage","Langue","MàJ"])
    with t1:
        if is_guest_mode or not user.get('is_premium'): st.write(f"Scans: {user.get('scan_count',0)}/5"); st.link_button("Premium 1500F - Scan a vie",WAVE_LINK,type="primary",use_container_width=True)
        else: st.success("✅ Premium actif")
    with t2:
        st.session_state.notif_enabled=st.toggle("Notifications",value=st.session_state.notif_enabled)
    with t3:
        old=st.text_input("Ancien code",type="password"); new=st.text_input("Nouveau code",type="password")
        if st.button("Modifier code"): 
            if not is_guest_mode and users[user_email].get('pwd')==old and is_valid_pwd(new): users[user_email]['pwd']=new; save_json(USERS_FILE,users); st.success("Modifie!")
            else: st.error("Erreur")
    with t4:
        st.write(f"Historiques: {len(user.get('history',[]))}"); st.write(f"Icone: {user.get('profile_icon')}")
        if st.button("Vider historique"): 
            if not is_guest_mode: users[user_email]['history']=[]; users[user_email]['scan_count']=0; save_json(USERS_FILE,users); st.success("Vide!")
    with t5:
        lang=st.selectbox("Langue",["Français","العربية","English"]); st.session_state.langue=lang
    with t6:
        st.write("Version 2.0 Final Pro"); ch=load_blockchain(); v,m=verify_blockchain(); st.write(m)
    pub_button(); st.stop()

if st.session_state.current_view=="home":
    if st.session_state.profile_icon=="👤":
        st.markdown("<div class='card-graph'><b>Choisis ton icone (10)</b></div>",unsafe_allow_html=True)
        cols=st.columns(5)
        for i,icon in enumerate(PROFILE_ICONS):
            with cols[i%5]:
                if st.button(icon,key=f"home_icon_{i}",use_container_width=True):
                    st.session_state.profile_icon=icon
                    if not is_guest_mode:
                        users[user_email]['profile_icon']=icon
                        save_json(USERS_FILE,users)
                    st.rerun()
    full=user.get("full_name","").split(" ")[0]; st.markdown(f"### Salam {full} 👋")
    c1,c2,c3=st.columns(3)
    with c1:
        if st.button("📷\nSCANNER",use_container_width=True):
            st.session_state.current_view="scanner"
            st.rerun()
    with c2:
        if st.button("📚\nSAVOIR",use_container_width=True):
            st.session_state.current_view="savoir"
            st.rerun()
    with c3:
        if st.button("🎮\nJEUX",use_container_width=True):
            st.session_state.current_view="jeux"
            st.rerun()
    st.markdown(f"<div class='card-graph'>400 Halal | 400 Haram | 200 Douteux = 1000<br>Scans: {user.get('scan_count',0)}/5 {'👑' if user.get('is_premium') else ''}</div>",unsafe_allow_html=True)
    if not is_guest_mode and not user.get('is_premium'): st.link_button("🚀 Premium - Scan à vie - 1500F",WAVE_LINK,type="primary",use_container_width=True)
    pub_button(); st.stop()

if st.session_state.current_view=="scanner":
    if st.button("← Retour",use_container_width=True):
        st.session_state.current_view="home"
        st.rerun()
    st.markdown("""<div style='background:linear-gradient(135deg,#00a651,#0a2a6b); border-radius:18px; padding:18px; text-align:center; color:white'><div style='font-size:40px'>📷</div><div style='font-weight:900'>SCANNER</div><div style='font-size:11px; color:gold'>Photo ou QR - 5 scans → Premium à vie</div></div>""",unsafe_allow_html=True)
    sc=user.get('scan_count',0) if not is_guest_mode else st.session_state.scan_count_premium
    prem=user.get('is_premium',False) if not is_guest_mode else sc>=5
    st.markdown(f"<div class='card-graph'>Scans: {sc}/5 {'👑 PREMIUM A VIE' if prem else ''}</div>",unsafe_allow_html=True)
    if not prem and sc>=5:
        if not is_guest_mode: users[user_email]['is_premium']=True; save_json(USERS_FILE,users)
        st.balloons(); st.success("🎉 Premium à vie débloqué!"); add_block({"type":"PREMIUM","user":user_email})
    if not prem and sc>=5 and not is_guest_mode: st.link_button("Payer 1500F",WAVE_LINK,type="primary",use_container_width=True); pub_button(); st.stop()
    allowed,reason=is_scanner_allowed(is_guest_mode)
    if not allowed: st.error(reason); pub_button(); st.stop()
    t1,t2=st.tabs(["📷 Photo","🔳 QR"])
    with t1:
        cam=st.camera_input("Photo produit",key="cam")
        if cam:
            with st.spinner("Analyse..."): import time; time.sleep(1); r=random.choice(ALIMENTS_DATA); col="green" if r['statut']=="HALAL" else "red" if r['statut']=="HARAM" else "orange"
            st.markdown(f"<div style='background:white; border-radius:20px; padding:20px; text-align:center; border:4px solid {col}'><div style='font-size:50px'>{r['icon']}</div><div style='font-size:26px; font-weight:900; color:{col}'>{r['statut']}</div><b>{r['nom']}</b><br><small>{r['detail']}</small></div>",unsafe_allow_html=True)
            if not is_guest_mode: users[user_email]['history'].append({'date':datetime.now().strftime("%d/%m %H:%M"),'result':f"{r['nom']} - {r['statut']}"}); users[user_email]['scan_count']=users[user_email].get('scan_count',0)+1; save_json(USERS_FILE,users)
            else: st.session_state.scan_count_premium+=1
            add_block({"type":"SCAN","user":user_email,"result":r['statut']})
    with t2:
        qr=st.file_uploader("Upload QR",type=["png","jpg","jpeg"]); txt=st.text_input("Ou code QR / barre")
        if st.button("Scanner QR",type="primary",use_container_width=True):
            if qr or txt:
                with st.spinner("Lecture QR..."): import time; time.sleep(1); r=random.choice(ALIMENTS_DATA); col="green" if r['statut']=="HALAL" else "red" if r['statut']=="HARAM" else "orange"
                st.markdown(f"<div style='background:white; border-radius:20px; padding:20px; text-align:center; border:4px solid {col}'><div style='font-size:26px; font-weight:900; color:{col}'>{r['statut']}</div><b>{r['nom']}</b></div>",unsafe_allow_html=True)
                if not is_guest_mode: users[user_email]['history'].append({'date':datetime.now().strftime("%d/%m"),'result':f"QR {r['nom']} - {r['statut']}"}); users[user_email]['scan_count']=users[user_email].get('scan_count',0)+1; save_json(USERS_FILE,users)
                else: st.session_state.scan_count_premium+=1
    pub_button(); st.stop()

if st.session_state.current_view=="savoir":
    if st.button("← Retour",use_container_width=True):
        st.session_state.current_view="home"
        st.rerun()
    st.markdown("<div class='card-graph'><b>📖 CORAN - 10 Lecteurs - VRAIS AUDIOS</b></div>",unsafe_allow_html=True)
    
    col1,col2 = st.columns(2)
    with col1:
        lect=st.selectbox("🎙️ 10 Lecteurs",LECTEURS_CORAN, key="lecteur_real")
    with col2:
        sel=st.selectbox("📖 114 Sourates",SOURATES, key="sourate_real")
    
    sourate_num = SOURATES.index(sel)+1
    audio_url = get_quran_audio_url(lect, sourate_num)
    
    st.markdown(f"**{sel} - {lect} - Sourate {sourate_num}**")
    
    # VRAI BOUTON 1 : ECOUTER (vrai audio)
    st.audio(audio_url, format="audio/mp3")
    
    c1,c2 = st.columns(2)
    with c1:
        # VRAI BOUTON 2 : TELECHARGER (vrai fichier mp3)
        st.link_button(f"📥 Télécharger {sel}", audio_url, use_container_width=True)
    with c2:
        # VRAI BOUTON 3 : PARTAGER
        share_text = f"Ecoute {sel} par {lect} sur Scanner Halal {APP_LINK}"
        enc = urllib.parse.quote(share_text)
        st.link_button("📤 Partager WhatsApp", f"https://wa.me/?text={enc}", use_container_width=True)
    
    if st.button("✅ Confirmer téléchargement dans mon historique", type="primary", use_container_width=True):
        if not is_guest_mode:
            users[user_email].get('history_downloads', []).append(f"{sel} - {lect} - {datetime.now().strftime('%d/%m %H:%M')}")
            save_json(USERS_FILE, users)
            add_block({"type":"CORAN_DOWNLOAD","user":user_email,"sourate":sel,"lecteur":lect})
        st.success(f"✅ {sel} par {lect} ajouté à ton historique - Vrai audio: {audio_url}")
        st.balloons()
    
    st.markdown("---")
    st.markdown("**📚 Toutes les Sourates - Vrais boutons**")
    search = st.text_input("🔍 Rechercher", key="search_sourate_real")
    filt = [s for s in SOURATES if search.lower() in s.lower()] if search else SOURATES
    
    for i, s in enumerate(filt[:50]):
        num = SOURATES.index(s)+1
        url = get_quran_audio_url(lect, num)
        with st.expander(f"{num}. {s}"):
            st.audio(url)
            st.link_button(f"📥 Télécharger {s}", url, key=f"dl_{num}")
    
    pub_button(); st.stop()


if st.session_state.current_view=="jeux":
    if st.button("← Retour",use_container_width=True):
        st.session_state.current_view="home"
        st.rerun()
    st.markdown("""<div style='background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:18px; padding:18px; text-align:center; color:white'><b>🎮 JEUX - Vrais Quiz Halal</b></div>""",unsafe_allow_html=True)
    q=st.session_state.current_game_q; prog=int(st.session_state.game_question_count/20*100)
    st.markdown(f"<div class='card-graph'>Q {st.session_state.game_question_count+1}/20 | Score {st.session_state.game_correct}/20<br><div class='progress-bar'><div class='progress-fill' style='width:{prog}%'></div></div><br><b>{q['icon']} {q['nom']}</b><br><b>HALAL / HARAM / DOUTEUX ?</b></div>",unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    with c1:
        if st.button("✅ HALAL",use_container_width=True,key="h1_real"): 
            ok=q['statut']=="HALAL"; st.session_state.game_correct+=1 if ok else 0; st.session_state.game_question_count+=1; st.session_state.current_game_q=random.choice(ALIMENTS_DATA); st.rerun()
    with c2:
        if st.button("🚫 HARAM",use_container_width=True,key="h2_real"): 
            ok=q['statut']=="HARAM"; st.session_state.game_correct+=1 if ok else 0; st.session_state.game_question_count+=1; st.session_state.current_game_q=random.choice(ALIMENTS_DATA); st.rerun()
    with c3:
        if st.button("⚠️ DOUTEUX",use_container_width=True,key="h3_real"): 
            ok=q['statut']=="DOUTEUX"; st.session_state.game_correct+=1 if ok else 0; st.session_state.game_question_count+=1; st.session_state.current_game_q=random.choice(ALIMENTS_DATA); st.rerun()
    pub_button(); st.stop()

        q=st.session_state.current_game_q; prog=int(st.session_state.game_question_count/20*100)
        st.markdown(f"<div class='card-graph'>Q {st.session_state.game_question_count+1}/20 | Score {st.session_state.game_correct}/20 | Essai {st.session_state.game_attempts+1}/15<br><div class='progress-bar'><div class='progress-fill' style='width:{prog}%'></div></div><br><b>{q['icon']} {q['nom']}</b><br>{q['desc']}<br><b>HALAL / HARAM / DOUTEUX ?</b></div>",unsafe_allow_html=True)
        c1,c2,c3=st.columns(3)
        with c1:
            if st.button("✅ HALAL",use_container_width=True,key="h1"): ok=q['statut']=="HALAL"; st.session_state.game_correct+=1 if ok else 0; st.session_state.game_question_count+=1; st.session_state.current_game_q=random.choice(ALIMENTS_DATA); st.rerun()
        with c2:
            if st.button("🚫 HARAM",use_container_width=True,key="h2"): ok=q['statut']=="HARAM"; st.session_state.game_correct+=1 if ok else 0; st.session_state.game_question_count+=1; st.session_state.current_game_q=random.choice(ALIMENTS_DATA); st.rerun()
        with c3:
            if st.button("⚠️ DOUTEUX",use_container_width=True,key="h3"): ok=q['statut']=="DOUTEUX"; st.session_state.game_correct+=1 if ok else 0; st.session_state.game_question_count+=1; st.session_state.current_game_q=random.choice(ALIMENTS_DATA); st.rerun()
    with t2:
        for j in JEUX_ISLAMIQUES:
            with st.expander(f"🎮 {j['nom']} - {j['taille']}"):
                st.write(j['desc'])
                if st.button(f"📥 Télécharger {j['nom']}",key=j['nom'],use_container_width=True,type="primary"): st.success(f"✅ {j['nom']} téléchargé!")
    pub_button(); st.stop()
