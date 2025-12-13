#!/usr/bin/env python3
"""
Script pour résoudre le problème de collation PostgreSQL sur Railway
"""

import os
import psycopg2
from dotenv import load_dotenv

def fix_collation():
    # Charger les variables d'environnement
    load_dotenv()
    
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        print("❌ DATABASE_URL non défini dans le fichier .env")
        return False
    
    try:
        print("🔗 Connexion à la base de données Railway...")
        conn = psycopg2.connect(DATABASE_URL)
        conn.set_session(autocommit=True)  # Nécessaire pour les commandes ALTER DATABASE
        
        with conn.cursor() as cur:
            print("🔍 Vérification de la version de collation actuelle...")
            
            # Obtenir le nom de la base de données
            cur.execute("SELECT current_database();")
            db_name = cur.fetchone()[0]
            print(f"📄 Base de données: {db_name}")
            
            # Vérifier les informations de collation
            cur.execute("""
                SELECT datname, datcollate, datctype 
                FROM pg_database 
                WHERE datname = current_database();
            """)
            
            result = cur.fetchone()
            print(f"📊 Collation actuelle: {result[1]}")
            print(f"📊 Type de caractères: {result[2]}")
            
            # Exécuter la commande de rafraîchissement
            print("🔄 Rafraîchissement de la version de collation...")
            cur.execute(f"ALTER DATABASE {db_name} REFRESH COLLATION VERSION;")
            
            print("✅ Problème de collation résolu avec succès!")
            print("🎉 Le warning ne devrait plus apparaître.")
            
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Erreur PostgreSQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

if __name__ == "__main__":
    print("🛠️  Script de résolution du problème de collation PostgreSQL")
    print("=" * 60)
    
    success = fix_collation()
    
    if success:
        print("\n🎯 Le problème a été résolu!")
        print("Tu peux maintenant relancer ton bot sans le warning.")
    else:
        print("\n⚠️  Le problème n'a pas pu être résolu automatiquement.")
        print("Tu peux utiliser les Solutions 1 ou 2 pour ignorer le warning.")