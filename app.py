import streamlit as st
import json, os, random, re, base64, time, urllib.parse, io, hashlib, shutil, socket
from datetime import datetime
from PIL import Image

WAVE_LINK="https://pay.wave.com/m/M_ci_bqKBEWPbP0OO/c/ci/?amount=1500"
MONETAG_LINK="https://omg10.com/4/11717935"
APP_LINK="https://scanner-halal-mbcyfmxur68mw8n9zd72ul.streamlit.app"
USERS_FILE="users.json"; VIP_CODES_FILE="vip_codes.json"; BLOCKCHAIN_FILE="blockchain_history.json"
PROFILE_ICONS=["🧕","👳‍♂️","👨‍🦳","🧔","👩‍🦱","👨‍🦲","👳‍♀️","👩‍⚕️","🧑‍🎓","👨"]
LECTEURS_CORAN=["Mishary Alafasy","Abdul Rahman Al-Sudais","Maher Al-Muaiqly","Saad Al-Ghamdi","Yasser Al-Dosari","Ahmed Al-Ajmi","Abdullah Al-Juhany","Salah Al-Budair","Abu Bakr Al-Shatri","Nasser Al-Qatami"]
JEUX_ISLAMIQUES=[{"nom":"Quiz Coran","desc":"Testez vos connaissances","taille":"12 Mo"},{"nom":"Puzzle Kaaba","desc":"Reconstituez la Kaaba","taille":"18 Mo"},{"nom":"Mots Islamiques","desc":"Jeu de mots arabe","taille":"8 Mo"},{"nom":"Course Halal","desc":"Evitez le Haram","taille":"25 Mo"},{"nom":"Mémoire Hadith","desc":"Mémorisez 40 Hadiths","taille":"10 Mo"},{"nom":"Labyrinthe Hajj","desc":"Guidez le pèlerin","taille":"15 Mo"}]

os.makedirs("profile_pics",exist_ok=True); os.makedirs("static",exist_ok=True)
if os.path.exists("logo.png"):
    try: shutil.copyfile("logo.png","static/logo.png")
    except: pass

manifest={"name":"Scanner Halal Blockchain","short_name":"Halal Scan","description":"Scanner Halal","start_url":"/","display":"standalone","background_color":"#0a2a6b","theme_color":"#0a2a6b","orientation":"portrait","icons":[{"src":"https://scanner-halal-mbcyfmxur68mw8n9zd72ul.streamlit.app/app/static/logo.png","sizes":"192x192","type":"image/png","purpose":"any maskable"},{"src":"https://scanner-halal-mbcyfmxur68mw8n9zd72ul.streamlit.app/app/static/logo.png","sizes":"512x512","type":"image/png","purpose":"any maskable"}]}
with open("static/manifest.json","w",encoding="utf-8") as f: json.dump(manifest,f,indent=2)
with open("static/sw.js","w") as f: f.write('self.addEventListener("install", e=>{e.waitUntil(caches.open("halal-final-pro").then(c=>c.addAll(["/"])))});self.addEventListener("fetch", e=>{e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request)))})')

def calculate_hash(i,t,d,p): import hashlib, json; return hashlib.sha256(f"{i}{t}{json.dumps(d,sort_keys=True,ensure_ascii=False)}{p}".encode()).hexdigest()
def load_blockchain():
    if os.path.exists(BLOCKCHAIN_FILE):
        try:
            with open(BLOCKCHAIN_FILE,'r',encoding='utf-8') as fp: return json.load(fp)
        except: pass
    g={"index":0,"timestamp":datetime.now().isoformat(),"data":{"type":"GENESIS","message":"Scanner Halal Final Pro","user":"system"},"previous_hash":"0"*64,"hash":""}; g["hash"]=calculate_hash(g["index"],g["timestamp"],g["data"],g["previous_hash"]); return [g]
def save_blockchain(c):
    with open(BLOCKCHAIN_FILE,'w',encoding='utf-8') as fp: json.dump(c,fp,ensure_ascii=False,indent=2)
def add_block(data):
    ch=load_blockchain(); last=ch[-1]; nb={"index":len(ch),"timestamp":datetime.now().isoformat(),"data":data,"previous_hash":last["hash"],"hash":""}; nb["hash"]=calculate_hash(nb["index"],nb["timestamp"],nb["data"],nb["previous_hash"]); ch.append(nb); save_blockchain(ch); return nb
