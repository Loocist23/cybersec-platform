"""Client pour récupérer les tweets depuis X (Twitter) via l'API officielle."""

import time
from datetime import datetime, timedelta
from typing import List, Optional

import tweepy

from twitter_service.config import config
from twitter_service.models.tweet import Tweet, TwitterAccount
from twitter_service.utils.logger import setup_logger

logger = setup_logger(__name__)


class TwitterClient:
    """Service client pour récupérer les tweets via l'API Twitter officielle v2.
    
    Utilise tweepy avec un Bearer Token pour accéder à l'API Twitter.
    Nécessite un compte développeur Twitter et un Bearer Token.
    
    Documentation: https://developer.twitter.com/en/docs/twitter-api
    """

    def __init__(self) -> None:
        """Initialise le client Twitter avec le Bearer Token."""
        self.max_tweets = config.MAX_TWEETS_PER_REQUEST
        self.request_delay = config.REQUEST_DELAY
        self.min_likes = config.MIN_LIKES
        self.min_retweets = config.MIN_RETWEETS
        self.language = config.LANGUAGE
        self.include_replies = config.INCLUDE_REPLIES
        self.include_retweets = config.INCLUDE_RETWEETS
        
        # Initialiser le client Tweepy
        if not config.TWITTER_BEARER_TOKEN:
            raise ValueError(
                "TWITTER_BEARER_TOKEN est requis pour utiliser l'API Twitter. "
                "Ajoutez-le dans votre fichier .env"
            )
        
        self.client = tweepy.Client(bearer_token=config.TWITTER_BEARER_TOKEN)

    def _tweet_to_model(self, tweet_data: dict) -> Optional[Tweet]:
        """Convertit un tweet de l'API Twitter en modèle Tweet.
        
        Args:
            tweet_data: Dictionnaire de données d'un tweet de l'API Twitter v2
            
        Returns:
            Tweet model ou None si le tweet ne passe pas les filtres
        """
        try:
            # Filtrer par likes/retweets si configuré
            likes = tweet_data.get("public_metrics", {}).get("like_count", 0)
            retweets = tweet_data.get("public_metrics", {}).get("retweet_count", 0)
            
            if likes < self.min_likes or retweets < self.min_retweets:
                return None

            # Extraire les hashtags
            hashtags = []
            if "entities" in tweet_data and "hashtags" in tweet_data["entities"]:
                hashtags = [tag["tag"] for tag in tweet_data["entities"]["hashtags"]]

            # Extraire les mentions
            mentions = []
            if "entities" in tweet_data and "mentions" in tweet_data["entities"]:
                mentions = [f"@{mention['username']}" for mention in tweet_data["entities"]["mentions"]]

            # Extraire les URLs
            urls = []
            if "entities" in tweet_data and "urls" in tweet_data["entities"]:
                urls = [url["expanded_url"] for url in tweet_data["entities"]["urls"]]

            # Extraire les images
            images = []
            if "attachments" in tweet_data and "media_keys" in tweet_data["attachments"]:
                media_keys = tweet_data["attachments"]["media_keys"]
                # Note: Pour obtenir les URLs des images, il faudrait faire une requête supplémentaire
                # Pour simplifier, on laisse vide pour l'instant

            # Extraire les vidéos (similaire aux images)
            videos = []

            # Construire l'URL du tweet
            tweet_id = tweet_data.get("id", "")
            username = tweet_data.get("author_id", "")
            tweet_url = f"https://twitter.com/{username}/status/{tweet_id}"

            return Tweet(
                tweet_id=str(tweet_id),
                username=tweet_data.get("author_id", ""),
                user_id=None,  # On n'a pas l'ID user directement, il faudrait une requête supplémentaire
                content=tweet_data.get("text", ""),
                date=datetime.strptime(tweet_data.get("created_at", ""), "%Y-%m-%dT%H:%M:%S.%fZ") if tweet_data.get("created_at") else datetime.utcnow(),
                url=tweet_url,
                likes=likes,
                retweets=retweets,
                replies=tweet_data.get("public_metrics", {}).get("reply_count", 0),
                quotes=tweet_data.get("public_metrics", {}).get("quote_count", 0),
                views=None,  # Pas disponible dans l'API standard
                is_retweet=tweet_data.get("retweeted", False) or tweet_data.get("referenced_tweets") is not None,
                is_quote=tweet_data.get("quoted", False),
                is_reply=tweet_data.get("in_reply_to_user_id") is not None,
                language=tweet_data.get("lang", None),
                hashtags=hashtags,
                mentions=mentions,
                urls=urls,
                images=images,
                videos=videos,
            )
        except Exception as e:
            logger.warning(f"Erreur de parsing pour le tweet {tweet_data.get('id', 'unknown')}: {e}")
            return None

    def get_tweets_by_query(
        self,
        query: str,
        limit: Optional[int] = None,
        days_back: Optional[int] = None,
    ) -> List[Tweet]:
        """Récupère les tweets correspondant à une requête via l'API Twitter v2.
        
        Args:
            query: Requête de recherche (ex: "cybersecurity")
            limit: Nombre maximum de tweets à retourner
            days_back: Nombre de jours à remonter
            
        Returns:
            Liste de tweets
        """
        if limit is None:
            limit = self.max_tweets
        
        if days_back is None:
            days_back = config.SEARCH_DAYS_BACK

        # Calculer la date de début (format ISO 8601)
        since_date = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%dT%H:%M:%SZ")
        until_date = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        tweets = []
        try:
            logger.info(f"Recherche des tweets pour : {query}")
            
            # Utiliser l'API Twitter v2 Search
            search_query = f"{query} -is:retweet"  # Exclure les retweets par défaut
            
            # Options de filtrage
            if not self.include_replies:
                search_query += " -is:reply"
            if not self.include_retweets:
                search_query += " -is:retweet"
            
            # Language filter
            if self.language:
                search_query += f" lang:{self.language}"
            
            # Exécuter la recherche
            response = self.client.search_recent_tweets(
                query=search_query,
                max_results=min(limit, 100),  # API limitée à 100 résultats max par requête
                start_time=since_date,
                end_time=until_date,
                tweet_fields=["created_at", "public_metrics", "lang", "entities", "referenced_tweets"],
                user_fields=["username"],
            )
            
            # Vérifier les erreurs
            if response.data is None:
                logger.error(f"Aucun résultat ou erreur: {response.includes if hasattr(response, 'includes') else 'Unknown'}")
                return tweets
            
            # Convertir chaque tweet
            for tweet_data in response.data:
                tweet_model = self._tweet_to_model(tweet_data)
                if tweet_model:
                    tweets.append(tweet_model)
                    
                # Respecter le délai si on fait plusieurs pages (pas implémenté pour l'instant)
                if len(tweets) >= limit:
                    break
            
            # Note: L'API v2 a une limite de 100 tweets par requête
            # Pour plus de résultats, il faudrait utiliser la pagination
            logger.info(f"Trouvé {len(tweets)} tweets pour la requête '{query}'")
            
        except tweepy.TweepError as e:
            logger.error(f"Erreur API Twitter pour '{query}': {e}")
        except Exception as e:
            logger.error(f"Erreur lors de la recherche des tweets pour '{query}': {e}")
        
        return tweets

    def get_tweets_by_username(
        self,
        username: str,
        limit: Optional[int] = None,
        days_back: Optional[int] = None,
    ) -> List[Tweet]:
        """Récupère les tweets d'un utilisateur spécifique via l'API Twitter v2.
        
        Args:
            username: Nom d'utilisateur Twitter (sans @)
            limit: Nombre maximum de tweets à retourner
            days_back: Nombre de jours à remonter
            
        Returns:
            Liste de tweets
        """
        if limit is None:
            limit = self.max_tweets
        
        if days_back is None:
            days_back = config.SEARCH_DAYS_BACK

        # Calculer la date de début
        since_date = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%dT%H:%M:%SZ")

        tweets = []
        try:
            logger.info(f"Recherche des tweets de @{username} depuis {since_date}")
            
            # Obtenir l'ID de l'utilisateur
            user = self.client.get_user(username=username, user_fields=["id"])
            if user.data is None:
                logger.warning(f"Utilisateur @{username} non trouvé")
                return tweets
            
            user_id = user.data.id
            
            # Récupérer les tweets de l'utilisateur
            response = self.client.get_users_tweets(
                id=user_id,
                max_results=min(limit, 100),
                start_time=since_date,
                tweet_fields=["created_at", "public_metrics", "lang", "entities", "referenced_tweets"],
                exclude="retweets,replies",
            )
            
            if response.data is None:
                return tweets
            
            # Convertir chaque tweet
            for tweet_data in response.data:
                # Ajouter l'username à tweet_data pour le modèle
                tweet_data["author_id"] = user.data.username
                tweet_model = self._tweet_to_model(tweet_data)
                if tweet_model:
                    tweets.append(tweet_model)
            
            logger.info(f"Trouvé {len(tweets)} tweets pour @{username}")
            
        except tweepy.TweepError as e:
            logger.error(f"Erreur API Twitter pour @{username}: {e}")
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des tweets de @{username}: {e}")
        
        return tweets

    def get_user_info(self, username: str) -> Optional[TwitterAccount]:
        """Récupère les informations d'un compte Twitter via l'API v2.
        
        Args:
            username: Nom d'utilisateur Twitter (sans @)
            
        Returns:
            TwitterAccount ou None si erreur
        """
        try:
            # Obtenir les infos de l'utilisateur
            response = self.client.get_user(
                username=username,
                user_fields=["username", "name", "description", "public_metrics", "created_at", "verified", "profile_image_url"],
            )
            
            if response.data is None:
                logger.warning(f"Utilisateur @{username} non trouvé")
                return None
            
            user_data = response.data
            user_metrics = user_data.public_metrics if hasattr(user_data, 'public_metrics') else {}
            
            return TwitterAccount(
                username=user_data.username,
                user_id=str(user_data.id),
                display_name=user_data.name or "",
                bio=user_data.description or "",
                followers_count=user_metrics.get("followers_count", 0),
                following_count=user_metrics.get("following_count", 0),
                tweet_count=user_metrics.get("tweet_count", 0),
                account_created_at=user_data.created_at if hasattr(user_data, 'created_at') else None,
                verified=user_data.verified if hasattr(user_data, 'verified') else False,
                avatar_url=user_data.profile_image_url if hasattr(user_data, 'profile_image_url') else None,
                url=f"https://twitter.com/{user_data.username}",
            )
            
        except tweepy.TweepError as e:
            logger.error(f"Erreur API Twitter pour @{username}: {e}")
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des infos de @{username}: {e}")
            return None

    def get_trending_tweets(
        self,
        query: str,
        limit: Optional[int] = None,
    ) -> List[Tweet]:
        """Récupère les tweets populaires pour une requête.
        
        Args:
            query: Requête de recherche
            limit: Nombre maximum de tweets
            
        Returns:
            Liste de tweets triés par popularité
        """
        tweets = self.get_tweets_by_query(query, limit)
        
        # Trier par nombre total d'interactions
        tweets.sort(
            key=lambda t: (t.likes + t.retweets * 2 + t.replies + t.quotes),
            reverse=True
        )
        
        return tweets

    def search_multiple_queries(
        self,
        queries: List[str],
        limit_per_query: Optional[int] = None,
    ) -> List[Tweet]:
        """Recherche sur plusieurs requêtes.
        
        Args:
            queries: Liste de requêtes à rechercher
            limit_per_query: Limite par requête
            
        Returns:
            Liste de tous les tweets trouvés
        """
        all_tweets = []
        
        for query in queries:
            tweets = self.get_tweets_by_query(
                query.strip(),
                limit=limit_per_query,
            )
            all_tweets.extend(tweets)
            
            # Pause entre les requêtes pour respecter le rate limit
            time.sleep(self.request_delay)
        
        return all_tweets
