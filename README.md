# Image Thread Manager bot

## Description

This Discord bot is designed to automatically create a discussion thread in the current channel whenever a user posts 
an image. The bot will use the image as the initial message content for the thread and will include a welcome message 
to encourage users to start a discussion.

This bot does not have any commands, as it is designed to run automatically in the background.

## Usage

If you want to use this bot locally, please make sure to specify the necessary environment variables by creating a .env file 
in the project directory. This file should contain TOKEN and ALLOWED_CHANNELS environment variables and their corresponding values.
Here is an example:
```
# Bot token
TOKEN='your-discord-bot-token-here'
# Allowed channels
ALLOWED_CHANNELS=1111111111, 2222222222
```
You can intentionally leave blank the ALLOWED_CHANNELS variable, so bot will have permission to create threads in any public channel.

Once you have added all the necessary environment variables to the .env file, you are ready to use the bot. 