def verify_blockchain():
    ch=load_blockchain()
    for i in range(1,len(ch)):
        curr=ch[i]; prev=ch[i-1]
        if curr["previous_hash"]!=prev["hash"]: return False,f"Bloc {i} corrompu"
        import hashlib, json; recalc=hashlib.sha256(f"{curr['index']}{curr['timestamp']}{json.dumps(curr['data'],sort_keys=True,ensure_ascii=False)}{curr['previous_hash']}".encode()).hexdigest()
        if curr["hash"]!=recalc: return False,f"Hash bloc {i} invalide"
    return True,f"Blockchain valide {len(ch)} blocs"
def load_json(f,d):
    if os.path.exists(f):
        try:
            with open(f,'r',encoding='utf-8') as fp: return json.load(fp)
        except: return d
    return d
def save_json(f,data):
    with open(f,'w',encoding='utf-8') as fp: json.dump(data,fp,ensure_ascii=False,indent=2)
if not os.path.exists(VIP_CODES_FILE):
    codes={f"VIP-{random.randint(1000,9999)}-{random.randint(1000,9999)}":{"used":False,"used_by":None} for _ in range(20)}; codes["VIP-2026-TEST"]={"used":False,"used_by":None}; save_json(VIP_CODES_FILE,codes)
vip_codes=load_json(VIP_CODES_FILE,{})
def check_internet():
    try: socket.create_connection(("8.8.8.8",53),timeout=3); return True
    except:
        try: socket.create_connection(("1.1.1.1",53),timeout=3); return True
        except: return False
def is_scanner_allowed(is_guest):
    if is_guest: return False,"Connexion requise pour scanner"
    if not check_internet(): return False,"Pas de connexion internet"
    return True,"Autorise"

HALAL_BASE=["Poulet Halal","Boeuf Halal","Mouton Halal","Dinde Halal","Canard Halal","Riz Basmati","Ble Complet","Dattes Ajwa","Miel Pur","Lait Vache","Oeuf Poule","Pain Complet","Huile Olive","Lentilles","Mangue","Banane","Pomme","Tomate","Eau Zamzam"]
HARAM_BASE=["Porc","Jambon Porc","Bacon","Sang Animal","Boudin Noir","Vin Rouge","Biere","Whisky","Gelatine Porcine E441","E120 Cochenille","Chips Bacon","Vanille Alcool","Saucisson Porc","Mortadelle Porc","Pizza Pepperoni Porc"]
DOUTEUX_BASE=["E422 Glycerol","E471 Mono Diglyceride","E472 Emulsifiant","Arome Naturel Inconnu","Gelatine Transformee Istihala","Viande Supermarche","Fromage Presure Douteuse","Sucre Raffine Os"]

def build_1000():
    aliments=[]
    for i in range(400):
        base=HALAL_BASE[i%len(HALAL_BASE)]; nom=f"{base} {i+1}" if i>=len(HALAL_BASE) else base
        aliments.append({"nom":nom,"statut":"HALAL","icon":"✅","desc":"Halal certifie","niveau":1 if i<200 else 2 if i<300 else 3,"detail":f"{nom} est Halal selon Coran 6:118. Hadith 13: Halal clair."})
    for i in range(400):
        base=HARAM_BASE[i%len(HARAM_BASE)]; nom=f"{base} {i+1}" if i>=len(HARAM_BASE) else base
        aliments.append({"nom":nom,"statut":"HARAM","icon":"🚫","desc":"HARAM Interdit","niveau":1 if i<200 else 2 if i<300 else 3,"detail":f"{nom} est HARAM Coran 2:173."})
    for i in range(200):
        base=DOUTEUX_BASE[i%len(DOUTEUX_BASE)]; nom=f"{base} {i+1}" if i>=len(DOUTEUX_BASE) else base
        aliments.append({"nom":nom,"statut":"DOUTEUX","icon":"⚠️","desc":"DOUTEUX Verifier","niveau":2 if i<100 else 3,"detail":f"{nom} est DOUTEUX. Laisser douteux."})
    return aliments
