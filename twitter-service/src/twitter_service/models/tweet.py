"""Modèles de données pour les tweets et comptes Twitter."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class TwitterAccount(BaseModel):
    """Modèle pour un compte Twitter/X."""
    
    username: str = Field(..., description="Nom d'utilisateur Twitter (ex: @user)")
    user_id: Optional[str] = Field(None, description="ID numérique de l'utilisateur")
    display_name: Optional[str] = Field(None, description="Nom affiché du compte")
    bio: Optional[str] = Field(None, description="Biographie du compte")
    followers_count: Optional[int] = Field(None, description="Nombre d'abonnés")
    following_count: Optional[int] = Field(None, description="Nombre d'abonnements")
    tweet_count: Optional[int] = Field(None, description="Nombre de tweets")
    account_created_at: Optional[datetime] = Field(None, description="Date de création du compte")
    verified: bool = Field(default=False, description="Compte vérifié")
    avatar_url: Optional[HttpUrl] = Field(None, description="URL de l'avatar")
    url: Optional[HttpUrl] = Field(None, description="URL du profil")
    category: Optional[str] = Field(None, description="Catégorie du compte")
    
    class Config:
        from_attributes = True


class Tweet(BaseModel):
    """Modèle pour un tweet complet."""
    
    tweet_id: str = Field(..., description="ID unique du tweet")
    username: str = Field(..., description="Nom d'utilisateur")
    user_id: Optional[str] = Field(None, description="ID de l'utilisateur")
    content: str = Field(..., description="Contenu du tweet")
    date: datetime = Field(..., description="Date de publication")
    url: HttpUrl = Field(..., description="URL du tweet")
    
    # Métriques
    likes: int = Field(default=0, description="Nombre de likes")
    retweets: int = Field(default=0, description="Nombre de retweets")
    replies: int = Field(default=0, description="Nombre de réponses")
    quotes: int = Field(default=0, description="Nombre de citations")
    views: Optional[int] = Field(None, description="Nombre de vues")
    
    # Informations supplémentaires
    is_retweet: bool = Field(default=False, description="Est-ce un retweet")
    is_quote: bool = Field(default=False, description="Est-ce une citation")
    is_reply: bool = Field(default=False, description="Est-ce une réponse")
    language: Optional[str] = Field(None, description="Langue du tweet")
    
    # Références
    hashtags: List[str] = Field(default_factory=list, description="Liste des hashtags")
    mentions: List[str] = Field(default_factory=list, description="Liste des mentions (@user)")
    urls: List[HttpUrl] = Field(default_factory=list, description="Liste des URLs dans le tweet")
    
    # Médias
    images: List[HttpUrl] = Field(default_factory=list, description="URLs des images")
    videos: List[HttpUrl] = Field(default_factory=list, description="URLs des vidéos")
    
    # Catégorisation (pour analyse)
    category: Optional[str] = Field(None, description="Catégorie attribuée")
    severity: Optional[str] = Field(None, description="Niveau de sévérité (si pertinent)")
    
    class Config:
        from_attributes = True


class TweetCreate(BaseModel):
    """Modèle pour créer un tweet (version simplifiée pour l'API)."""
    
    tweet_id: str = Field(..., description="ID unique du tweet")
    username: str = Field(..., description="Nom d'utilisateur")
    user_id: Optional[str] = Field(None, description="ID de l'utilisateur")
    content: str = Field(..., description="Contenu du tweet")
    date: datetime = Field(..., description="Date de publication")
    url: str = Field(..., description="URL du tweet")
    
    likes: int = Field(default=0, description="Nombre de likes")
    retweets: int = Field(default=0, description="Nombre de retweets")
    replies: int = Field(default=0, description="Nombre de réponses")
    quotes: int = Field(default=0, description="Nombre de citations")
    views: Optional[int] = Field(None, description="Nombre de vues")
    
    is_retweet: bool = Field(default=False, description="Est-ce un retweet")
    is_quote: bool = Field(default=False, description="Est-ce une citation")
    is_reply: bool = Field(default=False, description="Est-ce une réponse")
    language: Optional[str] = Field(None, description="Langue du tweet")
    
    hashtags: List[str] = Field(default_factory=list, description="Liste des hashtags")
    mentions: List[str] = Field(default_factory=list, description="Liste des mentions")
    urls: List[str] = Field(default_factory=list, description="Liste des URLs")
    
    images: List[str] = Field(default_factory=list, description="URLs des images")
    videos: List[str] = Field(default_factory=list, description="URLs des vidéos")
    
    category: Optional[str] = Field(None, description="Catégorie attribuée")
    severity: Optional[str] = Field(None, description="Niveau de sévérité")


class TweetDbRecord(BaseModel):
    """Enregistrement tweet tel que stocké en base de données ou envoyé à l'API."""
    
    tweet_id: str = Field(..., description="ID unique du tweet")
    username: str = Field(..., description="Nom d'utilisateur")
    user_id: Optional[str] = Field(None, description="ID de l'utilisateur")
    content: str = Field(..., description="Contenu du tweet")
    date: datetime = Field(..., description="Date de publication")
    url: str = Field(..., description="URL du tweet")
    
    likes: int = Field(default=0, description="Nombre de likes")
    retweets: int = Field(default=0, description="Nombre de retweets")
    replies: int = Field(default=0, description="Nombre de réponses")
    quotes: int = Field(default=0, description="Nombre de citations")
    views: Optional[int] = Field(None, description="Nombre de vues")
    
    is_retweet: bool = Field(default=False, description="Est-ce un retweet")
    is_quote: bool = Field(default=False, description="Est-ce une citation")
    is_reply: bool = Field(default=False, description="Est-ce une réponse")
    language: Optional[str] = Field(None, description="Langue du tweet")
    
    hashtags: List[str] = Field(default_factory=list, description="Liste des hashtags")
    mentions: List[str] = Field(default_factory=list, description="Liste des mentions")
    urls: List[str] = Field(default_factory=list, description="Liste des URLs")
    
    images: List[str] = Field(default_factory=list, description="URLs des images")
    videos: List[str] = Field(default_factory=list, description="URLs des vidéos")
    
    category: Optional[str] = Field(None, description="Catégorie attribuée")
    severity: Optional[str] = Field(None, description="Niveau de sévérité")
    
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Date d'ajout en DB")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Date de dernière mise à jour")
    
    class Config:
        from_attributes = True
