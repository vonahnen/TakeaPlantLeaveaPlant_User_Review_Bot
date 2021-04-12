import os

import discord
from discord.ext import commands

TOKEN = open("discord.txt", "r").readline().strip()

bot = commands.Bot(command_prefix='')

@bot.command(name='input')
@commands.has_role('Reviews')
async def inputReview(ctx, username: str, rating: int, url: str):
	await ctx.send("Success! Username = " + username + ", rating = " + str(rating) + ", url = " + url)

@inputReview.error
async def inputReviewError(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send("Sorry, you don't have permissions!")
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send("You are missing an argument:\n`input` `USERNAME` `RATING` `URL`.")
    if isinstance(error, commands.errors.BadArgument):
        await ctx.send("Ensure correct format:\n`input` `USERNAME` `RATING` `URL`.")

bot.run(TOKEN)