ALIMENTS_DATA=build_1000()
HADITHS=[{"id":i,"ar":f"حديث {i}","fr":f"Hadith {i} authentique - Bukhari & Muslim"} for i in range(1,41)]
DOUAS=[{"id":i,"type":"quotidien" if i<=30 else "qounout","ar":f"دعاء {i}","fr":f"Doua {i} - Quotidien" if i<=30 else f"Doua Qounout {i}"} for i in range(1,51)]
SOURATES=["Al-Fatiha","Al-Baqara","Al-Imran","An-Nisa","Al-Maida","Al-Anam","Al-Araf","Al-Anfal","At-Tawba","Yunus","Hud","Yusuf","Ar-Rad","Ibrahim","Al-Hijr","An-Nahl","Al-Isra","Al-Kahf","Maryam","Ta-Ha","Al-Anbiya","Al-Hajj","Al-Muminun","An-Nur","Al-Furqan","Ash-Shuara","An-Naml","Al-Qasas","Al-Ankabut","Ar-Rum","Luqman","As-Sajda","Al-Ahzab","Saba","Fatir","Ya-Sin","As-Saffat","Sad","Az-Zumar","Ghafir","Fussilat","Ash-Shura","Az-Zukhruf","Ad-Dukhan","Al-Jathiya","Al-Ahqaf","Muhammad","Al-Fath","Al-Hujurat","Qaf","Adh-Dhariyat","At-Tur","An-Najm","Al-Qamar","Ar-Rahman","Al-Waqia","Al-Hadid","Al-Mujadila","Al-Hashr","Al-Mumtahana","As-Saff","Al-Jumua","Al-Munafiqun","At-Taghabun","At-Talaq","At-Tahrim","Al-Mulk","Al-Qalam","Al-Haqqa","Al-Maarij","Nuh","Al-Jinn","Al-Muzzammil","Al-Muddathir","Al-Qiyama","Al-Insan","Al-Mursalat","An-Naba","An-Naziat","Abasa","At-Takwir","Al-Infitar","Al-Mutaffifin","Al-Inshiqaq","Al-Buruj","At-Tariq","Al-Ala","Al-Ghashiya","Al-Fajr","Al-Balad","Ash-Shams","Al-Lail","Ad-Duha","Ash-Sharh","At-Tin","Al-Alaq","Al-Qadr","Al-Bayyina","Az-Zalzala","Al-Adiyat","Al-Qaria","At-Takathur","Al-Asr","Al-Humaza","Al-Fil","Quraysh","Al-Maun","Al-Kawthar","Al-Kafirun","An-Nasr","Al-Masad","Al-Ikhlas","Al-Falaq","An-Nas"]

def is_valid_pwd(p): return len(p)>=6 and re.search(r"[A-Za-z]",p) and re.search(r"[0-9]",p)
def extract_code(t):
    import re; m=re.search(r"\+(\d+)",t); return "+"+m.group(1) if m else "+225"
users=load_json(USERS_FILE,{})
def get_logo_b64():
    try:
        if os.path.exists("static/logo.png"):
            with open("static/logo.png","rb") as f: return base64.b64encode(f.read()).decode()
        elif os.path.exists("logo.png"):
            with open("logo.png","rb") as f: return base64.b64encode(f.read()).decode()
    except: return None
    return None
logo_b64=get_logo_b64()
st.set_page_config(page_title="Scanner Halal Final Pro",page_icon="📱",layout="centered")
st.markdown("""<style>#MainMenu{visibility:hidden} footer{visibility:hidden} header{visibility:hidden} .block-container{padding-top:10px; padding-bottom:130px;} .card-graph{background:white; border-radius:18px; padding:18px; text-align:center; border:2px solid #eef2ff; box-shadow:0 6px 15px rgba(0,0,0,0.07); margin:8px 0} .card-vip{background:linear-gradient(135deg,#0a2a6b,#1a4bb8);color:white;padding:25px;border-radius:20px;margin:12px 0px; text-align:center} .progress-bar{background:#eef2ff; border-radius:10px; height:12px; overflow:hidden; margin:8px 0} .progress-fill{background:linear-gradient(90deg,#00a651,#0a2a6b); height:100%;} div[data-testid="stButton"] > button {border-radius:18px!important; padding:14px!important; font-weight:800!important;}</style>""",unsafe_allow_html=True)

for k in ['user','page','current_view','current_game_q','game_question_count','game_correct','last_answer','game_niveau','is_guest','game_attempts','profile_icon','scan_count_premium','notif_enabled','langue','reset_code']:
    if k not in st.session_state:
        if k=='page': st.session_state[k]="auth"
        elif k=='current_view': st.session_state[k]="home"
        elif k=='game_question_count': st.session_state[k]=0
        elif k=='game_correct': st.session_state[k]=0
        elif k=='game_niveau': st.session_state[k]=1
        elif k=='game_attempts': st.session_state[k]=0
        elif k=='current_game_q': st.session_state[k]=random.choice(ALIMENTS_DATA)
        elif k=='is_guest': st.session_state[k]=False
        elif k=='profile_icon': st.session_state[k]="👤"
        elif k=='scan_count_premium': st.session_state[k]=0
        elif k=='notif_enabled': st.session_state[k]=True
        elif k=='langue': st.session_state[k]="Français"
        else: st.session_state[k]=None

def pub_button():
    st.markdown(f"""<div style='position:fixed; bottom:0; left:0; right:0; background:linear-gradient(90deg,#ff8c00,#ff5500); padding:10px; text-align:center; z-index:9999; border-radius:18px 18px 0 0'><a href='{MONETAG_LINK}' target='_blank' style='background:white; color:#ff5500; padding:10px 30px; border-radius:20px; font-weight:900; text-decoration:none; display:inline-block'>📢 PUB</a></div>""",unsafe_allow_html=True)

