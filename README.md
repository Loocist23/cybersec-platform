# 🛡️ Cybersec Platform

> **Plateforme microservice pour la veille en cybersécurité**

Une architecture microservice modulaire pour agréger, stocker et analyser les vulnérabilités CVE.

---

## 📁 Architecture

```
cybersec-platform/
├── docker-compose.yml          # Orchestration Docker
├── .env                        # Configuration globale
├── .gitignore
└── services/
    ├── aggregator-service/      # Microservice 1 : Récupération des CVE
    │   ├── Dockerfile
    │   ├── pyproject.toml
    │   ├── src/
    │   └── .env
    └── api-service/             # Microservice 2 : API + PostgreSQL
        ├── Dockerfile
        ├── pyproject.toml
        ├── src/
        └── .env
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| **aggregator-service** | - | Récupère les CVE depuis l'API NVD |
| **api-service** | 8000 | API FastAPI avec PostgreSQL |
| **postgres** | 5432 | Base de données PostgreSQL |

---

## 🚀 Démarrage rapide

### 1. Cloner le projet
```bash
cd /home/loocist/PycharmProjects
# Le projet est dans cybersec-platform/
```

### 2. Configurer l'environnement
```bash
cd cybersec-platform

# Copier l'exemple de configuration
cp .env.example .env  # Si le fichier existe

# Configurer les variables dans .env (optionnel)
nano .env
```

### 3. Lancer avec Docker Compose
```bash
# Construire et lancer tous les services
docker-compose up -d --build

# Voir les logs
docker-compose logs -f

# Arrêter
docker-compose down
```

### 4. Tester l'API
```bash
# Lister les CVE
curl http://localhost:8000/cves/

# Statistiques
curl http://localhost:8000/cves/stats

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
- Envoi des données à l'API Service
- Stockage local en SQLite (optionnel, fallback)
- Respect du rate limiting (5 req/30s)

**Configuration** :
```bash
# Variables d'environnement (dans aggregator-service/.env)
NVD_API_URL=https://services.nvd.nist.gov/rest/json/cves/2.0
USE_API=true          # Envoyer à l'API au lieu de SQLite
API_URL=http://api:8000  # URL de l'API Service
USE_SQLITE=false      # Désactiver SQLite
INITIAL_DAYS_BACK=7   # Jours à remonter
LOG_LEVEL=INFO
```

**Commandes** :
```bash
# Récupérer les CVE des 7 derniers jours
docker-compose exec aggregator python -m cybersec_aggregator.main --days 7

# Récupérer uniquement les CVE critiques
docker-compose exec aggregator python -m cybersec_aggregator.main --critical-only

# Envoyer à l'API
docker-compose exec aggregator python -m cybersec_aggregator.main --send-to-api
```

### API Service

**Rôle** : API REST pour gérer les CVE stockées en PostgreSQL.

**Fonctionnalités** :
- CRUD complet sur les CVE
- Recherche et filtrage avancés
- Statistiques et analytics
- Documentation OpenAPI (Swagger/ReDoc)

**Endpoints principaux** :
```
GET  /cves/           # Lister les CVE (avec pagination)
GET  /cves/{cve_id}  # Récupérer une CVE spécifique
POST /cves/           # Créer une CVE
POST /cves/batch      # Créer plusieurs CVE
GET  /cves/stats      # Statistiques
PUT  /cves/{cve_id}   # Mettre à jour
DEL  /cves/{cve_id}   # Supprimer
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
```

### PostgreSQL

**Rôle** : Base de données relationnelle pour stocker les CVE.

**Configuration** :
```bash
# Variables d'environnement (dans .env parent)
POSTGRES_DB=cybersec_db
POSTGRES_USER=cybersec_user
POSTGRES_PASSWORD=cybersec_password
```

---

## 📊 Flux de données

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│   NVD API       │────▶│  Aggregator     │────▶│   API Service   │
│  (External)     │     │   Service       │     │  (FastAPI)       │
│                 │     │                 │     │                 │
└─────────────────┘     └──────────┬──────┘     └──────────┬──────┘
                                    │                      │
                                    ▼                      ▼
                            ┌───────────────────────┐
                            │                       │
                            │    PostgreSQL         │
                            │    (Persistance)      │
                            │                       │
                            └───────────────────────┘
```

1. **Aggregator** → Interroge l'API NVD toutes les N heures
2. **Aggregator** → Envoie les nouvelles CVE à l'API via POST /cves/batch
3. **API Service** → Valide et stocke les CVE en PostgreSQL
4. **API Service** →Expose les données via une API REST

---

## 🔧 Développement local

### Sans Docker

#### Aggregator Service
```bash
cd aggregator-service

