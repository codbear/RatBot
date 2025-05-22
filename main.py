# main.py
import discord
import os
from dotenv import load_dotenv
from core.bot import bot, tree
from utils.db import init_db

# ----- CONFIGURATION -----
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILDE_ID = int(os.getenv('GUILDE_ID'))

init_db()

# ----- IMPORT COMMANDES -----
import slash_commands.voyages  # noqa: F401
import slash_commands.ranking  # noqa: F401

@bot.event
async def setup_hook():
    tree.copy_global_to(guild=discord.Object(id=GUILDE_ID))

# ----- ÉVÉNEMENTS -----
@bot.event
async def on_ready():
    print(f"🤵 Intendant des Rongeurs connecté en tant que {bot.user}")
    print(f"Tentative de synchronisation avec la guilde : {GUILDE_ID}")
    try:
        guild = discord.Object(id=GUILDE_ID)
        synced = await tree.sync(guild=guild)
        print(f"{len(synced)} commandes slash synchronisées dans la guilde.")
    except Exception as e:
        print(f"Erreur lors de la synchronisation : {e}")

# ----- LANCEMENT -----
bot.run(TOKEN)