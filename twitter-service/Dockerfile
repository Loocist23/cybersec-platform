# Dockerfile pour le Twitter Service - Version Debian slim (plus stable)
# Microservice pour récupérer les tweets depuis X (Twitter)

FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances système nécessaires (Debian utilise apt)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev g++ libstdc++6 && \
    rm -rf /var/lib/apt/lists/*

# Installer uv
RUN pip install --no-cache-dir uv

# Copier les fichiers de dépendances
COPY pyproject.toml uv.lock README.md .env .

# Synchroniser les dépendances
RUN uv sync

# Nettoyer les dépendances de build (après compilation de snscrape)
RUN apt-get remove -y gcc python3-dev g++ && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Créer les répertoires runtime (en root)
RUN mkdir -p /app/data /app/logs

# Créer l'utilisateur non-root
RUN useradd --create-home --shell /bin/bash appuser
# Donner les permissions sur .venv et les répertoires à appuser
RUN chown -R appuser:appuser /app/.venv /app/data /app/logs
USER appuser

# Copier le code source
COPY --chown=appuser:appuser src/ /app/src/

# Définir les variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src
ENV PATH="/home/appuser/.venv/bin:$PATH"

# Commande par défaut
CMD ["uv", "run", "python", "-m", "twitter_service.main", "--queries", "cybersecurity,vulnerability,infosec,CVE,malware,hacking,exploit,zero-day"]
