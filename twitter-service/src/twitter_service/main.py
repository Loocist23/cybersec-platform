#!/usr/bin/env python3
"""Point d'entrée principal du Twitter Service.

Ce script peut être exécuté de différentes manières :
- `python -m twitter_service.main` : Récupère les tweets des requêtes par défaut
- `python -m twitter_service.main --queries cybersecurity,malware` : Récupère par requêtes spécifiques
- `python -m twitter_service.main --usernames user1,user2` : Récupère par utilisateurs
- `python -m twitter_service.main --trending` : Récupère les tweets populaires
- `python -m twitter_service.main --daemon` : Mode démon pour exécution périodique
- `python -m twitter_service.main --days 7` : Récupère les tweets des 7 derniers jours
"""

import argparse
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

# Ajouter le parent de src au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from twitter_service.config import config
from twitter_service.services.collector import TwitterCollectorService
from twitter_service.utils.logger import setup_logger

logger = setup_logger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse les arguments en ligne de commande."""
    parser = argparse.ArgumentParser(
        description="Twitter Service - Récupère et stocke les tweets depuis X (Twitter)"
    )

    parser.add_argument(
        "--queries",
        type=str,
        nargs="+",
        default=None,
        help="Requêtes de recherche (ex: cybersecurity malware infosec)"
    )

    parser.add_argument(
        "--usernames",
        type=str,
        nargs="+",
        default=None,
        help="Noms d'utilisateurs à surveiller (ex: @user1 @user2)"
    )

    parser.add_argument(
        "--trending",
        action="store_true",
        help="Récupérer uniquement les tweets populaires (trending)"
    )

    parser.add_argument(
        "--days",
        type=int,
        default=None,
        help="Nombre de jours à remonter (par défaut: SEARCH_DAYS_BACK)"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Nombre maximum de tweets par requête/utilisateur"
    )

    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Mode démon : exécution périodique"
    )

    parser.add_argument(
        "--daemon-interval",
        type=int,
        default=24,
        help="Intervalle en heures pour le mode démon (par défaut: 24)"
    )

    parser.add_argument(
        "--list-accounts",
        action="store_true",
        help="Lister les comptes Twitter stockés"
    )

    parser.add_argument(
        "--list-tweets",
        action="store_true",
        help="Lister les tweets stockés"
    )

    parser.add_argument(
        "--stats",
        action="store_true",
        help="Afficher les statistiques"
    )

    parser.add_argument(
        "--test",
        action="store_true",
        help="Test de connexion à l'API et à snscrape"
    )

    return parser.parse_args()


def print_tweet_list(tweets: list, limit: int = 20) -> None:
    """Affiche une liste de tweets de manière formatée."""
    for i, tweet in enumerate(tweets[:limit], 1):
        print(f"\n{i}. 🐦 @{tweet.username} ({tweet.date.strftime('%Y-%m-%d %H:%M')})")
        print(f"   💬 {tweet.content[:200]}{'...' if len(tweet.content) > 200 else ''}")
        print(f"   ❤️ {tweet.likes}   🔄 {tweet.retweets}   💬 {tweet.replies}")
        if tweet.hashtags:
            print(f"   🏷️  {', '.join(tweet.hashtags[:5])}")
        if tweet.urls:
            print(f"   🔗 {tweet.urls[0]}")
        print(f"   🔗 {tweet.url}")

    if len(tweets) > limit:
        print(f"\n... et {len(tweets) - limit} autres tweets")


def print_account_list(accounts: list, limit: int = 20) -> None:
    """Affiche une liste de comptes Twitter de manière formatée."""
    for i, account in enumerate(accounts[:limit], 1):
        verified_str = "✅" if account.verified else "❌"
        print(f"\n{i}. @{account.username} {verified_str}")
        print(f"   👤 {account.display_name or 'N/A'}")
        print(f"   📝 {account.bio[:100]}{'...' if account.bio and len(account.bio) > 100 else ''}")
        print(f"   👥 {account.followers_count or 0} followers | 📢 {account.tweet_count or 0} tweets")
        if account.url:
            print(f"   🌐 {account.url}")

    if len(accounts) > limit:
        print(f"\n... et {len(accounts) - limit} autres comptes")


def test_connections() -> bool:
    """Teste les connexions à l'API et à snscrape."""
    from twitter_service.services.api_client import TwitterAPIClient
    from twitter_service.services.twitter_client import TwitterClient
    
    print("\n" + "="*50)
    print("🧪 TEST DES CONNEXIONS")
    print("="*50)
    
    # Test API Service
    print("\n1️⃣  Test de l'API Service...")
    api_client = TwitterAPIClient()
    if api_client.health_check():
        print("✅ API Service est disponible !")
    else:
        print("❌ API Service n'est PAS disponible")
        print(f"   URL: {config.API_URL}")
        return False
    
    # Test snscrape
    print("\n2️⃣  Test de snscrape...")
    try:
        twitter_client = TwitterClient()
        tweets = twitter_client.get_tweets_by_query("cybersecurity", limit=1)
        if tweets:
            print(f"✅ snscrape fonctionne ! (1 tweet récupéré)")
        else:
            print("⚠️  snscrape fonctionne mais aucun tweet trouvé")
    except Exception as e:
        print(f"❌ snscrape échoué: {e}")
        return False
    
    print("\n" + "="*50)
    print("✅ TOUS LES TESTS ONT RÉUSSI !")
    print("="*50)
    return True


