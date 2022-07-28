import re
import discord
from discord.ext import commands
from config import Color
import messages
import word
import punishments
import asyncio
import mongo
import time
import datetime
import typing
import random
import cache
from profilactic import measures
from word import ago

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    '''@commands.group(aliases=['log', 'logchannel', 'log-channel', 'lc'])
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.check(messages.check_perms)
    async def log_channel(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(color=Color.primary)
            embed.title = "📝 | Канал логов"
            embed.add_field(name="Команды", inline=False, value=f"""
`{ctx.prefix}log-channel set` – указать канал для логов
`{ctx.prefix}log-channel remove` – удалить канал для логов
            """)
            try:
                channel = self.bot.get_channel(cache.logs_data[ctx.guild.id]["default-channel"]).mention
            except AttributeError:
                channel = None
            except KeyError:
                channel = None

            if channel:
                embed.add_field(name="Текущий канал логов", value=channel)

            await ctx.send(embed=embed)

    @log_channel.command(aliases=['set'])
    async def __set(self, ctx, channel1: discord.TextChannel):
        try:
            channel = cache.logs_data[ctx.guild.id]["default-channel"]
        except KeyError:
            channel = None

        if channel:
            if channel1.id == channel:
                return await messages.err(ctx, "Новый канал для логов не может совпадать со старым.")

        webhook = await channel1.create_webhook(name="Crash Protect Logs")
        await webhook.send("Этот канал указан в качестве канала для логов. Пожалуйста, не удаляйте этот вебхук. Спасибо!")
        cache.logs.add(ctx.guild.id, {"default-channel": channel1.id, "default-webhook": webhook.id})
        embed = discord.Embed(
            title="✅ | Готово", 
            description=f"Канал {channel1.mention} указан как канал для логов.", 
            color=Color.success
        )
        await ctx.send(embed=embed)

    @log_channel.command(aliases=['delete', 'remove'])
    async def __remove(self, ctx):
        try:
            channel = self.bot.get_channel(cache.logs_data[ctx.guild.id]["default-channel"])
        except KeyError:
            channel = None

        if not channel:
            return await messages.err(ctx, "Канал логов не был указан ранее!")

        embed = discord.Embed(
            title="✅ | Готово", 
            description=f"Канал {channel.mention} указан как канал для логов.", 
            color=Color.success
        )
        await ctx.send(embed=embed)'''

def setup(bot):
    bot.add_cog(Logs(bot))