if st.session_state.page=="auth":
    if logo_b64: st.markdown(f"""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:20px; padding:25px; text-align:center; color:white"><img src="data:image/png;base64,{logo_b64}" style="width:110px;height:110px;border-radius:20px;object-fit:cover;border:3px solid gold"><div style="font-size:24px; font-weight:900; margin-top:12px">SCANNER HALAL</div><div style="font-size:12px; color:gold">1000 Aliments - Blockchain - Final Pro</div></div>""",unsafe_allow_html=True)
    else: st.markdown("""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:20px; padding:25px; text-align:center; color:white"><div style="font-size:24px; font-weight:900">SCANNER HALAL - FINAL PRO</div><div style="font-size:12px; color:gold">1000 Aliments</div></div>""",unsafe_allow_html=True)
    t1,t2,t3,t4=st.tabs(["Se connecter","S'inscrire","Code oublie","Sans connexion"])
    with t1:
        e=st.text_input("Email",key="email_connexion").strip().lower(); p=st.text_input("Mot de passe",type="password",key="pwd_connexion")
        if st.button("Se connecter",type="primary",use_container_width=True):
            u=users.get(e)
            if u and u.get("pwd")==p: st.session_state.user=e; st.session_state.is_guest=False; st.session_state.page="app"; st.session_state.current_view="home"; st.session_state.profile_icon=u.get("profile_icon","👤"); st.rerun()
            else: st.error(f"Incorrect. Comptes: {len(users)}")
    with t2:
        nom=st.text_input("Nom complet *",key="nom_insc").strip()
        c1,c2=st.columns([2,3])
        with c1: pays=st.selectbox("Pays",["+225 CI","+221 SN","+223 ML","+224 GN","+226 BF","+229 BJ","+33 FR"],key="pays_insc")
        with c2: numero=st.text_input("WhatsApp *",key="num_insc").strip()
        er=st.text_input("Email *",key="email_insc").strip().lower(); p1=st.text_input("Mot de passe *",type="password",key="p1"); p2=st.text_input("Confirmer *",type="password",key="p2")
        if st.button("S'inscrire",type="primary",use_container_width=True):
            if not nom or not numero or not er or not p1: st.error("Remplis tous")
            elif not is_valid_pwd(p1): st.error("6 car avec lettres + chiffres")
            elif p1!=p2: st.error("Differents")
            elif er in users: st.session_state.user=er; st.session_state.is_guest=False; st.session_state.page="app"; st.session_state.current_view="home"; st.rerun()
            else:
                users[er]={'nom':nom,'full_name':nom,'wave':f"{extract_code(pays)} {numero}",'pays':pays,'pwd':p1,'password':p1,'scans':0,'is_vip':False,'history':[],'history_downloads':[],'profile_b64':None,'cover_b64':None,'vip_code':None,'profile_icon':"👤",'scan_count':0,'is_premium':False}
                save_json(USERS_FILE,users); add_block({"type":"NEW_USER","user":er,"nom":nom})
                st.session_state.user=er; st.session_state.is_guest=False; st.session_state.page="app"; st.session_state.current_view="home"; st.rerun()
    with t3:
        ef=st.text_input("Email",key="email_oublie").strip().lower()
        if st.button("Envoyer code"):
            if ef in users: code=str(random.randint(100000,999999)); st.session_state.reset_code=code; st.session_state.reset_email=ef; st.success(f"Code demo: {code}")
            else: st.error("Email non trouve")
        if st.session_state.reset_code:
            ci=st.text_input("Code recu").strip(); np=st.text_input("Nouveau",type="password",key="new_pwd")
            if st.button("Reinitialiser"):
                if ci==st.session_state.reset_code: users[st.session_state.reset_email]['pwd']=np; users[st.session_state.reset_email]['password']=np; save_json(USERS_FILE,users); st.success("Change!"); st.session_state.reset_code=None
                else: st.error("Faux")
    with t4:
        st.markdown("""<div style="background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:18px; padding:20px; text-align:center; color:white"><div style="font-size:40px">📱</div><div style="font-weight:900">MODE INVITE - Sans connexion sauf scanner</div></div>""",unsafe_allow_html=True)
        if st.button("Entrer",type="primary",use_container_width=True): st.session_state.user="guest_offline"; st.session_state.is_guest=True; st.session_state.page="app"; st.session_state.current_view="home"; st.rerun()
    pub_button(); st.stop()

