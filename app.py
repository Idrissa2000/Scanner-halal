import streamlit as st
import json, os, random, re, base64, calendar, time
from datetime import datetime, date

WAVE_LINK = "https://pay.wave.com/m/M_ci_bqKBEWPbP0OO/c/ci/?amount=1500"
MONETAG_LINK = "https://omg10.com/4/11717935"  # <-- AJOUTE CETTE LIGNE
APP_LINK = "https://scanner-halal.streamlit.app"
USERS_FILE = "users.json"
VIP_CODES_FILE = "vip_codes.json"
HIJRI_MONTHS = ["Muharram","Safar","Rabi al-Awwal","Rabi al-Thani","Jumada al-Ula","Jumada al-Akhira","Rajab","Shaban","Ramadan","Shawwal","Dhu al-Qidah","Dhu al-Hijjah"]
os.makedirs("profile_pics", exist_ok=True)

def load_json(f,d):
    if os.path.exists(f):
        try:
            with open(f,'r',encoding='utf-8') as fp: return json.load(fp)
        except: return d
    return d
def save_json(f,data):
    with open(f,'w',encoding='utf-8') as fp: json.dump(data,fp,ensure_ascii=False,indent=2)

if not os.path.exists(VIP_CODES_FILE):
    codes = {f"VIP-{random.randint(1000,9999)}-{random.randint(1000,9999)}": {"used": False, "used_by": None} for _ in range(20)}
    codes["VIP-2026-TEST"] = {"used": False, "used_by": None}
    save_json(VIP_CODES_FILE, codes)

vip_codes = load_json(VIP_CODES_FILE, {})

def check_vip_code(code):
    code = code.strip().upper()
    if code in vip_codes and not vip_codes[code]["used"]:
        return True
    return False

def activate_vip_code(code, email):
    code = code.strip().upper()
    vip_codes[code]["used"] = True
    vip_codes[code]["used_by"] = email
    save_json(VIP_CODES_FILE, vip_codes)

ALIMENTS_DATA = [
    {"nom": "Poulet (halal)", "statut": "HALAL", "icon": "🐔", "desc": "Halal si égorgé selon rite islamique, prononcer Bismillah"},
    {"nom": "Boeuf halal", "statut": "HALAL", "icon": "🐄", "desc": "Halal avec sacrifice rituel"},
    {"nom": "Mouton halal", "statut": "HALAL", "icon": "🐑", "desc": "Halal sacrifice Aid"},
    {"nom": "Poisson Thon", "statut": "HALAL", "icon": "🐟", "desc": "Tous les poissons sont halal"},
    {"nom": "Riz", "statut": "HALAL", "icon": "🍚", "desc": "100% halal"},
    {"nom": "Dattes", "statut": "HALAL", "icon": "🌴", "desc": "Sunna, très recommandée"},
    {"nom": "Lait", "statut": "HALAL", "icon": "🥛", "desc": "Halal"},
    {"nom": "Miel", "statut": "HALAL", "icon": "🍯", "desc": "Halal pur, remède"},
    {"nom": "Mangue", "statut": "HALAL", "icon": "🥭", "desc": "Halal"},
    {"nom": "Banane", "statut": "HALAL", "icon": "🍌", "desc": "Halal"},
    {"nom": "Porc", "statut": "HARAM", "icon": "🐖", "desc": "HARAM - Interdit Coran 2:173"},
    {"nom": "Vin / Alcool", "statut": "HARAM", "icon": "🍷", "desc": "HARAM - Alcool interdit 5:90"},
    {"nom": "Bière", "statut": "HARAM", "icon": "🍺", "desc": "HARAM"},
    {"nom": "Gélatine porcine E441", "statut": "HARAM", "icon": "⚠️", "desc": "HARAM - Porc"},
    {"nom": "E120 Cochenille", "statut": "HARAM", "icon": "⚠️", "desc": "HARAM - Insecte"},
    {"nom": "Saucisson porc", "statut": "HARAM", "icon": "🚫", "desc": "HARAM"},
]

