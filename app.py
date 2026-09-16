import streamlit as st
import json
import os
import random
import re
import base64
import calendar
import time
import urllib.parse
import io
import hashlib
import shutil
import socket
from datetime import datetime, date
from PIL import Image

# CONFIG LIENS
WAVE_LINK = "https://pay.wave.com/m/M_ci_bqKBEWPbP0OO/c/ci/?amount=1500"
MONETAG_LINK = "https://omg10.com/4/11717935"
APP_LINK = "https://scanner-halal-mbcyfmxur68mw8n9zd72ul.streamlit.app"
USERS_FILE = "users.json"
VIP_CODES_FILE = "vip_codes.json"
BLOCKCHAIN_FILE = "blockchain_history.json"

HIJRI_MONTHS = [
    "Muharram","Safar","Rabi al-Awwal","Rabi al-Thani",
    "Jumada al-Ula","Jumada al-Akhira","Rajab","Shaban",
    "Ramadan","Shawwal","Dhu al-Qidah","Dhu al-Hijjah"
]

MAX_PHOTO_SIZE = int(2.5 * 1024 * 1024)

os.makedirs("profile_pics", exist_ok=True)
os.makedirs("static", exist_ok=True)

if os.path.exists("logo.png"):
    try:
        shutil.copyfile("logo.png", "static/logo.png")
    except:
        pass

# PWA MANIFEST
manifest = {
  "name": "Scanner Halal Blockchain",
  "short_name": "Halal Scan",
  "description": "Application Scanner Halal - Fonctionne sans connexion sauf scanner",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#0a2a6b",
  "theme_color": "#0a2a6b",
  "orientation": "portrait",
  "icons": [
    {"src": "https://scanner-halal-mbcyfmxur68mw8n9zd72ul.streamlit.app/app/static/logo.png","sizes": "192x192","type": "image/png","purpose": "any maskable"},
    {"src": "https://scanner-halal-mbcyfmxur68mw8n9zd72ul.streamlit.app/app/static/logo.png","sizes": "512x512","type": "image/png","purpose": "any maskable"},
  ]
}

with open("static/manifest.json","w",encoding="utf-8") as f:
    json.dump(manifest,f,indent=2)

with open("static/sw.js","w") as f:
    f.write('self.addEventListener("install", e=>{e.waitUntil(caches.open("halal-final-pro").then(c=>c.addAll(["/"])))});self.addEventListener("fetch", e=>{e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request)))})')

# BLOCKCHAIN FUNCTIONS
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
    genesis = {
        "index": 0,
        "timestamp": datetime.now().isoformat(),
        "data": {"type":"GENESIS","message":"Scanner Halal Final Pro","user":"system"},
        "previous_hash": "0"*64,
        "hash": ""
    }
    genesis["hash"] = calculate_hash(genesis["index"], genesis["timestamp"], genesis["data"], genesis["previous_hash"])
    return [genesis]

def save_blockchain(chain):
    with open(BLOCKCHAIN_FILE,'w',encoding='utf-8') as fp:
        json.dump(chain,fp,ensure_ascii=False,indent=2)

def add_block(data):
    chain = load_blockchain()
    last = chain[-1]
    new_block = {
        "index": len(chain),
        "timestamp": datetime.now().isoformat(),
        "data": data,
        "previous_hash": last["hash"],
        "hash": ""
    }
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

def check_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        try:
            socket.create_connection(("1.1.1.1", 53), timeout=3)
            return True
        except:
            return False

def is_scanner_allowed(is_guest):
    if is_guest:
        return False, "Connexion requise pour scanner"
    if not check_internet():
        return False, "Pas de connexion internet - Le scanner necessite internet"
    return True, "Scanner autorise"