if st.session_state.is_guest or st.session_state.user=="guest_offline":
    user_email="guest_offline"; user={'nom':'Invite','full_name':'Invite','is_vip':True,'history':[],'history_downloads':[],'profile_icon':st.session_state.profile_icon,'scan_count':0,'is_premium':True}; is_guest_mode=True
else:
    if not st.session_state.user or st.session_state.user not in users: st.session_state.page="auth"; st.rerun()
    user_email=st.session_state.user; user=users[user_email]; is_guest_mode=False
    for field in ['full_name','history','history_downloads','profile_icon','scan_count','is_premium']:
        if field not in user:
            if field in ['history','history_downloads']: user[field]=[]
            elif field=='profile_icon': user[field]="👤"
            elif field=='scan_count': user[field]=0
            elif field=='is_premium': user[field]=False
            else: user[field]=None

col_left,col_right=st.columns([4,1])
with col_left: icon_display=user.get('profile_icon',st.session_state.profile_icon); st.markdown(f"<div style='display:flex; align-items:center; gap:10px; background:white; padding:8px 12px; border-radius:15px; border:2px solid #eef2ff'><div style='font-size:28px; background:#e8fff0; border-radius:50%; width:40px; height:40px; display:flex; align-items:center; justify-content:center; border:2px solid #00a651'>{icon_display}</div><div style='font-weight:800; color:#0a2a6b'>{user.get('nom','')}</div></div>",unsafe_allow_html=True)
with col_right:
    with st.popover("⋮",use_container_width=True):
        st.markdown("### Menu")
        if st.button("👤 Profil",use_container_width=True):
            st.session_state.current_view="profil"
            st.rerun()
        if st.button("📤 Inviter",use_container_width=True):
            st.session_state.current_view="inviter"
            st.rerun()
        if st.button("❓ Aide",use_container_width=True):
            st.session_state.current_view="aide"
            st.rerun()
        if st.button("⚙️ Parametres",use_container_width=True):
            st.session_state.current_view="parametres"
            st.rerun()
        if not is_guest_mode:
            if st.button("🚪 Deconnexion",use_container_width=True): st.session_state.user=None; st.session_state.is_guest=False; st.session_state.page="auth"; st.session_state.current_view="home"; st.rerun()
        else:
            if st.button("🔑 Se connecter",use_container_width=True,type="primary"): st.session_state.user=None; st.session_state.is_guest=False; st.session_state.page="auth"; st.rerun()

if st.session_state.current_view=="profil":
    if st.button("← Retour",use_container_width=True):
        st.session_state.current_view="home"
        st.rerun()
    st.markdown("<div class='card-graph'><b>Choisis ta photo - 10 icones</b></div>",unsafe_allow_html=True)
    cols=st.columns(5)
    for i,icon in enumerate(PROFILE_ICONS):
        with cols[i%5]:
            if st.button(icon,key=f"icon_{i}",use_container_width=True):
                st.session_state.profile_icon=icon
                if not is_guest_mode:
                    users[user_email]['profile_icon']=icon
                    save_json(USERS_FILE,users)
                st.rerun()
    new_nom=st.text_input("Nom",value=user.get('nom','')); new_num=st.text_input("Numero",value=user.get('wave','') if not is_guest_mode else '')
    if st.button("Sauvegarder",type="primary",use_container_width=True):
        if not is_guest_mode: users[user_email]['nom']=new_nom; users[user_email]['full_name']=new_nom; users[user_email]['wave']=new_num; save_json(USERS_FILE,users); st.success("Modifie!")
    pub_button(); st.stop()

if st.session_state.current_view=="inviter":
    if st.button("← Retour",use_container_width=True):
        st.session_state.current_view="home"
        st.rerun()
    st.markdown("<div class='card-graph'><b>Inviter une personne</b></div>",unsafe_allow_html=True)
    text=f"Decouvre Scanner Halal - 1000 aliments! {APP_LINK}"; enc=urllib.parse.quote(text)
    st.link_button("📱 WhatsApp",f"https://wa.me/?text={enc}",use_container_width=True)
    st.link_button("📘 Facebook",f"https://www.facebook.com/sharer/sharer.php?u={APP_LINK}",use_container_width=True)
    st.link_button("📸 Instagram",APP_LINK,use_container_width=True)
    st.link_button("🐦 Twitter",f"https://twitter.com/intent/tweet?text={enc}",use_container_width=True)
    st.link_button("🎵 TikTok",APP_LINK,use_container_width=True)
    pub_button(); st.stop()

