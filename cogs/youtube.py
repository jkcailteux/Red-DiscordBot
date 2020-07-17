import json
import urllib
import aiohttp
from discord.ext import commands

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]


class YouTube:
    """Le YouTube Cog"""

    def __init__(self, bot):
        self.bot = bot
        self.googleApiKey = ''
        self.session = aiohttp.ClientSession()

    @commands.command(pass_context=True, name='youtube')
    async def _youtube(self, ctx, *, query: str):
        uri = 'https://content.googleapis.com/youtube/v3/search?part=snippet&key=' + self.googleApiKey + '&q='
        encode = urllib.parse.quote_plus(query, encoding="utf-8", errors="replace")
        uir = uri + encode

        async with self.session.get(uir) as resp:
            response = await resp.content.read()
            try:
                items = json.loads(response.decode())['items']
                url = 'https://www.youtube.com/watch?v={}'.format(items[0]['id']['videoId'])
                await self.bot.say(url)
            except Exception as e:
                message = 'Something went terribly wrong! [{}]'.format(e)
                await self.bot.say(message)


def setup(bot):
    bot.add_cog(YouTube(bot))
