# 🚀 Quick Start - Cybersec Platform

> **Guide ultra-rapide pour lancer la plateforme**

---

## Étape 0 : Préquis
- Docker installé
- Python 3.10+ installé
- Accès internet (pour télécharger les images Docker)

---

## Étape 1 : Lancer PostgreSQL (1 commande)

```bash
cd /home/loocist/PycharmProjects/cybersec-platform

# Lancer UNIQUEMENT PostgreSQL
docker-compose up -d postgres

# Vérifier que PostgreSQL est prêt
docker-compose ps
# → Tu dois voir "cybersec_postgres" avec "Up (healthy)"
```

**Problème ?**
```bash
# Voir les logs
docker-compose logs postgres

# Redémarrer
docker-compose down && docker-compose up -d postgres
```

---

## Étape 2 : Configurer l'API Service (manuellement)

### Ouvrir un nouveau terminal :
```bash
cd /home/loocist/PycharmProjects/cybersec-platform/api-service

# Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate

# Installer les dépendances (une seule fois)
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv pydantic

# Copier la config
cp .env.example .env

# Lancer l'API
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

**Tester l'API** : Ouvre http://localhost:8000/docs dans ton navigateur ✅

---

## Étape 3 : Configurer l'Aggregator Service (manuellement)

### Ouvrir un NOUVEAU terminal :
```bash
cd /home/loocist/PycharmProjects/cybersec-platform/aggregator-service

# Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate

# Installer les dépendances (une seule fois)
pip install requests python-dotenv pydantic

# Copier la config
cp .env.example .env

# Modifier le .env pour utiliser l'API
nano .env
```

**Dans le .env, changer ces lignes :**
```
USE_API=true
API_URL=http://localhost:8000  # PAS http://api:8000 (car on est en local)
USE_SQLITE=false
```

---

## Étape 4 : Tester l'envoi à l'API

### Dans le terminal de l'agregator :
```bash
# Récupérer les CVE et les envoyer à l'API
python -m cybersec_aggregator.main --days 1 --send-to-api
```

**Résultat attendu :**
```
✅ X CVE envoyées à l'API
```

---

## Étape 5 : Vérifier que les CVE sont en base

### Dans le terminal de l'API (ou un nouveau terminal) :
```bash
# Lister les CVE via l'API
curl http://localhost:8000/cves/

# Voir les stats
curl http://localhost:8000/cves/stats
```

**Ou ouvre** http://localhost:8000/docs **et teste les endpoints** ✅

---

## ⚡ Commandes utiles

| Action | Commande |
|--------|----------|
| **Lancer PostgreSQL** | `docker-compose up -d postgres` |
| **Arrêter PostgreSQL** | `docker-compose down` |
| **Lancer l'API** | `uvicorn api.main:app --host 0.0.0.0 --port 8000` |
| **Lancer l'agregator** | `python -m cybersec_aggregator.main --days 1 --send-to-api` |
| **Voir les CVE** | `curl http://localhost:8000/cves/` |
| **Stats** | `curl http://localhost:8000/cves/stats` |

---

## 🔧 Problèmes courants

### Problème 1 : PostgreSQL ne démarre pas
```bash
# Vérifier les logs
docker-compose logs postgres

# Essayez de redémarrer
docker-compose down -v && docker-compose up -d postgres
```

### Problème 2 : Erreur de connexion à la base
```
# Vérifier que PostgreSQL est prêt
docker-compose ps

# Tester la connexion manuellement
psql -h localhost -U cybersec_user -d cybersec_db
# Mot de passe : cybersec_password
```

### Problème 3 : Port 8000 déjà utilisé
```bash
# Trouver qui utilise le port
lsof -i :8000

# Changer le port de l'API
uvicorn api.main:app --host 0.0.0.0 --port 8001
```

### Problème 4 : Erreur pip/uv (problème réseau)
C'est un problème de connexion internet. Essaie :
```bash
# Vérifier ta connexion
ping google.com

# Si ça marche pas, utilise ton téléphone en partage de connexion
# Ou attends que ton réseau soit de retour
```

---

## 🎯 Résumé

1. ✅ `docker-compose up -d postgres` → PostgreSQL tourne
2. ✅ Lancer l'API manuellement avec `uvicorn`
3. ✅ Lancer l'agregator manuellement avec `python -m cybersec_aggregator.main --send-to-api`
4. ✅ Vérifier avec `curl http://localhost:8000/cves/`

**Tout est prêt !** 🚀