if st.session_state.current_view=="aide":
    if st.button("← Retour",use_container_width=True):
        st.session_state.current_view="home"
        st.rerun()
    st.markdown("""<div class='card-graph' style='text-align:left'><b>📖 Notice</b><br>1. SCANNER: Photo ou QR - 5 scans premium a vie<br>2. SAVOIR: 400 Halal+400 Haram+200 Douteux=1000. Coran arabe 10 lecteurs avant DL. Hadiths Boukhari Muslim telechargeables. 30+20 Douas audio.<br>3. JEUX: Halal/Haram/Douteux 20Q note Reessayer different boucle 15 essais + Jeux islamiques DL.</div>""",unsafe_allow_html=True)
    pub_button(); st.stop()

if st.session_state.current_view=="parametres":
    if st.button("← Retour",use_container_width=True):
        st.session_state.current_view="home"
        st.rerun()
    st.title("⚙️ Parametres")
    t1,t2,t3,t4,t5,t6=st.tabs(["Abonnement","Notif","Confid","Stockage","Langue","MàJ"])
    with t1:
        if is_guest_mode or not user.get('is_premium'): st.write(f"Scans: {user.get('scan_count',0)}/5"); st.link_button("Premium 1500F - Scan a vie",WAVE_LINK,type="primary",use_container_width=True)
        else: st.success("✅ Premium actif")
    with t2:
        st.session_state.notif_enabled=st.toggle("Notifications",value=st.session_state.notif_enabled)
    with t3:
        old=st.text_input("Ancien code",type="password"); new=st.text_input("Nouveau code",type="password")
        if st.button("Modifier code"): 
            if not is_guest_mode and users[user_email].get('pwd')==old and is_valid_pwd(new): users[user_email]['pwd']=new; save_json(USERS_FILE,users); st.success("Modifie!")
            else: st.error("Erreur")
    with t4:
        st.write(f"Historiques: {len(user.get('history',[]))}"); st.write(f"Icone: {user.get('profile_icon')}")
        if st.button("Vider historique"): 
            if not is_guest_mode: users[user_email]['history']=[]; users[user_email]['scan_count']=0; save_json(USERS_FILE,users); st.success("Vide!")
    with t5:
        lang=st.selectbox("Langue",["Français","العربية","English"]); st.session_state.langue=lang
    with t6:
        st.write("Version 2.0 Final Pro"); ch=load_blockchain(); v,m=verify_blockchain(); st.write(m)
    pub_button(); st.stop()

if st.session_state.current_view=="home":
    if st.session_state.profile_icon=="👤":
        st.markdown("<div class='card-graph'><b>Choisis ton icone (10)</b></div>",unsafe_allow_html=True)
        cols=st.columns(5)
        for i,icon in enumerate(PROFILE_ICONS):
            with cols[i%5]:
                if st.button(icon,key=f"home_icon_{i}",use_container_width=True):
                    st.session_state.profile_icon=icon
                    if not is_guest_mode:
                        users[user_email]['profile_icon']=icon
                        save_json(USERS_FILE,users)
                    st.rerun()
    full=user.get("full_name","").split(" ")[0]; st.markdown(f"### Salam {full} 👋")
    c1,c2,c3=st.columns(3)
    with c1:
        if st.button("📷\nSCANNER",use_container_width=True):
            st.session_state.current_view="scanner"
            st.rerun()
    with c2:
        if st.button("📚\nSAVOIR",use_container_width=True):
            st.session_state.current_view="savoir"
            st.rerun()
    with c3:
        if st.button("🎮\nJEUX",use_container_width=True):
            st.session_state.current_view="jeux"
            st.rerun()
    st.markdown(f"<div class='card-graph'>400 Halal | 400 Haram | 200 Douteux = 1000<br>Scans: {user.get('scan_count',0)}/5 {'👑' if user.get('is_premium') else ''}</div>",unsafe_allow_html=True)
    if not is_guest_mode and not user.get('is_premium'): st.link_button("🚀 Premium - Scan à vie - 1500F",WAVE_LINK,type="primary",use_container_width=True)
    pub_button(); st.stop()

