# 📡 Guide Curl - Cybersec Platform API (Partie 1)

> **Health Check + CVE Endpoints**
> Version : 0.2.0 | Base URL : `http://localhost:8000`

---

## 📖 Table des Matières

1. [⚡ Prérequis](#-prérequis)
2. [🏥 Endpoints Health Check](#-endpoints-health-check)
3. [📋 Endpoints CVE (11 endpoints)](#-endpoints-cve-11-endpoints)
4. [🎯 Exemples CVE Avancés](#-exemples-cve-avancés)

---

## ⚡ Prérequis

**Démarrer l'API** :
```bash
# Avec Docker
docker-compose -f docker-compose-simple.yml up -d api

# Ou manuellement
cd api-service
uvicorn api.main:app --host 0.0.0.0 --port 8000

# Vérifier
curl http://localhost:8000/health
```

---

## 🏥 Endpoints Health Check

### 1️⃣ GET / - Message de Bienvenue

```bash
curl http://localhost:8000/
curl -s http://localhost:8000/ | jq
```

**Réponse** :
```json
{"message": "Cybersec API - OK", "version": "0.1.0"}
```

---

### 2️⃣ GET /health - Vérification de Santé

```bash
curl http://localhost:8000/health
curl -s http://localhost:8000/health | jq

# Dans un script
HEALTH=$(curl -s http://localhost:8000/health)
if echo "$HEALTH" | grep -q '"status": "healthy"'; then
    echo "✅ API est en bonne santé"
fi
```

**Réponse** :
```json
{"status": "healthy", "timestamp": "2026-06-06T14:30:45.123456"}
```

---

## 📋 Endpoints CVE (11 endpoints)

### 📄 1. GET /cves/ - Lister les CVE

#### Basique
```bash
# Toutes les CVE (page 1, 20 éléments)
curl -s http://localhost:8000/cves/ | jq

# Avec pagination
curl -s "http://localhost:8000/cves/?page=1&page_size=50" | jq
```

#### Filtres
```bash
# Par sévérité
curl -s "http://localhost:8000/cves/?severity=CRITICAL" | jq
curl -s "http://localhost:8000/cves/?severity=HIGH" | jq

# Par score minimum
curl -s "http://localhost:8000/cves/?min_score=7.0" | jq
curl -s "http://localhost:8000/cves/?min_score=9.0" | jq

# Par date (jours)
curl -s "http://localhost:8000/cves/?days=7" | jq
curl -s "http://localhost:8000/cves/?days=30" | jq
```

#### Combinaisons
```bash
# CRITICAL des 7 derniers jours avec score >= 9.0
curl -s "http://localhost:8000/cves/?severity=CRITICAL&days=7&min_score=9.0" | jq

# HIGH des 30 derniers jours, 50 éléments
curl -s "http://localhost:8000/cves/?severity=HIGH&days=30&page_size=50" | jq
```

**Réponse** :
```json
{
  "total": 150,
  "page": 1,
  "page_size": 20,
  "items": [
    {
      "id": 1,
      "cve_id": "CVE-2024-12345",
      "published_at": "2024-05-20T10:00:00",
      "last_modified": "2024-05-21T12:00:00",
      "description": "Buffer overflow vulnerability...",
      "cvss_score": 7.5,
      "cvss_severity": "HIGH",
      "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
      "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-12345"],
      "created_at": "2026-05-22T20:00:00",
      "updated_at": "2026-05-22T20:00:00"
    }
  ]
}
```

---

### 📄 2. GET /cves/{cve_id} - Détails d'une CVE

```bash
# Récupérer une CVE spécifique
curl -s http://localhost:8000/cves/CVE-2024-12345 | jq

# Vérifier si une CVE existe
CVE_ID="CVE-2024-12345"
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/cves/$CVE_ID | grep -q "200"; then
    echo "✅ CVE $CVE_ID existe"
else
    echo "❌ CVE $CVE_ID non trouvée"
fi
```

**Réponse (200)** : Voir la structure complète dans la Partie 1 de la documentation.

**Réponse (404)** :
```json
{"detail": "CVE CVE-9999-9999 non trouvée"}
```

---

### 📤 3. POST /cves/ - Créer une CVE

```bash
# Créer une CVE simple
curl -X POST http://localhost:8000/cves/ \
  -H "Content-Type: application/json" \
  -d '{
    "cve_id": "CVE-2024-TEST-001",
    "published_at": "2024-06-01T10:00:00",
    "last_modified": "2024-06-01T10:00:00",
    "description": "Test vulnerability for API",
    "cvss_score": 7.5,
    "cvss_severity": "HIGH",
    "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
    "references": ["https://example.com/cve-2024-test-001"]
  }' | jq

# Depuis un fichier
cat > /tmp/new_cve.json << 'EOF'
{
  "cve_id": "CVE-2024-TEST-002",
  "published_at": "2024-06-01T12:00:00",
  "last_modified": "2024-06-01T12:00:00",
  "description": "Another test CVE",
  "cvss_score": 9.8,
  "cvss_severity": "CRITICAL",
  "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
  "references": ["https://example.com/cve-2024-test-002"]
}
EOF

curl -X POST http://localhost:8000/cves/ \
  -H "Content-Type: application/json" \
  -d @/tmp/new_cve.json | jq
```

**Réponse (201)** :
```json
{
  "id": 151,
  "cve_id": "CVE-2024-TEST-001",
  "published_at": "2024-06-01T10:00:00",
  "last_modified": "2024-06-01T10:00:00",
  "description": "Test vulnerability for API",
  "cvss_score": 7.5,
  "cvss_severity": "HIGH",
  "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
  "references": ["https://example.com/cve-2024-test-001"],
  "created_at": "2026-06-06T14:30:00",
  "updated_at": "2026-06-06T14:30:00"
}
```

**Erreur (409 Conflict)** :
```json
{"detail": "CVE CVE-2024-TEST-001 déjà en base de données"}
```

---

### 📤 4. POST /cves/batch - Créer plusieurs CVE (Batch)

**⭐ Endpoint principal utilisé par l'Aggregator Service**

```bash
# Créer 3 CVE en batch
curl -X POST http://localhost:8000/cves/batch \
  -H "Content-Type: application/json" \
  -d '[
    {
      "cve_id": "CVE-2024-BATCH-001",
      "published_at": "2024-06-01T10:00:00",
      "last_modified": "2024-06-01T10:00:00",
      "description": "First batch CVE",
      "cvss_score": 8.5,
      "cvss_severity": "HIGH",
      "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
      "references": ["https://example.com/cve-batch-001"]
    },
    {
      "cve_id": "CVE-2024-BATCH-002",
      "published_at": "2024-06-01T11:00:00",
      "last_modified": "2024-06-01T11:00:00",
      "description": "Second batch CVE",
      "cvss_score": 6.5,
      "cvss_severity": "MEDIUM"
    },
    {
      "cve_id": "CVE-2024-BATCH-001",  # Doublon - sera ignoré
      "published_at": "2024-06-01T12:00:00",
      "last_modified": "2024-06-01T12:00:00",
      "description": "Duplicate - should be skipped"
    }
  ]' | jq

# Depuis un fichier
curl -X POST http://localhost:8000/cves/batch \
  -H "Content-Type: application/json" \
  -d @/tmp/cves_batch.json | jq
```

**Réponse (200)** :
```json
{"message": "2 CVE créées, 1 ignorées (déjà existantes)", "detail": "Total traité: 3"}
```

---

### ✏️ 5. PUT /cves/{cve_id} - Mettre à jour une CVE

```bash
# Mettre à jour la description et le score
curl -X PUT http://localhost:8000/cves/CVE-2024-TEST-001 \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Updated description - critical vulnerability",
    "cvss_score": 9.8,
    "cvss_severity": "CRITICAL"
  }' | jq

# Mettre à jour le vecteur seulement
curl -X PUT http://localhost:8000/cves/CVE-2024-TEST-001 \
  -H "Content-Type: application/json" \
  -d '{"vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"}' | jq
```

**Réponse (200)** : Voir la structure CVE complète.

**Erreur (404)** :
```json
{"detail": "CVE CVE-9999-9999 non trouvée"}
```

---

### 🗑️ 6. DELETE /cves/{cve_id} - Supprimer une CVE

```bash
# Supprimer une CVE
curl -X DELETE http://localhost:8000/cves/CVE-2024-TEST-001 | jq

# Supprimer avec vérification
CVE_ID="CVE-2024-TEST-001"
if curl -X DELETE -s -w "\n%{http_code}" http://localhost:8000/cves/$CVE_ID | grep -q "200"; then
    echo "✅ CVE $CVE_ID supprimée"
fi
```

**Réponse (200)** :
```json
{"message": "CVE CVE-2024-TEST-001 supprimée avec succès"}
```

---

### 🗑️ 7. DELETE /cves/?confirm=true - Supprimer TOUTES les CVE

**⚠️ DANGER - Supprime toutes les CVE**

```bash
# Supprimer TOUTES les CVE (nécessite confirmation)
curl -X DELETE "http://localhost:8000/cves/?confirm=true" | jq

# Sans confirmation (erreur)
curl -X DELETE http://localhost:8000/cves/ | jq

# Avec vérification interactive
read -p "Supprimer TOUTES les CVE? (yes/no): " confirm
if [ "$confirm" = "yes" ]; then
    curl -X DELETE "http://localhost:8000/cves/?confirm=true" | jq
fi
```

**Réponse (200)** :
```json
{"message": "150 CVE supprimées"}
```

**Erreur (400)** :
```json
{"detail": "La suppression de toutes les CVE nécessite confirm=true"}
```

---

### 📊 8. GET /cves/stats - Statistiques des CVE

```bash
# Statistiques globales
curl -s http://localhost:8000/cves/stats | jq

# Statistiques des 7 derniers jours
curl -s "http://localhost:8000/cves/stats?days=7" | jq

# Statistiques des 30 derniers jours
curl -s "http://localhost:8000/cves/stats?days=30" | jq

# Par sévérité seulement
curl -s "http://localhost:8000/cves/stats" | jq '.by_severity'

# Par jour seulement
curl -s "http://localhost:8000/cves/stats?days=7" | jq '.by_day'

# Affichage formaté
STATS=$(curl -s http://localhost:8000/cves/stats)
echo "Total: $(echo $STATS | jq '.total')"
echo "CRITICAL: $(echo $STATS | jq '.by_severity.CRITICAL // 0')"
echo "HIGH: $(echo $STATS | jq '.by_severity.HIGH // 0')"
echo "MEDIUM: $(echo $STATS | jq '.by_severity.MEDIUM // 0')"
echo "LOW: $(echo $STATS | jq '.by_severity.LOW // 0')"
```

**Réponse** :
```json
{
  "total": 150,
  "by_severity": {"CRITICAL": 15, "HIGH": 45, "MEDIUM": 70, "LOW": 20},
  "by_day": {
    "2026-06-06": 10,
    "2026-06-05": 20,
    "2026-06-04": 15
  }
}
```

---

## 🎯 Exemples CVE Avancés

### 🔹 Collecte et Vérification

```bash
#!/bin/bash
echo "=== Collecte et Vérification CVE ==="

# Collecter des CVE (simuler l'Aggregator)
docker-compose run aggregator python -m cybersec_aggregator.main --days 1 --send-to-api > /dev/null 2>&1

# Vérifier le nombre de CVE
CVE_COUNT=$(curl -s http://localhost:8000/cves/stats | jq '.total')
echo "Total CVE: $CVE_COUNT"

# Lister les 5 dernières CVE
curl -s "http://localhost:8000/cves/?page=1&page_size=5" | jq '.items[] | .cve_id, .cvss_score, .cvss_severity'

# Compter par sévérité
curl -s http://localhost:8000/cves/stats | jq '.by_severity'
```

### 🔹 Export des CVE

```bash
# Exporter toutes les CVE dans un fichier
curl -s "http://localhost:8000/cves/?page_size=10000" | jq '.items' > cves_export_$(date +%Y%m%d).json

# Exporter les CVE CRITICAL
curl -s "http://localhost:8000/cves/?severity=CRITICAL&page_size=10000" | jq '.items' > critical_cves.json

# Exporter les CVE des 7 derniers jours
curl -s "http://localhost:8000/cves/?days=7&page_size=10000" | jq '.items' > recent_cves.json
```

### 🔹 Recherche Avancée

```bash
# Trouver les CVE sans description
curl -s "http://localhost:8000/cves/?page_size=10000" | jq '.items[] | select(.description == null) | .cve_id'

# Trouver les CVE avec score CVSS manquant
curl -s "http://localhost:8000/cves/?page_size=10000" | jq '.items[] | select(.cvss_score == null) | .cve_id'

# Trouver les CVE modifiées récemment
curl -s "http://localhost:8000/cves/?page_size=10000" | \
  jq '.items | sort_by(.last_modified) | reverse | .[:10] | .[] | "\(.cve_id) - \(.last_modified)"'
```

### 🔹 Script de Surveillance

```bash
#!/bin/bash
# monitor_cves.sh - Surveillance des nouvelles CVE

while true; do
    echo "$(date) - Vérification des nouvelles CVE..."
    
    # Compter les CVE d'aujourd'hui
    TODAY=$(date +%Y-%m-%d)
    NEW_CVES=$(curl -s "http://localhost:8000/cves/?days=0" | jq '.total')
    echo "   📊 Nouvelles CVE aujourd'hui: $NEW_CVES"
    
    # Vérifier les CRITICAL
    CRITICAL=$(curl -s "http://localhost:8000/cves/?days=0&severity=CRITICAL" | jq '.total')
    if [ "$CRITICAL" -gt 0 ]; then
        echo "   🔴 $CRITICAL nouvelles CVE CRITICAL"
        curl -s "http://localhost:8000/cves/?days=0&severity=CRITICAL" | \
          jq -r '.items[] | "   - \(.cve_id): \(.cvss_score)"'
    fi
    
    sleep 300  # 5 minutes
done
```

---

## 📚 Voir aussi

- [API_CURL_GUIDE_PART2.md](./API_CURL_GUIDE_PART2.md) - Analyses + Tweets endpoints
- [API_CURL_GUIDE_PART3.md](./API_CURL_GUIDE_PART3.md) - Accounts + Exemples Pratiques
- [DOCUMENTATION_COMPLETE.md](./DOCUMENTATION_COMPLETE.md) - Documentation complète

---

*© 2026 Cybersec Platform - Tous droits réservés*
