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

# TODO These need to be class instance variables but the async methods are all static!!!
bot = commands.Bot(command_prefix=',')
debug_channel_id = 1000823699458506872 # TODO Parameterize
review_channel_id = 705624655649833082 # TODO Parameterize
discord_reddit = DiscordReddit("reddit.txt")


# TODO Add a help command.
class DiscordReviewBot:
  def __init__(self, token):
    bot.run(token)

  @bot.event
  async def on_ready():
    await DiscordReviewBot.log_debug_message(f"Bot '{bot.user.name}' (ID: {bot.user.id}) has started.")

  async def log_debug_message(message, ctx = None):
    if ctx is not None:
      await ctx.send(message) # Send the message back to the user before logging to the debug channel.
      command_context = f"\n\tbot={ctx.me}\n\tauthor={ctx.author}\n\tchannel_name={ctx.channel}\n\tcommand={ctx.command}\n\tcommand_args={ctx.args}"
      message = f"{message}{command_context}"

    print(f"[DEBUG] {message}") # TODO Python should have a logger library.
    debug_channel = bot.get_channel(debug_channel_id)
    await debug_channel.send(message)

  @bot.command(name='r')
  @commands.has_role('Reviews') # TODO Where is this role defined?
  async def input_review(ctx, username: str, rating: str, url: str):
    await DiscordReviewBot.log_debug_message(f"Inputting review for user '{username}': {rating}, {url}", ctx)

    result = ""
    async with asyncio.Lock():
      result = "`" + username + "` `" + rating + "` `" + url + "`\n" + await ctx.bot.loop.run_in_executor(None, discord_reddit.process_user_rating, username, rating, url)

    await ctx.send(result)

  @input_review.error
  async def input_review_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
      await ctx.send(":wilted_rose: Sorry, you don't have permissions!")
    if isinstance(error, commands.errors.MissingRequiredArgument):
      await ctx.send(":wilted_rose: You are missing an argument:\n`input` `USERNAME` `RATING` `URL`.")
    if isinstance(error, commands.errors.BadArgument):
      await ctx.send(":wilted_rose: Ensure correct format:\n`input` `USERNAME` `RATING` `URL`.")

  @bot.command(name='checkReview')
  async def checkReview(ctx, username):
    username = username.lower()

    await DiscordReviewBot.log_debug_message(f"Checking subreddit wiki for user '{username}'.", ctx)

    try:
      user_wiki = discord_reddit.get_user_wiki(username)
      await DiscordReviewBot.log_debug_message(f"Found the subreddit wiki for user '{username}'!", ctx)
      embed = discord.Embed(title=f"{user_wiki.username}", url=user_wiki.wiki_url, description=user_wiki.rating, color=0x84d7f9)
      await ctx.send(embed=embed)
    except Exception as e: # TODO Should be a custom exception?
      await DiscordReviewBot.log_debug_message(f"Failed to find subreddit wiki for user '{username}'! ([ERROR] {e})", ctx)

  # TODO A lot of the logic here makes more sense to go in the DiscordReddit class.
  @bot.command()
  async def fetchReviews(ctx, arg):
    await DiscordReviewBot.log_debug_message(f"Fetching {arg} review(s).", ctx)

    num_reviews = int(arg)
    if num_reviews>=0 and num_reviews<=1000:
      newReviews = []
      await ctx.send("Gathering past reviews...")
      pastReviews=await DiscordReviewBot.getPastReviews()
      if not pastReviews:
        await ctx.send("There were no recent post reviews in #reviews")
      await ctx.send("Gathering recent reddit posts and cross-checking with old posts...")
      for submission in discord_reddit.get_subreddit().search("flair:'New'",'new'):
        if submission.link_flair_text and "Trade Review" in submission.link_flair_text:
          found = False
          if pastReviews:
            for oldReview in pastReviews:
              #if this review has already been processed
              if oldReview[0] in submission.permalink:
                found=True
                break
          if not found:
            review = DiscordReviewBot.parseReview(submission)
            newReviews.append(review)
      await DiscordReviewBot.processReviews(ctx, newReviews)
    else:
      await ctx.send("Invalid arguments. Please include the number of reviews you want to fetch")

  # TODO This is a Reddit utility.
  def parseReview(submission):
    reddit_url = "https://www.reddit.com"
    user = ""
    rating = -1
    review=submission.title.replace("[","").replace("]","").lower().split()
    print("submission: " + submission.title.replace("[","").replace("]","").lower())
    for word in review:
      lowerCaseWord = word.lower()

      if word in ["0","1","2","3","4","5"] or lowerCaseWord in ["zero","one","two","three","four","five"]:
        if rating != -1:
          print("rating != -1")
          return [-1,submission.author.name,reddit_url+submission.permalink]

        if word.isdigit():
          rating = int(word)
        else:
          rating = DiscordReviewBot.wordToNum(lowerCaseWord)

      elif word.startswith("u/"):
        user = word[2:].strip(punctuation)
        print("User: " + word + ", " + user)

    print(str(user) + ": " + str(rating) + "\n")

    if rating >-1 and user:
      if rating == 5:
        return [0,user,rating,reddit_url+submission.permalink]
      else:
        return [1,user,rating,reddit_url+submission.permalink]
    #else cannot parse
    else:
      return [-1,submission.author.name,reddit_url+submission.permalink]

  # TODO This is a general utility.
  def wordToNum(word):
    switcher = {"zero":0,"one":1,"two":2,"three":3,"four":4,"five":5}
    return switcher[word]

  async def processReviews(ctx, newReviews):
    review_channel = bot.get_channel(705624655649833082)
    cantParse=""
    modReview=""
    if newReviews:
      for review in newReviews:
        #if error code 0, [error code, user, rating, url]
        if review[0] == 0:
          # print("5 stars")
          #await reviewChannel.send(",r "+review[1]+" "+str(review[2])+" <"+review[3]+">")
          await DiscordReviewBot.input_review(ctx, str(review[1]), str(review[2]), str(review[3]))
        #if error code -1, [error code, author, url]
        elif review[0] == -1:
          # print("cannot parse")
          cantParse+="[Submission by: "+review[1]+"]("+review[2]+")\n"
        #if error code 1, [error code, user, rating, url] 
        elif review[0] == 1:
          # print ("needs mod review")
          modReview+="["+str(review[2])+" stars to "+review[1]+"]("+review[3]+")\n"
        #else something went wrong
        else:
          await ctx.send("something went wrong")

      if cantParse:
        embed = discord.Embed(title="Could not parse the following review titles",description=cantParse, color =0xff4949)
        await review_channel.send(embed=embed)
      elif modReview:
        embed = discord.Embed(title="The following reviews are less than 5 stars and require mod review",description=modReview,color=0xacea48)
        await review_channel.send(embed=embed)
    else:
      await ctx.send("No reviews at this time")

  async def getPastReviews():
    currentReviewThread = "mhn3x5"
    pastReviews = []
    channel = bot.get_channel(review_channel_id)
    async for message in channel.history(limit=300):
      if(message.author.name == "Planty Bot" and "executed successfully" in message.content and not currentReviewThread in message.content):
        txt = message.content.replace("`","").split()
        idCode = txt[2][txt[2].find("comments/")+9:]
        idCode = idCode[:idCode.find("/")]
        pastReviews.append([idCode,txt[2]])
      return pastReviews