# Daily News Briefing Bot 🇧🇫

> Pipeline automatisé d'agrégation de news (Burkina Faso, Afrique, International) avec synthèse par IA et diffusion sur Telegram.  
> *Automated daily news briefing pipeline using RSS feeds, Llama 3.3 (Groq) and Telegram. Built with Python and GitHub Actions.*

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Groq](https://img.shields.io/badge/AI-Llama%203.3%20via%20Groq-orange.svg)](https://groq.com/)
[![GitHub Actions](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF.svg)](https://github.com/features/actions)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Problème résolu

Suivre l'actualité géopolitique et économique sur plusieurs sources prend du temps. Ce bot automatise complètement le processus : il agrège les flux RSS de sources fiables, demande à un LLM de synthétiser les informations clés en un briefing structuré, et l'envoie sur Telegram à heure fixe — chaque jour, sans intervention.

## Architecture
┌─────────────────┐
│ GitHub Actions  │  Cron quotidien à 19:00 UTC
└────────┬────────┘
│
▼
┌─────────────────┐     ┌──────────────┐     ┌──────────────┐
│  RSS Aggregator │────▶│  Groq API    │────▶│ Telegram Bot │
│  (feedparser)   │     │ (Llama 3.3)  │     │  (channel)   │
└─────────────────┘     └──────────────┘     └──────────────┘
7 flux RSS          Synthèse formatée       Diffusion

### Flux d'exécution

1. **Ingestion** : récupération de 35+ articles depuis 7 flux RSS (Burkina, Afrique, International)
2. **Traitement** : envoi à l'API Groq avec un prompt système optimisé pour la culture générale et la géopolitique
3. **Génération** : Llama 3.3 produit un briefing structuré (résumés, chiffre du jour, concept clé, QCM)
4. **Diffusion** : envoi formaté sur un canal Telegram dédié

## 🛠 Stack technique

| Couche | Technologie |
|---|---|
| Langage | Python 3.11 |
| Ingestion RSS | `feedparser` |
| Modèle de langage | Llama 3.3 70B via Groq API |
| Diffusion | Telegram Bot API |
| Orchestration | GitHub Actions (cron schedule) |
| Gestion des secrets | GitHub Secrets (chiffrement natif) |

## Sources d'actualités

| Catégorie | Sources |
|---|---|
| 🇧🇫 Burkina Faso | lefaso.net, burkina24.com |
| 🌍 Afrique & AES | RFI Afrique, Jeune Afrique, Agence Ecofin |
| 🌐 International | Le Monde, BBC Afrique |

## Installation locale

```bash
# 1. Cloner le dépôt
git clone https://github.com/Jovite-COMPAORE/Daily-news-aggregator.git
cd Daily-news-aggregator

# 2. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
export GROQ_API_KEY="gsk_..."
export TELEGRAM_BOT_TOKEN="..."
export TELEGRAM_CHAT_ID="-100..."

# 5. Lancer manuellement
python briefing.py
```

## Configuration

### Sources RSS

Modifier le dictionnaire `FLUX_RSS` dans `briefing.py` pour ajouter ou retirer des sources :

```python
FLUX_RSS = {
    "Catégorie": ["url_rss_1", "url_rss_2"],
}
```

### Heure d'exécution

Modifier le `cron` dans `.github/workflows/briefing.yml` :

```yaml
schedule:
  - cron: '0 19 * * *'  # Format : minute heure jour mois jour_semaine (UTC)
```

### Modèle de langage

Modifier la variable `MODELE_GROQ` dans `briefing.py` :
- `llama-3.3-70b-versatile` (qualité optimale, recommandé)
- `llama-3.1-8b-instant` (latence minimale, qualité réduite)

## Compétences démontrées

Ce projet illustre plusieurs compétences clés en data engineering et automatisation :

- ✅ **Pipeline de données end-to-end** : ingestion → transformation → diffusion
- ✅ **Intégration d'APIs REST** (Groq, Telegram) avec gestion d'erreurs
- ✅ **Automatisation CI/CD** via GitHub Actions
- ✅ **Gestion sécurisée des secrets** (jamais dans le code source)
- ✅ **Prompt engineering** pour LLM en production
- ✅ **Code Python modulaire** : fonctions isolées et testables
- ✅ **Documentation professionnelle** (README, conventions de commits)

## Améliorations envisagées

- [ ] Persistance des briefings dans une base SQLite pour archivage
- [ ] Détection de doublons inter-sources via similarité sémantique
- [ ] Dashboard de statistiques (sources les plus actives, sujets récurrents)
- [ ] Tests unitaires sur le parsing RSS et le formatage
- [ ] Support multi-canal (Telegram + Email + Slack)
- [ ] Interface web légère pour configuration sans toucher au code

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## Auteur

**Jovite COMPAORE**  
Data Analyst | Ouagadougou, Burkina Faso  
🔗 GitHub : [@Jovite-COMPAORE](https://github.com/Jovite-COMPAORE)

---

⭐ Si ce projet te plaît, n'hésite pas à mettre une étoile !
