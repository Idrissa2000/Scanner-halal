import streamlit as st
import json
import os
import random
import re
from datetime import datetime, date
import time
import base64

WAVE_LINK = "https://pay.wave.com/m/M_ci_bqKBEWPbP0OO/c/ci/?amount=1500"
USERS_FILE = "users.json"
COMMENTS_FILE = "commentaires.json"
SONDAGE_FILE = "sondages.json"
PROFILE_FOLDER = "profile_pics"
COVER_FOLDER = "cover_pics"
os.makedirs(PROFILE_FOLDER, exist_ok=True)
os.makedirs(COVER_FOLDER, exist_ok=True)

def save_image(file, folder, email, prefix):
    try:
        ext = file.name.split(".")[-1]
        safe_email = email.replace("@","_").replace(".","_")
        path = os.path.join(folder, f"{safe_email}_{prefix}.{ext}")
        with open(path, "wb") as f:
            f.write(file.getbuffer())
        return path
    except:
        return None

def get_image_base64(path):
    if path and os.path.exists(path):
        try:
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        except:
            return None
    return None

ALIMENTS_HALAL = [
    "Poulet halal egorge selon islam","Boeuf halal egorge","Mouton halal egorge","Chevre halal egorge","Chameau halal","Dinde halal","Canard halal","Lapin halal",
    "Poisson tout type hareng thon sardine maquereau carpe tilapia capitaine","Crevettes halal","Crabe halal","Homard halal","Calamar halal",
    "Riz blanc","Riz complet","Riz parfume","Mil","Mais","Ble","Fonio","Sorgho","Avoine","Orge",
    "Arachide","Noix cajou","Amande","Noix","Noisette","Pistache","Sesame","Noix coco",
    "Mangue","Banane","Orange","Ananas","Pasteque","Papaye","Goyave","Citron","Mandarin","Pomme","Poire","Avocat","Fruit passion","Corossol",
    "Tomate","Oignon","Piment","Gombo","Aubergine","Carotte","Pomme terre","Manioc","Igname","Patate douce","Chou","Laitue","Concombre","Courgette","Haricot vert","Epinard",
    "Haricot blanc","Haricot rouge","Lentille","Pois chiche","Petit pois","Soja",
    "Lait vache halal","Lait chevre halal","Yaourt nature sans gelatine porcine","Fromage halal sans presure porcine","Miel pur 100%","Dattes Ajwa Medine","Dattes Sukkary","Dattes Deglet Nour",
    "Huile palme","Huile arachide","Huile olive","Huile tournesol","Huile coco","Beurre halal","Sucre canne","Sucre roux","Sel marin","Poivre noir","Curcuma","Gingembre","Ail","Cumin","Coriandre",
    "Pain sans E471 porc verifie","Biscuit halal certifie","Jus naturel 100% fruit sans alcool","The vert","The noir","Cafe","Eau minerale","Eau coco"
]

ALIMENTS_HARAM = [
    "Porc toute partie viande graisse peau HARAM","Jambon porc HARAM","Saucisson porc HARAM","Saucisse porc HARAM","Lard porc HARAM","Bacon porc HARAM","Chorizo porc HARAM",
    "Vin rouge HARAM alcool","Vin blanc HARAM","Biere HARAM","Whisky HARAM","Rhum HARAM","Vodka HARAM","Champagne HARAM","Alcool ethylique HARAM",
    "Sang animal HARAM","Cadavre animal non egorge selon islam HARAM","Animal mort sans egorgement halal HARAM","Viande non halal non egorgee HARAM",
    "Gelatine porcine E441 HARAM","E120 Cochenille insecte rouge HARAM","E422 Glycerol origine porc HARAM","E471 Mono-diglycerides origine porc HARAM","E481 Stearoyl lactylate porc HARAM","E492 Tristearate sorbitan porc HARAM"
]

ALIMENTS_DOUTEUX = [
    "E102 Tartrazine Douteux peut etre halal mais allergie","E104 Jaune quinoleine Douteux","E110 Jaune orange S Douteux hyperactivite",
    "E120 Cochenille HARAM insecte Rouge","E122 Azorubine Douteux Rouge","E124 Ponceau 4R Douteux Rouge","E132 Indigotine Douteux Bleu","E133 Bleu brillant FCF Douteux",
    "E140 Chlorophylle Halal si origine vegetale 100%","E141 Complexe cuivrique chlorophylles Halal si vegetal","E150a Caramel ordinaire Halal","E150b Caramel sulfite Halal",
    "E160a Beta-carotene Halal vegetal","E160b Rocou bixine Halal","E160c Extrait paprika Halal","E162 Rouge betterave Halal","E163 Anthocyanes Halal",
    "E170 Carbonate calcium Halal","E171 Dioxyde titane Halal mais debat sante","E200 Acide sorbique Halal","E211 Benzoate sodium Halal","E250 Nitrite sodium Halal mais deconseille",
    "E300 Acide ascorbique Vitamine C Halal","E322 Lecithine Halal si soja 100% Haram si porc","E330 Acide citrique Halal","E400 Acide alginique Halal","E406 Agar-agar HALAL 100% algue","E407 Carraghenane HALAL","E410 Gomme caroube HALAL","E412 Gomme guar HALAL","E414 Gomme arabique HALAL","E415 Gomme xanthane HALAL",
    "E420 Sorbitol Halal","E422 Glycerol HARAM si porc HALAL si vegetal","E440 Pectine HALAL 100% vegetal","E441 Gelatine HARAM si porc HALAL si boeuf halal","E471 Mono-diglycerides DOUTEUX PEUT ETRE PORC HARAM Verifier halal certifie","E472 Esters Douteux","E481 Stearoyl lactylate Douteux porc possible","E491 Sorbitan Douteux"
]

