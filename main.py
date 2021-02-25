import discord
import random
import praw
import json
import asyncio
import os
from discord.ext import commands, tasks
from discord.utils import get
from itertools import cycle

settings = json.load(open('config.json'))
token = settings['token']
prefix = settings['prefix']
botrole = settings['bot-role']
staffrole = settings['staff-role']

reddit = praw.Reddit(client_id="",
                     client_secret="",
                     password="",
                     user_agent="",
                     username="")

client = commands.Bot(command_prefix = f"{prefix}")
client.remove_command("help")

status = cycle(['STATUS1', 'STATUS2'])


@client.event
async def on_ready():
    print("Bot is ready.")
    presence.start()

@client.event
async def on_command_error(ctx, error):
    if isinstance(error,commands.MissingPermissions):
        await ctx.send(f":x: {ctx.author.mention} No Permissions!")


@tasks.loop(seconds=10)
async def presence():
    await client.change_presence(activity=discord.Game(next(status)))


@client.command()
@commands.has_permissions(manage_messages = True)
async def purge(ctx, amount=3):
    await ctx.channel.purge(limit=amount)
    await ctx.send (f"{amount} messages purged by {ctx.author.mention}")

@client.command()
@commands.has_permissions(kick_members = True)
async def kick(ctx, member : discord.Member, *, reason=None):
        await member.kick(reason=reason)
        await ctx.send(f"{member.mention} has been kicked by {ctx.author.mention} for {reason}")

@client.command()
@commands.has_permissions(ban_members = True)
async def ban(ctx, member : discord.Member, *, reason=None):
        await member.ban(reason=f"{reason} - banned by {ctx.author}")
        await ctx.send(f"{member.mention} has been banned by {ctx.author.mention} for {reason}")


@client.command(aliases=['8ball'])
async def _8ball(ctx, * , question):
    responses = ["It is certain.",
    "It is decidedly so.",
    "Without a doubt.",
    "Yes - definitely.",
    "You may rely on it.",
    "As I see it, yes.",
    "Most likely.",
    "Outlook good.",
    "Yes.",
    "Signs point to yes.",
    "Reply hazy, try again.",
    "Ask again later.",
    "Better not tell you now.",
    "Cannot predict now.",
    "Concentrate and ask again.",
    "Don't count on it.",
    "My reply is no.",
    "My sources say no.",
    "Outlook not so good.",
    "Very doubtful."]
    await ctx.send(f':8ball: {random.choice(responses)}')

@client.command()
async def ticket(ctx, *, reason='Null'):
    if reason == 'Null':
        await ctx.channel.send("``Please provide a reason. E.g. !ticket I lost all my guns :(``")
    else:

        with open("config.json") as f:
            data = json.load(f)

        ticket_number = int(data["ticket-counter"])
        ticket_number += 1

        exists = discord.utils.get(ctx.guild.text_channels, name="ticket-{}".format(ticket_number))
        staff_role = get(ctx.guild.roles, name=staffrole)
        bot_role = get(ctx.guild.roles, name=botrole)

        if exists is not None:
            await ctx.channel.send("You already have an active ticket!")
        else:
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                ctx.author: discord.PermissionOverwrite(read_messages=True, manage_messages=True),
                staff_role: discord.PermissionOverwrite(read_messages=True),
                bot_role: discord.PermissionOverwrite(read_messages=True)
            }

            category = discord.utils.get(ctx.guild.categories, name='tickets')
            channel = await ctx.guild.create_text_channel("ticket-{}".format(ticket_number), category=category, overwrites=overwrites)
            await ctx.channel.send(f"Made a ticket! {channel.mention}")

            to_send = client.get_channel(channel.id)

            data["ticket-counter"] = int(ticket_number)
            with open("config.json", 'w') as f:
                json.dump(data, f)
                
            await to_send.send(f"User {ctx.author.mention} has created a ticket for reason ``{reason}`` <@&786608250190692374>")

@client.command()
@commands.has_permissions(manage_messages=True)
async def close(ctx, *, reason='Null'):
    channelCategory = str(ctx.channel.category)
    if channelCategory == 'tickets':
        await ctx.channel.delete()

@client.command()
async def meme(ctx):
        redditembed=discord.Embed(
        title="", 
        icon="",
        )
        subreddit = reddit.subreddit('funny').hot()
        for submission in range(0, random.randint(1, 100)):
                    submission = next(x for x in subreddit if not x.stickied)
        redditembed.set_author(name = f"{submission.title}", icon_url = "")
        redditembed.set_image(url=submission.url)
        redditembed.set_footer(text=f"posted by u/{submission.author}")
        await ctx.send(embed=redditembed)

@client.command()
async def dice(ctx):
    await ctx.send(f':game_die: You rolled {random.randrange(1,6)}')





client.run(token)