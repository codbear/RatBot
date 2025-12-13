# main.py
import discord
import os
from dotenv import load_dotenv
from core.bot import bot, tree
from utils.db import init_db
from utils.logger import logger

# ----- CONFIGURATION -----
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILDE_ID = int(os.getenv('GUILDE_ID'))

init_db()
logger.info("Bot starting up...")

# ----- IMPORT COMMANDES -----
import slash_commands.voyages  # noqa: F401
import slash_commands.ranking  # noqa: F401
import slash_commands.season  # noqa: F401
import slash_commands.stats  # noqa: F401

@bot.event
async def setup_hook():
    tree.copy_global_to(guild=discord.Object(id=GUILDE_ID))

# ----- ÉVÉNEMENTS -----
@bot.event
async def on_ready():
    logger.info(f"🤵 Intendant des Rongeurs connecté en tant que {bot.user}")
    logger.info(f"Tentative de synchronisation avec la guilde : {GUILDE_ID}")
    try:
        guild = discord.Object(id=GUILDE_ID)
        synced = await tree.sync(guild=guild)
        logger.info(f"{len(synced)} commandes slash synchronisées dans la guilde.")
        print(f"🎉 Bot prêt ! {len(synced)} commandes synchronisées.")
    except Exception as e:
        logger.error(f"Erreur lors de la synchronisation : {e}")
        print(f"❌ Erreur de synchronisation : {e}")

@bot.event
async def on_error(event, *args, **kwargs):
    logger.error(f"Erreur dans l'événement {event}", exc_info=True)

# ----- LANCEMENT -----
if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except Exception as e:
        logger.critical(f"Erreur critique lors du lancement du bot : {e}")
        print(f"💥 Erreur critique : {e}")