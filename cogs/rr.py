import discord
from discord.ext import commands
from dislash.interactions.message_components import ActionRow, Button, ButtonStyle
from config import Color, Other
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
from word import ago
from discord.utils import get
from profilactic import measures

slash = Other.slash

class RR(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        measures.add(what=5)
        if payload.message_id in cache.rr_data:
            data = cache.rr_data[payload.message_id]
            try:
                channel = self.bot.get_channel(data['channel'])
                message = await channel.fetch_message(payload.message_id)
                member = get(message.guild.members, id=payload.user_id)
                role = data['roles']
                if not member.bot:
                    for r in role[str(payload.emoji)]["add"]:
                        try:
                            await member.add_roles(channel.guild.get_role(r))
                        except:
                            pass
                    for r in role[str(payload.emoji)]["remove"]:
                        try:
                            await member.remove_roles(channel.guild.get_role(r))
                        except:
                            pass
            except:
                pass

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        measures.add(what=5)
        if payload.message_id in cache.rr_data:
            data = cache.rr_data[payload.message_id]
            try:
                channel = self.bot.get_channel(data['channel'])
                message = await channel.fetch_message(payload.message_id)
                member = get(message.guild.members, id=payload.user_id)
                role = data['roles']
                if not member.bot:
                    for r in role[str(payload.emoji)]["add"]:
                        try:
                            await member.remove_roles(channel.guild.get_role(r))
                        except:
                            pass
                    for r in role[str(payload.emoji)]["remove"]:
                        try:
                            await member.add_roles(channel.guild.get_role(r))
                        except:
                            pass
            except:
                pass

    @commands.command()
    @commands.check(messages.check_perms)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def addsingle(self, ctx):
        add = []
        remove = []

        embed = discord.Embed(title="🚩 | Роли за реакции", color=Color.primary, description="Пожалуйста, через пробел укажите роли, которые будут выдаваться при добавлении реакции.")
        embed.set_footer(text="Вы можете написать \"нет\", если их указывать не нужно.")
        msg = await ctx.send(embed=embed)

        def message_check(message):
            return message.channel == ctx.channel and ctx.author == message.author

        def reaction_check(reaction, user):
            return reaction.message.guild.id == ctx.guild.id and user == ctx.author

        m = await self.bot.wait_for('message', check=message_check)
        if m.content.lower() == "нет":
            pass
        else:
            for i in m.content.split():
                i = i.strip("<@&>")
                try:
                    i = ctx.guild.get_role(int(i))
                    if i:
                        if not i.managed:
                            if i != ctx.guild.default_role:
                                add.append(i.id)
                except:
                    pass
        await m.delete()
        embed.description = "Теперь укажите роли, которые будут сниматься при добавлении реакции."
        await msg.edit(embed=embed)
        o = await self.bot.wait_for('message', check=message_check)
        if o.content.lower() == "нет":
            pass
        else:
            for i in o.content.split():
                i = i.strip("<@&>")
                try:
                    i = ctx.guild.get_role(int(i))
                    if i:
                        if not i.managed:
                            if i != ctx.guild.default_role:
                                remove.append(i.id)
                                if i.id in add:
                                    add.pop(add.index(i.id))
                except:
                    pass
        if len(add) == 0 and len(remove) == 0:
            await msg.delete()
            return await messages.err(ctx, "Вы не указали никакие роли. Печально... :(")
        await o.delete()
        embed.description = "Теперь поставьте реакцию под сообщением, где будут выдаваться роли.\n**ИСПОЛЬЗУЙТЕ ТОЛЬКО СТАНДАРТНЫЕ ИЛИ ЭМОДЗИ С ЭТОГО СЕРВЕРА!**"
        embed.set_footer(text="Это последний шаг.")
        await msg.edit(embed=embed)
        r = await self.bot.wait_for('reaction_add', check=reaction_check)
        await r[0].message.add_reaction(str(r[0].emoji))
        try:
            old_emojis = cache.rr_data[r[0].message.id]["roles"]
        except:
            old_emojis = {}

        old_emojis[str(r[0].emoji)] = {"add": add, "remove": remove}
        cache.rr.add(r[0].message.id, {"channel": r[0].message.channel.id, "roles": old_emojis})
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        def get_roles(what: list):
            if not len(what): return "нет"
            else:
                return " ".join([ctx.guild.get_role(a).mention for a in what])
        embed.description = f"""
**Выдающиеся роли:** {get_roles(add)}
**Снимающиеся роли:** {get_roles(remove)}
**Эмодзи:** {r[0].emoji}
**Сообщение:** [Перейти]({r[0].message.jump_url})
        """
        await msg.edit(embed=embed)

    @commands.command()
    @commands.check(messages.check_perms)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def delsingle(self, ctx):
        embed = discord.Embed(title="🚩 | Роли за реакции", color=Color.primary, description="Пожалуйста, поставьте реакцию, которую нужно убрать.")
        msg = await ctx.send(embed=embed)
        def reaction_check(reaction, user):
            return reaction.message.guild.id == ctx.guild.id and user == ctx.author
        m = await self.bot.wait_for('reaction_add', check=reaction_check)
        if not m[0].message.id in cache.rr_data:
            await msg.delete()
            return await messages.err(ctx, "Роль за реакцию не была указана.")
        if not str(m[0].emoji) in cache.rr_data[m[0].message.id]["roles"]:
            await msg.delete()
            return await messages.err(ctx, "Роль за реакцию не была указана.")
        a = cache.rr_data[m[0].message.id]["roles"]
        del a[str(m[0].emoji)]
        cache.rr.add(m[0].message.id, {"roles": a})
        await m[0].message.remove_reaction(member=self.bot.user, emoji=m[0].emoji)
        await msg.delete()
        await ctx.message.add_reaction("✅")

def setup(bot):
    bot.add_cog(RR(bot))
