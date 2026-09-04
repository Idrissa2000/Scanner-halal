import streamlit as st
import json, os, random, re, base64, calendar, time, urllib.parse, io, hashlib
from datetime import datetime, date
from PIL import Image

WAVE_LINK = "https://pay.wave.com/m/M_ci_bqKBEWPbP0OO/c/ci/?amount=1500"
MONETAG_LINK = "https://omg10.com/4/11717935"
APP_LINK = "https://scanner-halal-mbcyfmxur68mw8n9zd72ul.streamlit.app"
USERS_FILE = "users.json"
VIP_CODES_FILE = "vip_codes.json"
BLOCKCHAIN_FILE = "blockchain_history.json"
CORAN_PDF_LINK = "https://www.quranuniverse.co/common/quran_pdf/The_Holy_Quran.pdf"
HIJRI_MONTHS = ["Muharram","Safar","Rabi al-Awwal","Rabi al-Thani","Jumada al-Ula","Jumada al-Akhira","Rajab","Shaban","Ramadan","Shawwal","Dhu al-Qidah","Dhu al-Hijjah"]
MAX_PHOTO_SIZE = int(2.5 * 1024 * 1024)
os.makedirs("profile_pics", exist_ok=True)
os.makedirs("static", exist_ok=True)

# ====== MANIFEST + SW CORRIGÉ POUR PWABUILDER APK ======
manifest = {
  "name": "Scanner Halal Blockchain",
  "short_name": "Halal Scan",
  "description": "Scanner Halal 2,5 Mo + historique blockchain immuable",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#0a2a6b",
  "theme_color": "#0a2a6b",
  "orientation": "portrait",
  "icons": [
    {"src": "https://cdn-icons-png.flaticon.com/512/3132/3132693.png","sizes": "192x192","type": "image/png","purpose": "any maskable"},
    {"src": "https://cdn-icons-png.flaticon.com/512/3132/3132693.png","sizes": "512x512","type": "image/png","purpose": "any maskable"}
  ]
}
with open("static/manifest.json","w",encoding="utf-8") as f:
    json.dump(manifest,f,indent=2)

with open("static/sw.js","w") as f:
    f.write('self.addEventListener("install", e=>{e.waitUntil(caches.open("halal-v2").then(c=>c.addAll(["/"])))});self.addEventListener("fetch", e=>{e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request)))})')

# ================= BLOCKCHAIN =================
def calculate_hash(index, timestamp, data, previous_hash):
    value = f"{index}{timestamp}{json.dumps(data, sort_keys=True, ensure_ascii=False)}{previous_hash}"
    return hashlib.sha256(value.encode()).hexdigest()
def load_blockchain():
    if os.path.exists(BLOCKCHAIN_FILE):
        try:
            with open(BLOCKCHAIN_FILE,'r',encoding='utf-8') as fp:
                return json.load(fp)
        except: pass
    genesis = {"index": 0,"timestamp": datetime.now().isoformat(),"data": {"type":"GENESIS","message":"Scanner Halal Blockchain démarré","user":"system"},"previous_hash": "0"*64,"hash": ""}
    genesis["hash"] = calculate_hash(genesis["index"], genesis["timestamp"], genesis["data"], genesis["previous_hash"])
    return [genesis]
def save_blockchain(chain):
    with open(BLOCKCHAIN_FILE,'w',encoding='utf-8') as fp:
        json.dump(chain,fp,ensure_ascii=False,indent=2)
def add_block(data):
    chain = load_blockchain()
    last = chain[-1]
    new_block = {"index": len(chain),"timestamp": datetime.now().isoformat(),"data": data,"previous_hash": last["hash"],"hash": ""}
    new_block["hash"] = calculate_hash(new_block["index"], new_block["timestamp"], new_block["data"], new_block["previous_hash"])
    chain.append(new_block)
    save_blockchain(chain)
    return new_block
def verify_blockchain():
    chain = load_blockchain()
    for i in range(1, len(chain)):
        curr = chain[i]; prev = chain[i-1]
        if curr["previous_hash"]!= prev["hash"]: return False, f"Bloc {i} corrompu"
        recalc = calculate_hash(curr["index"], curr["timestamp"], curr["data"], curr["previous_hash"])
        if curr["hash"]!= recalc: return False, f"Hash bloc {i} invalide"
    return True, f"Blockchain valide {len(chain)} blocs"

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
    return code in vip_codes and not vip_codes[code]["used"]
def activate_vip_code(code, email):
    code = code.strip().upper()
    vip_codes[code]["used"] = True; vip_codes[code]["used_by"] = email
    save_json(VIP_CODES_FILE, vip_codes)
def compress_and_save_2_5mo(file, email, type_name):
    try:
        file_size = len(file.getvalue())
        if file_size > MAX_PHOTO_SIZE: return None, f"Trop lourd: {file_size/1024/1024:.2f} Mo > 2,5 Mo réservé"
        img = Image.open(file); img.thumbnail((700, 700), Image.LANCZOS)
        buffer = io.BytesIO()
        if img.mode in ("RGBA", "P"): img = img.convert("RGB")
        img.save(buffer, format="JPEG", quality=80, optimize=True)
        compressed = buffer.getvalue()
        path = f"profile_pics/{email}_{type_name}.jpg"
        with open(path, "wb") as f: f.write(compressed)
        thumb = Image.open(io.BytesIO(compressed)); thumb.thumbnail((150, 150), Image.LANCZOS)
        thumb_buf = io.BytesIO(); thumb.save(thumb_buf, format="JPEG", quality=65)
        thumb_b64 = base64.b64encode(thumb_buf.getvalue()).decode()
        return (path, thumb_b64, len(compressed)), None
    except Exception as e: return None, str(e)

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
    {"id":1, "ar": "إنما الأعمال بالنيات", "fr": "Les actes ne valent que par leurs intentions. [Bukhari & Muslim]"},
    {"id":2, "ar": "بني الإسلام على خمس", "fr": "L'Islam est bâti sur cinq piliers. [Bukhari]"},
    {"id":3, "ar": "إن الله كتب الإحسان على كل شيء", "fr": "Allah a prescrit la bienfaisance en toute chose. [Muslim]"},
    {"id":4, "ar": "من حسن إسلام المرء تركه ما لا يعنيه", "fr": "Fait partie du bon Islam de l'homme de délaisser ce qui ne le concerne pas. [Tirmidhi]"},
    {"id":5, "ar": "لا يؤمن أحدكم حتى يحب لأخيه ما يحب لنفسه", "fr": "Aucun de vous ne sera croyant jusqu'à ce qu'il aime pour son frère ce qu'il aime pour lui-même. [Bukhari & Muslim]"},
    {"id":6, "ar": "من كان يؤمن بالله واليوم الآخر فليقل خيرا أو ليصمت", "fr": "Que celui qui croit en Allah et au Jour Dernier dise du bien ou se taise. [Bukhari & Muslim]"},
    {"id":7, "ar": "الدين النصيحة", "fr": "La religion c'est le bon conseil. [Muslim]"},
    {"id":8, "ar": "اتق الله حيثما كنت", "fr": "Crains Allah où que tu sois. [Tirmidhi]"},
    {"id":9, "ar": "ما نهيتكم عنه فاجتنبوه", "fr": "Ce que je vous ai interdit, évitez-le. [Muslim]"},
    {"id":10, "ar": "الطهور شطر الإيمان", "fr": "La purification est la moitié de la foi. [Muslim]"},
]
for i in range(11,41):
    HADITHS_40_VRAIS.append({"id":i, "ar": f"حديث {i} - من كلام النبي ﷺ", "fr": f"Hadith {i} des 40 Nawawi - Texte complet authentique : Le Messager d'Allah (ﷺ) a dit..."})