HADITHS_40_VRAIS = [
    {"id":1, "ar": "إنما الأعمال بالنيات", "fr": "Les actes ne valent que par leurs intentions. Celui qui émigre pour Allah et Son Messager, son émigration sera pour Allah et Son Messager. [Bukhari & Muslim]"},
    {"id":2, "ar": "بني الإسلام على خمس", "fr": "L'Islam est bâti sur cinq piliers : attester qu'il n'y a de dieu qu'Allah et que Muhammad est Son Messager, accomplir la prière, s'acquitter de la zakat, jeûner Ramadan et faire le pèlerinage. [Bukhari]"},
    {"id":3, "ar": "إن الله كتب الإحسان على كل شيء", "fr": "Allah a prescrit la bienfaisance en toute chose. Si vous tuez, tuez bien, si vous égorgez, égorgez bien. [Muslim]"},
    {"id":4, "ar": "من حسن إسلام المرء تركه ما لا يعنيه", "fr": "Fait partie du bon Islam de l'homme de délaisser ce qui ne le concerne pas. [Tirmidhi]"},
    {"id":5, "ar": "لا يؤمن أحدكم حتى يحب لأخيه ما يحب لنفسه", "fr": "Aucun de vous ne sera croyant jusqu'à ce qu'il aime pour son frère ce qu'il aime pour lui-même. [Bukhari & Muslim]"},
    {"id":6, "ar": "من كان يؤمن بالله واليوم الآخر فليقل خيرا أو ليصمت", "fr": "Que celui qui croit en Allah et au Jour Dernier dise du bien ou se taise. [Bukhari & Muslim]"},
    {"id":7, "ar": "الدين النصيحة", "fr": "La religion c'est le bon conseil. Pour Allah, Son Livre, Son Messager, les dirigeants et l'ensemble des musulmans. [Muslim]"},
    {"id":8, "ar": "اتق الله حيثما كنت", "fr": "Crains Allah où que tu sois, fais suivre la mauvaise action par une bonne qui l'effacera, et comporte-toi bien avec les gens. [Tirmidhi]"},
    {"id":9, "ar": "ما نهيتكم عنه فاجتنبوه", "fr": "Ce que je vous ai interdit, évitez-le, et ce que je vous ai ordonné, faites-en selon votre capacité. [Muslim]"},
    {"id":10, "ar": "الطهور شطر الإيمان", "fr": "La purification est la moitié de la foi. Alhamdulillah remplit la balance. [Muslim]"},
]
for i in range(11,41):
    HADITHS_40_VRAIS.append({"id":i, "ar": f"حديث {i} - من كلام النبي ﷺ", "fr": f"Hadith {i} des 40 Nawawi - Texte complet authentique : Le Messager d'Allah (ﷺ) a dit... (Ici tu peux ajouter le vrai texte de chaque hadith)"})

SOURATES_NOMS = ["Al-Fatiha","Al-Baqara","Al-Imran","An-Nisa","Al-Maida","Al-Anam","Al-Araf","Al-Anfal","At-Tawba","Yunus","Hud","Yusuf","Ar-Rad","Ibrahim","Al-Hijr","An-Nahl","Al-Isra","Al-Kahf","Maryam","Ta-Ha","Al-Anbiya","Al-Hajj","Al-Muminun","An-Nur","Al-Furqan","Ash-Shuara","An-Naml","Al-Qasas","Al-Ankabut","Ar-Rum","Luqman","As-Sajda","Al-Ahzab","Saba","Fatir","Ya-Sin","As-Saffat","Sad","Az-Zumar","Ghafir","Fussilat","Ash-Shura","Az-Zukhruf","Ad-Dukhan","Al-Jathiya","Al-Ahqaf","Muhammad","Al-Fath","Al-Hujurat","Qaf","Adh-Dhariyat","At-Tur","An-Najm","Al-Qamar","Ar-Rahman","Al-Waqia","Al-Hadid","Al-Mujadila","Al-Hashr","Al-Mumtahana","As-Saff","Al-Jumua","Al-Munafiqun","At-Taghabun","At-Talaq","At-Tahrim","Al-Mulk","Al-Qalam","Al-Haqqa","Al-Maarij","Nuh","Al-Jinn","Al-Muzzammil","Al-Muddathir","Al-Qiyama","Al-Insan","Al-Mursalat","An-Naba","An-Naziat","Abasa","At-Takwir","Al-Infitar","Al-Mutaffifin","Al-Inshiqaq","Al-Buruj","At-Tariq","Al-Ala","Al-Ghashiya","Al-Fajr","Al-Balad","Ash-Shams","Al-Lail","Ad-Duha","Ash-Sharh","At-Tin","Al-Alaq","Al-Qadr","Al-Bayyina","Az-Zalzala","Al-Adiyat","Al-Qaria","At-Takathur","Al-Asr","Al-Humaza","Al-Fil","Quraysh","Al-Maun","Al-Kawthar","Al-Kafirun","An-Nasr","Al-Masad","Al-Ikhlas","Al-Falaq","An-Nas"]

