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
        self.data = ""
        self.last_time = 0

    @commands.group(pass_context=True)
    async def crypto(self, ctx, *, term: str=None):
        """Crypto"""
        url = "https://api.coinmarketcap.com/v1/ticker"
        data = self.data
        if time.time() > self.last_time + 30:
            with urllib.request.urlopen(url) as req:
                data = json.loads(req.read().decode())
                self.last_time = time.time()
        self.data = data
        msg = term + " not found"
        for crypto in data:
            if term.lower() == crypto['id'].lower():
                msg = "$" + crypto['price_usd'] + "/" + crypto['symbol']
                break
            if term.lower() == crypto['name'].lower():
                msg = "$" + crypto['price_usd'] + "/" + crypto['symbol']
                break
            if term.lower() == crypto['symbol'].lower():
                msg = "$" + crypto['price_usd'] + "/" + crypto['symbol']
                break
        msg = "```" + msg + "```" 
        await self.bot.say(msg)
        

def setup(bot):
    bot.add_cog(Crypto(bot))