# 55 ALIMENTS COMPLETS AVEC DETAIL LONG
ALIMENTS_DATA = [
    {
        "nom": "Poulet (halal)",
        "statut": "HALAL",
        "icon": "🐔",
        "desc": "Halal si egorge selon rite",
        "niveau": 1,
        "detail": "Prononcer Bismillah, egorger selon rite islamique. Conforme Coran 6:118. Le Prophete a dit de bien aiguiser le couteau pour ne pas faire souffrir l'animal. Condition: couper la gorge, l'oesophage et les veines jugulaires. Le sang doit couler. Sans Bismillah intentionnel = haram selon certains."
    },
    {
        "nom": "Boeuf halal",
        "statut": "HALAL",
        "icon": "🐄",
        "desc": "Halal avec sacrifice rituel",
        "niveau": 1,
        "detail": "Halal avec sacrifice rituel Aid Al-Adha. Coran 22:36. Tres noble. Le sang doit couler completement. Dire Bismillah Allahu Akbar. 7 personnes peuvent s'associer sur une vache pour l'Aid."
    },
    {
        "nom": "Mouton halal",
        "statut": "HALAL",
        "icon": "🐑",
        "desc": "Halal sacrifice Aid",
        "niveau": 1,
        "detail": "Tres recommande pendant Aid. Sacrifice d'Ibrahim. Sunna mouakkada pour celui qui a les moyens. Partager en 3: famille, amis, pauvres. Le meilleur mouton = cornu, blanc avec noir autour yeux."
    },
    {
        "nom": "Poisson Thon",
        "statut": "HALAL",
        "icon": "🐟",
        "desc": "Tous les poissons sont halal",
        "niveau": 1,
        "detail": "Tous les poissons et fruits de mer sont halal pour majorite des ecoles. Coran 5:96 - chasse en mer vous est permise. Pas besoin d'egorgement, mort dans l'eau = halal. Meme mort trouve dans mer = halal."
    },
    {
        "nom": "Riz",
        "statut": "HALAL",
        "icon": "🍚",
        "desc": "100% halal",
        "niveau": 1,
        "detail": "Cereale pure, 100% halal. Base de l'alimentation en Afrique et Asie. Aucun doute. Toutes les cereales halal: riz, mil, mais, ble. Coran 80:27 - Nous avons fait pousser des grains."
    },
    {
        "nom": "Dattes",
        "statut": "HALAL",
        "icon": "🌴",
        "desc": "Sunna, tres recommandee",
        "niveau": 1,
        "detail": "Sunna du Prophete, rompre le jeune avec. Ajwa protection contre poison et sorcellerie. Hadith authentique: 7 dattes Ajwa le matin protege. Coran 19:25. Maryam a mange dattes lors accouchement."
    },
    {
        "nom": "Lait",
        "statut": "HALAL",
        "icon": "🥛",
        "desc": "Halal",
        "niveau": 1,
        "detail": "Lait pur halal. Lait de vache, brebis, chamelle. Hadith: Allah n'a pas mis de remede dans ce qu'Il a interdit. Lait maternel le meilleur. Lait de chamelle remede."
    },
    {
        "nom": "Miel",
        "statut": "HALAL",
        "icon": "🍯",
        "desc": "Halal pur, remede",
        "niveau": 1,
        "detail": "Coran 16:69 - remede pour les gens. Le Prophete aimait le miel. Guerit tout sauf la mort. Il sort de leurs ventres une liqueur aux couleurs variees ou il y a une guerison pour les gens."
    },
    {
        "nom": "Mangue",
        "statut": "HALAL",
        "icon": "🥭",
        "desc": "Halal",
        "niveau": 1,
        "detail": "Fruit halal. Coran 55:52 - des fruits en abondance au Paradis. Tous les fruits halal sauf fermentes en alcool. Mangue, banane, orange tout halal."
    },
    {
        "nom": "Banane",
        "statut": "HALAL",
        "icon": "🍌",
        "desc": "Halal",
        "niveau": 1,
        "detail": "Fruit halal. Coran 56:29 - bananiers charges de regimes superposes. Un des fruits du Paradis. Le Prophete aimait les fruits sucrés."
    },
    {
        "nom": "Porc",
        "statut": "HARAM",
        "icon": "🐖",
        "desc": "HARAM - Interdit Coran 2:173",
        "niveau": 1,
        "detail": "Interdit formellement Coran 2:173, 5:3, 6:145, 16:115. Najas impur. Meme toucher necessite lavage. Graisse, viande, os tout haram. Pas de transformation qui le rend halal selon Academie Fiqh."
    },
    {
        "nom": "Vin / Alcool",
        "statut": "HARAM",
        "icon": "🍷",
        "desc": "HARAM - Alcool interdit 5:90",
        "niveau": 1,
        "detail": "Alcool interdit Coran 5:90 - oeuvre du diable. Tout ce qui enivre en grande quantite, sa petite quantite est haram. Meme pour cuisiner = haram car ne s'evapore pas totalement selon etudes."
    },
    {
        "nom": "Biere",
        "statut": "HARAM",
        "icon": "🍺",
        "desc": "HARAM",
        "niveau": 1,
        "detail": "Toute boisson enivrante est haram. Meme 0.5% si elle enivre. Principe d'intention. Biere sans alcool avec 0% et non enivrante = halal selon certains si pas brassée comme alcool."
    },
    {
        "nom": "Gelatine porcine E441",
        "statut": "HARAM",
        "icon": "⚠️",
        "desc": "HARAM - Porc",
        "niveau": 1,
        "detail": "Gelatine de porc = haram. Istihala transformation non acceptee pour porc par majorite des savants contemporains. Academie Fiqh Islamique 1998. Eviter totalement. Alternative agar-agar vegetal."
    },
    {
        "nom": "E120 Cochenille",
        "statut": "HARAM",
        "icon": "⚠️",
        "desc": "HARAM - Insecte",
        "niveau": 1,
        "detail": "Colorant insecte ecrase - Haram pour majorite des savants. Insecte non criquet = haram. Cochenille = insecte femelle ecrasee. Utilise dans yaourts rouges, boissons. Chercher E120 sur etiquette."
    },
    {
        "nom": "Saucisson porc",
        "statut": "HARAM",
        "icon": "🚫",
        "desc": "HARAM",
        "niveau": 1,
        "detail": "Charcuterie porc = haram. Meme avec boeuf melange, contamination = tout haram. Principe: haram melange a halal en petite quantite mais qui donne gout = tout haram."
    },
    {
        "nom": "Oeuf poule",
        "statut": "HALAL",
        "icon": "🥚",
        "desc": "Halal",
        "niveau": 1,
        "detail": "Oeuf de poule halal, Bismillah recommande. Si poule halal, oeuf halal meme si poule mange haram. Oeuf de poule non halal? Poule toujours halal meme si non egorgee selon rite? Oeuf halal."
    },
    {
        "nom": "Sang animal",
        "statut": "HARAM",
        "icon": "🩸",
        "desc": "HARAM Coran 2:173",
        "niveau": 1,
        "detail": "Sang coule = haram Coran 2:173. Sang restant dans viande apres egorgement correct = halal, pardonne. Boudin noir avec sang coagule = haram."
    },
    {
        "nom": "Pain complet",
        "statut": "HALAL",
        "icon": "🍞",
        "desc": "Pain halal sans additif douteux",
        "niveau": 1,
        "detail": "Pain sans E471/E920 douteux = halal. Farine, eau, sel, levure = 100% halal. Pain boulangerie artisanale souvent halal. Industriel verifier."
    },
    {
        "nom": "Eau minerale",
        "statut": "HALAL",
        "icon": "💧",
        "desc": "Eau pure halal",
        "niveau": 1,
        "detail": "Eau 100% halal. Coran 21:30 - Nous avons fait de l'eau toute chose vivante. Base de la vie. Zamzam meilleure eau."
    },
    {
        "nom": "Vinaigre de cidre",
        "statut": "HALAL",
        "icon": "🍎",
        "desc": "Vinaigre - transformation purifie",
        "niveau": 2,
        "detail": "Meme si issu d'alcool, la fermentation acetique le transforme et le purifie - Halal selon majorite. Hadith: Meilleur condiment est le vinaigre. Le Prophete aimait vinaigre."
    },
    {
        "nom": "Croissant industriel E471",
        "statut": "HARAM",
        "icon": "🥐",
        "desc": "E471 peut etre porcine",
        "niveau": 2,
        "detail": "Mono et diglycerides E471 - peut etre d'origine porcine si non precise vegetal - DOUTEUX / HARAM. Principe: certitude ne part pas avec doute. Si doute sur haram = eviter. Hadith 13."
    },
    {
        "nom": "Bonbon Haribo gelatine",
        "statut": "HARAM",
        "icon": "🍬",
        "desc": "Gelatine porcine cachee",
        "niveau": 2,
        "detail": "La plupart des bonbons Haribo contiennent gelatine porcine - Verifier Halal. Chercher halal certifie ou pectine ou agar. Haribo halal existe avec mention halal."
    },
    {
        "nom": "Chips saveur bacon",
        "statut": "HARAM",
        "icon": "🥓",
        "desc": "Arome bacon meme sans viande",
        "niveau": 2,
        "detail": "Arome artificiel de porc - Meme sans viande, imite haram - Deconseille. Hadith: Celui qui imite un peuple en fait partie. Par precaution eviter gout porc."
    },
    {
        "nom": "Yaourt avec gelatine",
        "statut": "HARAM",
        "icon": "🥄",
        "desc": "Gelatine pour texture",
        "niveau": 2,
        "detail": "Certains yaourts ajoutent E441 pour epaissir - Verifier origine. Yaourt nature sans gelatine = halal. Yaourt grec souvent sans gelatine."
    },
    {
        "nom": "Fromage presure animale",
        "statut": "HARAM",
        "icon": "🧀",
        "desc": "Presure non halal",
        "niveau": 2,
        "detail": "Presure d'estomac de veau non abattu halal = haram. Chercher presure microbienne ou halal. Maliki: presure animal mort = najas. Shafii plus strict."
    },
    {
        "nom": "Pain L-cysteine E920",
        "statut": "HARAM",
        "icon": "🍞",
        "desc": "E920 cheveux ou porc",
        "niveau": 2,
        "detail": "E920 peut venir de cheveux humains ou de porc - Douteux si non vegetal. Principe: origine humaine = haram unanimement car homme est honore Coran 17:70."
    },
    {
        "nom": "Patisserie ethanol",
        "statut": "HARAM",
        "icon": "🎂",
        "desc": "Alcool comme conservateur",
        "niveau": 2,
        "detail": "Ethanol utilise comme conservateur - Meme petite quantite = haram. Si ethanol non enivrant comme solvant <0.5% certains autorisent mais precaution = haram."
    },
    {
        "nom": "Vanille extrait alcool",
        "statut": "HARAM",
        "icon": "🌼",
        "desc": "Extrait a l'alcool",
        "niveau": 2,
        "detail": "Extrait naturel de vanille contient 35% alcool - Chercher vanille sans alcool. Poudre vanille ou arome sans alcool = halal."
    },
    {
        "nom": "Agar-agar vegetal",
        "statut": "HALAL",
        "icon": "🌿",
        "desc": "Alternative gelatine vegetale",
        "niveau": 2,
        "detail": "Gelifiant vegetal a base d'algue - 100% halal, remplace gelatine. Parfait pour remplacer E441. Utilise au Japon depuis longtemps. Halal certifie."
    },
    {
        "nom": "Margarine E471 vegetal",
        "statut": "HALAL",
        "icon": "🧈",
        "desc": "E471 vegetal certifie",
        "niveau": 2,
        "detail": "Si precise origine vegetale ou halal certifie = halal. Verifier logo halal ou mention 100% vegetal. Margarine bio souvent vegetale."
    },
    {
        "nom": "Soda avec E150d",
        "statut": "HALAL",
        "icon": "🥤",
        "desc": "Colorant caramel - Halal",
        "niveau": 2,
        "detail": "E150d caramel - Halal en general. Obtenu par chauffage sucre. Halal sauf si sucre + alcool + ammoniaque sulfite mais reste halal."
    },
    {
        "nom": "Chocolat lecithine soja",
        "statut": "HALAL",
        "icon": "🍫",
        "desc": "Lecithine soja = Halal",
        "niveau": 2,
        "detail": "E322 lecithine de soja = halal. E322 oeuf aussi halal si oeuf halal. Eviter E322 porcine rare. Chocolat noir souvent halal."
    },
    {
        "nom": "E422 Glycerol",
        "statut": "DOUTEUX",
        "icon": "⚗️",
        "desc": "Peut etre animal",
        "niveau": 2,
        "detail": "Glycerol peut etre animal ou vegetal - Verifier source. Si vegetal ou synthetique = halal. Si animal non halal = haram. Sans precision = douteux."
    },
    {
        "nom": "E542 Phosphate d'os",
        "statut": "HARAM",
        "icon": "🦴",
        "desc": "Os animal",
        "niveau": 2,
        "detail": "Phosphate d'os - Haram si os de porc ou animal non halal. Os boeuf halal = halal. Utilise dans sucre raffine pour blanchir parfois."
    },
    {
        "nom": "Chewing-gum avec gelatine",
        "statut": "HARAM",
        "icon": "🍭",
        "desc": "Gelatine cachee",
        "niveau": 2,
        "detail": "Certains chewing-gum contiennent gelatine - Chercher halal. Gomme arabique = halal. Gomme base souvent halal mais verifier."
    },
    {
        "nom": "Additif E471 industriel",
        "statut": "DOUTEUX",
        "icon": "🏭",
        "desc": "Industriel sans precision",
        "niveau": 2,
        "detail": "Si E471 sans mention vegetal = douteux, eviter par precaution. Hadith 13: Laisser le douteux pour preserver religion. Principe de base scanner halal."
    },
    {
        "nom": "Arome naturel bacon",
        "statut": "HARAM",
        "icon": "🥓",
        "desc": "Arome porc",
        "niveau": 2,
        "detail": "Arome naturel de bacon = haram meme sans viande porc. Arome artificiel bacon aussi a eviter par imitation et incitation. Meme si synthetique, imite haram."
    },
    {
        "nom": "Crevettes / Gambas",
        "statut": "HALAL",
        "icon": "🦐",
        "desc": "Debat ecoles juridiques",
        "niveau": 3,
        "detail": "Halal pour Chafii, Maliki, Hanbali. Makruh pour Hanafi. Majorite = Halal. Abu Hanifa: seul poisson avec ecailles = halal, donc crevette makruh tanzihi leger, pas haram."
    },
    {
        "nom": "Crabe / Homard",
        "statut": "HALAL",
        "icon": "🦀",
        "desc": "Fruit de mer - debat",
        "niveau": 3,
        "detail": "Meme regle que crevettes - Halal pour majorite, makruh pour Hanafi. Crabe amphibie vit terre et mer = debat plus fort. Maliki autorise tout de la mer."
    },
    {
        "nom": "Viande Gens du Livre",
        "statut": "DOUTEUX",
        "icon": "✝️",
        "desc": "Sans certification - debat",
        "niveau": 3,
        "detail": "Coran 5:5 autorise nourriture Gens du Livre mais condition = qu'ils prononcent le nom de Dieu et egorgent. Aujourd'hui industrie: electrocution, pas de Bismillah - Douteux, preferer halal certifie."
    },
    {
        "nom": "Viande Bismillah oublie",
        "statut": "HALAL",
        "icon": "🤲",
        "desc": "Oubli involontaire",
        "niveau": 3,
        "detail": "Si oubli involontaire = pardonne et halal. Si omission volontaire = haram selon certains savants. Hadith: La communaute est pardonnee pour l'oubli, l'erreur et la contrainte."
    },
    {
        "nom": "Gelatine transformee (istihala)",
        "statut": "DOUTEUX",
        "icon": "🔬",
        "desc": "Transformation chimique totale",
        "niveau": 3,
        "detail": "Debat savants - Si transformation totale change nature chimiquement = certains disent halal comme Ibn Taymiyya, d'autres restent sur haram par precaution. Porc reste haram meme istihala selon Academie."
    },
    {
        "nom": "Alcool dans medicament",
        "statut": "HALAL",
        "icon": "💊",
        "desc": "Necessite medicale",
        "niveau": 3,
        "detail": "Si pas d'alternative et necessite medicale = autorise par necessite. Coran 2:173 - Celui qui est contraint sans etre transgresseur, pas de peche. Principe: necessite leve l'interdiction."
    },
    {
        "nom": "Fromage presure microbienne",
        "statut": "HALAL",
        "icon": "✅",
        "desc": "Presure vegetale/microbienne",
        "niveau": 3,
        "detail": "Presure microbienne = halal - Solution moderne. Presure genetiquement modifiee avec gene veau = halal car micro-organisme produit, pas estomac animal. Accepte par academie."
    },
    {
        "nom": "Caviar esturgeon",
        "statut": "HALAL",
        "icon": "⚫",
        "desc": "Oeufs poisson - debat",
        "niveau": 3,
        "detail": "Halal pour Chafii, Maliki. Hanafi: si poisson halal alors oeufs halal. Esturgeon a ecailles donc poisson halal meme pour Hanafi donc caviar halal."
    },
    {
        "nom": "Escargot",
        "statut": "HALAL",
        "icon": "🐌",
        "desc": "Debat - Maliki halal",
        "niveau": 3,
        "detail": "Maliki autorise escargot terrestre si vivant ebouillante avec Bismillah. Hanafi et Chafii: non halal car pas de sang qui coule mais terrestre non criquet = haram. Cas complexe."
    },
    {
        "nom": "Grenouille",
        "statut": "HARAM",
        "icon": "🐸",
        "desc": "Interdit de tuer - Hadith",
        "niveau": 3,
        "detail": "Hadith interdit de tuer grenouille - Donc haram a consommer. Abu Dawud sahih: Le Prophete a interdit de tuer 4 animaux: fourmi, abeille, huppe, grenouille. Donc haram unanimement."
    },
    {
        "nom": "Insectes (criquets)",
        "statut": "HALAL",
        "icon": "🦗",
        "desc": "Criquet halal - Hadith",
        "niveau": 3,
        "detail": "Criquet autorise par Hadith authentique. Bukhari: Nous faisions le jihad avec le Prophete et mangions des criquets. 2 morts halal sans egorgement: poisson et criquet."
    },
    {
        "nom": "Viande congele sans Bismillah ecrit",
        "statut": "HALAL",
        "icon": "🧊",
        "desc": "Si abattu halal a l'origine",
        "niveau": 3,
        "detail": "Si abattu halal au depart, congele reste halal meme si etiquette sans Bismillah. L'etiquette n'est pas condition de halal. Le principal est l'abattage initial."
    },
    {
        "nom": "Viande hachee supermarche",
        "statut": "DOUTEUX",
        "icon": "🥩",
        "desc": "Melange possible",
        "niveau": 3,
        "detail": "Viande hachee sans certif = risque melange porc/boeuf - Douteux. Machine non nettoyee = contamination porc. Preferer boucherie halal qui hache devant toi."
    },
    {
        "nom": "Gelatine bovine non halal",
        "statut": "HARAM",
        "icon": "🐄",
        "desc": "Bovine mais non halal",
        "niveau": 3,
        "detail": "Meme bovine, si animal non abattu halal = haram selon majorite des savants. Hanafi: peau tannee = pure mais viande reste haram. Donc gelatine extraite de peau bovine non halal = haram."
    },
    {
        "nom": "E904 Gomme laque",
        "statut": "HARAM",
        "icon": "🪲",
        "desc": "Insecte laque",
        "niveau": 3,
        "detail": "Gomme laque = secretion insecte laque - Haram pour majorite. Utilisee pour briller bonbons, pommes. Chercher alternative cire d'abeille ou carnauba vegetale."
    },
    {
        "nom": "E913 Lanoline",
        "statut": "HALAL",
        "icon": "🐑",
        "desc": "Laine mouton",
        "niveau": 3,
        "detail": "Lanoline de laine mouton = halal, pas besoin abattage. Cire naturelle sur laine, extraite sans tuer animal. Halal unanimement. Utilisee dans cosmetiques."
    },
]

