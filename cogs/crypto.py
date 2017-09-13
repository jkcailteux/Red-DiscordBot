from discord.ext import commands
from random import choice
from .utils.dataIO import dataIO
from .utils import checks
from .utils.chat_formatting import box
from collections import Counter, defaultdict, namedtuple
import discord
import time
import os
import urllib.request 
import json

class Crypto:
    """General commands."""
    def __init__(self, bot):
        self.bot = bot
        self.file_path = "data/crypto/settings.json"
        settings = dataIO.load_json(self.file_path)
        self.settings = defaultdict(lambda: DEFAULTS.copy(), settings)

    @commands.group(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(administrator=False)
    async def crypto(self, ctx, *, term: str=None):
        """Crypto"""
        url = "https://api.coinmarketcap.com/v1/ticker" 
        with urllib.request.urlopen(url) as req:
            data = json.loads(req.read().decode())
            msg = term + " not found"
            for crypto in data:
                if term == crypto['id']:
                    msg = "$" + crypto['price_usd'] + "/" + crypto['symbol']
                if term == crypto['name'].lower():
                    msg = "$" + crypto['price_usd'] + "/" + crypto['symbol']
                if term == crypto['symbol'].lower():
                    msg = "$" + crypto['price_usd'] + "/" + crypto['symbol']
            
            await self.bot.say(msg)    

def check_folders():
    folders = ("data", "data/crypto/")
    for folder in folders:
        if not os.path.exists(folder):
            print("Creating " + folder + " folder...")
            os.makedirs(folder)


def check_files():
    if not os.path.isfile("data/crypto/settings.json"):
        print("Creating empty settings.json...")
        dataIO.save_json("data/crypto/settings.json", {})


def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(Crypto(bot))