def daemon_mode(collector: TwitterCollectorService, queries: list, interval_hours: int) -> None:
    """Mode démon : exécution périodique."""
    logger.info(f"🤖 Mode démon activé (intervalle: {interval_hours}h)")
    
    while True:
        try:
            logger.info(f"🔄 Début de la collecte à {datetime.now()}")
            
            result = collector.collect_by_queries(queries)
            
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
            time.sleep(60)


def main() -> None:
    """Fonction principale."""
    args = parse_args()

    # Initialiser le service de collecte
    collector = TwitterCollectorService()
    api_client = collector.api_client

    # Mode test
    if args.test:
        success = test_connections()
        sys.exit(0 if success else 1)

    # Vérifier que l'API est disponible
    if not api_client.health_check():
        logger.error("❌ API Service non disponible. Vérifie que l'API tourne sur " + config.API_URL)
        print(f"\n❌ Erreur: API non disponible à {config.API_URL}")
        print("Lance d'abord: docker-compose -f docker-compose-simple.yml up -d api")
        sys.exit(1)

    # Mode daemon
    if args.daemon:
        queries = args.queries or config.SEARCH_QUERIES
        daemon_mode(collector, queries, args.daemon_interval)
        return

    # Mode trending
    if args.trending:
        queries = args.queries or config.SEARCH_QUERIES
        limit = args.limit or config.MAX_TWEETS_PER_REQUEST
        
        logger.info("📈 Récupération des tweets populaires...")
        tweets = collector.collect_trending(queries, limit)
        
        if tweets:
            print(f"\n🔥 {len(tweets)} tweets populaires trouvés :\n")
            print_tweet_list(tweets, 10)
            
            # Envoyer à l'API
            result = collector.api_client.create_tweets_batch(tweets)
            print(f"\n✅ {result['created']} tweets envoyés à l'API")
        else:
            print("✅ Aucun tweet populaire trouvé")
        return

    # Mode par requêtes
    if args.queries:
        days = args.days or config.SEARCH_DAYS_BACK
        limit = args.limit or config.MAX_TWEETS_PER_REQUEST
        
        logger.info(f"🔍 Récupération des tweets pour {len(args.queries)} requêtes...")
        result = collector.collect_by_queries(
            queries=args.queries,
            limit_per_query=limit // len(args.queries),
            days_back=days,
        )
        
        if result.get("error"):
            print(f"\n❌ Erreur: {result['error']}")
        else:
            print(f"\n✅ Collecte terminée !")
            print(f"   - {result.get('total_tweets', 0)} tweets")
            print(f"   - {result.get('total_accounts', 0)} comptes")
        return

    # Mode par utilisateurs
    if args.usernames:
        days = args.days or config.SEARCH_DAYS_BACK
        limit = args.limit or config.MAX_TWEETS_PER_REQUEST
        
        # Nettoyer les usernames (enlever @ si présent)
        clean_usernames = [u.strip().lstrip("@") for u in args.usernames]
        
        logger.info(f"👥 Récupération des tweets de {len(clean_usernames)} utilisateurs...")
        result = collector.collect_by_usernames(
            usernames=clean_usernames,
            limit_per_user=limit,
            days_back=days,
        )
        
        if result.get("error"):
            print(f"\n❌ Erreur: {result['error']}")
        else:
            print(f"\n✅ Collecte terminée !")
            print(f"   - {result.get('total_tweets', 0)} tweets")
            print(f"   - {result.get('total_accounts', 0)} comptes")
        return

    # Mode par défaut : utiliser les requêtes configurées
    logger.info("🚀 Récupération des tweets avec les requêtes par défaut...")
    days = args.days or config.SEARCH_DAYS_BACK
    limit = args.limit or config.MAX_TWEETS_PER_REQUEST
    
    result = collector.collect_by_queries(
        queries=None,  # Utilise SEARCH_QUERIES
        limit_per_query=limit // len(config.SEARCH_QUERIES),
        days_back=days,
    )
    
    if result.get("error"):
        print(f"\n❌ Erreur: {result['error']}")
    else:
        print(f"\n✅ Collecte terminée !")
        print(f"   - {result.get('total_tweets', 0)} tweets")
        print(f"   - {result.get('total_accounts', 0)} comptes")


if __name__ == "__main__":
    main()
