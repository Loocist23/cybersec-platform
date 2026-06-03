"""Client pour envoyer les données à l'API Cybersec."""

import logging
from typing import List, Optional

import requests

from twitter_service.config import config
from twitter_service.models.tweet import Tweet, TweetCreate, TwitterAccount
from twitter_service.utils.logger import setup_logger

logger = setup_logger(__name__)


class TwitterAPIClient:
    """Service client pour interagir avec l'API Cybersec.
    
    Ce service permet d'envoyer les tweets et comptes Twitter
    à l'API Service pour stockage.
    """

    def __init__(self) -> None:
        """Initialise le client API."""
        self.base_url = config.API_BASE_URL
        self.tweets_endpoint = config.TWEETS_ENDPOINT
        self.accounts_endpoint = config.ACCOUNTS_ENDPOINT
        
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "TwitterService/0.1.0",
            "Content-Type": "application/json",
        })

    def health_check(self) -> bool:
        """Vérifie que l'API est disponible.
        
        Returns:
            True si l'API répond, False sinon
        """
        try:
            response = self.session.get(
                f"{self.base_url}/health",
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check échoué: {e}")
            return False

    def create_tweet(self, tweet: Tweet) -> Optional[dict]:
        """Crée un tweet dans l'API.
        
        Args:
            tweet: Tweet à créer
            
        Returns:
            Réponse de l'API ou None en cas d'erreur
        """
        try:
            tweet_data = TweetCreate(
                tweet_id=tweet.tweet_id,
                username=tweet.username,
                user_id=tweet.user_id,
                content=tweet.content,
                date=tweet.date,
                url=str(tweet.url),
                likes=tweet.likes,
                retweets=tweet.retweets,
                replies=tweet.replies,
                quotes=tweet.quotes,
                views=tweet.views,
                is_retweet=tweet.is_retweet,
                is_quote=tweet.is_quote,
                is_reply=tweet.is_reply,
                language=tweet.language,
                hashtags=tweet.hashtags,
                mentions=tweet.mentions,
                urls=[str(u) for u in tweet.urls],
                images=[str(img) for img in tweet.images],
                videos=[str(vid) for vid in tweet.videos],
                category=tweet.category,
                severity=tweet.severity,
            )
            
            response = self.session.post(
                f"{self.tweets_endpoint}",
                json=tweet_data.model_dump(),
                timeout=30,
            )
            response.raise_for_status()
            
            logger.info(f"Tweet {tweet.tweet_id} créé avec succès")
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la création du tweet {tweet.tweet_id}: {e}")
            return None

    def create_tweets_batch(self, tweets: List[Tweet]) -> dict:
        """Crée plusieurs tweets en une seule requête.
        
        Args:
            tweets: Liste de tweets à créer
            
        Returns:
            Réponse de l'API
        """
        created_count = 0
        skipped_count = 0
        
        for tweet in tweets:
            result = self.create_tweet(tweet)
            if result:
                created_count += 1
            else:
                skipped_count += 1
        
        return {
            "message": f"{created_count} tweets créés, {skipped_count} ignorés",
            "created": created_count,
            "skipped": skipped_count,
            "total": len(tweets)
        }

    def create_account(self, account: TwitterAccount) -> Optional[dict]:
        """Crée un compte Twitter dans l'API.
        
        Args:
            account: Compte Twitter à créer
            
        Returns:
            Réponse de l'API ou None en cas d'erreur
        """
        try:
            account_data = {
                "username": account.username,
                "user_id": account.user_id,
                "display_name": account.display_name,
                "bio": account.bio,
                "followers_count": account.followers_count,
                "following_count": account.following_count,
                "tweet_count": account.tweet_count,
                "account_created_at": account.account_created_at.isoformat() if account.account_created_at else None,
                "verified": account.verified,
                "avatar_url": str(account.avatar_url) if account.avatar_url else None,
                "url": str(account.url) if account.url else None,
                "category": account.category,
            }
            
            response = self.session.post(
                f"{self.accounts_endpoint}",
                json=account_data,
                timeout=30,
            )
            response.raise_for_status()
            
            logger.info(f"Compte @{account.username} créé avec succès")
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la création du compte @{account.username}: {e}")
            return None

    def create_accounts_batch(self, accounts: List[TwitterAccount]) -> dict:
        """Crée plusieurs comptes en une seule requête.
        
        Args:
            accounts: Liste de comptes à créer
            
        Returns:
            Réponse de l'API
        """
        created_count = 0
        skipped_count = 0
        
        for account in accounts:
            result = self.create_account(account)
            if result:
                created_count += 1
            else:
                skipped_count += 1
        
        return {
            "message": f"{created_count} comptes créés, {skipped_count} ignorés",
            "created": created_count,
            "skipped": skipped_count,
            "total": len(accounts)
        }

    def get_tweets(
        self,
        limit: Optional[int] = None,
        username: Optional[str] = None,
        days: Optional[int] = None,
    ) -> List[dict]:
        """Récupère les tweets depuis l'API.
        
        Args:
            limit: Nombre maximum de tweets
            username: Filtrer par utilisateur
            days: Filtrer par les N derniers jours
            
        Returns:
            Liste de tweets
        """
        params = {}
        if limit:
            params["limit"] = limit
        if username:
            params["username"] = username
        if days:
            params["days"] = days
        
        try:
            response = self.session.get(
                f"{self.tweets_endpoint}",
                params=params,
                timeout=30,
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get("items", [])
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la récupération des tweets: {e}")
            return []

    def get_accounts(
        self,
        limit: Optional[int] = None,
        username: Optional[str] = None,
    ) -> List[dict]:
        """Récupère les comptes depuis l'API.
        
        Args:
            limit: Nombre maximum de comptes
            username: Filtrer par utilisateur
            
        Returns:
            Liste de comptes
        """
        params = {}
        if limit:
            params["limit"] = limit
        if username:
            params["username"] = username
        
        try:
            response = self.session.get(
                f"{self.accounts_endpoint}",
                params=params,
                timeout=30,
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get("items", [])
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la récupération des comptes: {e}")
            return []
