# utils/validators.py
"""
Validation des données d'entrée pour les commandes du bot.
"""

class ValidationError(Exception):
    """Exception levée pour les erreurs de validation."""
    pass

def validate_voyage_data(gold: int, emissaire: int, duree: int) -> None:
    """
    Valide les données d'un voyage.
    
    Args:
        gold: Montant d'or (doit être positif et raisonnable)
        emissaire: Valeur d'émissaire (doit être positive et raisonnable)
        duree: Durée en jours (doit être positive et raisonnable)
        
    Raises:
        ValidationError: Si les données ne sont pas valides
    """
    
    # Validation de l'or
    if gold < 0:
        raise ValidationError("❌ Le montant d'or ne peut pas être négatif.")
    if gold > 10_000_000:  # 10 millions max
        raise ValidationError("❌ Le montant d'or semble trop élevé (max: 10 000 000).")
    
    # Validation de l'émissaire
    if emissaire < 0:
        raise ValidationError("❌ La valeur d'émissaire ne peut pas être négative.")
    if emissaire > 1_000_000:  # 1 million max
        raise ValidationError("❌ La valeur d'émissaire semble trop élevée (max: 1 000 000).")
    
    # Validation de la durée
    if duree <= 0:
        raise ValidationError("❌ La durée du voyage doit être d'au moins 1 jour.")
    if duree > 365:  # 1 an max
        raise ValidationError("❌ La durée du voyage semble trop longue (max: 365 jours).")

def validate_season_name(name: str) -> str:
    """
    Valide et nettoie le nom d'une saison.
    
    Args:
        name: Nom de la saison à valider
        
    Returns:
        str: Nom de saison nettoyé
        
    Raises:
        ValidationError: Si le nom n'est pas valide
    """
    
    if not name or not name.strip():
        raise ValidationError("❌ Le nom de la saison ne peut pas être vide.")
    
    # Nettoyer le nom
    clean_name = name.strip()
    
    if len(clean_name) < 3:
        raise ValidationError("❌ Le nom de la saison doit contenir au moins 3 caractères.")
    
    if len(clean_name) > 50:
        raise ValidationError("❌ Le nom de la saison ne peut pas dépasser 50 caractères.")
    
    # Caractères interdits
    forbidden_chars = ['<', '>', '@', '#', '`', '|']
    if any(char in clean_name for char in forbidden_chars):
        raise ValidationError("❌ Le nom de la saison contient des caractères interdits.")
    
    return clean_name