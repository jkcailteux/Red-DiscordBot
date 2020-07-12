from discord.ext import commands
import aiohttp
import re
import urllib
import json
import time


import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

class YouTube:
    """Le YouTube Cog"""

    def __init__(self, bot):
        self.bot = bot
        self.youtube_regex = (
            r'(https?://)?(www\.)?'
            '(youtube|youtu|youtube-nocookie)\.(com|be)/'
            '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')

        self.googleApiKey = ""
        self.bearer = ''
        self.option = {
             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36",
             "Accept": "application/json",
             "Authorization": self.bearer

        }
        self.session = aiohttp.ClientSession()

    @commands.command(pass_context=True, name='youtube2')
    async def _youtube2(self, ctx, *, query: str):
        uri = 'https://content.googleapis.com/youtube/v3/search?part=snippet&key=' + self.googleApiKey + '&q='
        encode = urllib.parse.quote_plus(query, encoding="utf-8", errors="replace")
        uir = uri + encode

        async with self.session.get(uir, headers=self.option) as resp:
            test = await resp.content.read()
            #items = json.loads(test.decode())['items']
            url = ''
            error = ''
            try:
                url = ''
                # TODO Parse items into Discord message content
            except IndexError:
                error = True
        return url, error

    @commands.command(pass_context=True, name='youtube')
    async def _youtube(self, context, *, query: str):
        """Search on Youtube"""
        try:
            url = 'https://www.youtube.com/results?'
            payload = {'search_query': ''.join(query)}
            headers = {'user-agent': 'Red-cog/1.0'}
            conn = aiohttp.TCPConnector()
            session = aiohttp.ClientSession(connector=conn)
            async with session.get(url, params=payload, headers=headers) as r:
                result = await r.text()
                time.sleep(.5)
            await session.close()
            yt_find = re.findall(r'href=\"\/watch\?v=(.{11})', result)
            url = 'https://www.youtube.com/watch?v={}'.format(yt_find[0])
            await self.bot.say(url)
        except Exception as e:
            message = 'Something went terribly wrong! [{}]'.format(e)
            await self.bot.say(message)


def setup(bot):
    bot.add_cog(YouTube(bot))
