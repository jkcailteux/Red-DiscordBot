import json
import time
import urllib.request

from discord.ext import commands


class Crypto:
    """General commands."""

    def __init__(self, bot):
        self.bot = bot
        self.data = ""
        self.listings = dict()
        self.last_time = 0

    @commands.group(pass_context=True)
    async def crypto(self, ctx, *, term: str = ""):
        """Crypto"""

        if term.lower() == "jeth":
            await self.bot.say("```JETH is priceless```")
            return

        if term.lower() == "meth":
            await self.bot.say("```Don't do drugs kids```")
            return

        await get_listings(self)
        crypto_id = 0

        for crypto in self.listings.values():
            if term.lower() == crypto['name'].lower():
                crypto_id = crypto['id']
                break
            if term.lower() == crypto['symbol'].lower():
                crypto_id = crypto['id']
                break
            if term.lower() == crypto['slug'].lower():
                crypto_id = crypto['id']
                break

        if crypto_id == 0:
            await self.bot.say("```" + term + " not found" + "```")
            return

        crypto = self.listings[crypto_id]
        msg_price = "$" + "{:.2f}".format(crypto['quote']['USD']['price']) + "/" + crypto['symbol']
        msg_percent = "{:.2f}".format(crypto['quote']['USD']['percent_change_24h']) + "%"
        msg_rank = "#" + str(crypto['cmc_rank'])
        await self.bot.say("```" + msg_price + " " + msg_percent + " " + msg_rank + "```")
        return


def setup(bot):
    bot.add_cog(Crypto(bot))


async def get_listings(self):
    listings_url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?start=1&limit=1000&convert=USD"
    current_time = time.time()
    if current_time >= self.last_time + (2 * 60):
        self.last_time = current_time
        req = urllib.request.Request(listings_url)
        req.add_header("X-CMC_PRO_API_KEY", self.api_key)
        req.add_header("Accept", "application/json")

        data = json.loads(urllib.request.urlopen(req).read().decode())
        self.listings = {x["id"]: x for x in data["data"]}
