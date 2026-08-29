import streamlit as st
from PIL import Image
import pytesseract
from gtts import gTTS
from io import BytesIO

st.set_page_config(page_title="Scanner Halal Pro", page_icon="🕌", layout="centered")

# --- CONFIG ---
LIEN_WAVE = "https://pay.wave.com/m/M_ci_bqKBEWPbP0O0/c/ci/?amount=1500"
INGREDIENTS_HARAM = ["porc", "gélatine", "gelatine", "alcool", "ethanol", "lard", "saindoux", "cochenille", "E120", "E441", "E542", "vin", "bière", "rhum"]
INGREDIENTS_DOUTEUX = ["E471", "E472", "arôme", "arome", "lécithine", "lecithine"]

def parler(texte):
    try:
        tts = gTTS(text=texte, lang='fr')
        mp3_fp = BytesIO()
        tts.write_to_fp(mp3_fp)
        st.audio(mp3_fp, format='audio/mp3')
    except:
        pass

def analyser(texte):
    texte = texte.lower()
    haram_trouve = [i for i in INGREDIENTS_HARAM if i.lower() in texte]
    douteux_trouve = [i for i in INGREDIENTS_DOUTEUX if i.lower() in texte]
    if haram_trouve:
        return "HARAM", haram_trouve, "Ce produit contient un ingrédient Haram."
    elif douteux_trouve:
        return "DOUTEUX", douteux_trouve, "Attention, ingrédient douteux détecté, vérifiez."
    else:
        return "HALAL", [], "Aucun ingrédient Haram détecté, semble Halal."

# --- INTERFACE ---
st.title("🕌 Scanner Halal Pro")
st.markdown("Scannez les étiquettes et vérifiez en **voix**.")

st.link_button("💳 PAYER 1500F POUR DÉBLOQUER (WAVE)", LIEN_WAVE, type="primary", use_container_width=True)

code_acces = st.text_input("🔑 Entre ton code reçu après paiement Wave :", placeholder="Entre WAVE ou 1500")
acces_ok = code_acces.strip().lower() in ["wave", "1500", "halal", "payé", "paye"]

if acces_ok:
    st.success("✅ Accès débloqué! Tu peux scanner.")
    parler("Accès débloqué. Vous pouvez scanner votre produit.")

    source = st.radio("Source image :", ["📷 Caméra", "📁 Galerie"])
    image = None
    if source == "📷 Caméra":
        image = st.camera_input("Prends l'étiquette en photo")
    else:
        image = st.file_uploader("Choisis une photo d'étiquette", type=["jpg","png","jpeg"])

    if image:
        img = Image.open(image)
        st.image(img, caption="Image analysée", use_column_width=True)
        with st.spinner("Lecture de l'étiquette..."):
            try:
                texte_lu = pytesseract.image_to_string(img, lang='fra+eng')
            except:
                texte_lu = pytesseract.image_to_string(img)

        st.text_area("Texte lu :", texte_lu, height=150)

        if texte_lu.strip():
            statut, ingredients, message = analyser(texte_lu)
            if statut == "HARAM":
                st.error(f"🔴 {statut} - Trouvé : {', '.join(ingredients)}")
                st.write(message)
                parler(f"Attention Haram détecté. Ingrédient {ingredients[0]} trouvé.")
            elif statut == "DOUTEUX":
                st.warning(f"🟡 {statut} - Trouvé : {', '.join(ingredients)}")
                st.write(message)
                parler(f"Produit douteux. {ingredients[0]} détecté.")
            else:
                st.success(f"🟢 {statut} - {message}")
                parler("Produit Halal. Aucun ingrédient Haram détecté.")
        else:
            st.warning("Je n'ai rien pu lire. Rapproche la photo.")
else:
    st.info("👆 Paie 1500F avec le bouton Wave ci-dessus, puis tape WAVE pour débloquer le scanner.")
    parler("Veuillez payer 1500 francs pour débloquer le scanner.")

# --- Pour toi : mets à jour requirements.txt ---
# streamlit
# pillow
# gTTS
# pytesseract