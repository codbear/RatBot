import discord

async def post_voyage_embed(
        voyage: dict[str, any],
        interaction:discord.Interaction
):
    embed = discord.Embed(
        title=f"📜 Rapport du voyage n° {voyage.get('id')}",
        color=discord.Color.gold()
    )

    embed.add_field(
        name="Saison", 
        value=voyage.get('season', 'Saison inconnue'), 
        inline=True
    )

    embed.add_field(
        name="Jours en mer", 
        value=f"{voyage.get('duration'):,}".replace(',', ' ') + " jours",
        inline=True
    )
    
    embed.add_field(
        name="Équipage", 
        value=', '.join(f"<@{uid}>" for uid in voyage.get('members')) or "aucun",
        inline=False
    )

    embed.add_field(
        name="Butin", 
        value=f"{voyage.get('gold'):,}".replace(',', ' ') + " pièces d'or", 
        inline=True
    )

    embed.add_field(
        name="Valeur d'émissaire", 
        value=f"{voyage.get('emissary_value'):,}".replace(',', ' '), 
        inline=True
    )

    await interaction.channel.send(embed=embed)
