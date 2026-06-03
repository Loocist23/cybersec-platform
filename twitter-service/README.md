# Twitter Service

> **Microservice de récupération et d'analyse de tweets depuis X (Twitter)** — Cybersec Platform

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://python.org/)
[![snscrape](https://img.shields.io/badge/snscrape-0.6.0-orange.svg)](https://github.com/haccer/tweepy)
[![uv](https://img.shields.io/badge/uv-Package%20Manager-orange.svg)](https://github.com/astral-sh/uv)
[![Status](https://img.shields.io/badge/Status-Development-yellow.svg)]

---

## 📌 Description

**Twitter Service** est un **microservice Python** responsable de la **collecte automatique de tweets** depuis **X (Twitter)** via la librairie **snscrape**.

Il permet de :
- **Récupérer** les tweets par requêtes de recherche (hashtags, mots-clés)
- **Récupérer** les tweets par noms d'utilisateurs spécifiques
- **Extraire** les informations des comptes Twitter (followers, bio, etc.)
- **Envoyer** les données à l'API Service pour stockage
- **Suivre** les tendances en cybersécurité sur les réseaux sociaux

**Pas besoin d'API Key Twitter** : Utilise **snscrape** qui permet de scraper Twitter sans authentification.

---

## 🎯 Fonctionnalités

| Feature | Description |
|---------|-------------|
| **Recherche par requête** | Récupération de tweets par mots-clés/hashtags |
| **Recherche par utilisateur** | Récupération des tweets d'un compte spécifique |
| **Récupération des infos compte** | Informations complètes sur les comptes Twitter |
| **Filtrage** | Par likes, retweets, langue, période |
| **Tweets trending** | Récupération des tweets populaires |
| **Envoi batch à API** | POST /tweets/batch et /twitter_accounts/ |
| **Mode Daemon** | Exécution périodique automatique |
| **Rate Limiting** | Respect des limites de Twitter |

---

## 📦 Stack Technique

| Technologie | Version | Usage |
|-------------|---------|-------|
| **Python** | 3.10+ | Runtime |
| **snscrape** | ≥0.6.0 | Scraping Twitter |
| **requests** | ≥2.31.0 | HTTP Client |
| **uv** | latest | Package Manager |
| **pydantic** | ≥2.5.0 | Data Validation |
| **python-dotenv** | ≥1.0.0 | Environment Variables |

---

## 🚀 Installation et Configuration

### 📥 Prérequis

- Python 3.10+
- uv (recommandé) ou pip
- API Service en cours d'exécution (sur http://localhost:8000 par défaut)

### 🛠️ Configuration

#### 1. Installer les dépendances avec uv

```bash
# Depuis le dossier twitter-service/
uv sync
```

Ou avec pip :
```bash
pip install -r pyproject.toml
```

#### 2. Configurer .env

Copier `.env.example` en `.env` et adapter :

```bash
cp .env.example .env
nano .env
```

**Variables principales** :

| Variable | Description | Défaut |
|----------|-------------|--------|
| `API_URL` | URL de base de l'API | `http://localhost:8000` |
| `SEARCH_QUERIES` | Requêtes de recherche | `cybersecurity,vulnerability,...` |
| `SEARCH_DAYS_BACK` | Jours à remonter | `7` |
| `MAX_TWEETS_PER_REQUEST` | Max tweets par requête | `50` |
| `REQUEST_DELAY` | Délai entre requêtes (s) | `5` |
| `MIN_LIKES` | Likes minimum pour filtrer | `0` |
| `MIN_RETWEETS` | Retweets minimum | `0` |
| `LANGUAGE` | Langue des tweets | `en` |
| `LOG_LEVEL` | Niveau de logging | `INFO` |

---

## 🚀 Utilisation

### Commandes de base

```bash
# Récupérer les tweets par requêtes par défaut
python -m twitter_service.main

# Récupérer par requêtes spécifiques
python -m twitter_service.main --queries cybersecurity,malware,infosec

# Récupérer par utilisateurs
python -m twitter_service.main --usernames krebsbrian tavlakou swanandx

# Récupérer les tweets populaires (trending)
python -m twitter_service.main --trending

# Récupérer les tweets des 14 derniers jours
python -m twitter_service.main --days 14

# Limiter à 10 tweets par requête
python -m twitter_service.main --limit 10

# Combiner plusieurs options
python -m twitter_service.main --queries CVE,vulnerability --days 3 --limit 20
```

### Mode Daemon (Recommandé pour la production)

```bash
# Exécution toutes les 24 heures
python -m twitter_service.main --daemon

# Exécution toutes les 12 heures
python -m twitter_service.main --daemon --daemon-interval 12

# Avec des requêtes spécifiques
python -m twitter_service.main --daemon --queries cybersecurity,malware
```

### Test de connexion

```bash
# Vérifier que tout fonctionne
python -m twitter_service.main --test
```

### Docker

#### Build

```bash
docker build -t cybersec-twitter:latest .
```

#### Run

```bash
docker run -d \
  --name cybersec-twitter \
  -v $(pwd)/logs:/app/logs \
  --env-file .env \
  cybersec-twitter:latest
```

Ou avec les paramètres directement :
```bash
docker run -d \
  --name cybersec-twitter \
  -e API_URL=http://api:8000 \
  -e SEARCH_QUERIES=cybersecurity,malware \
  cybersec-twitter:latest
```

---

## 📡 API Endpoints Utilisés

### POST /tweets/batch

Endpoint utilisé pour envoyer les tweets collectés à l'API Service.

**Exemple de payload** :
```json
{
  "tweet_id": "123456789",
  "username": "krebsbrian",
  "content": "New zero-day vulnerability discovered...",
  "date": "2026-05-30T10:00:00",
  "url": "https://twitter.com/krebsbrian/status/123456789",
  "likes": 1500,
  "retweets": 500,
  "hashtags": ["cybersecurity", "zeroday"],
  "language": "en"
}
```

### POST /twitter_accounts/

Endpoint utilisé pour envoyer les informations des comptes.

**Exemple de payload** :
```json
{
  "username": "krebsbrian",
  "display_name": "Brian Krebs",
  "bio": "Investigative journalist...",
  "followers_count": 450000,
  "verified": true,
  "url": "https://twitter.com/krebsbrian"
}
```

---

## 📂 Structure du Projet

```
twitter-service/
├── pyproject.toml              # Dépendances uv
├── Dockerfile                  # Configuration Docker
├── .env.example                # Template de configuration
├── .gitignore
├── README.md
├── src/
│   └── twitter_service/
│       ├── __init__.py
│       ├── config.py          # Configuration centrale
│       ├── main.py            # CLI entry point
│       ├── models/
│       │   ├── __init__.py
│       │   └── tweet.py        # Modèles Pydantic
│       ├── services/
│       │   ├── __init__.py
│       │   ├── twitter_client.py  # Client snscrape
│       │   ├── api_client.py     # Client API Cybersec
│       │   └── collector.py      # Orchestrateur
│       └── utils/
│           ├── __init__.py
│           └── logger.py       # Configuration des logs
├── logs/                       # Logs (runtime)
└── data/                       # Data (runtime)
```

---

## 📊 Modèles de Données

### Tweet

```python
class Tweet(BaseModel):
    tweet_id: str           # ID unique du tweet
    username: str           # Nom d'utilisateur
    content: str            # Contenu du tweet
    date: datetime          # Date de publication
    url: str               # URL du tweet
    likes: int             # Nombre de likes
    retweets: int          # Nombre de retweets
    hashtags: List[str]     # Liste des hashtags
    language: Optional[str] # Langue du tweet
    # ... autres champs
```

### TwitterAccount

```python
class TwitterAccount(BaseModel):
    username: str              # Nom d'utilisateur
    display_name: Optional[str] # Nom affiché
    bio: Optional[str]        # Biographie
    followers_count: int    # Nombre d'abonnés
    verified: bool           # Compte vérifié
    url: Optional[str]       # URL du profil
    # ... autres champs
```

---

## 🔧 Configuration Avancée

### Personnalisation des requêtes

```ini
# Dans .env
SEARCH_QUERIES=cybersecurity,vulnerability,infosec,CVE,malware,hacking,exploit,zero-day
SEARCH_DAYS_BACK=7
MAX_TWEETS_PER_REQUEST=50
```

### Filtrage avancé

```ini
MIN_LIKES=10      # Ignorer les tweets avec moins de 10 likes
MIN_RETWEETS=5   # Ignorer les tweets avec moins de 5 retweets
LANGUAGE=en       # Seule la langue anglaise
INCLUDE_REPLIES=false  # Exclure les réponses
INCLUDE_RETWEETS=false # Exclure les retweets
```

### Rate Limiting

```ini
REQUEST_DELAY=5           # Secondes entre les requêtes
MAX_REQUESTS_PER_MINUTE=30 # Max requêtes par minute
```

---

## 🛠️ Dépannage

### Problèmes Courants

| Problème | Cause | Solution |
|----------|-------|----------|
| **API non disponible** | API Service non lancé | `docker-compose -f docker-compose-simple.yml up -d api` |
| **Aucun tweet trouvé** | Requêtes trop restrictives | Vérifier SEARCH_QUERIES |
| **Rate limit** | Trop de requêtes | Augmenter REQUEST_DELAY |
| **Erreur snscrape** | Problème réseau | Vérifier la connexion internet |
| **Erreur de parsing** | Format de tweet invalide | Vérifier les logs |

### Commandes Utiles

```bash
# Vérifier les logs
tail -f logs/twitter_service.log

# Tester la connexion à l'API
curl http://localhost:8000/health

# Voir les tweets stockés
curl http://localhost:8000/tweets/ | jq '.total'

# Voir les comptes stockés
curl http://localhost:8000/tweets/accounts/ | jq '.total'

# Voir les stats
curl http://localhost:8000/tweets/stats | jq
```

---

## 📅 Roadmap

### ✅ Terminé

- [x] Intégration de snscrape pour le scraping
- [x] Récupération par requêtes de recherche
- [x] Récupération par noms d'utilisateurs
- [x] Extraction des infos des comptes
- [x] Filtrage par likes/retweets/langue
- [x] Envoi batch à l'API Service
- [x] Mode Daemon
- [x] Docker support
- [x] CLI interface
- [x] Logging structuré

### 🟡 À Court Terme

- [ ] Ajouter la recherche par géolocalisation
- [ ] Implémenter la détection de nouvelles tendances
- [ ] Ajouter l'analyse de sentiment des tweets
- [ ] Notifications pour les tweets importants
- [ ] Cache des résultats

### 🟢 Moyen Terme

- [ ] Support de l'API Twitter officielle (avec OAuth)
- [ ] Intégration avec des outils d'analyse (NLP)
- [ ] Détection automatique de comptes pertinents
- [ ] Alertes en temps réel

### 🔵 Long Terme

- [ ] Streaming en temps réel
- [ ] Analyse de réseaux de comptes
- [ ] Détection de campagnes de désinformation
- [ ] Intégration avec MISP (Malware Information Sharing Platform)

---

## 📄 Documentation Connexe

- [Projet Cybersec Platform](../../README.md)
- [API Service](../api-service/README.md)
- [Docker Compose](../../docker-compose.yml)

---

## 📜 Metadata

| Propriété | Valeur |
|-----------|--------|
| **Créé** | Mai 2026 |
| **Auteur** | loocist |
| **Version** | 0.1.0 |
| **Language** | Python 3.10+ |
| **Dependencies** | uv, snscrape, requests, pydantic, python-dotenv |

---

*Dernière mise à jour : 31 mai 2026*
