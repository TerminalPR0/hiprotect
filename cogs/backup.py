import discord
from discord.ext import commands
from config import Color, Other
import messages
import word
import punishments
import asyncio
import mongo
import time
import datetime
import pytz
import random
from profilactic import measures
import json
import os
from word import ago
from discord.utils import get
from dislash.slash_commands import *
from dislash.interactions import *

def checkbackup(guild):
    return mongo.db.backups.count_documents({"_id": guild.id}) != 0
    
slash = Other.slash

def get_pin_buttons():
    buttons = []
    buttons.append(
        ActionRow(
            Button(
                style = ButtonStyle.grey,
                label = "1",
                custom_id = "one"
            ),
            Button(
                style = ButtonStyle.grey,
                label = "2",
                custom_id = "two"
            ),
            Button(
                style = ButtonStyle.grey,
                label = "3",
                custom_id = "three"
            )
        )
    )
    buttons.append(
        ActionRow(
            Button(
                style = ButtonStyle.grey,
                label = "4",
                custom_id = "four"
            ),
            Button(
                style = ButtonStyle.grey,
                label = "5",
                custom_id = "five"
            ),
            Button(
                style = ButtonStyle.grey,
                label = "6",
                custom_id = "six"
            )
        )
    )
    buttons.append(
        ActionRow(
            Button(
                style = ButtonStyle.grey,
                label = "7",
                custom_id = "seven"
            ),
            Button(
                style = ButtonStyle.grey,
                label = "8",
                custom_id = "eight"
            ),
            Button(
                style = ButtonStyle.grey,
                label = "9",
                custom_id = "nine"
            )
        )
    )
    buttons.append(
        ActionRow(
            Button(
                style = ButtonStyle.red,
                label="❌",
                custom_id = "cancel"
            ),
            Button(
                style = ButtonStyle.grey,
                label = "0",
                custom_id = "zero"
            ),
            Button(
                style = ButtonStyle.green,
                custom_id = "okay",
                label="✅"
            )
        )
    )
    return buttons

async def request_code(ctx, title = "⌨ | Пожалуйста, введите код", code = None, reifnone = True):
    entered = ""
    canceled = False
    if reifnone:
        if code is None:
            return True, False, ''
        elif len(code) == 0:
            return True, False, ''
    else:
        code = "0" * 10
    emb = discord.Embed(title = title, description = "```\n```", color = Color.primary)
    emb.add_field(name = "Забыли код?", value = "Обратитесь в [поддержку](https://discord.gg/U4ge8Fup5u)")
    msg = await ctx.send(embed = emb, components = get_pin_buttons())
    def check(inter):
        return inter.message.id == msg.id and ctx.author == inter.author
    while len(entered) != len(code):
        inter = await ctx.wait_for_button_click(check)
        if inter.clicked_button.label.isdigit():
            entered += inter.clicked_button.label
            emb.description = f"```\n{'•' * len(entered)}\n```"
            await msg.edit(embed = emb, components = get_pin_buttons())
            await inter.create_response(type=6)
        else:
            if inter.clicked_button.custom_id == "cancel":
                canceled = True
                await inter.create_response(type=6)
            break
    await msg.delete()
    return entered == code, canceled, entered
        