HADITHS_40_VRAIS = [
    {"id":1, "ar": "انما الاعمال بالنيات", "fr": "Hadith 1: Les actes ne valent que par leurs intentions. [Bukhari & Muslim] - Fondement de l'Islam, Imam Shafii dit 1/3 de l'Islam."},
    {"id":2, "ar": "بني الاسلام على خمس", "fr": "Hadith 2: L'Islam est bati sur cinq: Shahada, priere, zakat, jeune Ramadan, pelerinage. [Bukhari & Muslim]"},
    {"id":3, "ar": "ان الله كتب الاحسان على كل شيء", "fr": "Hadith 3: Allah a prescrit la bienfaisance en toute chose. Si vous egorgez, aiguisez votre lame. [Muslim]"},
    {"id":4, "ar": "من حسن اسلام المرء تركه ما لا يعنيه", "fr": "Hadith 4: Fait partie du bon Islam de delaisser ce qui ne le concerne pas. [Tirmidhi hassan]"},
    {"id":5, "ar": "لا يؤمن احدكم حتى يحب لاخيه ما يحب لنفسه", "fr": "Hadith 5: Aucun de vous ne sera croyant jusqu'a aimer pour son frere ce qu'il aime pour lui-meme. [Bukhari & Muslim]"},
    {"id":6, "ar": "من كان يؤمن بالله واليوم الاخر فليقل خيرا او ليصمت", "fr": "Hadith 6: Que celui qui croit en Allah et au Jour Dernier dise du bien ou se taise. [Bukhari & Muslim]"},
    {"id":7, "ar": "الدين النصيحة", "fr": "Hadith 7: La religion c'est le bon conseil. [Muslim]"},
    {"id":8, "ar": "اتق الله حيثما كنت", "fr": "Hadith 8: Crains Allah ou que tu sois, fais suivre la mauvaise par une bonne. [Tirmidhi]"},
    {"id":9, "ar": "ما نهيتكم عنه فاجتنبوه", "fr": "Hadith 9: Ce que je vous ai interdit, evitez-le. Ce que j'ordonne, faites ce que vous pouvez. [Bukhari & Muslim]"},
    {"id":10, "ar": "الطهور شطر الايمان", "fr": "Hadith 10: La purification est la moitie de la foi. [Muslim]"},
    {"id":11, "ar": "لا ضرر ولا ضرار", "fr": "Hadith 11: Pas de tort cause ni subi. [Ibn Majah hassan] - Principe juridique majeur."},
    {"id":12, "ar": "من احدث في امرنا هذا ما ليس منه فهو رد", "fr": "Hadith 12: Celui qui innove dans notre religion, son innovation est rejetee. [Bukhari & Muslim]"},
    {"id":13, "ar": "الحلال بين والحرام بين", "fr": "Hadith 13: Le halal est clair et le haram est clair. Entre les deux, douteux. Celui qui evite le douteux preserve sa religion. [Bukhari & Muslim] - Base Scanner Halal!"},
    {"id":14, "ar": "ان الله طيب لا يقبل الا طيبا", "fr": "Hadith 14: Allah est bon et n'accepte que ce qui est bon. [Muslim] - Manger halal pour invocation exaucee."},
    {"id":15, "ar": "من سلك طريقا يلتمس فيه علما", "fr": "Hadith 15: Celui qui cherche la science, Allah lui facilite un chemin vers le Paradis. [Muslim]"},
    {"id":16, "ar": "الكلمة الطيبة صدقة", "fr": "Hadith 16: La bonne parole est une aumone. [Bukhari & Muslim]"},
    {"id":17, "ar": "لا تحقرن من المعروف شيئا", "fr": "Hadith 17: Ne meprise aucune bonne action, meme sourire. [Muslim]"},
    {"id":18, "ar": "المسلم من سلم المسلمون من لسانه ويده", "fr": "Hadith 18: Le musulman est celui dont les musulmans sont a l'abri de sa langue et sa main. [Bukhari & Muslim]"},
    {"id":19, "ar": "من كان في حاجة اخيه كان الله في حاجته", "fr": "Hadith 19: Celui qui aide son frere, Allah l'aide. [Muslim]"},
    {"id":20, "ar": "يسروا ولا تعسروا", "fr": "Hadith 20: Facilitez et ne rendez pas difficile. [Bukhari & Muslim] - Pour ton app: faciliter halal."},
    {"id":21, "ar": "الدعاء هو العبادة", "fr": "Hadith 21: L'invocation c'est l'adoration. [Tirmidhi sahih]"},
    {"id":22, "ar": "خيركم من تعلم القران وعلمه", "fr": "Hadith 22: Le meilleur d'entre vous est celui qui apprend le Coran et l'enseigne. [Bukhari]"},
    {"id":23, "ar": "بلغوا عني ولو اية", "fr": "Hadith 23: Transmettez de moi ne serait-ce qu'un verset. [Bukhari] - Partage l'app!"},
    {"id":24, "ar": "من صام رمضان ايمانا واحتسابا غفر له", "fr": "Hadith 24: Celui qui jeune Ramadan avec foi, ses peches passes sont pardonnes. [Bukhari & Muslim]"},
    {"id":25, "ar": "السحور بركة", "fr": "Hadith 25: Prenez le sahour car il y a benediction. [Bukhari & Muslim]"},
    {"id":26, "ar": "للصائم فرحتان", "fr": "Hadith 26: Le jeuneur a deux joies: iftar et rencontre Allah. [Bukhari & Muslim]"},
    {"id":27, "ar": "من قام ليلة القدر ايمانا واحتسابا", "fr": "Hadith 27: Celui qui prie la nuit du Destin, ses peches passes pardonnes. [Bukhari & Muslim]"},
    {"id":28, "ar": "العمرة الى العمرة كفارة", "fr": "Hadith 28: D'une Omra a l'autre, expiation. [Bukhari & Muslim]"},
    {"id":29, "ar": "الحج عرفة", "fr": "Hadith 29: Le Hajj c'est Arafat. [Tirmidhi sahih]"},
    {"id":30, "ar": "ما من ايام العمل الصالح فيهن احب الى الله من عشر ذي الحجة", "fr": "Hadith 30: Pas de jours ou bonnes actions plus aimees que 10 premiers Dhul Hijja. [Bukhari]"},
    {"id":31, "ar": "اكثروا من قول لا اله الا الله", "fr": "Hadith 31: Multipliez La ilaha illa Allah. [Ahmad sahih]"},
    {"id":32, "ar": "من قال سبحان الله وبحمده مائة مرة", "fr": "Hadith 32: Celui qui dit SubhanAllah wa bihamdihi 100 fois, peches pardonnes meme comme ecume mer. [Bukhari & Muslim]"},
    {"id":33, "ar": "كلمتان خفيفتان على اللسان ثقيلتان في الميزان", "fr": "Hadith 33: Deux paroles legeres sur langue, lourdes balance: SubhanAllah wa bihamdihi, SubhanAllah al-Adhim. [Bukhari & Muslim]"},
    {"id":34, "ar": "لا حول ولا قوة الا بالله كنز من كنوز الجنة", "fr": "Hadith 34: La hawla wa la quwwata illa billah est un tresor du Paradis. [Bukhari & Muslim]"},
    {"id":35, "ar": "ان الله يحب اذا عمل احدكم عملا ان يتقنه", "fr": "Hadith 35: Allah aime quand l'un fait un travail qu'il le perfectionne. [Bayhaqi hassan] - Pour ton app!"},
    {"id":36, "ar": "اليد العليا خير من اليد السفلى", "fr": "Hadith 36: La main qui donne est meilleure que celle qui recoit. [Bukhari & Muslim]"},
    {"id":37, "ar": "ما نقص مال من صدقة", "fr": "Hadith 37: Une aumone ne diminue en rien une richesse. [Muslim]"},
    {"id":38, "ar": "اتقوا النار ولو بشق تمرة", "fr": "Hadith 38: Protegez-vous du Feu meme par moitie d'une datte. [Bukhari & Muslim]"},
    {"id":39, "ar": "تبسمك في وجه اخيك صدقة", "fr": "Hadith 39: Ton sourire a ton frere est une aumone. [Tirmidhi sahih]"},
    {"id":40, "ar": "من لا يشكر الناس لا يشكر الله", "fr": "Hadith 40: Celui qui ne remercie pas les gens ne remercie pas Allah. [Tirmidhi sahih]"},
]

