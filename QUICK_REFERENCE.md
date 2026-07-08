# 📋 Quick Reference - Cybersec Platform API

> **Tableau Récapitulatif de tous les Endpoints**
> Version : 0.2.0 | Base URL : `http://localhost:8000`
> **Total : 20 Endpoints** (2 Health + 11 CVE + 7 Analyses)

---

## 🎯 Navigation Rapide

- [🏥 Health Check](#-health-check) - 2 endpoints
- [📋 CVE Endpoints](#-cve-endpoints) - 11 endpoints
- [🧠 Analyses IA](#-analyses-ia) - 7 endpoints

---

## 🏥 Health Check (2 endpoints)

| Méthode | Endpoint | Description | Exemple | Réponse |
|---------|----------|-------------|---------|---------|
| **GET** | `/` | Message de bienvenue | `curl http://localhost:8000/` | `{"message": "Cybersec API - OK", "version": "0.2.0"}` |
| **GET** | `/health` | Vérification de santé | `curl http://localhost:8000/health` | `{"status": "healthy", "timestamp": "..."}` |

---

## 📋 CVE Endpoints (11 endpoints)

| Méthode | Endpoint | Description | Exemple | Réponse (200/201) | Erreurs |
|---------|----------|-------------|---------|-------------------|---------|
| **GET** | `/cves/` | Liste des CVE (paginée) | `curl "http://localhost:8000/cves/?page=1&page_size=50&severity=CRITICAL&days=7"` | `{"total": N, "page": 1, "page_size": 50, "items": [...]}` | - |
| **GET** | `/cves/{cve_id}` | Détails d'une CVE | `curl http://localhost:8000/cves/CVE-2024-12345` | Voir structure CVE | `404` si non trouvée |
| **POST** | `/cves/` | Créer une CVE | `curl -X POST http://localhost:8000/cves/ -H "Content-Type: application/json" -d '{"cve_id": "CVE-TEST", ...}'` | Voir structure CVE | `409` si doublon |
| **POST** | `/cves/batch` | **Créer plusieurs CVE** ⭐ | `curl -X POST http://localhost:8000/cves/batch -H "Content-Type: application/json" -d '[ {...}, {...} ]'` | `{"message": "X créées, Y ignorées"}` | - |
| **PUT** | `/cves/{cve_id}` | Mettre à jour une CVE | `curl -X PUT http://localhost:8000/cves/CVE-TEST -H "Content-Type: application/json" -d '{"description": "..."}'` | Voir structure CVE | `404` si non trouvée |
| **DELETE** | `/cves/{cve_id}` | Supprimer une CVE | `curl -X DELETE http://localhost:8000/cves/CVE-TEST` | `{"message": "CVE ... supprimée"}` | `404` si non trouvée |
| **DELETE** | `/cves/?confirm=true` | ⚠️ Supprimer TOUTES les CVE | `curl -X DELETE "http://localhost:8000/cves/?confirm=true"` | `{"message": "N CVE supprimées"}` | `400` si confirm manquant |
| **GET** | `/cves/stats` | Statistiques CVE | `curl "http://localhost:8000/cves/stats?days=7"` | `{"total": N, "by_severity": {...}, "by_day": {...}}` | - |

### 📊 Paramètres CVE (GET /cves/)

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `page` | int | 1 | Numéro de page |
| `page_size` | int | 20 | Éléments par page (1-100) |
| `severity` | enum | null | LOW, MEDIUM, HIGH, CRITICAL |
| `min_score` | float | null | Score CVSS minimum |
| `days` | int | null | Filtrer par les N derniers jours |

### 📥 Structure CVE (POST/PUT)

```json
{
  "cve_id": "CVE-2024-12345",           // String, requis, unique
  "published_at": "2024-05-20T10:00:00", // DateTime, requis
  "last_modified": "2024-05-21T12:00:00", // DateTime, requis
  "description": "Vulnerability description", // String, optionnel
  "cvss_score": 7.5,                      // Float (0-10), optionnel
  "cvss_severity": "HIGH",               // LOW/MEDIUM/HIGH/CRITICAL, optionnel
  "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H", // String, optionnel
  "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-12345"] // List[str], optionnel
}
```

### 📤 Structure Réponse CVE

```json
{
  "id": 1,                                // ID interne
  "cve_id": "CVE-2024-12345",
  "published_at": "2024-05-20T10:00:00",
  "last_modified": "2024-05-21T12:00:00",
  "description": "Vulnerability description",
  "cvss_score": 7.5,
  "cvss_severity": "HIGH",
  "vector": "CVSS:3.1/...",
  "references": [...],
  "created_at": "2026-06-06T14:30:00",
  "updated_at": "2026-06-06T14:30:00"
}
```

---

## 🧠 Analyses IA (7 endpoints)

| Méthode | Endpoint | Description | Exemple | Réponse (200/201) | Erreurs |
|---------|----------|-------------|---------|-------------------|---------|
| **GET** | `/analyses/` | Liste des analyses (paginée) | `curl "http://localhost:8000/analyses/?page=1&page_size=20&status_filter=completed&severity=CRITICAL&days=7"` | `{"total": N, "page": 1, "page_size": 20, "items": [...]}` | - |
| **GET** | `/analyses/{analysis_id}/` | Détails d'une analyse | `curl http://localhost:8000/analyses/analysis-20240523-001/` | Voir structure Analyse | `404` si non trouvée |
| **POST** | `/analyses/` | **Créer une analyse** ⭐ | `curl -X POST http://localhost:8000/analyses/ -H "Content-Type: application/json" -d '{...}'` | `{"message": "Analyse ... créée", "analysis_id": "...", "analysis": {...}}` | - |
| **PUT** | `/analyses/{analysis_id}/` | Mettre à jour une analyse | `curl -X PUT http://localhost:8000/analyses/analysis-20240523-001/ -H "Content-Type: application/json" -d '{...}'` | Voir structure Analyse | `404` si non trouvée |
| **DELETE** | `/analyses/{analysis_id}/` | Supprimer une analyse | `curl -X DELETE http://localhost:8000/analyses/analysis-20240523-001/` | `{"message": "Analyse ... supprimée", "detail": "ID interne: N"}` | `404` si non trouvée |
| **DELETE** | `/analyses/?confirm=true` | ⚠️ Supprimer TOUTES les analyses | `curl -X DELETE "http://localhost:8000/analyses/?confirm=true"` | `{"message": "N analyses et M mappings supprimés"}` | `400` si confirm manquant |
| **GET** | `/analyses/stats/` | Statistiques des analyses | `curl "http://localhost:8000/analyses/stats/?days=7"` | `{"total": N, "by_status": {...}, "by_severity": {...}, "avg_confidence": X}` | - |

### 📊 Paramètres Analyses (GET /analyses/)

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `page` | int | 1 | Numéro de page |
| `page_size` | int | 20 | Éléments par page (1-100) |
| `status_filter` | enum | null | pending/processing/completed/failed |
| `severity` | enum | null | LOW/MEDIUM/HIGH/CRITICAL |
| `days` | int | null | Filtrer par les N derniers jours |

### 📥 Structure Analyse (POST/PUT)

```json
{
  "analysis_id": "analysis-20240523-001",     // String, requis, unique
  "title": "Analyse des vulnérabilités Apache",
  "summary": "15 vulnérabilités critiques détectées...",
  "severity_overall": "CRITICAL",           // LOW/MEDIUM/HIGH/CRITICAL
  "confidence": 0.95,                       // Float (0-1)
  "status": "completed",                    // pending/processing/completed/failed
  "extra_data": {"model": "mistral-tiny", "tokens_used": 5000}, // Dict, optionnel
  "grouped_cves": [
    {
      "group_id": "apache-tomcat-2024",
      "cve_ids": ["CVE-2024-1234", "CVE-2024-5678"],
      "common_vendor": "Apache",
      "common_product": "Apache Tomcat",
      "common_cwe": ["CWE-20", "CWE-287"],
      "similarity_score": 0.92,
      "total_cves": 2,
      "avg_cvss_score": 9.5,
      "max_cvss_score": 9.8
    }
  ]
}
```

### 📤 Structure Réponse Analyse

```json
{
  "id": 1,                                  // ID interne
  "analysis_id": "analysis-20240523-001",
  "title": "Analyse des vulnérabilités Apache",
  "summary": "15 vulnérabilités...",
  "severity_overall": "CRITICAL",
  "confidence": 0.95,
  "status": "completed",
  "extra_data": {...},
  "grouped_cves": [...],
  "created_at": "2024-05-23T14:30:00",
  "updated_at": "2024-05-23T14:30:00"
}
```

---

## 📊 Statistiques Globales

### 🔢 Compte des Endpoints

| Catégorie | Nombre | Endpoints |
|----------|--------|-----------|
| **Health Check** | 2 | GET /, GET /health |
| **CVE** | 11 | GET /cves/, GET /cves/{id}, POST /cves/, POST /cves/batch, PUT /cves/{id}, DELETE /cves/{id}, DELETE /cves/, GET /cves/stats |
| **Analyses** | 7 | GET /analyses/, GET /analyses/{id}/, POST /analyses/, PUT /analyses/{id}/, DELETE /analyses/{id}/, DELETE /analyses/, GET /analyses/stats/ |
| **TOTAL** | **20** | - |

---

## 🏷️ Légende et Symboles

| Symbole | Signification |
|---------|----------------|
| ⭐ | Endpoint principal utilisé par les services (Aggregator, AI) |
| ⚠️ | Opération dangereuse (suppression de données) |
| **GRAS** | Nom de la catégorie ou endpoint important |

---

## 🎯 Endpoints par Utilisation

### 📥 Utilisé par l'Aggregator Service
- **POST /cves/batch** - Envoi des CVE collectées depuis NVD

### 🧠 Utilisé par l'AI Service
- **GET /cves/** - Récupération des CVE à analyser
- **POST /analyses/** - Envoi des analyses générées

---

## 🔧 Commandes de Base

### Vérification de Santé
```bash
# API en bonne santé ?
curl -s http://localhost:8000/health | jq '.status'

# Version de l'API
curl -s http://localhost:8000/ | jq '.version'
```

### Statistiques Rapides
```bash
# Nombre total de CVE
curl -s http://localhost:8000/cves/stats | jq '.total'

# Nombre total d'analyses
curl -s http://localhost:8000/analyses/stats/ | jq '.total'
```

---

## 📚 Documentation Complète

Pour des exemples détaillés et des scripts avancés :

- **[DOCUMENTATION_COMPLETE.md](./DOCUMENTATION_COMPLETE.md)** - Architecture complète, microservices, base de données, déploiement
- **[API_CURL_GUIDE_PART1.md](./API_CURL_GUIDE_PART1.md)** - Health Check + 11 endpoints CVE avec exemples avancés
- **[API_CURL_GUIDE_PART2.md](./API_CURL_GUIDE_PART2.md)** - 7 endpoints Analyses avec exemples avancés

---

## 🔗 Références Externes

- [cURL Documentation](https://curl.se/docs/) - Documentation officielle
- [jq Manual](https://stedolan.github.io/jq/manual/) - Manuel complet
- [FastAPI Documentation](https://fastapi.tiangolo.com/) - Framework API
- [PostgreSQL Documentation](https://www.postgresql.org/docs/) - Base de données
- [NVD API Documentation](https://nvd.nist.gov/developers/requests) - Source des CVE
- [Mistral AI API](https://docs.mistral.ai/) - Analyse IA

---

*© 2026 Cybersec Platform - Tous droits réservés*
