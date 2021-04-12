# /r/TakeaPlantLeaveaPlant User Review Bot
A user review bot for /r/TakeaPlantLeaveaPlant.

## User Guide

### Leave a Review (Moderators Only)
Leave a review, broski.

```
,r <Reddit Username> <[0-5]> <Reddit URL being Reviewed>
```

### Check Review (All Users)
Gives a Reddit user's averaged rating along with a URL to the user directory with all reviews.

```
,checkReview <Reddit Username>
```

## Requirements
1. Install [Python 3.6.8](https://www.python.org/downloads/release/python-368/)
2. Install [PRAW](https://praw.readthedocs.io/en/latest/getting_started/installation.html)

### Reddit Configuration
1. [Create a new Reddit app](https://reddit.com/prefs/apps)
   1. Select `script` type app
   2. `redirect uri` can be something like `http://localhost:8080`
2. Note the `personal use script` and the `secret` values

### Discord Configuration
1. [Create a new Discord app](https://discord.com/developers/applications).
    1. Click the `New Application` button in the top right-hand corner.
    2. Give it a fabulous name.
2. Open the new application and select `Bot` from the left-hand menu.
    1. Click `Add Bot` (and approve it).
    2. Reveal and note the bot's `TOKEN`.

## Usage
### Authentication
This app uses basic ["Password Flow" authentication](https://praw.readthedocs.io/en/latest/getting_started/authentication.html#password-flow). You will need two .txt files located inside of this script's directory in order for the application to run.

#### reddit.txt
This file will contain all of the information required to interact with your Reddit application, with one field per line. An example file is provided in this repo.

1. **Client ID** - The Reddit application's `personal use script` found in your Reddit bot's [authorized applications](https://ssl.reddit.com/prefs/apps/).
2. **Client Secret** - The Reddit application's `secret` found in your Reddit bot's [authorized applications](https://ssl.reddit.com/prefs/apps/).
3. **Username** - Your Reddit bot's username.
4. **Password** - Your Reddit bot's password.

#### discord.txt
This file will contain all of the information required to interact with your Discord bot, with one field per line. An example file is provided in this repo.

1. **Token** - The Discord bot's token found in your application's bot in [Applications](https://discord.com/developers/applications) (e.g. https://discord.com/developers/applications/THE_APPLICATION_ID_OR_WHATEVER/bot).

### Set Up
* Line `THE_FILE = "NAME.txt"` near the top can be changed to whatever you want your temporary local version of your wikipage to be. 
* In `main()` modify `sub = reddit.subreddit("YOUR_SUBREDDIT_NAME")` and `page = sub.wiki["YOUR_REVIEWS_WIKI_PAGE"]`
* I haven't tested what happens if you don't have the wiki pages for each character already set up. You may want to set up the wiki pages before hand. 

### Program Execution
When running the program, you will be prompted to enter a string consisting of `username rating review_URL`. Once this is entered, the review wiki page gets updated and the user's flair is calculated and set. 