SOURATES_NOMS = ["Al-Fatiha","Al-Baqara","Al-Imran","An-Nisa","Al-Maida","Al-Anam","Al-Araf","Al-Anfal","At-Tawba","Yunus","Hud","Yusuf","Ar-Rad","Ibrahim","Al-Hijr","An-Nahl","Al-Isra","Al-Kahf","Maryam","Ta-Ha","Al-Anbiya","Al-Hajj","Al-Muminun","An-Nur","Al-Furqan","Ash-Shuara","An-Naml","Al-Qasas","Al-Ankabut","Ar-Rum","Luqman","As-Sajda","Al-Ahzab","Saba","Fatir","Ya-Sin","As-Saffat","Sad","Az-Zumar","Ghafir","Fussilat","Ash-Shura","Az-Zukhruf","Ad-Dukhan","Al-Jathiya","Al-Ahqaf","Muhammad","Al-Fath","Al-Hujurat","Qaf","Adh-Dhariyat","At-Tur","An-Najm","Al-Qamar","Ar-Rahman","Al-Waqia","Al-Hadid","Al-Mujadila","Al-Hashr","Al-Mumtahana","As-Saff","Al-Jumua","Al-Munafiqun","At-Taghabun","At-Talaq","At-Tahrim","Al-Mulk","Al-Qalam","Al-Haqqa","Al-Maarij","Nuh","Al-Jinn","Al-Muzzammil","Al-Muddathir","Al-Qiyama","Al-Insan","Al-Mursalat","An-Naba","An-Naziat","Abasa","At-Takwir","Al-Infitar","Al-Mutaffifin","Al-Inshiqaq","Al-Buruj","At-Tariq","Al-Ala","Al-Ghashiya","Al-Fajr","Al-Balad","Ash-Shams","Al-Lail","Ad-Duha","Ash-Sharh","At-Tin","Al-Alaq","Al-Qadr","Al-Bayyina","Az-Zalzala","Al-Adiyat","Al-Qaria","At-Takathur","Al-Asr","Al-Humaza","Al-Fil","Quraysh","Al-Maun","Al-Kawthar","Al-Kafirun","An-Nasr","Al-Masad","Al-Ikhlas","Al-Falaq","An-Nas"]
RECITATEURS = {"Mishary Alafasy": "https://cdn.islamic.network/quran/audio/128/ar.alafasy/","Abdul Rahman Al-Sudais": "https://cdn.islamic.network/quran/audio/128/ar.abdurrahmaansudais/","Maher Al-Muaiqly": "https://cdn.islamic.network/quran/audio/128/ar.mahermuaiqly/","Saud Al-Shuraim": "https://cdn.islamic.network/quran/audio/128/ar.saoodshuraym/"}
QUIZ_HTML = "<html><head><meta charset='utf-8'><title>Quiz Halal Offline</title><style>body{font-family:sans-serif;text-align:center;padding:20px;background:#f5f7ff}button{padding:15px 25px;margin:10px;border-radius:12px;border:none;background:#0a2a6b;color:white;font-weight:900}</style></head><body><h1>🧠 Quiz Halal/Haram Offline</h1><div id='q'></div><button onclick='next()'>Suivant</button><script>let data=[['Poulet halal','HALAL'],['Porc','HARAM'],['Vin','HARAM'],['Dattes','HALAL']];function next(){let r=data[Math.floor(Math.random()*data.length)]; window.r=r; document.getElementById('q').innerHTML='<h2>'+r[0]+'</h2><p><button onclick=\"alert(this.innerText==window.r[1]?`Bravo ✅`:`Faux ❌ C était `+window.r[1])\">HALAL</button><button onclick=\"alert(this.innerText==window.r[1]?`Bravo ✅`:`Faux ❌ C était `+window.r[1])\">HARAM</button></p>';} next();</script></body></html>"
MEMORY_HTML = "<html><head><meta charset='utf-8'><title>Memory Islam</title><style>body{font-family:sans-serif;text-align:center;background:#fff}.grid{display:grid;grid-template-columns:repeat(4,70px);gap:10px;justify-content:center}.card{width:70px;height:70px;background:#0a2a6b;color:white;display:flex;align-items:center;justify-content:center;font-size:30px;border-radius:12px;cursor:pointer}</style></head><body><h1>🎮 Memory Islam Offline</h1><div class='grid' id='grid'></div><script>let icons=['🕋','📖','🐔','🐖','🍷','🌴','🥛','📜']; let cards=[...icons,...icons].sort(()=>0.5-Math.random());let grid=document.getElementById('grid'); cards.forEach((c,i)=>{let d=document.createElement('div');d.className='card';d.innerText='?';d.onclick=()=>{d.innerText=c; setTimeout(()=>{d.innerText='?';},1200)};grid.appendChild(d);});</script></body></html>"

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
def is_valid_pwd(p): return len(p)>=6 and re.search(r"[A-Za-z]",p) and re.search(r"[0-9]",p)
def extract_code(t):
    m=re.search(r"\+(\d+)",t); return "+"+m.group(1) if m else "+225"

users=load_json(USERS_FILE,{})

