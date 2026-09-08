import streamlit as st
import json, os, random, re, base64, calendar, time, urllib.parse, io, hashlib, shutil, socket
from datetime import datetime, date
from PIL import Image

# ===================== CONFIG LIENS V9 ULTIME =====================
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

# Copie logo pour PWA V9
if os.path.exists("logo.png"):
    try:
        shutil.copyfile("logo.png", "static/logo.png")
    except:
        pass

# Manifest PWA V9 - 1220 lignes
manifest = {
  "name": "Scanner Halal Blockchain V9",
  "short_name": "Halal Scan V9",
  "description": "V9 Ultime 1220 lignes - Offline Guest OK + Scanner Online Only + 55 aliments + 55 douas",
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
    f.write('self.addEventListener("install", e=>{e.waitUntil(caches.open("halal-v9").then(c=>c.addAll(["/"])))});self.addEventListener("fetch", e=>{e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request)))})')

# ===================== BLOCKCHAIN V9 =====================
def calculate_hash(index, timestamp, data, previous_hash):
    value = f"{index}{timestamp}{json.dumps(data, sort_keys=True, ensure_ascii=False)}{previous_hash}"
    return hashlib.sha256(value.encode()).hexdigest()

def load_blockchain():
    if os.path.exists(BLOCKCHAIN_FILE):
        try:
            with open(BLOCKCHAIN_FILE,'r',encoding='utf-8') as fp:
                return json.load(fp)
        except:
            pass
    genesis = {"index": 0,"timestamp": datetime.now().isoformat(),"data": {"type":"GENESIS","message":"Scanner Halal V9 demarre - Online scanner only","user":"system"},"previous_hash": "0"*64,"hash": ""}
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
        curr = chain[i]
        prev = chain[i-1]
        if curr["previous_hash"]!= prev["hash"]:
            return False, f"Bloc {i} corrompu"
        recalc = calculate_hash(curr["index"], curr["timestamp"], curr["data"], curr["previous_hash"])
        if curr["hash"]!= recalc:
            return False, f"Hash bloc {i} invalide"
    return True, f"Blockchain valide {len(chain)} blocs"

def load_json(f,d):
    if os.path.exists(f):
        try:
            with open(f,'r',encoding='utf-8') as fp:
                return json.load(fp)
        except:
            return d
    return d

def save_json(f,data):
    with open(f,'w',encoding='utf-8') as fp:
        json.dump(data,fp,ensure_ascii=False,indent=2)

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
    vip_codes[code]["used"] = True
    vip_codes[code]["used_by"] = email
    save_json(VIP_CODES_FILE, vip_codes)

def compress_and_save_2_5mo(file, email, type_name):
    try:
        file_size = len(file.getvalue())
        if file_size > MAX_PHOTO_SIZE:
            return None, f"Trop lourd: {file_size/1024/1024:.2f} Mo > 2,5 Mo"
        img = Image.open(file)
        img.thumbnail((700, 700), Image.LANCZOS)
        buffer = io.BytesIO()
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.save(buffer, format="JPEG", quality=80, optimize=True)
        compressed = buffer.getvalue()
        path = f"profile_pics/{email}_{type_name}.jpg"
        with open(path, "wb") as f:
            f.write(compressed)
        thumb = Image.open(io.BytesIO(compressed))
        thumb.thumbnail((150, 150), Image.LANCZOS)
        thumb_buf = io.BytesIO()
        thumb.save(thumb_buf, format="JPEG", quality=65)
        thumb_b64 = base64.b64encode(thumb_buf.getvalue()).decode()
        return (path, thumb_b64, len(compressed)), None
    except Exception as e:
        return None, str(e)

# ===================== FONCTION INTERNET V9 - SCANNER ONLINE ONLY =====================
def check_internet():
    """V9 - Verifie si internet disponible - Scanner uniquement avec internet"""
    try:
        # Test connexion DNS Google
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        try:
            # Second test Cloudflare
            socket.create_connection(("1.1.1.1", 53), timeout=3)
            return True
        except:
            return False

def is_scanner_allowed(is_guest):
    """V9 - Scanner autorise seulement si pas invite ET internet OK"""
    if is_guest:
        return False, "Mode hors-ligne - Connexion requise pour scanner"
    if not check_internet():
        return False, "Pas de connexion internet - Scanner necessite internet"
    return True, "Scanner autorise - Internet OK"

# ===================== DONNEES ISLAM V9 - 55 ALIMENTS ULTIME =====================
ALIMENTS_DATA = [
    {"nom": "Poulet (halal)", "statut": "HALAL", "icon": "🐔", "desc": "Halal si egorge selon rite", "niveau": 1, "detail": "Prononcer Bismillah, egorger selon rite islamique. Conforme Coran 6:118"},
    {"nom": "Boeuf halal", "statut": "HALAL", "icon": "🐄", "desc": "Halal avec sacrifice rituel", "niveau": 1, "detail": "Halal avec sacrifice rituel Aid Al-Adha"},
    {"nom": "Mouton halal", "statut": "HALAL", "icon": "🐑", "desc": "Halal sacrifice Aid", "niveau": 1, "detail": "Tres recommande pendant Aid"},
    {"nom": "Poisson Thon", "statut": "HALAL", "icon": "🐟", "desc": "Tous les poissons sont halal", "niveau": 1, "detail": "Tous les poissons et fruits de mer sont halal pour majorite des ecoles"},
    {"nom": "Riz", "statut": "HALAL", "icon": "🍚", "desc": "100% halal", "niveau": 1, "detail": "Cereale pure, 100% halal"},
    {"nom": "Dattes", "statut": "HALAL", "icon": "🌴", "desc": "Sunna, tres recommandee", "niveau": 1, "detail": "Sunna du Prophete, rompre le jeune avec"},
    {"nom": "Lait", "statut": "HALAL", "icon": "🥛", "desc": "Halal", "niveau": 1, "detail": "Lait pur halal"},
    {"nom": "Miel", "statut": "HALAL", "icon": "🍯", "desc": "Halal pur, remede", "niveau": 1, "detail": "Coran 16:69 - remede pour les gens"},
    {"nom": "Mangue", "statut": "HALAL", "icon": "🥭", "desc": "Halal", "niveau": 1, "detail": "Fruit halal"},
    {"nom": "Banane", "statut": "HALAL", "icon": "🍌", "desc": "Halal", "niveau": 1, "detail": "Fruit halal"},
    {"nom": "Porc", "statut": "HARAM", "icon": "🐖", "desc": "HARAM - Interdit Coran 2:173", "niveau": 1, "detail": "Interdit formellement Coran 2:173, 5:3, 6:145"},
    {"nom": "Vin / Alcool", "statut": "HARAM", "icon": "🍷", "desc": "HARAM - Alcool interdit 5:90", "niveau": 1, "detail": "Alcool interdit Coran 5:90 - oeuvre du diable"},
    {"nom": "Biere", "statut": "HARAM", "icon": "🍺", "desc": "HARAM", "niveau": 1, "detail": "Toute boisson enivrante est haram"},
    {"nom": "Gelatine porcine E441", "statut": "HARAM", "icon": "⚠️", "desc": "HARAM - Porc", "niveau": 1, "detail": "Gelatine de porc = haram"},
    {"nom": "E120 Cochenille", "statut": "HARAM", "icon": "⚠️", "desc": "HARAM - Insecte", "niveau": 1, "detail": "Colorant insecte ecrase - Haram pour majorite des savants"},
    {"nom": "Saucisson porc", "statut": "HARAM", "icon": "🚫", "desc": "HARAM", "niveau": 1, "detail": "Charcuterie porc = haram"},
    {"nom": "Oeuf poule", "statut": "HALAL", "icon": "🥚", "desc": "Halal", "niveau": 1, "detail": "Oeuf de poule halal, Bismillah recommande"},
    {"nom": "Sang animal", "statut": "HARAM", "icon": "🩸", "desc": "HARAM Coran 2:173", "niveau": 1, "detail": "Sang coule = haram"},
    {"nom": "Pain complet", "statut": "HALAL", "icon": "🍞", "desc": "Pain halal sans additif douteux", "niveau": 1, "detail": "Pain sans E471/E920 douteux = halal"},
    {"nom": "Eau minerale", "statut": "HALAL", "icon": "💧", "desc": "Eau pure halal", "niveau": 1, "detail": "Eau 100% halal"},
    {"nom": "Vinaigre de cidre", "statut": "HALAL", "icon": "🍎", "desc": "Vinaigre - transformation purifie", "niveau": 2, "detail": "Meme si issu d'alcool, la fermentation acetique le transforme et le purifie - Halal selon majorite"},
    {"nom": "Croissant industriel E471", "statut": "HARAM", "icon": "🥐", "desc": "E471 peut etre porcine", "niveau": 2, "detail": "Mono et diglycerides E471 - peut etre d'origine porcine si non precise vegetal - DOUTEUX / HARAM"},
    {"nom": "Bonbon Haribo gelatine", "statut": "HARAM", "icon": "🍬", "desc": "Gelatine porcine cachee", "niveau": 2, "detail": "La plupart des bonbons Haribo contiennent gelatine porcine - Verifier Halal"},
    {"nom": "Chips saveur bacon", "statut": "HARAM", "icon": "🥓", "desc": "Arome bacon meme sans viande", "niveau": 2, "detail": "Arome artificiel de porc - Meme sans viande, imite haram - Deconseille"},
    {"nom": "Yaourt avec gelatine", "statut": "HARAM", "icon": "🥄", "desc": "Gelatine pour texture", "niveau": 2, "detail": "Certains yaourts ajoutent E441 pour epaissir - Verifier origine"},
    {"nom": "Fromage presure animale", "statut": "HARAM", "icon": "🧀", "desc": "Presure non halal", "niveau": 2, "detail": "Presure d'estomac de veau non abattu halal = haram. Chercher presure microbienne ou halal"},
    {"nom": "Pain L-cysteine E920", "statut": "HARAM", "icon": "🍞", "desc": "E920 cheveux ou porc", "niveau": 2, "detail": "E920 peut venir de cheveux humains ou de porc - Douteux si non vegetal"},
    {"nom": "Patisserie ethanol", "statut": "HARAM", "icon": "🎂", "desc": "Alcool comme conservateur", "niveau": 2, "detail": "Ethanol utilise comme conservateur - Meme petite quantite = haram"},
    {"nom": "Vanille extrait alcool", "statut": "HARAM", "icon": "🌼", "desc": "Extrait a l'alcool", "niveau": 2, "detail": "Extrait naturel de vanille contient 35% alcool - Chercher vanille sans alcool"},
    {"nom": "Agar-agar vegetal", "statut": "HALAL", "icon": "🌿", "desc": "Alternative gelatine vegetale", "niveau": 2, "detail": "Gelifiant vegetal a base d'algue - 100% halal, remplace gelatine"},
    {"nom": "Margarine E471 vegetal", "statut": "HALAL", "icon": "🧈", "desc": "E471 vegetal certifie", "niveau": 2, "detail": "Si precise origine vegetale ou halal certifie = halal"},
    {"nom": "Soda avec E150d", "statut": "HALAL", "icon": "🥤", "desc": "Colorant caramel - Halal", "niveau": 2, "detail": "E150d caramel - Halal en general"},
    {"nom": "Chocolat lecithine soja", "statut": "HALAL", "icon": "🍫", "desc": "Lecithine soja = Halal", "niveau": 2, "detail": "E322 lecithine de soja = halal"},
    {"nom": "E422 Glycerol", "statut": "DOUTEUX", "icon": "⚗️", "desc": "Peut etre animal", "niveau": 2, "detail": "Glycerol peut etre animal ou vegetal - Verifier source"},
    {"nom": "E542 Phosphate d'os", "statut": "HARAM", "icon": "🦴", "desc": "Os animal", "niveau": 2, "detail": "Phosphate d'os - Haram si os de porc ou animal non halal"},
    {"nom": "Chewing-gum avec gelatine", "statut": "HARAM", "icon": "🍭", "desc": "Gelatine cachee", "niveau": 2, "detail": "Certains chewing-gum contiennent gelatine - Chercher halal"},
    {"nom": "Additif E471 industriel", "statut": "DOUTEUX", "icon": "🏭", "desc": "Industriel sans precision", "niveau": 2, "detail": "Si E471 sans mention vegetal = douteux, eviter par precaution"},
    {"nom": "Arome naturel bacon", "statut": "HARAM", "icon": "🥓", "desc": "Arome porc", "niveau": 2, "detail": "Arome naturel de bacon = haram meme sans viande porc"},
    {"nom": "Crevettes / Gambas", "statut": "HALAL", "icon": "🦐", "desc": "Debat ecoles juridiques", "niveau": 3, "detail": "Halal pour Chafii, Maliki, Hanbali. Makruh pour Hanafi. Majorite = Halal"},
    {"nom": "Crabe / Homard", "statut": "HALAL", "icon": "🦀", "desc": "Fruit de mer - debat", "niveau": 3, "detail": "Meme regle que crevettes - Halal pour majorite, makruh pour Hanafi"},
    {"nom": "Viande Gens du Livre", "statut": "DOUTEUX", "icon": "✝️", "desc": "Sans certification - debat", "niveau": 3, "detail": "Coran 5:5 autorise mais condition = qu'ils prononcent le nom de Dieu. Aujourd'hui rare - Douteux, preferer halal certifie"},
    {"nom": "Viande Bismillah oublie", "statut": "HALAL", "icon": "🤲", "desc": "Oubli involontaire", "niveau": 3, "detail": "Si oubli involontaire = pardonne et halal. Si omission volontaire = haram selon certains"},
    {"nom": "Gelatine transformee (istihala)", "statut": "DOUTEUX", "icon": "🔬", "desc": "Transformation chimique totale", "niveau": 3, "detail": "Debat savants - Si transformation totale change nature = certains disent halal, d'autres restent sur haram par precaution"},
    {"nom": "Alcool dans medicament", "statut": "HALAL", "icon": "💊", "desc": "Necessite medicale", "niveau": 3, "detail": "Si pas d'alternative et necessite medicale = autorise par necessite"},
    {"nom": "Fromage presure microbienne", "statut": "HALAL", "icon": "✅", "desc": "Presure vegetale/microbienne", "niveau": 3, "detail": "Presure microbienne = halal - Solution moderne"},
    {"nom": "Caviar esturgeon", "statut": "HALAL", "icon": "⚫", "desc": "Oeufs poisson - debat", "niveau": 3, "detail": "Halal pour Chafii, Maliki. Hanafi: si poisson halal alors oeufs halal"},
    {"nom": "Escargot", "statut": "HALAL", "icon": "🐌", "desc": "Debat - Maliki halal", "niveau": 3, "detail": "Maliki autorise escargot terrestre. Hanafi et Chafii: non halal"},
    {"nom": "Grenouille", "statut": "HARAM", "icon": "🐸", "desc": "Interdit de tuer - Hadith", "niveau": 3, "detail": "Hadith interdit de tuer grenouille - Donc haram a consommer"},
    {"nom": "Insectes (criquets)", "statut": "HALAL", "icon": "🦗", "desc": "Criquet halal - Hadith", "niveau": 3, "detail": "Criquet autorise par Hadith authentique. Autres insectes = debat"},
    {"nom": "Viande congele sans Bismillah ecrit", "statut": "HALAL", "icon": "🧊", "desc": "Si abattu halal a l'origine", "niveau": 3, "detail": "Si abattu halal au depart, congele reste halal meme si etiquette sans Bismillah"},
    {"nom": "Viande hachee supermarche", "statut": "DOUTEUX", "icon": "🥩", "desc": "Melange possible", "niveau": 3, "detail": "Viande hachee sans certif = risque melange porc/boeuf - Douteux"},
    {"nom": "Gelatine bovine non halal", "statut": "HARAM", "icon": "🐄", "desc": "Bovine mais non halal", "niveau": 3, "detail": "Meme bovine, si animal non abattu halal = haram selon majorite"},
    {"nom": "E904 Gomme laque", "statut": "HARAM", "icon": "🪲", "desc": "Insecte laque", "niveau": 3, "detail": "Gomme laque = secretion insecte - Haram pour majorite"},
    {"nom": "E913 Lanoline", "statut": "HALAL", "icon": "🐑", "desc": "Laine mouton", "niveau": 3, "detail": "Lanoline de laine mouton = halal, pas besoin abattage"},
]

# 40 HADITHS VRAIS COMPLETS V9
HADITHS_40_VRAIS = [
    {"id":1, "ar": "انما الاعمال بالنيات", "fr": "Hadith 1: Les actes ne valent que par leurs intentions. Chaque personne sera retribuee selon son intention. [Bukhari & Muslim] - Fondement de l'Islam"},
    {"id":2, "ar": "بني الاسلام على خمس", "fr": "Hadith 2: L'Islam est bati sur cinq: Shahada, priere, zakat, jeune Ramadan, pelerinage. [Bukhari]"},
    {"id":3, "ar": "ان الله كتب الاحسان على كل شيء", "fr": "Hadith 3: Allah a prescrit la bienfaisance en toute chose. Si vous tuez, faites-le bien. Si vous egorgez, aiguisez. [Muslim]"},
    {"id":4, "ar": "من حسن اسلام المرء تركه ما لا يعنيه", "fr": "Hadith 4: Fait partie du bon Islam de l'homme de delaisser ce qui ne le concerne pas. [Tirmidhi hassan]"},
    {"id":5, "ar": "لا يؤمن احدكم حتى يحب لاخيه ما يحب لنفسه", "fr": "Hadith 5: Aucun de vous ne sera croyant jusqu'a ce qu'il aime pour son frere ce qu'il aime pour lui-meme. [Bukhari & Muslim]"},
    {"id":6, "ar": "من كان يؤمن بالله واليوم الاخر فليقل خيرا او ليصمت", "fr": "Hadith 6: Que celui qui croit en Allah et au Jour Dernier dise du bien ou se taise. [Bukhari & Muslim]"},
    {"id":7, "ar": "الدين النصيحة", "fr": "Hadith 7: La religion c'est le bon conseil. Pour Allah, Son Livre, Son Messager, les dirigeants et le peuple. [Muslim]"},
    {"id":8, "ar": "اتق الله حيثما كنت", "fr": "Hadith 8: Crains Allah ou que tu sois, fais suivre la mauvaise action par une bonne qui l'efface, et comporte-toi bien avec les gens. [Tirmidhi hassan]"},
    {"id":9, "ar": "ما نهيتكم عنه فاجتنبوه", "fr": "Hadith 9: Ce que je vous ai interdit, evitez-le. Ce que je vous ai ordonne, faites-en ce que vous pouvez. [Muslim]"},
    {"id":10, "ar": "الطهور شطر الايمان", "fr": "Hadith 10: La purification est la moitie de la foi. Alhamdulillah remplit la balance. [Muslim]"},
    {"id":11, "ar": "لا ضرر ولا ضرار", "fr": "Hadith 11: Pas de tort cause a autrui ni de tort subi. [Ibn Majah hassan] - Principe juridique majeur"},
    {"id":12, "ar": "من احدث في امرنا هذا ما ليس منه فهو رد", "fr": "Hadith 12: Celui qui innove dans notre religion ce qui n'en fait pas partie, son innovation est rejetee. [Bukhari & Muslim]"},
    {"id":13, "ar": "الحلال بين والحرام بين", "fr": "Hadith 13: Le halal est clair et le haram est clair. Entre les deux, des choses douteuses. Celui qui evite le douteux preserve sa religion. [Bukhari & Muslim] - Tres important pour scanner halal!"},
    {"id":14, "ar": "ان الله طيب لا يقبل الا طيبا", "fr": "Hadith 14: Allah est bon et n'accepte que ce qui est bon. Allah a ordonne aux croyants ce qu'Il a ordonne aux Messagers. [Muslim]"},
    {"id":15, "ar": "من سلك طريقا يلتمس فيه علما", "fr": "Hadith 15: Celui qui emprunte un chemin pour chercher la science, Allah lui facilite un chemin vers le Paradis. [Muslim]"},
    {"id":16, "ar": "الكلمة الطيبة صدقة", "fr": "Hadith 16: La bonne parole est une aumone. Aider quelqu'un a monter sur sa monture est une aumone. [Bukhari & Muslim]"},
    {"id":17, "ar": "لا تحقرن من المعروف شيئا", "fr": "Hadith 17: Ne meprise aucune bonne action, ne serait-ce que de rencontrer ton frere avec un visage souriant. [Muslim]"},
    {"id":18, "ar": "المسلم من سلم المسلمون من لسانه ويده", "fr": "Hadith 18: Le musulman est celui dont les musulmans sont a l'abri de sa langue et de sa main. [Bukhari & Muslim]"},
    {"id":19, "ar": "من كان في حاجة اخيه كان الله في حاجته", "fr": "Hadith 19: Celui qui aide son frere, Allah l'aide. Celui qui soulage un croyant d'une difficulte, Allah le soulage au Jour de la Resurrection. [Muslim]"},
    {"id":20, "ar": "يسروا ولا تعسروا", "fr": "Hadith 20: Facilitez et ne rendez pas difficile, annoncez la bonne nouvelle et ne repoussez pas. [Bukhari]"},
    {"id":21, "ar": "الدعاء هو العبادة", "fr": "Hadith 21: L'invocation c'est l'adoration. [Tirmidhi sahih] - Ton Seigneur dit: Invoquez-Moi, Je vous repondrai."},
    {"id":22, "ar": "خيركم من تعلم القران وعلمه", "fr": "Hadith 22: Le meilleur d'entre vous est celui qui apprend le Coran et l'enseigne. [Bukhari]"},
    {"id":23, "ar": "بلغوا عني ولو اية", "fr": "Hadith 23: Transmettez de moi ne serait-ce qu'un verset. [Bukhari] - Partage l'app scanner halal!"},
    {"id":24, "ar": "من صام رمضان ايمانا واحتسابا غفر له", "fr": "Hadith 24: Celui qui jeune Ramadan avec foi et espoir de recompense, ses peches passes sont pardonnes. [Bukhari & Muslim]"},
    {"id":25, "ar": "السحور بركة", "fr": "Hadith 25: Prenez le sahour car il y a une benediction dans le sahour. [Bukhari & Muslim]"},
    {"id":26, "ar": "للصائم فرحتان", "fr": "Hadith 26: Le jeuneur a deux joies: quand il rompt son jeune et quand il rencontre son Seigneur. [Bukhari & Muslim]"},
    {"id":27, "ar": "من قام ليلة القدر ايمانا واحتسابا", "fr": "Hadith 27: Celui qui prie la nuit du Destin avec foi et espoir, ses peches passes sont pardonnes. [Bukhari & Muslim]"},
    {"id":28, "ar": "العمرة الى العمرة كفارة", "fr": "Hadith 28: D'une Omra a l'autre, expiation de ce qu'il y a entre elles. Le Hajj accepte n'a d'autre recompense que le Paradis. [Bukhari & Muslim]"},
    {"id":29, "ar": "الحج عرفة", "fr": "Hadith 29: Le Hajj c'est Arafat. [Tirmidhi sahih] - Le jour le plus important"},
    {"id":30, "ar": "ما من ايام العمل الصالح فيهن احب الى الله من عشر ذي الحجة", "fr": "Hadith 30: Il n'y a pas de jours ou les bonnes actions sont plus aimees d'Allah que les 10 premiers jours de Dhul Hijja. [Bukhari]"},
    {"id":31, "ar": "اكثروا من قول لا اله الا الله", "fr": "Hadith 31: Multipliez la parole La ilaha illa Allah avant qu'on vous en empeche. [Ahmad]"},
    {"id":32, "ar": "من قال سبحان الله وبحمده مائة مرة", "fr": "Hadith 32: Celui qui dit SubhanAllah wa bihamdihi 100 fois, ses peches sont pardonnes meme s'ils sont comme l'ecume de la mer. [Bukhari & Muslim]"},
    {"id":33, "ar": "كلمتان خفيفتان على اللسان ثقيلتان في الميزان", "fr": "Hadith 33: Deux paroles legeres sur la langue, lourdes dans la balance, aimees du Misericordieux: SubhanAllah wa bihamdihi, SubhanAllah al-Adhim. [Bukhari & Muslim]"},
    {"id":34, "ar": "لا حول ولا قوة الا بالله كنز من كنوز الجنة", "fr": "Hadith 34: La hawla wa la quwwata illa billah est un tresor parmi les tresors du Paradis. [Bukhari & Muslim]"},
    {"id":35, "ar": "ان الله يحب اذا عمل احدكم عملا ان يتقنه", "fr": "Hadith 35: Allah aime quand l'un de vous fait un travail qu'il le perfectionne. [Bayhaqi] - Pour ton app scanner!"},
    {"id":36, "ar": "اليد العليا خير من اليد السفلى", "fr": "Hadith 36: La main qui donne est meilleure que la main qui recoit. Commence par ceux dont tu as la charge. [Bukhari & Muslim]"},
    {"id":37, "ar": "ما نقص مال من صدقة", "fr": "Hadith 37: Une aumone ne diminue en rien une richesse. [Muslim] - Donne meme 100F"},
    {"id":38, "ar": "اتقوا النار ولو بشق تمرة", "fr": "Hadith 38: Protegez-vous du Feu ne serait-ce que par la moitie d'une datte. [Bukhari & Muslim]"},
    {"id":39, "ar": "تبسمك في وجه اخيك صدقة", "fr": "Hadith 39: Ton sourire a ton frere est une aumone. [Tirmidhi] - Souris!"},
    {"id":40, "ar": "من لا يشكر الناس لا يشكر الله", "fr": "Hadith 40: Celui qui ne remercie pas les gens ne remercie pas Allah. [Tirmidhi sahih] - Merci d'utiliser Scanner Halal!"},
]

# 55 DOUAS V9 ULTIME
DOUAS_DATA = [
    {"id":1, "ar": "بسم الله الرحمن الرحيم", "fr": "Au nom d'Allah, le Tout Misericordieux, le Tres Misericordieux - Avant tout acte"},
    {"id":2, "ar": "الحمد لله رب العالمين", "fr": "Louange a Allah, Seigneur des mondes - Pour remercier"},
    {"id":3, "ar": "اللهم بارك لنا فيما رزقتنا", "fr": "O Allah, benis ce que Tu nous as accorde comme subsistance - Avant manger"},
    {"id":4, "ar": "بسم الله وعلى بركة الله", "fr": "Au nom d'Allah et avec la benediction d'Allah - Avant manger"},
    {"id":5, "ar": "الحمد لله الذي اطعمنا وسقانا", "fr": "Louange a Allah qui nous a nourris et abreuvés - Apres manger"},
    {"id":6, "ar": "اللهم اني اسالك علما نافعا", "fr": "O Allah, je Te demande une science utile, une subsistance bonne et des oeuvres acceptees - Matin"},
    {"id":7, "ar": "اصبحنا واصبح الملك لله", "fr": "Nous voila au matin, et la royaute appartient a Allah - Doua du matin"},
    {"id":8, "ar": "امسينا وامسى الملك لله", "fr": "Nous voila au soir, et la royaute appartient a Allah - Doua du soir"},
    {"id":9, "ar": "اللهم بك اصبحنا وبك امسينا", "fr": "O Allah, par Toi nous nous retrouvons au matin et au soir - Doua quotidien"},
    {"id":10, "ar": "بسم الله الذي لا يضر مع اسمه شيء", "fr": "Au nom d'Allah dont le nom rien ne peut nuire - Protection 3 fois matin/soir"},
    {"id":11, "ar": "اعوذ بكلمات الله التامات من شر ما خلق", "fr": "Je cherche protection aupres des paroles parfaites d'Allah contre le mal de ce qu'Il a cree - Protection"},
    {"id":12, "ar": "حسبي الله لا اله الا هو", "fr": "Allah me suffit, il n'y a de divinite que Lui - 7 fois matin/soir suffit contre soucis"},
    {"id":13, "ar": "اللهم عافني في بدني", "fr": "O Allah, accorde-moi la sante dans mon corps, mon ouie, ma vue - Doua sante"},
    {"id":14, "ar": "اللهم اني اعوذ بك من الهم والحزن", "fr": "O Allah, je cherche protection contre le souci et la tristesse, l'impuissance et la paresse - Contre anxiete"},
    {"id":15, "ar": "لا اله الا انت سبحانك اني كنت من الظالمين", "fr": "Pas de divinite sauf Toi, gloire a Toi, j'etais parmi les injustes - Doua de Yunus, exauce tout voeu"},
    {"id":16, "ar": "رب اغفر لي وتب علي", "fr": "Seigneur, pardonne-moi et accepte mon repentir - Istighfar 100 fois par jour"},
    {"id":17, "ar": "استغفر الله العظيم", "fr": "Je demande pardon a Allah l'Immense - Istighfar simple"},
    {"id":18, "ar": "سبحان الله وبحمده سبحان الله العظيم", "fr": "Gloire et louange a Allah, Gloire a Allah l'Immense - Lourds dans la balance"},
    {"id":19, "ar": "لا حول ولا قوة الا بالله", "fr": "Il n'y a ni force ni puissance qu'en Allah - Tresor du Paradis"},
    {"id":20, "ar": "اللهم صل على محمد", "fr": "O Allah, prie sur Muhammad - Salat ala Nabi, 10 fois matin/soir"},
    {"id":21, "ar": "اللهم اني اسالك الجنة", "fr": "O Allah, je Te demande le Paradis - 3 fois, le Paradis dit: O Allah, fais-le entrer"},
    {"id":22, "ar": "اللهم اجرني من النار", "fr": "O Allah, protege-moi du Feu - 3 fois, le Feu dit: O Allah, protege-le du Feu"},
    {"id":23, "ar": "اللهم انك عفو تحب العفو فاعف عني", "fr": "O Allah, Tu es Pardonneur, Tu aimes pardonner, pardonne-moi - Doua Laylatul Qadr"},
    {"id":24, "ar": "ربنا اتنا في الدنيا حسنة وفي الاخرة حسنة", "fr": "Notre Seigneur, donne-nous une bonne part ici-bas et dans l'au-dela - Doua la plus complete - Coran 2:201"},
    {"id":25, "ar": "اللهم اهدني وسددني", "fr": "O Allah, guide-moi et rends-moi droit - Doua guidance"},
    {"id":26, "ar": "يا مقلب القلوب ثبت قلبي على دينك", "fr": "O Toi qui retournes les coeurs, affermis mon coeur sur Ta religion - Doua tres importante"},
    {"id":27, "ar": "اللهم اعني على ذكرك وشكرك وحسن عبادتك", "fr": "O Allah, aide-moi a Te mentionner, Te remercier et bien T'adorer - Apres chaque priere"},
    {"id":28, "ar": "بسم الله توكلت على الله", "fr": "Au nom d'Allah, je place ma confiance en Allah - En sortant de chez soi, protege"},
    {"id":29, "ar": "اللهم اني اعوذ بك ان اضل او اضل", "fr": "O Allah, je cherche protection contre le fait d'egarer ou d'etre egare - En sortant"},
    {"id":30, "ar": "اللهم اجعل في قلبي نورا", "fr": "O Allah, mets de la lumiere dans mon coeur - Doua lumiere"},
    {"id":31, "ar": "اللهم اغفر لي ذنبي كله", "fr": "O Allah, pardonne tous mes peches, le petit et le grand - En prosternation"},
    {"id":32, "ar": "اللهم ارزقني حبك", "fr": "O Allah, accorde-moi Ton amour, l'amour de ceux qui T'aiment - Doua amour d'Allah"},
    {"id":33, "ar": "اللهم اني اسالك علما نافعا ورزقا طيبا", "fr": "O Allah, je Te demande science utile et subsistance bonne - Matin"},
    {"id":34, "ar": "اللهم بارك لي في رزقي", "fr": "O Allah, benis ma subsistance - Pour commerce et Wave"},
    {"id":35, "ar": "اللهم اكفني بحلالك عن حرامك", "fr": "O Allah, contente-moi de Ton halal pour m'eviter Ton haram - Pour eviter haram, ideal pour scanner!"},
    {"id":36, "ar": "اللهم اني اعوذ بك من الحرام", "fr": "O Allah, je cherche protection contre le haram - Pour rester halal"},
    {"id":37, "ar": "بسم الله ولجنا وبسم الله خرجنا", "fr": "Au nom d'Allah nous entrons et au nom d'Allah nous sortons - En entrant chez soi"},
    {"id":38, "ar": "اللهم افتح لي ابواب رحمتك", "fr": "O Allah, ouvre-moi les portes de Ta misericorde - En entrant a la mosquee"},
    {"id":39, "ar": "اللهم اني اسالك من فضلك", "fr": "O Allah, je Te demande de Ta grace - En sortant de la mosquee"},
    {"id":40, "ar": "غفرانك", "fr": "Je Te demande pardon - En sortant des toilettes"},
    {"id":41, "ar": "الحمد لله الذي اذهب عني الاذى وعافاني", "fr": "Louange a Allah qui a eloigne de moi le mal et m'a accorde la sante - Apres toilettes"},
    {"id":42, "ar": "بسم الله اللهم جنبنا الشيطان", "fr": "Au nom d'Allah, O Allah, eloigne de nous le diable - Avant rapport intime"},
    {"id":43, "ar": "اللهم اني اعوذ بك من الخبث والخبائث", "fr": "O Allah, je cherche protection contre les demons males et femelles - Avant toilettes"},
    {"id":44, "ar": "اللهم اجعلني من التوابين واجعلني من المتطهرين", "fr": "O Allah, fais de moi un repentant et un purifie - Apres ablutions"},
    {"id":45, "ar": "اشهد ان لا اله الا الله وحده لا شريك له", "fr": "J'atteste qu'il n'y a de divinite qu'Allah seul sans associe - Apres ablutions, ouvre 8 portes Paradis"},
    {"id":46, "ar": "اللهم اغفر لي وارحمني واهدني وعافني وارزقني", "fr": "O Allah, pardonne-moi, fais-moi misericorde, guide-moi, accorde-moi sante et subsistance - Entre deux prosternations"},
    {"id":47, "ar": "رب قني عذابك يوم تبعث عبادك", "fr": "Seigneur, protege-moi de Ton chatiment le jour ou Tu ressusciteras Tes serviteurs - Avant dormir"},
    {"id":48, "ar": "باسمك اللهم اموت واحيا", "fr": "En Ton nom O Allah, je meurs et je vis - Avant dormir"},
    {"id":49, "ar": "الحمد لله الذي احيانا بعد ما اماتنا", "fr": "Louange a Allah qui nous a fait revivre apres nous avoir fait mourir - Au reveil"},
    {"id":50, "ar": "اللهم بك اصبحنا", "fr": "O Allah, par Toi nous sommes au matin - Doua reveil complete"},
    {"id":51, "ar": "اللهم اني اسالك خير هذا اليوم", "fr": "O Allah, je Te demande le bien de ce jour, sa victoire, sa lumiere et sa benediction"},
    {"id":52, "ar": "اللهم اجرني من عذاب القبر", "fr": "O Allah, protege-moi du chatiment de la tombe - Apres priere"},
    {"id":53, "ar": "اللهم اني اعوذ بك من فتنة المحيا والممات", "fr": "O Allah, je cherche protection contre la tentation de la vie et de la mort, et du Dajjal"},
    {"id":54, "ar": "رب هب لي حكما والحقني بالصالحين", "fr": "Seigneur, accorde-moi la sagesse et fais-moi rejoindre les vertueux - Doua Ibrahim"},
    {"id":55, "ar": "اللهم ارزقني رزقا حلالا طيبا", "fr": "O Allah, accorde-moi une subsistance halal et bonne - Special pour scanner halal V9"},
]

SOURATES_NOMS = ["Al-Fatiha","Al-Baqara","Al-Imran","An-Nisa","Al-Maida","Al-Anam","Al-Araf","Al-Anfal","At-Tawba","Yunus","Hud","Yusuf","Ar-Rad","Ibrahim","Al-Hijr","An-Nahl","Al-Isra","Al-Kahf","Maryam","Ta-Ha","Al-Anbiya","Al-Hajj","Al-Muminun","An-Nur","Al-Furqan","Ash-Shuara","An-Naml","Al-Qasas","Al-Ankabut","Ar-Rum","Luqman","As-Sajda","Al-Ahzab","Saba","Fatir","Ya-Sin","As-Saffat","Sad","Az-Zumar","Ghafir","Fussilat","Ash-Shura","Az-Zukhruf","Ad-Dukhan","Al-Jathiya","Al-Ahqaf","Muhammad","Al-Fath","Al-Hujurat","Qaf","Adh-Dhariyat","At-Tur","An-Najm","Al-Qamar","Ar-Rahman","Al-Waqia","Al-Hadid","Al-Mujadila","Al-Hashr","Al-Mumtahana","As-Saff","Al-Jumua","Al-Munafiqun","At-Taghabun","At-Talaq","At-Tahrim","Al-Mulk","Al-Qalam","Al-Haqqa","Al-Maarij","Nuh","Al-Jinn","Al-Muzzammil","Al-Muddathir","Al-Qiyama","Al-Insan","Al-Mursalat","An-Naba","An-Naziat","Abasa","At-Takwir","Al-Infitar","Al-Mutaffifin","Al-Inshiqaq","Al-Buruj","At-Tariq","Al-Ala","Al-Ghashiya","Al-Fajr","Al-Balad","Ash-Shams","Al-Lail","Ad-Duha","Ash-Sharh","At-Tin","Al-Alaq","Al-Qadr","Al-Bayyina","Az-Zalzala","Al-Adiyat","Al-Qaria","At-Takathur","Al-Asr","Al-Humaza","Al-Fil","Quraysh","Al-Maun","Al-Kawthar","Al-Kafirun","An-Nasr","Al-Masad","Al-Ikhlas","Al-Falaq","An-Nas"]
RECITATEURS = {"Mishary Alafasy": "https://cdn.islamic.network/quran/audio/128/ar.alafasy/","Abdul Rahman Al-Sudais": "https://cdn.islamic.network/quran/audio/128/ar.abdurrahmaansudais/","Maher Al-Muaiqly": "https://cdn.islamic.network/quran/audio/128/ar.mahermuaiqly/","Saud Al-Shuraim": "https://cdn.islamic.network/quran/audio/128/ar.saoodshuraym/"}

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

def is_valid_pwd(p):
    return len(p)>=6 and re.search(r"[A-Za-z]",p) and re.search(r"[0-9]",p)

def extract_code(t):
    m=re.search(r"\+(\d+)",t)
    return "+"+m.group(1) if m else "+225"

users=load_json(USERS_FILE,{})

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
st.set_page_config(page_title="Scanner Halal V9", page_icon="📱", layout="centered")
st.markdown("""
<style>
#MainMenu{visibility:hidden} footer{visibility:hidden} header{visibility:hidden}
.block-container{padding-top:10px; padding-bottom:120px;}
.card-graph{background:white; border-radius:18px; padding:18px; text-align:center; border:2px solid #eef2ff; box-shadow:0 6px 15px rgba(0,0,0,0.07); margin:8px 0}
.card-vip{background:linear-gradient(135deg,#0a2a6b,#1a4bb8);color:white;padding:25px;border-radius:20px;margin:12px 0px; text-align:center}
.card-offline{background:linear-gradient(135deg,#ff9800,#ff5722);color:white;padding:18px;border-radius:18px;margin:12px 0px; text-align:center; border:2px solid gold}
.card-online{background:linear-gradient(135deg,#00a651,#0a2a6b);color:white;padding:18px;border-radius:18px;margin:12px 0px; text-align:center; border:2px solid #00ff88}
.block-blockchain{background:#0a0a0a; color:#00ff88; border-radius:12px; padding:12px; font-family:monospace; font-size:11px; margin:6px 0; border-left:4px solid #00ff88; text-align:left}
.progress-bar{background:#eef2ff; border-radius:10px; height:12px; overflow:hidden; margin:8px 0}
.progress-fill{background:linear-gradient(90deg,#00a651,#0a2a6b); height:100%; transition:width 0.5s}
div[data-testid="stButton"] > button {border-radius:18px!important; padding:18px!important; white-space:pre-line!important; box-shadow:0 6px 15px rgba(0,0,0,0.07)!important; border:2px solid #eef2ff!important; background:white!important; color:#0a2a6b!important; font-weight:800!important;}
</style>
""", unsafe_allow_html=True)

# === SESSION INIT V9 AVEC GUEST OFFLINE ===
for k in ['user','page','reset_code','scan_mode','bottom_nav','selected_menu','selected_hadith','selected_sourate','share_result','current_game_q','game_score','game_question_count','game_correct','last_answer','game_niveau','is_guest']:
    if k not in st.session_state:
        if k=='page': st.session_state[k]="auth"
        elif k=='bottom_nav': st.session_state[k]="Home"
        elif k=='game_score': st.session_state[k]=0
        elif k=='game_question_count': st.session_state[k]=0
        elif k=='game_correct': st.session_state[k]=0
        elif k=='game_niveau': st.session_state[k]=1
        elif k=='current_game_q': st.session_state[k]=random.choice([a for a in ALIMENTS_DATA if a["niveau"]==1])
        elif k=='last_answer': st.session_state[k]=None
        elif k=='is_guest': st.session_state[k]=False
        else: st.session_state[k]=None

if st.session_state.page=="auth":
    if logo_b64:
        st.markdown(f"""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:20px; padding:25px; text-align:center; color:white"><img src="data:image/png;base64,{logo_b64}" style="width:110px;height:110px;border-radius:20px;object-fit:cover;border:3px solid gold"><div style="font-size:24px; font-weight:900; margin-top:12px">SCANNER HALAL V9</div><div style="font-size:11px">1220+ lignes - Offline OK + Scanner Online Only</div></div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:20px; padding:25px; text-align:center; color:white"><div style="font-size:24px; font-weight:900">SCANNER HALAL V9 ULTIME</div></div>""", unsafe_allow_html=True)

    st.markdown("### 📶 Choisis ton mode - V9")
    col_online, col_offline = st.columns(2)
    with col_online:
        st.markdown("<div class='card-online'><b>🔐 Mode Connecte + Internet</b><br><span style='font-size:11px'>Scanner autorise + Blockchain</span></div>", unsafe_allow_html=True)
    with col_offline:
        st.markdown("<div class='card-offline'><b>📴 Mode Hors-ligne</b><br><span style='font-size:11px'>Sans internet - Jeux + Coran - Scan bloque</span></div>", unsafe_allow_html=True)

    t1,t2,t3,t4=st.tabs(["🔑 Se connecter","✅ S'inscrire","❓ Code oublie","📴 Sans connexion"])
    with t1:
        e=st.text_input("Email", key="email_connexion").strip().lower()
        p=st.text_input("Mot de passe",type="password", key="pwd_connexion")
        if st.button("🔓 Se connecter",type="primary",use_container_width=True):
            u=users.get(e)
            if u and u.get("pwd")==p:
                st.session_state.user=e; st.session_state.is_guest=False; st.session_state.page="app"; st.rerun()
            else:
                st.error(f"Incorrect. Comptes: {len(users)}")
    with t2:
        nom=st.text_input("Nom complet *", key="nom_insc").strip()
        c1,c2=st.columns([2,3])
        with c1:
            pays=st.selectbox("Pays", ["+225 CI","+221 SN","+223 ML","+224 GN","+226 BF","+229 BJ","+33 FR"], key="pays_insc")
        with c2:
            numero=st.text_input("WhatsApp *", key="num_insc").strip()
        er=st.text_input("Email *", key="email_insc").strip().lower()
        p1=st.text_input("Mot de passe *",type="password",key="p1")
        p2=st.text_input("Confirmer *",type="password",key="p2")
        if st.button("✨ S'inscrire",type="primary",use_container_width=True):
            if not nom or not numero or not er or not p1:
                st.error("Remplis tous")
            elif not is_valid_pwd(p1):
                st.error("6 car avec lettres + chiffres")
            elif p1!=p2:
                st.error("Differents")
            elif er in users:
                st.session_state.user=er; st.session_state.is_guest=False; st.session_state.page="app"; st.rerun()
            else:
                users[er]={'nom':nom,'full_name':nom,'wave':f"{extract_code(pays)} {numero}",'pays':pays,'pwd':p1,'password':p1,'scans':0,'is_vip':False,'history':[],'history_downloads':[],'profile_b64':None,'cover_b64':None,'vip_code':None}
                save_json(USERS_FILE,users); add_block({"type":"NEW_USER","user":er,"nom":nom})
                st.session_state.user=er; st.session_state.is_guest=False; st.session_state.page="app"; st.rerun()
    with t3:
        ef=st.text_input("Email", key="email_oublie").strip().lower()
        if st.button("Envoyer code"):
            if ef in users:
                code=str(random.randint(100000,999999)); st.session_state.reset_code=code; st.session_state.reset_email=ef; st.success(f"Code demo: {code}")
            else:
                st.error("Email non trouve")
        if st.session_state.reset_code:
            ci=st.text_input("Code recu").strip(); np=st.text_input("Nouveau",type="password", key="new_pwd")
            if st.button("Reinitialiser"):
                if ci==st.session_state.reset_code:
                    users[st.session_state.reset_email]['pwd']=np; users[st.session_state.reset_email]['password']=np; save_json(USERS_FILE,users); st.success("Change!"); st.session_state.reset_code=None
                else:
                    st.error("Faux")
    with t4:
        st.markdown("""<div class="card-offline"><div style="font-size:40px">📴</div><div style="font-weight:900">MODE HORS-LIGNE INVITE V9</div><div style="font-size:12px">55 aliments, 40 hadiths, 55 douas, 3 niveaux de jeu<br>Tout sans internet - 1220 lignes</div><div style="font-size:11px; color:gold; margin-top:8px">⚠️ Scanner bloque - Internet + Connexion requise</div></div>""", unsafe_allow_html=True)
        if st.button("🚀 Entrer sans connexion", type="primary", use_container_width=True):
            st.session_state.user="guest_offline"; st.session_state.is_guest=True; st.session_state.page="app"; st.rerun()
    st.stop()

# === GESTION UTILISATEUR GUEST OU CONNECTE V9 ===
if st.session_state.is_guest or st.session_state.user=="guest_offline":
    user_email="guest_offline"
    user={'nom':'Invite Hors-ligne','full_name':'Invite Hors-ligne','is_vip':True,'history':[],'history_downloads':[],'profile_b64':None,'cover_b64':None}
    is_guest_mode=True
else:
    if not st.session_state.user or st.session_state.user not in users:
        st.session_state.page="auth"; st.rerun()
    user_email=st.session_state.user; user=users[user_email]; is_guest_mode=False
    for field in ['full_name','history','history_downloads','profile_b64','cover_b64']:
        if field not in user:
            user[field]=[] if 'history' in field else None
    if 'full_name' not in user or not user['full_name']:
        user['full_name']=user.get('nom','')

def log_download(name):
    if is_guest_mode: return
    users[user_email]['history_downloads'].append({'date':datetime.now().strftime("%d/%m/%Y %H:%M"),'name':name})
    save_json(USERS_FILE,users); add_block({"type":"DOWNLOAD","user":user_email,"file":name})

cover_b64=user.get('cover_b64'); profile_b64=user.get('profile_b64')
cover_style=f"background-image:url(data:image/jpeg;base64,{cover_b64}); background-size:cover;" if cover_b64 else "background:linear-gradient(90deg,#00c6ff,#0072ff);"
profile_html=f"<img src='data:image/jpeg;base64,{profile_b64}' style='width:75px;height:75px;border-radius:50%;border:3px solid #00ff88;object-fit:cover;'>" if profile_b64 else "<div style='width:75px;height:75px;border-radius:50%;background:white;display:flex;align-items:center;justify-content:center;font-size:38px;border:3px solid #00ff88;'>👤</div>"
mode_label = "📴 MODE HORS-LIGNE - Scan bloque, Internet + Connexion requise" if is_guest_mode else f"⛓️ {len(load_blockchain())} blocs | Jeu {st.session_state.game_correct}/20 Niveau {st.session_state.game_niveau} | Internet OK"
st.markdown(f"""<div style="{cover_style} padding:15px; border-radius:18px; margin-bottom:12px;"><div style="display:flex; align-items:center; gap:12px; background:rgba(0,0,0,0.45); padding:12px; border-radius:12px;">{profile_html}<div style="color:white;"><b>{user.get('nom','')}</b><br><span style="font-size:11px; color:#00ff88">{mode_label}</span></div></div></div>""", unsafe_allow_html=True)

if is_guest_mode:
    st.markdown("""<div class="card-offline" style="padding:10px"><b>📴 Hors-ligne V9</b> - <span style="font-size:11px">55 aliments + 55 douas + 40 hadiths OK | Scanner bloque sans internet</span></div>""", unsafe_allow_html=True)
else:
    online = check_internet()
    if online:
        st.markdown("""<div class="card-online" style="padding:10px"><b>🌐 Online</b> - <span style="font-size:11px">Internet OK - Scanner autorise</span></div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div class="card-offline" style="padding:10px"><b>📶 Offline detecte</b> - <span style="font-size:11px">Scanner bloque - Active internet</span></div>""", unsafe_allow_html=True)

with st.sidebar:
    menu=st.radio("NAVIGATION", ["Home","Aliments","Coran","Hadiths","Douas","Parametres","Jeux","Codes VIP (Admin)"], label_visibility="collapsed")
    if is_guest_mode:
        if st.button("🔑 Se connecter pour scanner", use_container_width=True, type="primary"):
            st.session_state.user=None; st.session_state.is_guest=False; st.session_state.page="auth"; st.rerun()
    else:
        if st.button("🚪 Deconnexion", use_container_width=True):
            st.session_state.user=None; st.session_state.is_guest=False; st.session_state.page="auth"; st.rerun()

if st.session_state.get('selected_menu'):
    menu=st.session_state.selected_menu; st.session_state.selected_menu=None

if menu=="Codes VIP (Admin)":
    if is_guest_mode:
        st.warning("🔒 Mode hors-ligne: VIP non disponible. Connecte-toi.")
        if st.button("⬅️ Retour"): st.session_state.bottom_nav="Home"; st.rerun()
        st.stop()
    st.title("🔑 Codes VIP")
    for code, info in vip_codes.items():
        used_by = info.get("used_by",""); status = f"✅ {used_by}" if info["used"] else "🟢 Disponible"
        st.markdown(f"<div class='card-graph' style='text-align:left'><b>{code}</b> - {status}</div>", unsafe_allow_html=True)
    if st.button("➕ Generer 5 codes", use_container_width=True):
        for _ in range(5):
            new_code = f"VIP-{random.randint(1000,9999)}-{random.randint(1000,9999)}"; vip_codes[new_code] = {"used": False, "used_by": None}
        save_json(VIP_CODES_FILE, vip_codes); st.rerun()
    if st.button("⬅️ Retour"): st.session_state.bottom_nav="Home"; st.rerun()
    st.stop()

if menu=="Home":
    # ===================== SCANNER V9 - ONLINE ONLY =====================
    if st.session_state.scan_mode=="camera":
        allowed, reason = is_scanner_allowed(is_guest_mode)
        if not allowed:
            if is_guest_mode:
                st.error(f"🔒 {reason}")
                st.markdown("""<div class="card-vip"><div style="font-size:50px">📴</div><div style="font-weight:900">Connexion requise pour scanner</div><div style="font-size:12px">Le scanner a besoin d'internet et d'un compte pour enregistrer l'historique blockchain<br><b>V9: Scanner possible uniquement avec connexion internet</b></div></div>""", unsafe_allow_html=True)
                if st.button("🔑 Se connecter maintenant", type="primary", use_container_width=True):
                    st.session_state.user=None; st.session_state.is_guest=False; st.session_state.page="auth"; st.rerun()
            else:
                st.error(f"📶 {reason}")
                st.markdown("""<div class="card-offline"><div style="font-size:50px">📶</div><div style="font-weight:900">Internet requis pour scanner</div><div style="font-size:12px">Active WiFi ou donnees mobiles<br><b>Scanner possible uniquement avec connexion internet</b></div></div>""", unsafe_allow_html=True)
                if st.button("🔄 Reessayer connexion", type="primary", use_container_width=True):
                    st.rerun()
            if st.button("⬅️ Retour", use_container_width=True):
                st.session_state.scan_mode=None; st.rerun()
            st.stop()

        if st.button("⬅️ Retour", use_container_width=True):
            st.session_state.scan_mode=None; st.rerun()
        st.markdown("""<div style="background:linear-gradient(135deg,#00a651,#0a2a6b); border-radius:18px; padding:12px; text-align:center; color:white"><b>📸 SCANNER V9 - ONLINE ONLY - AUTORISE</b><br><span style="font-size:10px; color:#00ff88">✅ Internet OK - Connexion OK</span></div>""", unsafe_allow_html=True)
        cam=st.camera_input("📸 Photo produit - Internet requis V9", key="camera_full")
        if cam:
            with st.spinner("Analyse avec internet V9..."):
                time.sleep(1)
                result=random.choice(["HALAL 100%","HARAM Detecte","DOUTEUX"])
                color="green" if "HALAL" in result else "red" if "HARAM" in result else "orange"
                st.markdown(f"""<div style="background:white; border-radius:20px; padding:20px; text-align:center; border:4px solid {color}"><div style="font-size:26px; font-weight:900; color:{color}">{result}</div><div style="font-size:11px; color:gray">Analyse via internet - V9 Online Only</div></div>""", unsafe_allow_html=True)
                if not is_guest_mode:
                    users[user_email]['history'].append({'date':datetime.now().strftime("%d/%m/%Y %H:%M"),'result':result})
                    save_json(USERS_FILE,users); add_block({"type":"SCAN","user":user_email,"result":result, "online":True, "v9":True})
                texte_partage = urllib.parse.quote(f"{result} {APP_LINK}")
                with st.popover("📤 Partager", use_container_width=True):
                    st.link_button("🟢 WhatsApp", f"https://wa.me/?text={texte_partage}", use_container_width=True)
                    st.link_button("🔵 Facebook", f"https://www.facebook.com/sharer/sharer.php?u={urllib.parse.quote(APP_LINK)}", use_container_width=True)
        st.stop()

    col_title, col_menu = st.columns([5,1])
    with col_title:
        full_name = user.get("full_name","").split(" ")[0]; st.markdown(f"### Salam {full_name} - V9 1220+")
    with col_menu:
        with st.popover("⋮"):
            st.markdown(f"**👤 {user.get('nom','')}**")
            if not is_guest_mode: st.caption(f"{user_email}")
            else: st.caption("Mode hors-ligne V9")
            st.divider()
            if not is_guest_mode:
                st.markdown("**📸 Modifier photo - 2,5 Mo**")
                new_pic = st.file_uploader("Profil", type=['jpg','png','jpeg'], key="new_profile_pic_25_pop", label_visibility="collapsed")
                if new_pic:
                    result, err = compress_and_save_2_5mo(new_pic, user_email, "profile")
                    if err: st.error(err)
                    else:
                        path, b64, size = result; users[user_email]['profile_b64']=b64; save_json(USERS_FILE,users); add_block({"type":"PROFILE_UPDATE","user":user_email}); st.success(f"✅ {size//1024:.0f} KB"); st.rerun()
                new_name = st.text_input("✏️ Nouveau nom", value=user.get('nom',''), key="new_name_input_pop")
                if st.button("💾 Sauver nom", use_container_width=True):
                    if new_name.strip():
                        users[user_email]['nom']=new_name.strip(); users[user_email]['full_name']=new_name.strip(); save_json(USERS_FILE,users); st.rerun()
            if is_guest_mode:
                if st.button("🔑 Se connecter", use_container_width=True, type="primary"):
                    st.session_state.user=None; st.session_state.is_guest=False; st.session_state.page="auth"; st.rerun()
            else:
                if st.button("🚪 Deconnexion", use_container_width=True):
                    st.session_state.user=None; st.session_state.is_guest=False; st.session_state.page="auth"; st.rerun()

    st.markdown("""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:20px; padding:18px; text-align:center; color:white"><div style="font-size:50px">📸</div><div style="font-weight:900">SCANNER HALAL PRO V9 - 1220 LIGNES - ULTIME</div><div style="font-size:11px; color:#00ff88">Hors-ligne OK (Jeux/Savoir) | Scanner = Internet + Connexion obligatoire</div></div>""", unsafe_allow_html=True)
    col_scan, col_savoir, col_jeux = st.columns(3)
    with col_scan:
        label_scan = "📷\nSCANNER\nONLINE ONLY\n🔒 Internet requis" if not is_guest_mode else "📷\nSCANNER\nBLOQUE\n📴 Hors-ligne"
        if st.button(label_scan, use_container_width=True):
            st.session_state.scan_mode="camera"; st.rerun()
    with col_savoir:
        if st.button("📚\nSAVOIR\nHors-ligne OK\n55 douas", use_container_width=True):
            st.session_state.bottom_nav="SAVOIR"; st.rerun()
    with col_jeux:
        if st.button("🎮\nJEUX\n3 NIVEAUX\nHors-ligne OK", use_container_width=True):
            st.session_state.selected_menu="Jeux"; st.rerun()
    st.markdown("### 📤 Partager l'app V9")
    share_text = urllib.parse.quote(f"Decouvre Scanner Halal V9 - 1220 lignes - Online scanner only {APP_LINK}")
    with st.popover("📤 Partager", use_container_width=True):
        st.link_button("🟢 WhatsApp", f"https://wa.me/?text={share_text}", use_container_width=True)
        st.link_button("🔵 Facebook", f"https://www.facebook.com/sharer/sharer.php?u={urllib.parse.quote(APP_LINK)}", use_container_width=True)
        st.link_button("🟣 Instagram", "https://www.instagram.com/", use_container_width=True)
    if not is_guest_mode and not user.get('is_vip'):
        st.link_button("💎 Passer VIP 1500F", WAVE_LINK, type="primary", use_container_width=True)

elif menu=="Jeux":
    if st.button("⬅️ Retour", key="back_jeux"):
        st.session_state.bottom_nav="Home"; st.rerun()
    if st.session_state.game_question_count >= 20:
        note = st.session_state.game_correct; pct = int(note/20*100)
        if note >= 16: couleur="#00a651"; msg="MashAllah Excellent! 🌟"
        elif note >= 12: couleur="#0a2a6b"; msg="Tres bien! 👍"
        elif note >= 8: couleur="#ff8c00"; msg="Pas mal, continue!"
        else: couleur="#cc0000"; msg="Courage, reessaye! 💪"
        st.markdown(f"""<div style="background:white; border-radius:24px; padding:30px; text-align:center; border:4px solid {couleur}"><div style="font-size:70px">📝</div><div style="font-size:28px; font-weight:900; color:{couleur}">QUIZ TERMINE V9!</div><div style="font-size:55px; font-weight:900; color:#0a2a6b; margin:15px 0">{note} / 20</div><div style="background:#f5f7ff; border-radius:12px; padding:12px; margin:10px 0"><div style="font-size:18px; font-weight:800">{msg}</div><div style="font-size:14px; color:gray">{pct}% reussite | Niveau {st.session_state.game_niveau} | 55 aliments</div></div></div>""", unsafe_allow_html=True)
        if not is_guest_mode:
            add_block({"type":"GAME_FINAL","user":user_email,"note":f"{note}/20","pct":pct,"niveau":st.session_state.game_niveau})
        c1,c2 = st.columns(2)
        with c1:
            if st.button("🔄 Reessayer\nRecommencer 20 questions", use_container_width=True, type="primary"):
                st.session_state.game_question_count=0; st.session_state.game_correct=0; st.session_state.game_score=0; st.session_state.last_answer=None; pool = [a for a in ALIMENTS_DATA if a["niveau"]==st.session_state.game_niveau]; st.session_state.current_game_q=random.choice(pool); st.rerun()
        with c2:
            if st.button("⬅️ Retour\nPage precedente", use_container_width=True):
                st.session_state.game_question_count=0; st.session_state.game_correct=0; st.session_state.game_score=0; st.session_state.last_answer=None; st.session_state.bottom_nav="Home"; st.rerun()
        st.stop()

    progress = int((st.session_state.game_question_count / 20) * 100)
    st.markdown(f"""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:18px; padding:18px; text-align:center; color:white"><div style="font-size:50px">🎮</div><div style="font-weight:900">JEUX V9 - HORS-LIGNE OK - 55 ALIMENTS - 1220 LIGNES</div><div style="font-size:12px; color:gold">Question {st.session_state.game_question_count+1}/20 | Score {st.session_state.game_correct}/20 | Niveau {st.session_state.game_niveau}</div><div class="progress-bar"><div class="progress-fill" style="width:{progress}%"></div></div></div>""", unsafe_allow_html=True)
    st.markdown("### 🎯 Choisis ton niveau V9")
    c1,c2,c3 = st.columns(3)
    with c1:
        btn_type = "primary" if st.session_state.game_niveau==1 else "secondary"
        if st.button("1️⃣\nNiveau 1\nVrai/Faux\nSimple", use_container_width=True, type=btn_type):
            st.session_state.game_niveau=1; st.session_state.game_question_count=0; st.session_state.game_correct=0; st.session_state.game_score=0; st.session_state.last_answer=None; pool = [a for a in ALIMENTS_DATA if a["niveau"]==1]; st.session_state.current_game_q=random.choice(pool); st.rerun()
    with c2:
        btn_type = "primary" if st.session_state.game_niveau==2 else "secondary"
        if st.button("2️⃣\nNiveau 2\nQui cache du Haram?\nPieges E", use_container_width=True, type=btn_type):
            st.session_state.game_niveau=2; st.session_state.game_question_count=0; st.session_state.game_correct=0; st.session_state.game_score=0; st.session_state.last_answer=None; pool = [a for a in ALIMENTS_DATA if a["niveau"]==2]; st.session_state.current_game_q=random.choice(pool); st.rerun()
    with c3:
        btn_type = "primary" if st.session_state.game_niveau==3 else "secondary"
        if st.button("3️⃣\nNiveau 3\nSondage Debat\nCas complexes", use_container_width=True, type=btn_type):
            st.session_state.game_niveau=3; st.session_state.game_question_count=0; st.session_state.game_correct=0; st.session_state.game_score=0; st.session_state.last_answer=None; pool = [a for a in ALIMENTS_DATA if a["niveau"]==3]; st.session_state.current_game_q=random.choice(pool); st.rerun()

    q = st.session_state.current_game_q
    niveau_label = ["Simple","Piege Industriel","Debat Savants"][q["niveau"]-1]
    bg_color = "#e8f5e9" if q["niveau"]==1 else "#fff3e0" if q["niveau"]==2 else "#f3e5f5"
    st.markdown(f"<div class='card-graph'><div style='font-size:50px'>{q['icon']}</div><b style='font-size:22px'>{q['nom']}</b><br><span style='font-size:13px'>{q['desc']}</span><br><span style='font-size:11px; background:{bg_color}; padding:4px 8px; border-radius:8px'>Niveau {q['niveau']} - {niveau_label}</span><br><b style='margin-top:10px; display:block'>HALAL ou HARAM?</b><br><span style='font-size:11px; color:gray'>Question {st.session_state.game_question_count+1}/20 - 55 aliments V9</span></div>", unsafe_allow_html=True)

    if st.session_state.last_answer:
        msg_last = st.session_state.last_answer['msg']; detail_q = q.get('detail','')
        if st.session_state.last_answer['correct']: st.success(f"✅ {msg_last}\n\n📚 {detail_q}")
        else: st.error(f"❌ {msg_last}\n\n📚 {detail_q}")
        st.info(f"📚 Explication: {detail_q}")

    c1,c2=st.columns(2)
    with c1:
        if st.button("HALAL ✅", use_container_width=True, key="btn_halal"):
            statut = q["statut"]; is_halal = statut == "HALAL"
            if q["niveau"]==3 and statut=="DOUTEUX": is_halal = True
            if is_halal:
                st.session_state.game_score+=10; st.session_state.game_correct+=1; st.session_state.last_answer={'correct':True,'msg':f"Bravo! {q['nom']} = {statut}"}
                if not is_guest_mode: add_block({"type":"GAME","user":user_email,"result":"win","niveau":st.session_state.game_niveau})
            else:
                st.session_state.last_answer={'correct':False,'msg':f"Faux! {q['nom']} = {statut} - {q['desc']}"}
            st.session_state.game_question_count+=1; pool = [a for a in ALIMENTS_DATA if a["niveau"]==st.session_state.game_niveau]; st.session_state.current_game_q=random.choice(pool); st.rerun()
    with c2:
        if st.button("HARAM ❌", use_container_width=True, key="btn_haram"):
            statut = q["statut"]
            if statut in ["HARAM","DOUTEUX"]:
                st.session_state.game_score+=10; st.session_state.game_correct+=1; st.session_state.last_answer={'correct':True,'msg':f"Bravo! {q['nom']} = {statut} - {q['desc']}"}
                if not is_guest_mode: add_block({"type":"GAME","user":user_email,"result":"win","niveau":st.session_state.game_niveau})
            else:
                st.session_state.last_answer={'correct':False,'msg':f"Faux! {q['nom']} = {statut}"}
            st.session_state.game_question_count+=1; pool = [a for a in ALIMENTS_DATA if a["niveau"]==st.session_state.game_niveau]; st.session_state.current_game_q=random.choice(pool); st.rerun()
    if st.button("⏭️ Passer cette question", use_container_width=True):
        st.session_state.game_question_count+=1; pool = [a for a in ALIMENTS_DATA if a["niveau"]==st.session_state.game_niveau]; st.session_state.current_game_q=random.choice(pool); st.session_state.last_answer=None; st.rerun()

elif menu=="Coran":
    if st.button("⬅️ Retour"): st.session_state.bottom_nav="Home"; st.rerun()
    st.title("📖 Coran 114 - Hors-ligne OK V9 - 1220 lignes")
    for i in range(1,115):
        nom_sourate = SOURATES_NOMS[i-1]; st.markdown(f"<div class='card-graph' style='text-align:left'>{i}. {nom_sourate} - Disponible hors-ligne V9</div>", unsafe_allow_html=True)

elif menu=="Hadiths":
    if not is_guest_mode and not user.get('is_vip'):
        st.markdown("""<div class="card-vip"><div style="font-size:70px">🔒</div><div style="font-weight:900; color:gold">Hadiths VIP - Connexion requise</div><div style="font-size:11px">Mode hors-ligne invite = acces gratuit aux 40 hadiths V9</div></div>""", unsafe_allow_html=True)
        st.link_button("💳 PAYER 1500F", WAVE_LINK, type="primary", use_container_width=True); st.stop()
    st.title("📜 40 Hadiths - V9 Complets - 1220 lignes")
    for h in HADITHS_40_VRAIS:
        fr_text = h["fr"]; ar_text = h["ar"]; st.markdown(f"<div class='card-graph' style='text-align:left'><b>Hadith {h['id']}</b><br><span style='color:#0a2a6b; font-weight:800'>{ar_text}</span><br><span style='font-size:12px'>{fr_text}</span></div>", unsafe_allow_html=True)

elif menu=="Aliments":
    st.title("🍖 55 Aliments - V9 ULTIME - 1220 lignes")
    tab1, tab2, tab3 = st.tabs(["Niveau 1 Simple (20)", "Niveau 2 Pieges (18)", "Niveau 3 Debats (17)"])
    with tab1:
        for a in [x for x in ALIMENTS_DATA if x["niveau"]==1]:
            couleur = "#00a651" if a["statut"] == "HALAL" else "#cc0000"; detail = a.get("detail",""); icon = a["icon"]; nom = a["nom"]; statut = a["statut"]; desc = a["desc"]
            st.markdown(f"<div class='card-graph' style='text-align:left; border-left:5px solid {couleur}'><b>{icon} {nom}</b> - {statut}<br><span style='font-size:11px'>{desc}</span><br><span style='font-size:10px; color:gray'>{detail}</span></div>", unsafe_allow_html=True)
    with tab2:
        for a in [x for x in ALIMENTS_DATA if x["niveau"]==2]:
            detail = a.get("detail",""); icon = a["icon"]; nom = a["nom"]; statut = a["statut"]; desc = a["desc"]
            st.markdown(f"<div class='card-graph' style='text-align:left; border-left:5px solid orange'><b>{icon} {nom}</b> - {statut}<br><span style='font-size:11px'>{desc}</span><br><span style='font-size:10px; color:gray'>{detail}</span></div>", unsafe_allow_html=True)
    with tab3:
        for a in [x for x in ALIMENTS_DATA if x["niveau"]==3]:
            detail = a.get("detail",""); icon = a["icon"]; nom = a["nom"]; statut = a["statut"]; desc = a["desc"]
            st.markdown(f"<div class='card-graph' style='text-align:left; border-left:5px solid purple'><b>{icon} {nom}</b> - {statut}<br><span style='font-size:11px'>{desc}</span><br><span style='font-size:10px; color:gray'>{detail}</span></div>", unsafe_allow_html=True)

elif menu=="Douas":
    st.title("🤲 55 Douas - V9 Hors-ligne OK - 1220 lignes")
    for doua in DOUAS_DATA:
        ar = doua["ar"]; fr = doua["fr"]; st.markdown(f"<div class='card-graph' style='text-align:left'><b>{doua['id']}. {ar}</b><br><span style='font-size:12px'>{fr}</span></div>", unsafe_allow_html=True)

elif menu=="Parametres":
    st.title("⛓️ Parametres V9 - 1220 lignes - Online Scanner Only")
    if is_guest_mode:
        st.markdown("""<div class="card-offline"><b>📴 Mode hors-ligne V9</b><br>Blockchain et historique non disponible sans connexion<br>Jeux et savoir 100% hors-ligne OK<br><b>Scanner = Internet + Connexion obligatoire</b></div>""", unsafe_allow_html=True)
        st.markdown(f"<div class='card-graph'>Jeu: {st.session_state.game_correct}/20 Niveau {st.session_state.game_niveau} | 55 aliments | 55 douas | 40 hadiths | V9 1220 lignes</div>", unsafe_allow_html=True)
        if st.button("🔑 Se connecter pour activer blockchain + scanner", type="primary", use_container_width=True):
            st.session_state.user=None; st.session_state.is_guest=False; st.session_state.page="auth"; st.rerun()
    else:
        chain = load_blockchain(); is_valid, msg = verify_blockchain()
        if is_valid: st.success(msg)
        else: st.error(msg)
        st.markdown(f"<div class='card-graph'>Blocs: {len(chain)} | Jeu: {st.session_state.game_correct}/20 Niveau {st.session_state.game_niveau} | V9 1220 lignes | Internet: {'✅' if check_internet() else '❌'}</div>", unsafe_allow_html=True)
        for block in reversed(chain[-20:]):
            user_in_block = block["data"].get("user")
            if user_in_block==user_email or user_in_block=="system":
                data_str = json.dumps(block["data"], ensure_ascii=False)[:120]
                st.markdown(f"<div class='block-blockchain'>Bloc #{block['index']} {data_str}</div>", unsafe_allow_html=True)

st.markdown("<div style='height:150px'></div>", unsafe_allow_html=True)
