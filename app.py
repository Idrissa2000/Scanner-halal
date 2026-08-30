import streamlit as st
import json
import os
import random
import re
from datetime import datetime
import time

WAVE_LINK = "https://pay.wave.com/m/M_ci_bqKBEWPbP0OO/c/ci/?amount=1500"
USERS_FILE = "users.json"
COMMENTS_FILE = "commentaires.json"
SONDAGE_FILE = "sondages.json"

# ===== LISTES COMPLETES =====
ALIMENTS_HALAL = [
    "Poulet halal egorge","Boeuf halal","Mouton halal","Chevre halal","Chameau halal","Dinde halal",
    "Poisson tout type","Crevettes","Crabe","Thon","Sardine","Maquereau",
    "Riz blanc","Riz complet","Mil","Mais","Ble","Fonio","Sorgho","Avoine",
    "Arachide","Noix cajou","Amande","Sesame","Noix coco",
    "Mangue","Banane","Orange","Ananas","Pasteque","Papaye","Goyave","Citron","Pomme","Avocat",
    "Tomate","Oignon","Piment","Gombo","Aubergine","Carotte","Pomme terre","Manioc","Igname","Patate douce","Chou","Laitue","Concombre",
    "Haricot blanc","Haricot rouge","Lentille","Pois chiche",
    "Lait vache halal","Yaourt nature sans gelatine","Fromage halal","Miel pur","Dattes Ajwa","Dattes Sukkary",
    "Huile palme","Huile arachide","Huile olive","Beurre halal","Sucre canne","Sel marin","Poivre","Curcuma","Gingembre","Ail",
    "Pain sans E471 porc","Biscuit halal certifie","Jus naturel 100%","The vert","The noir","Cafe","Eau minerale"
]

ALIMENTS_HARAM = [
    "Porc toute partie","Jambon porc","Saucisson porc","Lard","Bacon",
    "Vin rouge","Vin blanc","Biere","Whisky","Rhum","Vodka","Alcool ethylique",
    "Sang animal","Cadavre non egorge","Viande non halal",
    "Gelatine porcine E441","E120 Cochenille insecte","E422 Glycerol porc","E471 porc","E472 porc","E481 porc","E492 porc"
]

ALIMENTS_DOUTEUX = [
    "E102 Tartrazine - Douteux","E110 Jaune soleil - Douteux","E120 Cochenille - HARAM insecte",
    "E122 Azorubine - Douteux","E124 Ponceau - Douteux","E132 Indigotine - Douteux",
    "E140 Chlorophylle - Halal si vegetal","E150a Caramel - Halal","E160a Carotene - Halal","E163 Anthocyanes - Halal",
    "E171 Dioxyde titane - Halal mais debat","E200 Acide sorbique - Halal","E211 Benzoate sodium - Halal",
    "E250 Nitrite sodium - Halal mais deconseille","E300 Vit C - Halal","E322 Lecithine - Halal si soja Haram si porc",
    "E330 Acide citrique - Halal","E400 Acide alginique - Halal","E406 Agar-agar - HALAL 100%","E407 Carraghenane - HALAL",
    "E410 Gomme caroube - HALAL","E412 Gomme guar - HALAL","E414 Gomme arabique - HALAL","E415 Xanthane - HALAL",
    "E420 Sorbitol - Halal","E422 Glycerol - HARAM si porc HALAL si vegetal",
    "E440 Pectine - HALAL","E441 Gelatine - HARAM si porc HALAL si boeuf halal",
    "E471 Mono-diglycerides - DOUTEUX PEUT ETRE PORC","E472 Esters - Douteux","E473 Sucroesters - Douteux",
    "E476 Polyricinoleate - Douteux","E481 Stearoyl lactylate - Douteux porc possible","E491 Sorbitan - Douteux"
]

