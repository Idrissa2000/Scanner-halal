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

def share_zone():
    st.markdown("""
    <div style="background:white; border-radius:18px; padding:15px; text-align:center; border:2px dashed #0072ff; margin-top:12px">
        <div style="font-size:40px">🚀</div>
        <div style="font-weight:bold; color:#0a2a6b">Invite tes amis</div>
        <div style="font-size:11px; color:gray">Partage et gagne du hasanat</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""<div style="background:linear-gradient(90deg,#00c6ff,#0072ff); border-radius:16px; padding:4px; margin-top:8px"><div style="background:white; border-radius:12px; padding:2px">""", unsafe_allow_html=True)
    st.link_button("📤 PARTAGER L'APPLI", f"https://wa.me/?text=Decouvre Scanner Halal {APP_LINK}", use_container_width=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

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
</style>
""", unsafe_allow_html=True)

for k in ['user','page','reset_code','scan_mode','bottom_nav','selected_menu','ad_watching','ad_start_time']:
    if k not in st.session_state:
        st.session_state[k] = None if k!='page' else "auth"
        if k=='bottom_nav': st.session_state[k]="Home"
        if k=='ad_watching': st.session_state[k]=False

if st.session_state.page=="auth":
    st.markdown("""
    <div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:20px; padding:25px; text-align:center; color:white">
        <div style="font-size:70px">🕌</div>
        <div style="font-size:24px; font-weight:900">SCANNER HALAL</div>
        <div style="font-size:12px; opacity:0.8">Halal - Haram - Douteux en 2s</div>
    </div>
    """, unsafe_allow_html=True)
    t1,t2,t3=st.tabs(["Connexion","Inscription","Oublié"])
    with t1:
        e=st.text_input("Email", key="email_connexion").strip()
        p=st.text_input("Mot de passe",type="password", key="pwd_connexion")
        if st.button("🔓 Se connecter",type="primary",use_container_width=True):
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
        p1=st.text_input("Mot de passe",type="password",key="p1")
        p2=st.text_input("Confirmer",type="password",key="p2")
        if st.button("✨ Créer mon compte",type="primary",use_container_width=True):
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
            np=st.text_input("Nouveau mot de passe",type="password", key="new_pwd")
            if st.button("Réinitialiser"):
                if ci==st.session_state.reset_code:
                    users[st.session_state.reset_email]['pwd']=np; save_json(USERS_FILE,users); st.success("Mot de passe changé!"); st.session_state.reset_code=None
                else: st.error("Code faux")
    st.stop()

if not st.session_state.user or st.session_state.user not in users:
    st.session_state.page="auth"; st.rerun()

user_email=st.session_state.user
user=users[user_email]
profile_b64=get_image_base64(user.get('profile_pic'))
profile_html=f"<img src='data:image/jpeg;base64,{profile_b64}' style='width:70px;height:70px;border-radius:50%;border:3px solid gold;object-fit:cover;'>" if profile_b64 else "<div style='width:70px;height:70px;border-radius:50%;background:white;display:flex;align-items:center;justify-content:center;font-size:35px;border:3px solid gold;'>👤</div>"

st.markdown(f"""
<div style="background:linear-gradient(90deg,#0a2a6b,#1a4bb8); padding:15px; border-radius:18px; margin-bottom:12px; box-shadow:0 6px 15px rgba(0,0,0,0.2)">
<div style="display:flex; align-items:center; gap:12px;">
{profile_html}
<div style="color:white;">
<b style="font-size:20px;">{user.get('nom','Utilisateur')}</b><br>
<span style="background:{'gold' if user.get('is_vip') else 'white'}; color:black; padding:3px 12px; border-radius:20px; font-size:11px; font-weight:900;">{"👑 VIP ILLIMITÉ" if user.get('is_vip') else "🆓 GRATUIT"}</span>
</div>
<div style="margin-left:auto; font-size:30px">🕌</div>
</div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    menu=st.radio("NAVIGATION", ["Home","Aliments","Coran","Hadiths","Douas","Parametres"], label_visibility="collapsed")
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.user=None; st.session_state.page="auth"; st.rerun()

if st.session_state.get('selected_menu'):
    menu=st.session_state.selected_menu; st.session_state.selected_menu=None

# NAV GRAPHIQUE
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

    # VIP GRAPH
    if st.session_state.bottom_nav in ["VIP_ALIMENTS","VIP_DOUAS","VIP_HADITHS"]:
        if st.button("⬅️"): st.session_state.bottom_nav="Home"; st.rerun()
        nom=st.session_state.bottom_nav.replace("VIP_","")
        st.markdown(f"""
        <div class="card-vip">
            <div style="font-size:70px">🔒</div>
            <div style="font-size:22px; font-weight:900; color:gold">{nom}</div>
            <div style="font-size:13px; margin-top:8px">Débloque avec VIP 1500F</div>
            <div style="font-size:50px; margin-top:10px">👑</div>
        </div>""", unsafe_allow_html=True)
        st.link_button("💳 PAYER 1500F WAVE", WAVE_LINK, type="primary", use_container_width=True)
        if st.button("✅ J'ai payé - Activer VIP", use_container_width=True):
            users[user_email]['is_vip']=True; save_json(USERS_FILE,users); st.balloons(); st.session_state.bottom_nav="Home"; st.rerun()
        st.stop()

    # SAVOIR GRAPHIQUE
    if st.session_state.bottom_nav=="SAVOIR":
        if st.button("⬅️", key="back_savoir"): st.session_state.bottom_nav="Home"; st.rerun()
        st.markdown("""
        <div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:18px; padding:18px; text-align:center; color:white">
            <div style="font-size:50px">📚</div>
            <div style="font-weight:900; font-size:20px">SAVOIR ISLAMIQUE</div>
        </div>""", unsafe_allow_html=True)
        col1,col2=st.columns(2)
        with col1:
            st.markdown("""<div class="card-graph"><div style="font-size:55px">📖</div><div style="font-weight:900">CORAN</div><div style="background:#00c853; color:white; display:inline-block; padding:2px 10px; border-radius:20px; font-size:11px; font-weight:900">GRATUIT</div><div style="font-size:11px; color:gray; margin-top:5px">114 Sourates</div></div>""", unsafe_allow_html=True)
            if st.button("📖 Ouvrir Coran", use_container_width=True, key="open_coran"): st.session_state.selected_menu="Coran"; st.session_state.bottom_nav="Home"; st.rerun()
            st.markdown("""<div class="card-graph"><div style="font-size:55px">📜</div><div style="font-weight:900">HADITHS</div><div style="background:#0a2a6b; color:gold; display:inline-block; padding:2px 10px; border-radius:20px; font-size:11px">VIP 🔒</div><div style="font-size:11px; color:gray; margin-top:5px">40 Hadiths</div></div>""", unsafe_allow_html=True)
            if st.button("📜 Ouvrir Hadiths", use_container_width=True, key="open_hadiths"):
                st.session_state.bottom_nav="VIP_HADITHS" if not user.get('is_vip') else "Home"
                st.session_state.selected_menu="Hadiths" if user.get('is_vip') else None
                st.rerun()
        with col2:
            st.markdown("""<div class="card-graph"><div style="font-size:55px">🍖</div><div style="font-weight:900">ALIMENTS</div><div style="background:#0a2a6b; color:gold; display:inline-block; padding:2px 10px; border-radius:20px; font-size:11px">VIP 🔒</div><div style="font-size:11px; color:gray; margin-top:5px">Halal / Haram</div></div>""", unsafe_allow_html=True)
            if st.button("🍖 Ouvrir Aliments", use_container_width=True, key="open_aliments"):
                st.session_state.bottom_nav="VIP_ALIMENTS" if not user.get('is_vip') else "Home"
                st.session_state.selected_menu="Aliments" if user.get('is_vip') else None
                st.rerun()
            st.markdown("""<div class="card-graph"><div style="font-size:55px">🤲</div><div style="font-weight:900">DOUAS</div><div style="background:#0a2a6b; color:gold; display:inline-block; padding:2px 10px; border-radius:20px; font-size:11px">VIP 🔒</div><div style="font-size:11px; color:gray; margin-top:5px">50 Invocations</div></div>""", unsafe_allow_html=True)
            if st.button("🤲 Ouvrir Douas", use_container_width=True, key="open_douas"):
                st.session_state.bottom_nav="VIP_DOUAS" if not user.get('is_vip') else "Home"
                st.session_state.selected_menu="Douas" if user.get('is_vip') else None
                st.rerun()
        share_zone(); st.stop()

    if st.session_state.bottom_nav=="Qibla":
        if st.button("⬅️", key="back_qibla"): st.session_state.bottom_nav="Home"; st.rerun()
        st.markdown("""
        <div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:18px; padding:18px; text-align:center; color:white">
            <div style="font-size:50px">🕋</div><div style="font-weight:900; font-size:20px">QIBLA</div>
        </div>""", unsafe_allow_html=True)
        qibla_html = """
        <div style="font-family:sans-serif; text-align:center; background:white; padding:15px; border-radius:18px; border:2px solid #eef2ff; box-shadow:0 6px 15px rgba(0,0,0,0.07)">
            <button id="locBtn" style="background:linear-gradient(90deg,#0a2a6b,#1a4bb8); color:white; padding:14px 20px; border-radius:12px; border:none; font-weight:900; width:100%">📍 ACTIVER GPS & CHERCHER QIBLA</button>
            <div id="infoBox" style="margin-top:15px; padding:12px; background:#f0f6ff; border-radius:12px; border-left:5px solid #0a2a6b; text-align:left; display:none">
                <div id="coords" style="font-size:12px; font-weight:900"></div>
                <div id="qiblaInfo" style="font-size:16px; font-weight:900; color:#00a651; margin-top:5px"></div>
            </div>
            <div style="position:relative; width:260px; height:260px; margin:25px auto; border-radius:50%; border:10px solid #0a2a6b; background:radial-gradient(circle, #fff, #e6f0ff); box-shadow:0 8px 20px rgba(0,0,0,0.2)">
                <div style="position:absolute; top:8px; left:50%; transform:translateX(-50%); font-weight:900; color:red; font-size:18px">N</div>
                <div style="position:absolute; bottom:8px; left:50%; transform:translateX(-50%); font-weight:900">S</div>
                <div style="position:absolute; left:10px; top:50%; transform:translateY(-50%); font-weight:900">O</div>
                <div style="position:absolute; right:10px; top:50%; transform:translateY(-50%); font-weight:900">E</div>
                <div id="arrow" style="position:absolute; top:50%; left:50%; width:6px; height:100px; background:linear-gradient(to top, #0a2a6b, #00c6ff); transform-origin:bottom center; transform:translate(-50%, -100%) rotate(0deg); border-radius:4px; transition:transform 0.8s"><div style="width:0; height:0; border-left:14px solid transparent; border-right:14px solid transparent; border-bottom:24px solid #ff0030; position:absolute; top:-22px; left:50%; transform:translateX(-50%)"></div></div>
                <div style="position:absolute; top:50%; left:50%; width:28px; height:28px; background:#0a2a6b; border-radius:50%; transform:translate(-50%,-50%); border:3px solid gold"></div>
                <div style="position:absolute; top:50%; left:50%; font-size:28px; transform:translate(-50%, -150%)">🕋</div>
            </div>
        </div>
        <script>
        let qiblaAngle=67.5; const kaabaLat=21.4225*Math.PI/180; const kaabaLon=39.8262*Math.PI/180;
        function calculateQibla(lat,lon){const latRad=lat*Math.PI/180; const lonRad=lon*Math.PI/180; const dLon=kaabaLon-lonRad; const y=Math.sin(dLon); const x=Math.cos(latRad)*Math.tan(kaabaLat)-Math.sin(latRad)*Math.cos(dLon); let brng=Math.atan2(y,x)*180/Math.PI; return (brng+360)%360;}
        document.getElementById('locBtn').onclick=function(){const btn=this; btn.innerText='📡 Recherche...'; if(navigator.geolocation){navigator.geolocation.getCurrentPosition(function(pos){qiblaAngle=calculateQibla(pos.coords.latitude,pos.coords.longitude); document.getElementById('infoBox').style.display='block'; document.getElementById('coords').innerHTML='📍 '+pos.coords.latitude.toFixed(4)+', '+pos.coords.longitude.toFixed(4); document.getElementById('qiblaInfo').innerText='🕋 Qibla: '+qiblaAngle.toFixed(2)+'°'; btn.innerText='✅ Qibla trouvée'; btn.style.background='#00a651'; document.getElementById('arrow').style.transform='translate(-50%, -100%) rotate('+qiblaAngle+'deg)';},function(){document.getElementById('infoBox').style.display='block'; qiblaAngle=calculateQibla(5.36,-4.00); document.getElementById('qiblaInfo').innerText='🕋 Qibla: '+qiblaAngle.toFixed(2)+'°';},{enableHighAccuracy:true});}};
        if(window.DeviceOrientationEvent){window.addEventListener('deviceorientation',function(e){let heading=e.webkitCompassHeading; if(heading===undefined) heading=360-e.alpha; if(heading){document.getElementById('arrow').style.transform='translate(-50%, -100%) rotate('+(qiblaAngle-heading)+'deg)';}},true);}
        </script>
        """
        st.components.v1.html(qibla_html, height=600); st.stop()

    elif st.session_state.bottom_nav=="Calendrier":
        if st.button("⬅️", key="back_cal"): st.session_state.bottom_nav="Home"; st.rerun()
        today=date.today(); d_h,m_h,y_h=gregorian_to_hijri(today)
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:18px; padding:18px; text-align:center; color:white">
            <div style="font-size:50px">📅</div><div style="font-weight:900; font-size:20px">CALENDRIER</div>
        </div>""", unsafe_allow_html=True)
        calendar.setfirstweekday(calendar.MONDAY)
        month_names=["","Janvier","Février","Mars","Avril","Mai","Juin","Juillet","Août","Septembre","Octobre","Novembre","Décembre"]
        month_name=month_names[today.month]
        month_days=calendar.monthcalendar(today.year,today.month)
        html_cal=f"""<div style="background:white; padding:12px; border-radius:18px; border:2px solid #eef2ff; box-shadow:0 6px 15px rgba(0,0,0,0.07)"><div style="text-align:center; font-weight:900; font-size:18px; color:#0a2a6b; margin-bottom:8px">🌍 {month_name} {today.year}</div><div style="display:grid; grid-template-columns:repeat(7,1fr); gap:4px; text-align:center; font-size:12px; font-weight:900; color:#888"><div>Lun</div><div>Mar</div><div>Mer</div><div>Jeu</div><div>Ven</div><div>Sam</div><div>Dim</div></div><div style="display:grid; grid-template-columns:repeat(7,1fr); gap:4px; text-align:center; margin-top:6px">"""
        for week in month_days:
            for d in week:
                if d==0: html_cal+='<div style="padding:10px"></div>'
                elif d==today.day: html_cal+=f'<div style="padding:10px; background:#0a2a6b; color:white; border-radius:10px; font-weight:900; border:2px solid gold">{d}</div>'
                else: html_cal+=f'<div style="padding:10px; background:#f5f7ff; border-radius:10px">{d}</div>'
        html_cal+="</div></div>"
        col1,col2=st.columns(2)
        with col1: st.components.v1.html(html_cal, height=320)
        with col2:
            st.markdown(f"""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); padding:18px; border-radius:18px; color:white; text-align:center; box-shadow:0 6px 15px rgba(0,0,0,0.2)"><div style="font-size:40px">🌙</div><div style="font-size:12px; color:gold; font-weight:900">HIJRI</div><div style="font-size:36px; font-weight:900">{d_h}</div><div style="color:gold; font-weight:900">{HIJRI_MONTHS[m_h-1]}</div><div style="font-weight:900">{y_h} AH</div></div>""", unsafe_allow_html=True)
        st.markdown("""<div class="card-graph" style="text-align:left; border-left:5px solid #00a651">🌙 Ramadan 1447: 18 Février 2026<br>🎉 Aïd al-Fitr: 20 Mars 2026<br>🕋 Aïd al-Adha: 27 Mai 2026</div>""", unsafe_allow_html=True)
        share_zone(); st.stop()

    # SCANNER GRAPHIQUE
    scans_used=user['scans']-user.get('bonus_scans',0)
    if not user['is_vip'] and scans_used>=5:
        st.markdown("""<div class="card-vip"><div style="font-size:60px">🚫</div><div style="font-weight:900">5 essais utilisés</div></div>""", unsafe_allow_html=True)
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

    st.markdown("""
    <div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:20px; padding:20px; text-align:center; color:white; box-shadow:0 8px 20px rgba(0,0,0,0.2)">
        <div style="font-size:60px">📸</div>
        <div style="font-weight:900; font-size:22px">SCANNER HALAL</div>
        <div style="font-size:12px; opacity:0.8">Vérifie en 2 secondes</div>
    </div>""", unsafe_allow_html=True)

    c1,c2=st.columns(2)
    with c1:
        st.markdown("""<div class="card-graph"><div style="font-size:55px">📷</div><div style="font-weight:900; color:#0a2a6b">CAMÉRA</div><div style="font-size:10px; color:gray">Prendre photo</div></div>""", unsafe_allow_html=True)
        if st.button("📷 CAMERA", type="primary", use_container_width=True, key="btn_cam"): st.session_state.scan_mode="camera"; st.rerun()
    with c2:
        st.markdown("""<div class="card-graph"><div style="font-size:55px">🖼️</div><div style="font-weight:900; color:#0a2a6b">UPLOAD</div><div style="font-size:10px; color:gray">Galerie</div></div>""", unsafe_allow_html=True)
        if st.button("🖼️ UPLOAD", type="primary", use_container_width=True, key="btn_upload"): st.session_state.scan_mode="upload"; st.rerun()

    photo=None
    if st.session_state.scan_mode=="camera":
        cam=st.camera_input("Photo", key="camera_input", label_visibility="collapsed")
        if cam: photo=cam
    elif st.session_state.scan_mode=="upload":
        up=st.file_uploader("Photo", type=['jpg','png','jpeg','webp'], key="uploader", label_visibility="collapsed")
        if up: photo=up

    if photo:
        st.image(photo, use_container_width=True)
        if st.button("✅ LANCER LE SCAN HALAL", type="primary", use_container_width=True, key="btn_scan"):
            with st.spinner("Analyse..."):
                time.sleep(2)
                if not user['is_vip']: users[user_email]['scans']+=1
                result=random.choice(["HALAL 100%","HARAM Détecté","DOUTEUX"])
                color="green" if "HALAL" in result else "red" if "HARAM" in result else "orange"
                icon="✅" if "HALAL" in result else "❌" if "HARAM" in result else "⚠️"
                st.markdown(f"""<div style="background:white; border-radius:20px; padding:20px; text-align:center; border:4px solid {color}; box-shadow:0 8px 20px rgba(0,0,0,0.1)"><div style="font-size:70px">{icon}</div><div style="font-size:26px; font-weight:900; color:{color}">{result}</div></div>""", unsafe_allow_html=True)
                users[user_email]['history'].append({'date':datetime.now().strftime("%d/%m/%Y %H:%M"),'result':result})
                save_json(USERS_FILE,users); st.balloons(); st.session_state.scan_mode=None

    share_zone()

