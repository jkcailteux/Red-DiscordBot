
import json
import urllib.request

from discord.ext import commands


class Stocks:
    """General commands."""

    def __init__(self, bot):
        self.bot = bot
        self.data = ""

    @commands.group(pass_context=True)
    async def stocks(self, ctx, *, term: str = ""):
        """Stocks"""

        api_key = "&apikey=CYGECFFT35KMZ8E4"
        term = term.replace(" ", "+")
        search_url = "https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords=" + term + api_key

        with urllib.request.urlopen(search_url) as req:
            response = json.loads(req.read().decode())
            if 'Error Message' in response:
                await self.bot.say('Error getting stock: \"' + term + '\"')
                return
            results = response["bestMatches"]
            if len(results) > 0:

                company_symbol = results[0]["1. symbol"]
                company_name = results[0]["2. name"]

                stock_url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol="
                stock_url = stock_url + company_symbol + api_key

                with urllib.request.urlopen(stock_url) as req2:
                    response2 = json.loads(req2.read().decode())
                    if 'Error Message' in response2:
                        await self.bot.say('Error getting stock: \"' + term + '\"')
                        return
                    stock_days = response2['Time Series (Daily)']
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

                    msg = '```' + 'Stock: $' + str(current_price) + '/' + company_symbol + ' ' + change_str
                    msg = msg + ", " + company_name + '```'
                    await self.bot.say(msg)
                    return

    @commands.group()
    async def stonks(self):
        await self.bot.say("https://i.imgur.com/EFqRbev.png")
        return
    

def setup(bot):
    bot.add_cog(Stocks(bot))