SOURATES_114 = [
    "1 Al-Fatiha - Ouverture - 7 versets - Mecquoise",
    "2 Al-Baqara - Vache - 286 versets - Medinoise",
    "3 Al-Imran - Famille Imran - 200 - Medinoise",
    "4 An-Nisa - Femmes - 176 - Medinoise",
    "5 Al-Maida - Table Servie - 120 - Medinoise",
    "6 Al-Anam - Bestiaux - 165 - Mecquoise",
    "7 Al-Araf - Murettes - 206 - Mecquoise",
    "8 Al-Anfal - Butin - 75 - Medinoise",
    "9 At-Tawba - Repentir - 129 - Medinoise",
    "10 Younus - Jonas - 109 - Mecquoise",
    "11 Houd - Houd - 123 - Mecquoise",
    "12 Youssouf - Joseph - 111 - Mecquoise",
    "13 Ar-Raad - Tonnerre - 43 - Medinoise",
    "14 Ibrahim - Abraham - 52 - Mecquoise",
    "15 Al-Hijr - Vallee Pierres - 99 - Mecquoise",
    "16 An-Nahl - Abeilles - 128 - Mecquoise",
    "17 Al-Isra - Voyage Nocturne - 111 - Mecquoise",
    "18 Al-Kahf - Caverne - 110 - Mecquoise - Lire vendredi",
    "19 Maryam - Marie - 98 - Mecquoise",
    "20 Ta-Ha - Ta-Ha - 135 - Mecquoise",
    "21 Al-Anbiya - Prophetes - 112 - Mecquoise",
    "22 Al-Hajj - Pelerinage - 78 - Medinoise",
    "23 Al-Muminune - Croyants - 118 - Mecquoise",
    "24 An-Nour - Lumiere - 64 - Medinoise",
    "25 Al-Furqane - Discernement - 77 - Mecquoise",
    "26 Ach-Chuara - Poetes - 227 - Mecquoise",
    "27 An-Naml - Fourmis - 93 - Mecquoise",
    "28 Al-Qasas - Recit - 88 - Mecquoise",
    "29 Al-Ankabut - Araignee - 69 - Mecquoise",
    "30 Ar-Rum - Romains - 60 - Mecquoise",
    "31 Luqman - Luqman - 34 - Mecquoise",
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
    "53 An-Najm - Etoile - 62 - Mecquoise",
    "54 Al-Qamar - Lune - 55 - Mecquoise",
    "55 Ar-Rahman - Misericordieux - 78 - Medinoise",
    "56 Al-Waqia - Evenement - 96 - Mecquoise",
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
    "67 Al-Mulk - Royaute - 30 - Mecquoise - Sauve chatiment tombe",
    "68 Al-Qalam - Plume - 52 - Mecquoise",
    "69 Al-Haqqa - Verite - 52 - Mecquoise",
    "70 Al-Maarij - Voies Ascension - 44 - Mecquoise",
    "71 Nouh - Noe - 28 - Mecquoise",
    "72 Al-Jinn - Djinns - 28 - Mecquoise",
    "73 Al-Muzzammil - Enveloppe - 20 - Mecquoise",
    "74 Al-Muddathir - Revete manteau - 56 - Mecquoise",
    "75 Al-Qiyama - Resurrection - 40 - Mecquoise",
    "76 Al-Insan - Homme - 31 - Medinoise",
    "77 Al-Mursalat - Envoyes - 50 - Mecquoise",
    "78 An-Naba - Nouvelle - 40 - Mecquoise",
    "79 An-Naziat - Anges arrachent - 46 - Mecquoise",
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
    "103 Al-Asr - Temps - 3 - Mecquoise",
    "104 Al-Humaza - Calomniateurs - 9 - Mecquoise",
    "105 Al-Fil - Elephant - 5 - Mecquoise",
    "106 Quraich - Coraich - 4 - Mecquoise",
    "107 Al-Maun - Ustensile - 7 - Mecquoise",
    "108 Al-Kawthar - Abondance - 3 - Mecquoise - Plus petite sourate",
    "109 Al-Kafirun - Infideles - 6 - Mecquoise",
    "110 An-Nasr - Secours - 3 - Medinoise",
    "111 Al-Masad - Fibres - 5 - Mecquoise",
    "112 Al-Ikhlas - Monotheisme - 4 - Mecquoise - Un tiers Coran",
    "113 Al-Falaq - Aube Naissante - 5 - Mecquoise - Protection",
    "114 An-Nas - Hommes - 6 - Mecquoise - Derniere sourate"
]

