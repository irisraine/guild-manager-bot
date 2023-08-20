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

This bot does not have any commands, as it is designed to run automatically in the background.

## Usage

If you want to use this bot locally, please make sure to specify the necessary environment variables by creating a .env file 
in the project directory. This file should contain TOKEN and ALLOWED_CHANNELS environment variables and their corresponding values.
Finally, you need an API key of Microsoft Content Moderator service.
Here is an example:
```
# Bot token
TOKEN='your-discord-bot-token-here'
# Allowed channels
ALLOWED_CHANNELS=1111111111, 2222222222
# API key of Microsoft Content Moderator service
NSFW_CONTENT_MODERATOR_API_KEY='your-api-key-here'
```
You can intentionally leave blank the ALLOWED_CHANNELS variable, so bot will have permission to create threads in any public channel.

Once you have added all the necessary environment variables to the .env file, you are ready to use the bot. 