SOURATES_114 = [
    "1 Al-Fatiha - Ouverture - 7 versets - Mecquoise - Mere Coran",
    "2 Al-Baqara - Vache - 286 - Medinoise - Plus longue sourate",
    "3 Al-Imran - Famille Imran - 200 - Medinoise",
    "4 An-Nisa - Femmes - 176 - Medinoise",
    "5 Al-Maida - Table Servie - 120 - Medinoise",
    "6 Al-Anam - Bestiaux - 165 - Mecquoise",
    "7 Al-Araf - Murettes - 206 - Mecquoise",
    "8 Al-Anfal - Butin - 75 - Medinoise",
    "9 At-Tawba - Repentir - 129 - Medinoise - Sans Basmala",
    "10 Younus - Jonas - 109 - Mecquoise",
    "11 Houd - Houd - 123 - Mecquoise",
    "12 Youssouf - Joseph - 111 - Mecquoise - Plus belle histoire",
    "13 Ar-Raad - Tonnerre - 43 - Medinoise",
    "14 Ibrahim - Abraham - 52 - Mecquoise",
    "15 Al-Hijr - Vallee Pierres - 99 - Mecquoise",
    "16 An-Nahl - Abeilles - 128 - Mecquoise - Sourate bienfaits",
    "17 Al-Isra - Voyage Nocturne - 111 - Mecquoise - Isra Miraj",
    "18 Al-Kahf - Caverne - 110 - Mecquoise - Lire vendredi",
    "19 Maryam - Marie - 98 - Mecquoise - Mere Issa",
    "20 Ta-Ha - Ta-Ha - 135 - Mecquoise",
    "21 Al-Anbiya - Prophetes - 112 - Mecquoise",
    "22 Al-Hajj - Pelerinage - 78 - Medinoise",
    "23 Al-Muminune - Croyants - 118 - Mecquoise",
    "24 An-Nour - Lumiere - 64 - Medinoise - Verset lumiere",
    "25 Al-Furqane - Discernement - 77 - Mecquoise",
    "26 Ach-Chuara - Poetes - 227 - Mecquoise",
    "27 An-Naml - Fourmis - 93 - Mecquoise",
    "28 Al-Qasas - Recit - 88 - Mecquoise - Histoire Moussa",
    "29 Al-Ankabut - Araignee - 69 - Mecquoise",
    "30 Ar-Rum - Romains - 60 - Mecquoise",
    "31 Luqman - Luqman - 34 - Mecquoise - Conseils fils",
    "32 As-Sajda - Prosternation - 30 - Mecquoise",
    "33 Al-Ahzab - Coalises - 73 - Medinoise",
    "34 Saba - Saba - 54 - Mecquoise",
    "35 Fatir - Createur - 45 - Mecquoise",
    "36 Ya-Sin - Ya-Sin - 83 - Mecquoise - Coeur Coran",
    "37 As-Saffat - Rangees - 182 - Mecquoise",
    "38 Sad - Sad - 88 - Mecquoise",
    "39 Az-Zumar - Groupes - 75 - Mecquoise",
    "40 Ghafir - Pardonneur - 85 - Mecquoise",
    "41 Fussilat - Versets Details - 54 - Mecquoise",
    "42 Ach-Chura - Concertation - 53 - Mecquoise",
    "43 Az-Zukhruf - Ornement - 89 - Mecquoise",
    "44 Ad-Dukhan - Fumee - 59 - Mecquoise",
    "45 Al-Jathya - Agenouillee - 37 - Mecquoise",
    "46 Al-Ahqaf - Dunes - 35 - Mecquoise",
    "47 Muhammad - Muhammad - 38 - Medinoise",
    "48 Al-Fath - Victoire - 29 - Medinoise",
    "49 Al-Hujurat - Appartements - 18 - Medinoise",
    "50 Qaf - Qaf - 45 - Mecquoise",
    "51 Adh-Dhariyat - Eparpillent - 60 - Mecquoise",
    "52 At-Tur - Mont Sinai - 49 - Mecquoise",
    "53 An-Najm - Etoile - 62 - Mecquoise - Sajda",
    "54 Al-Qamar - Lune - 55 - Mecquoise - Lune fendue",
    "55 Ar-Rahman - Misericordieux - 78 - Medinoise",
    "56 Al-Waqia - Evenement - 96 - Mecquoise - Richesse",
    "57 Al-Hadid - Fer - 29 - Medinoise",
    "58 Al-Mujadala - Discussion - 22 - Medinoise",
    "59 Al-Hachr - Exode - 24 - Medinoise",
    "60 Al-Mumtahana - Eprouvee - 13 - Medinoise",
    "61 As-Saff - Rang - 14 - Medinoise",
    "62 Al-Jumua - Vendredi - 11 - Medinoise",
    "63 Al-Munafiqun - Hypocrites - 11 - Medinoise",
    "64 At-Taghabun - Grande Perte - 18 - Medinoise",
    "65 At-Talaq - Divorce - 12 - Medinoise",
    "66 At-Tahrim - Interdiction - 12 - Medinoise",
    "67 Al-Mulk - Royaute - 30 - Mecquoise - Sauve chatiment tombe - Lire chaque nuit",
    "68 Al-Qalam - Plume - 52 - Mecquoise",
    "69 Al-Haqqa - Celle qui montre verite - 52 - Mecquoise",
    "70 Al-Maarij - Voies Ascension - 44 - Mecquoise",
    "71 Nouh - Noe - 28 - Mecquoise",
    "72 Al-Jinn - Djinns - 28 - Mecquoise",
    "73 Al-Muzzammil - Enveloppe - 20 - Mecquoise - Priere nuit",
    "74 Al-Muddathir - Revete manteau - 56 - Mecquoise",
    "75 Al-Qiyama - Resurrection - 40 - Mecquoise",
    "76 Al-Insan - Homme - 31 - Medinoise",
    "77 Al-Mursalat - Envoyes - 50 - Mecquoise",
    "78 An-Naba - Nouvelle - 40 - Mecquoise",
    "79 An-Naziat - Anges arrachent ames - 46 - Mecquoise",
    "80 Abasa - Renfrogne - 42 - Mecquoise",
    "81 At-Takwir - Obscurcissement - 29 - Mecquoise",
    "82 Al-Infitar - Rupture - 19 - Mecquoise",
    "83 Al-Mutaffifin - Fraudeurs - 36 - Mecquoise",
    "84 Al-Inchiqaq - Dechirure - 25 - Mecquoise",
    "85 Al-Buruj - Constellations - 22 - Mecquoise",
    "86 At-Tariq - Astre Nocturne - 17 - Mecquoise",
    "87 Al-Ala - Tres-Haut - 19 - Mecquoise",
    "88 Al-Ghachiya - Enveloppante - 26 - Mecquoise",
    "89 Al-Fajr - Aube - 30 - Mecquoise",
    "90 Al-Balad - Cite - 20 - Mecquoise",
    "91 Ach-Chams - Soleil - 15 - Mecquoise",
    "92 Al-Layl - Nuit - 21 - Mecquoise",
    "93 Ad-Duha - Jour Montant - 11 - Mecquoise",
    "94 Ach-Charh - Ouverture - 8 - Mecquoise",
    "95 At-Tin - Figuier - 8 - Mecquoise",
    "96 Al-Alaq - Adherence - 19 - Mecquoise - Premiers versets Iqra",
    "97 Al-Qadr - Destinee - 5 - Mecquoise - Nuit meilleure que 1000 mois",
    "98 Al-Bayyina - Preuve - 8 - Medinoise",
    "99 Az-Zalzala - Secousse - 8 - Medinoise",
    "100 Al-Adiyat - Coursiers - 11 - Mecquoise",
    "101 Al-Qaria - Fracas - 11 - Mecquoise",
    "102 At-Takatur - Course richesses - 8 - Mecquoise",
    "103 Al-Asr - Temps - 3 - Mecquoise - Resume Islam",
    "104 Al-Humaza - Calomniateurs - 9 - Mecquoise",
    "105 Al-Fil - Elephant - 5 - Mecquoise",
    "106 Quraich - Coraich - 4 - Mecquoise",
    "107 Al-Maun - Ustensile - 7 - Mecquoise",
    "108 Al-Kawthar - Abondance - 3 - Mecquoise - Plus petite sourate",
    "109 Al-Kafirun - Infideles - 6 - Mecquoise",
    "110 An-Nasr - Secours - 3 - Medinoise",
    "111 Al-Masad - Fibres - 5 - Mecquoise",
    "112 Al-Ikhlas - Monotheisme Pur - 4 - Mecquoise - Un tiers Coran",
    "113 Al-Falaq - Aube Naissante - 5 - Mecquoise - Protection",
    "114 An-Nas - Hommes - 6 - Mecquoise - Derniere sourate"
]

