# utils/logger.py
import logging
import os
from datetime import datetime

def setup_logger():
    """Configure le système de logging pour le bot."""
    
    # Créer le dossier logs s'il n'existe pas
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Configuration du logger
    logger = logging.getLogger('ratbot')
    logger.setLevel(logging.INFO)
    
    # Éviter la duplication des handlers
    if logger.handlers:
        return logger
    
    # Format des logs
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    # Handler pour fichier
    file_handler = logging.FileHandler(
        f'logs/ratbot_{datetime.now().strftime("%Y%m%d")}.log',
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Handler pour console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Instance globale du logger
logger = setup_logger()