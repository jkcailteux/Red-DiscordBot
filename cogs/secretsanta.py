import logging

import random
import discord
from .utils import checks
from discord.ext import commands
from discord.ext.commands.context import Context


class SecretSanta:

    def __init__(self, bot):
        self.bot = bot
        self.groups = dict(dict())

    @commands.command(pass_context=True)
    async def secretsanta(self, ctx: Context, action: str):
        if action == "enroll":
            await enroll(self, ctx)
        elif action == "remove":
            await remove(self, ctx)
        elif action == "start":
            await start(self, ctx)
        elif action == "list":
            await list_members(self, ctx)


async def enroll(self, ctx: Context):
    server = ctx.message.server
    user = ctx.message.author
    group = self.groups.get(server.id, dict())
    group[user.id] = user
    self.groups[server.id] = group
    await self.bot.say("Added user: " + user.display_name + " to " + server.name + "'s secret Santa")


async def remove(self, ctx: Context):
    server = ctx.message.server
    user = ctx.message.author
    group = self.groups.get(server.id, dict())
    del group[user.id]
    self.groups[server.id] = group
    await self.bot.say("Removed user: " + user.display_name + " from " + server.name + "'s secret Santa")


async def list_members(self, ctx: Context):
    server = ctx.message.server
    group = self.groups.get(server.id, dict())
    msg = "The following users are enrolled in " + server.name + "'s secret santa:\n"
    for user in group.values():
        msg += user.display_name + "\n"

    await self.bot.say(msg)


@checks.serverowner_or_permissions(administrator=True)
async def start(self, ctx: Context):
    server = ctx.message.server
    group = self.groups.get(server.id, dict())
    randomized = list(group.values())
    random.shuffle(randomized)

    if randomized.__len__() == 0:
        await self.bot.say("There are no users in this secret santa")
        return

    for x in range(0, randomized.__len__()):
        user = randomized[x]
        if x == randomized.__len__() - 1:
            secret_santa = randomized[0]
        else:
            secret_santa = randomized[x + 1]

        await self.bot.send_message(discord.User(id=user.id),
                                    "Your secret Santa is: " + secret_santa.name + "#" + secret_santa.discriminator)


def setup(bot):
    global logger
    logger = logging.getLogger("secretsanta")
    if logger.level == 0:  # Prevents the logger from being loaded again in case of module reload
        logger.setLevel(logging.INFO)
    n = SecretSanta(bot)
    bot.add_cog(n)