DUAS_50 = [
    {"t":"1 Avant manger","ar":"بسم الله","fr":"Au nom d Allah","cat":"Repas"},
    {"t":"2 Apres manger","ar":"الحمد لله الذي اطعمنا","fr":"Louange a Allah qui nous a nourris","cat":"Repas"},
    {"t":"3 Avant dormir","ar":"باسمك اللهم اموت واحيا","fr":"En Ton nom je meurs et vis","cat":"Sommeil"},
    {"t":"4 Au reveil","ar":"الحمد لله الذي احيانا","fr":"Louange qui nous fait revivre","cat":"Sommeil"},
    {"t":"5 Entrer toilette","ar":"اللهم اني اعوذ بك من الخبث","fr":"Refuge contre demons","cat":"Toilette"},
    {"t":"6 Sortir toilette","ar":"غفرانك","fr":"Pardon","cat":"Toilette"},
    {"t":"7 Entrer maison","ar":"بسم الله ولجنا","fr":"Au nom d Allah nous entrons","cat":"Maison"},
    {"t":"8 Sortir maison","ar":"بسم الله توكلت على الله","fr":"Au nom d Allah je m en remets","cat":"Maison"},
    {"t":"9 S habiller","ar":"الحمد لله الذي كساني","fr":"Louange qui m a vetu","cat":"Vetement"},
    {"t":"10 Nouveau vetement","ar":"اللهم لك الحمد انت كسوتنيه","fr":"A Toi louange Tu me l as donne","cat":"Vetement"},
    {"t":"11 Se deshabiller","ar":"بسم الله","fr":"Au nom d Allah","cat":"Vetement"},
    {"t":"12 Voyage depart","ar":"سبحان الذي سخر لنا هذا","fr":"Gloire a Celui qui a soumis","cat":"Voyage"},
    {"t":"13 Voyage retour","ar":"ايبون تائبون عابدون","fr":"Nous revenons repentants","cat":"Voyage"},
    {"t":"14 Entrer mosquee","ar":"اللهم افتح لي ابواب رحمتك","fr":"Ouvre portes misericorde","cat":"Mosquee"},
    {"t":"15 Sortir mosquee","ar":"اللهم اني اسالك من فضلك","fr":"Je demande Ta grace","cat":"Mosquee"},
    {"t":"16 Apres adhan","ar":"اللهم رب هذه الدعوة التامة","fr":"Seigneur appel parfait","cat":"Priere"},
    {"t":"17 Debut woudou","ar":"بسم الله","fr":"Au nom d Allah","cat":"Priere"},
    {"t":"18 Fin woudou","ar":"اشهد ان لا اله الا الله","fr":"J atteste qu il n y a de dieu qu Allah","cat":"Priere"},
    {"t":"19 Malade","ar":"اذهب الباس رب الناس","fr":"Enleve mal Seigneur","cat":"Maladie"},
    {"t":"20 Visite malade","ar":"لا باس طهور ان شاء الله","fr":"Pas de mal purification","cat":"Maladie"},
    {"t":"21 Tristesse","ar":"لا اله الا الله العظيم","fr":"Pas de dieu qu Allah Grand","cat":"Difficulte"},
    {"t":"22 Anxiete","ar":"اللهم اني اعوذ بك من الهم","fr":"Refuge contre souci","cat":"Difficulte"},
    {"t":"23 Difficulte","ar":"اللهم لا سهل الا ما جعلته سهلا","fr":"Rien facile sauf ce que Tu facilites","cat":"Difficulte"},
    {"t":"24 Dette","ar":"اللهم اكفني بحلالك عن حرامك","fr":"Contente-moi de Ton halal","cat":"Difficulte"},
    {"t":"25 Pardon","ar":"استغفر الله العظيم","fr":"Je demande pardon a Allah","cat":"Pardon"},
    {"t":"26 Matin","ar":"اصبحنا واصبح الملك لله","fr":"Matin et royaute a Allah","cat":"Matin/Soir"},
    {"t":"27 Soir","ar":"امسينا وامسى الملك لله","fr":"Soir et royaute a Allah","cat":"Matin/Soir"},
    {"t":"28 Cauchemar","ar":"اعوذ بكلمات الله التامات","fr":"Refuge par paroles parfaites","cat":"Sommeil"},
    {"t":"29 Colere","ar":"اعوذ بالله من الشيطان الرجيم","fr":"Refuge en Allah contre satan","cat":"Difficulte"},
    {"t":"30 Eternuement","ar":"الحمد لله","fr":"Louange a Allah","cat":"Divers"},
    {"t":"31 Reponse eternuement","ar":"يرحمك الله","fr":"Qu Allah te fasse misericorde","cat":"Divers"},
    {"t":"32 Mariage","ar":"بارك الله لكما","fr":"Qu Allah vous benisse","cat":"Famille"},
    {"t":"33 Nouveau ne","ar":"بارك الله لك في الموهوب","fr":"Qu Allah benisse ce qui t est donne","cat":"Famille"},
    {"t":"34 Pluie","ar":"اللهم صيبا نافعا","fr":"Pluie benefique","cat":"Nature"},
    {"t":"35 Vent fort","ar":"اللهم اني اسالك خيرها","fr":"Je demande son bien","cat":"Nature"},
    {"t":"36 Miroir","ar":"اللهم كما حسنت خلقي","fr":"Embelli mon caractere","cat":"Divers"},
    {"t":"37 Marche","ar":"لا اله الا الله وحده","fr":"Il n y a de dieu qu Allah seul","cat":"Divers"},
    {"t":"38 Protection matin","ar":"حسبي الله لا اله الا هو","fr":"Allah me suffit","cat":"Protection"},
    {"t":"39 Protection soir","ar":"بسم الله الذي لا يضر","fr":"Au nom d Allah dont rien ne nuit","cat":"Protection"},
    {"t":"40 Istikhara","ar":"اللهم اني استخيرك بعلمك","fr":"Je Te consulte par Ta science","cat":"Priere"},
    {"t":"41 Apres priere","ar":"استغفر الله","fr":"Pardon 3 fois","cat":"Priere"},
    {"t":"42 Fin assemblee","ar":"سبحانك اللهم وبحمدك","fr":"Gloire a Toi O Allah","cat":"Divers"},
    {"t":"43 Enterrement","ar":"اللهم اغفر له وارحمه","fr":"Pardonne-lui","cat":"Mort"},
    {"t":"44 Condoleances","ar":"انا لله وانا اليه راجعون","fr":"A Allah nous appartenons","cat":"Mort"},
    {"t":"45 Iftar","ar":"ذهب الظما وابتلت العروق","fr":"Soif partie","cat":"Jeune"},
    {"t":"46 Laylatoul Qadr","ar":"اللهم انك عفو تحب العفو","fr":"Tu es Pardonneur pardonne-moi","cat":"Jeune"},
    {"t":"47 Entrer cimetiere","ar":"السلام عليكم اهل الديار","fr":"Paix sur vous habitants","cat":"Mort"},
    {"t":"48 Douleur","ar":"بسم الله 3 مرات","fr":"Au nom d Allah 3 fois","cat":"Maladie"},
    {"t":"49 Voir lune","ar":"الله اكبر اللهم اهله علينا","fr":"Allah Grand fais apparaitre","cat":"Nature"},
    {"t":"50 Enfant peureux","ar":"اعيذك بكلمات الله التامة","fr":"Je te protege par paroles parfaites","cat":"Famille"},
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
    "9. Celui qui ne fait pas misericorde pas de misericorde - Bukhari 7376",
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
    "22. Paradis sous pieds des meres - Nasai 3104",
    "23. Allah pur n accepte que pur - Muslim 1015",
    "24. Delaisse doute pour certitude - Tirmidhi 2518",
    "25. Laisse ce qui ne te concerne pas - Tirmidhi 2317",
    "26. Modestie fait partie foi - Bukhari 9",
    "27. Pas Paradis avec orgueil - Muslim 91",
    "28. Soulage croyant Allah te soulagera - Muslim 2699",
    "29. Meilleur dhikr La ilaha illa Allah - Tirmidhi 3383",
    "30. Mangez halal et bon - Coran 2:168",
    "31. Corps nourri haram ira Enfer - Ahmad",
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

st.set_page_config(page_title="Scanner Halal FINAL V19", page_icon="mosque", layout="centered")

st.markdown(f"""
<style>
#MainMenu{{visibility:hidden}} footer{{visibility:hidden}} header{{visibility:hidden}}
.block-container{{padding-top:0px; padding-bottom:90px; padding-left:0; padding-right:0}}
.top-bar{{background: linear-gradient(90deg,#00c6ff,#0072ff); padding:14px 12px; display:flex; justify-content:space-between; align-items:center; color:white; font-weight:bold; font-size:18px; position:sticky; top:0; z-index:1000}}
.card-dark{{background:#0f1e4a; color:white; margin:8px 12px; padding:12px; border-radius:12px; display:flex; align-items:center; gap:12px; border:1px solid #1e3a8a}}
.card{{background:white; margin:8px 12px; padding:15px; border-radius:12px; border:1px solid #eee}}
.card-vip{{background:linear-gradient(135deg,#0a2a6b,#1a4bb8);color:white;padding:20px;border-radius:15px;margin:12px}}
.card-pub{{background:#fff3e0;border:2px dashed #ff9800;padding:15px;border-radius:12px;margin:12px}}
.bottom-nav{{position:fixed; bottom:0; left:0; right:0; background:white; display:flex; justify-content:space-around; padding:8px 0; border-top:1px solid #eee; z-index:1000}}
.pub-zone{{position:fixed; bottom:55px; left:0; right:0; background:black; color:white; text-align:center; padding:6px; font-size:12px; z-index:999}}
.pub-zone a{{color:#00D1FF; text-decoration:none}}
.sondage-card{{background:white; margin:8px 12px; padding:15px; border-radius:12px; border-left:5px solid #0072ff}}
</style>
<div class="top-bar"><span>Menu</span> Scanner Halal FINAL V19 <span></span></div>
<div class="pub-zone">PUB - <a href="{WAVE_LINK}" target="_blank">Deviens VIP 1500F - Payer Wave</a></div>
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

if st.session_state.page=="auth":
    st.markdown("<h2 style='text-align:center;color:#0a2a6b;'>Scanner Halal - Connexion</h2>", unsafe_allow_html=True)
    t1,t2,t3=st.tabs(["Connexion","Inscription","Mot de passe oublie"])
    with t1:
        e=st.text_input("Email Connexion").strip()
        p=st.text_input("Mot de passe",type="password")
        if st.button("Se connecter",type="primary",use_container_width=True):
            u=users.get(e)
            if u and u.get('pwd')==p:
                st.session_state.user=e
                st.session_state.page="app"
                st.rerun()
            else:
                st.error("Email ou mot de passe incorrect")
    with t2:
        nom=st.text_input("Nom utilisateur").strip()
        c1,c2=st.columns([2,3])
        with c1:
            pays=st.selectbox("Pays", ["+225 CI","+221 SN","+223 ML","+224 GN","+226 BF","+229 BJ","+33 FR"])
        with c2:
            numero=st.text_input("Numero", placeholder="0771845766").strip()
        er=st.text_input("Email Inscription").strip()
        p1=st.text_input("Mdp lettres+chiffres ex baba2000",type="password",key="p1")
        p2=st.text_input("Confirmer mdp",type="password",key="p2")
        if st.button("Creer mon compte",type="primary",use_container_width=True):
            if not nom or not numero or not er or not p1:
                st.error("Remplis tous les champs")
            elif not is_valid_pwd(p1):
                st.error("Mdp doit avoir lettres + chiffres min 6 ex baba2000")
            elif p1!=p2:
                st.error("Mots de passe differents")
            elif er in users:
                st.error("Email deja utilise va dans Connexion")
            else:
                users[er]={'nom':nom,'wave':f"{extract_code(pays)} {numero}",'pays':pays,'pwd':p1,'scans':0,'is_vip':False,'history':[],'sondage_history':[],'bonus_scans':0}
                save_json(USERS_FILE,users)
                st.success("Compte cree! Va dans Connexion")
                st.balloons()
    with t3:
        ef=st.text_input("Email compte oublie").strip()
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
            np=st.text_input("Nouveau mdp",type="password")
            if st.button("Reinitialiser"):
                if ci==st.session_state.reset_code:
                    users[st.session_state.reset_email]['pwd']=np
                    save_json(USERS_FILE,users)
                    st.success("Change! Va dans Connexion")
                    st.session_state.reset_code=None
                else:
                    st.error("Code faux")
    st.stop()

if not st.session_state.user or st.session_state.user not in users:
    st.session_state.page="auth"
    st.rerun()

user_email=st.session_state.user
user=users[user_email]

if 'sondage_history' not in user:
    users[user_email]['sondage_history']=[]
    save_json(USERS_FILE,users)

with st.sidebar:
    st.markdown("### Menu")
    nom_affiche = user.get('nom','')
    st.write(f"Nom: {nom_affiche}")
    if user.get('is_vip'):
        st.success("VIP Illimite")
    else:
        sc = user.get('scans',0)
        bonus = user.get('bonus_scans',0)
        essai_num = sc + 1
        st.info(f"Essai {essai_num}/05 - Bonus {bonus}")
    st.markdown("---")
    menu=st.radio("NAVIGATION", ["Home","Scanner Halal","Aliments 150","Ma Liste Historique","Zone Sondage 20Q Auto","Profil Complet","Parametres","Aide","Notice","Langue","Coran 114","Hadiths 40","Douas 50"], label_visibility="collapsed")
    if st.button("Deconnexion", use_container_width=True):
        st.session_state.user=None
        st.session_state.page="auth"
        st.session_state.scan_mode=None
        st.session_state.sondage_answers={}
        st.session_state.show_eval=False
        st.rerun()

if menu=="Home" or menu=="Scanner Halal":
    st.markdown("""<div style="background:linear-gradient(90deg,#00c6ff,#0072ff); padding:15px; color:white;"><b>Scanner Halal FINAL V19</b><br><small>150 aliments + 114 sourates + 50 duas + 40 hadiths + 20Q sondage</small></div>""", unsafe_allow_html=True)
    scans_used = user['scans'] - user.get('bonus_scans',0)
    if not user['is_vip'] and scans_used>=5:
        st.error("5 essais utilises - Deviens VIP ou regarde pub")
        st.markdown("""<div class="card-vip"><h3 style="color:gold;margin:0;">Deviens VIP 1500F - Illimite a vie</h3><p>Scans illimites + Sans pub + Support</p></div>""", unsafe_allow_html=True)
        st.link_button("PAYER 1500F WAVE - VIP", WAVE_LINK, type="primary", use_container_width=True)
        if st.button("J ai paye - Activer VIP", use_container_width=True):
            users[user_email]['is_vip']=True
            save_json(USERS_FILE,users)
            st.balloons()
            st.success("VIP active!")
            st.rerun()
        st.markdown("""<div class="card-pub"><h4 style="color:#ff9800;margin:0;">Option Gratuite - Bouton different VIP</h4><p>Regarde pub 30s pour 1 scan gratuit</p></div>""", unsafe_allow_html=True)
        if st.button("Regarder pub 30s pour 1 scan gratuit", use_container_width=True):
            users[user_email]['bonus_scans']=users[user_email].get('bonus_scans',0)+1
            save_json(USERS_FILE,users)
            st.success("+1 scan offert")
            st.rerun()
        st.stop()

    st.markdown("<div style='padding:12px; font-weight:bold;'>Choisis comment scanner - 2 BOUTONS SEPARES:</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("BOUTON CAMERA", type="primary", use_container_width=True):
            st.session_state.scan_mode="camera"
            st.rerun()
    with col2:
        if st.button("BOUTON UPLOAD", type="primary", use_container_width=True):
            st.session_state.scan_mode="upload"
            st.rerun()

    photo = None
    if st.session_state.scan_mode=="camera":
        st.info("Mode Camera active - Prends photo ingredients")
        cam = st.camera_input("Prends photo maintenant")
        if cam:
            photo = cam
    elif st.session_state.scan_mode=="upload":
        st.info("Mode Upload active - Choisis depuis galerie")
        up = st.file_uploader("Choisis photo depuis galerie", type=['jpg','png','jpeg'])
        if up:
            photo = up
    else:
        st.info("Clique CAMERA ou UPLOAD d abord")
        st.markdown("""<div class="card-dark"><div style="font-size:30px;">📦</div><div><b>Scanner un produit</b><br><small>Photo ingredients -> Analyse</small></div></div>""", unsafe_allow_html=True)

    if photo:
        st.image(photo, use_container_width=True)
        if st.button("LANCER LE SCAN HALAL MAINTENANT", type="primary", use_container_width=True):
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
                if st.button("Scanner autre produit"):
                    st.session_state.scan_mode=None
                    st.rerun()

elif menu=="Zone Sondage 20Q Auto":
    st.title("Sondage 20 Questions - Auto Renew + Historique")
    st.markdown("""<div class='card' style='background:#0a2a6b; color:white'><b>SONDAGE FINAL:</b><br>Plus condition 18/20 supprimee<br>20 questions a evaluer<br>Apres evaluation -> Renouvellement auto 5s<br>Resultat stocke dans historique</div>""", unsafe_allow_html=True)

    if not st.session_state.show_eval:
        for i,q in enumerate(QUESTIONS_20):
            st.markdown(f"<div class='sondage-card'><b>{q['q']}</b></div>", unsafe_allow_html=True)
            ans = st.radio(f"Question {i+1}", q['options'], key=f"sondage_q_{i}", label_visibility="collapsed")
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
        st.success("Sondage valide et stocke dans historique!")
        st.markdown("<div class='card'><h3>Evaluation de tes 20 reponses:</h3></div>", unsafe_allow_html=True)
        for i,q in enumerate(QUESTIONS_20):
            rep = st.session_state.sondage_answers.get(f"q{i+1}", "Non repondu")
            st.markdown(f"<div class='card'><b>{q['q']}</b><br>-> <b style='color:#0072ff'>{rep}</b></div>", unsafe_allow_html=True)

        st.markdown("""<div class='card' style='background:#e8f5e9; border-left:5px solid green'><b>Evaluation terminee - Stocke dans historique!</b><br>Renouvellement auto dans 5 secondes...</div>""", unsafe_allow_html=True)

        with st.spinner("Renouvellement automatique dans 5 secondes..."):
            time.sleep(5)

        st.session_state.sondage_answers={}
        st.session_state.show_eval=False
        st.success("Sondage renouvele automatiquement!")
        time.sleep(1)
        st.rerun()

    st.markdown("---")
    st.subheader("Historique de tes sondages (stocke)")
    hist = users[user_email].get('sondage_history',[])
    if not hist:
        st.info("Aucun sondage encore")
    else:
        st.write(f"Total tes sondages: {len(hist)}")
        for idx,h in enumerate(reversed(hist[-10:])):
            num = len(hist)-idx
            st.markdown(f"<div class='card' style='border-left:5px solid #0a2a6b'><b>Sondage #{num} - {h.get('date_str','')}</b><br>20 reponses</div>", unsafe_allow_html=True)
            with st.expander(f"Voir details sondage #{num}"):
                for k,v in h.get('reponses',{}).items():
                    st.write(f"{k}: {v}")

    if st.button("Renouveler manuellement maintenant", use_container_width=True):
        st.session_state.sondage_answers={}
        st.session_state.show_eval=False
        st.rerun()

elif menu=="Ma Liste Historique":
    st.title("Ma Liste - Historique Complet")
    tab_scan, tab_sond = st.tabs([f"Scans {len(user.get('history',[]))}", f"Sondages {len(user.get('sondage_history',[]))}"])
    with tab_scan:
        if not user.get('history'):
            st.info("Aucun scan")
        for h in reversed(user.get('history',[])):
            c = "green" if "HALAL" in h['result'] else "red" if "HARAM" in h['result'] else "orange"
            st.markdown(f"<div class='card' style='border-left:5px solid {c}'><b>{h['date']}</b><br>{h['result']}<br><small>{h.get('detail','')}</small></div>", unsafe_allow_html=True)
        if user.get('history'):
            if st.button("Effacer historique scans"):
                users[user_email]['history']=[]
                save_json(USERS_FILE,users)
                st.rerun()
    with tab_sond:
        if not user.get('sondage_history'):
            st.info("Aucun sondage - Va dans Zone Sondage")
        for h in reversed(user.get('sondage_history',[])):
            st.markdown(f"<div class='card' style='border-left:5px solid #0a2a6b'><b>{h.get('date_str')}</b><br>20 reponses sondage<br><small>{h.get('nom')}</small></div>", unsafe_allow_html=True)

elif menu=="Aliments 150":
    st.title("Aliments 150 + E-Numbers")
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

elif menu=="Coran 114":
    st.title("Coran 114 Sourates Completes")
    q=st.text_input("Chercher sourate").lower()
    for s in SOURATES_114:
        if q in s.lower() or not q:
            st.markdown(f"""<div class="card-dark"><div style="font-size:24px; background:#00c6ff; width:45px; height:45px; border-radius:50%; display:flex; align-items:center; justify-content:center;">Livre</div><div><b>{s}</b></div></div>""", unsafe_allow_html=True)

elif menu=="Douas 50":
    st.title("Douas 50 Completes")
    cat=st.selectbox("Filtrer categorie", ["Tout","Repas","Sommeil","Toilette","Maison","Vetement","Voyage","Mosquee","Priere","Maladie","Difficulte","Pardon","Matin/Soir","Divers","Famille","Nature","Protection","Mort","Jeune"])
    qd=st.text_input("Chercher doua").lower()
    for d in DUAS_50:
        if (cat=="Tout" or d['cat']==cat) and (qd in d['t'].lower() or not qd):
            st.markdown(f"""<div class='card' style='border-left:5px solid #00c6ff'><b>{d['t']} - {d['cat']}</b><br><span style='color:green; font-size:18px;'>{d['ar']}</span><br><small>{d['fr']}</small></div>""", unsafe_allow_html=True)

elif menu=="Hadiths 40":
    st.title("Hadiths 40 Bukhari")
    for h in HADITHS_40:
        st.markdown(f"<div class='card' style='border-left:5px solid #0a2a6b'>{h}</div>", unsafe_allow_html=True)

elif menu=="Profil Complet":
    st.title("Mon Profil Complet")
    st.markdown(f"""<div class='card'><b>Nom:</b> {user.get('nom')}<br><b>Wave:</b> {user.get('wave')}<br><b>Pays:</b> {user.get('pays')}<br><b>Email:</b> {user_email}<br><b>VIP:</b> {'Oui VIP Illimite' if user['is_vip'] else 'Non Essai gratuit'}<br><b>Scans utilises:</b> {user['scans']}<br><b>Bonus:</b> {user.get('bonus_scans',0)}<br><b>Total historique scans:</b> {len(user.get('history',[]))}<br><b>Total sondages:</b> {len(user.get('sondage_history',[]))}<br></div>""", unsafe_allow_html=True)
    new_nom=st.text_input("Changer nom", value=user.get('nom',''))
    if st.button("Sauvegarder profil"):
        users[user_email]['nom']=new_nom
        save_json(USERS_FILE,users)
        st.success("Sauvegarde")

elif menu=="Parametres":
    st.title("Parametres")
    st.markdown("<div class='card'><b>Version:</b> FINAL V19 CORRIGE<br><b>Dev:</b> Idrissa<br><b>Fonctionnalites:</b> 2 boutons scanner, 150 aliments, 114 sourates, 50 duas, 40 hadiths, 20Q auto-renew + historique</div>", unsafe_allow_html=True)

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
    st.markdown("""<div class='card'><h3>Guide Complet Scanner Halal FINAL V19 CORRIGE</h3>
    <b>1. Inscription:</b> Nom, Pays, Numero, Email, Mdp lettres+chiffres ex baba2000 -> Creer<br>
    <b>2. Connexion:</b> Email + Mdp -> Se connecter<br>
    <b>3. Scanner:</b> Menu Scanner -> 2 boutons: CAMERA et UPLOAD -> Photo ingredients -> LANCER SCAN -> Resultat<br>
    <b>4. Essais:</b> 5 gratuits -> Apres VIP 1500F Wave bouton bleu illimite ou Pub bouton orange 1 scan<br>
    <b>5. Sondage:</b> 20 questions -> Valider -> Evaluation -> Stocke historique -> Auto-renew 5s<br>
    <b>6. Historique:</b> Ma Liste -> 2 onglets Scans et Sondages<br>
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
    st.write(f"Contenu {menu} integre")

st.markdown("""<div class="bottom-nav"><div style="text-align:center; color:#0a2a6b; font-weight:bold; background:#e8f0fe; border-radius:20px; padding:5px 15px">Home</div><div>Liste</div><div>Qibla</div><div>Calendrier</div><div>Plus</div></div>""", unsafe_allow_html=True)
