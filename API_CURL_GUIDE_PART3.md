# 📡 Guide Curl - Cybersec Platform API (Partie 3)

> **Comptes Twitter Endpoints + Exemples Pratiques + Bonnes Pratiques**
> Version : 0.2.0 | Base URL : `http://localhost:8000`

---

## 📖 Table des Matières

1. [👥 Endpoints Comptes Twitter (6 endpoints)](#-endpoints-comptes-twitter-6-endpoints)
2. [🎯 Exemples Pratiques Complets](#-exemples-pratiques-complets)
3. [💡 Bonnes Pratiques](#-bonnes-pratiques)
4. [📚 Références](#-références)

---

## 👥 Endpoints Comptes Twitter (6 endpoints)

Les comptes Twitter permettent de gérer les utilisateurs dont les tweets sont collectés. Ces endpoints sont utilisés par le **Twitter Service** pour stocker et gérer les métadonnées des comptes.

### 📄 1. GET /tweets/accounts/ - Lister les comptes Twitter

```bash
# Liste complète des comptes
curl -s http://localhost:8000/tweets/accounts/ | jq

# Avec pagination
curl -s "http://localhost:8000/tweets/accounts/?page=1&page_size=50" | jq

# Filtrer par statut vérifié
curl -s "http://localhost:8000/tweets/accounts/?verified=true" | jq

# Filtrer par nombre minimum d'abonnés
curl -s "http://localhost:8000/tweets/accounts/?min_followers=1000" | jq

# Filtrer par catégorie
curl -s "http://localhost:8000/tweets/accounts/?category=cybersecurity" | jq

# Combinaison de filtres
curl -s "http://localhost:8000/tweets/accounts/?verified=true&min_followers=1000" | jq
```

**Réponse** :
```json
{
  "total": 15,
  "page": 1,
  "page_size": 20,
  "items": [
    {
      "id": 1,
      "username": "krebsongsecurity",
      "user_id": "123456789",
      "display_name": "Brian Krebs",
      "bio": "Investigative journalist covering cybercrime...",
      "followers_count": 350000,
      "following_count": 500,
      "tweet_count": 15000,
      "account_created_at": "2005-03-15T00:00:00",
      "verified": true,
      "avatar_url": "https://pbs.twimg.com/profile_images/...",
      "url": "https://krebsonsecurity.com",
      "category": "cybersecurity",
      "created_at": "2026-06-06T10:00:00",
      "updated_at": "2026-06-06T10:00:00"
    }
  ]
}
```

---

### 📄 2. GET /tweets/accounts/{username} - Détails d'un compte

```bash
# Récupérer un compte spécifique
curl -s http://localhost:8000/tweets/accounts/krebsongsecurity | jq

# Vérifier si un compte existe
ACCOUNT="krebsongsecurity"
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/tweets/accounts/$ACCOUNT | grep -q "200"; then
    echo "✅ Compte @$ACCOUNT existe"
else
    echo "❌ Compte @$ACCOUNT non trouvé"
fi

# Récupérer avec des informations spécifiques
curl -s http://localhost:8000/tweets/accounts/taviso | jq '{username, display_name, followers_count, verified}'
```

**Réponse (200)** :
```json
{
  "id": 1,
  "username": "krebsongsecurity",
  "user_id": "123456789",
  "display_name": "Brian Krebs",
  "bio": "Investigative journalist covering cybercrime, cybersecurity...",
  "followers_count": 350000,
  "following_count": 500,
  "tweet_count": 15000,
  "account_created_at": "2005-03-15T00:00:00",
  "verified": true,
  "avatar_url": "https://pbs.twimg.com/profile_images/...",
  "url": "https://krebsonsecurity.com",
  "category": "cybersecurity",
  "created_at": "2026-06-06T10:00:00",
  "updated_at": "2026-06-06T10:00:00"
}
```

**Réponse (404)** :
```json
{"detail": "Compte @unknown_user non trouvé"}
```

---

### 📤 3. POST /tweets/accounts/ - Créer un compte Twitter

**⭐ Endpoint principal utilisé par le Twitter Service**

```bash
# Créer un compte simple
curl -X POST http://localhost:8000/tweets/accounts/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "new_cyber_account",
    "user_id": "999999999",
    "display_name": "New Cyber Account",
    "bio": "Cybersecurity news and updates",
    "followers_count": 5000,
    "following_count": 1000,
    "tweet_count": 2500,
    "verified": false,
    "category": "cybersecurity"
  }' | jq

# Depuis un fichier JSON
cat > /tmp/new_account.json << 'EOF'
{
  "username": "infosec_alerts",
  "user_id": "888888888",
  "display_name": "InfoSec Alerts",
  "bio": "Real-time cybersecurity alerts and threat intelligence",
  "followers_count": 50000,
  "following_count": 2000,
  "tweet_count": 10000,
  "account_created_at": "2020-01-01T00:00:00",
  "verified": true,
  "avatar_url": "https://pbs.twimg.com/profile_images/avatar.png",
  "url": "https://infosec-alerts.com",
  "category": "threat_intelligence"
}
EOF

curl -X POST http://localhost:8000/tweets/accounts/ \
  -H "Content-Type: application/json" \
  -d @/tmp/new_account.json | jq
```

**Réponse (201)** :
```json
{
  "id": 16,
  "username": "new_cyber_account",
  "user_id": "999999999",
  "display_name": "New Cyber Account",
  "bio": "Cybersecurity news and updates",
  "followers_count": 5000,
  "following_count": 1000,
  "tweet_count": 2500,
  "account_created_at": null,
  "verified": false,
  "avatar_url": null,
  "url": null,
  "category": "cybersecurity",
  "created_at": "2026-06-06T15:30:00",
  "updated_at": "2026-06-06T15:30:00"
}
```

**Note** : Si un compte avec le même `username` existe déjà, il est **mis à jour** avec les nouvelles informations au lieu d'être créé en double.

---

### ✏️ 4. PUT /tweets/accounts/{username} - Mettre à jour un compte

```bash
# Mettre à jour les informations de base
curl -X PUT http://localhost:8000/tweets/accounts/krebsongsecurity \
  -H "Content-Type: application/json" \
  -d '{
    "username": "krebsongsecurity",
    "display_name": "Brian Krebs Updated",
    "bio": "Updated bio - Investigative journalist...",
    "followers_count": 355000
  }' | jq

# Mettre à jour la catégorie et le statut vérifié
curl -X PUT http://localhost:8000/tweets/accounts/taviso \
  -H "Content-Type: application/json" \
  -d '{
    "username": "taviso",
    "category": "vulnerability_researcher",
    "verified": true
  }' | jq

# Mettre à jour avec toutes les informations
curl -X PUT http://localhost:8000/tweets/accounts/infosec_alerts \
  -H "Content-Type: application/json" \
  -d '{
    "username": "infosec_alerts",
    "display_name": "InfoSec Alerts Updated",
    "bio": "Updated description - Real-time threat intelligence",
    "followers_count": 55000,
    "tweet_count": 12000,
    "url": "https://infosec-alerts.com/new-url",
    "category": "threat_intelligence"
  }' | jq
```

**Réponse (200)** : Voir la structure complète du compte.

---

### 🗑️ 5. DELETE /tweets/accounts/{username} - Supprimer un compte

```bash
# Supprimer un compte spécifique
curl -X DELETE http://localhost:8000/tweets/accounts/test_account | jq

# Supprimer avec vérification
ACCOUNT="test_account"
if curl -X DELETE -s -w "\n%{http_code}" http://localhost:8000/tweets/accounts/$ACCOUNT | grep -q "200"; then
    echo "✅ Compte @$ACCOUNT supprimé"
fi

# Supprimer un compte qui n'existe pas (erreur)
curl -X DELETE http://localhost:8000/tweets/accounts/nonexistent_account | jq
```

**Réponse (200)** :
```json
{"message": "Compte @test_account supprimé avec succès"}
```

**Réponse (404)** :
```json
{"detail": "Compte @nonexistent_account non trouvé"}
```

**Note** : La suppression d'un compte **supprime aussi tous ses tweets associés** (cascade).

---

### 🗑️ 6. DELETE /tweets/accounts/?confirm=true - Supprimer TOUS les comptes

**⚠️ DANGER - Supprime tous les comptes Twitter et leurs tweets associés**

```bash
# Supprimer TOUS les comptes (nécessite confirmation)
curl -X DELETE "http://localhost:8000/tweets/accounts/?confirm=true" | jq

# Sans confirmation (erreur)
curl -X DELETE http://localhost:8000/tweets/accounts/ | jq

# Avec vérification interactive
read -p "Supprimer TOUS les comptes Twitter? (yes/no): " confirm
if [ "$confirm" = "yes" ]; then
    curl -X DELETE "http://localhost:8000/tweets/accounts/?confirm=true" | jq
fi
```

**Réponse (200)** :
```json
{"message": "15 comptes Twitter supprimés"}
```

**Erreur (400)** :
```json
{"detail": "La suppression de tous les comptes nécessite confirm=true"}
```

---

## 🎯 Exemples Pratiques Complets

### 🔹 Workflow Complet : Collecte Twitter

```bash
#!/bin/bash
# collect_and_analyze_twitter.sh - Script complet de collecte et analyse Twitter

echo "=== 🚀 Collecte et Analyse Twitter ==="
echo ""

# 1. Vérifier que l'API est en santé
echo "🔍 Vérification de l'API..."
if ! curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo "❌ L'API n'est pas disponible"
    exit 1
fi
echo "✅ API est opérationnelle"
echo ""

# 2. Vérifier les comptes Twitter existants
echo "📊 Compter les comptes Twitter existants..."
ACCOUNT_COUNT=$(curl -s http://localhost:8000/tweets/accounts/ | jq '.total')
echo "   Compte(s) existant(s): $ACCOUNT_COUNT"
echo ""

# 3. Lister les comptes vérifiés
curl -s "http://localhost:8000/tweets/accounts/?verified=true&page_size=50" | \
  jq -r '.items[] | "✓ @\(.username) - \(.display_name // "") (\(.followers_count // 0) followers)"'
echo ""

# 4. Vérifier les tweets existants
TWEET_COUNT=$(curl -s http://localhost:8000/tweets/stats | jq '.total')
echo "📊 Tweets existants: $TWEET_COUNT"
echo ""

# 5. Collecter de nouveaux tweets (simulation)
echo "🔄 Collecte de tweets depuis Twitter Service..."
docker-compose run twitter python -m twitter_service.main \
  --queries cybersecurity,vulnerability,infosec,CVE \
  --days 1 \
  --limit 20 > /dev/null 2>&1
echo "✅ Collecte terminée"
echo ""

# 6. Vérifier les nouveaux tweets
NEW_TWEET_COUNT=$(curl -s "http://localhost:8000/tweets/?days=1" | jq '.total')
echo "📈 Nouveaux tweets aujourd'hui: $NEW_TWEET_COUNT"
echo ""

# 7. Afficher les 5 tweets les plus populaires
echo "🏆 Top 5 tweets les plus populaires:"
curl -s "http://localhost:8000/tweets/?page_size=100" | \
  jq -r '.items | sort_by(-.likes) | .[:5] | .[] | "🔹 @\(.username): \(.likes) likes - \(.content[:60])..."'
echo ""

# 8. Statistiques complètes
echo "📊 Statistiques Twitter:"
curl -s http://localhost:8000/tweets/stats | \
  jq -r '"Total: \(.total) | Moyenne likes: \(.avg_likes) | Moyenne RT: \(.avg_retweets)"'
echo ""

echo "=== ✅ Collecte et analyse terminées ==="
```

---

### 🔹 Gestion des Comptes et Tweets

```bash
#!/bin/bash
# manage_twitter_data.sh - Gestion avancée des données Twitter

# Créer un compte et ses tweets
cat > /tmp/twitter_data.json << 'EOF'
{
  "account": {
    "username": "cybersec_news",
    "user_id": "111111111",
    "display_name": "CyberSec News",
    "bio": "Latest cybersecurity news and updates",
    "followers_count": 25000,
    "verified": true,
    "category": "news"
  },
  "tweets": [
    {
      "tweet_id": "1000000000000000001",
      "username": "cybersec_news",
      "content": "New critical vulnerability discovered in popular software. Patch immediately!",
      "date": "2026-06-06T10:00:00",
      "url": "https://twitter.com/cybersec_news/status/1000000000000000001",
      "likes": 500,
      "retweets": 200,
      "language": "en",
      "hashtags": ["cybersecurity", "vulnerability", "patch"],
      "category": "vulnerability",
      "severity": "CRITICAL"
    },
    {
      "tweet_id": "1000000000000000002",
      "username": "cybersec_news",
      "content": "Security researchers discover new malware campaign targeting enterprises.",
      "date": "2026-06-06T11:00:00",
      "url": "https://twitter.com/cybersec_news/status/1000000000000000002",
      "likes": 300,
      "retweets": 100,
      "language": "en",
      "hashtags": ["malware", "cybersecurity", "enterprise"],
      "category": "threat_intel",
      "severity": "HIGH"
    }
  ]
}
EOF

# Créer le compte
echo "Création du compte Twitter..."
curl -X POST http://localhost:8000/tweets/accounts/ \
  -H "Content-Type: application/json" \
  -d @<(/tmp/twitter_data.json | jq '.account') | jq

# Créer les tweets
echo ""
echo "Création des tweets..."
curl -X POST http://localhost:8000/tweets/batch \
  -H "Content-Type: application/json" \
  -d @<(/tmp/twitter_data.json | jq '.tweets') | jq

echo ""
echo "✅ Données Twitter créées"
```

---

### 🔹 Analyse Correlée CVE + Tweets

```bash
#!/bin/bash
# correlate_cve_tweets.sh - Corréler les CVE avec les tweets

echo "=== 🔍 Correllation CVE/Tweets ==="
echo ""

# 1. Récupérer les CVE CRITICAL récentes
CRITICAL_CVES=$(curl -s "http://localhost:8000/cves/?severity=CRITICAL&days=7" | jq -r '.items[] | .cve_id')

if [ -z "$CRITICAL_CVES" ]; then
    echo "⚠️ Aucune CVE CRITICAL récente"
else
    echo "📋 CVE CRITICAL récentes:"
    echo "$CRITICAL_CVES"
    echo ""
fi

# 2. Récupérer les tweets mentionnant des CVE
CVE_TWEETS=$(curl -s "http://localhost:8000/tweets/?hashtag=CVE&page_size=50" | jq -r '.items[]')

if [ -z "$CVE_TWEETS" ]; then
    echo "⚠️ Aucun tweet avec hashtag #CVE"
else
    echo "🐦 Tweets mentionnant des CVE:"
    echo "$CVE_TWEETS" | jq -r '.[] | "@\(.username): \(.content[:80])..."'
    echo ""
fi

# 3. Trouver les tweets populaires (>100 likes) sur la cybersécurité
POPULAR_TWEETS=$(curl -s "http://localhost:8000/tweets/?min_likes=100&page_size=20" | jq -r '.items[]')

echo "🔥 Tweets populaires (>100 likes):"
echo "$POPULAR_TWEETS" | jq -r '.[] | "@\(.username): \(.likes) likes - \(.content[:60])..."'
echo ""

# 4. Statistiques corréllées
echo "📊 Statistiques:"
echo "   CVE total: $(curl -s http://localhost:8000/cves/stats | jq '.total')"
echo "   Tweets total: $(curl -s http://localhost:8000/tweets/stats | jq '.total')"
echo "   CVE CRITICAL: $(curl -s "http://localhost:8000/cves/stats?days=7" | jq '.by_severity.CRITICAL // 0')"
echo "   Tweets #CVE: $(echo "$CVE_TWEETS" | jq 'length')"
```

---

### 🔹 Export et Sauvegarde

```bash
#!/bin/bash
# backup_cybersec_data.sh - Export complet des données

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/tmp/cybersec_backup_$DATE"
mkdir -p "$BACKUP_DIR"

echo "=== 💾 Export des données Cybersec Platform ==="
echo "Dossier: $BACKUP_DIR"
echo ""

# 1. Exporter toutes les CVE
echo "Export des CVE..."
curl -s "http://localhost:8000/cves/?page_size=10000" | jq '.items' > "$BACKUP_DIR/cves.json"
echo "✅ CVE exportées: $(jq 'length' $BACKUP_DIR/cves.json)"

# 2. Exporter toutes les analyses
echo "Export des analyses..."
curl -s "http://localhost:8000/analyses/?page_size=10000" | jq '.items' > "$BACKUP_DIR/analyses.json"
echo "✅ Analyses exportées: $(jq 'length' $BACKUP_DIR/analyses.json)"

# 3. Exporter tous les tweets
echo "Export des tweets..."
curl -s "http://localhost:8000/tweets/?page_size=10000" | jq '.items' > "$BACKUP_DIR/tweets.json"
echo "✅ Tweets exportés: $(jq 'length' $BACKUP_DIR/tweets.json)"

# 4. Exporter tous les comptes Twitter
echo "Export des comptes Twitter..."
curl -s "http://localhost:8000/tweets/accounts/?page_size=10000" | jq '.items' > "$BACKUP_DIR/accounts.json"
echo "✅ Comptes exportés: $(jq 'length' $BACKUP_DIR/accounts.json)"

# 5. Exporter les statistiques
echo "Export des statistiques..."
curl -s http://localhost:8000/cves/stats > "$BACKUP_DIR/cves_stats.json"
curl -s http://localhost:8000/analyses/stats > "$BACKUP_DIR/analyses_stats.json"
curl -s http://localhost:8000/tweets/stats > "$BACKUP_DIR/tweets_stats.json"

# 6. Créer une archive
echo "Création de l'archive..."
tar czf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR"
echo "✅ Archive créée: $BACKUP_DIR.tar.gz"

# 7. Nettoyer
echo "Nettoyage..."
rm -rf "$BACKUP_DIR"
echo "✅ Backup terminé"
```

---

### 🔹 Script de Surveillance Temps Réel

```bash
#!/bin/bash
# monitor_cybersec.sh - Surveillance en temps réel

echo "🔍 Surveillance Cybersec Platform - Ctrl+C pour arrêter"
echo "======================================================"
echo ""

while true; do
    clear
    echo "🔍 $(date) - Surveillance Cybersec Platform"
    echo "=============================================="
    echo ""
    
    # 1. Santé de l'API
    API_STATUS=$(curl -s http://localhost:8000/health | jq -r '.status // "unknown"')
    echo "🏥 API Status: $API_STATUS"
    
    # 2. Statistiques CVE
    CVE_STATS=$(curl -s "http://localhost:8000/cves/stats?days=1")
    CVE_TODAY=$(echo "$CVE_STATS" | jq '.total')
    CVE_CRITICAL=$(echo "$CVE_STATS" | jq '.by_severity.CRITICAL // 0')
    CVE_HIGH=$(echo "$CVE_STATS" | jq '.by_severity.HIGH // 0')
    echo "📋 CVE aujourd'hui: $CVE_TODAY (CRITICAL: $CVE_CRITICAL, HIGH: $CVE_HIGH)"
    
    # 3. Statistiques Tweets
    TWEET_STATS=$(curl -s "http://localhost:8000/tweets/stats?days=1")
    TWEET_TODAY=$(echo "$TWEET_STATS" | jq '.total')
    TWEET_POPULAR=$(echo "$TWEET_STATS" | jq '[.items[] | select(.likes > 50)] | length // 0')
    echo "🐦 Tweets aujourd'hui: $TWEET_TODAY (>50 likes: $TWEET_POPULAR)"
    
    # 4. Statistiques Analyses
    ANALYSIS_STATS=$(curl -s "http://localhost:8000/analyses/stats?days=1")
    ANALYSIS_TODAY=$(echo "$ANALYSIS_STATS" | jq '.total')
    echo "🧠 Analyses aujourd'hui: $ANALYSIS_TODAY"
    
    # 5. Alertes
    echo ""
    echo "⚠️  Alertes:"
    if [ "$CVE_CRITICAL" -gt 0 ]; then
        echo "   🔴 $CVE_CRITICAL nouvelles CVE CRITICAL aujourd'hui"
        curl -s "http://localhost:8000/cves/?days=1&severity=CRITICAL&page_size=5" | \
          jq -r '.items[] | "   - \(.cve_id): \(.cvss_score) - \(.description[:50])"'
    fi
    
    if [ "$TWEET_POPULAR" -gt 0 ]; then
        echo "   🟡 $TWEET_POPULAR tweets populaires (>50 likes) aujourd'hui"
    fi
    
    # 6. Comptes Twitter
    ACCOUNT_COUNT=$(curl -s http://localhost:8000/tweets/accounts/ | jq '.total')
    VERIFIED_COUNT=$(curl -s "http://localhost:8000/tweets/accounts/?verified=true" | jq '.total')
    echo "   👥 Comptes Twitter: $ACCOUNT_COUNT (vérifiés: $VERIFIED_COUNT)"
    
    echo ""
    echo "Prochaine mise à jour dans 30 secondes..."
    sleep 30
done
```

---

## 💡 Bonnes Pratiques

### ✅ Bonnes Pratiques Générales

#### 1. Toujours utiliser jq pour le parsing JSON
```bash
# ❌ Mauvaise pratique (JSON brut)
curl http://localhost:8000/cves/ | grep "cve_id"

# ✅ Bonne pratique (jq pour parsing structuré)
curl -s http://localhost:8000/cves/ | jq '.items[] | .cve_id'
```

#### 2. Utiliser les options silencieuses pour les scripts
```bash
# ❌ Bruyant
curl http://localhost:8000/cves/

# ✅ Silencieux
curl -s http://localhost:8000/cves/
```

#### 3. Vérifier les codes HTTP
```bash
# ❌ Pas de vérification
curl http://localhost:8000/cves/CVE-9999-9999

# ✅ Avec vérification du code
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/cves/CVE-9999-9999 | grep -q "200"; then
    echo "CVE existe"
else
    echo "CVE non trouvée"
fi
```

#### 4. Utiliser des variables pour les valeurs réutilisables
```bash
# ❌ Valeurs dupliquées
curl http://localhost:8000/cves/
curl http://localhost:8000/cves/stats

# ✅ Avec variables
BASE_URL="http://localhost:8000"
curl $BASE_URL/cves/
curl $BASE_URL/cves/stats
```

---

### ✅ Bonnes Pratiques pour les Requêtes

#### 1. Pagination
```bash
# ❌ Récupérer trop de données d'un coup
curl -s "http://localhost:8000/cves/?page_size=100000" 

# ✅ Utiliser la pagination
PAGE_SIZE=100
TOTAL=$(curl -s http://localhost:8000/cves/ | jq '.total')
PAGES=$(( (TOTAL + PAGE_SIZE - 1) / PAGE_SIZE ))

for ((page=1; page<=PAGES; page++)); do
    curl -s "http://localhost:8000/cves/?page=$page&page_size=$PAGE_SIZE"
done
```

#### 2. Gestion des Erreurs
```bash
# ❌ Ignorer les erreurs
curl http://localhost:8000/cves/nonexistent

# ✅ Gérer les erreurs proprement
response=$(curl -s -w "\n%{http_code}" http://localhost:8000/cves/nonexistent)
http_code=$(echo "$response" | tail -n1)

if [ "$http_code" = "200" ]; then
    echo "Succès"
elif [ "$http_code" = "404" ]; then
    echo "Ressource non trouvée"
elif [ "$http_code" = "400" ]; then
    echo "Requête invalide"
else
    echo "Erreur: $http_code"
fi
```

#### 3. Timeouts
```bash
# ❌ Pas de timeout (peut bloquer)
curl http://localhost:8000/cves/

# ✅ Avec timeout
curl --max-time 30 http://localhost:8000/cves/

# ✅ Timeout connect et total
curl --connect-timeout 5 --max-time 30 http://localhost:8000/cves/
```

#### 4. Retry avec Backoff
```bash
# Fonction de retry avec backoff exponentiel
retry_with_backoff() {
    local url="$1"
    local max_retries=3
    local backoff=1
    local retry=0
    
    while [ $retry -lt $max_retries ]; do
        response=$(curl -s -w "\n%{http_code}" "$url" 2>&1)
        http_code=$(echo "$response" | tail -n1)
        
        if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
            echo "${response%\n*}"
            return 0
        fi
        
        retry=$((retry + 1))
        echo "Erreur $http_code, retry $retry/$max_retries dans $backoff secondes..."
        sleep $backoff
        backoff=$((backoff * 2))
    done
    
    echo "Échec après $max_retries tentatives"
    return 1
}

# Utilisation
retry_with_backoff "http://localhost:8000/cves/"
```

---

### ✅ Bonnes Pratiques pour les Batch Operations

#### 1. Taille des Batches
```bash
# ❌ Trop grand batch
curl -X POST http://localhost:8000/cves/batch -d @huge_file.json

# ✅ Batch de taille raisonnable (50-100)
BATCH_SIZE=50
total_cves=1000

for ((i=0; i<total_cves; i+=BATCH_SIZE)); do
    batch=$(jq ".items[$i:$((i+BATCH_SIZE))]" huge_file.json)
    curl -X POST http://localhost:8000/cves/batch -d "$batch"
done
```

#### 2. Gestion des Doublons
```bash
# ✅ La déduplication est gérée par l'API
# L'API ignore automatiquement les doublons
curl -X POST http://localhost:8000/cves/batch \
  -d '[{"cve_id": "CVE-2024-0001", ...}, {"cve_id": "CVE-2024-0001", ...}]' | jq
# → {"message": "1 CVE créée, 1 ignorée (déjà existante)"}
```

---

### ✅ Bonnes Pratiques de Sécurité

#### 1. Ne jamais committer des secrets dans les commandes
```bash
# ❌ Secret en clair dans la commande
MISTRAL_API_KEY="sk-1234567890"
curl https://api.mistral.ai/... -H "Authorization: Bearer $MISTRAL_API_KEY"

# ✅ Utiliser des variables d'environnement
# Dans .bashrc ou .env
# export MISTRAL_API_KEY="sk-1234567890"

# Dans le script
if [ -z "$MISTRAL_API_KEY" ]; then
    echo "❌ MISTRAL_API_KEY non définie"
    exit 1
fi
curl https://api.mistral.ai/... -H "Authorization: Bearer $MISTRAL_API_KEY"
```

#### 2. Utiliser HTTPS en production
```bash
# ❌ HTTP en production
curl http://api.example.com/cves/

# ✅ HTTPS en production
curl https://api.example.com/cves/
```

#### 3. Valider les entrées utilisateur
```bash
# ❌ Pas de validation
CVE_ID="$1"
curl http://localhost:8000/cves/$CVE_ID

# ✅ Avec validation
CVE_ID="$1"
if [[ ! "$CVE_ID" =~ ^CVE-[0-9]{4}-[0-9]+$ ]]; then
    echo "❌ Format CVE invalide"
    exit 1
fi
curl http://localhost:8000/cves/$CVE_ID
```

---

### ✅ Bonnes Pratiques de Logging

#### 1. Logger les opérations importantes
```bash
#!/bin/bash
# script_with_logging.sh

LOG_FILE="/var/log/cybersec_operations.log"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "Début de la collecte CVE"
curl -s "http://localhost:8000/cves/?days=7" > /tmp/cves.json
log "Collecte terminée: $(jq 'length' /tmp/cves.json) CVE"

log "Début de l'analyse"
# ... analyse
log "Analyse terminée"
```

#### 2. Logger les erreurs
```bash
log_error() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ❌ ERREUR: $1" | tee -a "$LOG_FILE"
}

response=$(curl -s -w "\n%{http_code}" http://localhost:8000/cves/)
http_code=$(echo "$response" | tail -n1)

if [ "$http_code" != "200" ]; then
    log_error "Échec de la requête: HTTP $http_code"
    exit 1
fi
```

---

## 📚 Références

### 🔗 Documentation Interne

- [DOCUMENTATION_COMPLETE.md](./DOCUMENTATION_COMPLETE.md) - Architecture complète et détails techniques
- [API_CURL_GUIDE_PART1.md](./API_CURL_GUIDE_PART1.md) - Health Check + Endpoints CVE
- [API_CURL_GUIDE_PART2.md](./API_CURL_GUIDE_PART2.md) - Analyses IA + Endpoints Tweets
- [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) - Tableau récapitulatif rapide

### 📖 Documentation Externe

- [cURL Documentation](https://curl.se/docs/) - Documentation officielle de curl
- [jq Manual](https://stedolan.github.io/jq/manual/) - Manuel complet de jq
- [HTTP Status Codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status) - Codes HTTP standard
- [REST API Tutorial](https://www.restapitutorial.com/) - Bonnes pratiques REST

### 🎯 Prochaines Étapes

- [ ] **Authentification JWT** - Ajouter l'authentification à l'API
- [ ] **Rate Limiting** - Implémenter le rate limiting sur les endpoints
- [ ] **Webhooks** - Ajouter des notifications en temps réel
- [ ] **Dashboard** - Créer une interface graphique
- [ ] **Notifications** - Intégrer Discord/Email/Telegram

---

### 📊 Résumé des Endpoints

| Catégorie | Méthode | Endpoint | Description |
|-----------|---------|----------|-------------|
| **Comptes** | GET | `/tweets/accounts/` | Lister les comptes (paginé) |
| **Comptes** | GET | `/tweets/accounts/{username}` | Détails d'un compte |
| **Comptes** | POST | `/tweets/accounts/` | Créer un compte |
| **Comptes** | PUT | `/tweets/accounts/{username}` | Mettre à jour un compte |
| **Comptes** | DELETE | `/tweets/accounts/{username}` | Supprimer un compte |
| **Comptes** | DELETE | `/tweets/accounts/?confirm=true` | Supprimer TOUS les comptes |

**Total dans cette partie** : 6 endpoints Comptes Twitter

---

*© 2026 Cybersec Platform - Tous droits réservés*
