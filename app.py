from discord_bot import DiscordReviewBot

def main():
	bot = DiscordReviewBot.get_instance(open("discord.txt", "r").readline().strip(), 1000823699458506872, 705624655649833082)
	bot.run()

if __name__ == '__main__':
	main()
