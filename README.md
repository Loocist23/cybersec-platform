# 🛡️ Cybersec Platform

> **Plateforme microservice pour la veille en cybersécurité**

Une architecture microservice modulaire pour agréger, stocker, analyser et intelligemment regrouper les vulnérabilités CVE.

---

## 📁 Architecture

```
cybersec-platform/
├── docker-compose.yml          # Orchestration Docker
├── docker-compose-simple.yml  # PostgreSQL + API uniquement
├── .env                        # Configuration globale
├── .gitignore
├── QUICKSTART.md               # Guide de démarrage rapide
├── aggregator-service/        # Microservice : Récupération des CVE
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── src/
│   └── .env.example
├── api-service/               # Microservice : API + PostgreSQL
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── src/
│   └── .env.example
└── ai-service/                # Microservice : Analyse IA des CVE
    ├── Dockerfile
    ├── pyproject.toml
    ├── src/
    └── .env.example
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| **aggregator-service** | - | Récupère les CVE depuis l'API NVD |
| **api-service** | 8000 | API FastAPI avec PostgreSQL |
| **ai-service** | 8001 | Service d'analyse IA (groupement, classification) |
| **postgres** | 5432 | Base de données PostgreSQL |

---

## 🚀 Démarrage rapide

### 1. Cloner le projet
```bash
cd /home/loocist/PycharmProjects
# Le projet est dans cybersec-platform/
```

### 2. Lancer PostgreSQL
```bash
cd cybersec-platform

# Méthode 1: PostgreSQL seul (pour le développement)
docker-compose -f docker-compose-simple.yml up -d postgres

# Méthode 2: Tout lancer (PostgreSQL + API + Aggregator)
docker-compose up -d
```

### 3. Lancer l'API
```bash
# Si vous utilisez docker-compose-simple.yml
docker-compose -f docker-compose-simple.yml up -d api

# Sinon, manuellement avec uv
cd api-service
source .venv/bin/activate
python -m api.main
```

### 4. Collecter les CVE
```bash
# Avec Docker
cd cybersec-platform
docker-compose run aggregator python -m cybersec_aggregator.main --days 7 --send-to-api

# Manuellement
cd aggregator-service
source .venv/bin/activate
python -m cybersec_aggregator.main --days 7 --send-to-api
```

### 5. Lancer l'analyse IA
```bash
# Avec Docker
cd cybersec-platform
docker-compose run ai-service python -m ai_service.main

# Manuellement
cd ai-service
source .venv/bin/activate
python -m ai_service.main
```

### 6. Tester l'API
```bash
# Health check
curl http://localhost:8000/
curl http://localhost:8000/health

# Lister les CVE
curl http://localhost:8000/cves/

# Lister les analyses
curl http://localhost:8000/analyses/

# Documentation Swagger
# Ouvrir http://localhost:8000/docs dans le navigateur
```

---

## 🏗️ Services détaillés

### Aggregator Service

**Rôle** : Récupère automatiquement les vulnérabilités CVE depuis la [NVD](https://nvd.nist.gov/).

**Fonctionnalités** :
- Récupération périodique des CVE
- Filtrage par date, score CVSS, sévérité
- Envoi des données à l'API Service via POST /cves/batch
- Stockage local en SQLite (optionnel, fallback)
- Respect du rate limiting (5 req/30s)
- Détection automatique des doublons

**Configuration** :
```bash
# Variables d'environnement (dans aggregator-service/.env)
NVD_API_URL=https://services.nvd.nist.gov/rest/json/cves/2.0
USE_API=true          # Envoyer à l'API au lieu de SQLite
API_URL=http://api:8000  # URL de l'API Service
USE_SQLITE=false      # Désactiver SQLite
INITIAL_DAYS_BACK=7   # Jours à remonter
NVD_REQUEST_DELAY=30  # Délai entre les requêtes (secondes)
LOG_LEVEL=INFO
MAX_CVE_PER_REQUEST=50
```

**Commandes** :
```bash
# Récupérer les CVE des 7 derniers jours
python -m cybersec_aggregator.main --days 7

# Récupérer uniquement les CVE critiques
python -m cybersec_aggregator.main --days 7 --critical-only

