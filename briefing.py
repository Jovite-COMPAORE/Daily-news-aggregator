# -*- coding: utf-8 -*-
"""
Bot de briefing culturel quotidien — Version Premium
Formats différenciés matin / soir
Niveau : grand public cultivé
"""

import os
import sys
import feedparser
import requests
from datetime import datetime
from groq import Groq

# ============================================================
# CONFIGURATION
# ============================================================

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

MODELE_GROQ = "llama-3.3-70b-versatile"

FLUX_RSS = {
    "Burkina Faso": [
        "https://lefaso.net/spip.php?page=backend",
        "https://burkina24.com/feed/",
    ],
    "Afrique & AES": [
        "https://www.rfi.fr/fr/afrique/rss",
        "https://www.jeuneafrique.com/feed/",
        "https://www.agenceecofin.com/component/ninjarsssyndicator/?feed_id=1&format=raw",
    ],
    "International": [
        "https://www.lemonde.fr/rss/en_continu.xml",
        "https://feeds.bbci.co.uk/afrique/rss.xml",
    ],
}

NB_ARTICLES_PAR_FLUX = 6


# ============================================================
# ÉTAPE 1 : RÉCUPÉRER LES ACTUALITÉS
# ============================================================

def recuperer_actualites():
    actualites = {}
    for categorie, urls in FLUX_RSS.items():
        actualites[categorie] = []
        for url in urls:
            try:
                print(f"Recuperation : {url}")
                feed = feedparser.parse(url)
                for entry in feed.entries[:NB_ARTICLES_PAR_FLUX]:
                    titre = entry.get("title", "").strip()
                    resume = entry.get("summary", "")[:400]
                    if titre:
                        actualites[categorie].append({
                            "titre": titre,
                            "resume": resume,
                            "source": feed.feed.get("title", "Source inconnue"),
                        })
            except Exception as e:
                print(f"Erreur sur {url} : {e}")
                continue
    return actualites


# ============================================================
# ÉTAPE 2 : CONSTRUIRE LE PROMPT SELON LE MOMENT
# ============================================================

def construire_prompt(actualites):
    now = datetime.now()
    date_du_jour = now.strftime("%A %d %B %Y")
    moment_param = os.environ.get("MOMENT_JOURNEE", "auto")

    # Déterminer le moment
    if moment_param == "matin":
        moment = "matin"
    elif moment_param == "soir":
        moment = "soir"
    else:
        heure = now.hour
        moment = "matin" if 5 <= heure < 16 else "soir"

    # Préparer les actualités brutes
    texte_actualites = ""
    for categorie, articles in actualites.items():
        texte_actualites += f"\n\n### {categorie}\n"
        for art in articles:
            texte_actualites += f"- {art['titre']}\n"
            if art['resume']:
                texte_actualites += f"  Contexte : {art['resume'][:300]}\n"

    # ============================================================
    # PROMPT MATIN
    # ============================================================
    if moment == "matin":
        prompt = f"""Tu es un service de veille informationnelle neutre et fiable,
destiné à un public africain francophone cultivé et actif professionnellement.
Tu ne donnes pas d'opinions, tu n'as pas de ligne éditoriale.
Tu informes. Tu facilites la vie des gens en leur donnant l'essentiel
de l'actualité de façon claire, précise et accessible.

Ta mission ce matin : rédiger le briefing du matin du {date_du_jour}.

RÈGLES ABSOLUES :
- Chaque information doit tenir en 1 à 2 lignes maximum
- Chaque info doit contenir un fait ET son contexte immédiat (pas juste un titre)
- Ton neutre, factuel, sans jugement ni prise de position
- Aucune mention de "(5 infos)", "(3 infos)" ou de toute autre instruction dans le rendu
- Priorité aux sujets à portée nationale, régionale ou internationale significative
- Éviter les faits divers sans portée politique, économique ou sociale
- Choisir des concepts et chiffres réellement instructifs pour un adulte cultivé
- Le chiffre du jour doit être frappant et mémorisable
- Le mot du matin doit être utile à connaître, pas trop basique, pas trop technique

STRUCTURE OBLIGATOIRE — respecte exactement cet ordre et ces emojis :

🌅 BRIEFING DU MATIN — {date_du_jour}

🇧🇫 BURKINA FASO
• [Fait précis + contexte en 1-2 lignes]
• [Fait précis + contexte en 1-2 lignes]
• [Fait précis + contexte en 1-2 lignes]
• [Fait précis + contexte en 1-2 lignes]
• [Fait précis + contexte en 1-2 lignes]

🌍 AES & AFRIQUE
• [Fait précis + contexte en 1-2 lignes]
• [Fait précis + contexte en 1-2 lignes]
• [Fait précis + contexte en 1-2 lignes]

🌐 INTERNATIONAL
• [Fait précis + contexte en 1-2 lignes]
• [Fait précis + contexte en 1-2 lignes]
• [Fait précis + contexte en 1-2 lignes]

💡 CHIFFRE DU MATIN
[Un chiffre marquant issu des actualités ou du contexte africain + 1 phrase de contexte précis]

📚 MOT DU MATIN
[Terme ou acronyme utile à connaître + définition claire en 1-2 lignes, niveau grand public cultivé]

ACTUALITÉS BRUTES À TRAITER :
{texte_actualites}

Génère UNIQUEMENT le briefing. Pas d'introduction, pas de conclusion, pas de commentaire.
"""

    # ============================================================
    # PROMPT SOIR
    # ============================================================
    else:
        prompt = f"""Tu es un service de veille informationnelle neutre et fiable,
destiné à un public africain francophone cultivé et actif professionnellement.
Tu ne donnes pas d'opinions, tu n'as pas de ligne éditoriale.
Tu informes. Tu facilites la vie des gens en leur donnant l'essentiel
de l'actualité de façon claire, précise et accessible.

Ta mission ce soir : rédiger le briefing du soir du {date_du_jour}.

RÈGLES ABSOLUES :
- Chaque information doit tenir en 1 à 2 lignes maximum
- Chaque info doit contenir un fait ET son contexte immédiat (pas juste un titre)
- Ton neutre, factuel, sans jugement ni prise de position
- Aucune mention de "(5 infos)", "(3 infos)" ou de toute autre instruction dans le rendu
- Priorité aux sujets à portée nationale, régionale ou internationale significative
- Éviter les faits divers sans portée politique, économique ou sociale
- Le chiffre du jour doit être frappant et mémorisable
- Le concept du jour : ni trop basique (pas "l'ONU c'est quoi"), ni trop technique
  Vise un adulte cultivé qui lit de temps en temps mais n'est pas spécialiste
- L'institution du jour : choisir une institution africaine ou internationale
  réellement utile à connaître dans le contexte actuel
- La question du soir : niveau grand public cultivé, pas niveau concours
  Elle doit être intéressante, pas évidente, mais accessible sans être spécialiste
- "Demain à suivre" : 1 ou 2 événements/échéances concrets attendus le lendemain

STRUCTURE OBLIGATOIRE — respecte exactement cet ordre et ces emojis :

🌙 BRIEFING DU SOIR — {date_du_jour}

🇧🇫 BURKINA FASO
• [Fait précis + contexte en 1-2 lignes]
• [Fait précis + contexte en 1-2 lignes]
• [Fait précis + contexte en 1-2 lignes]
• [Fait précis + contexte en 1-2 lignes]
• [Fait précis + contexte en 1-2 lignes]

🌍 AES & AFRIQUE
• [Fait précis + contexte en 1-2 lignes]
• [Fait précis + contexte en 1-2 lignes]
• [Fait précis + contexte en 1-2 lignes]

🌐 INTERNATIONAL
• [Fait précis + contexte en 1-2 lignes]
• [Fait précis + contexte en 1-2 lignes]
• [Fait précis + contexte en 1-2 lignes]

💡 CHIFFRE DU JOUR
[Un chiffre marquant issu des actualités ou du contexte africain + 1 phrase de contexte précis]

📚 CONCEPT DU JOUR
[Notion utile à connaître + explication claire en 2 lignes, niveau grand public cultivé]

🏛 INSTITUTION DU JOUR
[Nom complet de l'institution + son rôle concret en 2 lignes dans le contexte actuel]

❓ QUESTION DU SOIR
Q : [Question intéressante et accessible, niveau grand public cultivé]
R : [Réponse directe + 1 phrase d'explication]

🗓 DEMAIN À SUIVRE
• [Événement ou échéance concret attendu demain]
• [Événement ou échéance concret attendu demain — si pertinent]

ACTUALITÉS BRUTES À TRAITER :
{texte_actualites}

Génère UNIQUEMENT le briefing. Pas d'introduction, pas de conclusion, pas de commentaire.
"""

    return prompt, moment