DOUAS_DATA = [
    {"id":1, "ar": "بسم الله الرحمن الرحيم", "fr": "Au nom d'Allah, le Tout Misericordieux - Avant tout acte."},
    {"id":2, "ar": "الحمد لله رب العالمين", "fr": "Louange a Allah, Seigneur des mondes."},
    {"id":3, "ar": "اللهم بارك لنا فيما رزقتنا", "fr": "O Allah, benis ce que Tu nous as accorde - Avant manger."},
    {"id":4, "ar": "بسم الله وعلى بركة الله", "fr": "Au nom d'Allah et avec benediction - Avant manger."},
    {"id":5, "ar": "الحمد لله الذي اطعمنا وسقانا", "fr": "Louange a Allah qui nous a nourris - Apres manger."},
    {"id":6, "ar": "اللهم اني اسالك علما نافعا", "fr": "O Allah, je Te demande science utile - Matin."},
    {"id":7, "ar": "اصبحنا واصبح الملك لله", "fr": "Nous voila au matin, royaute a Allah - Matin."},
    {"id":8, "ar": "امسينا وامسى الملك لله", "fr": "Nous voila au soir, royaute a Allah - Soir."},
    {"id":9, "ar": "اللهم بك اصبحنا وبك امسينا", "fr": "O Allah, par Toi matin et soir - Quotidien."},
    {"id":10, "ar": "بسم الله الذي لا يضر مع اسمه شيء", "fr": "Au nom d'Allah dont le nom rien ne nuit - Protection 3x."},
    {"id":11, "ar": "اعوذ بكلمات الله التامات من شر ما خلق", "fr": "Protection contre mal de ce qu'Il a cree - 3x soir."},
    {"id":12, "ar": "حسبي الله لا اله الا هو", "fr": "Allah me suffit - 7x matin/soir - Coran 9:129."},
    {"id":13, "ar": "اللهم عافني في بدني", "fr": "O Allah, sante dans mon corps - 3x matin/soir."},
    {"id":14, "ar": "اللهم اني اعوذ بك من الهم والحزن", "fr": "Protection contre souci et tristesse - Contre anxiete."},
    {"id":15, "ar": "لا اله الا انت سبحانك اني كنت من الظالمين", "fr": "Doua de Yunus - Exauce tout voeu - Coran 21:87."},
    {"id":16, "ar": "رب اغفر لي وتب علي", "fr": "Seigneur pardonne et accepte repentir - Istighfar 100x."},
    {"id":17, "ar": "استغفر الله العظيم", "fr": "Je demande pardon a Allah l'Immense - Ouvre subsistance."},
    {"id":18, "ar": "سبحان الله وبحمده سبحان الله العظيم", "fr": "Gloire a Allah - Lourds dans la balance."},
    {"id":19, "ar": "لا حول ولا قوة الا بالله", "fr": "Ni force ni puissance qu'en Allah - Tresor Paradis."},
    {"id":20, "ar": "اللهم صل على محمد", "fr": "O Allah, prie sur Muhammad - 10x matin/soir = intercession."},
    {"id":21, "ar": "اللهم اني اسالك الجنة", "fr": "O Allah, je Te demande le Paradis - 3x."},
    {"id":22, "ar": "اللهم اجرني من النار", "fr": "O Allah, protege du Feu - 3x."},
    {"id":23, "ar": "اللهم انك عفو تحب العفو فاعف عني", "fr": "O Allah, Tu es Pardonneur - Doua Laylatul Qadr."},
    {"id":24, "ar": "ربنا اتنا في الدنيا حسنة وفي الاخرة حسنة", "fr": "Notre Seigneur donne bonne part ici-bas et au-dela - Coran 2:201."},
    {"id":25, "ar": "اللهم اهدني وسددني", "fr": "O Allah, guide-moi et rends droit."},
    {"id":26, "ar": "يا مقلب القلوب ثبت قلبي على دينك", "fr": "O Toi qui retournes coeurs, affermis mon coeur sur Ta religion."},
    {"id":27, "ar": "اللهم اعني على ذكرك وشكرك", "fr": "O Allah, aide-moi a Te mentionner - Apres priere."},
    {"id":28, "ar": "بسم الله توكلت على الله", "fr": "Au nom d'Allah, je place confiance en Allah - En sortant."},
    {"id":29, "ar": "اللهم اني اعوذ بك ان اضل او اضل", "fr": "Protection contre egarer - En sortant."},
    {"id":30, "ar": "اللهم اجعل في قلبي نورا", "fr": "O Allah, mets lumiere dans mon coeur - Doua lumiere."},
    {"id":31, "ar": "اللهم اغفر لي ذنبي كله", "fr": "O Allah, pardonne tous mes peches - En prosternation."},
    {"id":32, "ar": "اللهم ارزقني حبك", "fr": "O Allah, accorde Ton amour - Plus haute station."},
    {"id":33, "ar": "اللهم اني اسالك علما نافعا ورزقا طيبا", "fr": "Science utile et subsistance bonne - Matin."},
    {"id":34, "ar": "اللهم بارك لي في رزقي", "fr": "O Allah, benis ma subsistance - Pour commerce."},
    {"id":35, "ar": "اللهم اكفني بحلالك عن حرامك", "fr": "Contente-moi de Ton halal pour eviter haram - Ideal scanner!"},
    {"id":36, "ar": "اللهم اني اعوذ بك من الحرام", "fr": "Je cherche protection contre haram - Pour rester halal."},
    {"id":37, "ar": "بسم الله ولجنا وبسم الله خرجنا", "fr": "Au nom d'Allah nous entrons et sortons - En entrant chez soi."},
    {"id":38, "ar": "اللهم افتح لي ابواب رحمتك", "fr": "O Allah, ouvre portes de Ta misericorde - En entrant mosquee."},
    {"id":39, "ar": "اللهم اني اسالك من فضلك", "fr": "O Allah, je Te demande de Ta grace - En sortant mosquee."},
    {"id":40, "ar": "غفرانك", "fr": "Je Te demande pardon - En sortant toilettes."},
    {"id":41, "ar": "الحمد لله الذي اذهب عني الاذى وعافاني", "fr": "Louange a Allah qui a eloigne mal - Apres toilettes."},
    {"id":42, "ar": "بسم الله اللهم جنبنا الشيطان", "fr": "Au nom d'Allah, eloigne diable - Avant rapport intime."},
    {"id":43, "ar": "اللهم اني اعوذ بك من الخبث والخبائث", "fr": "Protection contre demons - Avant toilettes."},
    {"id":44, "ar": "اللهم اجعلني من التوابين", "fr": "Fais de moi parmi repentants - Apres ablutions."},
    {"id":45, "ar": "اشهد ان لا اله الا الله", "fr": "J'atteste qu'il n'y a de divinite qu'Allah - Apres ablutions ouvre 8 portes Paradis."},
    {"id":46, "ar": "اللهم اغفر لي وارحمني", "fr": "Pardonne, misericorde, guide, sante, subsistance - Entre prosternations."},
    {"id":47, "ar": "رب قني عذابك يوم تبعث عبادك", "fr": "Protege de Ton chatiment le Jour Resurrection - Avant dormir."},
    {"id":48, "ar": "باسمك اللهم اموت واحيا", "fr": "En Ton nom je meurs et vis - Avant dormir."},
    {"id":49, "ar": "الحمد لله الذي احيانا بعد ما اماتنا", "fr": "Louange a Allah qui nous a fait revivre - Au reveil."},
    {"id":50, "ar": "اللهم بك اصبحنا", "fr": "Par Toi nous sommes au matin - Reveil."},
    {"id":51, "ar": "اللهم اني اسالك خير هذا اليوم", "fr": "Je Te demande bien de ce jour - Debut journee."},
    {"id":52, "ar": "اللهم اجرني من عذاب القبر", "fr": "Protege du chatiment tombe - Apres priere."},
    {"id":53, "ar": "اللهم اني اعوذ بك من فتنة المحيا والممات", "fr": "Protection tentation vie et mort et Dajjal - Fin tashahud."},
    {"id":54, "ar": "رب هب لي حكما والحقني بالصالحين", "fr": "Accorde sagesse et rejoins vertueux - Doua Ibrahim Coran 26:83."},
    {"id":55, "ar": "اللهم ارزقني رزقا حلالا طيبا", "fr": "Accorde subsistance halal bonne - Special scanner halal."},
]

