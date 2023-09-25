import discord
import os
from discord.ext import commands
import smtplib
from email.message import EmailMessage
import asyncio
import logging
import yaml
import zipfile

from discord_csv_manipylations import list_homeworks,get_classes_from_filenames, list_students_in_class, read_csv_headers, update_student_in_csv,get_class_by_discord_username,update_homework_status_in_csv


# Create an instance of the Intents class with default values
intents = discord.Intents.default()
intents.message_content = True
intents.members = True          # If you enabled Server Members Intent
# Initialize Discord bot with the specified intents
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
# Check current working directory
print("Current Working Directory:", os.getcwd())

# Check if the file exists in the current working directory
if os.path.exists("config.yaml"):
    print("config.yaml exists")
else:
    print("config.yaml does not exist")

# Your existing code for reading config.yaml
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
    for server in bot.guilds:
        await bot.tree.sync(guild=discord.Object(id=server.id))

@bot.event
async def on_message(message):
    ctx = await bot.get_context(message)
    
    author = str(message.author.display_name)
    
    if message.author == bot.user:
        print("Message from bot. Ignoring.")
        return

    print(f"Received a message from {author}: {message.content}")

    ctx = await bot.get_context(message)
    
    author = str(message.author.display_name)
    
    if message.content.startswith('/pass_off_setup'):
        await pass_off_setup(ctx)
    
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
                        channel = bot.get_channel(1153520298717610076)
                        file = discord.File(local_path, filename=attachment.filename)
                        await channel.send(content=f"Homework from {author}", file=file)
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
                        await ctx.send(f"Uploaded your homework to the server ✅, and deleted your zip from the chat... Good Job {author}.")
                        await message.author.send(f"The TechLab team will review your homework as soon as possible ⏳.")
                    except Exception as e:
                        print(f"Error while deleting message or sending confirmation: {e}")
                        return

                    # Assuming send_email is defined, uncomment the next line to call it.
                    # send_email(attachment.filename, author)
                else: print(f"Skipped {attachment.filename} as it's not a .zip file.")

@bot.tree.command(name="test", description="Test to see if slash commands are working")
async def test(interaction):
    await interaction.response.send_message("Test")
    
# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
print("Registering pass_off_setup command")
@bot.tree.command(name = "pass_off_setup", description = "sets up the bot for your username")
async def pass_off_setup(ctx):
    print("passoff setup: ")
    classes = get_classes_from_filenames("Developer/discord_bot/CSV/students")
    class_options = "\n".join(classes)
    print("class options {}",class_options)
    await ctx.send(f"Which class are you taking?\n{class_options}")

    def class_check(m):
        return m.channel == ctx.channel and m.content in classes
    selected_class = await bot.wait_for("message", check=class_check)
    read_csv_headers(selected_class)
    parts = selected_class.content.split(" ")
    teacher = parts[0]
    course = parts[1]
    section = parts[-1]
    class_csv = f"{teacher}_{course}_{section}.csv"

    students = list_students_in_class(class_csv)
    student_options = "\n".join(students)
    await ctx.send(f"Which student are you?\n{student_options}")

    def student_check(m):
        return m.channel == ctx.channel and m.content in students
    selected_student = await bot.wait_for("message", check=student_check)

    update_student_in_csv(class_csv, selected_student.content, ctx.author.display_name, str(ctx.author.id))

    await ctx.send(f"Setup complete. You are now linked as {selected_student.content} in the class {selected_class.content}.")

@bot.command(name='homework_submission')
async def homework_submission(ctx):
    # Get the class associated with the user (you may need to change this logic based on your actual setup)
    discord_username = str(ctx.author.id)
    associated_class = get_class_by_discord_username("CSV/students", discord_username)

    if associated_class is None:
        await ctx.send("You need to set up the bot first. Please run `/pass_off_setup`.")
        return    
    
    class_csv = f"CSV/students/{associated_class}.csv"

    # List available homework for the student
    homeworks = list_homeworks(class_csv, str(ctx.author.display_name))
    if not homeworks:
        await ctx.send("You have no homework left to submit.")
        return

    homework_options = "\n".join(homeworks)
    await ctx.send(f"You are associated with class {associated_class}. Which homework would you like to submit?\n{homework_options}")

    def homework_check(m):
        return m.channel == ctx.channel and m.content in homeworks
    selected_homework = await bot.wait_for("message", check=homework_check)

    # Wait for .zip file
    await ctx.send("Please upload your .zip file for the selected homework.")

    def zip_check(m):
        return m.channel == ctx.channel and m.author == ctx.author and len(m.attachments) > 0 and m.attachments[0].filename.endswith('.zip')
    message_with_zip = await bot.wait_for("message", check=zip_check)

    # Save and Forward the .zip
    attachment = message_with_zip.attachments[0]
    local_path = os.path.join(server_directory, attachment.filename)
    await attachment.save(local_path)

    # Forward to #pass_off_bot_beta thread (Assuming you have the channel and thread IDs)
    channel = bot.get_channel(1153520298717610076)
    file = discord.File(local_path, filename=attachment.filename)
    await channel.send(file=file)

    # Update CSV (implement this function)
    update_homework_status_in_csv(class_csv, str(ctx.author.display_name), selected_homework.content, "Submitted")

    await ctx.send("Homework submitted successfully!")

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
