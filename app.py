import streamlit as st
import json, os, random, re, base64, calendar, time, urllib.parse, io, hashlib, shutil
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

if os.path.exists("logo.png"):
    try:
        shutil.copyfile("logo.png", "static/logo.png")
    except:
        pass
logo_for_manifest = "/app/static/logo.png"
logo_exists_local = os.path.exists("static/logo.png") or os.path.exists("logo.png")

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
    {"src": "https://scanner-halal-mbcyfmxur68mw8n9zd72ul.streamlit.app/app/static/logo.png","sizes": "192x192","type": "image/png","purpose": "any maskable"},
    {"src": "https://scanner-halal-mbcyfmxur68mw8n9zd72ul.streamlit.app/app/static/logo.png","sizes": "512x512","type": "image/png","purpose": "any maskable"},
    {"src": "https://scanner-halal-mbcyfmxur68mw8n9zd72ul.streamlit.app/app/static/logo.png","sizes": "192x192","type": "image/png","purpose": "any"},
    {"src": "https://scanner-halal-mbcyfmxur68mw8n9zd72ul.streamlit.app/app/static/logo.png","sizes": "512x512","type": "image/png","purpose": "any"}
  ]
}
with open("static/manifest.json","w",encoding="utf-8") as f:
    json.dump(manifest,f,indent=2)

with open("static/sw.js","w") as f:
    f.write('self.addEventListener("install", e=>{e.waitUntil(caches.open("halal-v2").then(c=>c.addAll(["/"])))});self.addEventListener("fetch", e=>{e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request)))})')

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

# Fonction pour afficher logo en base64
def get_logo_b64():
    try:
        if os.path.exists("static/logo.png"):
            with open("static/logo.png","rb") as f:
                return base64.b64encode(f.read()).decode()
        elif os.path.exists("logo.png"):
            with open("logo.png","rb") as f:
                return base64.b64encode(f.read()).decode()
    except:
        return None
    return None

logo_b64 = get_logo_b64()
page_icon_path = "logo.png" if os.path.exists("logo.png") else "⛓️"
st.set_page_config(page_title="Scanner Halal Blockchain", page_icon=page_icon_path if os.path.exists("logo.png") else "⛓️", layout="centered")
st.markdown(f"""
<link rel="manifest" href="/app/static/manifest.json?v=3">
<meta name="theme-color" content="#0a2a6b">
<script>
// Supprime tous les anciens manifest de Streamlit
document.querySelectorAll('link[rel="manifest"]').forEach(el => {{
  if(el.getAttribute('href')!== '/app/static/manifest.json?v=3') {{
    el.remove();
  }}
}});
// Ajoute le bon manifest en force
var link = document.createElement('link');
link.rel = 'manifest';
link.href = '/app/static/manifest.json?v=3';
document.head.appendChild(link);

if ('serviceWorker' in navigator) {{
  navigator.serviceWorker.register('/app/static/sw.js?v=3');
}}
</script>
<style>
#MainMenu{{visibility:hidden}} footer{{visibility:hidden}} header{{visibility:hidden}}
.block-container{{padding-top:10px; padding-bottom:120px;}}
.card-graph{{background:white; border-radius:18px; padding:18px; text-align:center; border:2px solid #eef2ff; box-shadow:0 6px 15px rgba(0,0,0,0.07); margin:8px 0}}
.card-vip{{background:linear-gradient(135deg,#0a2a6b,#1a4bb8);color:white;padding:25px;border-radius:20px;margin:12px 0px; text-align:center}}
.block-blockchain{{background:#0a0a0a; color:#00ff88; border-radius:12px; padding:12px; font-family:monospace; font-size:11px; margin:6px 0; border-left:4px solid #00ff88; text-align:left}}
div[data-testid="stButton"] > button {{border-radius:18px!important; padding:18px!important; white-space:pre-line!important; box-shadow:0 6px 15px rgba(0,0,0,0.07)!important; border:2px solid #eef2ff!important; background:white!important; color:#0a2a6b!important; font-weight:800!important;}}
</style>
""", unsafe_allow_html=True)

for k in ['user','page','reset_code','scan_mode','bottom_nav','selected_menu','ad_watching','ad_start_time','selected_hadith','selected_aliment','selected_sourate','monetag_count']:
    if k not in st.session_state:
        st.session_state[k] = None if k not in ['page','bottom_nav','ad_watching','monetag_count'] else ("auth" if k=='page' else "Home" if k=='bottom_nav' else False if k=='ad_watching' else 0)

if st.session_state.page=="auth":
    # ====== ICI ON REMPLACE L'ICONE VERTE PAR LOGO ORANGE ======
    if logo_b64:
        st.markdown(f"""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:20px; padding:25px; text-align:center; color:white"><img src="data:image/png;base64,{logo_b64}" style="width:110px;height:110px;border-radius:20px;object-fit:cover;border:3px solid gold;box-shadow:0 4px 12px rgba(0,0,0,0.4)"><div style="font-size:24px; font-weight:900; margin-top:12px">SCANNER HALAL BLOCKCHAIN</div><div style="font-size:10px">2,5 Mo photo + Historique immuable + APK logo.png</div></div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:20px; padding:25px; text-align:center; color:white"><div style="font-size:24px; font-weight:900">SCANNER HALAL BLOCKCHAIN</div><div style="font-size:10px">2,5 Mo photo + Historique immuable + APK logo.png</div></div>""", unsafe_allow_html=True)
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
if 'profile_b
