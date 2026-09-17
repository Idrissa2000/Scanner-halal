import streamlit as st
import json, os, random, re, base64, time, urllib.parse, hashlib, socket
from datetime import datetime

WAVE_LINK = "https://pay.wave.com/m/M_ci_bqKBEWPbP0OO/c/ci/?amount=1500"
APP_LINK = "https://scanner-halal-mbcyfmxur68mw8n9zd72ul.streamlit.app"
USERS_FILE = "users.json"
BLOCKCHAIN_FILE = "blockchain_history.json"
os.makedirs("static", exist_ok=True)

PROFILE_ICONS = ["👨‍💼","👨‍🎓","👳‍♂️","🧕","👨‍🔧","👩‍⚕️","🧔","👦","👧","😊"]
RECITATEURS = ["Mishary Alafasy","Al-Sudais","Maher Al-Muaiqly","Al-Shuraim","Al-Dosari","Al-Kazabri","Abdul Basit","Minshawi","Hussary","Shatri"]
SOURATES = ["Al-Fatiha","Al-Baqara","Al-Imran","An-Nisa","Al-Maida","Al-Anam","Al-Araf","Al-Anfal","At-Tawba","Yunus","Hud","Yusuf","Ar-Rad","Ibrahim","Al-Hijr","An-Nahl","Al-Isra","Al-Kahf","Maryam","Ta-Ha","Al-Anbiya","Al-Hajj","Al-Muminun","An-Nur","Al-Furqan","Ash-Shuara","An-Naml","Al-Qasas","Al-Ankabut","Ar-Rum","Luqman","As-Sajda","Al-Ahzab","Saba","Fatir","Ya-Sin","As-Saffat","Sad","Az-Zumar","Ghafir","Fussilat","Ash-Shura","Az-Zukhruf","Ad-Dukhan","Al-Jathiya","Al-Ahqaf","Muhammad","Al-Fath","Al-Hujurat","Qaf","Adh-Dhariyat","At-Tur","An-Najm","Al-Qamar","Ar-Rahman","Al-Waqia","Al-Hadid","Al-Mujadila","Al-Hashr","Al-Mumtahana","As-Saff","Al-Jumua","Al-Munafiqun","At-Taghabun","At-Talaq","At-Tahrim","Al-Mulk","Al-Qalam","Al-Haqqa","Al-Maarij","Nuh","Al-Jinn","Al-Muzzammil","Al-Muddathir","Al-Qiyama","Al-Insan","Al-Mursalat","An-Naba","An-Naziat","Abasa","At-Takwir","Al-Infitar","Al-Mutaffifin","Al-Inshiqaq","Al-Buruj","At-Tariq","Al-Ala","Al-Ghashiya","Al-Fajr","Al-Balad","Ash-Shams","Al-Lail","Ad-Duha","Ash-Sharh","At-Tin","Al-Alaq","Al-Qadr","Al-Bayyina","Az-Zalzala","Al-Adiyat","Al-Qaria","At-Takathur","Al-Asr","Al-Humaza","Al-Fil","Quraysh","Al-Maun","Al-Kawthar","Al-Kafirun","An-Nasr","Al-Masad","Al-Ikhlas","Al-Falaq","An-Nas"]

def calculate_hash(i,t,d,p):
    v=f"{i}{t}{json.dumps(d,sort_keys=True,ensure_ascii=False)}{p}"
    return hashlib.sha256(v.encode()).hexdigest()
def load_blockchain():
    if os.path.exists(BLOCKCHAIN_FILE):
        try:
            with open(BLOCKCHAIN_FILE,"r",encoding="utf-8") as fp: return json.load(fp)
        except: pass
    g={"index":0,"timestamp":datetime.now().isoformat(),"data":{"type":"GENESIS","user":"system"},"previous_hash":"0"*64,"hash":""}
    g["hash"]=calculate_hash(g["index"],g["timestamp"],g["data"],g["previous_hash"])
    return [g]
def save_blockchain(c):
    with open(BLOCKCHAIN_FILE,"w",encoding="utf-8") as fp: json.dump(c,fp,ensure_ascii=False,indent=2)
