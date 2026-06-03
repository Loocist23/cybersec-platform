"""Service de collecte qui orchestre la récupération et l'envoi des tweets."""

import time
from datetime import datetime
from typing import List, Optional

from twitter_service.config import config
from twitter_service.models.tweet import Tweet, TwitterAccount, TweetDbRecord
from twitter_service.services.twitter_client import TwitterClient
from twitter_service.services.api_client import TwitterAPIClient
from twitter_service.utils.logger import setup_logger

logger = setup_logger(__name__)


class TwitterCollectorService:
    """Service principal de collecte des tweets."""

    def __init__(
        self,
        twitter_client: Optional[TwitterClient] = None,
        api_client: Optional[TwitterAPIClient] = None,
    ) -> None:
        """Initialise le service de collecte."""
        self.twitter_client = twitter_client or TwitterClient()
        self.api_client = api_client or TwitterAPIClient()

    def collect_by_queries(
        self,
        queries: Optional[List[str]] = None,
        limit_per_query: Optional[int] = None,
        days_back: Optional[int] = None,
    ) -> dict:
        """Collecte les tweets pour plusieurs requêtes.
        
        Args:
            queries: Liste de requêtes (si None, utilise SEARCH_QUERIES)
            limit_per_query: Limite par requête
            days_back: Nombre de jours à remonter
            
        Returns:
            Statistiques de la collecte
        """
        if queries is None:
            queries = config.SEARCH_QUERIES
        
        if days_back is None:
            days_back = config.SEARCH_DAYS_BACK

        all_tweets = []
        all_accounts = set()
        
        logger.info(f"Début de la collecte pour {len(queries)} requêtes")
        
        for query in queries:
            logger.info(f"Traitement de la requête: {query}")
            
            tweets = self.twitter_client.get_tweets_by_query(
                query.strip(),
                limit=limit_per_query,
                days_back=days_back,
            )
            
            all_tweets.extend(tweets)
            
            # Collecter les comptes uniques
            for tweet in tweets:
                if tweet.username not in all_accounts:
                    all_accounts.add(tweet.username)
            
            # Pause entre les requêtes
            time.sleep(config.REQUEST_DELAY)
        
        logger.info(f"Collecte terminée: {len(all_tweets)} tweets, {len(all_accounts)} comptes uniques")
        
        # Envoyer à l'API
        if self.api_client.health_check():
            # Envoyer les comptes
            accounts_to_create = []
            for username in all_accounts:
                account = self.twitter_client.get_user_info(username)
                if account:
                    accounts_to_create.append(account)
                time.sleep(0.5)  # Petit délai pour éviter le rate limit
            
            # Créer les comptes en batch
            if accounts_to_create:
                accounts_result = self.api_client.create_accounts_batch(accounts_to_create)
                logger.info(f"Comptes: {accounts_result}")
            
            # Envoyer les tweets en batch
            if all_tweets:
                tweets_result = self.api_client.create_tweets_batch(all_tweets)
                logger.info(f"Tweets: {tweets_result}")
            
            return {
                "tweets": tweets_result,
                "accounts": accounts_result,
                "total_tweets": len(all_tweets),
                "total_accounts": len(accounts_to_create),
            }
        else:
            logger.error("API non disponible, impossible d'envoyer les données")
            return {
                "error": "API non disponible",
                "total_tweets": len(all_tweets),
                "total_accounts": len(all_accounts),
            }

    def collect_by_usernames(
        self,
        usernames: List[str],
        limit_per_user: Optional[int] = None,
        days_back: Optional[int] = None,
    ) -> dict:
        """Collecte les tweets pour une liste d'utilisateurs.
        
        Args:
            usernames: Liste de noms d'utilisateurs
            limit_per_user: Limite par utilisateur
            days_back: Nombre de jours à remonter
            
        Returns:
            Statistiques de la collecte
        """
        all_tweets = []
        all_accounts = []
        
        logger.info(f"Début de la collecte pour {len(usernames)} utilisateurs")
        
        for username in usernames:
            logger.info(f"Traitement de @{username}")
            
            # Récupérer les infos du compte
            account = self.twitter_client.get_user_info(username)
            if account:
                all_accounts.append(account)
            
            # Récupérer les tweets
            tweets = self.twitter_client.get_tweets_by_username(
                username.strip().lstrip("@"),
                limit=limit_per_user,
                days_back=days_back,
            )
            
            all_tweets.extend(tweets)
            
            # Pause entre les utilisateurs
            time.sleep(config.REQUEST_DELAY)
        
        logger.info(f"Collecte terminée: {len(all_tweets)} tweets, {len(all_accounts)} comptes")
        
        # Envoyer à l'API
        if self.api_client.health_check():
            # Créer les comptes en batch
            if all_accounts:
                accounts_result = self.api_client.create_accounts_batch(all_accounts)
                logger.info(f"Comptes: {accounts_result}")
            
            # Envoyer les tweets en batch
            if all_tweets:
                tweets_result = self.api_client.create_tweets_batch(all_tweets)
                logger.info(f"Tweets: {tweets_result}")
            
            return {
                "tweets": tweets_result,
                "accounts": accounts_result,
                "total_tweets": len(all_tweets),
                "total_accounts": len(all_accounts),
            }
        else:
            logger.error("API non disponible, impossible d'envoyer les données")
            return {
                "error": "API non disponible",
                "total_tweets": len(all_tweets),
                "total_accounts": len(all_accounts),
            }

    def collect_trending(
        self,
        queries: Optional[List[str]] = None,
        limit: Optional[int] = None,
    ) -> List[Tweet]:
        """Récupère les tweets populaires (trending) pour les requêtes.
        
        Args:
            queries: Liste de requêtes
            limit: Nombre maximum de tweets
            
        Returns:
            Liste de tweets triés par popularité
        """
        if queries is None:
            queries = config.SEARCH_QUERIES
        
        if limit is None:
            limit = config.MAX_TWEETS_PER_REQUEST

        all_tweets = []
        
        for query in queries:
            tweets = self.twitter_client.get_trending_tweets(
                query.strip(),
                limit=limit // len(queries),  # Diviser la limite par le nombre de requêtes
            )
            all_tweets.extend(tweets)
            time.sleep(config.REQUEST_DELAY)
        
        # Re-trier tous les tweets par popularité
        all_tweets.sort(
            key=lambda t: (t.likes + t.retweets * 2 + t.replies + t.quotes),
            reverse=True
        )
        
        return all_tweets[:limit]

    def daemon_mode(
        self,
        queries: Optional[List[str]] = None,
        interval_hours: int = 24,
    ) -> None:
        """Mode démon : exécution périodique.
        
        Args:
            queries: Liste de requêtes
            interval_hours: Intervalle entre les exécutions
        """
        logger.info(f"🤖 Mode démon activé (intervalle: {interval_hours}h)")
        
        while True:
            try:
                logger.info(f"🔄 Début de la collecte à {datetime.now()}")
                
                result = self.collect_by_queries(queries)
                
                if result.get("total_tweets", 0) > 0:
                    logger.info(f"✅ {result['total_tweets']} tweets collectés")
                else:
                    logger.info("✅ Aucune nouvelle donnée trouvée")
                
                # Attendre l'intervalle suivant
                logger.info(f"⏳ Prochaine collecte dans {interval_hours}h...")
                time.sleep(interval_hours * 3600)
                
            except KeyboardInterrupt:
                logger.info("⏹️  Arrêt du mode démon")
                break
            except Exception as e:
                logger.error(f"❌ Erreur en mode démon: {e}")
                time.sleep(60)  # Attendre 1 minute avant de réessayer
