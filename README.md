# Daily News Briefing Bot

> Pipeline automatisé qui agrège des actualités du Burkina Faso, de l'Afrique et 
> de l'international, génère un briefing structuré avec une IA (Llama 3.3) et 
> le diffuse chaque soir à 19h sur Telegram.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Groq](https://img.shields.io/badge/AI-Llama%203.3%20via%20Groq-orange.svg)](https://groq.com/)
[![GitHub Actions](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF.svg)](https://github.com/features/actions)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Problème résolu

Suivre l'actualité géopolitique et économique sur plusieurs sources prend du temps. 
Ce bot automatise complètement le processus : il agrège les flux RSS de sources 
fiables, demande à un LLM de synthétiser les informations clés en un briefing 
structuré, et l'envoie sur Telegram à heure fixe — chaque jour, sans intervention.

## Architecture
