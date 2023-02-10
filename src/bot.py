import re
from collections.abc import Iterable
from os import getenv
from datetime import datetime, timezone, timedelta
from math import ceil, floor

from canvas import get_assignments_within_period, get_current_courses
from dotenv import load_dotenv
import discord

from userdata import UserData

intents = discord.Intents.default()
registered_users: dict[str, Iterable[UserData]] = dict()
prefix = "*"

intents.message_content = True

load_dotenv()

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message: discord.Message):
    # The bot can't reply to itself
    if message.author == client.user:
        return

    if (message.content.startswith(prefix)):
        await handle_command(message)


async def handle_command(msg: discord.Message):
    
    global prefix
    # Remove prefix from message.content
    msg.content = msg.content.lstrip(msg.content[:len(prefix)])
    print(msg.content)
    match msg.content.split()[0]:
        case "help":
            message = \
            f"""
            Use {prefix}register [base url] [api key] to register with this bot
    Example: {prefix}register https://instructure.com 2~3948392jkddf8d9fD7fd
Use {prefix}weekly to get upcoming assignments for each class that are due within the week
Use {prefix}prefix to change the prefix of the bot
            """
            await msg.channel.send(message)
        case "prefix":
            prefix = re.match("prefix\s+(.+)\s*", msg.content).group(1)
            await msg.channel.send(f"Set prefix to {prefix}")
        case "register":
            await register_command(msg)
        case "weekly":
            await weekly_command(msg)
        case _:
            print("Command not recognized")
            msg.channel.send("Command not recognized")

async def register_command(msg: discord.Message):
    matches = re.match("register\s+(http?s://[^ ]+)\s+([^ ]+)", msg.content)
    base_url, api_key = matches.group(1), matches.group(2)

    if (registered_users.get(msg.author) == None):
        registered_users[msg.author] = []
    registered_users[msg.author].append(UserData(api_key, base_url))

    await msg.channel.send(f"You have been registered {msg.author}!")


async def weekly_command(msg: discord.Message):
    userdata = registered_users.get(msg.author)

    if (not userdata):
        return

    now = datetime.now(timezone.utc)
    end = now + timedelta(days=7)
    assignments = get_assignments_within_period(now, end, userdata)
    message = ""
    for assignment in assignments:
        message += assignment.name
        if (hasattr(assignment, "due_at_date")):
            time = int(assignment.due_at_date.timestamp())
            message += f", due in <t:{time}:R>"
        if (hasattr(assignment, "html_url")):
            message += f", url: [link]({assignment.html_url})"
        message += "\n"
    await send_large_message(message, msg.channel)

MAX_SINGLE_MESSAGE_LENGTH = 1500
async def send_large_message(string: str, channel: discord.PartialMessageable):
    """
    Split a message into discord consumable parts

    :param string: The message to send in string format
    :param channel: The channel to send the message through
    """
    if (len(string) < MAX_SINGLE_MESSAGE_LENGTH):
        await channel.send(string)
        return
    parts = ceil(len(string) / MAX_SINGLE_MESSAGE_LENGTH)

    split_string = string.splitlines()
    split_count = floor(len(split_string) / parts)

    message_queue = []
    for part in range(parts):
        string_part = await handle_message_part(split_string, split_count * part, split_count * (part + 1))
        message_queue.append ( channel.send(string_part) )
    for message in message_queue:
        await message
    print("SEND LARGE MESSAGE: finished message")

async def handle_message_part(split_string: list[str], start_index: int, end_index: int) -> str:
    string_part = "\n".join( split_string[ start_index : end_index ] )
    print(f"SEND LARGE MESSAGE: Adding {len(string_part)} characters to message")
    return string_part

client.run(getenv("BOT_TOKEN"))