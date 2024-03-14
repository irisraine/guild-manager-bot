# Image Thread Manager bot

## Description

This Discord bot is designed to automatically create a discussion threads in the current channel whenever a user posts 
an image. The bot will use the image as the initial message content for the thread and will include a welcome message 
to encourage users to start a discussion.
Also this bot provides a moderation functions. It designed to automatically detect and delete NSFW images, temporarily 
block users who post them, as well as identify and remove spam messages during raids, while blocking the spammers.

The bot sends the uploaded images to the Microsoft Content Moderator service, which analyzes the images and returns a confidence 
score indicating the likelihood of the image containing NSFW content. The bot then compares this score to a predefined 
threshold to determine whether the image should be considered NSFW.
By utilizing the Content Moderator service, the bot can accurately detect and moderate NSFW images in real-time, ensuring 
a safe and appropriate environment for all users.

Another moderation function of the bot is watching over using of gif images by users and response if someone tries to overuse them - bot
detects whether user post gif image more than once per 10 minutes, and delete all excessive images, posted during this period.

Finally, this Discord bot has an option to automatically update your server's banner to display the overall number of server members and 
the number of members in voice channels. It's a great way to showcase your server's activity level and engagement at a glance!

All these functions is designed to run automatically in the background.

## Usage

If you want to use this bot locally, please make sure to specify the necessary environment variables by creating a .env file 
in the project directory. This file should contain DISCORD_BOT_TOKEN, GUILD_ID, COMMON_DISCUSSION_CHANNEL and ALLOWED_CHANNELS 
environment variables and their corresponding values.
Finally, you need an API key of Microsoft Content Moderator service, and place it to CONTENT_MODERATOR_API_KEY variable.
Here is an example:
```
# Bot token
DISCORD_BOT_TOKEN='your-discord-bot-token-here'
# ID of your server
GUILD_ID = 1111111111111111111
# Allowed channels
ALLOWED_CHANNELS=22222222222222, 333333333333333333
# Common discussion channel
COMMON_DISCUSSION_CHANNEL=4444444444444444
# API key of Microsoft Content Moderator service
CONTENT_MODERATOR_API_KEY='your-api-key-here'
```
You can intentionally leave blank the ALLOWED_CHANNELS variable, so bot will have permission to create threads in any public channel.

Once you have added all the necessary environment variables to the .env file, you are ready to use the bot. 

If you want to use a dynamic banner function, be sure that you put your current server's banner image in `assets` folder with name `banner.jpg` (replace the default image). 
The image must have a resolution of 1024x576 pixels.

## Commands

- `.dynamic_banner` - activate dynamic banner. After using this command, bot will automatically update the server banner with 
info of overall server members number. Updating period is set to 10 minutes.
- `.static_banner` - turn off dynamic banner.
- `toggle_gif_limits` - turn on/off gif images limitation function.

## Limitations

it is important to note that this bot has certain limitations due to the nature of image analysis. The process of analyzing
each image by AI takes approximately 1 to 2 seconds, which means that in order for the bot to function correctly, it is recommended 
to use it only on Discord servers with channels in slow mode, which ensures a minimum cooldown of 5 seconds between messages 
from a single author, allowing the bot enough time to accurately analyze and remove any potentially explicit content. By 
adhering to these guidelines, you can ensure the effective functioning of this Discord bot.