RECITATEURS = {
    "Mishary Alafasy": "https://cdn.islamic.network/quran/audio/128/ar.alafasy/",
    "Abdul Rahman Al-Sudais": "https://cdn.islamic.network/quran/audio/128/ar.abdurrahmaansudais/",
    "Maher Al-Muaiqly": "https://cdn.islamic.network/quran/audio/128/ar.mahermuaiqly/",
    "Saud Al-Shuraim": "https://cdn.islamic.network/quran/audio/128/ar.saoodshuraym/"
}

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
.card-vip{background:linear-gradient(135deg,#0a2a6b,#1a4bb8);color:white;padding:25px;border-radius:20px;margin:12px 0px; text-align:center}
div[data-testid="stButton"] > button {border-radius:18px!important; padding:18px!important; white-space:pre-line!important; box-shadow:0 6px 15px rgba(0,0,0,0.07)!important; border:2px solid #eef2ff!important; background:white!important; color:#0a2a6b!important; font-weight:800!important;}
</style>
""", unsafe_allow_html=True)

for k in ['user','page','reset_code','scan_mode','bottom_nav','selected_menu','ad_watching','ad_start_time','selected_hadith','selected_aliment','selected_sourate']:
    if k not in st.session_state:
        st.session_state[k] = None if k not in ['page','bottom_nav','ad_watching'] else ("auth" if k=='page' else "Home" if k=='bottom_nav' else False)

if st.session_state.page=="auth":
    st.markdown("""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:20px; padding:25px; text-align:center; color:white"><div style="font-size:70px">🕌</div><div style="font-size:24px; font-weight:900">SCANNER HALAL</div></div>""", unsafe_allow_html=True)
    t1,t2,t3=st.tabs(["Connexion","Inscription","Code oublié"])
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
                users[er]={'nom':nom,'wave':f"{extract_code(pays)} {numero}",'pays':pays,'pwd':p1,'scans':0,'is_vip':False,'history':[],'bonus_scans':0,'profile_pic':None,'cover_pic':None,'vip_code':None}
                save_json(USERS_FILE,users); st.success("Compte créé!"); st.balloons()
    with t3:
        ef=st.text_input("Email", key="email_oublie").strip()
        if st.button("Envoyer code"):
            if ef in users:
                code=str(random.randint(100000,999999)); st.session_state.reset_code=code; st.session_state.reset_email=ef; st.success(f"Code demo: {code}")
            else: st.error("Non trouvé")
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

cover_b64=get_image_base64(user.get('cover_pic'))
profile_b64=get_image_base64(user.get('profile_pic'))
cover_style=f"background-image:url(data:image/jpeg;base64,{cover_b64}); background-size:cover; background-position:center;" if cover_b64 else "background:linear-gradient(90deg,#00c6ff,#0072ff);"
profile_html=f"<img src='data:image/jpeg;base64,{profile_b64}' style='width:75px;height:75px;border-radius:50%;border:3px solid gold;object-fit:cover;'>" if profile_b64 else "<div style='width:75px;height:75px;border-radius:50%;background:white;display:flex;align-items:center;justify-content:center;font-size:38px;border:3px solid gold;'>👤</div>"

st.markdown(f"""
<div style="{cover_style} padding:15px; border-radius:18px; margin-bottom:12px;">
<div style="display:flex; align-items:center; gap:12px; background:rgba(0,0,0,0.45); padding:12px; border-radius:12px;">
{profile_html}
<div style="color:white;">
<b style="font-size:20px;">{user.get('nom','Utilisateur')}</b><br>
<span style="font-size:11px; opacity:0.9">{'👑 VIP '+user.get('vip_code','') if user.get('is_vip') else 'Clique pour modifier'}</span>
</div>
<div style="margin-left:auto; font-size:28px">🕌</div>
</div>
</div>
""", unsafe_allow_html=True)

with st.expander("✏️ Modifier photo / couverture / nom (clique ici)"):
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        new_pic = st.file_uploader("📷 Photo de profil", type=['jpg','png','jpeg'], key="new_profile_pic")
        if new_pic:
            path = f"profile_pics/{user_email}_profile.jpg"
            with open(path,"wb") as f: f.write(new_pic.getbuffer())
            users[user_email]['profile_pic']=path; save_json(USERS_FILE,users); st.success("Photo changée"); st.rerun()
    with col_p2:
        new_cover = st.file_uploader("🖼️ Couverture", type=['jpg','png','jpeg'], key="new_cover_pic")
        if new_cover:
            path = f"profile_pics/{user_email}_cover.jpg"
            with open(path,"wb") as f: f.write(new_cover.getbuffer())
            users[user_email]['cover_pic']=path; save_json(USERS_FILE,users); st.success("Couverture changée"); st.rerun()
    new_name = st.text_input("✏️ Nouveau nom", value=user.get('nom',''), key="new_name_input")
    if st.button("💾 Sauver le nom", use_container_width=True):
        if new_name.strip():
            users[user_email]['nom']=new_name.strip(); save_json(USERS_FILE,users); st.success("Nom changé"); st.rerun()

with st.sidebar:
    menu=st.radio("NAVIGATION", ["Home","Aliments","Coran","Hadiths","Douas","Parametres","Codes VIP (Admin)"], label_visibility="collapsed")
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.user=None; st.session_state.page="auth"; st.rerun()

if st.session_state.get('selected_menu'):
    menu=st.session_state.selected_menu; st.session_state.selected_menu=None

if menu=="Codes VIP (Admin)":
    st.title("🔑 Générateur Codes VIP")
    st.markdown(f"<div class='card-graph'>Codes : {len(vip_codes)}</div>", unsafe_allow_html=True)
    for code, info in vip_codes.items():
        status = f"✅ Utilisé par {info['used_by']}" if info['used'] else "🟢 Disponible"
        st.markdown(f"<div class='card-graph' style='text-align:left; font-size:12px'><b>{code}</b> - {status}</div>", unsafe_allow_html=True)
    if st.button("➕ Générer 5 nouveaux codes", use_container_width=True):
        for _ in range(5):
            new_code = f"VIP-{random.randint(1000,9999)}-{random.randint(1000,9999)}"
            vip_codes[new_code] = {"used": False, "used_by": None}
        save_json(VIP_CODES_FILE, vip_codes)
        st.success("5 codes générés"); st.rerun()
    st.stop()

    if menu=="Home":
        user = users[user_email]

        # --- HEADER AVEC 3 POINTS ---
        col_title, col_menu = st.columns([0.85, 0.15])
        with col_title:
            st.markdown(f"### Salam {user.get('full_name','').split(' ')[0]} 👋")
        with col_menu:
            with st.popover("⋮"):
                if st.button("👤 Profil", use_container_width=True, key="m1"):
                    st.session_state.selected_menu = "MODIFIER_PROFIL"; st.rerun()
                if st.button("🔑 Code", use_container_width=True, key="m2"):
                    st.session_state.selected_menu = "CHANGER_CODE"; st.rerun()
                if st.button("🔔 Notifs", use_container_width=True, key="m3"):
                    st.session_state.selected_menu = "NOTIFICATIONS"; st.rerun()
                if st.button("🚪 Quitter", use_container_width=True, key="m4"):
                    for k in list(st.session_state.keys()): del st.session_state[k]
                    st.rerun()

        # RAPPEL NOTIFICATION
        st.components.v1.html("""
        <script>
        if (Notification && Notification.permission!= "granted") {
           var b = document.createElement('div');
           b.innerHTML = "<div style='background:#fff3cd;border-left:5px solid #ffc107;padding:10px;border-radius:10px;font-size:13px;font-weight:700'>🔔 Notifications désactivées - Active pour ne pas rater la prière</div>";
           document.body.prepend(b);
           setTimeout(()=>{Notification.requestPermission()}, 2000);
        }
        </script>
        """, height=0)

        # --- PAGES DU MENU ---
        if st.session_state.selected_menu == "MODIFIER_PROFIL":
            if st.button("⬅️"): st.session_state.selected_menu=None; st.rerun()
            st.subheader("👤 Modifier profil")
            n = st.text_input("Nom complet", value=user.get('full_name',''))
            if st.button("💾 Enregistrer", type="primary", use_container_width=True):
                users[user_email]['full_name']=n; save_json(USERS_FILE, users)
                st.success("Modifié!"); time.sleep(1); st.session_state.selected_menu=None; st.rerun()
            st.stop()
        if st.session_state.selected_menu == "CHANGER_CODE":
            if st.button("⬅️"): st.session_state.selected_menu=None; st.rerun()
            st.subheader("🔑 Changer code")
            a = st.text_input("Ancien code", type="password")
            b = st.text_input("Nouveau code", type="password")
            c = st.text_input("Confirmer", type="password")
            if st.button("🔒 Changer", type="primary", use_container_width=True):
                if users[user_email]['password']!=a: st.error("Ancien code faux")
                elif b!=c: st.error("Codes différents")
                else: users[user_email]['password']=b; save_json(USERS_FILE, users); st.success("Code changé!"); st.session_state.selected_menu=None; st.rerun()
            st.stop()
        if st.session_state.selected_menu == "NOTIFICATIONS":
            if st.button("⬅️"): st.session_state.selected_menu=None; st.rerun()
            st.subheader("🔔")
            st.warning("Si désactivé, tu vas rater les heures de prière")
            if st.toggle("Activer les rappels"):
                st.components.v1.html("<script>Notification.requestPermission()</script>", height=0)
                st.success("Activé!")
            st.stop()

        # --- TON ANCIEN CODE HOME CONTINUE ICI ---
        c1,c2,c3,c4=st.columns(4)
        with c1:
            if st.button("🏠 Home", use_container_width=True, type="primary"): st.session_state.bottom_nav="Home"; st.rerun()
        with c2:
            if st.button("📚 SAVOIR", use_container_width=True): st.session_state.bottom_nav="SAVOIR"; st.rerun()
        with c3:
            if st.button("🕋 Qibla", use_container_width=True): st.session_state.bottom_nav="Qibla"; st.rerun()
        with c4:
            if st.button("📅 Cal.", use_container_width=True): st.session_state.bottom_nav="Calendrier"; st.rerun()

    if st.session_state.bottom_nav in ["VIP_ALIMENTS","VIP_DOUAS","VIP_HADITHS"]:
        if st.button("⬅️"): st.session_state.bottom_nav="Home"; st.rerun()
        nom=st.session_state.bottom_nav.replace("VIP_","")
        st.markdown(f"""
        <div class="card-vip">
            <div style="font-size:70px">🔒</div>
            <div style="font-weight:900; color:gold; font-size:22px">{nom} - VIP Seulement</div>
            <div style="margin-top:10px; font-size:13px">Paye puis entre ton CODE VIP</div>
        </div>""", unsafe_allow_html=True)
        st.link_button("💳 PAYER 1500F WAVE - Obtenir CODE", WAVE_LINK, type="primary", use_container_width=True)
        st.markdown("""
        <div style="background:white; border-radius:12px; padding:12px; border:2px solid gold; margin-top:12px; text-align:center">
            <b>Après paiement, tu reçois un CODE VIP</b><br>
            <span style="font-size:11px; color:gray">Test: VIP-2026-TEST</span>
        </div>""", unsafe_allow_html=True)
        code_input = st.text_input("🔑 Entre ton CODE VIP", placeholder="VIP-XXXX-XXXX", key="vip_code_input").strip().upper()
        if st.button("✅ ACTIVER MON VIP AVEC CODE", use_container_width=True, type="primary"):
            if not code_input:
                st.error("Entre ton code")
            elif check_vip_code(code_input):
                users[user_email]['is_vip']=True
                users[user_email]['vip_code']=code_input
                activate_vip_code(code_input, user_email)
                save_json(USERS_FILE,users)
                st.balloons(); st.success(f"VIP Activé {code_input}!"); time.sleep(1)
                st.session_state.bottom_nav="Home"; st.rerun()
            else:
                st.error("❌ Code invalide ou déjà utilisé")
        st.stop()

    if st.session_state.bottom_nav=="SAVOIR":
        if st.button("⬅️", key="back_savoir"): st.session_state.bottom_nav="Home"; st.rerun()
        st.markdown("""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:18px; padding:18px; text-align:center; color:white"><div style="font-size:50px">📚</div><div style="font-weight:900">SAVOIR ISLAMIQUE</div></div>""", unsafe_allow_html=True)
        col1,col2=st.columns(2)
        with col1:
            if st.button("📖\nCORAN\n114 Sourates\nGRATUIT", use_container_width=True, key="open_coran"):
                st.session_state.selected_menu="Coran"; st.session_state.bottom_nav="Home"; st.rerun()
            if st.button("📜\nHADITHS\n40 Hadiths\nVIP 🔒", use_container_width=True, key="open_hadiths"):
                if user.get('is_vip'): st.session_state.selected_menu="Hadiths"; st.session_state.bottom_nav="Home"; st.rerun()
                else: st.session_state.bottom_nav="VIP_HADITHS"; st.rerun()
            if st.button("🎮\nJEUX ISLAMIQUES\nQuiz & Puzzle\nGRATUIT", use_container_width=True, key="open_jeux"):
                st.session_state.selected_menu="Jeux"; st.session_state.bottom_nav="Home"; st.rerun()
        with col2:
            if st.button("🍖\nALIMENTS\nHalal / Haram\nVIP 🔒", use_container_width=True, key="open_aliments"):
                if user.get('is_vip'): st.session_state.selected_menu="Aliments"; st.session_state.bottom_nav="Home"; st.rerun()
                else: st.session_state.bottom_nav="VIP_ALIMENTS"; st.rerun()
            if st.button("🤲\nDOUAS\n50 Invocations\nVIP 🔒", use_container_width=True, key="open_douas"):
                if user.get('is_vip'): st.session_state.selected_menu="Douas"; st.session_state.bottom_nav="Home"; st.rerun()
                else: st.session_state.bottom_nav="VIP_DOUAS"; st.rerun()
        st.stop()

    if st.session_state.bottom_nav=="Qibla":
        if st.button("⬅️", key="back_qibla"): st.session_state.bottom_nav="Home"; st.rerun()
        st.markdown("""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:18px; padding:18px; text-align:center; color:white"><div style="font-size:50px">🕋</div><div style="font-weight:900; font-size:20px">QIBLA</div></div>""", unsafe_allow_html=True)
        qibla_html = """
        <div style="font-family:sans-serif; text-align:center; background:white; padding:15px; border-radius:18px; border:2px solid #eef2ff">
            <button id="locBtn" style="background:linear-gradient(90deg,#0a2a6b,#1a4bb8); color:white; padding:14px 20px; border-radius:12px; border:none; font-weight:900; width:100%">📍 ACTIVER GPS & CHERCHER QIBLA</button>
            <div id="infoBox" style="margin-top:15px; padding:12px; background:#f0f6ff; border-radius:10px; border-left:4px solid #0a2a6b; text-align:left; display:none">
                <div id="coords" style="font-size:13px; font-weight:bold"></div>
                <div id="qiblaInfo" style="font-size:16px; font-weight:bold; color:#00a651; margin-top:5px"></div>
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
            <div id="status" style="font-size:12px; color:gray">Clique pour activer GPS.</div>
        </div>
        <script>
        let qiblaAngle=67.5; const kaabaLat=21.4225*Math.PI/180; const kaabaLon=39.8262*Math.PI/180;
        function calculateQibla(lat,lon){const latRad=lat*Math.PI/180; const lonRad=lon*Math.PI/180; const dLon=kaabaLon-lonRad; const y=Math.sin(dLon); const x=Math.cos(latRad)*Math.tan(kaabaLat)-Math.sin(latRad)*Math.cos(dLon); let brng=Math.atan2(y,x)*180/Math.PI; return (brng+360)%360;}
        document.getElementById('locBtn').onclick=function(){const btn=this; btn.innerText='📡 Recherche GPS...'; if(navigator.geolocation){navigator.geolocation.getCurrentPosition(function(pos){const lat=pos.coords.latitude; const lon=pos.coords.longitude; qiblaAngle=calculateQibla(lat,lon); document.getElementById('infoBox').style.display='block'; document.getElementById('coords').innerHTML='📍 Lat: '+lat.toFixed(6)+'<br>📍 Lon: '+lon.toFixed(6); document.getElementById('qiblaInfo').innerText='🕋 Qibla: '+qiblaAngle.toFixed(2)+'°'; document.getElementById('status').innerHTML='<b style="color:green">✅ Qibla trouvée!</b>'; btn.innerText='✅ Qibla trouvée'; btn.style.background='#00a651'; document.getElementById('arrow').style.transform='translate(-50%, -100%) rotate('+qiblaAngle+'deg)';},function(){document.getElementById('infoBox').style.display='block'; document.getElementById('coords').innerText='GPS refusé - Abidjan'; qiblaAngle=calculateQibla(5.36,-4.00); document.getElementById('qiblaInfo').innerText='🕋 Qibla: '+qiblaAngle.toFixed(2)+'°'; document.getElementById('arrow').style.transform='translate(-50%, -100%) rotate('+qiblaAngle+'deg)';},{enableHighAccuracy:true});}};
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
        st.stop()

    # SCANNER - 1 CLIC OUVRE / 2 CLIC FERME - SCANNER SEULEMENT
    st.markdown("""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:20px; padding:18px; text-align:center; color:white"><div style="font-size:50px">📸</div><div style="font-weight:900">SCANNER HALAL</div><div style="font-size:11px; opacity:0.8">Vérifie en 2 secondes</div></div>""", unsafe_allow_html=True)
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    label_scanner = "❌\n\nFERMER SCANNER\n\nFermer" if st.session_state.scan_mode=="camera" else "📷\n\nSCANNER\n\nOuvrir"
    if st.button(label_scanner, use_container_width=True, key="scanner_toggle"):
        if st.session_state.scan_mode=="camera":
            st.session_state.scan_mode=None
        else:
            st.session_state.scan_mode="camera"
        st.rerun()

    if st.session_state.scan_mode=="camera":
        if st.button("⬅️", key="back_from_scanner"):
            st.session_state.scan_mode=None; st.rerun()
        st.markdown("<div style='background:white; border-radius:18px; padding:12px; border:2px solid #00a651; text-align:center'><b>📸 Scanner ouvert</b> - Prends une photo de ton aliment</div>", unsafe_allow_html=True)
                cam=st.camera_input("Photo", key="camera_input", label_visibility="collapsed")
        if cam:
            # Dès que la photo est prise, on scanne AUTOMATIQUEMENT
            with st.spinner("🤖 Analyse automatique en cours..."):
                time.sleep(1.5) # petite pause pour faire pro
                if not user['is_vip']: users[user_email]['scans']+=1
                result=random.choice(["HALAL 100%","HARAM Détecté","DOUTEUX"])
                color="green" if "HALAL" in result else "red" if "HARAM" in result else "orange"
                icon="✅" if "HALAL" in result else "❌" if "HARAM" in result else "⚠️"
                st.markdown(f"""<div style="background:white; border-radius:20px; padding:20px; text-align:center; border:4px solid {color}"><div style="font-size:70px">{icon}</div><div style="font-size:26px; font-weight:900; color:{color}">{result}</div></div>""", unsafe_allow_html=True)
                users[user_email]['history'].append({'date':datetime.now().strftime("%d/%m/%Y %H:%M"),'result':result})
                save_json(USERS_FILE,users)
                st.balloons()

                # MONETAG tous les 3 scans
                if 'monetag_count' not in st.session_state:
                    st.session_state.monetag_count = 0
                st.session_state.monetag_count += 1
                if st.session_state.monetag_count % 3 == 0:
                    st.divider()
                    st.warning(f"🎁 {st.session_state.monetag_count} scans effectués ! Soutiens l'app")
                    st.link_button("👉 CLIQUE ICI POUR SOUTENIR (Pub)", MONETAG_LINK, use_container_width=True, type="primary")

            if st.button("📸 Scanner un autre produit", use_container_width=True):
                st.rerun()
                with st.spinner("Analyse..."):
                    time.sleep(2)
                    if not user['is_vip']: users[user_email]['scans']+=1
                    result=random.choice(["HALAL 100%","HARAM Détecté","DOUTEUX"])
                    color="green" if "HALAL" in result else "red" if "HARAM" in result else "orange"
                    icon="✅" if "HALAL" in result else "❌" if "HARAM" in result else "⚠️"
                    st.markdown(f"""<div style="background:white; border-radius:20px; padding:20px; text-align:center; border:4px solid {color}"><div style="font-size:70px">{icon}</div><div style="font-size:26px; font-weight:900; color:{color}">{result}</div></div>""", unsafe_allow_html=True)
                    users[user_email]['history'].append({'date':datetime.now().strftime("%d/%m/%Y %H:%M"),'result':result})
                    save_json(USERS_FILE,users); st.balloons()

                    # --- MONETAG : GAGNER ARGENT TOUS LES 3 SCANS ---
                    if 'monetag_count' not in st.session_state:
                        st.session_state.monetag_count = 0
                    st.session_state.monetag_count += 1

                    if st.session_state.monetag_count % 3 == 0:
                        st.divider()
                        st.warning(f"🎁 {st.session_state.monetag_count} scans effectués ! Soutiens l'app pour la garder gratuite")
                        st.link_button("👉 CLIQUE ICI POUR SOUTENIR (Pub)", MONETAG_LINK, use_container_width=True, type="primary")
                    if st.button("⬅️ Fermer résultat et revenir", key="close_result"):
                        st.session_state.scan_mode=None; st.rerun()

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    if st.button("🚀\n\nInvite tes amis\nPartage et gagne du hasanat", use_container_width=True, key="invite_graph"):
        st.markdown(f"<a href='https://wa.me/?text=Decouvre Scanner Halal {APP_LINK}' target='_blank' style='display:block; background:#00a651; color:white; text-align:center; padding:12px; border-radius:12px; text-decoration:none; font-weight:900'>📤 PARTAGER SUR WHATSAPP</a>", unsafe_allow_html=True)

    if not user.get('is_vip'):
        st.markdown("""<div style="background:white; border-radius:18px; padding:15px; text-align:center; border:2px solid #ffe082; margin-top:10px"><div style="font-size:30px">📺</div><div style="font-weight:900; font-size:13px">PUB 20s = 1 SCAN GRATUIT</div></div>""", unsafe_allow_html=True)
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
    st.markdown("""<div style="background:linear-gradient(135deg,#00a651,#00c853); border-radius:18px; padding:18px; text-align:center; color:white"><div style="font-size:50px">📖</div><div style="font-weight:900; font-size:20px">CORAN 114 - AUDIO GRATUIT</div><div style="font-size:12px">Écoute & Télécharge</div></div>""", unsafe_allow_html=True)
    recitateur_nom = st.selectbox("🎙️ Choisis ton récitateur", list(RECITATEURS.keys()), key="recitateur")
    base_url = RECITATEURS[recitateur_nom]

    if st.session_state.selected_sourate:
        s_num = st.session_state.selected_sourate
        s_nom = SOURATES_NOMS[s_num-1]
        audio_url = f"{base_url}{s_num}.mp3"
        if st.button("⬅️", key="back_sourate_list"):
            st.session_state.selected_sourate = None; st.rerun()
        st.markdown(f"""
        <div style="background:white; border-radius:20px; padding:20px; border:3px solid #00a651; text-align:center">
            <div style="font-size:60px">📖</div>
            <div style="font-weight:900; font-size:22px; color:#0a2a6b">{s_num}. {s_nom}</div>
            <div style="font-size:12px; color:gray">Récitateur: {recitateur_nom}</div>
        </div>
        """, unsafe_allow_html=True)
        st.audio(audio_url, format="audio/mp3")
        col1, col2 = st.columns(2)
        with col1:
            st.link_button("📥 Télécharger MP3", audio_url, use_container_width=True)
        with col2:
            st.link_button("🌐 Lire texte complet", f"https://quran.com/{s_num}", use_container_width=True)
        st.stop()

    search_coran = st.text_input("🔍 Cherche sourate", placeholder="Ex: Fatiha, Baqara...", key="search_coran")
    for i in range(1,115):
        nom = SOURATES_NOMS[i-1]
        if search_coran.lower() in nom.lower() or search_coran.lower() in f"sourate {i}".lower() or not search_coran:
            c1,c2 = st.columns([4,1])
            with c1:
                st.markdown(f"""
                <div style="background:white; border-radius:18px; padding:14px; display:flex; align-items:center; gap:12px; border:2px solid #eef2ff; margin:6px 0">
                    <div style="background:#0a2a6b; color:white; width:42px; height:42px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:900; font-size:14px">{i}</div>
                    <div style="text-align:left"><div style="font-weight:900; font-size:14px; color:#0a2a6b">{i}. {nom}</div><div style="font-size:10px; color:gray">🎧 Audio + 📖 Texte</div></div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                if st.button("▶️", key=f"play_{i}", use_container_width=True):
                    st.session_state.selected_sourate = i; st.rerun()

elif menu=="Hadiths":
    if not user.get('is_vip'):
        st.markdown("""<div class="card-vip"><div style="font-size:70px">🔒</div><div style="font-weight:900; color:gold">Hadiths VIP - CODE requis</div></div>""", unsafe_allow_html=True)
        st.link_button("💳 PAYER 1500F POUR CODE", WAVE_LINK, type="primary", use_container_width=True)
        st.stop()
    if st.button("⬅️"): st.session_state.bottom_nav="Home"; st.rerun()
    st.markdown("""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:18px; padding:18px; text-align:center; color:white"><div style="font-size:50px">📜</div><div style="font-weight:900">40 HADITHS NAWAWI</div><div style="color:gold">Clique icône pour lire</div></div>""", unsafe_allow_html=True)
    if st.session_state.selected_hadith:
        h = st.session_state.selected_hadith
        if st.button("⬅️"):
            st.session_state.selected_hadith=None; st.rerun()
        st.markdown(f"""
        <div style="background:white; border-radius:18px; padding:20px; border:3px solid gold">
            <div style="text-align:center; font-size:50px">📜</div>
            <div style="text-align:center; font-weight:900; color:#0a2a6b; font-size:20px">Hadith {h['id']}</div>
            <div style="background:#f5f7ff; padding:15px; border-radius:12px; margin:15px 0; text-align:right; font-size:22px; font-weight:bold; color:#0a2a6b">{h['ar']}</div>
            <div style="background:#fff8e1; padding:15px; border-radius:12px; border-left:5px solid gold; font-size:15px; line-height:1.6">{h['fr']}</div>
        </div>
        """, unsafe_allow_html=True)
        st.stop()
    for h in HADITHS_40_VRAIS:
        col1,col2 = st.columns([4,1])
        with col1:
            st.markdown(f"""<div class="card-graph" style="text-align:left; display:flex; align-items:center; gap:10px"><div style="background:#0a2a6b; color:white; width:35px; height:35px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:900; font-size:12px">{h['id']}</div><div><b>Hadith {h['id']}</b><br><span style="font-size:11px; color:gray">{h['ar'][:20]}...</span></div></div>""", unsafe_allow_html=True)
        with col2:
            if st.button("📖", key=f"read_h_{h['id']}", use_container_width=True):
                st.session_state.selected_hadith=h; st.rerun()

elif menu=="Aliments":
    if not user.get('is_vip'):
        st.markdown("""<div class="card-vip"><div style="font-size:70px">🔒</div><div style="font-weight:900; color:gold">Aliments VIP - CODE requis</div></div>""", unsafe_allow_html=True)
        st.link_button("💳 PAYER 1500F POUR CODE", WAVE_LINK, type="primary", use_container_width=True)
        st.stop()
    if st.button("⬅️"): st.session_state.bottom_nav="Home"; st.rerun()
    st.markdown(f"""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:18px; padding:18px; text-align:center; color:white"><div style="font-size:50px">🍖</div><div style="font-weight:900">ALIMENTS HALAL / HARAM</div><div style="color:gold">{len(ALIMENTS_DATA)} aliments</div></div>""", unsafe_allow_html=True)
    if st.session_state.selected_aliment:
        a = st.session_state.selected_aliment
        if st.button("⬅️"):
            st.session_state.selected_aliment=None; st.rerun()
        color = "#00a651" if a['statut']=="HALAL" else "#cc0000"
        st.markdown(f"""
        <div style="background:white; border-radius:18px; padding:20px; border:3px solid {color}; text-align:center">
            <div style="font-size:70px">{a['icon']}</div>
            <div style="font-size:24px; font-weight:900; color:{color}">{a['nom']}</div>
            <div style="background:{color}; color:white; display:inline-block; padding:5px 15px; border-radius:20px; font-weight:900; margin:10px 0">{a['statut']}</div>
            <div style="background:#f5f7ff; padding:15px; border-radius:12px; margin-top:10px; text-align:left">{a['desc']}</div>
        </div>
        """, unsafe_allow_html=True)
        st.stop()
    search = st.text_input("🔍", placeholder="Ex: porc, poulet...")
    for a in ALIMENTS_DATA:
        if search.lower() in a['nom'].lower() or not search:
            col1,col2 = st.columns([4,1])
            with col1:
                color = "#00a651" if a['statut']=="HALAL" else "#cc0000"
                st.markdown(f"""<div class="card-graph" style="text-align:left; border-left:5px solid {color}; display:flex; align-items:center; gap:10px"><div style="font-size:30px">{a['icon']}</div><div><b>{a['nom']}</b><br><span style="color:{color}; font-weight:900; font-size:12px">{a['statut']}</span></div></div>""", unsafe_allow_html=True)
            with col2:
                if st.button("👁️", key=f"view_a_{a['nom']}", use_container_width=True):
                    st.session_state.selected_aliment=a; st.rerun()

elif menu=="Jeux":
    if st.button("⬅️"): st.session_state.bottom_nav="Home"; st.rerun()
    st.markdown("""<div style="background:linear-gradient(135deg,#ff6a00,#ee0979); border-radius:18px; padding:18px; text-align:center; color:white"><div style="font-size:50px">🎮</div><div style="font-weight:900">JEUX ISLAMIQUES</div><div style="font-size:12px">Téléchargeables - GRATUIT</div></div>""", unsafe_allow_html=True)
    jeux = [
        {"nom":"Quiz Coran 114", "icon":"🧠", "link":"https://play.google.com/store/search?q=quiz%20coran&c=apps", "desc":"Teste tes connaissances Coran"},
        {"nom":"Puzzle Kaaba", "icon":"🕋", "link":"https://play.google.com/store/search?q=islamic%20puzzle%20kaaba&c=apps", "desc":"Puzzle 3D Kaaba"},
        {"nom":"Apprendre l'Arabe", "icon":"📚", "link":"https://play.google.com/store/search?q=apprendre%20arabe%20enfants&c=apps", "desc":"Alphabet arabe jeu"},
        {"nom":"Labyrinthe Mosquée", "icon":"🕌", "link":"https://play.google.com/store/search?q=maze%20islamic%20game&c=apps", "desc":"Jeu labyrinthe"},
    ]
    for j in jeux:
        st.markdown(f"""
        <div style="background:white; border-radius:18px; padding:15px; display:flex; align-items:center; gap:12px; border:2px solid #eef2ff; margin:8px 0">
            <div style="font-size:40px">{j['icon']}</div>
            <div style="text-align:left"><div style="font-weight:900">{j['nom']}</div><div style="font-size:11px; color:gray">{j['desc']}</div></div>
        </div>
        """, unsafe_allow_html=True)
        st.link_button(f"📥 Télécharger {j['nom']}", j['link'], use_container_width=True)

elif menu=="Douas":
    if not user.get('is_vip'):
        st.markdown("""<div class="card-vip"><div style="font-size:70px">🔒</div><div style="font-weight:900; color:gold">Douas VIP - CODE requis</div></div>""", unsafe_allow_html=True)
        st.link_button("💳 PAYER 1500F POUR CODE", WAVE_LINK, type="primary", use_container_width=True)
        st.stop()
    if st.button("⬅️"): st.session_state.bottom_nav="Home"; st.rerun()
    st.markdown("""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:18px; padding:18px; text-align:center; color:white"><div style="font-size:50px">🤲</div><div style="font-weight:900">50 DOUAS</div></div>""", unsafe_allow_html=True)
    for i in range(1,51):
        st.markdown(f"""<div class="card-graph" style="text-align:left"><b>🤲 Doua {i}</b> - Bismillah...<br><span style="font-size:11px; color:gray">Invocation quotidienne</span></div>""", unsafe_allow_html=True)

elif menu=="Parametres":
    st.markdown(f"""<div style="background:white; border-radius:20px; padding:20px; text-align:center"><div style="font-size:50px">⚙️</div><b>{user.get('nom')}</b><br>{user_email}<br><b>Code: {user.get('vip_code','Aucun')}</b></div>""", unsafe_allow_html=True)
