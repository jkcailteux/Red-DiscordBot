import json
import logging
import os
import urllib.request

import discord
from discord.ext import commands

from .utils import checks
from .utils.dataIO import fileIO


class Files:
    data_movieclub = "data/movieclub"
    rated_movie_list_json = data_movieclub + "/rated_movielist.json"
    movie_list_json = data_movieclub + "/movielist.json"


class Api:
    api_key = "&apikey=cfe10214"
    omdb_url = "https://www.omdbapi.com/?i="


class MovieClub:

    def __init__(self, bot):
        self.bot = bot
        self.movie_list = list(fileIO(Files.movie_list_json, "load"))
        self.rated_movie_list = set(fileIO(Files.rated_movie_list_json, "load")["_set_object"])
        self.omdb_key = "cfe10214"
        self.movie_cache = {}

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
                self.movie_list.insert(0, movie_id)

                await self.bot.say("Movie set to ....")
                await create_movie_embed(self, movie, movie_id)
                fileIO(Files.movie_list_json, "save", self.movie_list)
            else:
                msg = "Movie " + movie_id + " not found"
        else:
            msg = "Movie " + movie_id + " not found"

        if msg is not None:
            await self.bot.say(msg)

    @commands.command(pass_context=True)
    async def movieget(self, ctx):

        if self.movie_list.__len__() > 0:
            await self.bot.say("Current Movie is .....")
            movie = await get_movie(self, movie_id=self.movie_list[0])
            await create_movie_embed(self, movie, self.movie_list[0])
        else:
            await self.bot.say("There is no current movie")

    @commands.command(pass_context=True)
    async def movierate(self, ctx, movie_id: str, plot: int, acting: int, visuals: int, sound: int, rewatchable: str,
                        entertaing: str):

        movie = await get_movie(self, movie_id)

        # Validate Input
        error_msg = ""

        if movie is None:
            error_msg = "Invalid movie id: " + movie_id
        if plot < 0 or plot > 10:
            error_msg = "Plot needs to be between 0 and 10"
        if acting < 0 or acting > 10:
            error_msg = "Acting needs to be between 0 and 10"
        if visuals < 0 or visuals > 10:
            error_msg = "Visuals needs to be between 0 and 10"
        if sound < 0 or sound > 10:
            error_msg = "Sound needs to be between 0 and 10"

        rewatchable_score = parse_binary_text(rewatchable)
        if rewatchable_score is None:
            error_msg = "Rewatchable needs to yes/no, true/false, or 1/0"

        entertaing_score = parse_binary_text(entertaing)
        if entertaing_score is None:
            error_msg = "Entertaining needs to yes/no, true/false, or 1/0"

        if error_msg is not "":
            await self.bot.say(
                "Error submitting report by " + "<@" + ctx.message.author.id + ">")
            await self.bot.say("```" + error_msg + "```")
            return

        # We have a valid movie rating
        self.rated_movie_list.add(movie_id)
        fileIO(Files.rated_movie_list_json, "save", dict(_set_object=list(self.rated_movie_list)))

        msg = "Movie Rating for `" + movie["Title"] + "` by <@" + ctx.message.author.id + ">\n\n"
        msg += "```"
        msg += "Plot:        " + str(plot) + "\n"
        msg += "Acting:      " + str(acting) + "\n"
        msg += "Visuals:     " + str(visuals) + "\n"
        msg += "Sound:       " + str(sound) + "\n"
        msg += "\n"
        msg += "Rewatchable: " + str(rewatchable_score) + "\n"
        msg += "Entertaing:  " + str(entertaing_score) + "\n"
        msg += "```"

        await self.bot.whisper(msg)

    @commands.command(pass_context=True)
    async def moviehelp(self, ctx):
        msg_set = "~movieset <imdb id> to set the current movie the group is watching (MODs only)\n"
        msg_get = "~movieget to get the current movie the group is watching\n"
        msg_rate = "~movierate <imdb id> <plot> <acting> <visuals> <sound> <rewatchable> <entertaining> to rate a " \
                   "movie. plot/acting/visuals/sound are 0-10 and rewatchable/entertaining are true/false "
        await self.bot.say("```" + msg_set + msg_get + msg_rate + "```")


# plot*2 + visual + sound + acting + 5*rewatchable + 5*entertaining

async def create_movie_embed(self, movie, movie_id: str):
    embed = discord.Embed(colour=discord.Colour.red())
    embed.set_image(url=movie["Poster"])
    embed.set_author(name=movie["Title"] + " (" + movie_id + ")")
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
    if movie_id in self.movie_cache:
        return self.movie_cache[movie_id]

    omdb_url = Api.omdb_url + movie_id + Api.api_key
    with urllib.request.urlopen(omdb_url) as req:
        movie = json.loads(req.read().decode())
        self.movie_cache[movie_id] = movie
        return movie


def parse_binary_text(text: str):
    if text.lower() == "yes" or text.lower() == "true" or text.lower() == "1":
        return True
    if text.lower() == "no" or text.lower() == "false" or text.lower() == "0":
        return False
    else:
        return None


def check_folders():
    if not os.path.exists(Files.data_movieclub):
        print("Creating data/movieclub folder...")
        os.makedirs(Files.data_movieclub)


def check_files():
    if not fileIO(Files.movie_list_json, "check"):
        print("Creating empty movielist.json...")
        fileIO(Files.movie_list_json, "save", [])

    if not fileIO(Files.rated_movie_list_json, "check"):
        print("Creating empty rated_movielist.json...")
        fileIO(Files.rated_movie_list_json, "save", {})


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
