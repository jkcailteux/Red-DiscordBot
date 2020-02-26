from discord.ext import commands
from random import choice
import aiohttp
import re
import urllib
import json

class AdvancedGoogle:
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.googleApiKey = ""
        self.option = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36"
        }
        self.regex = [
            re.compile(r",\"ou\":\"([^`]*?)\""),
            re.compile(r"class=\"r\"><a href=\"([^`]*?)\""),
            re.compile(r"Please click <a href=\"([^`]*?)\">here<\/a>"),
            re.compile(r"<img class=\"rg_i Q4LuWd tx8vtf\" src=\"([^`]*?)\"")
        ]

    def __unload(self):
        self.session.close()

    @commands.command(pass_context=True)
    @commands.cooldown(5, 60, commands.BucketType.server)
    async def google(self, ctx, text):
        """Its google, you search with it.
        Example: google A magical pug
        Special search options are available; Image, Images, Maps
        Example: google image You know, for kids! > Returns first image
        Another example: google maps New York
        Another example: google images cats > Returns a random image
        based on the query
        LEGACY EDITION! SEE HERE!
        https://twentysix26.github.io/Red-Docs/red_cog_approved_repos/#refactored-cogs
        Originally made by Kowlin https://github.com/Kowlin/refactored-cogs
        edited by Aioxas"""
        result = await self.get_response(ctx)
        await self.bot.say(result)

    async def images_old(self, ctx, images: bool = False):
        uri = "https://www.google.com/search?hl=en&tbm=isch&tbs=isz:m&q="
        num = 7
        if images:
            num = 8
        if isinstance(ctx, str):
            quary = str(ctx[num - 1 :].lower())
        else:
            quary = str(
                ctx.message.content[len(ctx.prefix + ctx.command.name) + num :].lower()
            )
        encode = urllib.parse.quote_plus(quary, encoding="utf-8", errors="replace")
        uir = uri + encode
        url = None
        async with self.session.get(uir, headers=self.option) as resp:
            test = await resp.content.read()
            unicoded = test.decode("unicode_escape")
            query_find = self.regex[3].findall(unicoded)
            try:
                if images:
                    url = choice(query_find)
                elif not images:
                    url = query_find[0]
                error = False
            except IndexError:
                error = True
        return url, error

    async def images(self, ctx):
        uri = "https://www.googleapis.com/customsearch/v1?key=" + self.googleApiKey + "&cx=009084991455056480736:dcagltkol4u&prettyPrint=false&q="
        num = 7
        if isinstance(ctx, str):
            quary = str(ctx[num - 1 :].lower())
        else:
            quary = str(
                ctx.message.content[len(ctx.prefix + ctx.command.name) + num :].lower()
            )
        encode = urllib.parse.quote_plus(quary, encoding="utf-8", errors="replace")
        uir = uri + encode
        url = None
        async with self.session.get(uir, headers=self.option) as resp:
            test = await resp.content.read()
            items = json.loads(test.decode())['items']
            try:
                item = choice(items)
                url = item['pagemap']['cse_image'][0]['src']
                error = False
            except IndexError:
                error = True
        return url, error

    def parsed(self, find):
        if len(find) > 5:
            find = find[:5]
        for i, _ in enumerate(find):
            if i == 0:
                find[i] = "<{}>\n\n**You might also want to check these out:**".format(
                    self.unescape(find[i])
                )
            else:
                find[i] = "<{}>".format(self.unescape(find[i]))
        return find

    def unescape(self, msg):
        msg = urllib.parse.unquote_plus(msg, encoding="utf-8", errors="replace")
        return msg

    async def get_response(self, ctx):
        if isinstance(ctx, str):
            search_type = ctx.lower().split(" ")
            search_valid = str(ctx.lower())
        else:
            search_type = (
                ctx.message.content[len(ctx.prefix + ctx.command.name) + 1 :]
                .lower()
                .split(" ")
            )
            search_valid = str(
                ctx.message.content[len(ctx.prefix + ctx.command.name) + 1 :].lower()
            )

        # Start of Image
        if search_type[0] == "image" or search_type[0] == "images":
            msg = "Your search yielded no results."
            if search_valid == "image" or search_valid == "images":
                msg = "Please actually search something"
                return msg
            else:
                if search_type[0] == "image":
                    url, error = await self.images(ctx)
                elif search_type[0] == "images":
                    url, error = await self.images(ctx)
                if url and not error:
                    return url
                elif error:
                    return msg
                    # End of Image
        # Start of Maps
        elif search_type[0] == "maps":
            if search_valid == "maps":
                msg = "Please actually search something"
                return msg
            else:
                uri = "https://www.google.com/maps/search/"
                if isinstance(ctx, str):
                    quary = str(ctx[5:].lower())
                else:
                    quary = str(
                        ctx.message.content[
                            len(ctx.prefix + ctx.command.name) + 6 :
                        ].lower()
                    )
                encode = urllib.parse.quote_plus(
                    quary, encoding="utf-8", errors="replace"
                )
                uir = uri + encode
                return uir
                # End of Maps
        # Start of generic search
        else:
            url = "https://www.google.com"
            uri = url + "/search?hl=en&q="
            if isinstance(ctx, str):
                quary = str(ctx)
            else:
                quary = str(
                    ctx.message.content[len(ctx.prefix + ctx.command.name) + 1 :]
                )
            encode = urllib.parse.quote_plus(quary, encoding="utf-8", errors="replace")
            uir = uri + encode
            query_find = await self.result_returner(uir)
            if isinstance(query_find, str):
                query_find = await self.result_returner(
                    url + query_find.replace("&amp;", "&")
                )
            query_find = "\n".join(query_find)
            return query_find
            # End of generic search

    async def result_returner(self, uir):
        async with self.session.get(uir, headers=self.option) as resp:
            test = await resp.text()
            query_find = self.regex[2].findall(test)
            result_find = self.regex[1].findall(test)
            if len(query_find) == 1 and len(result_find) == 0:
                return query_find[0]
            try:
                result_find = self.parsed(result_find)
            except IndexError:
                return IndexError
        return result_find

    async def on_message(self, message):
        author = message.author
        if author == self.bot.user:
            return
        if not self.bot.user_allowed(message):
            return
        channel = message.channel
        str2find = "ok google "
        text = message.content
        if not text.lower().startswith(str2find):
            return
        prefix = self.bot.settings.prefixes if len(self.bot.settings.get_server_prefixes(message.server)) == 0 else self.bot.settings.get_server_prefixes(message.server)
        message.content = message.content.replace(
            str2find,
            prefix[0] + "google ",
            1,
        )
        await self.bot.send_typing(channel)
        await self.bot.process_commands(message)

def setup(bot):
    n = AdvancedGoogle(bot)
    bot.add_cog(n)