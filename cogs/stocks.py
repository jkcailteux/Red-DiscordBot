
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


class Stocks:
    """General commands."""

    def __init__(self, bot):
        self.bot = bot
        self.data = ""

    @commands.group(pass_context=True)
    async def stocks(self, ctx, *, term: str = ""):
        """Stocks"""

        stock_url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=" + \
            str(term)
        stock_url = stock_url + "&apikey=CYGECFFT35KMZ8E4"

        with urllib.request.urlopen(stock_url) as req:
            stock_days = json.loads(req.read().decode())['Time Series (Daily)']
            # msg_price = "$" + \
            #     str(crypto['quotes']['USD']['price']) + "/" + crypto['symbol']
            # msg_percent = str(crypto['quotes']['USD']
            #                   ['percent_change_24h']) + "%"
            # msg_rank = "#" + str(crypto['rank'])
            # await self.bot.say("```" + msg_price + " " + msg_percent + " " + msg_rank + "```")
            await self.bot.say(stock_days)
            return


def setup(bot):
    bot.add_cog(Stocks(bot))
