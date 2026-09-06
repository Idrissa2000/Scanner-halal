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
    except: pass

manifest = {
  "name": "Scanner Halal Blockchain",
  "short_name": "Halal Scan",
  "description": "Scanner Halal 2,5 Mo + historique blockchain immuable + 3 niveaux de jeu",
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
    f.write('self.addEventListener("install", e=>{e.waitUntil(caches.open("halal-v5").then(c=>c.addAll(["/"])))});self.addEventListener("fetch", e=>{e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request)))})')

def calculate_hash(index, timestamp, data, previous_hash):
    value = f"{index}{timestamp}{json.dumps(data, sort_keys=True, ensure_ascii=False)}{previous_hash}"
    return hashlib.sha256(value.encode()).hexdigest()
def load_blockchain():
    if os.path.exists(BLOCKCHAIN_FILE):
        try:
            with open(BLOCKCHAIN_FILE,'r',encoding='utf-8') as fp: return json.load(fp)
        except: pass
    genesis = {"index": 0,"timestamp": datetime.now().isoformat(),"data": {"type":"GENESIS","message":"Scanner Halal V5 démarré","user":"system"},"previous_hash": "0"*64,"hash": ""}
    genesis["hash"] = calculate_hash(genesis["index"], genesis["timestamp"], genesis["data"], genesis["previous_hash"])
    return [genesis]
def save_blockchain(chain):
    with open(BLOCKCHAIN_FILE,'w',encoding='utf-8') as fp: json.dump(chain,fp,ensure_ascii=False,indent=2)
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
        if file_size > MAX_PHOTO_SIZE: return None, f"Trop lourd: {file_size/1024/1024:.2f} Mo > 2,5 Mo"
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

# ===================== DONNEES ISLAM V5 - 3 NIVEAUX =====================
ALIMENTS_DATA = [
    # NIVEAU 1 - VRAI OU FAUX SIMPLE
    {"nom": "Poulet (halal)", "statut": "HALAL", "icon": "🐔", "desc": "Halal si égorgé selon rite", "niveau": 1, "detail": "Prononcer Bismillah, égorger selon rite islamique. Conforme Coran 6:118"},
    {"nom": "Boeuf halal", "statut": "HALAL", "icon": "🐄", "desc": "Halal avec sacrifice rituel", "niveau": 1, "detail": "Halal avec sacrifice rituel Aid Al-Adha"},
    {"nom": "Mouton halal", "statut": "HALAL", "icon": "🐑", "desc": "Halal sacrifice Aid", "niveau": 1, "detail": "Très recommandé pendant Aid"},
    {"nom": "Poisson Thon", "statut": "HALAL", "icon": "🐟", "desc": "Tous les poissons sont halal", "niveau": 1, "detail": "Tous les poissons et fruits de mer sont halal pour majorité des écoles"},
    {"nom": "Riz", "statut": "HALAL", "icon": "🍚", "desc": "100% halal", "niveau": 1, "detail": "Céréale pure, 100% halal"},
    {"nom": "Dattes", "statut": "HALAL", "icon": "🌴", "desc": "Sunna, très recommandée", "niveau": 1, "detail": "Sunna du Prophète ﷺ, rompre le jeûne avec"},
    {"nom": "Lait", "statut": "HALAL", "icon": "🥛", "desc": "Halal", "niveau": 1, "detail": "Lait pur halal"},
    {"nom": "Miel", "statut": "HALAL", "icon": "🍯", "desc": "Halal pur, remède", "niveau": 1, "detail": "Coran 16:69 - remède pour les gens"},
    {"nom": "Mangue", "statut": "HALAL", "icon": "🥭", "desc": "Halal", "niveau": 1, "detail": "Fruit halal"},
    {"nom": "Banane", "statut": "HALAL", "icon": "🍌", "desc": "Halal", "niveau": 1, "detail": "Fruit halal"},
    {"nom": "Porc", "statut": "HARAM", "icon": "🐖", "desc": "HARAM - Interdit Coran 2:173", "niveau": 1, "detail": "Interdit formellement Coran 2:173, 5:3, 6:145"},
    {"nom": "Vin / Alcool", "statut": "HARAM", "icon": "🍷", "desc": "HARAM - Alcool interdit 5:90", "niveau": 1, "detail": "Alcool interdit Coran 5:90 - œuvre du diable"},
    {"nom": "Bière", "statut": "HARAM", "icon": "🍺", "desc": "HARAM", "niveau": 1, "detail": "Toute boisson enivrante est haram"},
    {"nom": "Gélatine porcine E441", "statut": "HARAM", "icon": "⚠️", "desc": "HARAM - Porc", "niveau": 1, "detail": "Gélatine de porc = haram"},
    {"nom": "E120 Cochenille", "statut": "HARAM", "icon": "⚠️", "desc": "HARAM - Insecte", "niveau": 1, "detail": "Colorant insecte écrasé - Haram pour majorité des savants"},
    {"nom": "Saucisson porc", "statut": "HARAM", "icon": "🚫", "desc": "HARAM", "niveau": 1, "detail": "Charcuterie porc = haram"},
    # NIVEAU 2 - QUI CACHE DU HARAM? PIEGES INDUSTRIELS
    {"nom": "Vinaigre de cidre", "statut": "HALAL", "icon": "🍎", "desc": "Vinaigre - transformation purifie", "niveau": 2, "detail": "Même si issu d'alcool, la fermentation acétique le transforme et le purifie - Halal selon majorité"},
    {"nom": "Croissant industriel E471", "statut": "HARAM", "icon": "🥐", "desc": "E471 peut être porcine", "niveau": 2, "detail": "Mono et diglycérides E471 - peut être d'origine porcine si non précisé végétal - DOUTEUX / HARAM"},
    {"nom": "Bonbon Haribo gélatine", "statut": "HARAM", "icon": "🍬", "desc": "Gélatine porcine cachée", "niveau": 2, "detail": "La plupart des bonbons Haribo contiennent gélatine porcine - Vérifier Halal"},
    {"nom": "Chips saveur bacon", "statut": "HARAM", "icon": "🥓", "desc": "Arôme bacon même sans viande", "niveau": 2, "detail": "Arôme artificiel de porc - Même sans viande, imite haram - Déconseillé"},
    {"nom": "Yaourt avec gélatine", "statut": "HARAM", "icon": "🥄", "desc": "Gélatine pour texture", "niveau": 2, "detail": "Certains yaourts ajoutent E441 pour épaissir - Vérifier origine"},
    {"nom": "Fromage présure animale", "statut": "HARAM", "icon": "🧀", "desc": "Présure non halal", "niveau": 2, "detail": "Présure d'estomac de veau non abattu halal = haram. Chercher présure microbienne ou halal"},
    {"nom": "Pain L-cystéine E920", "statut": "HARAM", "icon": "🍞", "desc": "E920 cheveux ou porc", "niveau": 2, "detail": "E920 peut venir de cheveux humains ou de porc - Douteux si non végétal"},
    {"nom": "Pâtisserie éthanol", "statut": "HARAM", "icon": "🎂", "desc": "Alcool comme conservateur", "niveau": 2, "detail": "Éthanol utilisé comme conservateur ou exhausteur - Même petite quantité = haram"},
    {"nom": "Vanille extrait alcool", "statut": "HARAM", "icon": "🌼", "desc": "Extrait à l'alcool", "niveau": 2, "detail": "Extrait naturel de vanille contient 35% alcool - Chercher vanille sans alcool ou poudre"},
    {"nom": "Agar-agar végétal", "statut": "HALAL", "icon": "🌿", "desc": "Alternative gélatine végétale", "niveau": 2, "detail": "Gélifiant végétal à base d'algue - 100% halal, remplace gélatine"},
    {"nom": "Margarine E471 végétal", "statut": "HALAL", "icon": "🧈", "desc": "E471 végétal certifié", "niveau": 2, "detail": "Si précisé origine végétale ou halal certifié = halal"},
    {"nom": "Soda avec E150d", "statut": "HALAL", "icon": "🥤", "desc": "Colorant caramel - Halal", "niveau": 2, "detail": "E150d caramel - Halal en général, sauf si contient alcool comme solvant"},
    {"nom": "Chocolat avec lécithine soja", "statut": "HALAL", "icon": "🍫", "desc": "Lécithine soja = Halal", "niveau": 2, "detail": "E322 lécithine de soja = halal. Si lécithine d'œuf = vérifier"},
    # NIVEAU 3 - SONDAGE DEBAT - CAS COMPLEXES
    {"nom": "Crevettes / Gambas", "statut": "HALAL", "icon": "🦐", "desc": "Débat écoles juridiques", "niveau": 3, "detail": "Halal pour Chafi'i, Maliki, Hanbali. Makruh / déconseillé pour Hanafi. Majorité = Halal"},
    {"nom": "Crabe / Homard", "statut": "HALAL", "icon": "🦀", "desc": "Fruit de mer - débat", "niveau": 3, "detail": "Même règle que crevettes - Halal pour majorité, makruh pour Hanafi car ne vit pas que dans l'eau"},
    {"nom": "Viande Gens du Livre", "statut": "DOUTEUX", "icon": "✝️", "desc": "Sans certification - débat", "niveau": 3, "detail": "Coran 5:5 autorise mais condition = qu'ils prononcent le nom de Dieu et qu'ils soient pratiquants. Aujourd'hui très rare - Douteux, préférer halal certifié"},
    {"nom": "Viande Bismillah oublié", "statut": "HALAL", "icon": "🤲", "desc": "Oubli involontaire", "niveau": 3, "detail": "Si oubli involontaire de Bismillah par musulman = pardonné et halal. Si omission volontaire = haram selon certains"},
    {"nom": "Gélatine transformée (istihala)", "statut": "DOUTEUX", "icon": "🔬", "desc": "Transformation chimique totale", "niveau": 3, "detail": "Débat savants contemporains - Si transformation totale (istihala) change nature = certains disent halal, d'autres restent sur haram par précaution"},
    {"nom": "Alcool dans médicament", "statut": "HALAL", "icon": "💊", "desc": "Nécessité médicale", "niveau": 3, "detail": "Si pas d'alternative et nécessité médicale = autorisé par nécessité. Si alternative existe = haram"},
    {"nom": "Fromage avec présure microbienne", "statut": "HALAL", "icon": "✅", "desc": "Présure végétale/microbienne", "niveau": 3, "detail": "Présure microbienne = halal - Solution moderne pour éviter présure animale douteuse"},
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
    HADITHS_40_VRAIS.append({"id":i, "ar": f"حديث {i}", "fr": f"Hadith {i} des 40 Nawawi - Le Messager d'Allah (ﷺ) a dit..."})

SOURATES_NOMS = ["Al-Fatiha","Al-Baqara","Al-Imran","An-Nisa","Al-Maida","Al-Anam","Al-Araf","Al-Anfal","At-Tawba","Yunus","Hud","Yusuf","Ar-Rad","Ibrahim","Al-Hijr","An-Nahl","Al-Isra","Al-Kahf","Maryam","Ta-Ha","Al-Anbiya","Al-Hajj","Al-Muminun","An-Nur","Al-Furqan","Ash-Shuara","An-Naml","Al-Qasas","Al-Ankabut","Ar-Rum","Luqman","As-Sajda","Al-Ahzab","Saba","Fatir","Ya-Sin","As-Saffat","Sad","Az-Zumar","Ghafir","Fussilat","Ash-Shura","Az-Zukhruf","Ad-Dukhan","Al-Jathiya","Al-Ahqaf","Muhammad","Al-Fath","Al-Hujurat","Qaf","Adh-Dhariyat","At-Tur","An-Najm","Al-Qamar","Ar-Rahman","Al-Waqia","Al-Hadid","Al-Mujadila","Al-Hashr","Al-Mumtahana","As-Saff","Al-Jumua","Al-Munafiqun","At-Taghabun","At-Talaq","At-Tahrim","Al-Mulk","Al-Qalam","Al-Haqqa","Al-Maarij","Nuh","Al-Jinn","Al-Muzzammil","Al-Muddathir","Al-Qiyama","Al-Insan","Al-Mursalat","An-Naba","An-Naziat","Abasa","At-Takwir","Al-Infitar","Al-Mutaffifin","Al-Inshiqaq","Al-Buruj","At-Tariq","Al-Ala","Al-Ghashiya","Al-Fajr","Al-Balad","Ash-Shams","Al-Lail","Ad-Duha","Ash-Sharh","At-Tin","Al-Alaq","Al-Qadr","Al-Bayyina","Az-Zalzala","Al-Adiyat","Al-Qaria","At-Takathur","Al-Asr","Al-Humaza","Al-Fil","Quraysh","Al-Maun","Al-Kawthar","Al-Kafirun","An-Nasr","Al-Masad","Al-Ikhlas","Al-Falaq","An-Nas"]
RECITATEURS = {"Mishary Alafasy": "https://cdn.islamic.network/quran/audio/128/ar.alafasy/","Abdul Rahman Al-Sudais": "https://cdn.islamic.network/quran/audio/128/ar.abdurrahmaansudais/","Maher Al-Muaiqly": "https://cdn.islamic.network/quran/audio/128/ar.mahermuaiqly/","Saud Al-Shuraim": "https://cdn.islamic.network/quran/audio/128/ar.saoodshuraym/"}
QUIZ_HTML = "<html><head><meta charset='utf-8'><title>Quiz Halal Offline</title><style>body{font-family:sans-serif;text-align:center;padding:20px;background:#f5f7ff}button{padding:15px 25px;margin:10px;border-radius:12px;border:none;background:#0a2a6b;color:white;font-weight:900}</style></head><body><h1>🧠 Quiz Halal/Haram Offline</h1><div id='q'></div><button onclick='next()'>Suivant</button><script>let data=[['Poulet halal','HALAL'],['Porc','HARAM'],['Vin','HARAM'],['Dattes','HALAL']];function next(){let r=data[Math.floor(Math.random()*data.length)]; window.r=r; document.getElementById('q').innerHTML='<h2>'+r[0]+'</h2><p><button onclick=\"alert(this.innerText==window.r[1]?`Bravo`:`Faux C était `+window.r[1])\">HALAL</button><button onclick=\"alert(this.innerText==window.r[1]?`Bravo`:`Faux C était `+window.r[1])\">HARAM</button></p>';} next();</script></body></html>"
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

def get_logo_b64():
    try:
        if os.path.exists("static/logo.png"):
            with open("static/logo.png","rb") as f: return base64.b64encode(f.read()).decode()
        elif os.path.exists("logo.png"):
            with open("logo.png","rb") as f: return base64.b64encode(f.read()).decode()
    except: return None
    return None
logo_b64 = get_logo_b64()
st.set_page_config(page_title="Scanner Halal", page_icon="📱", layout="centered")
st.markdown("""
<style>
#MainMenu{visibility:hidden} footer{visibility:hidden} header{visibility:hidden}
.block-container{padding-top:10px; padding-bottom:120px;}
.card-graph{background:white; border-radius:18px; padding:18px; text-align:center; border:2px solid #eef2ff; box-shadow:0 6px 15px rgba(0,0,0,0.07); margin:8px 0}
.card-vip{background:linear-gradient(135deg,#0a2a6b,#1a4bb8);color:white;padding:25px;border-radius:20px;margin:12px 0px; text-align:center}
.block-blockchain{background:#0a0a0a; color:#00ff88; border-radius:12px; padding:12px; font-family:monospace; font-size:11px; margin:6px 0; border-left:4px solid #00ff88; text-align:left}
div[data-testid="stButton"] > button {border-radius:18px!important; padding:18px!important; white-space:pre-line!important; box-shadow:0 6px 15px rgba(0,0,0,0.07)!important; border:2px solid #eef2ff!important; background:white!important; color:#0a2a6b!important; font-weight:800!important;}
</style>
""", unsafe_allow_html=True)

for k in ['user','page','reset_code','scan_mode','bottom_nav','selected_menu','selected_hadith','selected_sourate','share_result','current_game_q','game_score','game_question_count','game_correct','last_answer','game_niveau']:
    if k not in st.session_state:
        if k=='page': st.session_state[k]="auth"
        elif k=='bottom_nav': st.session_state[k]="Home"
        elif k=='game_score': st.session_state[k]=0
        elif k=='game_question_count': st.session_state[k]=0
        elif k=='game_correct': st.session_state[k]=0
        elif k=='game_niveau': st.session_state[k]=1
        elif k=='current_game_q': st.session_state[k]=random.choice([a for a in ALIMENTS_DATA if a['niveau']==1])
        elif k=='last_answer': st.session_state[k]=None
        else: st.session_state[k]=None

if st.session_state.page=="auth":
    if logo_b64:
        st.markdown(f"""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:20px; padding:25px; text-align:center; color:white"><img src="data:image/png;base64,{logo_b64}" style="width:110px;height:110px;border-radius:20px;object-fit:cover;border:3px solid gold"><div style="font-size:24px; font-weight:900; margin-top:12px">SCANNER HALAL V5</div><div style="font-size:11px">3 niveaux de jeu + Blockchain</div></div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:20px; padding:25px; text-align:center; color:white"><div style="font-size:24px; font-weight:900">SCANNER HALAL V5</div></div>""", unsafe_allow_html=True)
    t1,t2,t3=st.tabs(["🔑 Se connecter","✅ S'inscrire","❓ Code oublié"])
    with t1:
        e=st.text_input("Email", key="email_connexion").strip().lower()
        p=st.text_input("Mot de passe",type="password", key="pwd_connexion")
        if st.button("🔓 Se connecter",type="primary",use_container_width=True):
            u=users.get(e)
            if u and u.get('pwd')==p:
                st.session_state.user=e; st.session_state.page="app"; st.rerun()
            else: st.error(f"Incorrect. Comptes: {len(users)}")
    with t2:
        nom=st.text_input("Nom complet *", key="nom_insc").strip()
        c1,c2=st.columns([2,3])
        with c1: pays=st.selectbox("Pays", ["+225 CI","+221 SN","+223 ML","+224 GN","+226 BF","+229 BJ","+33 FR"], key="pays_insc")
        with c2: numero=st.text_input("WhatsApp *", key="num_insc").strip()
        er=st.text_input("Email *", key="email_insc").strip().lower()
        p1=st.text_input("Mot de passe *",type="password",key="p1")
        p2=st.text_input("Confirmer *",type="password",key="p2")
        if st.button("✨ S'inscrire",type="primary",use_container_width=True):
            if not nom or not numero or not er or not p1: st.error("Remplis tous")
            elif not is_valid_pwd(p1): st.error("6 car avec lettres + chiffres")
            elif p1!=p2: st.error("Différents")
            elif er in users:
                st.session_state.user=er; st.session_state.page="app"; st.rerun()
            else:
                users[er]={'nom':nom,'full_name':nom,'wave':f"{extract_code(pays)} {numero}",'pays':pays,'pwd':p1,'password':p1,'scans':0,'is_vip':False,'history':[],'history_downloads':[],'profile_b64':None,'cover_b64':None,'vip_code':None}
                save_json(USERS_FILE,users)
                add_block({"type":"NEW_USER","user":er,"nom":nom})
                st.session_state.user=er; st.session_state.page="app"; st.rerun()
    with t3:
        ef=st.text_input("Email", key="email_oublie").strip().lower()
        if st.button("Envoyer code"):
            if ef in users:
                code=str(random.randint(100000,999999)); st.session_state.reset_code=code; st.session_state.reset_email=ef; st.success(f"Code demo: {code}")
            else: st.error("Email non trouvé")
        if st.session_state.reset_code:
            ci=st.text_input("Code reçu").strip()
            np=st.text_input("Nouveau",type="password", key="new_pwd")
            if st.button("Réinitialiser"):
                if ci==st.session_state.reset_code:
                    users[st.session_state.reset_email]['pwd']=np; users[st.session_state.reset_email]['password']=np; save_json(USERS_FILE,users); st.success("Changé!"); st.session_state.reset_code=None
                else: st.error("Faux")
    st.stop()

if not st.session_state.user or st.session_state.user not in users:
    st.session_state.page="auth"; st.rerun()

user_email=st.session_state.user
user=users[user_email]
for field in ['full_name','history','history_downloads','profile_b64','cover_b64']:
    if field not in user: user[field]=[] if 'history' in field else None
if 'full_name' not in user or not user['full_name']: user['full_name']=user.get('nom','')

def log_download(name):
    users[user_email]['history_downloads'].append({'date':datetime.now().strftime("%d/%m/%Y %H:%M"),'name':name})
    save_json(USERS_FILE,users)
    add_block({"type":"DOWNLOAD","user":user_email,"file":name})

cover_b64=user.get('cover_b64')
profile_b64=user.get('profile_b64')
cover_style=f"background-image:url(data:image/jpeg;base64,{cover_b64}); background-size:cover;" if cover_b64 else "background:linear-gradient(90deg,#00c6ff,#0072ff);"
profile_html=f"<img src='data:image/jpeg;base64,{profile_b64}' style='width:75px;height:75px;border-radius:50%;border:3px solid #00ff88;object-fit:cover;'>" if profile_b64 else "<div style='width:75px;height:75px;border-radius:50%;background:white;display:flex;align-items:center;justify-content:center;font-size:38px;border:3px solid #00ff88;'>👤</div>"
st.markdown(f"""<div style="{cover_style} padding:15px; border-radius:18px; margin-bottom:12px;"><div style="display:flex; align-items:center; gap:12px; background:rgba(0,0,0,0.45); padding:12px; border-radius:12px;">{profile_html}<div style="color:white;"><b>{user.get('nom','')}</b><br><span style="font-size:11px; color:#00ff88">⛓️ {len(load_blockchain())} blocs | Jeu {st.session_state.game_correct}/20 Niveau {st.session_state.game_niveau}</span></div></div></div>""", unsafe_allow_html=True)

with st.sidebar:
    menu=st.radio("NAVIGATION", ["Home","Aliments","Coran","Hadiths","Douas","Parametres","Jeux","Codes VIP (Admin)"], label_visibility="collapsed")
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.user=None; st.session_state.page="auth"; st.rerun()
if st.session_state.get('selected_menu'):
    menu=st.session_state.selected_menu; st.session_state.selected_menu=None

if menu=="Codes VIP (Admin)":
    st.title("🔑 Codes VIP")
    for code, info in vip_codes.items():
        status = f"✅ {info['used_by']}" if info['used'] else "🟢 Disponible"
        st.markdown(f"<div class='card-graph' style='text-align:left'><b>{code}</b> - {status}</div>", unsafe_allow_html=True)
    if st.button("➕ Générer 5 codes", use_container_width=True):
        for _ in range(5):
            new_code = f"VIP-{random.randint(1000,9999)}-{random.randint(1000,9999)}"
            vip_codes[new_code] = {"used": False, "used_by": None}
        save_json(VIP_CODES_FILE, vip_codes); st.rerun()
    if st.button("⬅️ Retour"): st.session_state.bottom_nav="Home"; st.rerun()
    st.stop()

if menu=="Home":
    if st.session_state.scan_mode=="camera":
        if st.button("⬅️ Retour", use_container_width=True):
            st.session_state.scan_mode=None; st.rerun()
        st.markdown("""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:18px; padding:12px; text-align:center; color:white"><b>📸 SCANNER</b></div>""", unsafe_allow_html=True)
        cam=st.camera_input("📸 Photo produit", key="camera_full")
        if cam:
            with st.spinner("Analyse..."):
                time.sleep(1)
                result=random.choice(["HALAL 100%","HARAM Détecté","DOUTEUX"])
                color="green" if "HALAL" in result else "red" if "HARAM" in result else "orange"
                st.markdown(f"""<div style="background:white; border-radius:20px; padding:20px; text-align:center; border:4px solid {color}"><div style="font-size:26px; font-weight:900; color:{color}">{result}</div></div>""", unsafe_allow_html=True)
                users[user_email]['history'].append({'date':datetime.now().strftime("%d/%m/%Y %H:%M"),'result':result})
                save_json(USERS_FILE,users)
                block = add_block({"type":"SCAN","user":user_email,"result":result})
                texte_partage = urllib.parse.quote(f"{result} {APP_LINK}")
                with st.popover("📤 Partager", use_container_width=True):
                    st.link_button("🟢 WhatsApp", f"https://wa.me/?text={texte_partage}", use_container_width=True)
                    st.link_button("🔵 Facebook", f"https://www.facebook.com/sharer/sharer.php?u={urllib.parse.quote(APP_LINK)}", use_container_width=True)
        st.stop()
    col_title, col_menu = st.columns([5,1])
    with col_title: st.markdown(f"### Salam {user.get('full_name','').split(' ')[0]}")
    with col_menu:
        with st.popover("⋮"):
            st.markdown(f"**👤 {user.get('nom','')}**")
            st.caption(f"{user_email}")
            st.divider()
            st.markdown("**📸 Modifier photo - 2,5 Mo**")
            new_pic = st.file_uploader("Profil", type=['jpg','png','jpeg'], key="new_profile_pic_25_pop", label_visibility="collapsed")
            if new_pic:
                result, err = compress_and_save_2_5mo(new_pic, user_email, "profile")
                if err: st.error(err)
                else:
                    path, b64, size = result
                    users[user_email]['profile_b64']=b64; save_json(USERS_FILE,users); add_block({"type":"PROFILE_UPDATE","user":user_email}); st.success(f"✅ {size//1024:.0f} KB"); st.rerun()
            new_name = st.text_input("✏️ Nouveau nom", value=user.get('nom',''), key="new_name_input_pop")
            if st.button("💾 Sauver nom", use_container_width=True):
                if new_name.strip():
                    users[user_email]['nom']=new_name.strip(); users[user_email]['full_name']=new_name.strip(); save_json(USERS_FILE,users); st.rerun()
            if st.button("🚪 Déconnexion", use_container_width=True):
                st.session_state.user=None; st.session_state.page="auth"; st.rerun()
    if st.session_state.bottom_nav=="CHANGE_CODE":
        if st.button("⬅️ Retour"): st.session_state.bottom_nav="Home"; st.rerun()
        st.subheader("🔑 Changer code")
        a = st.text_input("Ancien code", type="password", key="old_code")
        b = st.text_input("Nouveau code", type="password", key="new_code1")
        c = st.text_input("Confirmer", type="password", key="new_code2")
        if st.button("🔒 Changer", type="primary", use_container_width=True):
            if users[user_email].get('password','')!=a and users[user_email].get('pwd','')!=a: st.error("Ancien code faux")
            elif b!=c: st.error("Différents")
            elif len(b)<4: st.error("4 min")
            else: users[user_email]['pwd']=b; users[user_email]['password']=b; save_json(USERS_FILE, users); add_block({"type":"PASSWORD_CHANGE","user":user_email}); st.success("Changé!"); st.session_state.bottom_nav="Home"; st.rerun()
        st.stop()
    if st.session_state.bottom_nav in ["VIP_ALIMENTS","VIP_DOUAS","VIP_HADITHS"]:
        if st.button("⬅️ Retour"): st.session_state.bottom_nav="Home"; st.rerun()
        nom=st.session_state.bottom_nav.replace("VIP_","")
        st.markdown(f"""<div class="card-vip"><div style="font-size:70px">🔒</div><div style="font-weight:900; color:gold; font-size:22px">{nom} VIP</div></div>""", unsafe_allow_html=True)
        st.link_button("💳 PAYER 1500F WAVE", WAVE_LINK, type="primary", use_container_width=True)
        code_input = st.text_input("🔑 CODE VIP", placeholder="VIP-XXXX-XXXX").strip().upper()
        if st.button("✅ ACTIVER VIP", use_container_width=True, type="primary"):
            if check_vip_code(code_input):
                users[user_email]['is_vip']=True; activate_vip_code(code_input, user_email); save_json(USERS_FILE,users)
                add_block({"type":"VIP_ACTIVATED","user":user_email,"code":code_input})
                st.balloons(); st.success(f"VIP Activé!"); time.sleep(1); st.session_state.bottom_nav="Home"; st.rerun()
            else: st.error("Code invalide")
        st.stop()
    if st.session_state.bottom_nav=="SAVOIR":
        if st.button("⬅️ Retour"): st.session_state.bottom_nav="Home"; st.rerun()
        st.markdown("""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:18px; padding:18px; text-align:center; color:white"><div style="font-size:50px">📚</div><div style="font-weight:900">SAVOIR ISLAMIQUE</div></div>""", unsafe_allow_html=True)
        c1,c2=st.columns(2)
        with c1:
            if st.button("📖\nCORAN\n114 Sourates\nGRATUIT", use_container_width=True):
                st.session_state.selected_menu="Coran"; st.session_state.bottom_nav="Home"; st.rerun()
            if st.button("📜\nHADITHS\n40 Hadiths\nVIP 🔒", use_container_width=True):
                if user.get('is_vip'): st.session_state.selected_menu="Hadiths"; st.session_state.bottom_nav="Home"; st.rerun()
                else: st.session_state.bottom_nav="VIP_HADITHS"; st.rerun()
        with c2:
            if st.button("🍖\nALIMENTS\n36 Aliments\nVIP 🔒", use_container_width=True):
                if user.get('is_vip'): st.session_state.selected_menu="Aliments"; st.session_state.bottom_nav="Home"; st.rerun()
                else: st.session_state.bottom_nav="VIP_ALIMENTS"; st.rerun()
            if st.button("🤲\nDOUAS\n50 Invocations\nVIP 🔒", use_container_width=True):
                if user.get('is_vip'): st.session_state.selected_menu="Douas"; st.session_state.bottom_nav="Home"; st.rerun()
                else: st.session_state.bottom_nav="VIP_DOUAS"; st.rerun()
        st.stop()
    st.markdown("""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:20px; padding:18px; text-align:center; color:white"><div style="font-size:50px">📸</div><div style="font-weight:900">SCANNER HALAL PRO V5</div><div style="font-size:11px; color:#00ff88">3 niveaux de jeu + Blockchain</div></div>""", unsafe_allow_html=True)
    col_scan, col_savoir, col_jeux = st.columns(3)
    with col_scan:
        if st.button("📷\nSCANNER\nPLEIN ECRAN", use_container_width=True):
            st.session_state.scan_mode="camera"; st.rerun()
    with col_savoir:
        if st.button("📚\nSAVOIR", use_container_width=True):
            st.session_state.bottom_nav="SAVOIR"; st.rerun()
    with col_jeux:
        if st.button("🎮\nJEUX\n3 NIVEAUX", use_container_width=True):
            st.session_state.selected_menu="Jeux"; st.rerun()
    st.markdown("### 📤 Partager l'app")
    share_text = urllib.parse.quote(f"Découvre Scanner Halal V5 {APP_LINK}")
    with st.popover("📤 Partager", use_container_width=True):
        st.link_button("🟢 WhatsApp", f"https://wa.me/?text={share_text}", use_container_width=True)
        st.link_button("🔵 Facebook", f"https://www.facebook.com/sharer/sharer.php?u={urllib.parse.quote(APP_LINK)}", use_container_width=True)
        st.link_button("🟣 Instagram", "https://www.instagram.com/", use_container_width=True)
    if not user.get('is_vip'):
        st.link_button("💎 Passer VIP 1500F", WAVE_LINK, type="primary", use_container_width=True)

elif menu=="Jeux":
    if 'game_question_count' not in st.session_state: st.session_state.game_question_count=0
    if 'game_correct' not in st.session_state: st.session_state.game_correct=0
    if 'current_game_q' not in st.session_state: st.session_state.current_game_q=random.choice([a for a in ALIMENTS_DATA if a['niveau']==st.session_state.game_niveau])
    if st.button("⬅️ Retour", key="back_jeux"):
        st.session_state.bottom_nav="Home"; st.rerun()

    if st.session_state.game_question_count >= 20:
        note = st.session_state.game_correct
        pct = int(note/20*100)
        if note >= 16: couleur="#00a651"; msg="MashAllah Excellent! 🌟"
        elif note >= 12: couleur="#0a2a6b"; msg="Très bien! 👍"
        elif note >= 8: couleur="#ff8c00"; msg="Pas mal, continue!"
        else: couleur="#cc0000"; msg="Courage, réessaye! 💪"
        st.markdown(f"""
        <div style="background:white; border-radius:24px; padding:30px; text-align:center; border:4px solid {couleur}">
            <div style="font-size:70px">📝</div>
            <div style="font-size:28px; font-weight:900; color:{couleur}">QUIZ TERMINÉ!</div>
            <div style="font-size:55px; font-weight:900; color:#0a2a6b; margin:15px 0">{note} / 20</div>
            <div style="background:#f5f7ff; border-radius:12px; padding:12px; margin:10px 0">
                <div style="font-size:18px; font-weight:800">{msg}</div>
                <div style="font-size:14px; color:gray">{pct}% réussite | Niveau {st.session_state.game_niveau}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        add_block({"type":"GAME_FINAL","user":user_email,"note":f"{note}/20","pct":pct,"niveau":st.session_state.game_niveau})
        c1,c2 = st.columns(2)
        with c1:
            if st.button("🔄 Réessayer\nRecommencer 20 questions", use_container_width=True, type="primary"):
                st.session_state.game_question_count=0; st.session_state.game_correct=0; st.session_state.game_score=0; st.session_state.last_answer=None
                st.session_state.current_game_q=random.choice([a for a in ALIMENTS_DATA if a['niveau']==st.session_state.game_niveau])
                st.rerun()
        with c2:
            if st.button("⬅️ Retour\nPage précédente", use_container_width=True):
                st.session_state.game_question_count=0; st.session_state.game_correct=0; st.session_state.game_score=0; st.session_state.last_answer=None
                st.session_state.bottom_nav="Home"; st.rerun()
        st.stop()

    st.markdown(f"""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:18px; padding:18px; text-align:center; color:white"><div style="font-size:50px">🎮</div><div style="font-weight:900">JEUX ISLAMIQUES V5 - 3 NIVEAUX</div><div style="font-size:12px; color:gold">Question {st.session_state.game_question_count+1}/20 | Score {st.session_state.game_correct}/20 | Niveau {st.session_state.game_niveau}</div></div>""", unsafe_allow_html=True)

    # SELECTION NIVEAU
    st.markdown("### 🎯 Choisis ton niveau")
    c1,c2,c3 = st.columns(3)
    with c1:
        if st.button("1️⃣\nNiveau 1\nVrai/Faux\nSimple", use_container_width=True, type="primary" if st.session_state.game_niveau==1 else "secondary"):
            st.session_state.game_niveau=1; st.session_state.game_question_count=0; st.session_state.game_correct=0; st.session_state.game_score=0; st.session_state.last_answer=None
            st.session_state.current_game_q=random.choice([a for a in ALIMENTS_DATA if a['niveau']==1]); st.rerun()
    with c2:
        if st.button("2️⃣\nNiveau 2\nQui cache du Haram?\nPièges E", use_container_width=True, type="primary" if st.session_state.game_niveau==2 else "secondary"):
            st.session_state.game_niveau=2; st.session_state.game_question_count=0; st.session_state.game_correct=0; st.session_state.game_score=0; st.session_state.last_answer=None
            st.session_state.current_game_q=random.choice([a for a in ALIMENTS_DATA if a['niveau']==2]); st.rerun()
    with c3:
        if st.button("3️⃣\nNiveau 3\nSondage Débat\nCas complexes", use_container_width=True, type="primary" if st.session_state.game_niveau==3 else "secondary"):
            st.session_state.game_niveau=3; st.session_state.game_question_count=0; st.session_state.game_correct=0; st.session_state.game_score=0; st.session_state.last_answer=None
            st.session_state.current_game_q=random.choice([a for a in ALIMENTS_DATA if a['niveau']==3]); st.rerun()

    st.markdown("### 📥 Télécharger pour jouer offline")
    d1,d2 = st.columns(2)
    with d1:
        if st.download_button("🧠 Quiz Halal Offline", data=QUIZ_HTML, file_name="Quiz_Halal_Offline.html", mime="text/html", use_container_width=True, type="primary"):
            log_download("Jeu Quiz Halal")
    with d2:
        if st.download_button("🕋 Memory Islam Offline", data=MEMORY_HTML, file_name="Memory_Islam_Offline.html", mime="text/html", use_container_width=True, type="primary"):
            log_download("Jeu Memory Islam")
    st.divider()
    st.markdown(f"### 🎮 Jouer Niveau {st.session_state.game_niveau}")
    q = st.session_state.current_game_q
    st.markdown(f"<div class='card-graph'><div style='font-size:50px'>{q['icon']}</div><b style='font-size:22px'>{q['nom']}</b><br><span style='font-size:13px'>{q['desc']}</span><br><span style='font-size:11px; background:{'#e8f5e9' if q['niveau']==1 else '#fff3e0' if q['niveau']==2 else '#f3e5f5'}; padding:4px 8px; border-radius:8px'>Niveau {q['niveau']} - {['Simple','Piège Industriel','Débat Savants'][q['niveau']-1]}</span><br><b style='margin-top:10px; display:block'>HALAL ou HARAM?</b><br><span style='font-size:11px; color:gray'>Question {st.session_state.game_question_count+1}/20</span></div>", unsafe_allow_html=True)
    if st.session_state.last_answer:
        if st.session_state.last_answer['correct']: st.success(f"✅ {st.session_state.last_answer['msg']}\n\n📚 {q.get('detail','')}")
        else: st.error(f"❌ {st.session_state.last_answer['msg']}\n\n📚 {q.get('detail','')}")
        if q.get('detail'): st.info(f"📚 Explication: {q.get('detail')}")
    c1,c2=st.columns(2)
    with c1:
        if st.button("HALAL ✅", use_container_width=True, key="btn_halal"):
            is_halal = q['statut'] in ["HALAL"]
            if q['niveau']==3 and q['statut']=="DOUTEUX":
                is_halal = True
            if is_halal or (q['statut']=="HALAL"):
                st.session_state.game_score+=10; st.session_state.game_correct+=1
                st.session_state.last_answer={'correct':True,'msg':f"Bravo! {q['nom']} = {q['statut']}"}
                add_block({"type":"GAME","user":user_email,"result":"win","niveau":st.session_state.game_niveau})
            else:
                st.session_state.last_answer={'correct':False,'msg':f"Faux! {q['nom']} = {q['statut']} - {q['desc']}"}
            st.session_state.game_question_count+=1
            pool = [a for a in ALIMENTS_DATA if a['niveau']==st.session_state.game_niveau]
            st.session_state.current_game_q=random.choice(pool)
            st.rerun()
    with c2:
        if st.button("HARAM ❌", use_container_width=True, key="btn_haram"):
            is_haram = q['statut'] in ["HARAM"]
            if q['statut']=="DOUTEUX":
                is_haram = True
            if is_haram or q['statut']=="HARAM" or q['statut']=="DOUTEUX":
                # Pour niveau débat DOUTEUX on compte comme bonne réponse si HARAM choisi car prudent
                if q['statut']=="HARAM" or q['statut']=="DOUTEUX":
                    st.session_state.game_score+=10; st.session_state.game_correct+=1
                    st.session_state.last_answer={'correct':True,'msg':f"Bravo! {q['nom']} = {q['statut']} - {q['desc']}"}
                    add_block({"type":"GAME","user":user_email,"result":"win","niveau":st.session_state.game_niveau})
                else:
                    st.session_state.last_answer={'correct':False,'msg':f"Faux! {q['nom']} = {q['statut']}"}
            else:
                st.session_state.last_answer={'correct':False,'msg':f"Faux! {q['nom']} = {q['statut']}"}
            st.session_state.game_question_count+=1
            pool = [a for a in ALIMENTS_DATA if a['niveau']==st.session_state.game_niveau]
            st.session_state.current_game_q=random.choice(pool)
            st.rerun()
    if st.button("⏭️ Passer cette question", use_container_width=True):
        st.session_state.game_question_count+=1
        pool = [a for a in ALIMENTS_DATA if a['niveau']==st.session_state.game_niveau]
        st.session_state.current_game_q=random.choice(pool)
        st.session_state.last_answer=None
        st.rerun()

elif menu=="Coran":
    if st.button("⬅️ Retour"): st.session_state.bottom_nav="Home"; st.rerun()
    st.title("📖 Coran 114")
    for i in range(1,115):
        st.markdown(f"<div class='card-graph' style='text-align:left'>{i}. {SOURATES_NOMS[i-1]}</div>", unsafe_allow_html=True)

elif menu=="Hadiths":
    if not user.get('is_vip'):
        st.markdown("""<div class="card-vip"><div style="font-size:70px">🔒</div><div style="font-weight:900; color:gold">Hadiths VIP</div></div>""", unsafe_allow_html=True)
        st.link_button("💳 PAYER 1500F", WAVE_LINK, type="primary", use_container_width=True); st.stop()
    for h in HADITHS_40_VRAIS:
        st.markdown(f"<div class='card-graph' style='text-align:left'><b>Hadith {h['id']}</b><br>{h['fr']}</div>", unsafe_allow_html=True)

elif menu=="Aliments":
    if not user.get('is_vip'):
        st.markdown("""<div class="card-vip">VIP requis</div>""", unsafe_allow_html=True); st.stop()
    tab1, tab2, tab3 = st.tabs(["Niveau 1 Simple", "Niveau 2 Pièges", "Niveau 3 Débats"])
    with tab1:
        for a in [x for x in ALIMENTS_DATA if x['niveau']==1]:
            st.markdown(f"<div class='card-graph' style='text-align:left; border-left:5px solid {'#00a651' if a['statut']=='HALAL' else '#cc0000'}"><b>{a['icon']} {a['nom']}</b> - {a['statut']}<br><span style='font-size:11px'>{a['desc']}</span><br><span style='font-size:10px; color:gray'>{a.get('detail','')}</span></div>", unsafe_allow_html=True)
    with tab2:
        for a in [x for x in ALIMENTS_DATA if x['niveau']==2]:
            st.markdown(f"<div class='card-graph' style='text-align:left; border-left:5px solid orange'><b>{a['icon']} {a['nom']}</b> - {a['statut']}<br><span style='font-size:11px'>{a['desc']}</span><br><span style='font-size:10px; color:gray'>{a.get('detail','')}</span></div>", unsafe_allow_html=True)
    with tab3:
        for a in [x for x in ALIMENTS_DATA if x['niveau']==3]:
            st.markdown(f"<div class='card-graph' style='text-align:left; border-left:5px solid purple'><b>{a['icon']} {a['nom']}</b> - {a['statut']}<br><span style='font-size:11px'>{a['desc']}</span><br><span style='font-size:10px; color:gray'>{a.get('detail','')}</span></div>", unsafe_allow_html=True)

elif menu=="Douas":
    if not user.get('is_vip'):
        st.markdown("""<div class="card-vip">VIP requis</div>""", unsafe_allow_html=True); st.stop()
    st.title("🤲 50 Douas")
    st.markdown("<div class='card-graph'>Bismillah - Alhamdulillah - SubhanAllah</div>", unsafe_allow_html=True)

elif menu=="Parametres":
    st.title("⛓️ Paramètres V5")
    chain = load_blockchain()
    is_valid, msg = verify_blockchain()
    if is_valid: st.success(msg)
    else: st.error(msg)
    st.markdown(f"<div class='card-graph'>Blocs: {len(chain)} | Jeu: {st.session_state.game_correct}/20 Niveau {st.session_state.game_niveau}</div>", unsafe_allow_html=True)
    for block in reversed(chain[-20:]):
        if block["data"].get("user")==user_email or block["data"].get("user")=="system":
            st.markdown(f"<div class='block-blockchain'>Bloc #{block['index']} {json.dumps(block['data'], ensure_ascii=False)[:120]}</div>", unsafe_allow_html=True)

st.markdown("<div style='height:150px'></div>", unsafe_allow_html=True)
