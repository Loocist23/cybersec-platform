# 📡 Guide Curl - Cybersec Platform API (Partie 2)

> **Analyses IA + Tweets Endpoints**
> Version : 0.2.0 | Base URL : `http://localhost:8000`

---

## 📖 Table des Matières

1. [🧠 Endpoints Analyses IA (7 endpoints)](#-endpoints-analyses-ia-7-endpoints)
2. [🐦 Endpoints Tweets (10 endpoints)](#-endpoints-tweets-10-endpoints)
3. [🎯 Exemples Avancés](#-exemples-avancés)

---

## 🧠 Endpoints Analyses IA (7 endpoints)

### 📄 1. GET /analyses/ - Lister les analyses

```bash
# Liste complète des analyses
curl -s http://localhost:8000/analyses/ | jq

# Avec pagination
curl -s "http://localhost:8000/analyses/?page=1&page_size=20" | jq

# Filtrer par statut
curl -s "http://localhost:8000/analyses/?status_filter=completed" | jq
curl -s "http://localhost:8000/analyses/?status_filter=processing" | jq

# Filtrer par sévérité
curl -s "http://localhost:8000/analyses/?severity=CRITICAL" | jq
curl -s "http://localhost:8000/analyses/?severity=HIGH" | jq

# Filtrer par date (7 derniers jours)
curl -s "http://localhost:8000/analyses/?days=7" | jq

# Combinaison de filtres
curl -s "http://localhost:8000/analyses/?status_filter=completed&severity=CRITICAL&days=7" | jq
```

**Réponse** :
```json
{
  "total": 5,
  "page": 1,
  "page_size": 20,
  "items": [
    {
      "id": 1,
      "analysis_id": "analysis-20240523-001",
      "title": "Analyse des vulnérabilités Apache",
      "summary": "15 vulnérabilités critiques détectées...",
      "grouped_cves": [
        {
          "group_id": "apache-tomcat-2024",
          "cve_ids": ["CVE-2024-1234", "CVE-2024-5678"],
          "common_vendor": "Apache",
          "common_product": "Apache Tomcat",
          "similarity_score": 0.92,
          "total_cves": 2,
          "avg_cvss_score": 9.5,
          "max_cvss_score": 9.8
        }
      ],
      "severity_overall": "CRITICAL",
      "confidence": 0.95,
      "extra_data": {"model": "mistral-tiny", "tokens_used": 5000},
      "status": "completed",
      "created_at": "2024-05-23T14:30:00",
      "updated_at": "2024-05-23T14:30:00"
    }
  ]
}
```

---

### 📄 2. GET /analyses/{analysis_id}/ - Détails d'une analyse

```bash
# Récupérer une analyse spécifique
curl -s http://localhost:8000/analyses/analysis-20240523-001/ | jq

# Vérifier si une analyse existe
ANALYSIS_ID="analysis-20240523-001"
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/analyses/$ANALYSIS_ID/ | grep -q "200"; then
    echo "✅ Analyse $ANALYSIS_ID existe"
else
    echo "❌ Analyse $ANALYSIS_ID non trouvée"
fi
```

**Réponse (200)** :
```json
{
  "id": 1,
  "analysis_id": "analysis-20240523-001",
  "title": "Analyse des vulnérabilités Apache",
  "summary": "15 vulnérabilités critiques détectées dans les produits Apache...",
  "grouped_cves": [...],
  "severity_overall": "CRITICAL",
  "confidence": 0.95,
  "extra_data": {"model": "mistral-tiny", "tokens_used": 5000},
  "status": "completed",
  "created_at": "2024-05-23T14:30:00",
  "updated_at": "2024-05-23T14:30:00"
}
```

**Réponse (404)** :
```json
{"detail": "Analyse analysis-9999 non trouvée"}
```

---

### 📤 3. POST /analyses/ - Créer une analyse

**⭐ Endpoint principal utilisé par l'AI Service**

```bash
# Créer une analyse simple
curl -X POST http://localhost:8000/analyses/ \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_id": "analysis-test-001",
    "title": "Analyse Test",
    "summary": "Ceci est une analyse de test générée par IA",
    "severity_overall": "HIGH",
    "confidence": 0.9,
    "status": "completed",
    "extra_data": {"model": "mistral-tiny", "tokens_used": 1000},
    "grouped_cves": [
      {
        "group_id": "test-group-1",
        "cve_ids": ["CVE-2024-0001", "CVE-2024-0002"],
        "common_vendor": "Test Vendor",
        "common_product": "Test Product",
        "similarity_score": 0.95,
        "total_cves": 2,
        "avg_cvss_score": 8.5,
        "max_cvss_score": 9.0
      }
    ]
  }' | jq

# Depuis un fichier JSON
cat > /tmp/new_analysis.json << 'EOF'
{
  "analysis_id": "analysis-mistral-001",
  "title": "Analyse des vulnérabilités critiques de mai 2026",
  "summary": "Cette analyse a identifié 25 vulnérabilités critiques dans divers produits. Une attention particulière doit être portée aux CVE-2024-1234 et CVE-2024-5678.",
  "severity_overall": "CRITICAL",
  "confidence": 0.92,
  "status": "completed",
  "extra_data": {
    "model": "mistral-tiny",
    "tokens_used": 8500,
    "processing_time": 3.2
  },
  "grouped_cves": [
    {
      "group_id": "apache-group",
      "cve_ids": ["CVE-2024-1234", "CVE-2024-1235"],
      "common_vendor": "Apache",
      "common_product": "Apache Tomcat",
      "similarity_score": 0.94,
      "total_cves": 2,
      "avg_cvss_score": 9.2,
      "max_cvss_score": 9.8
    }
  ]
}
EOF

curl -X POST http://localhost:8000/analyses/ \
  -H "Content-Type: application/json" \
  -d @/tmp/new_analysis.json | jq
```

**Réponse (201)** :
```json
{
  "message": "Analyse analysis-test-001 créée avec succès",
  "analysis_id": "analysis-test-001",
  "analysis": {
    "id": 6,
    "analysis_id": "analysis-test-001",
    "title": "Analyse Test",
    "summary": "Ceci est une analyse de test...",
    "grouped_cves": [...],
    "severity_overall": "HIGH",
    "confidence": 0.9,
    "status": "completed",
    "created_at": "2026-06-06T15:30:00",
    "updated_at": "2026-06-06T15:30:00"
  }
}
```

---

### ✏️ 4. PUT /analyses/{analysis_id}/ - Mettre à jour une analyse

```bash
# Mettre à jour le titre et le résumé
curl -X PUT http://localhost:8000/analyses/analysis-test-001/ \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_id": "analysis-test-001",
    "title": "Analyse Test - Mise à jour",
    "summary": "Résumé mis à jour avec de nouvelles informations",
    "severity_overall": "CRITICAL",
    "confidence": 0.95
  }' | jq

# Mettre à jour le statut
curl -X PUT http://localhost:8000/analyses/analysis-test-001/ \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_id": "analysis-test-001",
    "status": "processing"
  }' | jq

# Mettre à jour avec de nouveaux groupes
curl -X PUT http://localhost:8000/analyses/analysis-test-001/ \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_id": "analysis-test-001",
    "title": "Analyse mise à jour",
    "grouped_cves": [
      {
        "group_id": "updated-group",
        "cve_ids": ["CVE-2024-0001", "CVE-2024-0002", "CVE-2024-0003"],
        "similarity_score": 0.95,
        "total_cves": 3,
        "avg_cvss_score": 8.8,
        "max_cvss_score": 9.5
      }
    ]
  }' | jq
```

**Réponse (200)** : Voir la structure analyse complète.

---

### 🗑️ 5. DELETE /analyses/{analysis_id}/ - Supprimer une analyse

```bash
# Supprimer une analyse
curl -X DELETE http://localhost:8000/analyses/analysis-test-001/ | jq

# Supprimer avec vérification
ANALYSIS_ID="analysis-test-001"
if curl -X DELETE -s -w "\n%{http_code}" http://localhost:8000/analyses/$ANALYSIS_ID/ | grep -q "200"; then
    echo "✅ Analyse $ANALYSIS_ID supprimée"
fi
```

**Réponse (200)** :
```json
{"message": "Analyse analysis-test-001 supprimée avec succès", "detail": "ID interne: 6"}
```

---

### 🗑️ 6. DELETE /analyses/?confirm=true - Supprimer TOUTES les analyses

**⚠️ DANGER - Supprime toutes les analyses**

```bash
# Supprimer TOUTES les analyses (nécessite confirmation)
curl -X DELETE "http://localhost:8000/analyses/?confirm=true" | jq

# Sans confirmation (erreur)
curl -X DELETE http://localhost:8000/analyses/ | jq
```

**Réponse (200)** :
```json
{"message": "5 analyses et 15 mappings supprimés"}
```

**Erreur (400)** :
```json
{"detail": "La suppression de toutes les analyses nécessite confirm=true"}
```

---

### 📊 7. GET /analyses/stats/ - Statistiques des analyses

```bash
# Statistiques globales
curl -s http://localhost:8000/analyses/stats/ | jq

# Statistiques des 7 derniers jours
curl -s "http://localhost:8000/analyses/stats/?days=7" | jq

# Statistiques par statut seulement
curl -s "http://localhost:8000/analyses/stats/" | jq '.by_status'

# Statistiques par sévérité seulement
curl -s "http://localhost:8000/analyses/stats/" | jq '.by_severity'

# Affichage formaté
STATS=$(curl -s http://localhost:8000/analyses/stats/)
echo "Total: $(echo $STATS | jq '.total')"
echo "Confiance moyenne: $(echo $STATS | jq '.avg_confidence')"
echo "Par statut: $(echo $STATS | jq '.by_status')"
echo "Par sévérité: $(echo $STATS | jq '.by_severity')"
```

**Réponse** :
```json
{
  "total": 42,
  "by_status": {"pending": 0, "processing": 2, "completed": 40, "failed": 0},
  "by_severity": {"LOW": 5, "MEDIUM": 15, "HIGH": 18, "CRITICAL": 4},
  "avg_confidence": 0.87
}
```

---

## 🐦 Endpoints Tweets (10 endpoints)

### 📄 1. GET /tweets/ - Lister les tweets

```bash
# Liste complète des tweets
curl -s http://localhost:8000/tweets/ | jq

# Avec pagination
curl -s "http://localhost:8000/tweets/?page=1&page_size=20" | jq

# Filtrer par utilisateur
curl -s "http://localhost:8000/tweets/?username=krebsongsecurity" | jq

# Filtrer par hashtag
curl -s "http://localhost:8000/tweets/?hashtag=cybersecurity" | jq

# Filtrer par date (7 derniers jours)
curl -s "http://localhost:8000/tweets/?days=7" | jq

# Filtrer par likes minimum
curl -s "http://localhost:8000/tweets/?min_likes=100" | jq

# Filtrer par langue
curl -s "http://localhost:8000/tweets/?language=en" | jq

# Filtrer par catégorie
curl -s "http://localhost:8000/tweets/?category=vulnerability" | jq

# Combinaison de filtres
curl -s "http://localhost:8000/tweets/?username=krebsongsecurity&days=7&min_likes=50" | jq
```

**Réponse** :
```json
{
  "total": 250,
  "page": 1,
  "page_size": 20,
  "items": [
    {
      "id": 1,
      "tweet_id": "1234567890123456789",
      "account_id": 1,
      "username": "krebsongsecurity",
      "user_id": "123456789",
      "content": "New critical vulnerability discovered...",
      "date": "2024-06-05T10:30:00",
      "url": "https://twitter.com/krebsongsecurity/status/1234567890123456789",
      "likes": 150,
      "retweets": 45,
      "replies": 12,
      "quotes": 5,
      "views": 10000,
      "is_retweet": false,
      "is_quote": false,
      "is_reply": false,
      "language": "en",
      "hashtags": ["cybersecurity", "vulnerability", "CVE"],
      "mentions": ["@user1"],
      "urls": ["https://example.com/vulnerability"],
      "images": [],
      "videos": [],
      "category": "vulnerability",
      "severity": "HIGH",
      "created_at": "2026-06-05T11:00:00",
      "updated_at": "2026-06-05T11:00:00"
    }
  ]
}
```

---

### 📄 2. GET /tweets/{tweet_id} - Détails d'un tweet

```bash
# Récupérer un tweet spécifique
curl -s http://localhost:8000/tweets/1234567890123456789 | jq

# Vérifier si un tweet existe
TWEET_ID="1234567890123456789"
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/tweets/$TWEET_ID | grep -q "200"; then
    echo "✅ Tweet $TWEET_ID existe"
else
    echo "❌ Tweet $TWEET_ID non trouvé"
fi
```

**Réponse (200)** : Voir la structure tweet complète.

---

### 📤 3. POST /tweets/ - Créer un tweet

```bash
# Créer un tweet simple
curl -X POST http://localhost:8000/tweets/ \
  -H "Content-Type: application/json" \
  -d '{
    "tweet_id": "9999999999999999999",
    "username": "testuser",
    "content": "Test tweet for Cybersec Platform API",
    "date": "2024-06-06T15:00:00",
    "url": "https://twitter.com/testuser/status/9999999999999999999",
    "likes": 10,
    "retweets": 2,
    "language": "en",
    "hashtags": ["cybersec", "test"],
    "category": "test",
    "severity": "LOW"
  }' | jq

# Depuis un fichier JSON
cat > /tmp/new_tweet.json << 'EOF'
{
  "tweet_id": "8888888888888888888",
  "username": "fileuser",
  "user_id": "777777777",
  "content": "Tweet created from JSON file",
  "date": "2024-06-06T16:00:00",
  "url": "https://twitter.com/fileuser/status/8888888888888888888",
  "likes": 250,
  "retweets": 50,
  "hashtags": ["cybersecurity", "infosec"],
  "mentions": ["@krebsongsecurity"],
  "category": "threat_intel",
  "severity": "CRITICAL"
}
EOF

curl -X POST http://localhost:8000/tweets/ \
  -H "Content-Type: application/json" \
  -d @/tmp/new_tweet.json | jq
```

**Réponse (201)** : Voir la structure tweet complète.

---

### 📤 4. POST /tweets/batch - Créer plusieurs tweets (Batch)

**⭐ Endpoint principal utilisé par le Twitter Service**

```bash
# Créer 3 tweets en batch
curl -X POST http://localhost:8000/tweets/batch \
  -H "Content-Type: application/json" \
  -d '[
    {
      "tweet_id": "1111111111111111111",
      "username": "user1",
      "content": "First batch tweet",
      "date": "2024-06-06T10:00:00",
      "url": "https://twitter.com/user1/status/1111111111111111111",
      "likes": 50,
      "retweets": 10
    },
    {
      "tweet_id": "2222222222222222222",
      "username": "user2",
      "content": "Second batch tweet",
      "date": "2024-06-06T11:00:00",
      "url": "https://twitter.com/user2/status/2222222222222222222",
      "likes": 100,
      "retweets": 20
    }
  ]' | jq

# Depuis un fichier
curl -X POST http://localhost:8000/tweets/batch \
  -H "Content-Type: application/json" \
  -d @/tmp/tweets_batch.json | jq
```

**Réponse (200)** :
```json
{"message": "2 tweets créés, 0 ignorés (déjà existants)", "detail": "Total traité: 2"}
```

---

### ✏️ 5. PUT /tweets/{tweet_id} - Mettre à jour un tweet

```bash
# Mettre à jour les métriques
curl -X PUT http://localhost:8000/tweets/1234567890123456789 \
  -H "Content-Type: application/json" \
  -d '{
    "tweet_id": "1234567890123456789",
    "username": "krebsongsecurity",
    "likes": 200,
    "retweets": 75,
    "views": 15000
  }' | jq

# Mettre à jour la catégorie et la sévérité
curl -X PUT http://localhost:8000/tweets/1234567890123456789 \
  -H "Content-Type: application/json" \
  -d '{
    "tweet_id": "1234567890123456789",
    "username": "krebsongsecurity",
    "category": "critical_vulnerability",
    "severity": "CRITICAL"
  }' | jq
```

**Réponse (200)** : Voir la structure tweet complète.

---

### 🗑️ 6. DELETE /tweets/{tweet_id} - Supprimer un tweet

```bash
# Supprimer un tweet
curl -X DELETE http://localhost:8000/tweets/1234567890123456789 | jq

# Supprimer avec vérification
TWEET_ID="1234567890123456789"
if curl -X DELETE -s -w "\n%{http_code}" http://localhost:8000/tweets/$TWEET_ID | grep -q "200"; then
    echo "✅ Tweet $TWEET_ID supprimé"
fi
```

**Réponse (200)** :
```json
{"message": "Tweet 1234567890123456789 supprimé avec succès"}
```

---

### 🗑️ 7. DELETE /tweets/?confirm=true - Supprimer TOUS les tweets

**⚠️ DANGER - Supprime tous les tweets**

```bash
# Supprimer TOUS les tweets (nécessite confirmation)
curl -X DELETE "http://localhost:8000/tweets/?confirm=true" | jq

# Sans confirmation (erreur)
curl -X DELETE http://localhost:8000/tweets/ | jq
```

**Réponse (200)** :
```json
{"message": "250 tweets supprimés"}
```

**Erreur (400)** :
```json
{"detail": "La suppression de tous les tweets nécessite confirm=true"}
```

---

### 📊 8. GET /tweets/stats - Statistiques des tweets

```bash
# Statistiques globales
curl -s http://localhost:8000/tweets/stats | jq

# Statistiques des 7 derniers jours
curl -s "http://localhost:8000/tweets/stats?days=7" | jq

# Statistiques pour un utilisateur spécifique
curl -s "http://localhost:8000/tweets/stats?username=krebsongsecurity" | jq

# Statistiques par hashtag
curl -s "http://localhost:8000/tweets/stats" | jq '.by_hashtag'

# Statistiques par langue
curl -s "http://localhost:8000/tweets/stats" | jq '.by_language'

# Affichage formaté
STATS=$(curl -s http://localhost:8000/tweets/stats)
echo "Total: $(echo $STATS | jq '.total')"
echo "Moyenne likes: $(echo $STATS | jq '.avg_likes')"
echo "Par utilisateur: $(echo $STATS | jq '.by_username')"
```

**Réponse** :
```json
{
  "total": 250,
  "by_username": {"krebsongsecurity": 50, "taviso": 30, "others": 170},
  "by_hashtag": {"cybersecurity": 80, "vulnerability": 60, "CVE": 35},
  "by_language": {"en": 200, "fr": 20, "es": 15, "other": 15},
  "by_day": {"2026-06-06": 50, "2026-06-05": 75},
  "avg_likes": 75.5,
  "avg_retweets": 15.2
}
```

---

## 🎯 Exemples Avancés

### 🔹 Collecte Twitter Complète

```bash
#!/bin/bash
echo "=== Collecte Twitter ==="

# Collecter les tweets (simuler le Twitter Service)
docker-compose run twitter python -m twitter_service.main \
  --queries cybersecurity,vulnerability,infosec \
  --days 7 \
  --limit 50 > /dev/null 2>&1

echo "✅ Collecte terminée"

# Vérifier le nombre de tweets
TWEET_COUNT=$(curl -s http://localhost:8000/tweets/stats | jq '.total')
echo "Total tweets: $TWEET_COUNT"

# Lister les 10 tweets les plus populaires
curl -s "http://localhost:8000/tweets/?page_size=100" | \
  jq -r '.items | sort_by(-.likes) | .[:10] | .[] | "@\(.username): \(.likes) likes - \(.content[:60])"'
```

### 🔹 Analyse des Tweets

```bash
# Trouver les tweets sans catégorie
curl -s "http://localhost:8000/tweets/?page_size=10000" | \
  jq '.items[] | select(.category == null or .category == "") | "@\(.username): \(.content[:80])"'

# Trouver les tweets avec beaucoup de retweets (>50)
curl -s "http://localhost:8000/tweets/?page_size=10000" | \
  jq '.items[] | select(.retweets > 50) | "@\(.username): \(.retweets) RT - \(.content[:60])"'

# Compter les tweets par hashtag
curl -s http://localhost:8000/tweets/stats | jq '.by_hashtag | to_entries | sort_by(-.value) | .[:10]'

# Trouver les tweets avec des URLs
curl -s "http://localhost:8000/tweets/?page_size=10000" | \
  jq '.items[] | select(.urls != null and .urls != [] and .urls[0] != null) | "\(.username): \(.urls[0])"'
```

### 🔹 Export des Tweets

```bash
# Exporter tous les tweets dans un fichier
curl -s "http://localhost:8000/tweets/?page_size=10000" | jq '.items' > tweets_export_$(date +%Y%m%d).json

# Exporter les tweets d'un utilisateur
curl -s "http://localhost:8000/tweets/?username=krebsongsecurity&page_size=10000" | jq '.items' > krebs_tweets.json

# Exporter les tweets avec hashtag cybersecurity
curl -s "http://localhost:8000/tweets/?hashtag=cybersecurity&page_size=10000" | jq '.items' > cybersecurity_tweets.json
```

### 🔹 Surveillance Tweets + CVE

```bash
#!/bin/bash
echo "🔍 Surveillance combinée CVE + Tweets"
echo "====================================="

while true; do
    echo ""
    echo "$(date) - Vérification..."
    
    # CVE
    NEW_CVES=$(curl -s "http://localhost:8000/cves/?days=0" | jq '.total')
    CRITICAL_CVE=$(curl -s "http://localhost:8000/cves/?days=0&severity=CRITICAL" | jq '.total')
    echo "   📋 CVE: $NEW_CVES nouvelles, $CRITICAL_CVE CRITICAL"
    
    # Tweets
    NEW_TWEETS=$(curl -s "http://localhost:8000/tweets/?days=0" | jq '.total')
    POPULAR_TWEETS=$(curl -s "http://localhost:8000/tweets/?days=0&min_likes=50" | jq '.total')
    echo "   🐦 Tweets: $NEW_TWEETS nouveaux, $POPULAR_TWEETS populaires (>50 likes)"
    
    # Statistiques globales
    TOTAL_CVE=$(curl -s http://localhost:8000/cves/stats | jq '.total')
    TOTAL_TWEETS=$(curl -s http://localhost:8000/tweets/stats | jq '.total')
    echo "   📊 Total: $TOTAL_CVE CVE, $TOTAL_TWEETS tweets"
    
    sleep 300
done
```

---

## 📚 Voir aussi

- [API_CURL_GUIDE_PART1.md](./API_CURL_GUIDE_PART1.md) - Health Check + CVE endpoints
- [API_CURL_GUIDE_PART3.md](./API_CURL_GUIDE_PART3.md) - Comptes Twitter + Exemples Pratiques
- [DOCUMENTATION_COMPLETE.md](./DOCUMENTATION_COMPLETE.md) - Documentation complète

---

*© 2026 Cybersec Platform - Tous droits réservés*
