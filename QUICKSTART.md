# 🚀 Quick Start - Cybersec Platform

> **Guide ultra-rapide pour lancer la plateforme en 5 minutes**

---

## Étape 0 : Prérequis
- Docker installé et démarré
- Docker Compose installé
- Python 3.12+ installé
- Accès internet (pour télécharger les images Docker)

---

## 🎯 Méthode 1 : Démarrage complet avec Docker (Recommandé)

### 1. Lancer tous les services
```bash
cd /home/loocist/PycharmProjects/cybersec-platform

# Construire et lancer PostgreSQL + API
docker-compose -f docker-compose-simple.yml up -d

# Attendre que PostgreSQL soit prêt (30 secondes)
sleep 30

# Vérifier que tout tourne
docker-compose -f docker-compose-simple.yml ps
# → Tu dois voir "cybersec_postgres" et "cybersec_api" avec "Up (healthy)"
```

### 2. Tester l'API
```bash
# Health check
curl http://localhost:8000/

# Documentation Swagger (dans ton navigateur)
# Ouvre : http://localhost:8000/docs

# Lister les CVE (vide pour l'instant)
curl http://localhost:8000/cves/
```

### 3. Collecter les premières CVE
```bash
# Récupérer les CVE des 2 derniers jours et les envoyer à l'API
docker-compose run aggregator python -m cybersec_aggregator.main --days 2 --send-to-api
```

**Résultat attendu :**
```
🔍 Récupération des CVE des 2 derniers jours...
✅ 45 CVE trouvées
✅ 45 CVE envoyées à l'API
```

### 4. Vérifier les données
```bash
# Lister les CVE
curl http://localhost:8000/cves/ | python -m json.tool | head -20

# Statistiques
curl http://localhost:8000/cves/stats
```

### 5. (Optionnel) Lancer l'analyse IA
```bash
# Analyser les CVE collectées
docker-compose run ai-service python -m ai_service.main --days 2
```

**Résultat attendu :**
```
🔍 Récupération de 45 CVE depuis l'API...
🧠 Analyse en cours avec Mistral AI...
✅ 3 groupes de CVE similaires identifiés
✅ 3 analyses créées et envoyées à l'API
```

### 6. Vérifier les analyses
```bash
# Lister les analyses générées
curl http://localhost:8000/analyses/ | python -m json.tool
```

---

## 🎯 Méthode 2 : Développement local (sans Docker)

### 1. Lancer PostgreSQL
```bash
# Avec Docker (le plus simple)
docker run -d --name postgres -e POSTGRES_PASSWORD=cybersec_password -p 5432:5432 postgres:15

# Attendre 30 secondes que PostgreSQL démarre
sleep 30

# Vérifier
psql -h localhost -U postgres
# (mot de passe : cybersec_password)
```

### 2. Lancer l'API Service
```bash
cd /home/loocist/PycharmProjects/cybersec-platform/api-service

# Créer l'environnement virtuel (une seule fois)
python -m venv .venv

# Activer et installer les dépendances
source .venv/bin/activate
pip install -e .

# Copier la configuration
cp .env.example .env

# Lancer l'API
python -m api.main
```

**Tester** : Ouvre http://localhost:8000/docs dans ton navigateur ✅

### 3. Lancer l'Aggregator Service
```bash
# Dans un NOUVEAU terminal
cd /home/loocist/PycharmProjects/cybersec-platform/aggregator-service

# Créer l'environnement virtuel
python -m venv .venv
source .venv/bin/activate

# Installer les dépendances
pip install -e .

# Copier la configuration
cp .env.example .env

# Modifier .env pour utiliser l'API locale
nano .env
```

**Dans le .env, s'assurer que :**
```
USE_API=true
API_URL=http://localhost:8000
USE_SQLITE=false
```

### 4. Collecter les CVE
```bash
# Dans le terminal de l'agregator
python -m cybersec_aggregator.main --days 2 --send-to-api
```

### 5. (Optionnel) Lancer l'AI Service
```bash
# Dans un NOUVEAU terminal
cd /home/loocist/PycharmProjects/cybersec-platform/ai-service

# Créer l'environnement virtuel
python -m venv .venv
source .venv/bin/activate

# Installer les dépendances
pip install -e .

# Copier la configuration
cp .env.example .env

# Modifier .env
nano .env
```

**Dans le .env, configurer :**
```
API_BASE_URL=http://localhost:8000
MISTRAL_API_KEY=ta_clef_api_mistral  # Optionnel, pour l'IA
```

