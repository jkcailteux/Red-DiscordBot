from discord.ext import commands
from .utils import checks
import discord
import json
import hashlib
import hmac
import requests

class CryptoTrade:
    """General commands."""
    def __init__(self, bot):
        self.bot = bot
        self.API_URL = 'https://api.changelly.com'
        self.API_KEY = '191af27a253b43c991a621797b01d55e'
        self.API_SECRET = '98ebb23488bbb42f048edecff39b19257788757727eb07795b566c3a5c57e447'

    async def getCurrencies(self):
        message = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'getCurrencies',
            'params': []
        }

        serialized_data = json.dumps(message)

        sign = hmac.new(self.API_SECRET.encode('utf-8'), serialized_data.encode('utf-8'), hashlib.sha512).hexdigest()
        headers = {'api-key': self.API_KEY, 'sign': sign, 'Content-type': 'application/json'}
        response = requests.post(self.API_URL, headers=headers, data=serialized_data)
        
        await self.bot.say("Supported Coins:")
        await self.bot.say(response.json()['result'])

    @commands.group(pass_context=True)
    @checks.mod_or_permissions(administrator=False)
    async def trade(self, ctx, *, term: str=None):
        """Crypto Trade"""

        await self.getCurrencies()

def setup(bot):
    bot.add_cog(CryptoTrade(bot))