class Backup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.check(messages.check_perms)
    async def backup(self, ctx):
        measures.add(what=1)
        if ctx.invoked_subcommand is None:
            p = ctx.prefix
            embed = discord.Embed(color=Color.primary)
            embed.title = "💾 | Резервные копии"
            embed.description = f'''
`{p}backup create` – Создать/перезаписать резервную копию
`{p}backup delete` – Удалить резервную копию
`{p}backup load` – Загрузить резервную копию
`{p}backup protect` – Установить пароль для сохранения и загрузки сервера
            '''
            if checkbackup(ctx.guild):
                data = mongo.db.backups.find_one({"_id": ctx.guild.id}, projection={"info": True})
                embed.add_field(name='Последнее обновление резервной копии', value=f"<t:{data['info']['created']}:f> (<t:{data['info']['created']}:R>)")
            await ctx.send(embed=embed)

    @backup.command()
    async def delete(self, ctx):
        if checkbackup(ctx.guild):
            try:
                code = mongo.db.backups.find_one({"_id": ctx.guild.id}, {"code": True})['code']
            except:
                code = None
            a = await request_code(ctx, code=code)
            if not a[1]:
                if a[0]:
                    embed = discord.Embed(color = Color.warning)
                    embed.title = "⚠ | Внимание"
                    embed.description = "Вы хотите удалить резервную копию сервера?"
                    embed.set_footer(text = ctx.author, icon_url = ctx.author.avatar_url)

                    msg = await ctx.send(embed=embed, components = [ActionRow(
                    Button(style = ButtonStyle.green, label = "Да", custom_id = "delyes"),
                    Button(style = ButtonStyle.red, label = "Нет", custom_id = "delno"))
                    ])
                    next = True
                    def check(inter):
                        return inter.message.id == msg.id and inter.author == ctx.author
                    while next:
                        inter = await ctx.wait_for_button_click(check)
                        if inter.author == ctx.author:
                            next = False
                        if inter.clicked_button.label == "Да":
                            mongo.db.backups.delete_one({"_id": ctx.guild.id})
                            embed.color = Color.success
                            embed.title = "✅ | Готово"
                            embed.description = "Резервная копия сервера была удалена."
                            await msg.edit(embed=embed, components=[])
                            await inter.create_response(type=6)
                        elif inter.clicked_button.label == "Нет":
                            embed.color = Color.danger
                            embed.title = "🚫 | Отказ"
                            embed.description = "Резервная копия сервера не была удалена."
                            await msg.edit(embed=embed, components=[])
                            await inter.create_response(type=6)
                else:
                    await messages.err(ctx, "Неверный код.", True)
            else:
                embed = discord.Embed()
                embed.set_footer(text = ctx.author, icon_url = ctx.author.avatar_url)
                embed.color = Color.danger
                embed.title = "🚫 | Отказ"
                embed.description = "Резервная копия сервера не была удалена."
                await ctx.send(embed=embed)
        else:
            await messages.err(ctx, "Резервная копия не была создана.", True)

    @backup.command(aliases = ['file'])
    @commands.cooldown(1, 50, commands.BucketType.guild)
    async def _file(self, ctx):
        if checkbackup(ctx.guild):
            backup = {
                "guild": {},
                "text_channels": {},
                "voice_channels": {},
                "categories": {},
                "roles": {}
            }
            data = mongo.db.backups.find_one({"_id": ctx.guild.id})
            backup['guild']['name'] = data['guild']['name']
            backup['text_channels'] = data['text']
            backup['voice_channels'] = data['voice']
            backup['categories'] = data['category']
            backup['roles'] = data['roles']
            with open(str(ctx.guild.id) + ".json", "w") as f:
                json.dump(backup, f, indent=4)
            await ctx.send(file = discord.File(str(ctx.guild.id) + ".json"))
            os.remove(str(ctx.guild.id) + ".json")
        else:
            await messages.err(ctx, "Резервная копия не была создана.", True)

    @backup.command()
    @commands.cooldown(1, 30, commands.BucketType.guild)
    async def create(self, ctx):
        try:
            code = mongo.db.backups.find_one({"_id": ctx.guild.id}, {"code": True})['code']
        except:
            code = None
        a = await request_code(ctx, code=code)
        if not a[1]:
            if a[0]:
                embed = discord.Embed(color = Color.warning)
                embed.title = "⚠ | Внимание"
                embed.description = "Вы хотите создать резервную копию сервера? Если она уже была создана, произойдёт её перезапись."
                embed.set_footer(text = ctx.author, icon_url = ctx.author.avatar_url)
                msg = await ctx.send(embed=embed, components = [ActionRow(
                    Button(style = ButtonStyle.green, label = "Да", custom_id = "createyes"),
                    Button(style = ButtonStyle.red, label = "Нет", custom_id = "createno"))
                    ])
                next = True
                def check(inter):
                    return inter.message.id == msg.id and inter.author == ctx.author
                while next:
                    inter = await ctx.wait_for_button_click(check)
                    if inter.author == ctx.author:
                            next = False
                    if inter.clicked_button.label == "Да":
                            await inter.create_response(type=6)
                            try:
                                embed.title = "⏳ | Подождите"
                                embed.description = "Идёт создание резервной копии."
                                await msg.edit(embed=embed, components = [])
                                b = {}
                                b['info'] = {}
                                b['info']['nextsave'] = 2147483647
                                b['info']['interval'] = 0
                                b['info']['created'] = int(time.time())
                                b['guild'] = {}
                                b['text'] = {}
                                b['voice'] = {}
                                b['category'] = {}
                                b['roles'] = {}
                                b['guild']['name'] = ctx.guild.name
                                c = 0
                                for i in ctx.guild.text_channels:
                                    compact = {}
                                    for role, ovw in i.overwrites.items():
                                        allow, deny = ovw.pair()
                                        compact[role.name] = {'a':allow.value, 'd':deny.value}
                                    try:
                                        topic = i.topic.replace(".", "")
                                    except:
                                        topic = None
                                    if i.category is not None:
                                        b['text'][str(c)] = {
                                            "name":i.name,
                                            "topic":topic,
                                            "slowmode":i.slowmode_delay,
                                            "nsfw":i.nsfw,
                                            "position":i.position,
                                            "perms":compact,
                                            "category":i.category.name
                                        }
                                    else:
                                        b['text'][str(c)] = {
                                            "name":i.name,
                                            "topic":topic,
                                            "slowmode":i.slowmode_delay,
                                            "nsfw":i.nsfw,
                                            "position":i.position,
                                            "perms":compact,
                                            "category":None
                                        }
                                    c += 1
                                c = 0
                                for i in ctx.guild.voice_channels:
                                    compact = {}
                                    for role, ovw in i.overwrites.items():
                                        allow, deny = ovw.pair()
                                        compact[role.name] = {'a':allow.value, 'd':deny.value}

                                    if i.category is not None:
                                        b['voice'][str(c)] = {
                                            "name":i.name.replace('.', ' '),
                                            "limit":i.user_limit,
                                            "bitrate":i.bitrate,
                                            "position":i.position,
                                            "perms":compact,
                                            "category":i.category.name
                                        }
                                    else:
                                        b['voice'][str(c)] = {
                                            "name":i.name.replace('.', ' '),
                                            "limit":i.user_limit,
                                            "bitrate":i.bitrate,
                                            "position":i.position,
                                            "perms":compact,
                                            "category":None
                                        }
                                    c += 1
                                for i in ctx.guild.categories:
                                    compact = {}
                                    for role, ovw in i.overwrites.items():
                                        allow, deny = ovw.pair()
                                        compact[role.name] = {'a':allow.value, 'd':deny.value}
                                    b['category'][str(c)] = {
                                            "name":i.name.replace(".", ""),
                                            "position":i.position,
                                            "perms":compact
                                        }
                                    c += 1
                                c = 0
                                for i in ctx.guild.roles:
                                    if i != ctx.guild.default_role and not i.managed:
                                        b['roles'][str(c)] = {
                                                "name":i.name.replace(".", ""),
                                                "perms":i.permissions.value,
                                                "color":i.colour.value,
                                                "hoist":i.hoist,
                                                "mentionable":i.mentionable
                                            }
                                        c += 1
                                if checkbackup(ctx.guild):
                                    mongo.db.backups.update_one({"_id": ctx.guild.id}, {"$set":{
                                        "info": b['info'],
                                        "guild": b['guild'],
                                        "text": b['text'],
                                        "voice": b['voice'],
                                        "category": b['category'],
                                        "roles": b['roles']
                                    }})
                                else:
                                    mongo.db.backups.insert_one({"_id": ctx.guild.id,
                                        "info": b['info'],
                                        "guild": b['guild'],
                                        "text": b['text'],
                                        "voice": b['voice'],
                                        "category": b['category'],
                                        "roles": b['roles']
                                    })
                                embed.color = Color.success
                                embed.title = "✅ | Готово"
                                embed.description = "Сервер успешно сохранён."
                                await msg.edit(embed=embed)
                                await msg.edit(embed=embed, components = [])
                            except Exception as e:
                                embed.color = Color.danger
                                embed.title = "🚫 | ОшибОчка"
                                embed.description = "Произошла при создании резервной копии. Названия ролей, каналов и категорий не должны начинаться с `$`!"
                                await msg.edit(embed=embed, components = [])
                                raise e
                    else:
                            embed.color = Color.danger
                            embed.title = "🚫 | Отказ"
                            embed.description = "Резервная копия сервера не была создана."
                            await msg.edit(embed=embed, components = [])
                            await inter.create_response(type=6)
            else:
                await messages.err(ctx, "Неверный код.", True)
        else:
            embed = discord.Embed()
            embed.set_footer(text = ctx.author, icon_url = ctx.author.avatar_url)
            embed.color = Color.danger
            embed.title = "🚫 | Отказ"
            embed.description = "Резервная копия сервера не была создана."
            await ctx.send(embed=embed)

    @backup.command()
    @commands.cooldown(1, 120, commands.BucketType.guild)
    async def load(self, ctx):
        if checkbackup(ctx.guild):
            try:
                code = mongo.db.backups.find_one({"_id": ctx.guild.id}, {"code": True})['code']
            except:
                code = None
            a = await request_code(ctx, code=code)
            if not a[1]:
                if a[0]:
                    embed = discord.Embed(color = Color.primary)
                    embed.title = "💾 | Загрузка резервной копии"
                    embed.description = "Для загрузки резервной копии выберите один из вариантов:\n> 1️⃣ – полное восстановление (доступно только владельцу сервера; удаляются все каналы и роли)\n> 2️⃣ – частичное восстановление (создаются только несуществующие каналы и роли)"
                    embed.set_footer(text = ctx.author, icon_url = ctx.author.avatar_url)
                    fullb = Button(style = ButtonStyle.red, label = "Полное восстановление", custom_id = "full")
                    partb = Button(style = ButtonStyle.red, label = "Частичное восстановление", custom_id = "partially")
                    if ctx.author != ctx.guild.owner:
                        fullb.disabled = True
                    msg = await ctx.send(embed=embed, components = [
                        ActionRow(fullb, partb)
                    ])
                    next = True
                    def check(inter):
                        return inter.message.id == msg.id and inter.author == ctx.author
                    while next:
                        inter = await ctx.wait_for_button_click(check)
                        if inter.author == ctx.author:
                            next = False
                        if inter.clicked_button.label == "Полное восстановление":
                            await inter.create_response(type=6)
                            if ctx.author == ctx.guild.owner:
                                data = mongo.db.backups.find_one({"_id": ctx.guild.id})
                                embed.description = "Этап 1 из 6\n> Восстановление названия сервера"
                                await msg.edit(embed = embed)
                                await ctx.guild.edit(name = data['guild']['name'])
                                embed.description = "Этап 2 из 6\n> Удаление ролей"
                                await msg.edit(embed = embed)
                                for i in ctx.guild.roles:
                                    try:
                                        await i.delete()
                                    except:
                                        pass
                                embed.description = "Этап 3 из 6\n> Удаление каналов"
                                await msg.edit(embed = embed)
                                for i in ctx.guild.channels:
                                    try:
                                        if i != ctx.channel:
                                            await i.delete()
                                    except:
                                        pass
                                embed.description = "Этап 4 из 6\n> Создание ролей"
                                await msg.edit(embed = embed)
                                for k in range(250):
                                    j = 249 - k
                                    try:
                                        await ctx.guild.create_role(
                                            name=data['roles'][str(j)]['name'],
                                            colour=discord.Colour(value=data['roles'][str(j)]['color']),
                                            permissions=discord.Permissions(permissions=data['roles'][str(j)]['perms']),
                                            hoist=data['roles'][str(j)]['hoist'],
                                            mentionable=data['roles'][str(j)]['mentionable']
                                            )
                                    except:
                                        pass
                                embed.description = "Этап 5 из 6\n> Создание категорий"
                                await msg.edit(embed = embed)
                                for i in range(500):
                                    try:
                                        ovws = {}
                                        raw_ovw = data['category'][str(i)]['perms']
                                        for role in ctx.guild.roles:
                                            try:
                                                ovw = discord.PermissionOverwrite.from_pair(discord.Permissions(permissions=raw_ovw[role.name]['a']), discord.Permissions(permissions=raw_ovw[role.name]['d']))
                                                ovws[role] = ovw
                                            except:
                                                pass
                                        await ctx.guild.create_category(
                                            name=data['category'][str(i)]['name'],
                                            position=data['category'][str(i)]['position'],
                                            overwrites=ovws
                                            )
                                    except:
                                        pass
                                embed.description = "Этап 6 из 6\n> Создание каналов"
                                await msg.edit(embed = embed)
                                for i in range(500):
                                    try:
                                        ovws = {}
                                        raw_ovw = data['text'][str(i)]['perms']
                                        for role in ctx.guild.roles:
                                            try:
                                                ovw = discord.PermissionOverwrite.from_pair(discord.Permissions(permissions=raw_ovw[role.name]['a']), discord.Permissions(permissions=raw_ovw[role.name]['d']))
                                                ovws[role] = ovw
                                            except:
                                                pass
                                        if data['text'][str(i)]['category'] == None:
                                            await ctx.guild.create_text_channel(
                                                name=data['text'][str(i)]['name'],
                                                topic=data['text'][str(i)]['topic'],
                                                nsfw=data['text'][str(i)]['nsfw'],
                                                slowmode_delay=data['text'][str(i)]['slowmode'],
                                                position=data['text'][str(i)]['position'],
                                                overwrites=ovws
                                                )
                                        else:
                                            await ctx.guild.create_text_channel(
                                                name=data['text'][str(i)]['name'],
                                                topic=data['text'][str(i)]['topic'],
                                                nsfw=data['text'][str(i)]['nsfw'],
                                                slowmode_delay=data['text'][str(i)]['slowmode'],
                                                position=data['text'][str(i)]['position'],
                                                category=get(ctx.guild.categories, name=data['text'][str(i)]['category']),
                                                overwrites=ovws
                                                )
                                    except:
                                        pass
                                for i in range(500):
                                    try:
                                        ovws = {}
                                        raw_ovw = data['voice'][str(i)]['perms']
                                        for role in ctx.guild.roles:
                                            try:
                                                ovw = discord.PermissionOverwrite.from_pair(discord.Permissions(permissions=raw_ovw[role.name]['a']), discord.Permissions(permissions=raw_ovw[role.name]['d']))
                                                ovws[role] = ovw
                                            except:
                                                pass
                                        if data['voice'][str(i)]['category'] == None:
                                            await ctx.guild.create_voice_channel(
                                                name=data['voice'][str(i)]['name'],
                                                user_limit=data['voice'][str(i)]['limit'],
                                                bitrate=data['voice'][str(i)]['bitrate'],
                                                position=data['voice'][str(i)]['position'],
                                                overwrites=ovws
                                                )
                                        else:
                                            await ctx.guild.create_voice_channel(
                                                name=data['voice'][str(i)]['name'],
                                                user_limit=data['voice'][str(i)]['limit'],
                                                bitrate=data['voice'][str(i)]['bitrate'],
                                                position=data['voice'][str(i)]['position'],
                                                category=get(ctx.guild.categories, name=data['voice'][str(i)]['category']),
                                                overwrites=ovws
                                                )
                                    except:
                                        pass
                                embed.title = "✅ | Готово"
                                embed.color = Color.success
                                embed.description = "Сервер был восстановлен."
                                await msg.edit(embed = embed, components = [])
                                await msg.clear_reactions()
                            else:
                                embed.color = Color.danger
                                embed.title = "🚫 | Отказ"
                                embed.description = "Только владелец сервера может использовать этот режим восстановления."
                                await msg.edit(embed=embed, components = [])
                                await msg.clear_reactions()
                        elif inter.clicked_button.label == 'Частичное восстановление':
                            await inter.create_response(type=6)
                            data = mongo.db.backups.find_one({"_id": ctx.guild.id})
                            embed.description = "Этап 1 из 4\n> Восстановление названия сервера"
                            await msg.edit(embed = embed)
                            await ctx.guild.edit(name = data['guild']['name'])
                            embed.description = "Этап 2 из 4\n> Создание ролей"
                            await msg.edit(embed = embed)
                            roles = []
                            text = []
                            voice = []
                            cat = []
                            for i in ctx.guild.roles:
                                roles.append(i.name)
                            for i in ctx.guild.text_channels:
                                text.append(i.name)
                            for i in ctx.guild.voice_channels:
                                voice.append(i.name)
                            for i in ctx.guild.categories:
                                cat.append(i.name)
                            for k in range(250):
                                j = 249 - k
                                try:
                                    if not data['roles'][str(j)]['name'] in roles:
                                        await ctx.guild.create_role(
                                            name=data['roles'][str(j)]['name'],
                                            colour=discord.Colour(value=data['roles'][str(j)]['color']),
                                            permissions=discord.Permissions(permissions=data['roles'][str(j)]['perms']),
                                            hoist=data['roles'][str(j)]['hoist'],
                                            mentionable=data['roles'][str(j)]['mentionable']
                                        )
                                except:
                                    pass
                            embed.description = "Этап 3 из 4\n> Создание категорий"
                            await msg.edit(embed = embed)
                            for i in range(500):
                                try:
                                    if not data['category'][str(i)]['name'] in cat:
                                        ovws = {}
                                        raw_ovw = data['category'][str(i)]['perms']
                                        for role in ctx.guild.roles:
                                            try:
                                                ovw = discord.PermissionOverwrite.from_pair(discord.Permissions(permissions=raw_ovw[role.name]['a']), discord.Permissions(permissions=raw_ovw[role.name]['d']))
                                                ovws[role] = ovw
                                            except:
                                                pass
                                        await ctx.guild.create_category(
                                            name=data['category'][str(i)]['name'],
                                            position=data['category'][str(i)]['position'],
                                            overwrites=ovws
                                            )
                                except:
                                    pass
                            embed.description = "Этап 4 из 4\n> Создание каналов"
                            await msg.edit(embed = embed)
                            for i in range(500):
                                try:
                                    if not data['text'][str(i)]['name'] in text:
                                        ovws = {}
                                        raw_ovw = data['text'][str(i)]['perms']
                                        for role in ctx.guild.roles:
                                            try:
                                                ovw = discord.PermissionOverwrite.from_pair(discord.Permissions(permissions=raw_ovw[role.name]['a']), discord.Permissions(permissions=raw_ovw[role.name]['d']))
                                                ovws[role] = ovw
                                            except:
                                                pass
                                        if data['text'][str(i)]['category'] == None:
                                            await ctx.guild.create_text_channel(
                                                name=data['text'][str(i)]['name'],
                                                topic=data['text'][str(i)]['topic'],
                                                nsfw=data['text'][str(i)]['nsfw'],
                                                slowmode_delay=data['text'][str(i)]['slowmode'],
                                                position=data['text'][str(i)]['position'],
                                                overwrites=ovws
                                                )
                                        else:
                                            await ctx.guild.create_text_channel(
                                                name=data['text'][str(i)]['name'],
                                                topic=data['text'][str(i)]['topic'],
                                                nsfw=data['text'][str(i)]['nsfw'],
                                                slowmode_delay=data['text'][str(i)]['slowmode'],
                                                position=data['text'][str(i)]['position'],
                                                category=get(ctx.guild.categories, name=data['text'][str(i)]['category']),
                                                overwrites=ovws
                                                )
                                except:
                                    pass
                            for i in range(500):
                                try:
                                    if not data['voice'][str(i)]['name'] in voice:
                                        ovws = {}
                                        raw_ovw = data['voice'][str(i)]['perms']
                                        for role in ctx.guild.roles:
                                            try:
                                                ovw = discord.PermissionOverwrite.from_pair(discord.Permissions(permissions=raw_ovw[role.name]['a']), discord.Permissions(permissions=raw_ovw[role.name]['d']))
                                                ovws[role] = ovw
                                            except:
                                                pass
                                        if data['voice'][str(i)]['category'] == None:
                                            await ctx.guild.create_voice_channel(
                                                name=data['voice'][str(i)]['name'],
                                                user_limit=data['voice'][str(i)]['limit'],
                                                bitrate=data['voice'][str(i)]['bitrate'],
                                                position=data['voice'][str(i)]['position'],
                                                overwrites=ovws
                                                )
                                        else:
                                            await ctx.guild.create_voice_channel(
                                                name=data['voice'][str(i)]['name'],
                                                user_limit=data['voice'][str(i)]['limit'],
                                                bitrate=data['voice'][str(i)]['bitrate'],
                                                position=data['voice'][str(i)]['position'],
                                                category=get(ctx.guild.categories, name=data['voice'][str(i)]['category']),
                                                overwrites=ovws
                                                )
                                except:
                                    pass
                            embed.title = "✅ | Готово"
                            embed.color = Color.success
                            embed.description = "Сервер был восстановлен."
                            await msg.edit(embed = embed, components = [])
                            await msg.clear_reactions()
                else:
                    await messages.err(ctx, "Неверный код.", True)    
            else:
                embed = discord.Embed()
                embed.set_footer(text = ctx.author, icon_url = ctx.author.avatar_url)
                embed.color = Color.danger
                embed.title = "🚫 | Отказ"
                embed.description = "Резервная копия сервера не была загружена."
                await ctx.send(embed=embed)                
        else:
            await messages.err(ctx, "Резервная копия не была создана.")

    @backup.command()
    @commands.cooldown(1, 30, commands.BucketType.guild)
    async def protect(self, ctx):
        if ctx.author == ctx.guild.owner:
            if checkbackup(ctx.guild):
                try:
                    code = mongo.db.backups.find_one({"_id": ctx.guild.id}, {"code": True})['code']
                except:
                    code = None
                a = await request_code(ctx, "⌨ | Пожалуйста, введите текущий код", code)
                if a[0]:
                    a = await request_code(ctx, "⌨ | Пожалуйста, введите новый код", code, False)
                    if not a[0]:
                        if not a[1]:
                            new = a[2]
                            a = await request_code(ctx, "⌨ | Пожалуйста, повторите код", code, False)
                            if not a[1]:
                                if a[2] != new:
                                    await messages.err(ctx, "Коды не совпадают.")
                                else:
                                    mongo.db.backups.update_one({"_id": ctx.guild.id}, {"$set": {"code": new}}, upsert=True)
                                    embed = discord.Embed()
                                    embed.title = "✅ | Готово"
                                    embed.color = Color.success
                                    embed.description = "Вы защитили резервную копию."
                                    await ctx.send(embed = embed)
                    elif not a[1]:
                        await messages.err(ctx, "Новый код не может совпадать со старым.")
                elif not a[1]:
                    await messages.err(ctx, "Неверный код.")
            else:
                await messages.err(ctx, "Резервная копия не была создана ранее.")
        else:
            await messages.only_owner(ctx)

def setup(bot):
    bot.add_cog(Backup(bot))