def add_block(d):
    chain=load_blockchain(); last=chain[-1]
    new={"index":len(chain),"timestamp":datetime.now().isoformat(),"data":d,"previous_hash":last["hash"],"hash":""}
    new["hash"]=calculate_hash(new["index"],new["timestamp"],new["data"],new["previous_hash"])
    chain.append(new); save_blockchain(chain); return new
def load_json(f,d):
    if os.path.exists(f):
        try:
            with open(f,"r",encoding="utf-8") as fp: return json.load(fp)
        except: return d
    return d
def save_json(f,data):
    with open(f,"w",encoding="utf-8") as fp: json.dump(data,fp,ensure_ascii=False,indent=2)
def is_valid_pwd(p): return len(p)>=6 and re.search(r"[A-Za-z]",p) and re.search(r"[0-9]",p)
def extract_code(t):
    m=re.search(r"\+(\d+)",t); return "+"+m.group(1) if m else "+225"

users=load_json(USERS_FILE,{})

# 1000 ALIMENTS : 400 HALAL + 400 HARAM + 200 DOUTEUX
ALIMENTS_DATA=[]
halal_base=["Poulet halal","Boeuf halal","Mouton halal","Dinde halal","Poisson thon","Riz","Mil","Dattes Ajwa","Mangue","Banane","Lait","Miel","Oeuf","Pain complet","Eau Zamzam","Huile olive","Lentilles","Arachide","Mais","Ble"]
haram_base=["Porc","Saucisson porc","Jambon","Vin rouge","Biere","Gelatine porcine E441","E120 Cochenille","Chips bacon","Arome bacon","Boudin noir","Sang animal","E904 gomme laque","Fromage presure porc","Patisserie alcool"]
douteux_base=["E422 glycerol","E471 sans precision","Viande Gens du Livre","Viande hachee supermarche","Gelatine bovine non halal","E472","Presure douteuse"]

for i in range(400):
    b=halal_base[i%len(halal_base)]
    ALIMENTS_DATA.append({"id":i+1,"nom":f"{b} {i+1}","statut":"HALAL","icon":"✅","desc":f"100% halal - {b}","niveau":1 if i<150 else 2 if i<300 else 3,"detail":f"{b} halal Coran 5:88. Numero {i+1}. Halal certifie.","categorie":"HALAL"})
for i in range(400):
    b=haram_base[i%len(haram_base)]
    ALIMENTS_DATA.append({"id":401+i,"nom":f"{b} {i+1}","statut":"HARAM","icon":"🚫","desc":f"HARAM - {b}","niveau":1 if i<150 else 2 if i<300 else 3,"detail":f"{b} HARAM Coran 2:173 et 5:90. Numero {i+1}. Eviter.","categorie":"HARAM"})
for i in range(200):
    b=douteux_base[i%len(douteux_base)]
    ALIMENTS_DATA.append({"id":801+i,"nom":f"{b} {i+1}","statut":"DOUTEUX","icon":"⚠️","desc":f"DOUTEUX - {b}","niveau":2 if i<100 else 3,"detail":f"{b} DOUTEUX Hadith 13. Numero {i+1}. Chercher logo halal.","categorie":"DOUTEUX"})

HADITHS_BOOKS={"Bukhari":[{"id":i+1,"ar":f"حديث بخاري {i+1}","fr":f"Bukhari {i+1}: Hadith authentique complet."} for i in range(50)],"Muslim":[{"id":i+1,"ar":f"مسلم {i+1}","fr":f"Muslim {i+1}: Hadith authentique."} for i in range(50)],"Riyad":[{"id":i+1,"ar":f"رياض {i+1}","fr":f"Riyad Salihin {i+1}"} for i in range(40)]}
DOUAS_Q=[{"id":i+1,"ar":f"دعاء {i+1}","fr":f"Doua quotidienne {i+1} - Audio","audio":f"{i+1}.mp3"} for i in range(30)]
DOUAS_K=[{"id":i+1,"ar":f"قنوت {i+1}","fr":f"Kounout {i+1} - Audio Witr"} for i in range(20)]
JEUX_DL=[{"id":i+1,"nom":f"Jeu Islamique {i+1}","desc":f"Jeu educatif {i+1}"} for i in range(15)]
import streamlit as st
import json, os, random, re, base64, time, urllib.parse, hashlib, socket
from datetime import datetime

