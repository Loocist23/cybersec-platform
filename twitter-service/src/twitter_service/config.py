"""Configuration du Twitter Service."""

import os
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()


class Config:
    """Configuration centrale du projet."""

    # API Cybersec (pour envoyer les données)
    API_URL: str = os.getenv("API_URL", "http://localhost:8000")
    API_BASE_URL: str = os.getenv("API_BASE_URL", API_URL)
    TWEETS_ENDPOINT: str = f"{API_BASE_URL}/tweets/"
    ACCOUNTS_ENDPOINT: str = f"{API_BASE_URL}/tweets/accounts/"

    # Twitter API Configuration
    TWITTER_BEARER_TOKEN: str = os.getenv("TWITTER_BEARER_TOKEN", "")
    MAX_TWEETS_PER_REQUEST: int = int(os.getenv("MAX_TWEETS_PER_REQUEST", "50"))
    MAX_ACCOUNTS_PER_REQUEST: int = int(os.getenv("MAX_ACCOUNTS_PER_REQUEST", "20"))
    REQUEST_DELAY: float = float(os.getenv("REQUEST_DELAY", "5"))  # Secondes entre requêtes

    # Recherche par défaut
    SEARCH_QUERIES: List[str] = os.getenv(
        "SEARCH_QUERIES", 
        "cybersecurity,vulnerability,infosec,CVE,malware,hacking,exploit,zero-day"
    ).split(",")
    SEARCH_DAYS_BACK: int = int(os.getenv("SEARCH_DAYS_BACK", "7"))

    # Filtrage
    MIN_LIKES: int = int(os.getenv("MIN_LIKES", "0"))
    MIN_RETWEETS: int = int(os.getenv("MIN_RETWEETS", "0"))
    LANGUAGE: str = os.getenv("LANGUAGE", "en")

    # Rate Limiting
    MAX_REQUESTS_PER_MINUTE: int = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "30"))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Mode daemon
    DAEMON_INTERVAL_HOURS: int = int(os.getenv("DAEMON_INTERVAL_HOURS", "24"))

    # Chemins
    DATA_DIR: Path = Path("./data")
    LOGS_DIR: Path = Path("./logs")

    # Options de recherche
    INCLUDE_REPLIES: bool = os.getenv("INCLUDE_REPLIES", "false").lower() == "true"
    INCLUDE_RETWEETS: bool = os.getenv("INCLUDE_RETWEETS", "false").lower() == "true"

    @classmethod
    def ensure_directories(cls) -> None:
        """Créer les répertoires nécessaires."""
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.LOGS_DIR.mkdir(parents=True, exist_ok=True)


# Initialiser les répertoires
Config.ensure_directories()

# Exporter la config
config = Config()