# Envoyer à l'API (nécessite --send-to-api)
python -m cybersec_aggregator.main --days 7 --send-to-api

# Avec API URL personnalisée
python -m cybersec_aggregator.main --days 7 --send-to-api --api-url http://localhost:8000

# Mode debug
python -m cybersec_aggregator.main --days 1 --send-to-api --log-level DEBUG
```

### API Service

**Rôle** : API REST pour gérer les CVE et les analyses stockées en PostgreSQL.

**Fonctionnalités** :
- CRUD complet sur les CVE
- CRUD complet sur les analyses IA
- Recherche et filtrage avancés
- Statistiques et analytics
- Documentation OpenAPI (Swagger/ReDoc)
- Validation automatique des données
- Détection des doublons (UNIQUE constraint sur cve_id)

**Endpoints CVE** :
```
GET  /cves/           # Lister les CVE (avec pagination)
GET  /cves/{cve_id}  # Récupérer une CVE spécifique
POST /cves/          # Créer une CVE
POST /cves/batch     # Créer plusieurs CVE
GET  /cves/stats     # Statistiques des CVE
PUT  /cves/{cve_id}  # Mettre à jour une CVE
DEL  /cves/{cve_id}  # Supprimer une CVE
```

**Endpoints Analyses** :
```
GET  /analyses/              # Lister les analyses (avec pagination)
GET  /analyses/{id}/         # Récupérer une analyse spécifique
POST /analyses/              # Créer une analyse
GET  /analyses/stats/        # Statistiques des analyses
PUT  /analyses/{id}/         # Mettre à jour une analyse
DEL  /analyses/{id}/         # Supprimer une analyse
DEL  /analyses/              # Supprimer toutes les analyses
```

**Configuration** :
```bash
# Variables d'environnement (dans api-service/.env)
DB_HOST=postgres
DB_PORT=5432
DB_NAME=cybersec_db
DB_USER=cybersec_user
DB_PASSWORD=cybersec_password
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
ALLOW_ORIGINS=*
```

### AI Service

**Rôle** : Service d'analyse intelligente des CVE avec IA (Mistral).

**Fonctionnalités** :
- Récupération des CVE depuis l'API Service
- Groupement intelligent des CVE similaires
- Génération de titres et résumés avec l'IA
- Classification par sévérité globale
- Calcul de score de confiance
- Envoi des analyses à l'API Service

**Configuration** :
```bash
# Variables d'environnement (dans ai-service/.env)
API_BASE_URL=http://localhost:8000
CVES_ENDPOINT=/cves/
ANALYSES_ENDPOINT=/analyses/
MISTRAL_API_KEY=votre_clef_api_mistral
MISTRAL_MODEL=mistral-tiny  # ou mistral-small, mistral-medium
GROUPING_THRESHOLD=0.85     # Seuil de similarité pour le groupement
LOG_LEVEL=INFO
```

**Commandes** :
```bash
# Lancer une analyse complète
python -m ai_service.main

# Analyser les CVE des 7 derniers jours
python -m ai_service.main --days 7

# Avec un modèle spécifique
python -m ai_service.main --model mistral-small

# Mode debug
python -m ai_service.main --days 1 --log-level DEBUG
```

### PostgreSQL

**Rôle** : Base de données relationnelle pour stocker les CVE et les analyses.

**Configuration** :
```bash
# Variables d'environnement (dans .env parent)
POSTGRES_DB=cybersec_db
POSTGRES_USER=cybersec_user
POSTGRES_PASSWORD=cybersec_password
```

**Structure de la base** :
- Table `cves` : Stockage des vulnérabilités CVE
- Table `cve_references` : URLs de référence des CVE
- Table `cve_analyses` : Analyses IA générées
- Table `cve_analysis_mappings` : Relation entre analyses et CVEs

---

## 📊 Flux de données

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │     │                 │
│   NVD API       │────▶│  Aggregator     │────▶│   API Service   │◀────│   AI Service     │
│  (External)     │     │   Service       │     │  (FastAPI)       │     │                 │
│                 │     │                 │     │                 │     │                 │
└─────────────────┘     └──────────┬──────┘     └──────────┬──────┘     └──────────┬──────┘
                                    │                      │                   │
                                    ▼                      ▼                   ▼
                            ┌─────────────────────────────────────────────┐
                            │                                             │
                            │            PostgreSQL                         │
                            │   - cves table                               │
                            │   - cve_references table                     │
                            │   - cve_analyses table                       │
                            │   - cve_analysis_mappings table              │
                            │                                             │
                            └─────────────────────────────────────────────┘
```

