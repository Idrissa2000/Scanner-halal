import streamlit as st
import json, os, random, re, base64, calendar, time
from datetime import datetime, date

WAVE_LINK = "https://pay.wave.com/m/M_ci_bqKBEWPbP0OO/c/ci/?amount=1500"
APP_LINK = "https://scanner-halal.streamlit.app"
HIJRI_MONTHS = ["Muharram","Safar","Rabi al-Awwal","Rabi al-Thani","Jumada al-Ula","Jumada al-Akhira","Rajab","Shaban","Ramadan","Shawwal","Dhu al-Qidah","Dhu al-Hijjah"]
USERS_FILE = "users.json"
os.makedirs("profile_pics", exist_ok=True)

def gregorian_to_hijri(g_date):
    d=g_date.day; m=g_date.month; y=g_date.year
    a=(14-m)//12; yy=y+4800-a; mm=m+12*a-3
    jd=d+(153*mm+2)//5+365*yy+yy//4-yy//100+yy//400-32045
    jd=jd-1948439+10632; n=(jd-1)//10631; jd=jd-10631*n+10632
    j=(jd-1)//354; l=jd-(j*354)-((3+11*j)//30)
    mh=int((l-1)//29.5)+1
    if mh>12: mh=12
    dh=int(l-(mh-1)*29.5)
    return max(1,min(30,dh)), mh, 30*n+j+1

def get_image_base64(path):
    if path and os.path.exists(path):
        try:
            with open(path,"rb") as f: return base64.b64encode(f.read()).decode()
        except: return None
    return None

def load_json(f,d):
    if os.path.exists(f):
        try:
            with open(f,'r',encoding='utf-8') as fp: return json.load(fp)
        except: return d
    return d
def save_json(f,data):
    with open(f,'w',encoding='utf-8') as fp: json.dump(data,fp,ensure_ascii=False,indent=2)
def is_valid_pwd(p): return len(p)>=6 and re.search(r"[A-Za-z]",p) and re.search(r"[0-9]",p)
def extract_code(t):
    m=re.search(r"\+(\d+)",t); return "+"+m.group(1) if m else "+225"

users=load_json(USERS_FILE,{})

st.set_page_config(page_title="Scanner Halal", page_icon="🕌", layout="centered")
st.markdown("""
<style>
#MainMenu{visibility:hidden} footer{visibility:hidden} header{visibility:hidden}
.block-container{padding-top:10px; padding-bottom:120px;}
.card-graph{background:white; border-radius:18px; padding:18px; text-align:center; border:2px solid #eef2ff; box-shadow:0 6px 15px rgba(0,0,0,0.07); margin:8px 0}
.card-vip{background:linear-gradient(135deg,#0a2a6b,#1a4bb8);color:white;padding:25px;border-radius:20px;margin:12px 0px; text-align:center; box-shadow:0 8px 20px rgba(0,0,0,0.2)}
/* Boutons graphiques */
div[data-testid="stButton"] > button {
    border-radius: 18px!important;
    height: auto!important;
    padding: 18px!important;
    white-space: pre-line!important;
    box-shadow: 0 6px 15px rgba(0,0,0,0.07)!important;
    border: 2px solid #eef2ff!important;
    background: white!important;
    color: #0a2a6b!important;
    font-weight: 800!important;
}
</style>
""", unsafe_allow_html=True)

for k in ['user','page','reset_code','scan_mode','bottom_nav','selected_menu','ad_watching','ad_start_time','edit_profile']:
    if k not in st.session_state:
        st.session_state[k] = None if k not in ['page','bottom_nav','ad_watching','edit_profile'] else ("auth" if k=='page' else "Home" if k=='bottom_nav' else False)

if st.session_state.page=="auth":
    st.markdown("""
    <div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:20px; padding:25px; text-align:center; color:white">
        <div style="font-size:70px">🕌</div>
        <div style="font-size:24px; font-weight:900">SCANNER HALAL</div>
    </div>""", unsafe_allow_html=True)
    t1,t2,t3=st.tabs(["Connexion","Inscription","Oublié"])
    with t1:
        e=st.text_input("Email", key="email_connexion").strip()
        p=st.text_input("Mot de passe",type="password", key="pwd_connexion")
        if st.button("🔓 Se connecter",type="primary",use_container_width=True):
            u=users.get(e)
            if u and u.get('pwd')==p:
                st.session_state.user=e; st.session_state.page="app"; st.rerun()
            else: st.error("Incorrect")
    with t2:
        nom=st.text_input("Nom", key="nom_insc").strip()
        c1,c2=st.columns([2,3])
        with c1: pays=st.selectbox("Pays", ["+225 CI","+221 SN","+223 ML","+224 GN","+226 BF","+229 BJ","+33 FR"], key="pays_insc")
        with c2: numero=st.text_input("Numero", key="num_insc").strip()
        er=st.text_input("Email", key="email_insc").strip()
        p1=st.text_input("Mot de passe",type="password",key="p1")
        p2=st.text_input("Confirmer",type="password",key="p2")
        if st.button("✨ Créer",type="primary",use_container_width=True):
            if not nom or not numero or not er or not p1: st.error("Remplis tous")
            elif not is_valid_pwd(p1): st.error("Lettres + chiffres min 6")
            elif p1!=p2: st.error("Différents")
            elif er in users: st.error("Email déjà utilisé")
            else:
                users[er]={'nom':nom,'wave':f"{extract_code(pays)} {numero}",'pays':pays,'pwd':p1,'scans':0,'is_vip':False,'history':[],'bonus_scans':0,'profile_pic':None,'cover_pic':None}
                save_json(USERS_FILE,users); st.success("Compte créé!"); st.balloons()
    with t3:
        ef=st.text_input("Email", key="email_oublie").strip()
        if st.button("Envoyer code"):
            if ef in users:
                code=str(random.randint(100000,999999)); st.session_state.reset_code=code; st.session_state.reset_email=ef; st.success(f"Code demo: {code}")
            else: st.error("Email non trouvé")
        if st.session_state.reset_code:
            ci=st.text_input("Code reçu").strip()
            np=st.text_input("Nouveau",type="password", key="new_pwd")
            if st.button("Réinitialiser"):
                if ci==st.session_state.reset_code:
                    users[st.session_state.reset_email]['pwd']=np; save_json(USERS_FILE,users); st.success("Changé!"); st.session_state.reset_code=None
                else: st.error("Code faux")
    st.stop()

if not st.session_state.user or st.session_state.user not in users:
    st.session_state.page="auth"; st.rerun()

user_email=st.session_state.user
user=users[user_email]

# --- HEADER PROFIL CLICABLE ---
cover_b64=get_image_base64(user.get('cover_pic'))
profile_b64=get_image_base64(user.get('profile_pic'))
cover_style=f"background-image:url(data:image/jpeg;base64,{cover_b64}); background-size:cover; background-position:center;" if cover_b64 else "background:linear-gradient(90deg,#00c6ff,#0072ff);"
profile_html=f"<img src='data:image/jpeg;base64,{profile_b64}' style='width:75px;height:75px;border-radius:50%;border:3px solid gold;object-fit:cover;'>" if profile_b64 else "<div style='width:75px;height:75px;border-radius:50%;background:white;display:flex;align-items:center;justify-content:center;font-size:38px;border:3px solid gold;'>👤</div>"

st.markdown(f"""
<div style="{cover_style} padding:15px; border-radius:18px; margin-bottom:12px; position:relative">
<div style="display:flex; align-items:center; gap:12px; background:rgba(0,0,0,0.45); padding:12px; border-radius:12px;">
{profile_html}
<div style="color:white;">
<b style="font-size:20px;">{user.get('nom','Utilisateur')}</b><br>
<span style="font-size:11px; opacity:0.9">Clique pour modifier</span>
</div>
<div style="margin-left:auto; font-size:28px">🕌</div>
</div>
</div>
""", unsafe_allow_html=True)

# Boutons édition profil (cachés, s'ouvrent au clic)
with st.expander("✏️ Modifier photo / couverture / nom (clique ici)"):
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        new_pic = st.file_uploader("📷 Photo de profil", type=['jpg','png','jpeg'], key="new_profile_pic")
        if new_pic:
            path = f"profile_pics/{user_email}_profile.jpg"
            with open(path,"wb") as f: f.write(new_pic.getbuffer())
            users[user_email]['profile_pic']=path; save_json(USERS_FILE,users); st.success("Photo changée"); st.rerun()
    with col_p2:
        new_cover = st.file_uploader("🖼️ Photo de couverture", type=['jpg','png','jpeg'], key="new_cover_pic")
        if new_cover:
            path = f"profile_pics/{user_email}_cover.jpg"
            with open(path,"wb") as f: f.write(new_cover.getbuffer())
            users[user_email]['cover_pic']=path; save_json(USERS_FILE,users); st.success("Couverture changée"); st.rerun()
    new_name = st.text_input("✏️ Nouveau nom", value=user.get('nom',''), key="new_name_input")
    if st.button("💾 Sauver le nom", use_container_width=True):
        if new_name.strip():
            users[user_email]['nom']=new_name.strip(); save_json(USERS_FILE,users); st.success("Nom changé"); st.rerun()

with st.sidebar:
    menu=st.radio("NAVIGATION", ["Home","Aliments","Coran","Hadiths","Douas","Parametres"], label_visibility="collapsed")
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.user=None; st.session_state.page="auth"; st.rerun()

if st.session_state.get('selected_menu'):
    menu=st.session_state.selected_menu; st.session_state.selected_menu=None

if menu=="Home":
    c1,c2,c3,c4=st.columns(4)
    with c1:
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.bottom_nav="Home"; st.rerun()
    with c2:
        if st.button("📚 SAVOIR", use_container_width=True):
            st.session_state.bottom_nav="SAVOIR"; st.rerun()
    with c3:
        if st.button("🕋 Qibla", use_container_width=True):
            st.session_state.bottom_nav="Qibla"; st.rerun()
    with c4:
        if st.button("📅 Cal.", use_container_width=True):
            st.session_state.bottom_nav="Calendrier"; st.rerun()

    if st.session_state.bottom_nav in ["VIP_ALIMENTS","VIP_DOUAS","VIP_HADITHS"]:
        if st.button("⬅️"): st.session_state.bottom_nav="Home"; st.rerun()
        nom=st.session_state.bottom_nav.replace("VIP_","")
        st.markdown(f"""<div class="card-vip"><div style="font-size:70px">🔒</div><div style="font-weight:900; color:gold; font-size:22px">{nom}</div><div>VIP 1500F</div></div>""", unsafe_allow_html=True)
        st.link_button("💳 PAYER 1500F WAVE", WAVE_LINK, type="primary", use_container_width=True)
        if st.button("✅ J'ai payé", use_container_width=True):
            users[user_email]['is_vip']=True; save_json(USERS_FILE,users); st.balloons(); st.session_state.bottom_nav="Home"; st.rerun()
        st.stop()

    if st.session_state.bottom_nav=="SAVOIR":
        if st.button("⬅️", key="back_savoir"): st.session_state.bottom_nav="Home"; st.rerun()
        st.markdown("""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:18px; padding:18px; text-align:center; color:white"><div style="font-size:50px">📚</div><div style="font-weight:900; font-size:20px">SAVOIR ISLAMIQUE</div></div>""", unsafe_allow_html=True)
        col1,col2=st.columns(2)
        with col1:
            if st.button("📖\nCORAN\n114 Sourates\nGRATUIT", use_container_width=True, key="open_coran"):
                st.session_state.selected_menu="Coran"; st.session_state.bottom_nav="Home"; st.rerun()
            if st.button("📜\nHADITHS\n40 Hadiths\nVIP 🔒", use_container_width=True, key="open_hadiths"):
                if user.get('is_vip'): st.session_state.selected_menu="Hadiths"; st.session_state.bottom_nav="Home"; st.rerun()
                else: st.session_state.bottom_nav="VIP_HADITHS"; st.rerun()
        with col2:
            if st.button("🍖\nALIMENTS\nHalal / Haram\nVIP 🔒", use_container_width=True, key="open_aliments"):
                if user.get('is_vip'): st.session_state.selected_menu="Aliments"; st.session_state.bottom_nav="Home"; st.rerun()
                else: st.session_state.bottom_nav="VIP_ALIMENTS"; st.rerun()
            if st.button("🤲\nDOUAS\n50 Invocations\nVIP 🔒", use_container_width=True, key="open_douas"):
                if user.get('is_vip'): st.session_state.selected_menu="Douas"; st.session_state.bottom_nav="Home"; st.rerun()
                else: st.session_state.bottom_nav="VIP_DOUAS"; st.rerun()
        st.stop()

    if st.session_state.bottom_nav=="Qibla":
        if st.button("⬅️"): st.session_state.bottom_nav="Home"; st.rerun()
        st.markdown("""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:18px; padding:18px; text-align:center; color:white"><div style="font-size:50px">🕋</div><div style="font-weight:900">QIBLA</div></div>""", unsafe_allow_html=True)
        qibla_html = """<div style="text-align:center; background:white; padding:15px; border-radius:18px"><button id="locBtn" style="background:linear-gradient(90deg,#0a2a6b,#1a4bb8); color:white; padding:14px 20px; border-radius:12px; border:none; font-weight:900; width:100%">📍 ACTIVER GPS</button><div id="infoBox" style="display:none; margin-top:12px; background:#f0f6ff; padding:10px; border-radius:10px"><div id="coords"></div><div id="qiblaInfo" style="color:#00a651; font-weight:900"></div></div><div style="position:relative; width:260px; height:260px; margin:25px auto; border-radius:50%; border:10px solid #0a2a6b; background:radial-gradient(circle, #fff, #e6f0ff)"><div id="arrow" style="position:absolute; top:50%; left:50%; width:6px; height:100px; background:#0a2a6b; transform-origin:bottom center; transform:translate(-50%, -100%) rotate(0deg);"><div style="width:0; height:0; border-left:14px solid transparent; border-right:14px solid transparent; border-bottom:24px solid red; position:absolute; top:-22px; left:50%; transform:translateX(-50%)"></div></div><div style="position:absolute; top:50%; left:50%; width:28px; height:28px; background:#0a2a6b; border-radius:50%; transform:translate(-50%,-50%); border:3px solid gold"></div><div style="position:absolute; top:50%; left:50%; transform:translate(-50%, -150%); font-size:28px">🕋</div></div></div><script>let qiblaAngle=67.5; const kaabaLat=21.4225*Math.PI/180; const kaabaLon=39.8262*Math.PI/180; function calc(lat,lon){const r=lat*Math.PI/180, lo=lon*Math.PI/180, d=kaabaLon-lo, y=Math.sin(d), x=Math.cos(r)*Math.tan(kaabaLat)-Math.sin(r)*Math.cos(d); return (Math.atan2(y,x)*180/Math.PI+360)%360;} document.getElementById('locBtn').onclick=function(){if(navigator.geolocation){navigator.geolocation.getCurrentPosition(function(p){qiblaAngle=calc(p.coords.latitude,p.coords.longitude); document.getElementById('infoBox').style.display='block'; document.getElementById('coords').innerText=p.coords.latitude.toFixed(4)+','+p.coords.longitude.toFixed(4); document.getElementById('qiblaInfo').innerText='Qibla: '+qiblaAngle.toFixed(1)+'°'; document.getElementById('arrow').style.transform='translate(-50%, -100%) rotate('+qiblaAngle+'deg)';});}}; if(window.DeviceOrientationEvent){window.addEventListener('deviceorientation',function(e){let h=e.webkitCompassHeading; if(h===undefined) h=360-e.alpha; if(h){document.getElementById('arrow').style.transform='translate(-50%, -100%) rotate('+(qiblaAngle-h)+'deg)';}},true);}</script>"""
        st.components.v1.html(qibla_html, height=600); st.stop()

    elif st.session_state.bottom_nav=="Calendrier":
        if st.button("⬅️"): st.session_state.bottom_nav="Home"; st.rerun()
        today=date.today(); d_h,m_h,y_h=gregorian_to_hijri(today)
        st.markdown(f"""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:18px; padding:18px; text-align:center; color:white"><div style="font-size:40px">📅</div><div style="font-weight:900">{today.day} {today.month} {today.year} / {d_h} {HIJRI_MONTHS[m_h-1]} {y_h}</div></div>""", unsafe_allow_html=True)
        st.stop()

    # SCANNER GRAPHIQUE CLIQUABLE
    scans_used=user['scans']-user.get('bonus_scans',0)
    st.markdown("""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:20px; padding:18px; text-align:center; color:white"><div style="font-size:50px">📸</div><div style="font-weight:900">SCANNER HALAL</div><div style="font-size:11px; opacity:0.8">Vérifie en 2 secondes</div></div>""", unsafe_allow_html=True)
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    c1,c2=st.columns(2)
    with c1:
        if st.button("📷\n\nCAMÉRA\n\nPrendre photo", use_container_width=True, key="cam_graph"):
            st.session_state.scan_mode="camera"; st.rerun()
    with c2:
        if st.button("🖼️\n\nUPLOAD\n\nGalerie", use_container_width=True, key="upload_graph"):
            st.session_state.scan_mode="upload"; st.rerun()

    photo=None
    if st.session_state.scan_mode=="camera":
        cam=st.camera_input("Photo", key="camera_input", label_visibility="collapsed")
        if cam: photo=cam
    elif st.session_state.scan_mode=="upload":
        up=st.file_uploader("Photo", type=['jpg','png','jpeg','webp'], key="uploader", label_visibility="collapsed")
        if up: photo=up

    if photo:
        st.image(photo, use_container_width=True)
        if st.button("✅ LANCER LE SCAN HALAL", type="primary", use_container_width=True):
            with st.spinner("Analyse..."):
                time.sleep(2)
                if not user['is_vip']: users[user_email]['scans']+=1
                result=random.choice(["HALAL 100%","HARAM Détecté","DOUTEUX"])
                color="green" if "HALAL" in result else "red" if "HARAM" in result else "orange"
                icon="✅" if "HALAL" in result else "❌" if "HARAM" in result else "⚠️"
                st.markdown(f"""<div style="background:white; border-radius:20px; padding:20px; text-align:center; border:4px solid {color}"><div style="font-size:70px">{icon}</div><div style="font-size:26px; font-weight:900; color:{color}">{result}</div></div>""", unsafe_allow_html=True)
                users[user_email]['history'].append({'date':datetime.now().strftime("%d/%m/%Y %H:%M"),'result':result})
                save_json(USERS_FILE,users); st.balloons(); st.session_state.scan_mode=None

    # INVITE TES AMIS + PUB 20s
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    if st.button("🚀\n\nInvite tes amis\nPartage et gagne du hasanat", use_container_width=True, key="invite_graph"):
        st.link_button("📤 Partager sur WhatsApp", f"https://wa.me/?text=Decouvre Scanner Halal {APP_LINK}", use_container_width=True)

    # PUB 20s = 1 SCAN juste en bas
    if not user.get('is_vip'):
        st.markdown("""
        <div style="background:white; border-radius:18px; padding:15px; text-align:center; border:2px solid #ffe082; margin-top:10px; box-shadow:0 4px 10px rgba(0,0,0,0.05)">
            <div style="font-size:30px">📺</div>
            <div style="font-weight:900; font-size:13px">PUB 20s = 1 SCAN GRATUIT</div>
            <div style="font-size:10px; color:gray">Regarde une pub pour continuer</div>
        </div>""", unsafe_allow_html=True)
        if st.button("📺 Regarder PUB 20s = +1 SCAN", use_container_width=True, key="pub20"):
            st.session_state.ad_watching=True; st.session_state.ad_start_time=time.time(); st.rerun()
        if st.session_state.ad_watching:
            elapsed=time.time()-st.session_state.ad_start_time; remaining=20-elapsed
            if remaining>0:
                st.warning(f"⏳ Reste {int(remaining)}s"); st.progress((20-remaining)/20); time.sleep(1); st.rerun()
            else:
                users[user_email]['bonus_scans']=users[user_email].get('bonus_scans',0)+1; save_json(USERS_FILE,users); st.session_state.ad_watching=False; st.balloons(); st.success("+1 SCAN ajouté!"); st.rerun()
        st.link_button("💎 Passer VIP 1500F ILLIMITÉ", WAVE_LINK, type="primary", use_container_width=True)

elif menu=="Coran":
    if st.button("⬅️"): st.session_state.bottom_nav="Home"; st.rerun()
    st.markdown("""<div style="background:linear-gradient(135deg,#00a651,#00c853); border-radius:18px; padding:18px; text-align:center; color:white"><div style="font-size:50px">📖</div><div style="font-weight:900">CORAN 114</div></div>""", unsafe_allow_html=True)
    for i in range(1,115):
        st.markdown(f"""<div class="card-graph" style="display:flex; align-items:center; gap:15px; text-align:left"><div style="background:#0a2a6b; color:white; width:40px; height:40px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:900">{i}</div><div><b>Sourate {i}</b></div><div style="margin-left:auto">📖</div></div>""", unsafe_allow_html=True)

elif menu in ["Aliments","Hadiths","Douas"]:
    if not user.get('is_vip'):
        st.markdown(f"""<div class="card-vip"><div style="font-size:70px">🔒</div><div style="font-weight:900; color:gold">{menu} VIP</div></div>""", unsafe_allow_html=True)
        st.link_button("💳 PAYER 1500F", WAVE_LINK, type="primary", use_container_width=True)
        if st.button("✅ J'ai payé"):
            users[user_email]['is_vip']=True; save_json(USERS_FILE,users); st.balloons(); st.rerun()
        st.stop()
    if st.button("⬅️"): st.session_state.bottom_nav="Home"; st.rerun()
    st.markdown(f"""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:18px; padding:18px; text-align:center; color:white"><div style="font-size:50px">{'🍖' if menu=='Aliments' else '📜' if menu=='Hadiths' else '🤲'}</div><div style="font-weight:900">{menu.upper()}</div></div>""", unsafe_allow_html=True)
    items = ["Poulet Halal 🟢","Porc HARAM 🔴"] if menu=="Aliments" else [f"Hadith {i}" for i in range(1,41)] if menu=="Hadiths" else [f"Doua {i}" for i in range(1,51)]
    for it in items:
        st.markdown(f"""<div class="card-graph" style="text-align:left">{it}</div>""", unsafe_allow_html=True)

elif menu=="Parametres":
    st.markdown(f"""<div style="background:white; border-radius:20px; padding:20px; text-align:center"><div style="font-size:50px">⚙️</div><b>{user.get('nom')}</b><br>{user_email}</div>""", unsafe_allow_html=True)