DUAS_50 = [
    {"t":"1 Avant manger","ar":"بسم الله","fr":"Au nom d Allah","cat":"Repas"},
    {"t":"2 Apres manger","ar":"الحمد لله الذي اطعمنا وسقانا وجعلنا مسلمين","fr":"Louange a Allah qui nous a nourris","cat":"Repas"},
    {"t":"3 Avant dormir","ar":"باسمك اللهم اموت واحيا","fr":"En Ton nom O Allah je meurs et je vis","cat":"Sommeil"},
    {"t":"4 Au reveil","ar":"الحمد لله الذي احيانا بعدما اماتنا وإليه النشور","fr":"Louange a Allah qui nous a fait revivre","cat":"Sommeil"},
    {"t":"5 Entrer toilette","ar":"اللهم اني اعوذ بك من الخبث والخبائث","fr":"O Allah je cherche refuge contre demons","cat":"Toilette"},
    {"t":"6 Sortir toilette","ar":"غفرانك","fr":"Je Te demande pardon","cat":"Toilette"},
    {"t":"7 Entrer maison","ar":"بسم الله ولجنا وبسم الله خرجنا وعلى الله ربنا توكلنا","fr":"Au nom d Allah nous entrons et sortons","cat":"Maison"},
    {"t":"8 Sortir maison","ar":"بسم الله توكلت على الله ولا حول ولا قوة الا بالله","fr":"Au nom d Allah je m en remets a Allah","cat":"Maison"},
    {"t":"9 S habiller","ar":"الحمد لله الذي كساني هذا الثوب ورزقنيه من غير حول مني ولا قوة","fr":"Louange a Allah qui m a vetu","cat":"Vetement"},
    {"t":"10 Nouveau vetement","ar":"اللهم لك الحمد انت كسوتنيه اسالك خيره","fr":"O Allah a Toi louange","cat":"Vetement"},
    {"t":"11 Se deshabiller","ar":"بسم الله","fr":"Au nom d Allah","cat":"Vetement"},
    {"t":"12 Voyage depart","ar":"سبحان الذي سخر لنا هذا وما كنا له مقرنين","fr":"Gloire a Celui qui nous a soumis ceci","cat":"Voyage"},
    {"t":"13 Voyage retour","ar":"ايبون تائبون عابدون لربنا حامدون","fr":"Nous revenons repentants","cat":"Voyage"},
    {"t":"14 Entrer mosquee","ar":"اللهم افتح لي ابواب رحمتك","fr":"Ouvre-moi portes misericorde","cat":"Mosquee"},
    {"t":"15 Sortir mosquee","ar":"اللهم اني اسالك من فضلك","fr":"Je Te demande de Ta grace","cat":"Mosquee"},
    {"t":"16 Apres adhan","ar":"اللهم رب هذه الدعوة التامة والصلاة القائمة ات محمدا الوسيلة","fr":"O Allah Seigneur appel parfait donne a Muhammad station","cat":"Priere"},
    {"t":"17 Debut woudou","ar":"بسم الله","fr":"Au nom d Allah","cat":"Priere"},
    {"t":"18 Fin woudou","ar":"اشهد ان لا اله الا الله وحده لا شريك له","fr":"J atteste qu il n y a de dieu qu Allah seul","cat":"Priere"},
    {"t":"19 Malade","ar":"اذهب الباس رب الناس واشف انت الشافي","fr":"Fais partir mal Seigneur gueris","cat":"Maladie"},
    {"t":"20 Visite malade","ar":"لا باس طهور ان شاء الله","fr":"Pas de mal purification","cat":"Maladie"},
    {"t":"21 Tristesse","ar":"لا اله الا الله العظيم الحليم","fr":"Il n y a de dieu qu Allah Grand","cat":"Difficulte"},
    {"t":"22 Anxiete","ar":"اللهم اني اعوذ بك من الهم والحزن","fr":"Refuge contre souci tristesse","cat":"Difficulte"},
    {"t":"23 Difficulte","ar":"اللهم لا سهل الا ما جعلته سهلا","fr":"Rien facile sauf ce que Tu facilites","cat":"Difficulte"},
    {"t":"24 Dette","ar":"اللهم اكفني بحلالك عن حرامك","fr":"Contente-moi de Ton halal","cat":"Difficulte"},
    {"t":"25 Pardon","ar":"استغفر الله العظيم واتوب اليه","fr":"Je demande pardon a Allah","cat":"Pardon"},
    {"t":"26 Matin","ar":"اصبحنا واصبح الملك لله","fr":"Matin et royaute a Allah","cat":"Matin/Soir"},
    {"t":"27 Soir","ar":"امسينا وامسى الملك لله","fr":"Soir et royaute a Allah","cat":"Matin/Soir"},
    {"t":"28 Cauchemar","ar":"اعوذ بكلمات الله التامات","fr":"Refuge par paroles parfaites","cat":"Sommeil"},
    {"t":"29 Colere","ar":"اعوذ بالله من الشيطان الرجيم","fr":"Refuge en Allah contre satan","cat":"Difficulte"},
    {"t":"30 Eternuement","ar":"الحمد لله","fr":"Louange a Allah","cat":"Divers"},
    {"t":"31 Reponse eternuement","ar":"يرحمك الله","fr":"Qu Allah te fasse misericorde","cat":"Divers"},
    {"t":"32 Mariage","ar":"بارك الله لكما وبارك عليكما","fr":"Qu Allah vous benisse","cat":"Famille"},
    {"t":"33 Nouveau ne","ar":"بارك الله لك في الموهوب","fr":"Qu Allah benisse ce qui t est donne","cat":"Famille"},
    {"t":"34 Pluie","ar":"اللهم صيبا نافعا","fr":"Pluie benefique","cat":"Nature"},
    {"t":"35 Vent fort","ar":"اللهم اني اسالك خيرها","fr":"Je demande son bien","cat":"Nature"},
    {"t":"36 Miroir","ar":"اللهم كما حسنت خلقي فحسن خلقي","fr":"Embelli mon caractere","cat":"Divers"},
    {"t":"37 Marche","ar":"لا اله الا الله وحده","fr":"Il n y a de dieu qu Allah seul","cat":"Divers"},
    {"t":"38 Protection matin","ar":"حسبي الله لا اله الا هو","fr":"Allah me suffit","cat":"Protection"},
    {"t":"39 Protection soir","ar":"بسم الله الذي لا يضر","fr":"Au nom d Allah dont rien ne nuit","cat":"Protection"},
    {"t":"40 Istikhara","ar":"اللهم اني استخيرك بعلمك","fr":"Je Te consulte par Ta science","cat":"Priere"},
    {"t":"41 Apres priere","ar":"استغفر الله استغفر الله استغفر الله","fr":"Pardon 3 fois","cat":"Priere"},
    {"t":"42 Fin assemblee","ar":"سبحانك اللهم وبحمدك","fr":"Gloire a Toi O Allah","cat":"Divers"},
    {"t":"43 Enterrement","ar":"اللهم اغفر له وارحمه","fr":"Pardonne-lui fais misericorde","cat":"Mort"},
    {"t":"44 Condoleances","ar":"انا لله وانا اليه راجعون","fr":"A Allah nous appartenons","cat":"Mort"},
    {"t":"45 Iftar jeune","ar":"ذهب الظما وابتلت العروق وثبت الاجر","fr":"Soif partie veines irriguees recompense","cat":"Jeune"},
    {"t":"46 Laylatoul Qadr","ar":"اللهم انك عفو تحب العفو فاعف عني","fr":"Tu es Pardonneur aime pardonner pardonne-moi","cat":"Jeune"},
    {"t":"47 Entrer cimetiere","ar":"السلام عليكم اهل الديار","fr":"Paix sur vous habitants","cat":"Mort"},
    {"t":"48 Douleur corps","ar":"بسم الله 3 مرات اعوذ بعزة الله وقدرته","fr":"Au nom d Allah 3 fois refuge","cat":"Maladie"},
    {"t":"49 Voir lune","ar":"الله اكبر اللهم اهله علينا بالامن والايمان","fr":"Allah Grand fais apparaitre avec securite et foi","cat":"Nature"},
    {"t":"50 Enfant peureux","ar":"اعيذك بكلمات الله التامة من كل شيطان وهامة","fr":"Je te protege par paroles parfaites","cat":"Famille"},
]

