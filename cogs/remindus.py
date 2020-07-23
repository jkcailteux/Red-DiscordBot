import asyncio
import logging
import os
import time

import discord
from discord.ext import commands

from .utils.dataIO import fileIO


class RemindUs:
    """Never forget anything anymore."""

    def __init__(self, bot):
        self.bot = bot
        self.reminders = fileIO("data/remindus/reminders.json", "load")
        self.units = {"minute": 60, "hour": 3600, "day": 86400, "week": 604800, "month": 2592000}

    @commands.command(pass_context=True)
    async def remindus(self, ctx, quantity: int, time_unit: str, *, text: str):
        """Sends you <text> when the time is up

        Accepts: minutes, hours, days, weeks, month
        Example:
        [p]remindus 3 days Have sushi with Asu and JennJenn"""
        time_unit = time_unit.lower()
        server = ctx.message.server
        if server is None:
            await self.bot.say("You can NOT make group reminders from a Private Channel")
            return
        author = ctx.message.channel
        s = ""
        if time_unit.endswith("s"):
            time_unit = time_unit[:-1]
            s = "s"
        if not time_unit in self.units:
            await self.bot.say("Invalid time unit. Choose minutes/hours/days/weeks/month")
            return
        if quantity < 1:
            await self.bot.say("Quantity must not be 0 or negative.")
            return
        if len(text) > 1960:
            await self.bot.say("Text is too long.")
            return
        seconds = self.units[time_unit] * quantity
        future = int(time.time() + seconds)
        self.reminders.append({"ID": author.id, "FUTURE": future, "TEXT": text})
        logger.info("{} ({}) set a reminder.".format(author.name, author.id))
        await self.bot.say("I will remind this channel that in {} {}.".format(str(quantity), time_unit + s))
        fileIO("data/remindus/reminders.json", "save", self.reminders)

    @commands.command(pass_context=True)
    async def forgetus(self, ctx):
        """Removes all your upcoming notifications"""
        server = ctx.message.server
        if server is None:
            await self.bot.say("You can NOT make group reminders from a Private Channel")
            return
        author = ctx.message.channel
        to_remove = []
        for reminder in self.reminders:
            if reminder["ID"] == author.id:
                to_remove.append(reminder)

        if not to_remove == []:
            for reminder in to_remove:
                self.reminders.remove(reminder)
            fileIO("data/remindus/reminders.json", "save", self.reminders)
            await self.bot.say("All your notifications have been removed.")
        else:
            await self.bot.say("You don't have any upcoming notification.")

    async def check_reminders(self):
        while self is self.bot.get_cog("RemindUs"):
            to_remove = []
            for reminder in self.reminders:
                if reminder["FUTURE"] <= int(time.time()):
                    try:
                        await self.bot.send_message(discord.Object(id=reminder["ID"]),
                                                    "You asked me to remind you this:\n{}".format(reminder["TEXT"]))
                    except (discord.errors.Forbidden, discord.errors.NotFound):
                        to_remove.append(reminder)
                    except discord.errors.HTTPException:
                        pass
                    else:
                        to_remove.append(reminder)
            for reminder in to_remove:
                self.reminders.remove(reminder)
            if to_remove:
                fileIO("data/remindus/reminders.json", "save", self.reminders)
            await asyncio.sleep(5)


def check_folders():
    if not os.path.exists("data/remindus"):
        print("Creating data/remindus folder...")
        os.makedirs("data/remindus")


def check_files():
    f = "data/remindus/reminders.json"
    if not fileIO(f, "check"):
        print("Creating empty reminders.json...")
        fileIO(f, "save", [])


def setup(bot):
    global logger
    check_folders()
    check_files()
    logger = logging.getLogger("remindus")
    if logger.level == 0:  # Prevents the logger from being loaded again in case of module reload
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(filename='data/remindus/reminders.log', encoding='utf-8', mode='a')
        handler.setFormatter(logging.Formatter('%(asctime)s %(message)s', datefmt="[%d/%m/%Y %H:%M]"))
        logger.addHandler(handler)
    n = RemindUs(bot)
    loop = asyncio.get_event_loop()
    loop.create_task(n.check_reminders())
    bot.add_cog(n)