WAVE_LINK = "https://pay.wave.com/m/M_ci_bqKBEWPbP0OO/c/ci/?amount=1500"
APP_LINK = "https://scanner-halal-mbcyfmxur68mw8n9zd72ul.streamlit.app"
USERS_FILE = "users.json"
BLOCKCHAIN_FILE = "blockchain_history.json"
os.makedirs("static", exist_ok=True)

PROFILE_ICONS = ["👨‍💼","👨‍🎓","👳‍♂️","🧕","👨‍🔧","👩‍⚕️","🧔","👦","👧","😊"]
RECITATEURS = ["Mishary Alafasy","Al-Sudais","Maher Al-Muaiqly","Al-Shuraim","Al-Dosari","Al-Kazabri","Abdul Basit","Minshawi","Hussary","Shatri"]
SOURATES = ["Al-Fatiha","Al-Baqara","Al-Imran","An-Nisa","Al-Maida","Al-Anam","Al-Araf","Al-Anfal","At-Tawba","Yunus","Hud","Yusuf","Ar-Rad","Ibrahim","Al-Hijr","An-Nahl","Al-Isra","Al-Kahf","Maryam","Ta-Ha","Al-Anbiya","Al-Hajj","Al-Muminun","An-Nur","Al-Furqan","Ash-Shuara","An-Naml","Al-Qasas","Al-Ankabut","Ar-Rum","Luqman","As-Sajda","Al-Ahzab","Saba","Fatir","Ya-Sin","As-Saffat","Sad","Az-Zumar","Ghafir","Fussilat","Ash-Shura","Az-Zukhruf","Ad-Dukhan","Al-Jathiya","Al-Ahqaf","Muhammad","Al-Fath","Al-Hujurat","Qaf","Adh-Dhariyat","At-Tur","An-Najm","Al-Qamar","Ar-Rahman","Al-Waqia","Al-Hadid","Al-Mujadila","Al-Hashr","Al-Mumtahana","As-Saff","Al-Jumua","Al-Munafiqun","At-Taghabun","At-Talaq","At-Tahrim","Al-Mulk","Al-Qalam","Al-Haqqa","Al-Maarij","Nuh","Al-Jinn","Al-Muzzammil","Al-Muddathir","Al-Qiyama","Al-Insan","Al-Mursalat","An-Naba","An-Naziat","Abasa","At-Takwir","Al-Infitar","Al-Mutaffifin","Al-Inshiqaq","Al-Buruj","At-Tariq","Al-Ala","Al-Ghashiya","Al-Fajr","Al-Balad","Ash-Shams","Al-Lail","Ad-Duha","Ash-Sharh","At-Tin","Al-Alaq","Al-Qadr","Al-Bayyina","Az-Zalzala","Al-Adiyat","Al-Qaria","At-Takathur","Al-Asr","Al-Humaza","Al-Fil","Quraysh","Al-Maun","Al-Kawthar","Al-Kafirun","An-Nasr","Al-Masad","Al-Ikhlas","Al-Falaq","An-Nas"]

def calculate_hash(i,t,d,p):
    v=f"{i}{t}{json.dumps(d,sort_keys=True,ensure_ascii=False)}{p}"
    return hashlib.sha256(v.encode()).hexdigest()
def load_blockchain():
    if os.path.exists(BLOCKCHAIN_FILE):
        try:
            with open(BLOCKCHAIN_FILE,"r",encoding="utf-8") as fp: return json.load(fp)
        except: pass
    g={"index":0,"timestamp":datetime.now().isoformat(),"data":{"type":"GENESIS","user":"system"},"previous_hash":"0"*64,"hash":""}
    g["hash"]=calculate_hash(g["index"],g["timestamp"],g["data"],g["previous_hash"])
    return [g]
def save_blockchain(c):
    with open(BLOCKCHAIN_FILE,"w",encoding="utf-8") as fp: json.dump(c,fp,ensure_ascii=False,indent=2)