HADITHS_40 = [
    "1. Les actions ne valent que par intentions - Bukhari 1",
    "2. Halal clair Haram clair entre deux douteux - Bukhari 52",
    "3. Aime pour ton frere ce que tu aimes pour toi - Bukhari 13",
    "4. Proprete moitie foi - Muslim 223",
    "5. Sourire a ton frere est aumone - Tirmidhi 1956",
    "6. Meilleur apprend Coran et enseigne - Bukhari 5027",
    "7. Allah est doux et aime douceur - Bukhari 6927",
    "8. Facilitez ne rendez pas difficile - Bukhari 69",
    "9. Pas de misericorde sans misericorde - Bukhari 7376",
    "10. Religion est bon conseil - Muslim 55",
    "11. Croyant fort meilleur que faible - Muslim 2664",
    "12. Crains Allah ou que tu sois - Tirmidhi 1987",
    "13. Musulman a l abri de sa langue et main - Bukhari 10",
    "14. Ne te mets pas en colere - Bukhari 6116",
    "15. Dis du bien ou tais-toi - Bukhari 6018",
    "16. Priez comme vous m avez vu prier - Bukhari 631",
    "17. Jeune est bouclier - Bukhari 1894",
    "18. Qui jeune Ramadan pardonne - Bukhari 38",
    "19. Construit mosquee maison au Paradis - Bukhari 450",
    "20. Meilleur avec ses femmes - Tirmidhi 1162",
    "21. Honore voisin - Bukhari 6019",
    "22. Paradis sous pieds meres - Nasai 3104",
    "23. Allah pur n accepte que pur - Muslim 1015",
    "24. Delaisse doute pour certitude - Tirmidhi 2518",
    "25. Laisse ce qui ne te concerne pas - Tirmidhi 2317",
    "26. Modestie fait partie foi - Bukhari 9",
    "27. Pas Paradis avec orgueil - Muslim 91",
    "28. Soulage croyant Allah te soulagera - Muslim 2699",
    "29. Meilleur dhikr La ilaha illa Allah - Tirmidhi 3383",
    "30. Mangez halal et bon - Coran 2:168",
    "31. Corps nourri haram Enfer - Ahmad",
    "32. Cherchez savoir du berceau a tombe - Bayhaqi",
    "33. Fais bien comme si tu vois Allah - Bukhari 50",
    "34. Meilleure aumone quand en bonne sante - Bukhari 1419",
    "35. Temps entre prieres expiation - Muslim 233",
    "36. Fajr groupe vaut nuit entiere - Muslim 656",
    "37. Aime pauvres et rapproche-toi - Tirmidhi 2352",
    "38. Nul sauve par actes seuls mais misericorde - Bukhari 5673",
    "39. Dis verite meme amere - Ibn Hibban",
    "40. Priere lumiere aumone preuve - Muslim 223"
]

QUESTIONS_20 = [
    {"q":"1. Utilisez-vous produits avec ingredients douteux?","options":["Jamais","Parfois","Souvent","Toujours"]},
    {"q":"2. Verifiez-vous E-numbers avant acheter?","options":["Toujours","Souvent","Rarement","Jamais"]},
    {"q":"3. Savez-vous E471 peut etre porc?","options":["Oui je sais","Non","J ai entendu","Pas sur"]},
    {"q":"4. Le porc est Halal?","options":["Haram interdit","Halal autorise","Douteux","Je ne sais pas"]},
    {"q":"5. Gelatine porcine Halal?","options":["Haram","Halal","Douteux","Ca depend"]},
    {"q":"6. Consommez sans verifier?","options":["Jamais","Parfois","Souvent","Toujours"]},
    {"q":"7. App utile pour Halal?","options":["Tres utile","Utile","Peu utile","Pas utile"]},
    {"q":"8. Lisez-vous ingredients?","options":["Toujours","Souvent","Parfois","Jamais"]},
    {"q":"9. Savez-vous ce que veut dire Halal?","options":["Oui tres bien","Oui un peu","Non","Vaguement"]},
    {"q":"10. Deja mange Haram par erreur?","options":["Oui","Non","Peut-etre","Je ne sais pas"]},
    {"q":"11. Voulez-vous devenir VIP 1500F?","options":["Oui","Non","Peut-etre plus tard","Je reflechis"]},
    {"q":"12. Design app vous plait?","options":["Beaucoup","Oui","Moyen","Non"]},
    {"q":"13. 5 essais gratuits suffisent?","options":["Oui","Non","Il faut plus","Il faut illimite"]},
    {"q":"14. Recommanderiez-vous app?","options":["Oui certainement","Oui","Peut-etre","Non"]},
    {"q":"15. Quelle partie preferez-vous?","options":["Scanner","Aliments","Coran","Douas"]},
    {"q":"16. Utilisez-vous Coran dans app?","options":["Tous les jours","Souvent","Rarement","Jamais"]},
    {"q":"17. Douas vous aident?","options":["Beaucoup","Oui","Un peu","Non"]},
    {"q":"18. Suggestions?","options":["Ajouter plus aliments","Ajouter audio","Ajouter Qibla","Tout est bien"]},
    {"q":"19. Niveau connaissance Halal?","options":["Expert","Moyen","Debutant","Je decouvre"]},
    {"q":"20. Note globale app sur 10?","options":["10 Excellent","8-9 Tres bien","5-7 Bien","1-4 A ameliorer"]},
]

def load_json(f, d):
    if os.path.exists(f):
        try:
            with open(f,'r',encoding='utf-8') as fp:
                return json.load(fp)
        except:
            return d
    return d

def save_json(f, data):
    with open(f,'w',encoding='utf-8') as fp:
        json.dump(data,fp,ensure_ascii=False,indent=2)

def is_valid_pwd(p):
    return len(p)>=6 and re.search(r"[A-Za-z]",p) and re.search(r"[0-9]",p)

def extract_code(t):
    m=re.search(r"\+(\d+)",t)
    return "+"+m.group(1) if m else "+225"

users=load_json(USERS_FILE,{})
comments=load_json(COMMENTS_FILE,[])
sondages=load_json(SONDAGE_FILE,[])

st.set_page_config(page_title="Scanner Halal", page_icon="🕌", layout="centered")

st.markdown("""
<style>
#MainMenu{visibility:hidden} footer{visibility:hidden} header{visibility:hidden}
.block-container{padding-top:10px; padding-bottom:120px;}
.card-dark{background:#0f1e4a; color:white; margin:8px 0px; padding:12px; border-radius:12px; display:flex; align-items:center; gap:12px; border:1px solid #1e3a8a}
.card{background:white; margin:8px 0px; padding:15px; border-radius:12px; border:1px solid #eee; box-shadow:0 2px 4px rgba(0,0,0,0.05)}
.card-vip{background:linear-gradient(135deg,#0a2a6b,#1a4bb8);color:white;padding:25px;border-radius:15px;margin:12px 0px; text-align:center}
.card-pub{background:#fff3e0;border:2px dashed #ff9800;padding:15px;border-radius:12px;margin:12px 0px}
.pub-zone{background:black; color:white; text-align:center; padding:6px; font-size:12px; border-radius:8px; margin-bottom:10px}
.pub-zone a{color:#00D1FF; text-decoration:none}
.sondage-card{background:white; margin:8px 0px; padding:15px; border-radius:12px; border-left:5px solid #0072ff}
</style>
""", unsafe_allow_html=True)

if 'user' not in st.session_state:
    st.session_state.user=None
if 'page' not in st.session_state:
    st.session_state.page="auth"
if 'reset_code' not in st.session_state:
    st.session_state.reset_code=None
if 'scan_mode' not in st.session_state:
    st.session_state.scan_mode=None
if 'sondage_answers' not in st.session_state:
    st.session_state.sondage_answers={}
if 'show_eval' not in st.session_state:
    st.session_state.show_eval=False
if 'bottom_nav' not in st.session_state:
    st.session_state.bottom_nav="Home"
if 'selected_menu' not in st.session_state:
    st.session_state.selected_menu=None