# ============================================================
# ÉTAPE 3 : GÉNÉRER LE BRIEFING AVEC GROQ
# ============================================================

def generer_briefing(actualites):
    client = Groq(api_key=GROQ_API_KEY)
    prompt, moment = construire_prompt(actualites)

    print(f"Generation du briefing ({moment}) par Llama 3.3 via Groq...")

    completion = client.chat.completions.create(
        model=MODELE_GROQ,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=2500,
    )

    return completion.choices[0].message.content


# ============================================================
# ÉTAPE 4 : ENVOYER SUR TELEGRAM
# ============================================================

def envoyer_telegram(texte):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    MAX_LONGUEUR = 4000
    morceaux = []

    if len(texte) <= MAX_LONGUEUR:
        morceaux = [texte]
    else:
        lignes = texte.split("\n")
        morceau_actuel = ""
        for ligne in lignes:
            if len(morceau_actuel) + len(ligne) + 1 > MAX_LONGUEUR:
                morceaux.append(morceau_actuel)
                morceau_actuel = ligne + "\n"
            else:
                morceau_actuel += ligne + "\n"
        if morceau_actuel:
            morceaux.append(morceau_actuel)

    for i, morceau in enumerate(morceaux):
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": morceau,
            "disable_web_page_preview": True,
        }
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print(f"Message {i+1}/{len(morceaux)} envoye sur Telegram")
        else:
            print(f"Erreur Telegram : {response.status_code} - {response.text}")
            return False
    return True


# ============================================================
# FONCTION PRINCIPALE
# ============================================================

def main():
    if not GROQ_API_KEY:
        print("Cle GROQ_API_KEY manquante")
        sys.exit(1)
    if not TELEGRAM_BOT_TOKEN:
        print("TELEGRAM_BOT_TOKEN manquant")
        sys.exit(1)
    if not TELEGRAM_CHAT_ID:
        print("TELEGRAM_CHAT_ID manquant")
        sys.exit(1)

    print(f"Demarrage du briefing - {datetime.now()}")

    actualites = recuperer_actualites()
    total_articles = sum(len(arts) for arts in actualites.values())
    print(f"{total_articles} articles recuperes au total")

    if total_articles == 0:
        print("Aucun article recupere. Arret.")
        sys.exit(1)

    briefing = generer_briefing(actualites)
    print(f"Briefing genere ({len(briefing)} caracteres)")

    succes = envoyer_telegram(briefing)

    if succes:
        print("Briefing envoye avec succes !")
    else:
        print("Echec de l'envoi")
        sys.exit(1)


if __name__ == "__main__":
    main()