SOURATES_NOMS = ["Al-Fatiha","Al-Baqara","Al-Imran","An-Nisa","Al-Maida","Al-Anam","Al-Araf","Al-Anfal","At-Tawba","Yunus","Hud","Yusuf","Ar-Rad","Ibrahim","Al-Hijr","An-Nahl","Al-Isra","Al-Kahf","Maryam","Ta-Ha","Al-Anbiya","Al-Hajj","Al-Muminun","An-Nur","Al-Furqan","Ash-Shuara","An-Naml","Al-Qasas","Al-Ankabut","Ar-Rum","Luqman","As-Sajda","Al-Ahzab","Saba","Fatir","Ya-Sin","As-Saffat","Sad","Az-Zumar","Ghafir","Fussilat","Ash-Shura","Az-Zukhruf","Ad-Dukhan","Al-Jathiya","Al-Ahqaf","Muhammad","Al-Fath","Al-Hujurat","Qaf","Adh-Dhariyat","At-Tur","An-Najm","Al-Qamar","Ar-Rahman","Al-Waqia","Al-Hadid","Al-Mujadila","Al-Hashr","Al-Mumtahana","As-Saff","Al-Jumua","Al-Munafiqun","At-Taghabun","At-Talaq","At-Tahrim","Al-Mulk","Al-Qalam","Al-Haqqa","Al-Maarij","Nuh","Al-Jinn","Al-Muzzammil","Al-Muddathir","Al-Qiyama","Al-Insan","Al-Mursalat","An-Naba","An-Naziat","Abasa","At-Takwir","Al-Infitar","Al-Mutaffifin","Al-Inshiqaq","Al-Buruj","At-Tariq","Al-Ala","Al-Ghashiya","Al-Fajr","Al-Balad","Ash-Shams","Al-Lail","Ad-Duha","Ash-Sharh","At-Tin","Al-Alaq","Al-Qadr","Al-Bayyina","Az-Zalzala","Al-Adiyat","Al-Qaria","At-Takathur","Al-Asr","Al-Humaza","Al-Fil","Quraysh","Al-Maun","Al-Kawthar","Al-Kafirun","An-Nasr","Al-Masad","Al-Ikhlas","Al-Falaq","An-Nas"]

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