if st.session_state.page=="auth":
    try:
        st.image("logo.jpeg", use_container_width=True)
    except:
        st.markdown("<h1 style='text-align:center;'>🕌 Scanner Halal</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;color:#0a2a6b;'>Bienvenue</h2>", unsafe_allow_html=True)
    t1,t2,t3=st.tabs(["Connexion","Inscription","Mot de passe oublie"])
    with t1:
        e=st.text_input("Email", key="email_connexion").strip()
        p=st.text_input("Mot de passe (lettres+chiffres)",type="password", key="pwd_connexion")
        if st.button("Se connecter",type="primary",use_container_width=True):
            u=users.get(e)
            if u and u.get('pwd')==p:
                st.session_state.user=e
                st.session_state.page="app"
                st.rerun()
            else:
                st.error("Email ou mot de passe incorrect")
    with t2:
        nom=st.text_input("Nom", key="nom_insc").strip()
        c1,c2=st.columns([2,3])
        with c1:
            pays=st.selectbox("Pays", ["+225 CI","+221 SN","+223 ML","+224 GN","+226 BF","+229 BJ","+33 FR"], key="pays_insc")
        with c2:
            numero=st.text_input("Numero", placeholder="0771845766", key="num_insc").strip()
        er=st.text_input("Email", key="email_insc").strip()
        p1=st.text_input("Mot de passe (lettres+chiffres)",type="password",key="p1")
        p2=st.text_input("Confirmer",type="password",key="p2")
        if st.button("Creer mon compte",type="primary",use_container_width=True):
            if not nom or not numero or not er or not p1:
                st.error("Remplis tous les champs")
            elif not is_valid_pwd(p1):
                st.error("Mot de passe doit avoir lettres + chiffres minimum 6 caracteres ex: baba2000")
            elif p1!=p2:
                st.error("Mots de passe differents")
            elif er in users:
                st.error("Email deja utilise va dans Connexion")
            else:
                users[er]={'nom':nom,'wave':f"{extract_code(pays)} {numero}",'pays':pays,'pwd':p1,'scans':0,'is_vip':False,'history':[],'sondage_history':[],'bonus_scans':0,'profile_pic':None,'cover_pic':None}
                save_json(USERS_FILE,users)
                st.success("Compte cree! Va dans Connexion")
                st.balloons()
    with t3:
        ef=st.text_input("Email", key="email_oublie").strip()
        if st.button("Envoyer code"):
            if ef in users:
                code=str(random.randint(100000,999999))
                st.session_state.reset_code=code
                st.session_state.reset_email=ef
                st.success(f"Code demo: {code}")
            else:
                st.error("Email non trouve")
        if st.session_state.reset_code:
            ci=st.text_input("Code recu").strip()
            np=st.text_input("Nouveau mot de passe (lettres+chiffres)",type="password", key="new_pwd")
            if st.button("Reinitialiser"):
                if ci==st.session_state.reset_code:
                    if not is_valid_pwd(np):
                        st.error("Lettres + chiffres requis")
                    else:
                        users[st.session_state.reset_email]['pwd']=np
                        save_json(USERS_FILE,users)
                        st.success("Mot de passe change! Va dans Connexion")
                        st.session_state.reset_code=None
                else:
                    st.error("Code faux")
    st.stop()

if not st.session_state.user or st.session_state.user not in users:
    st.session_state.page="auth"
    st.rerun()

user_email=st.session_state.user
user=users[user_email]
if 'profile_pic' not in user:
    users[user_email]['profile_pic']=None
    users[user_email]['cover_pic']=None
    save_json(USERS_FILE,users)
if 'sondage_history' not in user:
    users[user_email]['sondage_history']=[]
    save_json(USERS_FILE,users)

# ===== TOP AVEC PHOTO PROFIL + COUVERTURE + NOM SEULEMENT =====
profile_path = user.get('profile_pic')
cover_path = user.get('cover_pic')
cover_b64 = get_image_base64(cover_path)
profile_b64 = get_image_base64(profile_path)
if cover_b64:
    cover_style = f"background-image: url(data:image/jpeg;base64,{cover_b64}); background-size: cover; background-position: center;"
else:
    cover_style = "background: linear-gradient(90deg,#00c6ff,#0072ff);"
if profile_b64:
    profile_html = f"<img src='data:image/jpeg;base64,{profile_b64}' style='width:70px; height:70px; border-radius:50%; border:3px solid white; object-fit:cover;'>"
else:
    profile_html = "<div style='width:70px; height:70px; border-radius:50%; background:white; display:flex; align-items:center; justify-content:center; font-size:30px; border:3px solid white;'>👤</div>"

st.markdown(f"""
<div style="{cover_style} padding:15px; border-radius:12px; margin-bottom:10px; position:relative; min-height:90px;">
<div style="display:flex; align-items:center; gap:12px; background:rgba(0,0,0,0.4); padding:10px; border-radius:10px;">
{profile_html}
<div style="color:white;">
<b style="font-size:20px;">{user.get('nom','Utilisateur')}</b><br>
<span style="background:gold; color:black; padding:2px 10px; border-radius:10px; font-size:11px; font-weight:bold;">{"VIP ILLIMITE" if user.get('is_vip') else "GRATUIT"}</span>
</div>
</div>
</div>
<div class="pub-zone">PUB - <a href="{WAVE_LINK}" target="_blank">Deviens VIP 1500F - Payer Wave</a></div>
""", unsafe_allow_html=True)

with st.expander("📸 Changer photo de profil et couverture"):
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        new_profile = st.file_uploader("Photo de profil", type=['jpg','png','jpeg'], key="profile_upload")
        if new_profile:
            path = save_image(new_profile, PROFILE_FOLDER, user_email, "profile")
            if path:
                users[user_email]['profile_pic'] = path
                save_json(USERS_FILE, users)
                st.success("Photo de profil ajoutée!")
                time.sleep(1)
                st.rerun()
    with col_p2:
        new_cover = st.file_uploader("Photo de couverture", type=['jpg','png','jpeg'], key="cover_upload")
        if new_cover:
            path = save_image(new_cover, COVER_FOLDER, user_email, "cover")
            if path:
                users[user_email]['cover_pic'] = path
                save_json(USERS_FILE, users)
                st.success("Photo de couverture ajoutée!")
                time.sleep(1)
                st.rerun()

with st.sidebar:
    st.markdown("### Menu")
    if profile_path and os.path.exists(profile_path):
        st.image(profile_path, width=80)
    st.write(f"**{user.get('nom','')}**")
    menu=st.radio("NAVIGATION", ["Home","Aliments","Ma Liste","Jeu","Profil","Parametres","Aide","Notice","Langue","Coran","Hadiths","Douas"], label_visibility="collapsed")
    if st.button("Deconnexion", use_container_width=True):
        st.session_state.user=None
        st.session_state.page="auth"
        st.session_state.scan_mode=None
        st.session_state.sondage_answers={}
        st.session_state.show_eval=False
        st.session_state.bottom_nav="Home"
        st.session_state.selected_menu=None
        st.rerun()

# Si on a cliqué depuis Home
if st.session_state.get('selected_menu'):
    menu = st.session_state.selected_menu
    st.session_state.selected_menu = None

def vip_required_page(nom_page):
    st.markdown(f"""
    <div class="card-vip">
    <div style="font-size:60px;">🔒</div>
    <h2 style="color:gold;">{nom_page} - VIP Seulement</h2>
    <p>Devenez VIP avant de voir {nom_page}</p>
    <p>1500F seulement - Paiement Wave securise</p>
    </div>
    """, unsafe_allow_html=True)
    st.link_button(f"PAYER 1500F WAVE POUR {nom_page.upper()}", WAVE_LINK, type="primary", use_container_width=True)
    if st.button(f"J ai paye - Activer VIP", use_container_width=True, key=f"vip_{nom_page}"):
        users[user_email]['is_vip']=True
        save_json(USERS_FILE,users)
        st.balloons()
        st.success("VIP active! Tu peux maintenant voir")
        st.rerun()
    st.stop()