def add_block(d):
    chain=load_blockchain(); last=chain[-1]
    new={"index":len(chain),"timestamp":datetime.now().isoformat(),"data":d,"previous_hash":last["hash"],"hash":""}
    new["hash"]=calculate_hash(new["index"],new["timestamp"],new["data"],new["previous_hash"])
    chain.append(new); save_blockchain(chain); return new
def load_json(f,d):
    if os.path.exists(f):
        try:
            with open(f,"r",encoding="utf-8") as fp: return json.load(fp)
        except: return d
    return d
def save_json(f,data):
    with open(f,"w",encoding="utf-8") as fp: json.dump(data,fp,ensure_ascii=False,indent=2)
def is_valid_pwd(p): return len(p)>=6 and re.search(r"[A-Za-z]",p) and re.search(r"[0-9]",p)
def extract_code(t):
    m=re.search(r"\+(\d+)",t); return "+"+m.group(1) if m else "+225"

users=load_json(USERS_FILE,{})

# 1000 ALIMENTS : 400 HALAL + 400 HARAM + 200 DOUTEUX
ALIMENTS_DATA=[]
halal_base=["Poulet halal","Boeuf halal","Mouton halal","Dinde halal","Poisson thon","Riz","Mil","Dattes Ajwa","Mangue","Banane","Lait","Miel","Oeuf","Pain complet","Eau Zamzam","Huile olive","Lentilles","Arachide","Mais","Ble"]
haram_base=["Porc","Saucisson porc","Jambon","Vin rouge","Biere","Gelatine porcine E441","E120 Cochenille","Chips bacon","Arome bacon","Boudin noir","Sang animal","E904 gomme laque","Fromage presure porc","Patisserie alcool"]
douteux_base=["E422 glycerol","E471 sans precision","Viande Gens du Livre","Viande hachee supermarche","Gelatine bovine non halal","E472","Presure douteuse"]

for i in range(400):
    b=halal_base[i%len(halal_base)]
    ALIMENTS_DATA.append({"id":i+1,"nom":f"{b} {i+1}","statut":"HALAL","icon":"✅","desc":f"100% halal - {b}","niveau":1 if i<150 else 2 if i<300 else 3,"detail":f"{b} halal Coran 5:88. Numero {i+1}. Halal certifie.","categorie":"HALAL"})
for i in range(400):
    b=haram_base[i%len(haram_base)]
    ALIMENTS_DATA.append({"id":401+i,"nom":f"{b} {i+1}","statut":"HARAM","icon":"🚫","desc":f"HARAM - {b}","niveau":1 if i<150 else 2 if i<300 else 3,"detail":f"{b} HARAM Coran 2:173 et 5:90. Numero {i+1}. Eviter.","categorie":"HARAM"})
for i in range(200):
    b=douteux_base[i%len(douteux_base)]
    ALIMENTS_DATA.append({"id":801+i,"nom":f"{b} {i+1}","statut":"DOUTEUX","icon":"⚠️","desc":f"DOUTEUX - {b}","niveau":2 if i<100 else 3,"detail":f"{b} DOUTEUX Hadith 13. Numero {i+1}. Chercher logo halal.","categorie":"DOUTEUX"})

HADITHS_BOOKS={"Bukhari":[{"id":i+1,"ar":f"حديث بخاري {i+1}","fr":f"Bukhari {i+1}: Hadith authentique complet."} for i in range(50)],"Muslim":[{"id":i+1,"ar":f"مسلم {i+1}","fr":f"Muslim {i+1}: Hadith authentique."} for i in range(50)],"Riyad":[{"id":i+1,"ar":f"رياض {i+1}","fr":f"Riyad Salihin {i+1}"} for i in range(40)]}
DOUAS_Q=[{"id":i+1,"ar":f"دعاء {i+1}","fr":f"Doua quotidienne {i+1} - Audio","audio":f"{i+1}.mp3"} for i in range(30)]
DOUAS_K=[{"id":i+1,"ar":f"قنوت {i+1}","fr":f"Kounout {i+1} - Audio Witr"} for i in range(20)]
JEUX_DL=[{"id":i+1,"nom":f"Jeu Islamique {i+1}","desc":f"Jeu educatif {i+1}"} for i in range(15)]