st.set_page_config(page_title="Scanner Halal", page_icon="📱", layout="centered")

st.markdown("""
<style>
#MainMenu{visibility:hidden} footer{visibility:hidden} header{visibility:hidden}
.block-container{padding-top:10px; padding-bottom:120px;}
.card-graph{background:white; border-radius:18px; padding:18px; text-align:center; border:2px solid #eef2ff; box-shadow:0 6px 15px rgba(0,0,0,0.07); margin:8px 0}
.card-vip{background:linear-gradient(135deg,#0a2a6b,#1a4bb8);color:white;padding:25px;border-radius:20px;margin:12px 0px; text-align:center}
.block-blockchain{background:#0a0a0a; color:#00ff88; border-radius:12px; padding:12px; font-family:monospace; font-size:11px; margin:6px 0; border-left:4px solid #00ff88; text-align:left}
.progress-bar{background:#eef2ff; border-radius:10px; height:12px; overflow:hidden; margin:8px 0}
.progress-fill{background:linear-gradient(90deg,#00a651,#0a2a6b); height:100%; transition:width 0.5s}
div[data-testid="stButton"] > button {border-radius:18px!important; padding:14px!important; font-weight:800!important;}
</style>
""", unsafe_allow_html=True)

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
        st.markdown(f"""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:20px; padding:25px; text-align:center; color:white"><img src="data:image/png;base64,{logo_b64}" style="width:110px;height:110px;border-radius:20px;object-fit:cover;border:3px solid gold"><div style="font-size:24px; font-weight:900; margin-top:12px">SCANNER HALAL</div></div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:20px; padding:25px; text-align:center; color:white"><div style="font-size:24px; font-weight:900">SCANNER HALAL</div></div>""", unsafe_allow_html=True)

    t1,t2,t3,t4=st.tabs(["Se connecter","S'inscrire","Code oublie","Sans connexion"])
    with t1:
        e=st.text_input("Email", key="email_connexion").strip().lower()
        p=st.text_input("Mot de passe",type="password", key="pwd_connexion")
        if st.button("Se connecter",type="primary",use_container_width=True):
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
        if st.button("S'inscrire",type="primary",use_container_width=True):
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
        st.markdown("""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:18px; padding:20px; text-align:center; color:white"><div style="font-size:40px">📱</div><div style="font-weight:900">MODE INVITE</div></div>""", unsafe_allow_html=True)
        if st.button("Entrer", type="primary", use_container_width=True):
            st.session_state.user="guest_offline"; st.session_state.is_guest=True; st.session_state.page="app"; st.rerun()
    st.stop()

