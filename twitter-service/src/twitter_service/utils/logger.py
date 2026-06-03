"""Configuration des logs pour le Twitter Service."""

import logging
import sys
from pathlib import Path

from twitter_service.config import config


def setup_logger(name: str) -> logging.Logger:
    """Configurer le logger pour un module.
    
    Args:
        name: Nom du module pour le logger
        
    Returns:
        Logger configuré
    """
    # Créer les répertoires si nécessaire
    Path("./logs").mkdir(parents=True, exist_ok=True)
    
    # Créer le logger
    logger = logging.getLogger(name)
    
    # Définir le niveau de log
    log_level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Formatter
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Handlers : Console + Fichier
    handlers = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/twitter_service.log")
    ]
    
    for handler in handlers:
        handler.setFormatter(formatter)
        handler.setLevel(log_level)
        logger.addHandler(handler)
    
    # Éviter la propagation aux loggers parents
    logger.propagate = False
    
    return logger
