# -*- coding: utf-8 -*-
import os
import sys
import feedparser
import requests
from datetime import datetime
from groq import Groq

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

NB_ARTICLES_PAR_FLUX = 5


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
                    resume = entry.get("summary", "")[:300]
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


def construire_prompt(actualites):
    now = datetime.now()
    date_du_jour = now.strftime("%A %d %B %Y")

    moment_param = os.environ.get("MOMENT_JOURNEE", "auto")

    if moment_param == "matin":
        moment = "matin"
        emoji_titre = "🌅"
        titre = f"BRIEFING DU MATIN — {date_du_jour}"
        intro_contextuelle = (
            "Tour d'horizon rapide pour bien demarrer la journee. "
            "Ton direct, energique, informatif."
        )
    elif moment_param == "soir":
        moment = "soir"
        emoji_titre = "🌙"
        titre = f"BRIEFING DU SOIR — {date_du_jour}"
        intro_contextuelle = (
            "Point final de la journee avec prise de recul sur les evenements."
        )
    else:
        heure = now.hour
        if 5 <= heure < 16:
            moment = "matin"
            emoji_titre = "🌅"
            titre = f"BRIEFING DU MATIN — {date_du_jour}"
            intro_contextuelle = "Tour d'horizon rapide pour bien demarrer la journee."
        else:
            moment = "soir"
            emoji_titre = "🌙"
            titre = f"BRIEFING DU SOIR — {date_du_jour}"
            intro_contextuelle = "Point final de la journee avec prise de recul."

    texte_actualites = ""
    for categorie, articles in actualites.items():
        texte_actualites += f"\n\n### {categorie}\n"
        for art in articles:
            texte_actualites += f"- {art['titre']}\n"
            if art['resume']:
                texte_actualites += f"  Extrait : {art['resume'][:200]}\n"

    prompt = f"""Tu es un coach de culture generale qui prepare un candidat a un concours
de la fonction publique au Burkina Faso. Le candidat vise des postes de Data Analyst
dans des societes d'Etat burkinabe.

{intro_contextuelle}

A partir des actualites brutes ci-dessous, redige un briefing de culture generale
structure pour le {moment} du {date_du_jour}.

EXIGENCES DE FORMAT :
- Utilise exactement la structure donnee ci-dessous
- Sois concis : chaque info en 1-2 lignes maximum
- Priorite aux sujets qui peuvent tomber dans un concours : geopolitique, economie,
  Burkina Faso, AES (Alliance des Etats du Sahel), institutions africaines
- Evite les faits divers sans portee geopolitique ou economique
- N'affiche PAS les mentions comme "(3 infos max)" dans le rendu final

ACTUALITES BRUTES A TRAITER :
{texte_actualites}

STRUCTURE OBLIGATOIRE DU BRIEFING :

{emoji_titre} {titre}

🇧🇫 BURKINA FASO
- [Info 1]
- [Info 2]
- [Info 3]

🌍 AES & AFRIQUE
- [Info 1]
- [Info 2]
- [Info 3]

🌐 INTERNATIONAL
- [Info 1]
- [Info 2]

💡 LE CHIFFRE DU JOUR
[Un chiffre marquant tire des actualites + 1 phrase de contexte]

📚 MOT/CONCEPT DU JOUR
[Un acronyme, institution ou concept important a retenir + definition en 2 lignes]

❓ QUESTION DU JOUR
Q : [Question type QCM concours, 1 phrase claire]
R : [Reponse + 1 phrase d'explication]

Genere UNIQUEMENT le briefing, sans introduction ni commentaire.
"""
    return prompt


def generer_briefing(actualites):
    client = Groq(api_key=GROQ_API_KEY)
    prompt = construire_prompt(actualites)
    print("Generation du briefing par Llama 3.3 via Groq...")
    completion = client.chat.completions.create(
        model=MODELE_GROQ,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=2000,
    )
    return completion.choices[0].message.content


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