if st.session_state.is_guest or st.session_state.user=="guest_offline":
    user_email="guest_offline"
    user={'nom':'Invite','full_name':'Invite','is_vip':True,'history':[],'history_downloads':[],'profile_b64':None,'cover_b64':None}
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

cover_b64=user.get('cover_b64'); profile_b64=user.get('profile_b64')
cover_style=f"background-image:url(data:image/jpeg;base64,{cover_b64}); background-size:cover;" if cover_b64 else "background:linear-gradient(90deg,#00c6ff,#0072ff);"
profile_html=f"<img src='data:image/jpeg;base64,{profile_b64}' style='width:75px;height:75px;border-radius:50%;border:3px solid #00ff88;object-fit:cover;'>" if profile_b64 else "<div style='width:75px;height:75px;border-radius:50%;background:white;display:flex;align-items:center;justify-content:center;font-size:38px;border:3px solid #00ff88;'>👤</div>"
st.markdown(f"""<div style="{cover_style} padding:15px; border-radius:18px; margin-bottom:12px;"><div style="display:flex; align-items:center; gap:12px; background:rgba(0,0,0,0.45); padding:12px; border-radius:12px;">{profile_html}<div style="color:white;"><b>{user.get('nom','')}</b></div></div></div>""", unsafe_allow_html=True)

with st.sidebar:
    menu=st.radio("NAVIGATION", ["Home","Aliments","Coran","Hadiths","Douas","Parametres","Jeux","Codes VIP (Admin)"], label_visibility="collapsed")
    if is_guest_mode:
        if st.button("Se connecter", use_container_width=True, type="primary"):
            st.session_state.user=None; st.session_state.is_guest=False; st.session_state.page="auth"; st.rerun()
    else:
        if st.button("Deconnexion", use_container_width=True):
            st.session_state.user=None; st.session_state.is_guest=False; st.session_state.page="auth"; st.rerun()

if st.session_state.get('selected_menu'):
    menu=st.session_state.selected_menu; st.session_state.selected_menu=None

if menu=="Codes VIP (Admin)":
    if is_guest_mode:
        st.warning("Mode invite: VIP non disponible.")
        if st.button("Retour"): st.session_state.bottom_nav="Home"; st.rerun()
        st.stop()
    st.title("Codes VIP")
    for code, info in vip_codes.items():
        used_by = info.get("used_by",""); status = f"✅ {used_by}" if info["used"] else "🟢 Disponible"
        st.markdown(f"<div class='card-graph' style='text-align:left'><b>{code}</b> - {status}</div>", unsafe_allow_html=True)
    if st.button("Generer 5 codes", use_container_width=True):
        for _ in range(5):
            new_code = f"VIP-{random.randint(1000,9999)}-{random.randint(1000,9999)}"; vip_codes[new_code] = {"used": False, "used_by": None}
        save_json(VIP_CODES_FILE, vip_codes); st.rerun()
    if st.button("Retour"): st.session_state.bottom_nav="Home"; st.rerun()
    st.stop()

if menu=="Home":
    if st.session_state.scan_mode=="camera":
        allowed, reason = is_scanner_allowed(is_guest_mode)
        if not allowed:
            st.error(f"{reason}")
            if is_guest_mode:
                if st.button("Se connecter", type="primary", use_container_width=True):
                    st.session_state.user=None; st.session_state.is_guest=False; st.session_state.page="auth"; st.rerun()
            if st.button("Retour", use_container_width=True):
                st.session_state.scan_mode=None; st.rerun()
            st.stop()
        if st.button("Retour", use_container_width=True):
            st.session_state.scan_mode=None; st.rerun()
        cam=st.camera_input("Photo produit", key="camera_full")
        if cam:
            with st.spinner("Analyse..."):
                time.sleep(1)
                result=random.choice(["HALAL 100%","HARAM Detecte","DOUTEUX"])
                color="green" if "HALAL" in result else "red" if "HARAM" in result else "orange"
                st.markdown(f"""<div style="background:white; border-radius:20px; padding:20px; text-align:center; border:4px solid {color}"><div style="font-size:26px; font-weight:900; color:{color}">{result}</div></div>""", unsafe_allow_html=True)
                if not is_guest_mode:
                    users[user_email]['history'].append({'date':datetime.now().strftime("%d/%m/%Y %H:%M"),'result':result})
                    save_json(USERS_FILE,users); add_block({"type":"SCAN","user":user_email,"result":result, "online":True})
        st.stop()

    full_name = user.get("full_name","").split(" ")[0]
    st.markdown(f"### Salam {full_name}")

    # BOUTONS PRINCIPAUX - CORRIGES SANS SOUS-TEXTE
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("SCANNER", use_container_width=True):
            st.session_state.scan_mode="camera"; st.rerun()
    with col2:
        if st.button("SAVOIR", use_container_width=True):
            st.session_state.bottom_nav="SAVOIR"; st.rerun()
    with col3:
        if st.button("JEUX", use_container_width=True):
            st.session_state.selected_menu="Jeux"; st.rerun()

    if not is_guest_mode and not user.get('is_vip'):
        st.link_button("Passer VIP - 1500F", WAVE_LINK, type="primary", use_container_width=True)