**Étapes** :

1. **Aggregator** → Interroge l'API NVD toutes les N heures (respectant le rate limit)
2. **Aggregator** → Parse les CVE et les envoie à l'API via POST /cves/batch
3. **API Service** → Valide les données et les stocke en PostgreSQL
4. **AI Service** → Récupère les CVE via GET /cves/ et les analyse
5. **AI Service** → Groupe les CVE similaires, génère des résumés avec l'IA
6. **AI Service** → Envoie les analyses à l'API via POST /analyses/
7. **API Service** → Stocke les analyses en PostgreSQL

---

## 🔧 Développement local

### Prérequis

- Python 3.12+
- PostgreSQL 15+
- Docker et Docker Compose
- uv (pour la gestion des dépendances) - optionnel

### Installation avec uv (recommandé)

```bash
# Installer uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Dans chaque service
cd aggregator-service
uv pip install -e .

cd ../api-service
uv pip install -e .

cd ../ai-service
uv pip install -e .
```

### Sans Docker

#### PostgreSQL
```bash
# Avec Docker (recommandé pour le développement)
docker run -d --name postgres -e POSTGRES_PASSWORD=cybersec_password -p 5432:5432 postgres:15

# Ou installer PostgreSQL localement
sudo apt install postgresql postgresql-contrib
sudo -u postgres createuser cybersec_user
sudo -u postgres createdb cybersec_db -O cybersec_user
```

#### API Service
```bash
cd api-service
source .venv/bin/activate

# Configurer la base de données
cp .env.example .env
nano .env  # Vérifier DB_HOST, DB_USER, DB_PASSWORD

# Créer les tables (automatique au démarrage)
python -m api.main

# L'API est disponible sur http://localhost:8000
```

#### Aggregator Service
```bash
cd aggregator-service
source .venv/bin/activate

cp .env.example .env
nano .env  # Configurer API_URL=http://localhost:8000

# Tester la collecte
python -m cybersec_aggregator.main --days 1 --send-to-api
```

#### AI Service
```bash
cd ai-service
source .venv/bin/activate

cp .env.example .env
nano .env  # Configurer API_BASE_URL et MISTRAL_API_KEY

# Lancer une analyse
python -m ai_service.main --days 1
```

---

## 🐳 Docker

### Construire les images
```bash
# Construire tous les services
docker-compose build

# Construire un service spécifique
docker-compose build api
docker-compose build aggregator
docker-compose build ai-service
```

### Lancer les services
```bash
# Lancer uniquement PostgreSQL
docker-compose -f docker-compose-simple.yml up -d postgres

# Lancer PostgreSQL + API
docker-compose -f docker-compose-simple.yml up -d

# Lancer tous les services (PostgreSQL + API + Aggregator)
docker-compose up -d
```

### Commandes utiles
```bash
# Voir les logs de tous les services
docker-compose logs -f

# Voir les logs d'un service spécifique
docker-compose logs -f api
docker-compose logs -f aggregator
docker-compose logs -f ai-service

# Arrêter tous les services
docker-compose down

# Arrêter et supprimer les volumes
docker-compose down -v
```

### Exécuter des commandes dans un conteneur
```bash
# Lancer une collecte manuelle
docker-compose run aggregator python -m cybersec_aggregator.main --days 7 --send-to-api

# Lancer une analyse IA
docker-compose run ai-service python -m ai_service.main --days 7

# Accéder à PostgreSQL
docker-compose exec postgres psql -U cybersec_user -d cybersec_db

# Accéder à l'API
docker-compose exec api bash
```

---

## 🧪 Tests

### Tester l'API avec curl