**Lancer l'analyse** :
```bash
python -m ai_service.main --days 2
```

---

## ⚡ Commandes utiles

| Action | Commande |
|--------|----------|
| **Lancer PostgreSQL** | `docker-compose -f docker-compose-simple.yml up -d postgres` |
| **Lancer l'API** | `docker-compose -f docker-compose-simple.yml up -d api` |
| **Arrêter tout** | `docker-compose -f docker-compose-simple.yml down` |
| **Collecter CVE** | `docker-compose run aggregator python -m cybersec_aggregator.main --days 7 --send-to-api` |
| **Analyse IA** | `docker-compose run ai-service python -m ai_service.main --days 7` |
| **Voir les CVE** | `curl http://localhost:8000/cves/` |
| **Voir les analyses** | `curl http://localhost:8000/analyses/` |
| **Stats CVE** | `curl http://localhost:8000/cves/stats` |
| **Stats Analyses** | `curl http://localhost:8000/analyses/stats` |
| **Health check** | `curl http://localhost:8000/health` |
| **Docs Swagger** | Ouvre http://localhost:8000/docs |

---

## 🔧 Problèmes courants

### ❌ Problème 1 : PostgreSQL ne démarre pas
**Symptômes** : `docker-compose ps` montre "unhealthy"

**Solution** :
```bash
# Voir les logs
docker-compose -f docker-compose-simple.yml logs postgres

# Redémarrer avec suppression des volumes
docker-compose -f docker-compose-simple.yml down -v
docker-compose -f docker-compose-simple.yml up -d postgres
```

### ❌ Problème 2 : Erreur de connexion à PostgreSQL
**Symptômes** : `connection refused` ou `could not connect to server`

**Solution** :
```bash
# Vérifier que PostgreSQL est prêt
sleep 30 && docker-compose -f docker-compose-simple.yml ps

# Tester la connexion manuellement
docker-compose -f docker-compose-simple.yml exec postgres psql -U cybersec_user -d cybersec_db

# Si tu utilises l'API manuellement (sans docker-compose)
# Assure-toi que .env contient :
# DB_HOST=localhost
# DB_PORT=5432
# DB_USER=cybersec_user
# DB_PASSWORD=cybersec_password
# DB_NAME=cybersec_db
```

### ❌ Problème 3 : Port 8000 déjà utilisé
**Symptômes** : `Address already in use`

**Solution** :
```bash
# Trouver qui utilise le port
lsof -i :8000

# Tuer le processus
kill -9 <PID>

# Ou changer le port dans api-service/.env
PORT=8001
```

### ❌ Problème 4 : Erreur pip/uv (problème réseau)
**Symptômes** : Timeout lors de l'installation

**Solution** :
```bash
# Vérifier ta connexion
ping google.com

# Essayer avec le miroir de PyPI
pip install --index-url https://pypi.tuna.tsinghua.edu.cn/simple -e .
```

### ❌ Problème 5 : "ModuleNotFoundError: No module named 'fastapi'"
**Symptômes** : L'API ne démarre pas

**Solution** :
```bash
cd api-service
source .venv/bin/activate
pip install -e .
```

### ❌ Problème 6 : "AttributeError: 'str' object has no attribute 'value'"
**Symptômes** : Erreur 500 sur POST /analyses/

**Solution** : 
Cette erreur est corrigée dans la dernière version. Assure-toi que api-service est à jour :
```bash
cd api-service
git pull origin master
```

---

## 📋 Checklist

- [ ] PostgreSQL tourne (`docker-compose -f docker-compose-simple.yml ps`)
- [ ] API tourne (`curl http://localhost:8000/health`)
- [ ] Aggregator a envoyé des CVE (`curl http://localhost:8000/cves/`)
- [ ] AI Service a généré des analyses (`curl http://localhost:8000/analyses/`)

---

## 🎉 Tout est prêt !

Tu as maintenant une plateforme complète de cybersécurité avec :
- ✅ **Aggregator** : Récupère les CVE depuis NVD
- ✅ **API** : Stocke et expose les données
- ✅ **AI Service** : Analyse et groupe les CVE intelligemment
- ✅ **PostgreSQL** : Base de données persistante

**Prochaines étapes :**
1. Automatiser avec cron : `0 */6 * * * docker-compose run aggregator python -m cybersec_aggregator.main --days 6 --send-to-api`
2. Configurer Mistral API key pour l'analyse IA
3. Ajouter un dashboard pour visualiser les données

---

## 📚 Documentation complète

Pour plus de détails, voir : [README.md](./README.md)
