# 📚 Documentation Complète - Cybersec Platform

> **Plateforme Microservice de Veille en Cybersécurité**
> Version : 0.2.0 | Dernière mise à jour : 6 juin 2026

---

## 📖 Table des Matières

1. [🎯 Vue d'Ensemble](#-vue-densemble)
2. [🏗️ Architecture](#-architecture)
3. [📦 Microservices](#-microservices)
   - [Aggregator Service](#1-aggregator-service)
   - [API Service](#2-api-service)
   - [AI Service](#3-ai-service)
   - [Twitter Service](#4-twitter-service)
4. [🗃️ Base de Données](#-base-de-données)
5. [🚀 Déploiement](#-déploiement)
6. [📊 Flux de Données](#-flux-de-données)
7. [🔧 Configuration](#-configuration)
8. [🛠️ Dépannage](#-dépannage)

---

## 🎯 Vue d'Ensemble

**Cybersec Platform** est une **architecture microservice modulaire** conçue pour :

- ✅ **Collecter** automatiquement les vulnérabilités CVE depuis NVD
- ✅ **Stocker** les données dans PostgreSQL
- ✅ **Exposer** via une API REST FastAPI
- ✅ **Analyser** intelligemment avec IA (Mistral)
- ✅ **Récupérer** les tweets liés à la cybersécurité
- ✅ **Grouper** et classer les vulnérabilités

### 🎯 Objectifs Atteints

| Phase | Status | Fonctionnalités |
|-------|--------|-----------------|
| **Phase 1 : Fondation** | ✅ Terminé | Aggregator + API + PostgreSQL + Docker |
| **Phase 2 : Analyse IA** | ✅ Terminé | AI Service + Groupement + Mistral |
| **Phase 3 : Social** | ✅ Terminé | Twitter Service + Tweets |
| **Phase 4 : Production** | 🟡 En cours | Auth, Notifications, Dashboard |

### 📊 Statistiques Projet

| Métrique | Valeur |
|----------|--------|
| Nombre de microservices | **4** (Aggregator + API + AI + Twitter) |
| Langage | Python 3.12 |
| Package Manager | uv |
| Conteneurs Docker | 4 (PostgreSQL + 3 services) + 1 (Twitter) |
| Rate Limiting NVD | 5 requêtes / 30 secondes |
| Tables PostgreSQL | 6+ (cves, references, analyses, mappings, tweets, accounts) |
| **Endpoints API** | **28 endpoints** total |
| Lignes de code | ~2,500+ |

---

## 🏗️ Architecture

### Diagramme Global

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CYBERSEC PLATFORM v0.2.0                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐          │
│  │                 │    │                 │    │                 │          │
│  │  Aggregator     │    │    API          │    │  AI Service     │          │
│  │  Service        │───▶│    Service       │───▶│                 │          │
│  │  (NVD API)      │    │  (FastAPI)       │    │  (Mistral)      │          │
│  │                 │    │                 │    │                 │          │
│  └─────────────────┘    └──────────┬──────┘    └─────────────────┘          │
│                                      │                                    │
│                                      ▼                                    │
│                              ┌─────────────────┐                          │
│                              │  PostgreSQL      │                          │
│                              │  (Docker)        │                          │
│                              │  - cves         │                          │
│                              │  - references    │                          │
│                              │  - analyses      │                          │
│                              │  - mappings      │                          │
│                              │  - tweets        │                          │
│                              │  - accounts      │                          │
│                              └──────────┬──────┘                          │
│                                         │                                   │
│                                         ▼                                   │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                                                                         │  │
│  │                        Twitter Service                               │  │
│  │                        (snscrape)                                     │  │
│  │                                                                         │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
     │                    │                    │                    │
     ▼                    ▼                    ▼                    ▼
  NVD API            API REST           Mistral AI        X (Twitter)
```

### Communication Inter-Services

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│ Aggregator   │──────▶│ API         │◀──────│ AI Service   │
│             │ POST   │             │        │             │
│             │ /cves/batch │        │             │
└─────────────┘       └──────────┬──┘        └─────────────┘
                                    │
                                    ▼
                          ┌─────────────┐
                          │ PostgreSQL  │
                          │             │
                          └─────────────┘
                                    │
┌─────────────┐       ┌─────────────┐       │
│ Twitter      │──────▶│ API         │───────┘
│ Service      │ POST   │             │
│             │ /tweets/batch │
└─────────────┘       └─────────────┘
```

---

## 📦 Microservices

---

### 1️⃣ Aggregator Service

**Rôle** : Collecte et prétraite les vulnérabilités CVE depuis l'API NVD.

#### 🎯 Fonctionnalités

| Feature | Description | Status |
|---------|-------------|--------|
| Collection NVD API | Récupération via API REST officielle | ✅ |
| Respect Rate Limiting | 5 req/30s (NVD_REQUEST_DELAY=30) | ✅ |
| Filtrage temporel | Par nombre de jours | ✅ |
| Filtrage severity | CRITICAL, HIGH, MEDIUM, LOW | ✅ |
| Filtrage score | Score CVSS minimum | ✅ |
| Normalisation | cvss_severity → majuscules | ✅ |
| Batch Processing | Envoi groupé vers API | ✅ |
| Fallback SQLite | Stockage local si API indisponible | ✅ |
| Mode Daemon | Exécution périodique | ✅ |
| Détection doublons | Vérification avant envoi | ✅ |

#### 🏗️ Architecture Interne

```
aggregator-service/
├── src/cybersec_aggregator/
│   ├── config.py              # Configuration centrale
│   ├── main.py                # CLI entry point
│   ├── models/
│   │   └── cve.py             # Modèles Pydantic (CVE, CVEDbRecord)
│   ├── services/
│   │   ├── collector.py       # Orchestrateur principal
│   │   ├── nvd.py             # Client API NVD
│   │   └── database.py        # Service SQLite (fallback)
│   └── utils/
│       └── logger.py          # Configuration logging
├── Dockerfile
├── pyproject.toml
└── .env.example
```

#### 📊 Modèles de Données

**CVE (NVD brut)** : Modèle complet tel que retourné par NVD API
- `id`: str (ex: CVE-2024-12345)
- `published`: datetime
- `lastModified`: datetime
- `descriptions`: List[CVEDescription] (multi-langues)
- `metrics`: Dict[str, List[CVSSMetrics]]
- `references`: List[CVEReference]
- `weakesses`: Optional[List[Dict]] (CWE)

**CVEDbRecord (Pour stockage/envoi API)** :
- `cve_id`: str
- `published_at`: datetime
- `last_modified`: datetime
- `description`: Optional[str]
- `cvss_score`: Optional[float]
- `cvss_severity`: Optional[str] (LOW, MEDIUM, HIGH, CRITICAL)
- `vector`: Optional[str]
- `references`: Optional[List[str]]

#### 🚀 Commandes CLI

```bash
# Collection basique (7 derniers jours)
python -m cybersec_aggregator.main --days 7 --send-to-api

# Collection avec filtres
python -m cybersec_aggregator.main \
  --days 30 \
  --severity CRITICAL HIGH \
  --min-score 7.0 \
  --send-to-api \
  --api-url http://localhost:8000

# Mode daemon (toutes les 6 heures)
python -m cybersec_aggregator.main \
  --daemon \
  --daemon-interval 6 \
  --send-to-api

# Lister les CVE locales (SQLite)
python -m cybersec_aggregator.main --list --limit 50

# Statistiques
python -m cybersec_aggregator.main --stats

# Effacer les données locales
python -m cybersec_aggregator.main --clear
```

#### 📝 Configuration (.env)

```ini
# NVD API
NVD_API_URL=https://services.nvd.nist.gov/rest/json/cves/2.0
NVD_REQUEST_DELAY=30
MAX_CVE_PER_REQUEST=50
INITIAL_DAYS_BACK=7

# Stockage
USE_SQLITE=false
DB_PATH=/app/data/aggregator.db

# API
USE_API=true
API_URL=http://api:8000

# Logging
LOG_LEVEL=INFO
```

#### 🔄 Workflow

1. **Récupération** : `NVDService.get_recent_cves()` → Requêtes paginées à NVD
2. **Parsing** : Transformation JSON → Objets CVE
3. **Normalisation** : `cvss_severity.upper()`, valeurs valides
4. **Conversion** : CVE → CVEDbRecord
5. **Batch** : Préparation du payload JSON
6. **Envoi** : POST /cves/batch vers API Service
7. **Fallback** : Stockage SQLite si API indisponible

#### 📈 Performances

| Métrique | Valeur |
|----------|--------|
| Requêtes NVD/heure | 10-12 |
| CVEs/jour max | ~8,640 |
| Temps/requête | 2-5s |
| Batch size | 50 CVEs |
| Temps d'insertion | 10-50ms/CVE |

---

### 2️⃣ API Service

**Rôle** : API REST FastAPI pour le stockage et l'exposition des données.

#### 🎯 Fonctionnalités

| Feature | Description | Status |
|---------|-------------|--------|
| CRUD complet | Create, Read, Update, Delete | ✅ |
| Batch import | POST /cves/batch | ✅ |
| Deduplication | UNIQUE constraint + check API | ✅ |
| Validation | Pydantic v2 | ✅ |
| Pagination | Liste paginée | ✅ |
| Filtrage | Severity, score, date, statut | ✅ |
| Statistiques | /cves/stats, /analyses/stats | ✅ |
| Auto-create DB | Création tables au démarrage | ✅ |
| CORS | Accès cross-origin | ✅ |
| **Gestion Tweets** | CRUD complet sur tweets | ✅ |
| **Gestion Analyses** | CRUD complet sur analyses IA | ✅ |

#### 🏗️ Architecture Interne

```
api-service/
├── src/api/
│   ├── config.py              # Configuration centrale
│   ├── main.py                # FastAPI app + startup events
│   ├── db/
│   │   ├── __init__.py
│   │   ├── session.py          # SQLAlchemy session factory
│   │   └── models.py           # SQLAlchemy ORM models
│   ├── models/
│   │   ├── __init__.py
│   │   ├── cve.py              # Pydantic models (CVE + Analyses)
│   │   └── tweet.py            # Pydantic models (Tweets + Accounts)
│   └── routes/
│       ├── __init__.py
│       ├── cves.py             # Routes CVE (11 endpoints)
│       ├── analyses.py         # Routes Analyses (7 endpoints)
│       └── tweets.py           # Routes Tweets + Accounts (10 endpoints)
├── Dockerfile
├── pyproject.toml
└── .env.example
```

#### 🌐 Endpoints API (28 au total)

| Category | Méthode | Endpoint | Description |
|----------|---------|----------|-------------|
| **Health** | GET | `/` | Message de bienvenue |
| **Health** | GET | `/health` | Status de santé |
| **CVE** | GET | `/cves/` | Liste des CVE (paginée) |
| **CVE** | GET | `/cves/{cve_id}` | Détails d'une CVE |
| **CVE** | POST | `/cves/` | Créer une CVE |
| **CVE** | POST | `/cves/batch` | Créer plusieurs CVE (batch) |
| **CVE** | PUT | `/cves/{cve_id}` | Mettre à jour une CVE |
| **CVE** | DELETE | `/cves/{cve_id}` | Supprimer une CVE |
| **CVE** | DELETE | `/cves/?confirm=true` | Supprimer TOUTES les CVE |
| **CVE** | GET | `/cves/stats` | Statistiques des CVE |
| **Analyse** | GET | `/analyses/` | Liste des analyses |
| **Analyse** | GET | `/analyses/{analysis_id}/` | Détails d'une analyse |
| **Analyse** | POST | `/analyses/` | Créer une analyse |
| **Analyse** | PUT | `/analyses/{analysis_id}/` | Mettre à jour une analyse |
| **Analyse** | DELETE | `/analyses/{analysis_id}/` | Supprimer une analyse |
| **Analyse** | DELETE | `/analyses/?confirm=true` | Supprimer TOUTES les analyses |
| **Analyse** | GET | `/analyses/stats/` | Statistiques des analyses |
| **Tweet** | GET | `/tweets/` | Liste des tweets |
| **Tweet** | GET | `/tweets/{tweet_id}` | Détails d'un tweet |
| **Tweet** | POST | `/tweets/` | Créer un tweet |
| **Tweet** | POST | `/tweets/batch` | Créer plusieurs tweets |
| **Tweet** | PUT | `/tweets/{tweet_id}` | Mettre à jour un tweet |
| **Tweet** | DELETE | `/tweets/{tweet_id}` | Supprimer un tweet |
| **Tweet** | DELETE | `/tweets/?confirm=true` | Supprimer TOUS les tweets |
| **Tweet** | GET | `/tweets/stats` | Statistiques des tweets |
| **Account** | GET | `/tweets/accounts/` | Liste des comptes Twitter |
| **Account** | GET | `/tweets/accounts/{username}` | Détails d'un compte |
| **Account** | POST | `/tweets/accounts/` | Créer un compte |
| **Account** | PUT | `/tweets/accounts/{username}` | Mettre à jour un compte |
| **Account** | DELETE | `/tweets/accounts/{username}` | Supprimer un compte |
| **Account** | DELETE | `/tweets/accounts/?confirm=true` | Supprimer TOUS les comptes |

#### 📊 Modèles SQLAlchemy

**Tables PostgreSQL** :

1. **cves** : Vulnérabilités CVE principales
2. **cve_references** : URLs de référence des CVE
3. **cve_analyses** : Analyses IA générées
4. **cve_analysis_mappings** : Relations CVE ↔ Analyse (groupes)
5. **tweets** : Tweets collectés
6. **twitter_accounts** : Comptes Twitter associés

#### 📝 Configuration (.env)

```ini
# PostgreSQL
DB_HOST=postgres
DB_PORT=5432
DB_NAME=cybersec_db
DB_USER=cybersec_user
DB_PASSWORD=cybersec_password
DATABASE_URL=postgresql://cybersec_user:cybersec_password@postgres:5432/cybersec_db

# API
HOST=0.0.0.0
PORT=8000
ALLOW_ORIGINS=*

# Logging
LOG_LEVEL=INFO
```

#### 🚀 Démarrage

```bash
# Avec uvicorn (développement)
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Sans reload (moins de logs)
uvicorn api.main:app --host 0.0.0.0 --port 8000

# Avec Docker
docker-compose -f docker-compose-simple.yml up -d api
```

---

### 3️⃣ AI Service

**Rôle** : Analyse intelligente des vulnérabilités avec Mistral AI.

#### 🎯 Fonctionnalités

| Feature | Description | Status |
|---------|-------------|--------|
| Récupération CVE | GET /cves/ depuis API | ✅ |
| Groupement | Algorithme de similarité (vendor, product, CWE) | ✅ |
| Analyse IA | Mistral pour titres et résumés | ✅ |
| Sévérité globale | Calcul automatique | ✅ |
| Confiance | Score de confiance | ✅ |
| Persistance | POST /analyses/ vers API | ✅ |
| Filtrage temporel | Par nombre de jours | ✅ |

#### 🏗️ Architecture Interne

```
ai-service/
├── src/ai_service/
│   ├── config.py              # Configuration centrale
│   ├── main.py                # CLI entry point + orchestration
│   ├── models/
│   │   ├── __init__.py
│   │   ├── cve.py              # Modèles CVE
│   │   └── analysis.py         # Modèles Analyse
│   ├── services/
│   │   ├── __init__.py
│   │   ├── api_client.py       # Client HTTP pour API Cybersec
│   │   ├── grouping_service.py # Logique de groupement
│   │   ├── analysis_service.py # Orchestration
│   │   └── mistral_service.py  # Intégration Mistral AI
│   └── utils/
│       └── logger.py          # Configuration logging
├── Dockerfile
└── pyproject.toml
```

#### 🔄 Workflow

1. **Récupération** : `APIClient.get_cves(days=N)` → Récupère les CVE depuis l'API
2. **Groupement** : `GroupingService.group_similar_cves()` → Regroupe par vendor/product/CWE
3. **Analyse IA** : `MistralService.generate_analysis()` → Appel à Mistral AI
4. **Calculs** : Sévérité globale, score de confiance
5. **Envoi** : POST /analyses/ vers API Service

#### 📝 Configuration (.env)

```ini
# API Service
API_BASE_URL=http://api:8000
CVES_ENDPOINT=/cves/
ANALYSES_ENDPOINT=/analyses/

# Mistral AI
MISTRAL_API_KEY=ta_clé_api_ici
MISTRAL_MODEL=mistral-tiny

# Groupement
GROUPING_THRESHOLD=0.85

# Logging
LOG_LEVEL=INFO
```

#### 🚀 Commandes CLI

```bash
# Analyse des CVE des 7 derniers jours
python -m ai_service.main --days 7

# Avec seuil de groupement personnalisé
python -m ai_service.main --days 7 --grouping-threshold 0.7

# Mode debug
python -m ai_service.main --days 1 --log-level DEBUG
```

#### 💡 Algorithmes

**Groupement** :
- Critère 1 : Vendor commun
- Critère 2 : Product commun  
- Critère 3 : CWE commun
- Critère 4 : Plage de dates proche
- Seuil : GROUPING_THRESHOLD (défaut : 0.85)

**Sévérité Globale** :
```python
if max_cvss >= 9.0: return "CRITICAL"
elif max_cvss >= 7.0: return "HIGH"
elif max_cvss >= 4.0: return "MEDIUM"
else: return "LOW"
```

**Confiance** :
- Qualité des données : 0-1
- Précision du groupement : 0-1
- Modèle IA : mistral-tiny (0.8), small (0.9), medium (0.95)

---

### 4️⃣ Twitter Service

**Rôle** : Récupération et stockage des tweets liés à la cybersécurité.

#### 🎯 Fonctionnalités

| Feature | Description | Status |
|---------|-------------|--------|
| Recherche par mots-clés | snscrape pour rechercher des tweets | ✅ |
| Recherche par utilisateurs | Récupération des tweets d'utilisateurs spécifiques | ✅ |
| Filtrage temporel | Par nombre de jours | ✅ |
| Filtrage métriques | Likes minimum, retweets minimum | ✅ |
| Batch Processing | Envoi groupé vers API | ✅ |
| Mode Daemon | Exécution périodique | ✅ |
| Détection doublons | tweet_id unique | ✅ |

#### 🏗️ Architecture Interne

```
twitter-service/
├── src/twitter_service/
│   ├── config.py              # Configuration centrale
│   ├── main.py                # CLI entry point
│   ├── models/
│   │   ├── __init__.py
│   │   └── tweet.py            # Modèles Tweet + Account
│   ├── services/
│   │   ├── __init__.py
│   │   ├── api_client.py       # Client HTTP pour API Cybersec
│   │   ├── collector.py        # Orchestrateur principal
│   │   ├── twitter_client.py   # Client snscrape
│   │   └── database.py        # (Optionnel - pour stockage local)
│   └── utils/
│       └── logger.py          # Configuration logging
├── Dockerfile
└── pyproject.toml
```

#### 📊 Modèles de Données

**Tweet** :
- `tweet_id`: str (ID unique Twitter)
- `username`: str
- `user_id`: Optional[str]
- `content`: str
- `date`: datetime
- `url`: str
- **Métriques** : likes, retweets, replies, quotes, views
- **Flags** : is_retweet, is_quote, is_reply
- **Métadonnées** : language, hashtags, mentions, urls, images, videos
- **Catégorisation** : category, severity

**TwitterAccount** :
- `username`: str (unique)
- `user_id`: Optional[str]
- `display_name`: Optional[str]
- `bio`: Optional[str]
- **Stats** : followers_count, following_count, tweet_count
- `account_created_at`: Optional[datetime]
- `verified`: bool
- `avatar_url`: Optional[str]
- `url`: Optional[str]
- `category`: Optional[str]

#### 🚀 Commandes CLI

```bash
# Recherche par mots-clés
python -m twitter_service.main --queries cybersecurity vulnerability malware

# Recherche par utilisateurs
python -m twitter_service.main --usernames user1 user2 user3

# Mode trending (tweets populaires)
python -m twitter_service.main --trending

# Avec filtres
python -m twitter_service.main \
  --queries cybersecurity \
  --days 7 \
  --limit 100 \
  --min-likes 10

# Mode daemon (toutes les 24h)
python -m twitter_service.main \
  --daemon \
  --daemon-interval 24 \
  --queries cybersecurity,malware,infosec

# Test de connexion
python -m twitter_service.main --test

# Lister les tweets
twitter-service/main.py --list-tweets

# Statistiques
twitter-service/main.py --stats
```

#### 📝 Configuration (.env)

```ini
# API Service
API_URL=http://api:8000
API_BASE_URL=http://api:8000

# Recherche
SEARCH_QUERIES=cybersecurity,vulnerability,infosec,CVE,malware,hacking,exploit,zero-day
SEARCH_DAYS_BACK=7
MAX_TWEETS_PER_REQUEST=50
REQUEST_DELAY=5
MIN_LIKES=0
MIN_RETWEETS=0
LANGUAGE=en

# Daemon
DAEMON_INTERVAL_HOURS=24

# Logging
LOG_LEVEL=INFO
```

#### 🔄 Workflow

1. **Recherche** : `TwitterClient.get_tweets_by_query()` → snscrape
2. **Filtrage** : Par date, likes, retweets
3. **Parsing** : Extraction des métadonnées (hashtags, mentions, etc.)
4. **Batch** : Préparation du payload JSON
5. **Envoi** : POST /tweets/batch vers API Service
6. **Création comptes** : POST /tweets/accounts/ pour les nouveaux utilisateurs

---

## 🗃️ Base de Données

### 📊 Schéma PostgreSQL

```sql
-- Table 1: cves (Vulnérabilités)
CREATE TABLE cves (
    id SERIAL PRIMARY KEY,
    cve_id VARCHAR(50) NOT NULL UNIQUE,
    published_at TIMESTAMP WITH TIME ZONE NOT NULL,
    last_modified TIMESTAMP WITH TIME ZONE NOT NULL,
    description TEXT,
    cvss_score NUMERIC(3, 1),
    cvss_severity VARCHAR(20),
    vector TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table 2: cve_references (Références)
CREATE TABLE cve_references (
    id SERIAL PRIMARY KEY,
    cve_id INTEGER NOT NULL REFERENCES cves(id),
    url TEXT NOT NULL
);

-- Table 3: cve_analyses (Analyses IA)
CREATE TABLE cve_analyses (
    id SERIAL PRIMARY KEY,
    analysis_id VARCHAR(50) NOT NULL UNIQUE,
    title VARCHAR(500) NOT NULL,
    summary TEXT NOT NULL,
    severity_overall VARCHAR(20),
    confidence NUMERIC(3, 2),
    extra_data JSON,
    status VARCHAR(20) DEFAULT 'completed',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table 4: cve_analysis_mappings (Mappings)
CREATE TABLE cve_analysis_mappings (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER NOT NULL REFERENCES cve_analyses(id),
    cve_id INTEGER NOT NULL REFERENCES cves(id),
    group_id VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table 5: tweets
CREATE TABLE tweets (
    id SERIAL PRIMARY KEY,
    tweet_id VARCHAR(50) NOT NULL UNIQUE,
    account_id INTEGER REFERENCES twitter_accounts(id),
    username VARCHAR(50) NOT NULL,
    user_id VARCHAR(50),
    content TEXT NOT NULL,
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    url TEXT NOT NULL,
    likes INTEGER DEFAULT 0,
    retweets INTEGER DEFAULT 0,
    replies INTEGER DEFAULT 0,
    quotes INTEGER DEFAULT 0,
    views INTEGER,
    is_retweet BOOLEAN DEFAULT FALSE,
    is_quote BOOLEAN DEFAULT FALSE,
    is_reply BOOLEAN DEFAULT FALSE,
    language VARCHAR(20),
    hashtags JSON,
    mentions JSON,
    urls JSON,
    images JSON,
    videos JSON,
    category VARCHAR(100),
    severity VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table 6: twitter_accounts
CREATE TABLE twitter_accounts (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    user_id VARCHAR(50),
    display_name VARCHAR(200),
    bio TEXT,
    followers_count INTEGER,
    following_count INTEGER,
    tweet_count INTEGER,
    account_created_at TIMESTAMP WITH TIME ZONE,
    verified BOOLEAN DEFAULT FALSE,
    avatar_url VARCHAR(500),
    url VARCHAR(500),
    category VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 🔍 Index

```sql
-- CVE
CREATE INDEX idx_cves_cve_id ON cves(cve_id);
CREATE INDEX idx_cves_published ON cves(published_at);
CREATE INDEX idx_cves_severity ON cves(cvss_severity);
CREATE INDEX idx_cves_score ON cves(cvss_score);

-- References
CREATE INDEX idx_cve_references_cve_id ON cve_references(cve_id);

-- Analyses
CREATE INDEX idx_cve_analyses_analysis_id ON cve_analyses(analysis_id);
CREATE INDEX idx_cve_analyses_severity ON cve_analyses(severity_overall);

-- Mappings
CREATE INDEX idx_cve_analysis_mappings_analysis_id ON cve_analysis_mappings(analysis_id);
CREATE INDEX idx_cve_analysis_mappings_cve_id ON cve_analysis_mappings(cve_id);

-- Tweets
CREATE INDEX idx_tweets_tweet_id ON tweets(tweet_id);
CREATE INDEX idx_tweets_username ON tweets(username);
CREATE INDEX idx_tweets_date ON tweets(date);
CREATE INDEX idx_tweets_category ON tweets(category);

-- Accounts
CREATE INDEX idx_twitter_accounts_username ON twitter_accounts(username);
```

### 📈 Requêtes Utiles

```sql
-- Compter les CVE par sévérité
SELECT cvss_severity, COUNT(*) as count
FROM cves
GROUP BY cvss_severity
ORDER BY 
    CASE cvss_severity 
        WHEN 'CRITICAL' THEN 1 
        WHEN 'HIGH' THEN 2 
        WHEN 'MEDIUM' THEN 3 
        WHEN 'LOW' THEN 4 
        ELSE 5 
    END;

-- Top 10 CVE les plus critiques
SELECT cve_id, cvss_score, cvss_severity, description
FROM cves
WHERE cvss_score IS NOT NULL
ORDER BY cvss_score DESC
LIMIT 10;

-- CVE récentes (7 derniers jours)
SELECT * FROM cves
WHERE published_at >= NOW() - INTERVAL '7 days'
ORDER BY published_at DESC;

-- Tweets populaires (>100 likes)
SELECT t.*, ta.display_name
FROM tweets t
JOIN twitter_accounts ta ON t.account_id = ta.id
WHERE t.likes > 100
ORDER BY t.likes DESC
LIMIT 20;

-- Compte Twitter avec plus d'abonnés
SELECT username, display_name, followers_count
FROM twitter_accounts
WHERE followers_count IS NOT NULL
ORDER BY followers_count DESC
LIMIT 10;

-- Analyses récentes
SELECT a.analysis_id, a.title, a.severity_overall, a.confidence
FROM cve_analyses a
ORDER BY a.created_at DESC
LIMIT 10;
```

---

## 🚀 Déploiement

### 📁 Structure des Fichiers

```
cybersec-platform/
├── docker-compose.yml          # Orchestration complète (4 services)
├── docker-compose-simple.yml   # PostgreSQL + API uniquement
├── .env                        # Variables globales (optionnel)
├── README.md                   # Documentation principale
├── QUICKSTART.md              # Guide de démarrage rapide
│
├── aggregator-service/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── .env.example
│   └── src/cybersec_aggregator/
│
├── api-service/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── .env.example
│   └── src/api/
│
├── twitter-service/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── .env.example
│   └── src/twitter_service/
│
└── ai-service/ (dans notes, à créer)
    ├── Dockerfile
    ├── pyproject.toml
    ├── .env.example
    └── src/ai_service/
```

### 🐳 Docker Compose

#### docker-compose.yml (Complet)

Lance **PostgreSQL + API + Aggregator + Twitter** :

```bash
# Builder et lancer tous les services
docker-compose build
docker-compose up -d

# Vérifier
docker-compose ps

# Voir les logs
docker-compose logs -f

# Arrêter
docker-compose down

# Arrêter avec suppression des volumes
docker-compose down -v
```

#### docker-compose-simple.yml (API + PostgreSQL)

Pour tester **seulement l'API** :

```bash
# Lancer PostgreSQL + API
docker-compose -f docker-compose-simple.yml up -d

# Tester
curl http://localhost:8000/health
```

### 🔧 Configuration par Environnement

#### Développement

```bash
# .env.development
POSTGRES_DB=cybersec_db_dev
POSTGRES_USER=dev_user
POSTGRES_PASSWORD=dev_password
LOG_LEVEL=DEBUG
```

#### Production

```bash
# .env.production
POSTGRES_DB=cybersec_db_prod
POSTGRES_USER=prod_user
POSTGRES_PASSWORD=strong_password_here
LOG_LEVEL=WARNING
ALLOW_ORIGINS=https://cybersec.example.com
NVD_REQUEST_DELAY=30
```

### 📊 Variables d'Environnement par Service

**Global (.env à la racine)** :
```ini
POSTGRES_DB=cybersec_db
POSTGRES_USER=cybersec_user
POSTGRES_PASSWORD=cybersec_password
```

**API Service** :
```ini
DB_HOST=postgres
DB_PORT=5432
DATABASE_URL=postgresql://cybersec_user:cybersec_password@postgres:5432/cybersec_db
HOST=0.0.0.0
PORT=8000
ALLOW_ORIGINS=*
LOG_LEVEL=INFO
```

**Aggregator Service** :
```ini
NVD_API_URL=https://services.nvd.nist.gov/rest/json/cves/2.0
USE_API=true
API_URL=http://api:8000
USE_SQLITE=false
NVD_REQUEST_DELAY=30
MAX_CVE_PER_REQUEST=50
INITIAL_DAYS_BACK=7
LOG_LEVEL=INFO
```

**Twitter Service** :
```ini
API_URL=http://api:8000
API_BASE_URL=http://api:8000
SEARCH_QUERIES=cybersecurity,vulnerability,infosec,CVE,malware,hacking,exploit,zero-day
SEARCH_DAYS_BACK=7
MAX_TWEETS_PER_REQUEST=50
REQUEST_DELAY=5
MIN_LIKES=0
MIN_RETWEETS=0
LANGUAGE=en
DAEMON_INTERVAL_HOURS=24
LOG_LEVEL=INFO
```

---

## 📊 Flux de Données

### 🔄 Flux Principal (CVE)

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│   NVD API       │────▶│  Aggregator     │────▶│   API Service   │
│  (External)     │     │   Service       │     │  (FastAPI)       │
│  5 req/30s      │     │                 │     │                 │
└─────────────────┘     └──────────┬──────┘     └──────────┬──────┘
                                    │                      │
                                    ▼                      ▼
                            ┌─────────────────────────────────────────────┐
                            │            PostgreSQL                         │
                            │   - cves table                               │
                            │   - cve_references table                     │
                            │                                             │
                            └─────────────────────────────────────────────┘
                                    ▲
                                    │
                            ┌─────────────────┐
                            │                 │
                            │   AI Service    │
                            │  (Mistral AI)   │
                            │                 │
                            └──────────┬──────┘
                                       │
                                       ▼
                            ┌─────────────────┐
                            │  /analyses/      │
                            │  endpoint        │
                            └─────────────────┘
```

**Étapes détaillées** :

1. **Aggregator** → Interroge NVD API toutes les N heures (respectant rate limit)
2. **Aggregator** → Parse les CVE JSON, filtre les doublons locaux
3. **Aggregator** → Normalise cvss_severity, prépare batch JSON
4. **Aggregator** → Envoie les nouvelles CVE à l'API via **POST /cves/batch**
5. **API Service** → Valide les données avec Pydantic v2
6. **API Service** → Vérifie les doublons (SELECT COUNT WHERE cve_id = ?)
7. **API Service** → Insère en PostgreSQL (INSERT cves + cve_references)
8. **AI Service** → Récupère les CVE via **GET /cves/?days=N**
9. **AI Service** → Groupe les CVE par vendor, product, CWE
10. **AI Service** → Appelle Mistral AI pour titres et résumés
11. **AI Service** → Calcule sévérité globale et confiance
12. **AI Service** → Envoie l'analyse via **POST /analyses/**
13. **API Service** → Stocke l'analyse (INSERT cve_analyses + mappings)

### 🔄 Flux Twitter

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  X (Twitter)    │────▶│ Twitter Service  │────▶│   API Service   │
│  (snscrape)     │     │                 │     │                 │
│                 │     │                 │     │                 │
└─────────────────┘     └──────────┬──────┘     └──────────┬──────┘
                                    │                      │
                                    ▼                      ▼
                            ┌─────────────────────────────────────────────┐
                            │            PostgreSQL                         │
                            │   - tweets table                              │
                            │   - twitter_accounts table                    │
                            │                                             │
                            └─────────────────────────────────────────────┘
```

**Étapes détaillées** :

1. **Twitter Service** → Recherche tweets via snscrape (par query ou username)
2. **Twitter Service** → Parse les tweets, extrait métadonnées
3. **Twitter Service** → Crée les comptes Twitter manquants via **POST /tweets/accounts/**
4. **Twitter Service** → Envoie les tweets via **POST /tweets/batch**
5. **API Service** → Valide et stocke en PostgreSQL

---

## 🔧 Configuration

### 📝 Fichiers de Configuration

#### pyproject.toml (API Service)

```toml
[project]
name = "api-service"
version = "0.2.0"
description = "API FastAPI pour le projet Cybersec"
requires-python = ">=3.10"
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "sqlalchemy>=2.0.23",
    "psycopg2-binary>=2.9.9",
    "pydantic>=2.5.0",
    "python-dotenv>=1.0.0",
    "alembic>=1.13.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

#### .env.example (API Service)

```ini
# PostgreSQL
DB_HOST=postgres
DB_PORT=5432
DB_NAME=cybersec_db
DB_USER=cybersec_user
DB_PASSWORD=cybersec_password
DATABASE_URL=postgresql://cybersec_user:cybersec_password@postgres:5432/cybersec_db

# API
HOST=0.0.0.0
PORT=8000
ALLOW_ORIGINS=*

# Logging
LOG_LEVEL=INFO
```

### 🎛️ Configuration par Variable

| Service | Variable | Défaut | Description |
|---------|----------|--------|-------------|
| **All** | LOG_LEVEL | INFO | Niveau de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| **PostgreSQL** | POSTGRES_DB | cybersec_db | Nom de la base |
| **PostgreSQL** | POSTGRES_USER | cybersec_user | Utilisateur |
| **PostgreSQL** | POSTGRES_PASSWORD | cybersec_password | Mot de passe |
| **API** | DB_HOST | postgres | Hôte PostgreSQL |
| **API** | DB_PORT | 5432 | Port PostgreSQL |
| **API** | HOST | 0.0.0.0 | Host API |
| **API** | PORT | 8000 | Port API |
| **API** | ALLOW_ORIGINS | * | CORS origins |
| **Aggregator** | NVD_API_URL | https://... | URL API NVD |
| **Aggregator** | USE_API | true | Envoyer à l'API |
| **Aggregator** | API_URL | http://api:8000 | URL de l'API |
| **Aggregator** | USE_SQLITE | false | Utiliser SQLite |
| **Aggregator** | NVD_REQUEST_DELAY | 30 | Délai entre requêtes (s) |
| **Aggregator** | MAX_CVE_PER_REQUEST | 50 | Max CVEs par requête |
| **Aggregator** | INITIAL_DAYS_BACK | 7 | Jours à remonter |
| **Twitter** | API_URL | http://api:8000 | URL de l'API |
| **Twitter** | SEARCH_QUERIES | cybersecurity,... | Requêtes de recherche |
| **Twitter** | SEARCH_DAYS_BACK | 7 | Jours à remonter |
| **Twitter** | MAX_TWEETS_PER_REQUEST | 50 | Max tweets par requête |
| **AI** | API_BASE_URL | http://api:8000 | URL de l'API |
| **AI** | MISTRAL_API_KEY | - | Clé API Mistral |
| **AI** | MISTRAL_MODEL | mistral-tiny | Modèle Mistral |
| **AI** | GROUPING_THRESHOLD | 0.85 | Seuil de groupement |

---

## 🛠️ Dépannage

### ❌ Problèmes Courants et Solutions

#### Problèmes PostgreSQL

| Problème | Symptôme | Solution |
|----------|----------|----------|
| **Connection refused** | `could not connect to server` | `docker-compose up -d postgres` |
| **Authentication failed** | `password authentication failed` | Vérifier POSTGRES_PASSWORD |
| **Database does not exist** | `database "cybersec_db" does not exist` | Vérifier POSTGRES_DB |
| **Port 5432 occupé** | `Address already in use` | `lsof -i :5432` puis `kill -9 PID` |
| **Tables non créées** | `relation "cves" does not exist` | L'API crée les tables au démarrage |

**Commandes utiles** :
```bash
# Vérifier PostgreSQL
docker-compose exec postgres psql -U cybersec_user -d cybersec_db

# Voir les tables
\dt

# Compter les CVE
SELECT COUNT(*) FROM cves;

# Vérifier la connexion
psql -h localhost -U cybersec_user -d cybersec_db -c "SELECT 1;"
```

#### Problèmes API Service

| Problème | Symptôme | Solution |
|----------|----------|----------|
| **Port 8000 occupé** | `Address already in use` | `lsof -i :8000` puis `kill -9 PID` |
| **watchfiles spam** | Logs excessifs | Lancer sans `--reload` ou baisser log level |
| **Pydantic error** | `ValidationError` | Vérifier le schéma des données envoyées |
| **Module not found** | `ModuleNotFoundError` | `uv sync` ou `pip install -e .` |
| **Connection to DB** | `connection refused` | Vérifier DB_HOST, DB_PORT |

**Commandes utiles** :
```bash
# Tester l'API
curl http://localhost:8000/health

# Voir les logs
tail -f api-service/logs/api.log

# Tester la connexion DB
docker-compose exec api python -c "from api.db.session import engine; print(engine)"
```

#### Problèmes Aggregator Service

| Problème | Symptôme | Solution |
|----------|----------|----------|
| **Rate limit dépassé** | `429 Too Many Requests` | Augmenter NVD_REQUEST_DELAY |
| **API non disponible** | `Connection refused` | Lancer l'API d'abord |
| **Aucune CVE trouvée** | `0 CVE found` | Augmenter --days ou vérifier la date |
| **Erreur 500 API** | `500 Internal Server Error` | Vérifier le format des données (cvss_severity doit être majuscule) |

**Commandes utiles** :
```bash
# Tester NVD API
curl "https://services.nvd.nist.gov/rest/json/cves/2.0?pubStartDate=2024-01-01T00:00:00&resultsPerPage=5"

# Tester l'envoi à l'API
curl -X POST http://localhost:8000/cves/batch \
  -H "Content-Type: application/json" \
  -d '[{"cve_id": "CVE-TEST-001", "published_at": "2024-01-01T00:00:00", "last_modified": "2024-01-01T00:00:00", "description": "Test"}]'

# Voir les logs
tail -f aggregator-service/logs/aggregator.log
```

#### Problèmes Twitter Service

| Problème | Symptôme | Solution |
|----------|----------|----------|
| **snscrape échoue** | `ModuleNotFoundError: snscrape` | `pip install snscrape` |
| **API non disponible** | `Connection refused` | Lancer l'API d'abord |
| **Aucun tweet trouvé** | `0 tweets found` | Vérifier les queries ou --days |
| **Erreur de parsing** | `AttributeError` | Vérifier le format des tweets |

**Commandes utiles** :
```bash
# Tester snscrape
python -c "import snscrape.modules.twitter; print('OK')"

# Tester la recherche
docker-compose run twitter python -m twitter_service.main --queries cybersecurity --limit 5

# Vérifier l'API
docker-compose exec api python -c "import requests; r = requests.get('http://localhost:8000/health'); print(r.json())"
```

#### Problèmes AI Service

| Problème | Symptôme | Solution |
|----------|----------|----------|
| **Mistral API key** | `AuthenticationError` | Vérifier MISTRAL_API_KEY |
| **API non disponible** | `Connection refused` | Lancer l'API d'abord |
| **Aucune CVE à analyser** | `0 CVE found` | Vérifier que l'Aggregator a bien envoyé des données |
| **Erreur de groupement** | `AttributeError` | Mettre à jour api-service |

**Commandes utiles** :
```bash
# Tester Mistral API
curl https://api.mistral.ai/v1/chat/completions \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "mistral-tiny", "messages": [{"role": "user", "content": "Hello"}]}'

# Tester l'AI Service
python -m ai_service.main --days 1 --log-level DEBUG
```

---

## 📚 Références

### 🔗 Liens Utiles

- [NVD API Documentation](https://nvd.nist.gov/developers/requests)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/14/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [Mistral AI API](https://docs.mistral.ai/)
- [snscrape Documentation](https://haccer.github.io/snscrape/)

### 📖 Documentation Interne

- [README.md](./README.md) - Documentation principale
- [QUICKSTART.md](./QUICKSTART.md) - Guide de démarrage rapide
- [Aggregator Service README](./aggregator-service/README.md)
- [API Service README](./api-service/README.md)

### 🎯 Prochaines Étapes

#### À Court Terme
- [ ] Déployer en production (Docker Swarm/Kubernetes)
- [ ] Ajouter authentication JWT à l'API
- [ ] Configurer des notifications (Discord/Telegram)
- [ ] Créer un dashboard frontal (React/Vue)
- [ ] Automatiser les collectes avec cron

#### Moyen Terme
- [ ] Ajouter d'autres sources de CVE (CIRCL, VulnDB)
- [ ] Intégrer un système de cache (Redis)
- [ ] Ajouter un système de retry avec backoff
- [ ] Implémenter le rate limiting sur l'API
- [ ] Ajouter des métriques (Prometheus)

#### Long Terme
- [ ] Support multi-tenancy
- [ ] Recherche full-text avec Elasticsearch
- [ ] GraphQL endpoint
- [ ] Webhooks pour notifications temps réel
- [ ] Système de recommandation proactive

---

## 📜 Metadata

| Propriété | Valeur |
|-----------|--------|
| **Projet** | Cybersec Platform |
| **Version** | 0.2.0 |
| **Auteur** | loocist |
| **Langage** | Python 3.12 |
| **Framework** | FastAPI, SQLAlchemy, Pydantic |
| **Base de données** | PostgreSQL 15 |
| **Orchestration** | Docker Compose |
| **Créé** | Mai 2026 |
| **Dernière mise à jour** | 6 juin 2026 |

---

*© 2026 Cybersec Platform - Tous droits réservés*
