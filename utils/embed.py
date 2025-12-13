import discord
from datetime import datetime
from utils.format_number import format_number

async def post_voyage_embed(
        voyage: dict[str, any],
        interaction: discord.Interaction
):
    embed = discord.Embed(
        title=f"📜 Rapport du voyage n° {voyage.get('id')}",
        color=discord.Color.gold(),
        timestamp=datetime.now()
    )

    embed.add_field(
        name="🏴‍☠️ Saison", 
        value=voyage.get('season', 'Saison inconnue'), 
        inline=True
    )

    embed.add_field(
        name="⏱️ Jours en mer", 
        value=f"{voyage.get('duration'):,}".replace(',', ' ') + " jours",
        inline=True
    )

    # Champ vide pour alignement
    embed.add_field(name="\u200b", value="\u200b", inline=True)
    
    embed.add_field(
        name="👥 Équipage", 
        value=', '.join(f"<@{uid}>" for uid in voyage.get('members')) or "aucun",
        inline=False
    )

    embed.add_field(
        name="🪙 Butin", 
        value=f"{format_number(voyage.get('gold'))} pièces d'or", 
        inline=True
    )

    embed.add_field(
        name="🏆 Valeur d'émissaire", 
        value=format_number(voyage.get('emissary_value')), 
        inline=True
    )

    # Calculer les stats moyennes
    duration = voyage.get('duration', 1)
    avg_gold_per_day = voyage.get('gold', 0) / duration
    avg_emissary_per_day = voyage.get('emissary_value', 0) / duration

    embed.add_field(
        name="📊 Moyenne/jour", 
        value=f"🪙 {format_number(int(avg_gold_per_day))} or\n🏆 {format_number(int(avg_emissary_per_day))} émissaire",
        inline=True
    )

    # Footer avec informations supplémentaires
    embed.set_footer(
        text=f"Déclaré par {interaction.user.display_name} • {len(voyage.get('members', []))} membre(s)",
        icon_url=interaction.user.display_avatar.url if interaction.user.display_avatar else None
    )

    await interaction.channel.send(embed=embed)
