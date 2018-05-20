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
        self.data = ""
        self.listings = ""
        self.last_time = 0

    @commands.group(pass_context=True)
    async def crypto(self, ctx, *, term: str=""):
        """Crypto"""

        if (term.lower() == "jeth"):
            await self.bot.say("```JETH is priceless```")
            return

        if (term.lower() == "meth"):
            await self.bot.say("```Don't do drugs kids```")
            return

        await getListings(self)
        cryptoId = 0

        for crypto in self.listings['data']:
            if term.lower() == crypto['name'].lower():    
                cryptoId = crypto['id']
                break
            if term.lower() == crypto['symbol'].lower():    
                cryptoId = crypto['id']
                break
            if term.lower() == crypto['website_slug'].lower():    
                cryptoId = crypto['id']
                break

        if cryptoId == 0:
            await self.bot.say("```" + term + " not found" + "```")
            return

        msg = ""
        crypto_url = "https://api.coinmarketcap.com/v2/ticker/" + str(cryptoId) + "/"
        with urllib.request.urlopen(crypto_url) as req:
            crypto = json.loads(req.read().decode())['data']
            msg_price = "$" + str(crypto['quotes']['USD']['price']) + "/" + crypto['symbol']
            msg_percent = str(crypto['quotes']['USD']['percent_change_24h']) + "%"
            msg_rank = "#" + str(crypto['rank'])
            await self.bot.say("```" + msg_price + " " + msg_percent + " " + msg_rank + "```")
            return
        
def setup(bot):
    bot.add_cog(Crypto(bot))

async def getListings(self):
    listings_url = "https://api.coinmarketcap.com/v2/listings"
    if self.listings == "":
        with urllib.request.urlopen(listings_url) as req:
            self.listings = json.loads(req.read().decode())        