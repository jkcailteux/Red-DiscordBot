import discord
from discord.ext import commands
from .utils.dataIO import fileIO
from .utils import checks
import os
import logging
import urllib.request
import json


class MovieClub:

    def __init__(self, bot):
        self.bot = bot
        self.movie_list = fileIO("data/movieclub/movielist.json", "load")
        self.omdb_key = "cfe10214"

    @commands.command(pass_context=True)
    @checks.serverowner_or_permissions(administrator=True)
    async def movieset(self, ctx, movie_id: str):
        movie = await get_movie(self, movie_id)

        msg = None
        if movie is not None:
            if 'Year' in movie and 'Plot' in movie:
                # We have a valid movie, save it
                # Movie is inserted into first position
                # Todo support movie history
                self.movie_list.insert(0, movie)

                await self.bot.say("Movie set to ....")
                await create_movie_embed(self, movie)
                fileIO("data/movieclub/movielist.json", "save", self.movie_list)
            else:
                msg = "Movie " + movie_id + " not found"
        else:
            msg = "Movie " + movie_id + " not found"

        if msg is not None:
            await self.bot.say(msg)

    @commands.command(pass_context=True)
    async def movieget(self, ctx):

        if self.movie_list.__sizeof__() > 0:
            await self.bot.say("Current Movie is .....")
            await create_movie_embed(self, self.movie_list[0])
        else:
            await self.bot.say("There is no current movie")

    @commands.command(pass_context=True)
    async def movierate(self, ctx, movie_id: str, plot: int, acting: int, visuals: int, sound: int, rewatchable: str,
                        entertaing: str):

        movie = await get_movie(self, movie_id)

        msg = "Movie Rating for `" + movie["Title"] + "` by `" + ctx.message.author.name + "`\n\n"
        msg += "```"
        msg += "Plot:        " + str(plot) + "\n"
        msg += "Acting:      " + str(acting) + "\n"
        msg += "Visuals:     " + str(visuals) + "\n"
        msg += "Sound:       " + str(sound) + "\n"
        msg += "\n"
        msg += "Rewatchable: " + str(rewatchable) + "\n"
        msg += "Entertaing:  " + str(entertaing) + "\n"
        msg += "```"

        await self.bot.say(msg)


# plot*2 + visual + sound + acting + 5*rewatchable + 5*entertaining

async def create_movie_embed(self, movie):
    embed = discord.Embed(colour=discord.Colour.red())
    embed.set_image(url=movie["Poster"])
    embed.set_author(name=movie["Title"])
    embed.add_field(name="Year", value=movie["Year"])
    embed.add_field(name="Rated", value=movie["Rated"])
    embed.add_field(name="Runtime", value=movie["Runtime"])
    embed.add_field(name="Director", value=movie["Director"])
    embed.add_field(name="IMDB Rating", value=movie["imdbRating"])
    embed.add_field(name="Genre", value=movie["Genre"])
    embed.set_footer(text=movie["Plot"] + "\n\n" + "https://www.imdb.com/title/" + movie["imdbID"])

    try:
        await self.bot.say(embed=embed)
    except discord.HTTPException:
        await self.bot.say("I need the `Embed links` permission to send this")


async def get_movie(self, movie_id: str):
    omdb_url = "https://www.omdbapi.com/?i=" + movie_id + "&apikey=" + self.omdb_key
    with urllib.request.urlopen(omdb_url) as req:
        return json.loads(req.read().decode())


def check_folders():
    if not os.path.exists("data/movieclub"):
        print("Creating data/movieclub folder...")
        os.makedirs("data/movieclub")


def check_files():
    f = "data/movieclub/movielist.json"
    if not fileIO(f, "check"):
        print("Creating empty movielist.json...")
        fileIO(f, "save", [])


def setup(bot):
    global logger
    check_folders()
    check_files()
    logger = logging.getLogger("movieclub")
    if logger.level == 0:  # Prevents the logger from being loaded again in case of module reload
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(filename='data/movieclub/movielist.log', encoding='utf-8', mode='a')
        handler.setFormatter(logging.Formatter('%(asctime)s %(message)s', datefmt="[%d/%m/%Y %H:%M]"))
        logger.addHandler(handler)
    n = MovieClub(bot)
    bot.add_cog(n)