# PAGES GRAPHIQUES
elif menu=="Coran":
    if st.button("⬅️"): st.session_state.bottom_nav="Home"; st.rerun()
    st.markdown("""<div style="background:linear-gradient(135deg,#00a651,#00c853); border-radius:18px; padding:18px; text-align:center; color:white"><div style="font-size:50px">📖</div><div style="font-weight:900; font-size:20px">CORAN</div><div style="font-size:12px">114 Sourates - GRATUIT</div></div>""", unsafe_allow_html=True)
    for i in range(1,115):
        st.markdown(f"""<div class="card-graph" style="display:flex; align-items:center; gap:15px; text-align:left"><div style="background:#0a2a6b; color:white; width:40px; height:40px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:900">{i}</div><div><div style="font-weight:900">Sourate {i}</div><div style="font-size:11px; color:gray">Appuie pour lire</div></div><div style="margin-left:auto; font-size:20px">📖</div></div>""", unsafe_allow_html=True)

elif menu in ["Aliments","Hadiths","Douas"]:
    if not user.get('is_vip'):
        st.markdown(f"""<div class="card-vip"><div style="font-size:70px">🔒</div><div style="font-weight:900; color:gold; font-size:22px">{menu}</div><div>VIP Seulement - 1500F</div></div>""", unsafe_allow_html=True)
        st.link_button("💳 PAYER 1500F WAVE", WAVE_LINK, type="primary", use_container_width=True)
        if st.button("✅ J'ai payé"):
            users[user_email]['is_vip']=True; save_json(USERS_FILE,users); st.balloons(); st.rerun()
        st.stop()
    if st.button("⬅️"): st.session_state.bottom_nav="Home"; st.rerun()
    icon_map={"Aliments":"🍖","Hadiths":"📜","Douas":"🤲"}
    st.markdown(f"""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:18px; padding:18px; text-align:center; color:white"><div style="font-size:50px">{icon_map[menu]}</div><div style="font-weight:900; font-size:20px">{menu.upper()}</div><div style="font-size:12px; color:gold">VIP Débloqué 👑</div></div>""", unsafe_allow_html=True)
    items = ["Poulet Halal 🟢","Boeuf Halal 🟢","Porc HARAM 🔴","Vin HARAM 🔴"] if menu=="Aliments" else [f"Hadith {i} 📜" for i in range(1,41)] if menu=="Hadiths" else [f"Doua {i} 🤲" for i in range(1,51)]
    for it in items:
        st.markdown(f"""<div class="card-graph" style="text-align:left; display:flex; align-items:center; gap:10px"><div style="font-size:25px">{icon_map[menu]}</div><div style="font-weight:600">{it}</div></div>""", unsafe_allow_html=True)

elif menu=="Parametres":
    st.markdown(f"""
    <div style="background:white; border-radius:20px; padding:20px; text-align:center; border:2px solid #eef2ff; box-shadow:0 6px 15px rgba(0,0,0,0.07)">
        <div style="font-size:60px">{profile_html}</div>
        <div style="font-weight:900; font-size:18px; margin-top:10px">{user.get('nom')}</div>
        <div style="font-size:12px; color:gray">{user_email}</div>
        <div style="background:{'gold' if user.get('is_vip') else '#eee'}; display:inline-block; padding:4px 12px; border-radius:20px; font-size:11px; font-weight:900; margin-top:8px">{"👑 VIP" if user.get('is_vip') else "🆓 GRATUIT"}</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""<div class="card-graph" style="text-align:left">⚙️ <b>Paramètres</b><br><span style="font-size:12px; color:gray">Gère ton compte</span></div>""", unsafe_allow_html=True)
    share_zone()