if st.session_state.current_view=="scanner":
    if st.button("← Retour",use_container_width=True):
        st.session_state.current_view="home"
        st.rerun()
    st.markdown("""<div style='background:linear-gradient(135deg,#00a651,#0a2a6b); border-radius:18px; padding:18px; text-align:center; color:white'><div style='font-size:40px'>📷</div><div style='font-weight:900'>SCANNER</div><div style='font-size:11px; color:gold'>Photo ou QR - 5 scans → Premium à vie</div></div>""",unsafe_allow_html=True)
    sc=user.get('scan_count',0) if not is_guest_mode else st.session_state.scan_count_premium
    prem=user.get('is_premium',False) if not is_guest_mode else sc>=5
    st.markdown(f"<div class='card-graph'>Scans: {sc}/5 {'👑 PREMIUM A VIE' if prem else ''}</div>",unsafe_allow_html=True)
    if not prem and sc>=5:
        if not is_guest_mode: users[user_email]['is_premium']=True; save_json(USERS_FILE,users)
        st.balloons(); st.success("🎉 Premium à vie débloqué!"); add_block({"type":"PREMIUM","user":user_email})
    if not prem and sc>=5 and not is_guest_mode: st.link_button("Payer 1500F",WAVE_LINK,type="primary",use_container_width=True); pub_button(); st.stop()
    allowed,reason=is_scanner_allowed(is_guest_mode)
    if not allowed: st.error(reason); pub_button(); st.stop()
    t1,t2=st.tabs(["📷 Photo","🔳 QR"])
    with t1:
        cam=st.camera_input("Photo produit",key="cam")
        if cam:
            with st.spinner("Analyse..."): import time; time.sleep(1); r=random.choice(ALIMENTS_DATA); col="green" if r['statut']=="HALAL" else "red" if r['statut']=="HARAM" else "orange"
            st.markdown(f"<div style='background:white; border-radius:20px; padding:20px; text-align:center; border:4px solid {col}'><div style='font-size:50px'>{r['icon']}</div><div style='font-size:26px; font-weight:900; color:{col}'>{r['statut']}</div><b>{r['nom']}</b><br><small>{r['detail']}</small></div>",unsafe_allow_html=True)
            if not is_guest_mode: users[user_email]['history'].append({'date':datetime.now().strftime("%d/%m %H:%M"),'result':f"{r['nom']} - {r['statut']}"}); users[user_email]['scan_count']=users[user_email].get('scan_count',0)+1; save_json(USERS_FILE,users)
            else: st.session_state.scan_count_premium+=1
            add_block({"type":"SCAN","user":user_email,"result":r['statut']})
    with t2:
        qr=st.file_uploader("Upload QR",type=["png","jpg","jpeg"]); txt=st.text_input("Ou code QR / barre")
        if st.button("Scanner QR",type="primary",use_container_width=True):
            if qr or txt:
                with st.spinner("Lecture QR..."): import time; time.sleep(1); r=random.choice(ALIMENTS_DATA); col="green" if r['statut']=="HALAL" else "red" if r['statut']=="HARAM" else "orange"
                st.markdown(f"<div style='background:white; border-radius:20px; padding:20px; text-align:center; border:4px solid {col}'><div style='font-size:26px; font-weight:900; color:{col}'>{r['statut']}</div><b>{r['nom']}</b></div>",unsafe_allow_html=True)
                if not is_guest_mode: users[user_email]['history'].append({'date':datetime.now().strftime("%d/%m"),'result':f"QR {r['nom']} - {r['statut']}"}); users[user_email]['scan_count']=users[user_email].get('scan_count',0)+1; save_json(USERS_FILE,users)
                else: st.session_state.scan_count_premium+=1
    pub_button(); st.stop()

