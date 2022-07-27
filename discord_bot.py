import os
import asyncio
import utils
from string import punctuation

import discord
from discord.ext import commands

import praw
from praw.models import Message

from time import sleep
from enum import Enum

from discord_reddit import DiscordReddit
from discord_reddit import UserWiki

class DiscordReviewBot:
  __instance = None

  # TODO Class variables need to be private.
  bot = commands.Bot(command_prefix=',')

  @staticmethod
  def get_instance(token, debug_channel_id, review_channel_id):
    if DiscordReviewBot.__instance == None:
      DiscordReviewBot.discord_reddit = DiscordReddit("reddit.txt")
      DiscordReviewBot.debug_channel_id = debug_channel_id
      DiscordReviewBot.review_channel_id = review_channel_id
      DiscordReviewBot(token)

    return DiscordReviewBot.__instance

  def __init__(self, token):
    self.token = token

    if DiscordReviewBot.__instance != None:
      raise Exception("Cannot instantiate multiple instances of the singleton class 'DiscordReviewBot'.")
    else:
      DiscordReviewBot.__instance = self

  def run(self):
    DiscordReviewBot.bot.run(self.token)

  async def log(message, ctx = None):
    if ctx is not None:
      await ctx.send(message) # Send the message back to the user before logging to the debug channel.
      command_context = f"\n\tbot={ctx.me}\n\tauthor={ctx.author}\n\tchannel={ctx.channel.name} (ID: {ctx.channel.id})\n\tcommand={ctx.command}\n\tcommand_args={ctx.args}"
      message = f"{message}{command_context}"

    print(f"[DEBUG] {message}") # TODO Python should have a logger library.
    debug_channel = DiscordReviewBot.bot.get_channel(DiscordReviewBot.debug_channel_id)
    await debug_channel.send(message)

  async def validate_command_channel(ctx):
    if ctx.channel.id not in [DiscordReviewBot.review_channel_id]: # TODO Need to define this list.
      message = f"Failed to run {ctx.author.name}'s command in unauthorized channel '#{ctx.channel.name}'!"
      await DiscordReviewBot.log(message, ctx)
      raise discord.ext.commands.CommandError(message)

  @bot.event
  async def on_ready():
    await DiscordReviewBot.log(f"Bot '{DiscordReviewBot.bot.user.name}' (ID: {DiscordReviewBot.bot.user.id}) has started.")

  @bot.command(
    help="Enters the provided review.",
    name="input_review"
  )
  @commands.has_role('Reviews') # TODO Where is this role defined?
  @commands.before_invoke(validate_command_channel)
  async def input_review(ctx, username: str, rating: str, url: str):
    await DiscordReviewBot.log(f"Inputting review for user '{username}': {rating}, {url}", ctx)

    result = ""
    async with asyncio.Lock():
      result = "`" + username + "` `" + rating + "` `" + url + "`\n" + await ctx.bot.loop.run_in_executor(None, DiscordReviewBot.discord_reddit.process_user_rating, username, rating, url)

    await ctx.send(result)

  # TODO Really hard to tell what is happening upstream of this.
  @input_review.error
  async def input_review_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
      await ctx.send(":wilted_rose: Sorry, you don't have permissions!")
    if isinstance(error, commands.errors.MissingRequiredArgument):
      await ctx.send(":wilted_rose: You are missing an argument:\n`input` `USERNAME` `RATING` `URL`.")
    if isinstance(error, commands.errors.BadArgument):
      await ctx.send(":wilted_rose: Ensure correct format:\n`input` `USERNAME` `RATING` `URL`.")

  @bot.command(
    help="Finds and returns the user's wiki.",
    name="check_user"
  )
  @commands.before_invoke(validate_command_channel)
  async def check_user(ctx, username):
    username = username.lower()

    await DiscordReviewBot.log(f"Checking subreddit wiki for user '{username}'.", ctx)

    try:
      user_wiki = DiscordReviewBot.discord_reddit.get_user_wiki(username)
      await DiscordReviewBot.log(f"Found the subreddit wiki for user '{username}'!", ctx)
      embed = discord.Embed(title=f"{user_wiki.username}", url=user_wiki.wiki_url, description=user_wiki.rating, color=0x84d7f9)
      await ctx.send(embed=embed)
    except Exception as e:
      await DiscordReviewBot.log(f"Failed to find subreddit wiki for user '{username}'! ([ERROR] {e})", ctx)