#### Endpoints CVE
```bash
# Health check
curl http://localhost:8000/
curl http://localhost:8000/health

# Lister les CVE
curl http://localhost:8000/cves/

# Filtrer par sévérité
curl "http://localhost:8000/cves/?severity=CRITICAL"

# Filtrer par score minimum
curl "http://localhost:8000/cves/?min_score=7.0"

# Filtrer par nombre de jours
curl "http://localhost:8000/cves/?days=7"

# Statistiques
curl http://localhost:8000/cves/stats

# Créer une CVE (POST)
curl -X POST http://localhost:8000/cves/ \
  -H "Content-Type: application/json" \
  -d '{
    "cve_id": "CVE-2024-1234",
    "published_at": "2024-01-15T10:00:00",
    "last_modified": "2024-01-15T10:00:00",
    "description": "Test vulnerability",
    "cvss_score": 9.8,
    "cvss_severity": "CRITICAL",
    "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
    "references": ["https://example.com"]
  }'

# Créer plusieurs CVE (batch)
curl -X POST http://localhost:8000/cves/batch \
  -H "Content-Type: application/json" \
  -d '[{"cve_id": "CVE-2024-1235", "published_at": "2024-01-16T10:00:00", "last_modified": "2024-01-16T10:00:00", "description": "Test 2", "cvss_score": 7.5, "cvss_severity": "HIGH"}]'
```

#### Endpoints Analyses
```bash
# Lister les analyses
curl http://localhost:8000/analyses/

# Filtrer les analyses par statut
curl "http://localhost:8000/analyses/?status_filter=completed"

# Filtrer par sévérité
curl "http://localhost:8000/analyses/?severity=HIGH"

# Statistiques des analyses
curl http://localhost:8000/analyses/stats

# Créer une analyse (exemple de structure)
curl -X POST http://localhost:8000/analyses/ \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_id": "analysis-20240523-001",
    "title": "Analyse des vulnérabilités critiques",
    "summary": "15 vulnérabilités critiques détectées dans les produits Apache",
    "severity_overall": "CRITICAL",
    "confidence": 0.95,
    "status": "completed",
    "extra_data": {"model": "mistral-tiny", "tokens_used": 5000},
    "grouped_cves": [
      {
        "group_id": "apache-group-1",
        "cve_ids": ["CVE-2024-1234", "CVE-2024-5678"],
        "common_vendor": "Apache",
        "common_product": "Apache Tomcat",
        "common_cwe": ["CWE-20"],
        "similarity_score": 0.92,
        "total_cves": 2,
        "avg_cvss_score": 9.5,
        "max_cvss_score": 9.8
      }
    ]
  }'
```

---

## 📁 Structure des fichiers

### Aggregator Service
```
aggregator-service/
├── Dockerfile
├── pyproject.toml
├── .env.example
├── .gitignore
├── README.md
└── src/
    └── cybersec_aggregator/
        ├── __init__.py
        ├── config.py          # Configuration centrale
        ├── main.py           # Point d'entrée CLI
        ├── models/
        │   ├── __init__.py
        │   └── cve.py         # Modèles Pydantic
        ├── services/
        │   ├── __init__.py
        │   ├── collector.py   # Orchestration
        │   ├── database.py    # SQLite fallback
        │   └── nvd.py         # Client API NVD
        └── utils/
            ├── __init__.py
            └── logger.py       # Configuration des logs
```

### API Service
```
api-service/
├── Dockerfile
├── pyproject.toml
├── .env.example
├── .gitignore
├── README.md
└── src/
    └── api/
        ├── __init__.py
        ├── config.py          # Configuration
        ├── main.py           # Application FastAPI
        ├── db/
        │   ├── __init__.py
        │   ├── models.py      # Modèles SQLAlchemy
        │   └── session.py     # Session et connexion
        ├── models/
        │   ├── __init__.py
        │   └── cve.py         # Modèles Pydantic + Analyses
        └── routes/
            ├── __init__.py
            ├── cves.py        # Routes CVE
            └── analyses.py    # Routes Analyses
```