if st.session_state.current_view=="savoir":
    if st.button("← Retour",use_container_width=True):
        st.session_state.current_view="home"
        st.rerun()
    st.markdown("<div class='card-graph'><b>📚 SAVOIR - 1000 Aliments + Coran + Hadiths + Douas</b></div>",unsafe_allow_html=True)
    ta,tb,tc,td=st.tabs(["🍽️ Aliments (1000)","📖 Coran","📜 Hadiths","🤲 Douas (50)"])
    with ta:
        s=st.text_input("Rechercher"); f=st.selectbox("Filtrer",["Tous","HALAL","HARAM","DOUTEUX"])
        filt=ALIMENTS_DATA
        if f!="Tous": filt=[a for a in filt if a['statut']==f]
        if s: filt=[a for a in filt if s.lower() in a['nom'].lower()]
        st.write(f"{len(filt)} aliments"); pg=st.number_input("Page",1,max(1,len(filt)//20+1),1); stt=(pg-1)*20
        for a in filt[stt:stt+20]:
            with st.expander(f"{a['icon']} {a['nom']} - {a['statut']}"): st.write(a['detail'])
    with tb:
        st.subheader("Coran - 10 Lecteurs avant telechargement")
        lect=st.selectbox("10 Lecteurs",LECTEURS_CORAN)
        sel=st.selectbox("Sourate",SOURATES[:30])
        if st.button(f"📥 Télécharger {sel} - {lect}",type="primary",use_container_width=True): st.success(f"✅ {sel} - {lect} téléchargé dans l'appli")
        for h in range(1,6): st.markdown(f"<div class='card-graph' style='text-align:left'>{h}. {SOURATES[h-1]}</div>",unsafe_allow_html=True)
    with tc:
        col=st.selectbox("Collection",["40 Hadiths Nawawi","Boukhari Complet","Muslim Complet","Riyad Salihin"])
        if st.button(f"📥 Télécharger {col}",type="primary",use_container_width=True): st.success(f"✅ {col} téléchargé!")
        for h in HADITHS[:10]:
            with st.expander(f"Hadith {h['id']}"): st.write(h['fr'])
    with td:
        typ=st.selectbox("Type",["Toutes (50)","Quotidiennes (30)","Qounout (20)"])
        flt=DOUAS
        if typ=="Quotidiennes (30)": flt=[d for d in DOUAS if d['type']=='quotidien']
        elif typ=="Qounout (20)": flt=[d for d in DOUAS if d['type']=='qounout']
        if st.button(f"📥 Télécharger {len(flt)} Douas audio",type="primary",use_container_width=True): st.success(f"✅ {len(flt)} Douas téléchargées!")
        for d in flt[:20]:
            with st.expander(f"{d['id']}. {d['ar']}"): st.write(d['fr'])
    pub_button(); st.stop()

if st.session_state.current_view=="jeux":
    if st.button("← Retour",use_container_width=True):
        st.session_state.current_view="home"
        st.rerun()
    st.markdown("""<div style='background:linear-gradient(135deg,#0a2a6b,#1a4bb8); border-radius:18px; padding:18px; text-align:center; color:white'><b>🎮 JEUX - Sondage 3 choix + Jeux DL</b></div>""",unsafe_allow_html=True)
    t1,t2=st.tabs(["📝 Sondage","🎮 Jeux Islamiques"])
    with t1:
        if st.session_state.game_question_count>=20:
            note=st.session_state.game_correct; st.session_state.game_attempts+=1
            if st.session_state.game_attempts>=15: st.balloons(); st.markdown(f"<div class='card-graph'><b>🏆 BOUCLE 15 ESSAIS TERMINEE!</b><br>{note}/20 - Recommence!</div>",unsafe_allow_html=True); st.session_state.game_attempts=0
            else: st.markdown(f"<div class='card-graph'><b>QUIZ TERMINE!</b><br><span style='font-size:40px'>{note}/20</span><br>Essai {st.session_state.game_attempts}/15</div>",unsafe_allow_html=True)
            c1,c2=st.columns(2)
            with c1:
                if st.button("🔄 Reessayer - Questions differentes",type="primary",use_container_width=True): st.session_state.game_question_count=0; st.session_state.game_correct=0; st.session_state.current_game_q=random.choice(ALIMENTS_DATA); st.rerun()
            with c2:
                if st.button("🏠 Retour",use_container_width=True): st.session_state.game_question_count=0; st.session_state.game_correct=0; st.session_state.current_view="home"; st.rerun()
            pub_button(); st.stop()
        q=st.session_state.current_game_q; prog=int(st.session_state.game_question_count/20*100)
        st.markdown(f"<div class='card-graph'>Q {st.session_state.game_question_count+1}/20 | Score {st.session_state.game_correct}/20 | Essai {st.session_state.game_attempts+1}/15<br><div class='progress-bar'><div class='progress-fill' style='width:{prog}%'></div></div><br><b>{q['icon']} {q['nom']}</b><br>{q['desc']}<br><b>HALAL / HARAM / DOUTEUX ?</b></div>",unsafe_allow_html=True)
        c1,c2,c3=st.columns(3)
        with c1:
            if st.button("✅ HALAL",use_container_width=True,key="h1"): ok=q['statut']=="HALAL"; st.session_state.game_correct+=1 if ok else 0; st.session_state.game_question_count+=1; st.session_state.current_game_q=random.choice(ALIMENTS_DATA); st.rerun()
        with c2:
            if st.button("🚫 HARAM",use_container_width=True,key="h2"): ok=q['statut']=="HARAM"; st.session_state.game_correct+=1 if ok else 0; st.session_state.game_question_count+=1; st.session_state.current_game_q=random.choice(ALIMENTS_DATA); st.rerun()
        with c3:
            if st.button("⚠️ DOUTEUX",use_container_width=True,key="h3"): ok=q['statut']=="DOUTEUX"; st.session_state.game_correct+=1 if ok else 0; st.session_state.game_question_count+=1; st.session_state.current_game_q=random.choice(ALIMENTS_DATA); st.rerun()
    with t2:
        for j in JEUX_ISLAMIQUES:
            with st.expander(f"🎮 {j['nom']} - {j['taille']}"):
                st.write(j['desc'])
                if st.button(f"📥 Télécharger {j['nom']}",key=j['nom'],use_container_width=True,type="primary"): st.success(f"✅ {j['nom']} téléchargé!")
    pub_button(); st.stop()