# Créer l'environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -e .

# Copier et configurer l'environnement
cp .env.example .env
nano .env

# Lancer la collecte
python -m cybersec_aggregator.main --days 1 --critical-only
```

#### API Service
```bash
cd api-service

# Créer l'environnement virtuel
python -m venv .venv
source .venv/bin/activate

# Installer les dépendances
pip install -e .

# Copier et configurer l'environnement
cp .env.example .env
nano .env

# Lancer l'API
python -m api.main

# Ou avec uvicorn directement
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Note** : Pour le développement local, assurez-vous que PostgreSQL est lancé :
```bash
# Avec Docker
docker run -d --name postgres -e POSTGRES_PASSWORD=cybersec_password -p 5432:5432 postgres:15

# Ou installer PostgreSQL localement
```

---

## 🐳 Docker

### Construire un service spécifique
```bash
# Aggregator
docker-compose build aggregator

# API
docker-compose build api

# Tous
docker-compose build
```

### Lancer un service
```bash
# Lancer uniquement PostgreSQL
docker-compose up -d postgres

# Lancer PostgreSQL + API
docker-compose up -d postgres api

# Tout lancer
docker-compose up -d
```

### Voir les logs
```bash
# Tous les services
docker-compose logs -f

# Service spécifique
docker-compose logs -f api
docker-compose logs -f aggregator
```

### Exécuter une commande dans un conteneur
```bash
# Lancer une collecte manuelle
docker-compose exec aggregator python -m cybersec_aggregator.main --days 1

# Accéder à la base de données PostgreSQL
docker-compose exec postgres psql -U cybersec_user -d cybersec_db
```

---

## 🧪 Tests

### Tester l'API avec curl

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

---

## 📁 Structure des fichiers

### Aggregator Service
```
aggregator-service/
├── Dockerfile
├── pyproject.toml
├── .env.example
├── .gitignore
├── src/
│   └── cybersec_aggregator/
│       ├── __init__.py
│       ├── config.py
│       ├── main.py
│       ├── models/
│       │   ├── __init__.py
│       │   └── cve.py
│       ├── services/
│       │   ├── __init__.py
│       │   ├── collector.py
│       │   ├── database.py
│       │   └── nvd.py
│       └── utils/
│           ├── __init__.py
│           └── logger.py
└── data/
└── logs/
```

### API Service
```
api-service/
├── Dockerfile
├── pyproject.toml
├── .env.example
├── .gitignore
├── src/
│   └── api/
│       ├── __init__.py
│       ├── config.py
│       ├── main.py
│       ├── db/
│       │   ├── __init__.py
│       │   ├── models.py
│       │   └── session.py
│       ├── models/
│       │   ├── __init__.py
│       │   └── cve.py
│       └── routes/
│           ├── __init__.py
│           └── cves.py
└── logs/
```

---

## 🔄 Intégration continue

### Git Submodules (optionnel)

Pour une vraie architecture microservice, chaque service peut être un dépôt Git séparé :

```bash
# Initialiser le parent comme git repo
cd cybersec-platform
git init
git add .
git commit -m "Initial commit"

# Ajouter les services comme submodules
git submodule add https://github.com/ton-user/aggregator-service.git services/aggregator-service
git submodule add https://github.com/ton-user/api-service.git services/api-service

# Mettre à jour les submodules
git submodule update --init --recursive
```

---

## 📝 Notes

### Rate Limiting NVD
L'API NVD a un **rate limit strict** : **5 requêtes toutes les 30 secondes**.
Le service Aggregator respecte cette limite automatiquement.

### Détection des doublons
La détection des doublons est gérée par :
1. **Base de données** : Contrainte UNIQUE sur `cve_id` dans PostgreSQL
2. **API** : Vérification avant insertion dans l'endpoint POST /cves/

### Architecture Microservice
Cette plateforme est conçue pour être :
- **Modulaire** : Chaque service peut être déployé séparément
- **Scalable** : Ajout facile de nouveaux services
- **Résiliente** : Fallback SQLite si l'API est indisponible
- **Portable** : Docker pour un déploiement uniformisé

---

## 🎯 Prochaines étapes

1. **Configurer un cron job** pour l'Aggregator :
   ```bash
   # Exemple : toutes les 6 heures
   0 */6 * * * docker-compose exec aggregator python -m cybersec_aggregator.main --days 6 --send-to-api
   ```

2. **Ajouter un service de notification** (Discord, Telegram, etc.)
3. **Ajouter un service de transformation IA** (pour générer du contenu)
4. **Configurer un reverse proxy** (Nginx, Traefik) pour l'API
5. **Ajouter l'authentification** à l'API (JWT, OAuth2)

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
