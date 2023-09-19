import discord
from discord.ext import commands
import smtplib
from email.message import EmailMessage
import asyncio
import os
import logging
import yaml
import zipfile


# Create an instance of the Intents class with default values
intents = discord.Intents.default()
intents.message_content = True
intents.members = True          # If you enabled Server Members Intent
# Initialize Discord bot with the specified intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Read the YAML file
with open("config.yaml", 'r') as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

# Get the values from the YAML file
server_directory = config.get("server_directory", "/default/path")
email_address = config.get("email_address", "")
email_app_password = config.get("email_app_password", "")
techlab_email = config.get("techlab_email", "")
bot_token = config.get("bot_token")

# Your existing Python code here

@bot.event
async def on_ready():
    print("Bot is ready")

@bot.event
async def on_message(message):
    ctx = await bot.get_context(message)
    
    author = str(message.author)
    
    if message.author == bot.user:
        print("Message from bot. Ignoring.")
        return

    print(f"Received a message from {author}: {message.content}")

    # Check if the message is from a channel
    if message.guild is not None:

        if len(message.attachments) > 0:
            print("Attachments found.")

            if len(ctx.message.attachments) == 0:
                print("No attachments found in context message.")
                await ctx.send("No files attached!")
                return

            print(f"Found {len(ctx.message.attachments)} attachment(s) in context message.")

            for attachment in ctx.message.attachments:
                print(f"Processing attachment: {attachment.filename}")

                if attachment.filename.endswith('.zip'):
                    print(f"Saving {attachment.filename}...")
                    
                    local_path = os.path.join(server_directory, attachment.filename + author)
                    
                    try:
                        await attachment.save(local_path)
                        print("Attachment saved.")

                        # Unzip the saved file
                        unzip_path = os.path.join(server_directory, 'unzipped_' + author)
                        with zipfile.ZipFile(local_path, 'r') as zip_ref:
                            zip_ref.extractall(unzip_path)
                        print(f"Attachment unzipped to {unzip_path}.")

                    except Exception as e:
                        print(f"Error occurred: {e}")

                    # Delete the message from the channel
                    try:
                        await message.delete()
                        await ctx.send(f"Uploaded ✅ and deleted your zip from the chat... Good Job {author}. The TechLab team will review your assignment as soon as possible ⏳")
                    except Exception as e:
                        print(f"Error while deleting message or sending confirmation: {e}")
                        return

                    # Assuming send_email is defined, uncomment the next line to call it.
                    send_email(attachment.filename, author)
                else: print(f"Skipped {attachment.filename} as it's not a .zip file.")

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def send_email(file_name, author):
    logging.info("send_email function invoked.")
    try:
        msg = EmailMessage()
        msg['Subject'] = f'Pass off from {author}'
        msg['From'] = email_address
        msg['To'] = techlab_email
        msg.set_content(f'The file {file_name} has been uploaded to the server, and ready to be reviewed.')

        logging.info(f"Attempting to send email with subject: {msg['Subject']}")

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(email_address, email_app_password)
            smtp.send_message(msg)

        logging.info("Email sent successfully to " + techlab_email)
    except Exception as e:
        logging.error(f"An error occurred: {e}")        
@bot.event
async def on_command_error(ctx, error):
    print(f"An error occurred: {error}")

# Run the bot
bot.run(bot_token)