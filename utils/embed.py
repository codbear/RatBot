import discord

async def post_voyage_embed(
        voyage: dict[str, any],
        interaction:discord.Interaction
):
    embed = discord.Embed(
        title="📜 Rapport de voyage",
        color=discord.Color.gold()
    )

    embed.add_field(
        name="Numéro de voyage", 
        value=str(voyage.get('id')), 
        inline=False
    )

    embed.add_field(
        name="Capitaine", 
        value=interaction.user.display_name, 
        inline=False
    )
    
    embed.add_field(
        name="Équipage", 
        value=', '.join(f"<@{uid}>" for uid in voyage.get('members') if uid != interaction.user.id) or "aucun",
        inline=False
    )

    embed.add_field(
        name="Butin", 
        value=f"{voyage.get('gold'):,}".replace(',', ' ') + " pièces d'or", 
        inline=False
    )

    await interaction.channel.send(embed=embed)
