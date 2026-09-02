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
    mh=int((l-1)//29.5)+1;
    if mh>12: mh=12
    dh=int(l-(mh-1)*29.5)
    if dh<1: dh=1
    if dh>30: dh=30
    yh=30*n+j+1
    return dh,mh,yh

def get_image_base64(path):
    if path and os.path.exists(path):
        try:
            with open(path,"rb") as f: return base64.b64encode(f.read()).decode()
        except: return None
    return None

def show_back_button():
    if st.button("⬅️", key=f"back_{st.session_state.bottom_nav}"):
        st.session_state.bottom_nav="Home"; st.rerun()

def share_zone():
    st.link_button("📤 Partager l'app", f"https://wa.me/?text=Decouvre Scanner Halal {APP_LINK}", use_container_width=True)

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

ALIMENTS_HALAL = ["Poulet halal","Boeuf halal","Mouton halal","Poisson thon","Riz","Mangue","Banane","Lait halal","Miel","Dattes"]
ALIMENTS_HARAM = ["Porc HARAM","Vin HARAM","Biere HARAM","Gelatine porcine E441 HARAM","E120 Cochenille HARAM"]
SOURATES_114 = [f"{i+1}. Sourate {i+1}" for i in range(114)]
HADITHS_40 = [f"Hadith {i+1}: Les actions ne valent que par intentions" for i in range(40)]
DUAS_50 = [f"Doua {i+1}: Bismillah" for i in range(50)]

users=load_json(USERS_FILE,{})

st.set_page_config(page_title="Scanner Halal", page_icon="🕌", layout="centered")
st.markdown("""
<style>
#MainMenu{visibility:hidden} footer{visibility:hidden} header{visibility:hidden}
.block-container{padding-top:10px; padding-bottom:120px;}
.card{background:white; margin:8px 0px; padding:15px; border-radius:12px; border:1px solid #eee; box-shadow:0 2px 4px rgba(0,0,0,0.05)}
.card-vip{background:linear-gradient(135deg,#0a2a6b,#1a4bb8);color:white;padding:25px;border-radius:15px;margin:12px 0px; text-align:center}
</style>
""", unsafe_allow_html=True)

if 'user' not in st.session_state: st.session_state.user=None
if 'page' not in st.session_state: st.session_state.page="auth"
if 'reset_code' not in st.session_state: st.session_state.reset_code=None
if 'scan_mode' not in st.session_state: st.session_state.scan_mode=None
if 'bottom_nav' not in st.session_state: st.session_state.bottom_nav="Home"
if 'selected_menu' not in st.session_state: st.session_state.selected_menu=None
if 'ad_watching' not in st.session_state: st.session_state.ad_watching=False
if 'ad_start_time' not in st.session_state: st.session_state.ad_start_time=None

if st.session_state.page=="auth":
    try: st.image("logo.jpeg", use_container_width=True)
    except: st.markdown("<h1 style='text-align:center;'>🕌 Scanner Halal</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;color:#0a2a6b;'>Bienvenue 🕌</h2>", unsafe_allow_html=True)
    t1,t2,t3=st.tabs(["Connexion","Inscription","Mot de passe oublie"])
    with t1:
        e=st.text_input("Email", key="email_connexion").strip()
        p=st.text_input("Mot de passe",type="password", key="pwd_connexion")
        if st.button("Se connecter",type="primary",use_container_width=True):
            u=users.get(e)
            if u and u.get('pwd')==p:
                st.session_state.user=e; st.session_state.page="app"; st.rerun()
            else: st.error("Email ou mot de passe incorrect")
    with t2:
        nom=st.text_input("Nom", key="nom_insc").strip()
        c1,c2=st.columns([2,3])
        with c1: pays=st.selectbox("Pays", ["+225 CI","+221 SN","+223 ML","+224 GN","+226 BF","+229 BJ","+33 FR"], key="pays_insc")
        with c2: numero=st.text_input("Numero", placeholder="0771845766", key="num_insc").strip()
        er=st.text_input("Email", key="email_insc").strip()
        p1=st.text_input("Mot de passe (lettres+chiffres)",type="password",key="p1")
        p2=st.text_input("Confirmer",type="password",key="p2")
        if st.button("Creer mon compte",type="primary",use_container_width=True):
            if not nom or not numero or not er or not p1: st.error("Remplis tous les champs")
            elif not is_valid_pwd(p1): st.error("Lettres + chiffres min 6 ex: baba2000")
            elif p1!=p2: st.error("Mots de passe differents")
            elif er in users: st.error("Email deja utilise")
            else:
                users[er]={'nom':nom,'wave':f"{extract_code(pays)} {numero}",'pays':pays,'pwd':p1,'scans':0,'is_vip':False,'history':[],'bonus_scans':0,'profile_pic':None,'cover_pic':None}
                save_json(USERS_FILE,users); st.success("Compte cree! Va dans Connexion"); st.balloons()
    with t3:
        ef=st.text_input("Email", key="email_oublie").strip()
        if st.button("Envoyer code"):
            if ef in users:
                code=str(random.randint(100000,999999)); st.session_state.reset_code=code; st.session_state.reset_email=ef; st.success(f"Code demo: {code}")
            else: st.error("Email non trouve")
        if st.session_state.reset_code:
            ci=st.text_input("Code recu").strip()
            np=st.text_input("Nouveau mot de passe",type="password", key="new_pwd")
            if st.button("Reinitialiser"):
                if ci==st.session_state.reset_code:
                    users[st.session_state.reset_email]['pwd']=np; save_json(USERS_FILE,users); st.success("Mot de passe change!"); st.session_state.reset_code=None
                else: st.error("Code faux")
    st.stop()

if not st.session_state.user or st.session_state.user not in users:
    st.session_state.page="auth"; st.rerun()

user_email=st.session_state.user
user=users[user_email]

cover_b64=get_image_base64(user.get('cover_pic'))
profile_b64=get_image_base64(user.get('profile_pic'))
cover_style=f"background-image:url(data:image/jpeg;base64,{cover_b64}); background-size:cover;" if cover_b64 else "background:linear-gradient(90deg,#00c6ff,#0072ff);"
profile_html=f"<img src='data:image/jpeg;base64,{profile_b64}' style='width:70px;height:70px;border-radius:50%;border:3px solid white;object-fit:cover;'>" if profile_b64 else "<div style='width:70px;height:70px;border-radius:50%;background:white;display:flex;align-items:center;justify-content:center;font-size:30px;border:3px solid white;'>👤</div>"

st.markdown(f"""
<div style="{cover_style} padding:15px; border-radius:12px; margin-bottom:10px;">
<div style="display:flex; align-items:center; gap:12px; background:rgba(0,0,0,0.4); padding:10px; border-radius:10px;">
{profile_html}
<div style="color:white;">
<b style="font-size:20px;">{user.get('nom','Utilisateur')}</b><br>
<span style="background:gold; color:black; padding:2px 10px; border-radius:10px; font-size:11px; font-weight:bold;">{"VIP ILLIMITE" if user.get('is_vip') else "GRATUIT"}</span>
</div>
</div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    menu=st.radio("NAVIGATION", ["Home","Aliments","Coran","Hadiths","Douas","Parametres"], label_visibility="collapsed")
    if st.button("Deconnexion", use_container_width=True):
        st.session_state.user=None; st.session_state.page="auth"; st.rerun()

if st.session_state.get('selected_menu'):
    menu=st.session_state.selected_menu; st.session_state.selected_menu=None

if menu=="Home":
    c1,c2,c3,c4=st.columns(4)
    with c1:
        if st.button("🏠 Home", use_container_width=True, type="primary" if st.session_state.bottom_nav=="Home" else "secondary"):
            st.session_state.bottom_nav="Home"; st.rerun()
    with c2:
        if st.button("📚 SAVOIR", use_container_width=True, type="primary" if st.session_state.bottom_nav=="SAVOIR" else "secondary"):
            st.session_state.bottom_nav="SAVOIR"; st.rerun()
    with c3:
        if st.button("🕋 Qibla", use_container_width=True, type="primary" if st.session_state.bottom_nav=="Qibla" else "secondary"):
            st.session_state.bottom_nav="Qibla"; st.rerun()
    with c4:
        if st.button("📅 Cal.", use_container_width=True, type="primary" if st.session_state.bottom_nav=="Calendrier" else "secondary"):
            st.session_state.bottom_nav="Calendrier"; st.rerun()

    if st.session_state.bottom_nav in ["VIP_ALIMENTS","VIP_DOUAS","VIP_HADITHS"]:
        show_back_button()
        nom=st.session_state.bottom_nav.replace("VIP_","")
        st.markdown(f"""<div class="card-vip"><h2 style="color:gold;">{nom} - VIP Seulement</h2></div>""", unsafe_allow_html=True)
        st.link_button("PAYER 1500F WAVE", WAVE_LINK, type="primary", use_container_width=True)
        if st.button("J'ai paye - Activer VIP", use_container_width=True, key="vip_activate"):
            users[user_email]['is_vip']=True; save_json(USERS_FILE,users); st.balloons(); st.session_state.bottom_nav="Home"; st.rerun()
        st.stop()

    if st.session_state.bottom_nav=="SAVOIR":
        if st.button("⬅️", key="back_savoir"):
            st.session_state.bottom_nav="Home"; st.rerun()
        st.title("📚 SAVOIR")
        col1,col2=st.columns(2)
        with col1:
            st.markdown("""<div style="background:white; border-radius:16px; padding:20px; text-align:center; border:2px solid #eee; box-shadow:0 4px 10px rgba(0,0,0,0.05)"><div style="font-size:50px">📖</div><div style="font-weight:bold; margin-top:5px">CORAN</div><div style="color:green; font-size:12px; font-weight:bold">GRATUIT</div></div>""", unsafe_allow_html=True)
            if st.button("Ouvrir Coran", use_container_width=True, key="open_coran"):
                st.session_state.selected_menu="Coran"; st.session_state.bottom_nav="Home"; st.rerun()
            st.markdown("""<div style="background:white; border-radius:16px; padding:20px; text-align:center; border:2px solid #eee; margin-top:12px"><div style="font-size:50px">📜</div><div style="font-weight:bold; margin-top:5px">HADITHS</div><div style="color:gold; background:#0a2a6b; display:inline-block; padding:2px 8px; border-radius:10px; font-size:11px; margin-top:4px">VIP 🔒</div></div>""", unsafe_allow_html=True)
            if st.button("Ouvrir Hadiths", use_container_width=True, key="open_hadiths"):
                if user.get('is_vip'):
                    st.session_state.selected_menu="Hadiths"; st.session_state.bottom_nav="Home"; st.rerun()
                else:
                    st.session_state.bottom_nav="VIP_HADITHS"; st.rerun()
        with col2:
            st.markdown("""<div style="background:white; border-radius:16px; padding:20px; text-align:center; border:2px solid #eee;"><div style="font-size:50px">🍖</div><div style="font-weight:bold; margin-top:5px">ALIMENTS</div><div style="color:gold; background:#0a2a6b; display:inline-block; padding:2px 8px; border-radius:10px; font-size:11px; margin-top:4px">VIP 🔒</div></div>""", unsafe_allow_html=True)
            if st.button("Ouvrir Aliments", use_container_width=True, key="open_aliments"):
                if user.get('is_vip'):
                    st.session_state.selected_menu="Aliments"; st.session_state.bottom_nav="Home"; st.rerun()
                else:
                    st.session_state.bottom_nav="VIP_ALIMENTS"; st.rerun()
            st.markdown("""<div style="background:white; border-radius:16px; padding:20px; text-align:center; border:2px solid #eee; margin-top:12px"><div style="font-size:50px">🤲</div><div style="font-weight:bold; margin-top:5px">DOUAS</div><div style="color:gold; background:#0a2a6b; display:inline-block; padding:2px 8px; border-radius:10px; font-size:11px; margin-top:4px">VIP 🔒</div></div>""", unsafe_allow_html=True)
            if st.button("Ouvrir Douas", use_container_width=True, key="open_douas"):
                if user.get('is_vip'):
                    st.session_state.selected_menu="Douas"; st.session_state.bottom_nav="Home"; st.rerun()
                else:
                    st.session_state.bottom_nav="VIP_DOUAS"; st.rerun()
        st.markdown("---"); share_zone(); st.stop()

    if st.session_state.bottom_nav=="Qibla":
        if st.button("⬅️", key="back_qibla"): st.session_state.bottom_nav="Home"; st.rerun()
        st.title("🕋 Qibla")
        qibla_html = """
        <div style="font-family:sans-serif; text-align:center; background:white; padding:15px; border-radius:12px">
            <button id="locBtn" style="background:linear-gradient(90deg,#0a2a6b,#1a4bb8); color:white; padding:14px 20px; border-radius:12px; border:none; font-weight:bold; width:100%">📍 Activer localisation & Chercher Qibla</button>
            <div id="infoBox" style="margin-top:15px; padding:12px; background:#f0f6ff; border-radius:10px; border-left:4px solid #0a2a6b; text-align:left; display:none">
                <div id="coords" style="font-size:13px; color:#0a2a6b; font-weight:bold"></div>
                <div id="qiblaInfo" style="font-size:16px; font-weight:bold; color:#00a651; margin-top:5px"></div>
            </div>
            <div style="display:flex; gap:8px; justify-content:center; margin-top:15px">
                <button onclick="setMode('classique')" id="btn-classique" style="padding:8px 12px; border-radius:20px; border:2px solid #0a2a6b; background:#0a2a6b; color:white; font-size:12px">Classique</button>
                <button onclick="setMode('moderne')" id="btn-moderne" style="padding:8px 12px; border-radius:20px; border:1px solid #ddd; background:white; font-size:12px">Moderne</button>
                <button onclick="setMode('rose')" id="btn-rose" style="padding:8px 12px; border-radius:20px; border:1px solid #ddd; background:white; font-size:12px">Rose</button>
                <button onclick="setMode('num')" id="btn-num" style="padding:8px 12px; border-radius:20px; border:1px solid #ddd; background:white; font-size:12px">Numérique</button>
            </div>
            <div style="position:relative; width:260px; height:260px; margin:25px auto; border-radius:50%; border:10px solid #0a2a6b; background:radial-gradient(circle, #fff, #e6f0ff); box-shadow:0 8px 20px rgba(0,0,0,0.2)">
                <div style="position:absolute; top:8px; left:50%; transform:translateX(-50%); font-weight:900; color:red; font-size:18px">N</div>
                <div style="position:absolute; bottom:8px; left:50%; transform:translateX(-50%); font-weight:900">S</div>
                <div style="position:absolute; left:10px; top:50%; transform:translateY(-50%); font-weight:900">O</div>
                <div style="position:absolute; right:10px; top:50%; transform:translateY(-50%); font-weight:900">E</div>
                <div id="arrow" style="position:absolute; top:50%; left:50%; width:6px; height:100px; background:linear-gradient(to top, #0a2a6b, #00c6ff); transform-origin:bottom center; transform:translate(-50%, -100%) rotate(0deg); border-radius:4px; transition:transform 0.8s"><div style="width:0; height:0; border-left:14px solid transparent; border-right:14px solid transparent; border-bottom:24px solid #ff0030; position:absolute; top:-22px; left:50%; transform:translateX(-50%)"></div></div>
                <div style="position:absolute; top:50%; left:50%; width:28px; height:28px; background:#0a2a6b; border-radius:50%; transform:translate(-50%,-50%); border:3px solid gold"></div>
                <div id="kaabaIcon" style="position:absolute; top:50%; left:50%; font-size:28px; transform:translate(-50%, -150%)">🕋</div>
            </div>
            <div id="status" style="font-size:12px; color:gray">Clique pour activer GPS. Bouge ton téléphone ensuite.</div>
        </div>
        <script>
        let qiblaAngle=67.5; const kaabaLat=21.4225*Math.PI/180; const kaabaLon=39.8262*Math.PI/180;
        function setMode(m){document.querySelectorAll('[id^=btn-]').forEach(b=>{b.style.background='white'; b.style.color='black'; b.style.border='1px solid #ddd'}); document.getElementById('btn-'+m).style.background='#0a2a6b'; document.getElementById('btn-'+m).style.color='white';}
        function calculateQibla(lat,lon){const latRad=lat*Math.PI/180; const lonRad=lon*Math.PI/180; const dLon=kaabaLon-lonRad; const y=Math.sin(dLon); const x=Math.cos(latRad)*Math.tan(kaabaLat)-Math.sin(latRad)*Math.cos(dLon); let brng=Math.atan2(y,x)*180/Math.PI; return (brng+360)%360;}
        document.getElementById('locBtn').onclick=function(){const btn=this; btn.innerText='📡 Recherche GPS...'; if(navigator.geolocation){navigator.geolocation.getCurrentPosition(function(pos){const lat=pos.coords.latitude; const lon=pos.coords.longitude; qiblaAngle=calculateQibla(lat,lon); document.getElementById('infoBox').style.display='block'; document.getElementById('coords').innerHTML='📍 Lat: '+lat.toFixed(6)+'<br>📍 Lon: '+lon.toFixed(6); document.getElementById('qiblaInfo').innerText='🕋 Qibla: '+qiblaAngle.toFixed(2)+'°'; document.getElementById('status').innerHTML='<b style="color:green">✅ Qibla trouvée!</b>'; btn.innerText='✅ Qibla trouvée'; btn.style.background='#00a651'; document.getElementById('arrow').style.transform='translate(-50%, -100%) rotate('+qiblaAngle+'deg)';},function(){document.getElementById('infoBox').style.display='block'; document.getElementById('coords').innerText='GPS refusé - Abidjan 5.36, -4.00'; qiblaAngle=calculateQibla(5.36,-4.00); document.getElementById('qiblaInfo').innerText='🕋 Qibla: '+qiblaAngle.toFixed(2)+'°'; document.getElementById('arrow').style.transform='translate(-50%, -100%) rotate('+qiblaAngle+'deg)';},{enableHighAccuracy:true});}};
        if(window.DeviceOrientationEvent){window.addEventListener('deviceorientation',function(e){let heading=e.webkitCompassHeading; if(heading===undefined) heading=360-e.alpha; if(heading){let finalAngle=qiblaAngle-heading; document.getElementById('arrow').style.transform='translate(-50%, -100%) rotate('+finalAngle+'deg)';}},true);}
        </script>
        """
        st.components.v1.html(qibla_html, height=650); st.stop()

    elif st.session_state.bottom_nav=="Calendrier":
        if st.button("⬅️", key="back_cal"): st.session_state.bottom_nav="Home"; st.rerun()
        st.title("📅 Calendrier")
        today=date.today(); d_h,m_h,y_h=gregorian_to_hijri(today)
        calendar.setfirstweekday(calendar.MONDAY)
        month_names=["","Janvier","Février","Mars","Avril","Mai","Juin","Juillet","Août","Septembre","Octobre","Novembre","Décembre"]
        month_name=month_names[today.month]
        month_days=calendar.monthcalendar(today.year,today.month)
        html_cal=f"""<div style="background:white; padding:12px; border-radius:12px; border:1px solid #eee"><div style="text-align:center; font-weight:bold; font-size:18px; color:#0a2a6b; margin-bottom:8px">{month_name} {today.year}</div><div style="display:grid; grid-template-columns:repeat(7,1fr); gap:4px; text-align:center; font-size:12px; font-weight:bold; color:#888"><div>Lun</div><div>Mar</div><div>Mer</div><div>Jeu</div><div>Ven</div><div>Sam</div><div>Dim</div></div><div style="display:grid; grid-template-columns:repeat(7,1fr); gap:4px; text-align:center; margin-top:6px">"""
        for week in month_days:
            for d in week:
                if d==0: html_cal+='<div style="padding:10px"></div>'
                elif d==today.day: html_cal+=f'<div style="padding:10px; background:#0a2a6b; color:white; border-radius:8px; font-weight:bold; border:2px solid gold">{d}</div>'
                else: html_cal+=f'<div style="padding:10px; background:#f5f7ff; border-radius:8px">{d}</div>'
        html_cal+="</div></div>"
        col1,col2=st.columns(2)
        with col1:
            st.markdown(f"""<div style="background:white; padding:10px; border-radius:12px; border-left:5px solid #0072ff; margin-bottom:8px; text-align:center"><b>🌍 Grégorien</b><br><span style="font-size:20px; font-weight:bold; color:#0a2a6b">{today.day} {month_name} {today.year}</span></div>""", unsafe_allow_html=True)
            st.components.v1.html(html_cal, height=320)
        with col2:
            st.markdown(f"""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); padding:15px; border-radius:12px; color:white; text-align:center; min-height:300px"><b style="color:gold">🌙 Hijri</b><br><span style="font-size:36px; font-weight:bold">{d_h}</span><br><b style="color:gold; font-size:20px">{HIJRI_MONTHS[m_h-1]}</b><br><b style="font-size:20px">{y_h} AH</b></div>""", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("""<div style="background:white; padding:12px; border-radius:12px; border-left:5px solid #00a651">🌙 <b>Ramadan 1447</b> : 18 Février 2026<br>🎉 <b>Aïd al-Fitr</b> : 20 Mars 2026<br>🕋 <b>Aïd al-Adha</b> : 27 Mai 2026</div>""", unsafe_allow_html=True)
        st.markdown("---"); share_zone(); st.stop()

    # HOME SCANNER
    scans_used=user['scans']-user.get('bonus_scans',0)
    if not user['is_vip'] and scans_used>=5:
        st.error("🚫 5 essais gratuits utilises")
        if st.button("📺 PUB 15s = +1 SCAN", use_container_width=True):
            st.session_state.ad_watching=True; st.session_state.ad_start_time=time.time(); st.rerun()
        st.link_button("💎 VIP 1500F ILLIMITE", WAVE_LINK, type="primary", use_container_width=True)
        if st.session_state.ad_watching:
            elapsed=time.time()-st.session_state.ad_start_time; remaining=15-elapsed
            if remaining>0:
                st.warning(f"⏳ {int(remaining)}s"); st.progress((15-remaining)/15); time.sleep(1); st.rerun()
            else:
                users[user_email]['bonus_scans']=users[user_email].get('bonus_scans',0)+1; save_json(USERS_FILE,users); st.session_state.ad_watching=False; st.balloons(); st.success("+1 SCAN!"); st.rerun()
        st.stop()

    st.markdown("### 📸 Scanner Halal")
    c1,c2=st.columns(2)
    with c1:
        if st.button("📷 CAMERA", type="primary", use_container_width=True): st.session_state.scan_mode="camera"; st.rerun()
    with c2:
        if st.button("🖼️ UPLOAD", type="primary", use_container_width=True): st.session_state.scan_mode="upload"; st.rerun()
    photo=None
    if st.session_state.scan_mode=="camera":
        cam=st.camera_input("Prends photo", key="camera_input", label_visibility="collapsed")
        if cam: photo=cam
    elif st.session_state.scan_mode=="upload":
        up=st.file_uploader("Choisis photo", type=['jpg','png','jpeg','webp'], key="uploader", label_visibility="collapsed")
        if up: photo=up
    if photo:
        st.image(photo, caption="Photo ajoutee", use_container_width=True)
        if st.button("✅ LANCER LE SCAN HALAL", type="primary", use_container_width=True):
            with st.spinner("Analyse..."):
                time.sleep(2)
                if not user['is_vip']: users[user_email]['scans']+=1
                result=random.choice(["HALAL 100% Halal","HARAM Haram detecte","DOUTEUX Verifier"])
                color="green" if "HALAL" in result else "red" if "HARAM" in result else "orange"
                st.markdown(f"<div class='card' style='border-left:8px solid {color}'><h2 style='color:{color}'>{result}</h2></div>", unsafe_allow_html=True)
                users[user_email]['history'].append({'date':datetime.now().strftime("%d/%m/%Y %H:%M"),'result':result})
                save_json(USERS_FILE,users); st.balloons(); st.session_state.scan_mode=None
    share_zone()

elif menu=="Coran":
    show_back_button() if st.session_state.bottom_nav!="Home" else None
    if st.button("⬅️ Home", key="back_coran"): st.session_state.bottom_nav="Home"; st.rerun()
    st.title("📖 Coran - 114 Sourates")
    st.markdown("<p style='color:green; font-weight:bold'>GRATUIT - Acces libre</p>", unsafe_allow_html=True)
    for s in SOURATES_114:
        st.markdown(f"<div class='card'>🕌 {s}</div>", unsafe_allow_html=True)
    share_zone()

elif menu in ["Aliments","Hadiths","Douas"]:
    if not user.get('is_vip'):
        st.markdown(f"""<div class="card-vip"><h2 style="color:gold;">{menu} - VIP Seulement</h2><p>Active VIP 1500F pour debloquer</p></div>""", unsafe_allow_html=True)
        st.link_button("PAYER 1500F WAVE", WAVE_LINK, type="primary", use_container_width=True)
        if st.button("J'ai paye - Activer VIP", key=f"vip_{menu}"):
            users[user_email]['is_vip']=True; save_json(USERS_FILE,users); st.balloons(); st.rerun()
        st.stop()
    if st.button("⬅️", key=f"back_{menu}"): st.session_state.bottom_nav="Home"; st.rerun()
    st.title(f"📚 {menu}")
    items = ALIMENTS_HALAL+ALIMENTS_HARAM if menu=="Aliments" else HADITHS_40 if menu=="Hadiths" else DUAS_50
    for it in items:
        st.markdown(f"<div class='card'>{it}</div>", unsafe_allow_html=True)
    share_zone()

elif menu=="Parametres":
    st.title("Parametres")
    st.markdown(f"""<div class='card'><b>Nom:</b> {user.get('nom')}<br><b>Email:</b> {user_email}<br><b>VIP:</b> {'Oui' if user.get('is_vip') else 'Non'}</div>""", unsafe_allow_html=True)
    share_zone()
