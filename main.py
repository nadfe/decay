import discord
from discord.ext import commands
from discord import Spotify
import json
import os
from os import system, name
import random
import requests
import subprocess
import sys
from colorama import Fore

bot = commands.Bot(command_prefix='', self_bot=True, fetch_offline_members=False)
bot.remove_command('help')

# ASCII Splash Screens
@bot.event
async def on_ready():
    def ascii():
        i = random.randrange(12) + 1
        if sys.platform == 'win32':
            os.system("cls")
            print(open("./art/" + str(i) + '.txt').read())
            print()
            print(Fore.WHITE + "[+] {0}".format(bot.user) + Fore.RED)
        elif sys.platform == 'linux' or 'darwin':
            os.system("clear")
            os.system("cat art/" + str(i) + '.txt | lolcat')
            print()
            print(Fore.WHITE + "[+] {0}".format(bot.user) + Fore.RED)
    ascii()

# Ignore missing commands in console but raise all other errors
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass
    else:
        raise error

# Retrieves bot user's Discord WebSocket latency.
@bot.command()
async def PING(ctx):
    await ctx.message.edit(content=f":ping_pong:`Ping: {round(bot.latency * 1000)}ms`")

# Restarts script from within itself without spawning a new terminal window.
@bot.command()
async def rsc(ctx):
    await ctx.message.delete()
    subprocess.signal.SIGINT
    os.execl(sys.executable, sys.executable, * sys.argv)

# Message clear command. Clearing with a set amount currently counts messages from all users and not the bot user.
@bot.command()
async def cl(ctx, amount=None):
    if not amount:
        amount = 1999
    try:
        async for ctx.message in ctx.channel.history(limit=int(amount) + 1):
            if ctx.message.author == bot.user:
                await ctx.message.delete()
    except discord.Forbidden:
        pass

# Crypto price command. Uses cryptowatch API.
@bot.command()
async def PRICE(ctx):
    embed = discord.Embed(color=0xf2a900)
    price = 'https://api.cryptowat.ch/markets/kraken/btcusd/price'
    response = requests.get(price).json()
    btc = str(response["result"]["price"])
    price = 'https://api.cryptowat.ch/markets/kraken/ethusd/price'
    response = requests.get(price).json()
    eth = str(response["result"]["price"])
    embed.add_field(name="BTC", value="$" + btc, inline=False)
    embed.add_field(name="ETH", value="$" + eth, inline=False)
    await ctx.send(embed=embed)

# Retrieves avatar from any user from any mutual server. For more accurate results, its best to mention the user but just appending the username works fine.
@bot.command()
async def av(ctx, user: discord.User = None):
    if not user:
        user = bot.user
    avatar = user.avatar_url_as(static_format='png', size=1024)
    await ctx.send(avatar)

# Spotify status
@bot.command(aliases=['fm'])
async def spotify(ctx, user: discord.Member=None):
    user = user or ctx.author

    for activity in user.activities:
        if isinstance(activity, Spotify):
            embed = discord.Embed(color=0x1ed760)
            embed.set_author(name=f"{user.nick or user.name} is listening to:", icon_url="https://i.imgur.com/5bPu8ke.jpg")
            embed.set_thumbnail(url=activity.album_cover_url)
            embed.add_field(name="Track:", value=f"[{activity.title}](https://open.spotify.com/track/{activity.track_id})")
            embed.add_field(name="Artist:", value=f"[{activity.artist}](https://open.spotify.com/track/{activity.track_id})")
            embed.set_footer(text=f"Album: {activity.album} | Track ID: {activity.track_id}")
            await ctx.send(embed=embed)
        break
    else:
        pass

# Accesses token from json file to prevent token leaks when sending a signal interrupt or editing code while screensharing with people :)
token = json.loads(open("token.json").read())['token']
bot.run(token, bot=False)