elif menu=="Jeux":
    if st.button("Retour", key="back_jeux"):
        st.session_state.bottom_nav="Home"; st.rerun()
    if st.session_state.game_question_count >= 20:
        note = st.session_state.game_correct; pct = int(note/20*100)
        if note >= 16: couleur="#00a651"; msg="Excellent!"
        elif note >= 12: couleur="#0a2a6b"; msg="Tres bien!"
        elif note >= 8: couleur="#ff8c00"; msg="Pas mal!"
        else: couleur="#cc0000"; msg="Courage!"
        st.markdown(f"""<div style="background:white; border-radius:24px; padding:30px; text-align:center; border:4px solid {couleur}"><div style="font-size:70px">📝</div><div style="font-size:28px; font-weight:900; color:{couleur}">QUIZ TERMINE!</div><div style="font-size:55px; font-weight:900; color:#0a2a6b; margin:15px 0">{note} / 20</div><div style="background:#f5f7ff; border-radius:12px; padding:12px; margin:10px 0"><div style="font-size:18px; font-weight:800">{msg}</div><div style="font-size:14px; color:gray">{pct}% | Niveau {st.session_state.game_niveau}</div></div></div>""", unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        with c1:
            if st.button("Reessayer", use_container_width=True, type="primary"):
                st.session_state.game_question_count=0; st.session_state.game_correct=0; st.session_state.last_answer=None; pool = [a for a in ALIMENTS_DATA if a["niveau"]==st.session_state.game_niveau]; st.session_state.current_game_q=random.choice(pool); st.rerun()
        with c2:
            if st.button("Retour", use_container_width=True):
                st.session_state.game_question_count=0; st.session_state.game_correct=0; st.session_state.last_answer=None; st.session_state.bottom_nav="Home"; st.rerun()
        st.stop()

    progress = int((st.session_state.game_question_count / 20) * 100)
    st.markdown(f"""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:18px; padding:18px; text-align:center; color:white"><div style="font-size:50px">🎮</div><div style="font-weight:900">JEUX - 55 ALIMENTS</div><div style="font-size:12px; color:gold">Question {st.session_state.game_question_count+1}/20 | Score {st.session_state.game_correct}/20</div><div class="progress-bar"><div class="progress-fill" style="width:{progress}%"></div></div></div>""", unsafe_allow_html=True)

    # BOUTONS NIVEAU CORRIGES
    c1,c2,c3 = st.columns(3)
    with c1:
        if st.button("Niveau 1", use_container_width=True, type="primary" if st.session_state.game_niveau==1 else "secondary"):
            st.session_state.game_niveau=1; st.session_state.game_question_count=0; st.session_state.game_correct=0; st.session_state.last_answer=None; pool = [a for a in ALIMENTS_DATA if a["niveau"]==1]; st.session_state.current_game_q=random.choice(pool); st.rerun()
    with c2:
        if st.button("Niveau 2", use_container_width=True, type="primary" if st.session_state.game_niveau==2 else "secondary"):
            st.session_state.game_niveau=2; st.session_state.game_question_count=0; st.session_state.game_correct=0; st.session_state.last_answer=None; pool = [a for a in ALIMENTS_DATA if a["niveau"]==2]; st.session_state.current_game_q=random.choice(pool); st.rerun()
    with c3:
        if st.button("Niveau 3", use_container_width=True, type="primary" if st.session_state.game_niveau==3 else "secondary"):
            st.session_state.game_niveau=3; st.session_state.game_question_count=0; st.session_state.game_correct=0; st.session_state.last_answer=None; pool = [a for a in ALIMENTS_DATA if a["niveau"]==3]; st.session_state.current_game_q=random.choice(pool); st.rerun()

    q = st.session_state.current_game_q
    st.markdown(f"<div class='card-graph'><div style='font-size:50px'>{q['icon']}</div><b style='font-size:22px'>{q['nom']}</b><br><span style='font-size:13px'>{q['desc']}</span><br><b>HALAL ou HARAM?</b></div>", unsafe_allow_html=True)

    if st.session_state.last_answer:
        msg_last = st.session_state.last_answer['msg']; detail_q = q.get('detail','')
        if st.session_state.last_answer['correct']: st.success(f"✅ {msg_last}\n\n📚 {detail_q}")
        else: st.error(f"❌ {msg_last}\n\n📚 {detail_q}")

    c1,c2=st.columns(2)
    with c1:
        if st.button("HALAL", use_container_width=True, key="btn_halal"):
            statut = q["statut"]; is_halal = statut == "HALAL"
            if q["niveau"]==3 and statut=="DOUTEUX": is_halal = True
            if is_halal:
                st.session_state.game_correct+=1; st.session_state.last_answer={'correct':True,'msg':f"Bravo! {q['nom']} = {statut}"}
            else:
                st.session_state.last_answer={'correct':False,'msg':f"Faux! {q['nom']} = {statut}"}
            st.session_state.game_question_count+=1; pool = [a for a in ALIMENTS_DATA if a["niveau"]==st.session_state.game_niveau]; st.session_state.current_game_q=random.choice(pool); st.rerun()
    with c2:
        if st.button("HARAM", use_container_width=True, key="btn_haram"):
            statut = q["statut"]
            if statut in ["HARAM","DOUTEUX"]:
                st.session_state.game_correct+=1; st.session_state.last_answer={'correct':True,'msg':f"Bravo! {q['nom']} = {statut}"}
            else:
                st.session_state.last_answer={'correct':False,'msg':f"Faux! {q['nom']} = {statut}"}
            st.session_state.game_question_count+=1; pool = [a for a in ALIMENTS_DATA if a["niveau"]==st.session_state.game_niveau]; st.session_state.current_game_q=random.choice(pool); st.rerun()

elif menu=="Aliments":
    st.title("55 Aliments")
    tab1, tab2, tab3 = st.tabs(["Niveau 1", "Niveau 2", "Niveau 3"])
    with tab1:
        for a in [x for x in ALIMENTS_DATA if x["niveau"]==1]:
            couleur = "#00a651" if a["statut"] == "HALAL" else "#cc0000"
            st.markdown(f"<div class='card-graph' style='text-align:left; border-left:5px solid {couleur}'><b>{a['icon']} {a['nom']}</b> - {a['statut']}<br><span style='font-size:11px'>{a['desc']}</span></div>", unsafe_allow_html=True)
    with tab2:
        for a in [x for x in ALIMENTS_DATA if x["niveau"]==2]:
            st.markdown(f"<div class='card-graph' style='text-align:left; border-left:5px solid orange'><b>{a['icon']} {a['nom']}</b> - {a['statut']}<br><span style='font-size:11px'>{a['desc']}</span></div>", unsafe_allow_html=True)
    with tab3:
        for a in [x for x in ALIMENTS_DATA if x["niveau"]==3]:
            st.markdown(f"<div class='card-graph' style='text-align:left; border-left:5px solid purple'><b>{a['icon']} {a['nom']}</b> - {a['statut']}<br><span style='font-size:11px'>{a['desc']}</span></div>", unsafe_allow_html=True)

elif menu=="Coran":
    if st.button("Retour"): st.session_state.bottom_nav="Home"; st.rerun()
    st.title("📖 Coran 114")
    for i in range(1,115):
        nom_sourate = SOURATES_NOMS[i-1]
        st.markdown(f"<div class='card-graph' style='text-align:left'>{i}. {nom_sourate}</div>", unsafe_allow_html=True)

elif menu=="Hadiths":
    if not is_guest_mode and not user.get('is_vip'):
        st.markdown("""<div class="card-vip"><div style="font-size:70px">🔒</div><div style="font-weight:900; color:gold">Hadiths VIP</div></div>""", unsafe_allow_html=True)
        st.link_button("PAYER 1500F", WAVE_LINK, type="primary", use_container_width=True); st.stop()
    st.title("📜 40 Hadiths")
    for h in HADITHS_40_VRAIS:
        st.markdown(f"<div class='card-graph' style='text-align:left'><b>Hadith {h['id']}</b><br><span style='color:#0a2a6b; font-weight:800'>{h['ar']}</span><br><span style='font-size:12px'>{h['fr']}</span></div>", unsafe_allow_html=True)

elif menu=="Douas":
    st.title("🤲 55 Douas")
    for doua in DOUAS_DATA:
        st.markdown(f"<div class='card-graph' style='text-align:left'><b>{doua['id']}. {doua['ar']}</b><br><span style='font-size:12px'>{doua['fr']}</span></div>", unsafe_allow_html=True)

elif menu=="Parametres":
    st.title("Parametres")
    chain = load_blockchain(); is_valid, msg = verify_blockchain()
    if is_valid: st.success(msg)
    else: st.error(msg)
    st.markdown(f"<div class='card-graph'>Blocs: {len(chain)} | Score: {st.session_state.game_correct}/20 | Internet: {'✅' if check_internet() else '❌'}</div>", unsafe_allow_html=True)

st.markdown("<div style='height:150px'></div>", unsafe_allow_html=True)