### AI Service
```
ai-service/
├── Dockerfile
├── pyproject.toml
├── .env.example
├── .gitignore
├── README.md
└── src/
    └── ai_service/
        ├── __init__.py
        ├── config.py          # Configuration
        ├── main.py           # Point d'entrée
        ├── models/
        │   ├── __init__.py
        │   ├── cve.py         # Modèles CVE
        │   └── analysis.py    # Modèles Analyse
        ├── services/
        │   ├── __init__.py
        │   ├── analysis_service.py   # Logique d'analyse
        │   ├── api_client.py       # Client pour l'API
        │   ├── grouping_service.py  # Groupement des CVE
        │   └── mistral_service.py   # Intégration Mistral AI
        └── utils/
            ├── __init__.py
            └── logger.py       # Configuration des logs
```

---

## 🔄 Intégration Git

Chaque service a son propre dépôt Git :

```bash
# aggregator-service
cd aggregator-service
git init  # Si pas déjà fait
git add .
git commit -m "Initial commit"

# api-service
cd api-service
git init  # Si pas déjà fait
git add .
git commit -m "Initial commit"

# ai-service
cd ai-service
git init  # Si pas déjà fait
git add .
git commit -m "Initial commit"
```

Pour gérer les services comme des sous-modules (optionnel) :

```bash
cd cybersec-platform
git init
git submodule add ../aggregator-service aggregator-service
git submodule add ../api-service api-service
git submodule add ../ai-service ai-service
git submodule update --init --recursive
```

---

## 📝 Notes techniques

### Rate Limiting NVD
L'API NVD a un **rate limit strict** : **5 requêtes toutes les 30 secondes**.
Le service Aggregator respecte cette limite automatiquement avec `NVD_REQUEST_DELAY=30`.

### Détection des doublons
La détection des doublons est gérée par :
1. **Base de données** : Contrainte UNIQUE sur `cve_id` dans la table `cves`
2. **API** : Le endpoint POST /cves/ vérifie l'existence avant insertion
3. **Aggregator** : Filtrage local avant envoi

### Groupement des CVE
Le AI Service utilise un algorithme de similarité pour regrouper les CVE :
- Similarité basée sur : vendor, product, CWE, description
- Seuil configurable via `GROUPING_THRESHOLD`
- Chaque groupe génère une analyse unifiée

### Sévérité globale
L'analyse calcule une sévérité globale basée sur :
- Moyenne des scores CVSS des CVE dans chaque groupe
- Score maximum du groupe
- Confiance de l'analyse IA

---

## 🎯 Prochaines étapes

1. **Automatiser les collectes** :
   ```bash
   # Cron job pour l'Aggregator (toutes les 6 heures)
   0 */6 * * * cd /home/loocist/PycharmProjects/cybersec-platform/aggregator-service && \
     source .venv/bin/activate && \
     python -m cybersec_aggregator.main --days 6 --send-to-api --api-url http://localhost:8000
   
   # Cron job pour l'AI Service (toutes les 12 heures)
   0 */12 * * * cd /home/loocist/PycharmProjects/cybersec-platform/ai-service && \
     source .venv/bin/activate && \
     python -m ai_service.main --days 12
   ```

2. **Ajouter des notifications** :
   - Discord/Telegram bot pour les nouvelles vulnérabilités critiques
   - Email alerts
   - Webhooks

3. **Améliorer l'analyse IA** :
   - Génération de recommandations de correction
   - Prédiction de l'impact
   - Détection de patterns

4. **Configurer un reverse proxy** (Nginx, Traefik, Caddy)

5. **Ajouter l'authentification** à l'API :
   - JWT tokens
   - OAuth2
   - API keys

6. **Déployer en production** :
   - Docker Swarm
   - Kubernetes
   - Serverless (pour l'AI Service)

7. **Ajouter un dashboard** :
   - Grafana pour les statistiques
   - Frontend React/Vue.js
   - Tableau de bord en temps réel

---

## 📄 Licence

Projet personnel - Tous droits réservés.

---

## 🙏 Remerciements

- [NVD (National Vulnerability Database)](https://nvd.nist.gov/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [PostgreSQL](https://www.postgresql.org/)
- [Docker](https://www.docker.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Mistral AI](https://mistral.ai/)
- [Pydantic](https://docs.pydantic.dev/)
- [Uvicorn](https://www.uvicorn.org/)