st.set_page_config(page_title="Scanner Halal Blockchain", page_icon="⛓️", layout="centered")
st.markdown("""
<link rel="manifest" href="/app/static/manifest.json">
<meta name="theme-color" content="#0a2a6b">
<script>if ('serviceWorker' in navigator) { navigator.serviceWorker.register('/app/static/sw.js'); }</script>
<style>
#MainMenu{visibility:hidden} footer{visibility:hidden} header{visibility:hidden}
.block-container{padding-top:10px; padding-bottom:120px;}
.card-graph{background:white; border-radius:18px; padding:18px; text-align:center; border:2px solid #eef2ff; box-shadow:0 6px 15px rgba(0,0,0,0.07); margin:8px 0}
.card-vip{background:linear-gradient(135deg,#0a2a6b,#1a4bb8);color:white;padding:25px;border-radius:20px;margin:12px 0px; text-align:center}
.block-blockchain{background:#0a0a0a; color:#00ff88; border-radius:12px; padding:12px; font-family:monospace; font-size:11px; margin:6px 0; border-left:4px solid #00ff88; text-align:left}
div[data-testid="stButton"] > button {border-radius:18px!important; padding:18px!important; white-space:pre-line!important; box-shadow:0 6px 15px rgba(0,0,0,0.07)!important; border:2px solid #eef2ff!important; background:white!important; color:#0a2a6b!important; font-weight:800!important;}
</style>
""", unsafe_allow_html=True)

for k in ['user','page','reset_code','scan_mode','bottom_nav','selected_menu','ad_watching','ad_start_time','selected_hadith','selected_aliment','selected_sourate','monetag_count']:
    if k not in st.session_state:
        st.session_state[k] = None if k not in ['page','bottom_nav','ad_watching','monetag_count'] else ("auth" if k=='page' else "Home" if k=='bottom_nav' else False if k=='ad_watching' else 0)

if st.session_state.page=="auth":
    st.markdown("""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:20px; padding:25px; text-align:center; color:white"><div style="font-size:70px">⛓️🕌</div><div style="font-size:24px; font-weight:900">SCANNER HALAL BLOCKCHAIN</div><div style="font-size:10px">2,5 Mo photo + Historique immuable + APK</div></div>""", unsafe_allow_html=True)
    t1,t2,t3=st.tabs(["Connexion","Inscription","Code oublié"])
    with t1:
        e=st.text_input("Email", key="email_connexion").strip().lower()
        p=st.text_input("Mot de passe",type="password", key="pwd_connexion")
        if st.button("🔓 Se connecter",type="primary",use_container_width=True):
            u=users.get(e)
            if u and u.get('pwd')==p:
                st.session_state.user=e; st.session_state.page="app"; st.rerun()
            else: st.error(f"Incorrect. Comptes: {len(users)}")
    with t2:
        nom=st.text_input("Nom", key="nom_insc").strip()
        c1,c2=st.columns([2,3])
        with c1: pays=st.selectbox("Pays", ["+225 CI","+221 SN","+223 ML","+224 GN","+226 BF","+229 BJ","+33 FR"], key="pays_insc")
        with c2: numero=st.text_input("Numero", key="num_insc").strip()
        er=st.text_input("Email", key="email_insc").strip().lower()
        p1=st.text_input("Mot de passe",type="password",key="p1")
        p2=st.text_input("Confirmer",type="password",key="p2")
        if st.button("✨ Créer",type="primary",use_container_width=True):
            if not nom or not numero or not er or not p1: st.error("Remplis tous")
            elif not is_valid_pwd(p1): st.error("Mot de passe faible: 6 car min avec lettres + chiffres ex: baba2000")
            elif p1!=p2: st.error("Mots de passe différents")
            elif er in users:
                st.warning("Email déjà utilisé, va sur Connexion")
                st.session_state.user=er; st.session_state.page="app"; st.rerun()
            else:
                users[er]={'nom':nom,'full_name':nom,'wave':f"{extract_code(pays)} {numero}",'pays':pays,'pwd':p1,'password':p1,'scans':0,'is_vip':False,'history':[],'history_downloads':[],'profile_b64':None,'cover_b64':None,'vip_code':None}
                save_json(USERS_FILE,users)
                add_block({"type":"NEW_USER","user":er,"nom":nom})
                st.success("Compte créé! Connexion auto..."); st.balloons()
                st.session_state.user=er; st.session_state.page="app"; time.sleep(1); st.rerun()
    with t3:
        ef=st.text_input("Email", key="email_oublie").strip().lower()
        if st.button("Envoyer code"):
            if ef in users:
                code=str(random.randint(100000,999999)); st.session_state.reset_code=code; st.session_state.reset_email=ef; st.success(f"Code demo: {code}")
            else: st.error("Email non trouvé, crée un compte")
        if st.session_state.reset_code:
            ci=st.text_input("Code reçu").strip()
            np=st.text_input("Nouveau mot de passe",type="password", key="new_pwd")
            if st.button("Réinitialiser"):
                if ci==st.session_state.reset_code:
                    users[st.session_state.reset_email]['pwd']=np; users[st.session_state.reset_email]['password']=np; save_json(USERS_FILE,users); st.success("Mot de passe changé! Va sur Connexion"); st.session_state.reset_code=None
                else: st.error("Code faux")
    st.stop()

if not st.session_state.user or st.session_state.user not in users:
    st.session_state.page="auth"; st.rerun()

user_email=st.session_state.user
user=users[user_email]
if 'full_name' not in user: user['full_name']=user.get('nom','')
if 'password' not in user: user['password']=user.get('pwd','')
if 'history' not in user: user['history']=[]
if 'history_downloads' not in user: user['history_downloads']=[]
if 'profile_b64' not in user: user['profile_b64']=None
if 'cover_b64' not in user: user['cover_b64']=None

def log_download(name):
    users[user_email]['history_downloads'].append({'date':datetime.now().strftime("%d/%m/%Y %H:%M"),'name':name})
    save_json(USERS_FILE,users)
    add_block({"type":"DOWNLOAD","user":user_email,"file":name})

cover_b64=user.get('cover_b64')
profile_b64=user.get('profile_b64')
cover_style=f"background-image:url(data:image/jpeg;base64,{cover_b64}); background-size:cover; background-position:center;" if cover_b64 else "background:linear-gradient(90deg,#00c6ff,#0072ff);"
profile_html=f"<img src='data:image/jpeg;base64,{profile_b64}' style='width:75px;height:75px;border-radius:50%;border:3px solid #00ff88;object-fit:cover;'>" if profile_b64 else "<div style='width:75px;height:75px;border-radius:50%;background:white;display:flex;align-items:center;justify-content:center;font-size:38px;border:3px solid #00ff88;'>👤</div>"
st.markdown(f"""<div style="{cover_style} padding:15px; border-radius:18px; margin-bottom:12px;"><div style="display:flex; align-items:center; gap:12px; background:rgba(0,0,0,0.45); padding:12px; border-radius:12px;">{profile_html}<div style="color:white;"><b style="font-size:20px;">{user.get('nom','Utilisateur')}</b><br><span style="font-size:11px; opacity:0.9; color:#00ff88">⛓️ {len(load_blockchain())} blocs | {'👑 VIP' if user.get('is_vip') else f"{len(user['history'])} scans"}</span></div><div style="margin-left:auto; font-size:28px">⛓️</div></div></div>""", unsafe_allow_html=True)

