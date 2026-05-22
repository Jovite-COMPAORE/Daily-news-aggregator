# -*- coding: utf-8 -*-
"""
Bot de briefing culturel quotidien
Récupère les actualités du jour, les fait résumer par Llama 3.3 (via Groq),
et envoie le briefing sur Telegram à 8h00 et à 19h00.

API utilisée : Groq (gratuite)
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

# Modèle Groq à utiliser
# Alternatives :
# - "llama-3.3-70b-versatile" (recommandé, meilleure qualité)
# - "llama-3.1-8b-instant" (plus rapide, moins précis)
MODELE_GROQ = "llama-3.3-70b-versatile"

# Sources RSS fiables
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


# ============================================================
# ÉTAPE 1 : RÉCUPÉRER LES ACTUALITÉS
# ============================================================

def recuperer_actualites():
    """Parcourt tous les flux RSS et récupère les derniers titres"""
    actualites = {}

    for categorie, urls in FLUX_RSS.items():
        actualites[categorie] = []

        for url in urls:
            try:
                print(f"📡 Récupération : {url}")
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
                print(f"⚠ Erreur sur {url} : {e}")
                continue

    return actualites


# ============================================================
# ÉTAPE 2 : GÉNÉRER LE BRIEFING AVEC GROQ
# ============================================================

def construire_prompt(actualites):
    """
    Construit le prompt qui sera envoyé à Llama 3.3
    Adapte le ton et le titre selon l'heure (matin ou soir)
    """
now = datetime.now()
    date_du_jour = now.strftime("%A %d %B %Y")

    # Moment imposé par cron-job.org (fiable) ou deviné par l'heure (fallback)
    moment_param = os.environ.get("MOMENT_JOURNEE", "auto")

    if moment_param == "matin":
        moment, emoji_titre = "matin", "🌅"
        titre = f"BRIEFING DU MATIN — {date_du_jour}"
        intro_contextuelle = (
            "Tour d'horizon rapide pour bien démarrer la journée. "
            "Ton direct, énergique, informatif."
        )
    elif moment_param == "soir":
        moment, emoji_titre = "soir", "🌙"
        titre = f"BRIEFING DU SOIR — {date_du_jour}"
        intro_contextuelle = (
            "Point final de la journée avec prise de recul sur les événements."
        )
    else:
        # Fallback si déclenché par le schedule GitHub (sans paramètre)
        heure = now.hour
        if 5 <= heure < 16:
            moment, emoji_titre = "matin", "🌅"
            titre = f"BRIEFING DU MATIN — {date_du_jour}"
            intro_contextuelle = "Tour d'horizon rapide pour bien démarrer la journée."
        else:
            moment, emoji_titre = "soir", "🌙"
            titre = f"BRIEFING DU SOIR — {date_du_jour}"
            intro_contextuelle = "Point final de la journée avec prise de recul."
    texte_actualites = ""
    for categorie, articles in actualites.items():
        texte_actualites += f"\n\n### {categorie}\n"
        for art in articles:
            texte_actualites += f"- {art['titre']}\n"
            if art['resume']:
                texte_actualites += f"  Extrait : {art['resume'][:200]}\n"

    prompt = f"""Tu es un coach de culture générale qui prépare un candidat à un concours 
de la fonction publique au Burkina Faso. Le candidat vise des postes de Data Analyst 
dans des sociétés d'État burkinabè.

{intro_contextuelle}

À partir des actualités brutes ci-dessous, rédige un briefing de culture générale 
structuré pour le {moment} du {date_du_jour}.

EXIGENCES DE FORMAT :
- Utilise exactement la structure donnée ci-dessous
- Sois concis : chaque info en 1-2 lignes maximum
- Priorité aux sujets qui peuvent tomber dans un concours : géopolitique, économie, 
  Burkina Faso, AES (Alliance des États du Sahel), institutions africaines
- Évite les faits divers sans portée géopolitique ou économique
- Termine par UNE question de culture générale pertinente avec sa réponse
- N'affiche PAS les mentions "(3 infos max)" dans le rendu final

ACTUALITÉS BRUTES À TRAITER :
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
[Un chiffre marquant tiré des actualités + 1 phrase de contexte]

📚 MOT/CONCEPT DU JOUR
[Un acronyme, institution ou concept important à retenir + définition en 2 lignes]

❓ QUESTION DU JOUR
Q : [Question type QCM concours, 1 phrase claire]
R : [Réponse + 1 phrase d'explication]

Génère UNIQUEMENT le briefing, sans introduction ni commentaire.
"""
    return prompt


def generer_briefing(actualites):
    """Envoie les actualités à Groq et récupère le briefing formaté"""
    client = Groq(api_key=GROQ_API_KEY)
    prompt = construire_prompt(actualites)

    print("🧠 Génération du briefing par Llama 3.3 via Groq...")

    completion = client.chat.completions.create(
        model=MODELE_GROQ,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=2000,
    )

    return completion.choices[0].message.content


# ============================================================
# ÉTAPE 3 : ENVOYER SUR TELEGRAM
# ============================================================

def envoyer_telegram(texte):
    """Envoie le briefing sur Telegram (découpé si > 4096 caractères)"""
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
            print(f"✅ Message {i+1}/{len(morceaux)} envoyé sur Telegram")
        else:
            print(f"❌ Erreur Telegram : {response.status_code} - {response.text}")
            return False

    return True


# ============================================================
# FONCTION PRINCIPALE
# ============================================================

def main():
    if not GROQ_API_KEY:
        print("❌ Clé GROQ_API_KEY manquante")
        sys.exit(1)
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN manquant")
        sys.exit(1)
    if not TELEGRAM_CHAT_ID:
        print("❌ TELEGRAM_CHAT_ID manquant")
        sys.exit(1)

    print(f"🚀 Démarrage du briefing - {datetime.now()}")

    actualites = recuperer_actualites()
    total_articles = sum(len(arts) for arts in actualites.values())
    print(f"📰 {total_articles} articles récupérés au total")

    if total_articles == 0:
        print("⚠ Aucun article récupéré. Arrêt.")
        sys.exit(1)

    briefing = generer_briefing(actualites)
    print(f"📝 Briefing généré ({len(briefing)} caractères)")

    succes = envoyer_telegram(briefing)

    if succes:
        print("🎉 Briefing envoyé avec succès !")
    else:
        print("❌ Échec de l'envoi")
        sys.exit(1)


if __name__ == "__main__":
    main()
