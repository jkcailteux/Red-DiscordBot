
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

        stock_url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=" + term
        stock_url = stock_url + "&apikey=CYGECFFT35KMZ8E4"

        with urllib.request.urlopen(stock_url) as req:
            response = json.loads(req.read().decode())
            if 'Error Message' in response:
                await self.bot.say('Error getting stock: \"' + term.upper() + '\"')
                return
            stock_days = response['Time Series (Daily)']
            current_day_key = sorted(stock_days.keys())[-1]
            past_day_key = sorted(stock_days.keys())[-2]

            current_day = stock_days[current_day_key]
            past_day = stock_days[past_day_key]

            current_price = float(current_day['4. close'])
            past_price = float(past_day['4. close'])

            change = current_price / past_price
            change_str = ''
            if change >= 1:
                change_str = str(round((change - 1) * 100, 2)) + '%'
            else:
                change_str = '-' + str(round((1 - change) * 100, 2)) + '%'

            msg = '```' + 'Stock: $' + str(current_price) + '/' + term.upper() + ' ' + change_str + '```'
            await self.bot.say(msg)
            return


def setup(bot):
    bot.add_cog(Stocks(bot))