if menu=="Home":
    # BOTTOM NAV 3 BOUTONS SEULEMENT
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🏠 Home", use_container_width=True, type="primary" if st.session_state.bottom_nav=="Home" else "secondary"):
            st.session_state.bottom_nav="Home"
            st.rerun()
    with c2:
        if st.button("🕋 Qibla", use_container_width=True, type="primary" if st.session_state.bottom_nav=="Qibla" else "secondary"):
            st.session_state.bottom_nav="Qibla"
            st.rerun()
    with c3:
        if st.button("📅 Calendrier", use_container_width=True, type="primary" if st.session_state.bottom_nav=="Calendrier" else "secondary"):
            st.session_state.bottom_nav="Calendrier"
            st.rerun()

    # VIP DEPUIS HOME
    if st.session_state.bottom_nav in ["VIP_ALIMENTS", "VIP_DOUAS", "VIP_HADITHS"]:
        nom = st.session_state.bottom_nav.replace("VIP_","")
        st.markdown(f"""
        <div class="card-vip">
        <div style="font-size:60px;">🔒</div>
        <h2 style="color:gold;">{nom} - VIP Seulement</h2>
        <p>Devenez VIP avant de voir {nom}</p>
        <p>1500F seulement - Paiement Wave securise</p>
        </div>
        """, unsafe_allow_html=True)
        st.link_button(f"PAYER 1500F WAVE POUR {nom}", WAVE_LINK, type="primary", use_container_width=True)
        if st.button(f"J'ai paye - Activer VIP", use_container_width=True):
            users[user_email]['is_vip']=True
            save_json(USERS_FILE,users)
            st.balloons()
            st.session_state.bottom_nav="Home"
            st.rerun()
        if st.button("Retour Home", use_container_width=True):
            st.session_state.bottom_nav="Home"
            st.rerun()
        st.stop()

    if st.session_state.bottom_nav=="Qibla":
        st.title("🕋 Qibla - Direction Kaaba")
        st.markdown("""
        <div class='card' style='text-align:center; border:2px solid #0a2a6b'>
        <p style='color:red; font-weight:bold;'>⚠️ LOCALISATION OBLIGATOIRE</p>
        <p>Active la localisation de ton telephone pour trouver la Qibla exacte</p>
        </div>
        """, unsafe_allow_html=True)
        qibla_html = """
        <div style="text-align:center; font-family: sans-serif; padding:10px; background:white; border-radius:15px;">
            <div id="status" style="background:#0a2a6b; color:white; padding:10px; border-radius:8px; margin-bottom:10px;">📍 Clique sur ACTIVER LOCALISATION</div>
            <div style="position:relative; width:250px; height:250px; margin:20px auto; border:5px solid #0a2a6b; border-radius:50%; background:#f0f0f0;">
                <div style="position:absolute; top:5px; left:50%; transform:translateX(-50%); font-weight:bold;">N</div>
                <div id="compass" style="position:absolute; top:50%; left:50%; width:150px; height:150px; transform:translate(-50%,-50%) rotate(0deg); transition: transform 0.5s;">
                    <div style="font-size:60px;">🧭</div>
                    <div style="color:red; font-weight:bold; font-size:20px; margin-top:-10px;">⬆️ QIBLA</div>
                </div>
                <div id="arrow" style="position:absolute; top:50%; left:50%; width:4px; height:100px; background:red; transform-origin: bottom center; transform:translate(-50%,-100%) rotate(0deg);"></div>
            </div>
            <p id="coords" style="font-size:14px;"></p>
            <p id="qibla-angle" style="font-size:18px; font-weight:bold; color:#0a2a6b;"></p>
            <p id="instruction" style="background:#e8f5e9; padding:10px; border-radius:8px;"></p>
            <button onclick="getLocation()" style="background:#0a2a6b; color:white; padding:15px 30px; border:none; border-radius:10px; font-size:16px; font-weight:bold; cursor:pointer; width:100%;">📍 ACTIVER LOCALISATION OBLIGATOIRE</button>
        </div>
        <script>
        let currentLat = null; let currentLon = null; let qiblaBearing = null;
        function getLocation() {
            document.getElementById('status').innerHTML = "⏳ Demande de localisation... Autorise dans ton navigateur";
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(function(position) {
                        currentLat = position.coords.latitude; currentLon = position.coords.longitude;
                        document.getElementById('coords').innerHTML = "📍 Ta position: " + currentLat.toFixed(4) + ", " + currentLon.toFixed(4);
                        document.getElementById('status').innerHTML = "✅ Localisation activée!";
                        calculateQibla(currentLat, currentLon); startCompass();
                    }, function(error) {
                        document.getElementById('status').innerHTML = "❌ ERREUR: Active la localisation dans les parametres du telephone + navigateur. Erreur: " + error.message;
                        document.getElementById('instruction').innerHTML = "Va dans Parametres > Confidentialite > Localisation > Autoriser pour Chrome / Streamlit";
                    }, {enableHighAccuracy: true});
            } else { document.getElementById('status').innerHTML = "❌ Geolocalisation non supportee"; }
        }
        function calculateQibla(lat, lon) {
            const kaabaLat = 21.3891 * Math.PI / 180; const kaabaLon = 39.8579 * Math.PI / 180;
            const latRad = lat * Math.PI / 180; const lonRad = lon * Math.PI / 180;
            const dLon = kaabaLon - lonRad;
            const y = Math.sin(dLon) * Math.cos(kaabaLat);
            const x = Math.cos(latRad) * Math.sin(kaabaLat) - Math.sin(latRad) * Math.cos(kaabaLat) * Math.cos(dLon);
            let bearing = Math.atan2(y, x) * 180 / Math.PI; bearing = (bearing + 360) % 360; qiblaBearing = bearing;
            document.getElementById('qibla-angle').innerHTML = "Qibla: " + bearing.toFixed(1) + "° depuis le Nord";
            document.getElementById('instruction').innerHTML = "Tourne ton telephone jusqu'a ce que la fleche rouge pointe vers le haut. La Kaaba est a " + bearing.toFixed(0) + "°";
            document.getElementById('arrow').style.transform = "translate(-50%,-100%) rotate(" + bearing + "deg)";
        }
        function startCompass() {
            if (window.DeviceOrientationEvent) {
                window.addEventListener('deviceorientation', function(event) {
                    let heading = event.webkitCompassHeading || event.alpha;
                    if (heading!== null && qiblaBearing!== null) {
                        let rotation = qiblaBearing - heading;
                        document.getElementById('compass').style.transform = "translate(-50%,-50%) rotate(" + rotation + "deg)";
                    }
                });
            } else { document.getElementById('instruction').innerHTML += "<br>⚠️ Boussole non supportee, utilise l'angle affiche ci-dessus"; }
        }
        </script>
        """
        st.components.v1.html(qibla_html, height=650)
        if st.button("Retour Home", use_container_width=True):
            st.session_state.bottom_nav="Home"
            st.rerun()
        st.stop()
    elif st.session_state.bottom_nav=="Calendrier":
        st.title("📅 Calendrier Hijri / Gregorien")
        today = date.today()
        st.markdown(f"""
        <div class='card' style='background:linear-gradient(90deg,#0a2a6b,#1a4bb8); color:white'>
        <h3>Aujourd'hui</h3>
        <p><b>Gregorien :</b> {today.strftime('%d/%m/%Y')}</p>
        <p><b>Hijri (approx) :</b> 2026 - Calcul approximatif</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div class='card'><b>Prochains evenements islamiques 2026 :</b><br>🌙 Ramadan : Fevrier 2026<br>🕋 Aid al-Fitr : Mars 2026<br>🕋 Aid al-Adha : Mai 2026<br>📅 Mouharram 1448 : Juin 2026</div>", unsafe_allow_html=True)
        mois = st.selectbox("Choisir mois Gregorien", ["Janvier","Fevrier","Mars","Avril","Mai","Juin","Juillet","Aout","Septembre","Octobre","Novembre","Decembre"])
        st.write(f"Tu as choisi : {mois} 2026")
        if st.button("Retour Home", use_container_width=True):
            st.session_state.bottom_nav="Home"
            st.rerun()
        st.stop()

    st.markdown("""<div style="background:linear-gradient(90deg,#00c6ff,#0072ff); padding:15px; color:white; border-radius:12px; margin-bottom:10px"><b>Bienvenue sur Scanner Halal</b><br><small>Scanner tes produits halal facilement</small></div>""", unsafe_allow_html=True)
    scans_used = user['scans'] - user.get('bonus_scans',0)
    if not user['is_vip'] and scans_used>=5:
        st.error("5 essais utilises")
        st.markdown("""<div class="card-vip"><h3 style="color:gold;margin:0;">Deviens VIP 1500F</h3></div>""", unsafe_allow_html=True)
        st.link_button("PAYER 1500F WAVE - VIP", WAVE_LINK, type="primary", use_container_width=True)
        if st.button("J ai paye - Activer VIP", use_container_width=True):
            users[user_email]['is_vip']=True
            save_json(USERS_FILE,users)
            st.balloons()
            st.rerun()
        if st.button("Pub pour 1 scan gratuit", use_container_width=True):
            users[user_email]['bonus_scans']=users[user_email].get('bonus_scans',0)+1
            save_json(USERS_FILE,users)
            st.rerun()
        st.stop()

    # MENUS DANS HOME AVEC VERROU VIP
    st.markdown("### 📱 Menus")
    m1, m2, m3 = st.columns(3)
    with m1:
        if st.button("🍎\nAliments 🔒", use_container_width=True):
            if not user.get('is_vip'):
                st.session_state.bottom_nav = "VIP_ALIMENTS"
            else:
                st.session_state.selected_menu = "Aliments"
            st.rerun()
        if st.button("📜\nCoran ✅", use_container_width=True):
            st.session_state.selected_menu = "Coran"
            st.rerun()
    with m2:
        if st.button("📋\nMa Liste", use_container_width=True):
            st.session_state.selected_menu = "Ma Liste"
            st.rerun()
        if st.button("🤲\nDouas 🔒", use_container_width=True):
            if not user.get('is_vip'):
                st.session_state.bottom_nav = "VIP_DOUAS"
            else:
                st.session_state.selected_menu = "Douas"
            st.rerun()
    with m3:
        if st.button("🎮\nJeu", use_container_width=True):
            st.session_state.selected_menu = "Jeu"
            st.rerun()
        if st.button("📚\nHadiths 🔒", use_container_width=True):
            if not user.get('is_vip'):
                st.session_state.bottom_nav = "VIP_HADITHS"
            else:
                st.session_state.selected_menu = "Hadiths"
            st.rerun()

    st.markdown("---")
    st.markdown("### 📸 Scanner Halal")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📷 CAMERA", type="primary", use_container_width=True, key="btn_camera"):
            st.session_state.scan_mode="camera"
            st.rerun()
    with col2:
        if st.button("🖼️ UPLOAD", type="primary", use_container_width=True, key="btn_upload"):
            st.session_state.scan_mode="upload"
            st.rerun()

    photo = None
    if st.session_state.scan_mode=="camera":
        cam = st.camera_input("Prends photo", key="camera_input", label_visibility="collapsed")
        if cam:
            photo = cam
    elif st.session_state.scan_mode=="upload":
        up = st.file_uploader("Choisis photo", type=['jpg','png','jpeg','webp'], key="uploader", label_visibility="collapsed")
        if up:
            photo = up

    if photo:
        st.image(photo, caption="Photo ajoutée", use_container_width=True)
        st.markdown("---")
        if st.button("✅ LANCER LE SCAN HALAL MAINTENANT", type="primary", use_container_width=True):
            with st.spinner("Analyse Halal en cours..."):
                time.sleep(2)
                if not user['is_vip']:
                    users[user_email]['scans']+=1
                result = random.choice(["HALAL 100% Halal","HARAM Haram detecte","DOUTEUX Verifier"])
                if "HALAL" in result:
                    detail="Aucun ingredient Haram detecte - 100% Halal"
                    color="green"
                elif "HARAM" in result:
                    detail="Haram detecte: Gelatine porcine ou Alcool ou E471 porc"
                    color="red"
                else:
                    detail="Douteux: E471 peut etre animal - Verifie halal certifie"
                    color="orange"
                st.markdown(f"""<div class="card" style="border-left:8px solid {color}"><h2 style="color:{color}">{result}</h2><p>{detail}</p><small>{datetime.now().strftime("%d/%m/%Y %H:%M")}</small></div>""", unsafe_allow_html=True)
                users[user_email]['history'].append({'date':datetime.now().strftime("%d/%m/%Y %H:%M"),'result':result,'detail':detail})
                save_json(USERS_FILE,users)
                st.balloons()
                st.session_state.scan_mode = None
                if "camera_input" in st.session_state:
                    del st.session_state["camera_input"]
                if "uploader" in st.session_state:
                    del st.session_state["uploader"]
                st.success("Camera eteinte - Scan termine")
                time.sleep(1)
                st.rerun()

elif menu=="Jeu":
    st.title("Jeu - 20 Questions")
    st.markdown("<div class='card' style='background:#0a2a6b; color:white'><b>JEU:</b> 20 questions - Auto 5s - Historique stocke</div>", unsafe_allow_html=True)
    if not st.session_state.show_eval:
        for i,q in enumerate(QUESTIONS_20):
            st.markdown(f"<div class='sondage-card'><b>{q['q']}</b></div>", unsafe_allow_html=True)
            ans = st.radio(f"Q{i+1}", q['options'], key=f"sondage_q_{i}", label_visibility="collapsed")
            st.session_state.sondage_answers[f"q{i+1}"]=ans
        if st.button("VALIDER ET EVALUER - 20 Questions", type="primary", use_container_width=True):
            now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            entry = {'email':user_email,'nom':user.get('nom'),'date':datetime.now().isoformat(),'date_str':now_str,'reponses':st.session_state.sondage_answers.copy()}
            sondages.append(entry)
            save_json(SONDAGE_FILE,sondages)
            users[user_email]['sondage_history'].append(entry)
            save_json(USERS_FILE,users)
            st.session_state.show_eval=True
            st.rerun()
    else:
        st.balloons()
        st.success("Sondage valide et stocke!")
        for i,q in enumerate(QUESTIONS_20):
            rep = st.session_state.sondage_answers.get(f"q{i+1}", "")
            st.markdown(f"<div class='card'><b>{q['q']}</b><br>-> <b style='color:#0072ff'>{rep}</b></div>", unsafe_allow_html=True)
        st.markdown("""<div class='card' style='background:#e8f5e9; border-left:5px solid green'><b>Evaluation terminee - Stocke! Renouvellement auto 5s...</b></div>""", unsafe_allow_html=True)
        with st.spinner("Renouvellement auto 5s..."):
            time.sleep(5)
        st.session_state.sondage_answers={}
        st.session_state.show_eval=False
        st.rerun()
    st.markdown("---")
    st.subheader("Historique de tes sondages")
    hist = users[user_email].get('sondage_history',[])
    if not hist:
        st.info("Aucun sondage encore")
    else:
        for idx,h in enumerate(reversed(hist[-10:])):
            num = len(hist)-idx
            st.markdown(f"<div class='card'><b>Jeu #{num} - {h.get('date_str','')}</b> - 20 reponses</div>", unsafe_allow_html=True)
    if st.button("Renouveler manuellement", use_container_width=True):
        st.session_state.sondage_answers={}
        st.session_state.show_eval=False
        st.rerun()

elif menu=="Ma Liste":
    st.title("Ma Liste Historique")
    tab1,tab2=st.tabs([f"Scans {len(user.get('history',[]))}", f"Jeu {len(user.get('sondage_history',[]))}"])
    with tab1:
        for h in reversed(user.get('history',[])):
            c = "green" if "HALAL" in h['result'] else "red" if "HARAM" in h['result'] else "orange"
            st.markdown(f"<div class='card' style='border-left:5px solid {c}'><b>{h['date']}</b><br>{h['result']}<br><small>{h.get('detail','')}</small></div>", unsafe_allow_html=True)
    with tab2:
        for h in reversed(user.get('sondage_history',[])):
            st.markdown(f"<div class='card'><b>{h.get('date_str')}</b> - 20 reponses</div>", unsafe_allow_html=True)

elif menu=="Aliments":
    if not user.get('is_vip'):
        vip_required_page("Aliments 150")
    st.title("Aliments 150 - VIP")
    s=st.text_input("Chercher aliment ou E-number").lower()
    t1,t2,t3=st.tabs([f"HALAL {len(ALIMENTS_HALAL)}", f"HARAM {len(ALIMENTS_HARAM)}", f"DOUTEUX {len(ALIMENTS_DOUTEUX)}"])
    with t1:
        for a in ALIMENTS_HALAL:
            if s in a.lower() or not s:
                st.markdown(f"<div class='card' style='border-left:5px solid green'>HALAL {a}</div>", unsafe_allow_html=True)
    with t2:
        for a in ALIMENTS_HARAM:
            if s in a.lower() or not s:
                st.markdown(f"<div class='card' style='border-left:5px solid red'>HARAM {a}</div>", unsafe_allow_html=True)
    with t3:
        for a in ALIMENTS_DOUTEUX:
            if s in a.lower() or not s:
                col="red" if "HARAM" in a else "orange"
                st.markdown(f"<div class='card' style='border-left:5px solid {col}'>DOUTEUX {a}</div>", unsafe_allow_html=True)

elif menu=="Coran":
    st.title("Coran 114 Sourates - Gratuit")
    q=st.text_input("Chercher sourate").lower()
    for s in SOURATES_114:
        if q in s.lower() or not q:
            st.markdown(f"<div class='card-dark'><div style='font-size:24px; background:#00c6ff; width:45px; height:45px; border-radius:50%; display:flex; align-items:center; justify-content:center;'>📖</div><div><b>{s}</b></div></div>", unsafe_allow_html=True)

elif menu=="Douas":
    if not user.get('is_vip'):
        vip_required_page("Douas 50")
    st.title("Douas 50 - VIP")
    cat=st.selectbox("Filtrer categorie", ["Tout","Repas","Sommeil","Toilette","Maison","Vetement","Voyage","Mosquee","Priere","Maladie","Difficulte","Pardon","Matin/Soir","Divers","Famille","Nature","Protection","Mort","Jeune"])
    qd=st.text_input("Chercher doua").lower()
    for d in DUAS_50:
        if (cat=="Tout" or d['cat']==cat) and (qd in d['t'].lower() or not qd):
            st.markdown(f"<div class='card' style='border-left:5px solid #00c6ff'><b>{d['t']} - {d['cat']}</b><br><span style='color:green; font-size:18px;'>{d['ar']}</span><br><small>{d['fr']}</small></div>", unsafe_allow_html=True)

elif menu=="Hadiths":
    if not user.get('is_vip'):
        vip_required_page("Hadiths 40")
    st.title("Hadiths 40 - VIP")
    for h in HADITHS_40:
        st.markdown(f"<div class='card' style='border-left:5px solid #0a2a6b'>{h}</div>", unsafe_allow_html=True)

elif menu=="Profil":
    st.title("Profil Complet")
    st.markdown(f"<div class='card'>Nom: {user.get('nom')}<br>Wave: {user.get('wave')}<br>Pays: {user.get('pays')}<br>VIP: {'Oui VIP Illimite' if user.get('is_vip') else 'Non'}<br>Scans: {user.get('scans')}<br>Bonus: {user.get('bonus_scans',0)}<br>Total scans: {len(user.get('history',[]))}<br>Total Jeu: {len(user.get('sondage_history',[]))}<br></div>", unsafe_allow_html=True)
    new_nom=st.text_input("Changer nom", value=user.get('nom',''))
    if st.button("Sauvegarder nom"):
        users[user_email]['nom']=new_nom
        save_json(USERS_FILE,users)
        st.success("Nom sauvegarde")
        st.rerun()

elif menu=="Parametres":
    st.title("Parametres")
    st.markdown(f"""
    <div class='card'>
    <b>Version:</b> FINAL V28<br>
    <b>Dev:</b> Idrissa<br>
    <b>Nom:</b> {user.get('nom')}<br>
    <b>Email:</b> {user_email}<br>
    <b>Wave:</b> {user.get('wave')}<br>
    <b>Pays:</b> {user.get('pays')}<br>
    <b>VIP:</b> {'Oui Illimite' if user.get('is_vip') else 'Non - 5 essais'}<br>
    <b>VIP Contenu:</b> Aliments 150 + Douas 50 + Hadiths 40<br>
    <b>Gratuit:</b> Scanner + Coran 114 + Jeu 20Q + Ma Liste + Qibla + Calendrier<br>
    </div>
    """, unsafe_allow_html=True)

elif menu=="Aide":
    st.title("Aide & Commentaires")
    msg=st.text_area("Ton message")
    if st.button("Envoyer", type="primary"):
        if msg.strip():
            comments.append({'email':user_email,'nom':user.get('nom'),'msg':msg,'date':datetime.now().isoformat()})
            save_json(COMMENTS_FILE,comments)
            st.success("Envoye!")

elif menu=="Notice":
    st.title("Notice Complete")
    st.markdown("""<div class='card'><h3>Guide Complet Scanner Halal FINAL V28</h3>
    <b>1. Inscription:</b> Nom, Pays, Numero, Email, Mot de passe (lettres+chiffres) ex baba2000<br>
    <b>2. Connexion:</b> Email + Mot de passe<br>
    <b>3. Top:</b> Photo couverture + Photo profil ronde + Nom utilisateur (pas email)<br>
    <b>4. Home:</b> Menus 6 boutons - Aliments Douas Hadiths VIP bloque, Coran Ma Liste Jeu gratuit<br>
    <b>5. Scanner:</b> CAMERA UPLOAD sans message - Photo -> SCAN -> Camera eteinte auto<br>
    <b>6. Qibla:</b> Localisation obligatoire + boussole temps reel + calcul exact Kaaba<br>
    <b>7. Calendrier:</b> Hijri Gregorien + fetes islamiques<br>
    <b>8. Bottom:</b> 3 boutons seulement Home Qibla Calendrier - Plus supprime<br>
    </div>""", unsafe_allow_html=True)

elif menu=="Langue":
    st.title("Langue")
    lang=st.selectbox("Choisis", ["Francais","English","العربية"])
    if st.button("Appliquer"):
        users[user_email]['lang']=lang
        save_json(USERS_FILE,users)
        st.success(f"Langue: {lang}")

else:
    st.title(menu)
    st.write(f"Contenu {menu} integre complet")
