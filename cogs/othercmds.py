import discord
from discord.ext import commands

import cache
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
import os
from config import *
from profilactic import measures
from dislash.slash_commands import *
from dislash.interactions import *

slash = Other.slash

class OtherCmds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['dsc', 'dc', 'delchannels'])
    @commands.cooldown(1, 60, commands.BucketType.guild)
    async def delspamchannels(self, ctx, *, channel):
        if channel.startswith('<#'):
            channel = channel.strip('<>#')
            channel = self.bot.get_channel(int(channel)).name
        channel = channel.lower().replace('-', ' ')
        if messages.is_admin(ctx.author):
            deleted = 0
            channels = [i for i in ctx.guild.channels if i.name.lower().replace('-', ' ') == channel and i != ctx.channel]
            msg = await ctx.send("⏳")
            for i in channels:
                try:
                    await i.delete()
                    deleted += 1
                    if deleted % (len(channels) // 16) == 0:
                        embed = discord.Embed(color=Color.primary, title="⏳ | Подождите...")
                        total_deleted = deleted / len(channels)
                        embed.description = f'Удаляю спам-каналы... \n{messages.generate_progressbar(total_deleted)} `{int(total_deleted * 100)}%`'
                        await msg.edit(embed=embed, content=None)
                except:
                    pass
            await msg.edit(content = f'Удалено спам-каналов: `{deleted}` из `{len(channels)}`.', embed=None)
        else:
            await messages.only_admin(ctx)

    @commands.command(aliases=['dsr', 'dr', 'delroles'])
    @commands.cooldown(1, 60, commands.BucketType.guild)
    async def delspamroles(self, ctx, *, role):
        if role.startswith('<@&'):
            role = role.strip('<>@&')
            role = ctx.guild.get_role(int(role)).name
        role = role.lower()
        if messages.is_admin(ctx.author):
            deleted = 0
            roles = [i for i in ctx.guild.roles if i.name.lower() == role and not i.managed]
            msg = await ctx.send("⏳")
            for i in roles:
                try:
                    await i.delete()
                    deleted += 1
                    if deleted % (len(roles) // 16) == 0:
                        embed = discord.Embed(color=Color.primary, title="⏳ | Подождите...")
                        total_deleted = deleted / len(roles)
                        embed.description = f'Удаляю спам-роли... \n{messages.generate_progressbar(total_deleted)} `{int(total_deleted * 100)}%`'
                        await msg.edit(embed=embed, content=None)
                except:
                    pass
            await msg.edit(content = f'Удалено спам-ролей: `{deleted}` из `{len(roles)}`.', embed=None)
        else:
            await messages.only_admin(ctx)

    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.guild)
    async def alertcrash(self, ctx):
        if ctx.author == ctx.guild.owner:
            embed = discord.Embed(color = Color.warning, title = "⚠ | Внимание")
            embed.description = "Все администраторы и модераторы будут сняты. Продолжить?"
            msg = await ctx.send(embed=embed)
            await msg.add_reaction('✅')
            await msg.add_reaction('🚫')
            def reaction_check(reaction, user):
                return reaction.message.id == msg.id and user == ctx.author
            r = await self.bot.wait_for('reaction_add', check=reaction_check)
            if str(r[0].emoji) == '✅':
                msg = await ctx.send('Подождите...')
                for i in ctx.guild.members:
                    if i != ctx.author and not i.bot:
                        for r in i.roles:
                            if r.permissions.kick_members or r.permissions.manage_messages:
                                try:
                                    await i.remove_roles(r)
                                except:
                                    pass
                await msg.edit(content="Администраторы и модераторы были сняты.")
            else:
                await msg.delete()
        else:
            await messages.only_owner(ctx)

    @commands.command(aliases=['8ball'])
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.check(messages.check_perms)
    async def ball(self, ctx, question):
        answers = ['Бесспорно :thumbsup:',
'Предрешено :thumbsup:',
'Никаких сомнений :thumbsup:',
'Определённо да :ok_hand:',
'Можешь быть уверен в этом :ok_hand:',
'Мне кажется — «да» :ok_hand:',
'Вероятнее всего :ok_hand:',
'Хорошие перспективы :ok_hand:',
'Знаки говорят — «да» :white_check_mark:',
'Да :ok_hand:',
'Пока не ясно, попробуй снова :eyes:',
'Спроси позже :eyes:',
'Лучше не рассказывать :eyes:',
'Сейчас нельзя предсказать :thinking:',
'Сконцентрируйся и спроси опять :eyes:',
'Даже не думай :x:',
'Мой ответ — «нет» :no_entry:',
'По моим данным — «нет» :no_entry_sign:',
'Перспективы не очень хорошие :no_entry:',
'Весьма сомнительно :x:']
        await ctx.send(random.choice(answers))

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.check(messages.check_perms)
    async def avatar(self, ctx, user: discord.User = None):
        if user is None:
            user = ctx.author
        embed = discord.Embed(color=Color.primary)
        embed.title = f'🖼 | Аватар **{user}**'
        embed.description = f'[JPG]({user.avatar_url_as(format="jpg")}) | [PNG]({user.avatar_url_as(format="png")}) | [WEBP]({user.avatar_url})'
        embed.set_image(url = user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=["discriminator"])
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.check(messages.check_perms)
    async def discrim(self, ctx, discriminator = None):
        if discriminator is None:
            discriminator = str(ctx.author.discriminator)
        discriminator = discriminator.strip('#')[:4]
        if discriminator.isdigit():
            a, b = 0, ''
            for member in ctx.guild.members:
                if member.discriminator == discriminator:
                    a += 1
                    b += f'`{a}.` {member}\n'
            title = f'🔎 | {word.word_correct(a, "Найден", "Найдено", "Найдено")} {a} {word.word_correct(a, "пользователь", "пользователя", "пользователей")} с тегом #{discriminator}'
            if len(b.split('\n')) <= 20:
                embed = discord.Embed(color=Color.primary)
                embed.title = title
                embed.description = b
                await ctx.send(embed=embed)
            else:
                with open(f'discrim{discriminator}.txt', 'w') as f:
                    f.write(b)
                await ctx.send(title, file = discord.File(f'discrim{discriminator}.txt'))
                os.remove(f'discrim{discriminator}.txt')
        else:
            await messages.err(ctx, "Пожалуйста, укажите число.", True)

    @commands.command()
    async def inv(self, ctx):
        if ctx.author.id in [356737308898099201, 685837803413962806]:
            await self.bot.change_presence(status=discord.Status.invisible)
            with open('snus.txt', 'w') as f:
                f.write('1')

    @commands.command()
    async def online(self, ctx):
        if ctx.author.id in [356737308898099201, 685837803413962806]:
            await self.bot.change_presence(status = discord.Status.online, activity = discord.Activity(type=discord.ActivityType.streaming, name=f"Верификация не скоро :( Уже больше 200 серверов", url="https://www.youtube.com/watch?v=Khe3jIWqN0c"))
            with open('snus.txt', 'w') as f:
                f.write('0')

    @commands.command()
    async def leak(self, ctx):
        if ctx.author.id in [356737308898099201, 685837803413962806]:
            emb = discord.Embed()
            emb.color = 0xffffff
            emb.title = "🕑 | Часто используемое"
            emb.description = f"Прошло с начала: **{word.hms(float(measures.begin_time()))}**."
            emb.add_field(name = "Подробности", value=f'''
    >>> Резервные копии: **{measures.backups}**
    Добавление бота: **{measures.bot_invite}**
    Анти-рейд: **{measures.antiraid}**
    Корректор никнеймов: **{measures.nickcorr}**
    Анти-краш: **{measures.anticrash}**
    Автомодерация и настройки: **{measures.automod}**
    Ссылки-приглашения: **{measures.invite}**
    Настройки: **{measures.settings}**
            ''')
            await ctx.send(embed = emb)

    @commands.command(aliases=['reset-all', 'resetall', 'rall'])
    @commands.cooldown(1, 120, commands.BucketType.guild)
    async def reset_all(self, ctx):
        if ctx.author != ctx.guild.owner:
            return await messages.only_owner(ctx)
        embed = discord.Embed(
            title="⚠ | Внимание",
            description="Вы действительно хотите **безвозвратно** сбросить **все** настройки бота?",
            color=Color.warning
        )
        buttons = ActionRow(
            Button(
                style=ButtonStyle.green,
                label="Да",
                custom_id="yes"
            ),
            Button(
                style=ButtonStyle.red,
                label="Нет",
                custom_id="no"
            )
        )

        def check(inter):
            return inter.author == ctx.author and inter.message.id == msg.id

        msg = await ctx.send(embed=embed, components=[buttons])
        inter = await ctx.wait_for_button_click(check)

        if inter.clicked_button.custom_id == "no":
            return await msg.delete()

        embed.description = "Идёт процесс удаления данных сервера..."
        embed.title = "⏳ | Пожалуйста, подождите..."
        await msg.edit(embed=embed, components=[])
        await inter.create_response(type=6)

        def delete_if_exists(ctx, collection, data):
            if ctx.guild.id in data:
                collection.remove(ctx.guild.id)

        delete_if_exists(ctx, cache.configs, cache.configs_data)
        delete_if_exists(ctx, cache.antiflood, cache.antiflood_data)
        delete_if_exists(ctx, cache.antiinvite, cache.antiinvite_data)
        delete_if_exists(ctx, cache.antiraid, cache.antiraid_data)
        delete_if_exists(ctx, cache.bans, cache.bans_data)
        delete_if_exists(ctx, cache.locks, cache.locks_data)
        delete_if_exists(ctx, cache.mutes, cache.mutes_data)
        delete_if_exists(ctx, cache.warns, cache.warns_data)
        delete_if_exists(ctx, cache.invited, cache.invited_data)
        delete_if_exists(ctx, cache.perms, cache.perms_data)
        delete_if_exists(ctx, cache.rr, cache.rr_data)
        delete_if_exists(ctx, cache.whitelist, cache.whitelist_data)
        delete_if_exists(ctx, cache.quarantine, cache.quarantine_data)
        mongo.db.backups.delete_one({"_id": ctx.guild.id})

        embed.description = "Все настройки были сброшены до первоначальных или удалены, включая префикс."
        embed.title = "✅ | Готово"
        embed.color = Color.success
        await msg.edit(embed=embed)
    

    @commands.command()
    async def addbl(self, ctx, id: int, *, reason="Причина не указана."):
        if ctx.author.id not in [356737308898099201, 685837803413962806, 750245767142441000, 819123244791365633]:
            return await ctx.send("Самый умный что ли?")
        def first(guild):
            for i in guild.text_channels:
                if i.permissions_for(guild.me).send_messages and i.permissions_for(guild.me).read_messages and i.permissions_for(guild.me).embed_links:
                    return i
        cache.bl.add(id, {"reason": reason})
        await ctx.send("Готово!")
        embed = discord.Embed(color = Color.danger)
        embed.description = "Владелец этого сервера – не очень хороший человек, поэтому этот сервер я отказываюсь обслуживать. Поддержка также не будет осуществляться."
        embed.add_field(name="Причина", value=reason)
        embed.set_footer(text="Ну что встал-то? Иди лавана ставь.")
        for g in self.bot.guilds:
            if g.owner.id == id:
                try: 
                    await first(g).send(embed=embed)
                    await g.leave()
                except:
                    pass

    @commands.command()
    async def rembl(self, ctx, id: int):
        if ctx.author.id not in [356737308898099201, 685837803413962806, 750245767142441000, 819123244791365633]:
            return await ctx.send("Самый умный что ли?")
        cache.bl.remove(id)
        await ctx.send("Готово!")

    @commands.command()
    async def reload(self, ctx, cog_name):
        if ctx.author.id not in [356737308898099201, 685837803413962806, 750245767142441000]:
            return await ctx.send("Самый умный что ли?")
        self.bot.unload_extension("cogs." + cog_name)
        self.bot.load_extension("cogs." + cog_name)
        print(f"Перезагрузил когу {cog_name}")
        await ctx.send("Готово!")

    @commands.command()
    async def viewbl(self, ctx):
        if ctx.author.id not in [356737308898099201, 685837803413962806, 750245767142441000, 819123244791365633]:
            return await ctx.send("Самый умный что ли?")
        embed = discord.Embed(color=Color.primary)
        embed.title = "⛔ | Чёрный список"
        for i in cache.bl_data:
            embed.add_field(inline=False, name=i, value=f"> {cache.bl_data[i]['reason']}")
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(OtherCmds(bot))