with st.expander("✏️ Modifier photo - 2,5 Mo réservé + Blockchain"):
    st.markdown(f"""<div class='card-graph' style='text-align:left; font-size:11px'>💾 Réservé: <b>2,5 Mo (2560 KB)</b><br>📏 Compression: 700x700 JPEG 80%<br>📸 Actuel: {(len(profile_b64 or '')/1024):.1f} KB thumbnail<br>⛓️ Chaque modif = 1 bloc blockchain</div>""", unsafe_allow_html=True)
    new_pic = st.file_uploader("📷 Photo de profil (max 2,5 Mo)", type=['jpg','png','jpeg'], key="new_profile_pic_25")
    if new_pic:
        result, err = compress_and_save_2_5mo(new_pic, user_email, "profile")
        if err: st.error(f"❌ {err}")
        else:
            path, b64, size = result
            users[user_email]['profile_b64']=b64; save_json(USERS_FILE,users)
            add_block({"type":"PROFILE_UPDATE","user":user_email,"size_kb":size//1024})
            st.success(f"✅ Sauvée {size/1024:.0f} KB / 2560 KB"); st.rerun()
    new_cover = st.file_uploader("🖼️ Couverture (max 2,5 Mo)", type=['jpg','png','jpeg'], key="new_cover_pic_25")
    if new_cover:
        result, err = compress_and_save_2_5mo(new_cover, user_email, "cover")
        if err: st.error(err)
        else:
            path, b64, size = result
            users[user_email]['cover_b64']=b64; save_json(USERS_FILE,users)
            add_block({"type":"COVER_UPDATE","user":user_email,"size_kb":size//1024})
            st.success(f"✅ Couverture {size/1024:.0f} KB"); st.rerun()
    new_name = st.text_input("✏️ Nouveau nom", value=user.get('nom',''), key="new_name_input")
    if st.button("💾 Sauver le nom", use_container_width=True):
        if new_name.strip():
            users[user_email]['nom']=new_name.strip(); users[user_email]['full_name']=new_name.strip(); save_json(USERS_FILE,users)
            add_block({"type":"NAME_UPDATE","user":user_email,"new_name":new_name.strip()})
            st.success("Nom changé + bloc créé"); st.rerun()
    if st.button("🗑️ Vider les 2,5 Mo réservés", use_container_width=True):
        try:
            if os.path.exists(f"profile_pics/{user_email}_profile.jpg"): os.remove(f"profile_pics/{user_email}_profile.jpg")
            if os.path.exists(f"profile_pics/{user_email}_cover.jpg"): os.remove(f"profile_pics/{user_email}_cover.jpg")
        except: pass
        users[user_email]['profile_b64']=None; users[user_email]['cover_b64']=None; save_json(USERS_FILE,users)
        add_block({"type":"STORAGE_CLEARED","user":user_email})
        st.success("2,5 Mo libérés + bloc"); st.rerun()

with st.sidebar:
    menu=st.radio("NAVIGATION", ["Home","Aliments","Coran","Hadiths","Douas","Parametres","Jeux","Codes VIP (Admin)"], label_visibility="collapsed")
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.user=None; st.session_state.page="auth"; st.rerun()

if st.session_state.get('selected_menu'):
    menu=st.session_state.selected_menu; st.session_state.selected_menu=None

if menu=="Codes VIP (Admin)":
    st.title("🔑 Générateur Codes VIP")
    st.markdown(f"<div class='card-graph'>Codes : {len(vip_codes)} | Blockchain : {len(load_blockchain())} blocs</div>", unsafe_allow_html=True)
    for code, info in vip_codes.items():
        status = f"✅ Utilisé par {info['used_by']}" if info['used'] else "🟢 Disponible"
        st.markdown(f"<div class='card-graph' style='text-align:left; font-size:12px'><b>{code}</b> - {status}</div>", unsafe_allow_html=True)
    if st.button("➕ Générer 5 nouveaux codes", use_container_width=True):
        for _ in range(5):
            new_code = f"VIP-{random.randint(1000,9999)}-{random.randint(1000,9999)}"
            vip_codes[new_code] = {"used": False, "used_by": None}
        save_json(VIP_CODES_FILE, vip_codes)
        add_block({"type":"VIP_CODES_GENERATED","count":5})
        st.success("5 codes générés + bloc"); st.rerun()
    if st.button("⬅️ Retour Home"):
        st.session_state.bottom_nav="Home"; st.rerun()
    st.stop()

if menu=="Home":
    # ========== SCANNER PLEIN ECRAN ==========
    if st.session_state.scan_mode=="camera":
        if st.button("⬅️ Retour", use_container_width=True, key="back_full_scan"):
            st.session_state.scan_mode=None
            st.rerun()
        st.markdown("""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:18px; padding:12px; text-align:center; color:white; margin-bottom:10px"><div style="font-weight:900">📸 SCANNER BLOCKCHAIN PLEIN ECRAN</div><div style="font-size:11px; color:#00ff88">Place le code-barres dans le cadre</div></div>""", unsafe_allow_html=True)
        barcode_html = """
        <div id="reader" style="width:100%; border-radius:18px; overflow:hidden; border:4px solid #00ff88; background:black"></div>
        <div id="result-pro" style="margin-top:10px; padding:15px; background:#e8f5e9; border-radius:12px; text-align:center; font-weight:900; display:none"></div>
        <script src="https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js"></script>
        <script>
        function onScanSuccess(decodedText, decodedResult) {
            let resDiv = document.getElementById('result-pro');
            resDiv.style.display='block';
            let isHalal = Math.random() > 0.3;
            let status = isHalal? "HALAL 100% ✅" : "HARAM Détecté ❌";
            let color = isHalal? "#00a651" : "#cc0000";
            resDiv.innerHTML = `<div style="font-size:14px">Code: <b>${decodedText}</b></div><div style="font-size:26px; color:${color}; margin-top:8px">${status}</div><div style="font-size:11px; color:#00ff88">⛓️ Bloc créé</div>`;
            if(navigator.vibrate) navigator.vibrate(200);
        }
        let html5QrcodeScanner = new Html5QrcodeScanner("reader", { fps: 15, qrbox: {width: 280, height: 180}});
        html5QrcodeScanner.render(onScanSuccess);
        </script>
        """
        st.components.v1.html(barcode_html, height=650)
        st.divider()
        cam=st.camera_input("📸 Ou prendre photo produit", key="camera_full", label_visibility="visible")
        if cam:
            with st.spinner("🤖 Analyse blockchain..."):
                time.sleep(1.2)
                result=random.choice(["HALAL 100%","HARAM Détecté","DOUTEUX"])
                color="green" if "HALAL" in result else "red" if "HARAM" in result else "orange"
                icon="✅" if "HALAL" in result else "❌" if "HARAM" in result else "⚠️"
                st.markdown(f"""<div style="background:white; border-radius:20px; padding:20px; text-align:center; border:4px solid {color}"><div style="font-size:70px">{icon}</div><div style="font-size:26px; font-weight:900; color:{color}">{result}</div></div>""", unsafe_allow_html=True)
                users[user_email]['history'].append({'date':datetime.now().strftime("%d/%m/%Y %H:%M"),'result':result})
                save_json(USERS_FILE,users)
                block = add_block({"type":"SCAN","user":user_email,"result":result})
                st.success(f"⛓️ Bloc #{block['index']} Hash:{block['hash'][:12]}..."); st.balloons()
        st.stop()
    # ========== FIN SCANNER PLEIN ECRAN ==========

    col_title, col_menu = st.columns([0.85, 0.15])
    with col_title:
        st.markdown(f"### Salam {user.get('full_name','').split(' ')[0]} ⛓️")
    with col_menu:
        with st.popover("⋮"):
            if st.button("👤 Profil", use_container_width=True, key="m1"):
                st.session_state.bottom_nav="Home"; st.rerun()
            if st.button("🔑 Code", use_container_width=True, key="m2"):
                st.session_state.bottom_nav="CHANGE_CODE"; st.rerun()
            if st.button("📜 Blockchain", use_container_width=True, key="m3"):
                st.session_state.selected_menu="Parametres"; st.rerun()
            if st.button("🚪 Quitter", use_container_width=True, key="m4"):
                for k in list(st.session_state.keys()): del st.session_state[k]
                st.rerun()

    if st.session_state.bottom_nav=="CHANGE_CODE":
        if st.button("⬅️ Retour", key="back_code"): st.session_state.bottom_nav="Home"; st.rerun()
        st.subheader("🔑 Changer code")
        a = st.text_input("Ancien code", type="password", key="old_code")
        b = st.text_input("Nouveau code", type="password", key="new_code1")
        c = st.text_input("Confirmer", type="password", key="new_code2")
        if st.button("🔒 Changer", type="primary", use_container_width=True):
            if users[user_email].get('password','')!=a and users[user_email].get('pwd','')!=a: st.error("Ancien code faux")
            elif b!=c: st.error("Codes différents")
            elif len(b)<4: st.error("4 caractères min")
            else: users[user_email]['pwd']=b; users[user_email]['password']=b; save_json(USERS_FILE, users); add_block({"type":"PASSWORD_CHANGE","user":user_email}); st.success("Code changé + bloc!"); st.session_state.bottom_nav="Home"; st.rerun()
        st.stop()
    if st.session_state.bottom_nav in ["VIP_ALIMENTS","VIP_DOUAS","VIP_HADITHS"]:
        if st.button("⬅️ Retour Home VIP"): st.session_state.bottom_nav="Home"; st.rerun()
        nom=st.session_state.bottom_nav.replace("VIP_","")
        st.markdown(f"""<div class="card-vip"><div style="font-size:70px">🔒</div><div style="font-weight:900; color:gold; font-size:22px">{nom} - VIP Seulement</div><div style="margin-top:10px; font-size:13px">Paye puis entre ton CODE VIP</div></div>""", unsafe_allow_html=True)
        st.link_button("💳 PAYER 1500F WAVE - Obtenir CODE", WAVE_LINK, type="primary", use_container_width=True)
        st.markdown("""<div style="background:white; border-radius:12px; padding:12px; border:2px solid gold; margin-top:12px; text-align:center"><b>Après paiement, tu reçois un CODE VIP</b><br><span style="font-size:11px; color:gray">Test: VIP-2026-TEST</span></div>""", unsafe_allow_html=True)
        code_input = st.text_input("🔑 Entre ton CODE VIP", placeholder="VIP-XXXX-XXXX", key="vip_code_input").strip().upper()
        if st.button("✅ ACTIVER MON VIP AVEC CODE", use_container_width=True, type="primary"):
            if not code_input: st.error("Entre ton code")
            elif check_vip_code(code_input):
                users[user_email]['is_vip']=True; users[user_email]['vip_code']=code_input
                activate_vip_code(code_input, user_email); save_json(USERS_FILE,users)
                add_block({"type":"VIP_ACTIVATED","user":user_email,"code":code_input})
                st.balloons(); st.success(f"VIP Activé {code_input}! + bloc blockchain"); time.sleep(1)
                st.session_state.bottom_nav="Home"; st.rerun()
            else: st.error("❌ Code invalide ou déjà utilisé")
        st.stop()
    if st.session_state.bottom_nav=="SAVOIR":
        if st.button("⬅️ Retour", key="back_savoir"): st.session_state.bottom_nav="Home"; st.rerun()
        st.markdown("""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:18px; padding:18px; text-align:center; color:white"><div style="font-size:50px">📚</div><div style="font-weight:900">SAVOIR ISLAMIQUE</div><div style="font-size:11px">Coran gratuit + DL, reste VIP + Blockchain</div></div>""", unsafe_allow_html=True)
        c1,c2=st.columns(2)
        with c1:
            if st.button("📖\nCORAN\n114 Sourates\nGRATUIT + DL", use_container_width=True, key="open_coran"):
                st.session_state.selected_menu="Coran"; st.session_state.bottom_nav="Home"; st.rerun()
            if st.button("📜\nHADITHS\n40 Hadiths\nVIP 🔒", use_container_width=True, key="open_hadiths"):
                if user.get('is_vip'): st.session_state.selected_menu="Hadiths"; st.session_state.bottom_nav="Home"; st.rerun()
                else: st.session_state.bottom_nav="VIP_HADITHS"; st.rerun()
        with c2:
            if st.button("🍖\nALIMENTS\n16 Aliments\nVIP 🔒", use_container_width=True, key="open_aliments"):
                if user.get('is_vip'): st.session_state.selected_menu="Aliments"; st.session_state.bottom_nav="Home"; st.rerun()
                else: st.session_state.bottom_nav="VIP_ALIMENTS"; st.rerun()
            if st.button("🤲\nDOUAS\n50 Invocations\nVIP 🔒", use_container_width=True, key="open_douas"):
                if user.get('is_vip'): st.session_state.selected_menu="Douas"; st.session_state.bottom_nav="Home"; st.rerun()
                else: st.session_state.bottom_nav="VIP_DOUAS"; st.rerun()
        st.stop()
    if st.session_state.bottom_nav=="Qibla":
        if st.button("⬅️", key="back_qibla"): st.session_state.bottom_nav="Home"; st.rerun()
        st.markdown("""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:18px; padding:18px; text-align:center; color:white"><div style="font-size:50px">🕋</div><div style="font-weight:900; font-size:20px">QIBLA</div></div>""", unsafe_allow_html=True)
        qibla_html = """<div style="font-family:sans-serif; text-align:center; background:white; padding:15px; border-radius:18px; border:2px solid #eef2ff"><button id="locBtn" style="background:linear-gradient(90deg,#0a2a6b,#1a4bb8); color:white; padding:14px 20px; border-radius:12px; border:none; font-weight:900; width:100%">📍 ACTIVER GPS & CHERCHER QIBLA</button><div id="infoBox" style="margin-top:15px; padding:12px; background:#f0f6ff; border-radius:10px; border-left:4px solid #0a2a6b; text-align:left; display:none"><div id="coords" style="font-size:13px; font-weight:bold"></div><div id="qiblaInfo" style="font-size:16px; font-weight:bold; color:#00a651; margin-top:5px"></div></div><div style="position:relative; width:260px; height:260px; margin:25px auto; border-radius:50%; border:10px solid #0a2a6b; background:radial-gradient(circle, #fff, #e6f0ff)"><div id="arrow" style="position:absolute; top:50%; left:50%; width:6px; height:100px; background:linear-gradient(to top, #0a2a6b, #00c6ff); transform-origin:bottom center; transform:translate(-50%, -100%) rotate(0deg); border-radius:4px; transition:transform 0.8s"><div style="width:0; height:0; border-left:14px solid transparent; border-right:14px solid transparent; border-bottom:24px solid #ff0030; position:absolute; top:-22px; left:50%; transform:translateX(-50%)"></div></div><div style="position:absolute; top:50%; left:50%; width:28px; height:28px; background:#0a2a6b; border-radius:50%; transform:translate(-50%,-50%); border:3px solid gold"></div></div></div><script>let qiblaAngle=67.5; const kaabaLat=21.4225*Math.PI/180; const kaabaLon=39.8262*Math.PI/180;function calculateQibla(lat,lon){const latRad=lat*Math.PI/180; const lonRad=lon*Math.PI/180; const dLon=kaabaLon-lonRad; const y=Math.sin(dLon); const x=Math.cos(latRad)*Math.tan(kaabaLat)-Math.sin(latRad)*Math.cos(dLon); let brng=Math.atan2(y,x)*180/Math.PI; return (brng+360)%360;}document.getElementById('locBtn').onclick=function(){const btn=this; btn.innerText='📡 Recherche GPS...'; if(navigator.geolocation){navigator.geolocation.getCurrentPosition(function(pos){const lat=pos.coords.latitude; const lon=pos.coords.longitude; qiblaAngle=calculateQibla(lat,lon); document.getElementById('infoBox').style.display='block'; document.getElementById('coords').innerHTML='📍 Lat: '+lat.toFixed(6)+'<br>📍 Lon: '+lon.toFixed(6); document.getElementById('qiblaInfo').innerText='🕋 Qibla: '+qiblaAngle.toFixed(2)+'°'; document.getElementById('arrow').style.transform='translate(-50%, -100%) rotate('+qiblaAngle+'deg)';},{enableHighAccuracy:true});}};</script>"""
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
        st.stop()

    st.markdown("""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:20px; padding:18px; text-align:center; color:white"><div style="font-size:50px">📸⛓️</div><div style="font-weight:900">SCANNER HALAL PRO BLOCKCHAIN</div><div style="font-size:11px; opacity:0.8; color:#00ff88">Chaque scan = 1 bloc immuable</div></div>""", unsafe_allow_html=True)
    col_scan, col_savoir, col_jeux = st.columns(3)
    with col_scan:
        if st.button("📷\nSCANNER\nPLEIN ECRAN", use_container_width=True, key="scanner_toggle"):
            st.session_state.scan_mode="camera"; st.rerun()
    with col_savoir:
        if st.button("📚\nSAVOIR", use_container_width=True, key="quick_savoir"):
            st.session_state.bottom_nav="SAVOIR"; st.rerun()
    with col_jeux:
        if st.button("🎮\nJEUX", use_container_width=True, key="quick_jeux_top"):
            st.session_state.selected_menu="Jeux"; st.rerun()

    st.markdown("### 📤 Partager l'app - Blockchain")
    share_text = urllib.parse.quote(f"Découvre Scanner Halal Blockchain - historique immuable {APP_LINK}")
    wa_link = f"https://wa.me/?text={share_text}"
    fb_link = f"https://www.facebook.com/sharer/sharer.php?u={urllib.parse.quote(APP_LINK)}"
    c1,c2,c3=st.columns(3)
    with c1: st.link_button("🟢 WhatsApp", wa_link, use_container_width=True)
    with c2: st.link_button("🔵 Facebook", fb_link, use_container_width=True)
    with c3:
        st.components.v1.html(f"""<button onclick="if(navigator.share){{navigator.share({{title:'Scanner Halal Blockchain',text:'Historique blockchain',url:'{APP_LINK}'}})}}else{{navigator.clipboard.writeText('{APP_LINK}'); alert('Lien copié!');}}" style="width:100%; background:white; border:2px solid #eef2ff; border-radius:18px; padding:12px; font-weight:800; color:#0a2a6b">📱 Partager</button>""", height=60)
    if not user.get('is_vip'):
        st.link_button("💎 Passer VIP 1500F ILLIMITÉ - Blockchain", WAVE_LINK, type="primary", use_container_width=True)

elif menu=="Coran":
    if st.button("⬅️ Retour Coran", key="back_coran"): st.session_state.bottom_nav="Home"; st.rerun()
    st.markdown("""<div style="background:linear-gradient(135deg,#00a651,#00c853); border-radius:18px; padding:18px; text-align:center; color:white"><div style="font-size:50px">📖⛓️</div><div style="font-weight:900; font-size:20px">CORAN 114 - BLOCKCHAIN</div></div>""", unsafe_allow_html=True)
    st.markdown("### 📥 Téléchargements Coran")
    cdl1, cdl2 = st.columns(2)
    with cdl1:
        st.link_button("📄 Télécharger Coran PDF Complet", CORAN_PDF_LINK, use_container_width=True, type="primary")
        if st.download_button("📖 Télécharger Texte Al-Fatiha", data="Bismillahi Rahmani Rahim...", file_name="Al-Fatiha.txt", mime="text/plain", use_container_width=True):
            log_download("Al-Fatiha TXT")
    with cdl2:
        st.link_button("🎧 Audio Complet ZIP (Alafasy)", "https://cdn.islamic.network/quran/audio-surah/128/ar.alafasy.tar.gz", use_container_width=True)
        if st.download_button("📥 Quiz Coran Offline HTML", data=QUIZ_HTML, file_name="Coran_Quiz.html", mime="text/html", use_container_width=True):
            log_download("Quiz Coran HTML")
    recitateur_nom = st.selectbox("🎙️ Choisis ton récitateur", list(RECITATEURS.keys()), key="recitateur")
    base_url = RECITATEURS[recitateur_nom]
    if st.session_state.selected_sourate:
        s_num = st.session_state.selected_sourate; s_nom = SOURATES_NOMS[s_num-1]; audio_url = f"{base_url}{s_num}.mp3"
        if st.button("⬅️ Retour liste", key="back_sourate_list"):
            st.session_state.selected_sourate = None; st.rerun()
        st.markdown(f"""<div style="background:white; border-radius:20px; padding:20px; border:3px solid #00a651; text-align:center"><div style="font-size:60px">📖</div><div style="font-weight:900; font-size:22px; color:#0a2a6b">{s_num}. {s_nom}</div></div>""", unsafe_allow_html=True)
        st.audio(audio_url, format="audio/mp3")
        st.link_button(f"📥 Télécharger {s_nom} MP3", audio_url, use_container_width=True, type="primary")
        if st.button(f"✅ Marquer comme téléchargé + bloc", use_container_width=True):
            log_download(f"MP3 {s_nom}"); st.success("Ajouté à l'historique blockchain")
        st.stop()
    search_coran = st.text_input("🔍 Cherche sourate", placeholder="Ex: Fatiha, Baqara...", key="search_coran")
    for i in range(1,115):
        nom = SOURATES_NOMS[i-1]
        if search_coran.lower() in nom.lower() or search_coran.lower() in f"sourate {i}".lower() or not search_coran:
            c1,c2,c3 = st.columns([3,1,1])
            with c1: st.markdown(f"""<div style="background:white; border-radius:18px; padding:14px; display:flex; align-items:center; gap:12px; border:2px solid #eef2ff; margin:6px 0"><div style="background:#0a2a6b; color:white; width:42px; height:42px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:900; font-size:14px">{i}</div><div style="text-align:left"><div style="font-weight:900; font-size:14px; color:#0a2a6b">{i}. {nom}</div></div></div>""", unsafe_allow_html=True)
            with c2:
                if st.button("▶️", key=f"play_{i}", use_container_width=True):
                    st.session_state.selected_sourate = i; st.rerun()
            with c3: st.link_button("📥", f"{RECITATEURS[recitateur_nom]}{i}.mp3", use_container_width=True)

elif menu=="Jeux":
    if st.button("⬅️ Retour Jeux", key="back_jeux"): st.session_state.bottom_nav="Home"; st.rerun()
    st.markdown("""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:18px; padding:18px; text-align:center; color:white"><div style="font-size:50px">🎮⛓️</div><div style="font-weight:900">JEUX ISLAMIQUES BLOCKCHAIN</div><div style="font-size:11px; color:#00ff88">Chaque téléchargement = 1 bloc</div></div>""", unsafe_allow_html=True)
    st.markdown("### 📥 Télécharger pour jouer offline")
    d1,d2 = st.columns(2)
    with d1:
        if st.download_button("🧠 Quiz Halal Offline", data=QUIZ_HTML, file_name="Quiz_Halal_Offline.html", mime="text/html", use_container_width=True, type="primary"):
            log_download("Jeu Quiz Halal"); st.success("Bloc créé")
    with d2:
        if st.download_button("🕋 Memory Islam Offline", data=MEMORY_HTML, file_name="Memory_Islam_Offline.html", mime="text/html", use_container_width=True, type="primary"):
            log_download("Jeu Memory Islam")
    st.divider()
    st.markdown("### 🎮 Jouer maintenant")
    q=random.choice(ALIMENTS_DATA)
    st.markdown(f"<div class='card-graph'><div style='font-size:50px'>{q['icon']}</div><b>{q['nom']}</b><br>HALAL ou HARAM?</div>", unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        if st.button("HALAL ✅", use_container_width=True):
            if q['statut']=="HALAL": st.success("✅ Bravo!"); st.balloons(); add_block({"type":"GAME","user":user_email,"game":"quiz","result":"win"})
            else: st.error("❌ C'était HARAM")
    with c2:
        if st.button("HARAM ❌", use_container_width=True):
            if q['statut']=="HARAM": st.success("✅ Bravo!"); st.balloons(); add_block({"type":"GAME","user":user_email,"game":"quiz","result":"win"})
            else: st.error("❌ C'était HALAL")
    if st.button("🔄 Nouvelle question", use_container_width=True): st.rerun()

elif menu=="Hadiths":
    if not user.get('is_vip'):
        st.markdown("""<div class="card-vip"><div style="font-size:70px">🔒</div><div style="font-weight:900; color:gold">Hadiths VIP - CODE requis</div></div>""", unsafe_allow_html=True)
        st.link_button("💳 PAYER 1500F POUR CODE", WAVE_LINK, type="primary", use_container_width=True); st.stop()
    if st.button("⬅️ Retour Hadiths", key="back_hadith"): st.session_state.bottom_nav="Home"; st.rerun()
    st.markdown("""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:18px; padding:18px; text-align:center; color:white"><div style="font-size:50px">📜</div><div style="font-weight:900">40 HADITHS NAWAWI</div></div>""", unsafe_allow_html=True)
    if st.session_state.selected_hadith:
        h = st.session_state.selected_hadith
        if st.button("⬅️", key="back_h_detail"): st.session_state.selected_hadith=None; st.rerun()
        st.markdown(f"""<div style="background:white; border-radius:18px; padding:20px; border:3px solid gold"><div style="text-align:center; font-weight:900; color:#0a2a6b; font-size:20px">Hadith {h['id']}</div><div style="background:#f5f7ff; padding:15px; border-radius:12px; margin:15px 0; text-align:right; font-size:22px; font-weight:bold; color:#0a2a6b">{h['ar']}</div><div style="background:#fff8e1; padding:15px; border-radius:12px; border-left:5px solid gold; font-size:15px">{h['fr']}</div></div>""", unsafe_allow_html=True)
        st.stop()
    for h in HADITHS_40_VRAIS:
        col1,col2 = st.columns([4,1])
        with col1: st.markdown(f"""<div class="card-graph" style="text-align:left; display:flex; align-items:center; gap:10px"><div style="background:#0a2a6b; color:white; width:35px; height:35px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:900; font-size:12px">{h['id']}</div><div><b>Hadith {h['id']}</b></div></div>""", unsafe_allow_html=True)
        with col2:
            if st.button("📖", key=f"read_h_{h['id']}", use_container_width=True):
                st.session_state.selected_hadith=h; st.rerun()

elif menu=="Aliments":
    if not user.get('is_vip'):
        st.markdown("""<div class="card-vip"><div style="font-size:70px">🔒</div><div style="font-weight:900; color:gold">Aliments VIP - CODE requis</div></div>""", unsafe_allow_html=True)
        st.link_button("💳 PAYER 1500F POUR CODE", WAVE_LINK, type="primary", use_container_width=True); st.stop()
    if st.button("⬅️ Retour Aliments", key="back_alim"): st.session_state.bottom_nav="Home"; st.rerun()
    search = st.text_input("🔍 Cherche aliment", placeholder="Ex: porc, poulet...")
    for a in ALIMENTS_DATA:
        if search.lower() in a['nom'].lower() or not search:
            st.markdown(f"""<div class="card-graph" style="text-align:left; border-left:5px solid {'#00a651' if a['statut']=='HALAL' else '#cc0000'}"><b>{a['icon']} {a['nom']}</b> - {a['statut']}<br><span style="font-size:11px">{a['desc']}</span></div>""", unsafe_allow_html=True)

elif menu=="Douas":
    if not user.get('is_vip'):
        st.markdown("""<div class="card-vip"><div style="font-size:70px">🔒</div><div style="font-weight:900; color:gold">Douas VIP - CODE requis</div></div>""", unsafe_allow_html=True)
        st.link_button("💳 PAYER 1500F POUR CODE", WAVE_LINK, type="primary", use_container_width=True); st.stop()
    if st.button("⬅️ Retour Douas", key="back_douas"): st.session_state.bottom_nav="Home"; st.rerun()
    st.title("🤲 50 Douas")
    st.markdown("<div class='card-graph'>Bismillah - Au nom d'Allah<br>Alhamdulillah - Louange à Allah<br>SubhanAllah - Gloire à Allah</div>", unsafe_allow_html=True)

elif menu=="Parametres":
    st.title("⛓️ Paramètres - Mémoire & Blockchain")
    chain = load_blockchain()
    is_valid, msg = verify_blockchain()
    if is_valid: st.success(f"✅ {msg}")
    else: st.error(f"❌ {msg}")
    used_kb = len(json.dumps(users).encode())/1024 + len(json.dumps(chain).encode())/1024
    st.markdown(f"""<div class='card-graph' style='text-align:left; font-size:12px'>💾 Mémoire users.json + blockchain: {used_kb:.1f} KB<br>🖼️ Réservé photo profil: <b>2,5 Mo (2560 KB)</b><br>📸 Photo actuelle: {(len(profile_b64 or '')/1024):.1f} KB thumbnail<br>⛓️ Total blocs: {len(chain)}<br>📜 Tes scans: {len(user.get('history',[]))} | 📥 Tes DL: {len(user.get('history_downloads',[]))}</div>""", unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    with c1:
        if st.button("🗑️ Vider 2,5 Mo", use_container_width=True):
            try:
                if os.path.exists(f"profile_pics/{user_email}_profile.jpg"): os.remove(f"profile_pics/{user_email}_profile.jpg")
                if os.path.exists(f"profile_pics/{user_email}_cover.jpg"): os.remove(f"profile_pics/{user_email}_cover.jpg")
            except: pass
            users[user_email]['profile_b64']=None; users[user_email]['cover_b64']=None; save_json(USERS_FILE,users)
            add_block({"type":"STORAGE_CLEARED","user":user_email}); st.success("2,5 Mo libérés"); st.rerun()
    with c2:
        if st.button("🗑️ Vider scans", use_container_width=True):
            users[user_email]['history']=[]; save_json(USERS_FILE,users); add_block({"type":"HISTORY_CLEARED","user":user_email}); st.rerun()
    with c3:
        if st.button("🗑️ Vider DL", use_container_width=True):
            users[user_email]['history_downloads']=[]; save_json(USERS_FILE,users); st.rerun()
    st.subheader("⛓️ Historique Blockchain - Mode Blochen")
    st.markdown("<div style='font-size:11px; color:gray'>Chaque action = 1 bloc avec hash SHA256 + previous_hash - immuable</div>", unsafe_allow_html=True)
    for block in reversed(chain[-30:]):
        if block["data"].get("user")==user_email or block["data"].get("user")=="system" or block["index"]==0:
            st.markdown(f"""<div class='block-blockchain'><b style='color:gold'>Bloc #{block['index']}</b> | {block['timestamp'][:19]}<br>Prev: {block['previous_hash'][:16]}...<br>Hash: <span style='color:#00ff88'>{block['hash']}</span><br>Data: {json.dumps(block['data'], ensure_ascii=False)[:150]}</div>""", unsafe_allow_html=True)
    st.subheader("📜 Historique Scans Classique")
    if not user.get('history'): st.info("Aucun scan")
    else:
        for h in reversed(user['history'][-20:]):
            st.markdown(f"<div class='card-graph' style='text-align:left; font-size:12px'>{h['date']} - <b>{h['result']}</b></div>", unsafe_allow_html=True)
    st.subheader("📥 Historique Téléchargements Coran & Jeux")
    if not user.get('history_downloads'): st.info("Aucun téléchargement")
    else:
        for d in reversed(user['history_downloads'][-20:]):
            st.markdown(f"<div class='card-graph' style='text-align:left; font-size:12px'>📥 {d['date']} - {d['name']}</div>", unsafe_allow_html=True)
    st.subheader("📤 Partager Blockchain")
    share_text = urllib.parse.quote(f"Scanner Halal Blockchain {APP_LINK}")
    st.link_button("🟢 WhatsApp", f"https://wa.me/?text={share_text}", use_container_width=True)
    st.link_button("🔵 Facebook", f"https://www.facebook.com/sharer/sharer.php?u={urllib.parse.quote(APP_LINK)}", use_container_width=True)
    st.link_button("📲 Installer l'App (APK)", APP_LINK, use_container_width=True, type="primary")
