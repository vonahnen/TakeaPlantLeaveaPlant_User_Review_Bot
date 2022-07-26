from discord_bot import DiscordReviewBot

def main():
	bot = DiscordReviewBot(open("discord.txt", "r").readline().strip())

if __name__ == '__main__':
	main()
