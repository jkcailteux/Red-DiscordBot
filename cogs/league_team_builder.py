import json
import aiohttp

from discord.ext import commands

CURRENT_PATCH = "10.14.1"
CHAMPIONS_URL = "http://ddragon.leagueoflegends.com/cdn/" + CURRENT_PATCH + "/data/en_US/champion.json"
PROFILE_URL = "https://beta.iesdev.com/api/lolapi/na1/accounts/name/{}?force=false"
PLAYSTYLE_URL = "https://beta.iesdev.com/graphql?query=query%20playerSeasonChampionStatsAll%28%24aggregate" \
                "%3AAggregate%21%2C%24accountId%3AString%21%2C%24region%3ARegion%21%2C%24group%3ABoolean%21%2C" \
                "%24queue%3AQueue%29%7BplayerChampionStats%28aggregate%3A%24aggregate%2CaccountId%3A%24accountId" \
                "%2Cregion%3A%24region%2Cgroup_by_queue%3A%24group%2Cqueue%3A%24queue%2Cgroup_by_role%3Afalse%29" \
                "%7BchampionId%20gameCount%20role%20basicStats%7Bassists%20deaths%20kills%20wins%7D%7D%7D&variables" \
                "=%7B%22region%22%3A%22NA1%22%2C%22accountId%22%3A%22{}" \
                "%22%2C%22aggregate%22%3A%22SUM%22%2C%22group%22%3Afalse%7D "


class LeagueTeamBuilder:
    """General commands."""

    def __init__(self, bot):
        self.bot = bot
        self.champions = {}
        self.summoners = {}
        self.play_styles = {}
        self.session = aiohttp.ClientSession()

    async def load_champions(self):
        if self.champions:
            return

        async with self.session.get(CHAMPIONS_URL) as resp:
            response = await resp.content.read()
            try:
                champions = json.loads(response.decode())["data"]
                for champion in champions:
                    champ_data = champions[champion]
                    self.champions[champ_data["key"]] = champ_data
                return
            except Exception as e:
                message = 'Something went terribly wrong! [{}]'.format(e)
                await self.bot.say(message)

    @commands.group(pass_context=True)
    async def load_league(self, ctx):
        if not self.champions:
            await self.load_champions()

    @commands.group(pass_context=True)
    async def load_summoner(self, ctx, name: str = ""):
        await self.load_league.invoke(ctx)

        async with self.session.get(PROFILE_URL.format(name)) as resp:
            response = await resp.content.read()
            try:
                data = json.loads(response.decode())["data"]
                self.summoners[name] = data
                await self.load_summoner_playstyle(data["accountId"], data["name"])
            except Exception as e:
                message = 'Something went terribly wrong! [{}]'.format(e)
                await self.bot.say(message)

    async def load_summoner_playstyle(self, account_id: str = "", summoner_name: str = ""):
        async with self.session.get(PLAYSTYLE_URL.format(account_id)) as resp:
            response = await resp.content.read()
            try:
                data = json.loads(response.decode())["data"]["playerChampionStats"]
                self.play_styles[account_id] = sorted(data, key=lambda x: x["gameCount"], reverse=True)

                message = "Top 5 champions for **{}** are...```".format(summoner_name)

                for x in range(0, min(5, len(data))):
                    play_data = self.play_styles[account_id][x]
                    champ = self.champions[play_data["championId"]]
                    total_games = play_data["gameCount"]
                    wins = play_data["basicStats"]["wins"]
                    loses = total_games - wins
                    win_rate = (wins / total_games) * 100

                    message += "\n{} {}-{} {}%".format(champ["name"], int(wins), int(loses), "{:.2f}".format(win_rate))

                message += "```"
                await self.bot.say(message)

            except Exception as e:
                message = 'Something went terribly wrong! [{}]'.format(e)
                await self.bot.say(message)


def setup(bot):
    cog = LeagueTeamBuilder(bot)
    bot.add_cog(cog)
