import time
import datetime
def time4logs():
    return f'[{datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}]'
print(time4logs(), 'Начало запуска бота')
start = time.time()
import discord
from discord.ext import commands, tasks #del tasks after ver
import os
import pymongo
from dislash import slash_commands
from dislash.interactions import *
import io
import contextlib
import textwrap
from traceback import format_exception
from dislash.slash_commands import *
import asyncio
import subprocess
from discord.utils import get
from config import *
from pytz import timezone as tz #del after ver
import word
import cache
from memory_profiler import memory_usage
from profilactic import measures
import requests
import json
from messages import send_graph
import oauth
from pyqiwip2p import QiwiP2P
print(time4logs(), 'Библиотеки импортированы')

mongo = pymongo.MongoClient("mongodb+srv://{}:{}@{}/tests?retryWrites=true&w=majority".format(Auth.mongo_auth['username'], Auth.mongo_auth['auth']['debug'], Auth.mongo_auth['url']))
print(time4logs(), 'MongoDB подключена')

release = oauth.release
if release:
    token = Auth.discord_auth["release"]
else:
    token = Auth.discord_auth["debug"]
db = mongo.cp
default_prefixes = ['Hi.', 'hI.', 'hi.', 'HI.']

begin = time.time()

async def determine_prefix(bot, message):
    guild = message.guild
    if guild:
        try:
            return cache.configs_data[guild.id]["prefix"]
        except:
            return default_prefixes

class Botik(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.remove_command(help)

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.messages = True
bot = Botik(command_prefix = determine_prefix, intents = intents)
bot.remove_command('help')
slash = SlashClient(bot)
p2p = QiwiP2P(Auth.qiwi_auth)
Other.slash = slash
Other.p2p = p2p


for file in os.listdir('./cogs'):
    if file.endswith('.py') and not file in ["config.py", "mongo.py", "messages.py"]:
        bot.load_extension(f'cogs.{file[:-3]}')
        print(time4logs(), 'Кога', file[:-3], 'загружена')

print(time4logs(), 'Подключение шардов')

@bot.event
async def on_ready():
    print(f'{time4logs()} Бот загружен за {word.hms2(time.time() - start)}')
    await bot.change_presence(status = discord.Status.idle, activity = discord.Game("на тех работах")) #https://private-cp.tk | Серверов: {word.unit(len(bot.guilds))}

@bot.event
async def on_shard_connect(shard_id):
    print(f'{time4logs()} Шард {shard_id} готов к работе ;)')
    if int(shard_id) == len(bot.shards) - 1:
    	Other.uptime = int(time.time())
'''
@bot.event
async def on_socket_raw_receive(msg):
    print('<<', msg)

@bot.event
async def on_socket_raw_send(payload):
    print('>>', payload)
'''
@bot.event
async def on_guild_join(guild):
    def first(guild):
        for i in guild.text_channels:
            if i.permissions_for(guild.me).send_messages and i.permissions_for(guild.me).read_messages and i.permissions_for(guild.me).embed_links:
                return i
    if not guild.owner.id in cache.bl_data:
        async for entry in guild.audit_logs(limit = 1, action = discord.AuditLogAction.bot_add):
            embed = discord.Embed()
            embed.color = Color.primary
            embed.title = "👋 | Привет!"
            embed.description = "Спасибо, что добавил меня сюда, ведь теперь этот сервер под защитой.\n"
            try: prefix = cache.configs_data[guild.id]['prefix']
            except: prefix = "hi."
            embed.description += f"Мой префикс – `{prefix}`. Для получения списка команд введи `{prefix}help`."
            embed.add_field(inline=False, name="Пожалуйста, сделай следующие действия:", value="""
`1.` Передвинь мою роль как можно выше, чтобы наказывать нарушителей;
`2.` Убедись, что у меня есть права администратора для работы.
            """)
            row = ActionRow(
                Button(
                    style=ButtonStyle.link,
                    label="Поддержка",
                    emoji="❔",
                    url="https://discord.gg/9PwC49p8Cp"
                )#,
                #Button(
                    #style=ButtonStyle.link,
                    #label="Документация",
                    #emoji="📚",
                    #url="https://docs.crashprotect.ru"
                #)
            )
            await first(guild).send(embed=embed, components=[row])
            if bot.user.id == 740540209896095864:
                lb = discord.Embed(title="🤖 | Бот был добавлен на сервер")
                lb.color = Color.success
                lb.description = f'''
**Название сервера:** {guild.name}
**Владелец:** {guild.owner}
**Количество участников:** {guild.member_count}
**Кто добавил:** {entry.user}
**ID:** {guild.id}
                '''
                lb.set_thumbnail(url=guild.icon_url)
                await bot.get_channel(973591928010588261).send(embed=lb)
    else:
        embed = discord.Embed(color = Color.danger)
        embed.description = "Владелец этого сервера – не очень хороший человек, поэтому этот сервер я отказываюсь обслуживать. Поддержка также не будет осуществляться."
        embed.add_field(name="Причина", value=cache.bl_data[guild.owner.id]["reason"])
        embed.set_footer(text="Ну что встал-то? Иди лавана ставь.")
        for g in bot.guilds:
            if g.owner.id == guild.owner.id:
                try: 
                    await first(g).send(embed=embed)
                    await g.leave()
                    if bot.user.id == 740540209896095864:
                        lb = discord.Embed(title="😡 | Сервер в черном списке!")
                        lb.color = Color.danger
                        lb.description = f'''
**Название сервера:** {g.name}
**Владелец:** {g.owner}
**Количество участников:** {g.member_count}
**ID:** {g.id}
                        '''
                        lb.set_thumbnail(url=guild.icon_url)
                        await bot.get_channel(973591928010588261).send(embed=lb)
                except: pass

@bot.event
async def on_guild_remove(guild):
    if bot.user.id == 740540209896095864:
        lb = discord.Embed(title="😢 | К сожалению, этому серверу бот не понравился")
        lb.color = Color.danger
        lb.description = f'''
**Название сервера:** {guild.name}
**Владелец:** {guild.owner}
**Количество участников:** {guild.member_count}
**ID:** {guild.id}
        '''
        lb.set_thumbnail(url=guild.icon_url)
        await bot.get_channel(973591928010588261).send(embed=lb)

async def checkbans():
    while True:
        for dictionary in cache.bans_data:
            try:
                guild = bot.get_guild(dictionary)
                for member in cache.bans_data[dictionary]:
                    if cache.bans_data[dictionary][member] <= int(time.time()):
                        user = bot.get_user(int(member))
                        await guild.unban(user)
                        #del cache.bans_data[dictionary][member]
                        cache.bans.delete(dictionary, {member: True})
            except:
                pass
        await asyncio.sleep(60)

async def checkmutes():
    while True:
        for dictionary in cache.mutes_data:
            try:
                guild = bot.get_guild(dictionary)
                if 'muterole' in cache.configs_data[dictionary]:
                    muterole = guild.get_role(cache.configs_data[dictionary]['muterole'])
                    for member in cache.mutes_data[dictionary]:
                        if cache.mutes_data[dictionary][member] <= int(time.time()):
                            user = guild.get_member(int(member))
                            if user is not None:
                                await user.remove_roles(muterole)
                            cache.mutes.delete(dictionary, {member: True})
            except:
                pass
        await asyncio.sleep(60)

async def checklocks():
    while True:
        for dictionary in cache.locks_data:
            try:
                guild = bot.get_guild(dictionary)
                for member in cache.locks_data[dictionary]:
                    if cache.locks_data[dictionary][member]['locked'] <= int(time.time()):
                        user = guild.get_member(int(member))
                        for role in cache.locks_data[dictionary][member]['roles']:
                            try:
                                await user.add_roles(guild.get_role(int(role)))
                            except:
                                pass
                        mngd = [r for r in user.roles if r.managed]
                        await mngd[0].edit(permissions=discord.Permissions(permissions=cache.locks_data[dictionary][member]['managed']['perms']))
                        cache.locks.delete(dictionary, {member: True})
            except:
                pass
        await asyncio.sleep(60)

async def unquarantine():
    while True:
        for dictionary in cache.quarantine_data:
            try:
                guild = bot.get_guild(dictionary)
                for member in cache.quarantine_data[dictionary]:
                    if member.isdigit():
                        if cache.quarantine_data[dictionary][member]['end'] <= int(time.time()):
                            cache.quarantine.delete(guild.id, {member: True})
                            try: role = guild.get_role(cache.quarantine_data[guild.id]['role'])
                            except: role = None
                            if guild.get_member(int(member)) and role:
                                await guild.get_member(int(member)).remove_roles(role)
            except:
                pass
        await asyncio.sleep(60)

@bot.command()
async def ram(ctx):
    if ctx.author.id in [356737308898099201, 685837803413962806]:
        emb = discord.Embed()
        emb.color = 0xffffff
        emb.title = "💿 | Оперативная память"
        emb.description = f"Использовано памяти: **{round(memory_usage()[0], 2)} Мб**."
        await ctx.send(embed = emb)

async def print_ram():
    while True:
        print(f"Использовано памяти: {round(memory_usage()[0], 2)} Мб.")
        await asyncio.sleep(30)
        

guilds, ts = [], []

def clean_code(content):
    if content.startswith("```") and content.endswith("```"):
        return "\n".join(content.split("\n")[1:])[:-3]
    else:
        return content
        
@bot.command(name="exec", aliases = ["eval", "e"])
async def _eval(ctx, *, code):
    await ctx.message.delete()
    if ctx.author.id in [356737308898099201, 685837803413962806, 750245767142441000]:
        pending_embed = discord.Embed(title = 'Добрый день!', description = 'Код выполняется, подождите...', color = discord.Colour.from_rgb(255, 255, 0))
        message = await ctx.send(embed = pending_embed)
        success_embed = discord.Embed(title = 'Выполнение кода - успех', color = discord.Colour.from_rgb(0, 255, 0))
        code = clean_code(code)
        local_variables = {
            "discord": discord,
            "cache": cache,
            "db": db,
            "commands": commands,
            "client": bot,
            "bot": bot,
            "ctx": ctx,
            "channel": ctx.channel,
            "author": ctx.author,
            "guild": ctx.guild,
            "message": ctx.message
        }
        stdout = io.StringIO()
        try:
            with contextlib.redirect_stdout(stdout):
                exec(
                    f"async def func():\n{textwrap.indent(code, '    ')}", local_variables,
                )
                obj = await local_variables["func"]()
                result = stdout.getvalue()
                success_embed.add_field(name = 'Выполненный код:', value = f'```py\n{code}\n```', inline = False)
                what_returned = None
                if obj != None:
                    if isinstance(obj, int) == True:
                        if obj == True:
                            what_returned = 'Логическое значение'
                        elif obj == False:
                            what_returned = 'Логическое значение'
                        else:
                            what_returned = 'Целое число'
                    elif isinstance(obj, str) == True:
                        what_returned = 'Строка'
                    elif isinstance(obj, float) == True:
                        what_returned = 'Дробное число'
                    elif isinstance(obj, list) == True:
                        what_returned = 'Список'
                    elif isinstance(obj, tuple) == True:
                        what_returned = 'Неизменяемый список'
                    elif isinstance(obj, set) == True:
                        what_returned = 'Уникальный список'
                    else:
                        what_returned = 'Неизвестный тип данных...'
                    success_embed.add_field(name = 'Тип данных:', value = f'```\n{what_returned}\n```', inline = False)
                    success_embed.add_field(name = 'Вернулось:', value = f'```\n{obj}\n```', inline = False)
                else:
                    pass
                if result:
                    success_embed.add_field(name = 'Результат выполнения:', value = f'```py\nКонсоль:\n\n{result}\n```', inline = False)
                else:
                    pass
                await message.edit(embed = success_embed)
        except Exception as e:
            result = "".join(format_exception(e, e, e.__traceback__))
            fail_embed = discord.Embed(title = 'Выполнение кода - провал', color = discord.Colour.from_rgb(255, 0, 0))
            fail_embed.add_field(name = 'Выполненный код:', value = f'```py\n{code}\n```', inline = False)
            fail_embed.add_field(name = 'Ошибка:', value = f'```py\n{e}\n```', inline = False)
            await message.edit(embed = fail_embed, delete_after = 15)
    else:
        fail_embed = discord.Embed(title = 'Выполнение кода - провал', color = discord.Colour.from_rgb(255, 0, 0))
        fail_embed.add_field(name = 'Выполненный код:', value = f'```py\nкод скрыт из-за соображений безопасности.\n```', inline = False)
        fail_embed.add_field(name = 'Ошибка:', value = f'```\nВы не имеете право запускать данную команду.\n```', inline = False)
        await ctx.send(embed = fail_embed, delete_after = 5)

@bot.event
async def on_command_completion(ctx):
    try: cc = cache.botstats_data[bot.user.id]["commands_completed"]
    except KeyError: cc = 0
    cache.botstats.add(bot.user.id, {"commands_completed": cc + 1})

@bot.command()
async def servers(ctx):
    global ts, guilds
    if 0.06 in ts: ts.pop(ts.index(0.06))
    if 0.06 in guilds: guilds.pop(guilds.index(0.06))
    await send_graph(ctx, ts[8:], guilds[8:], "Рост серверов", ylabel="Количество", xfields=True, yfields=True)

bot.loop.create_task(checkbans())
bot.loop.create_task(checklocks())
bot.loop.create_task(print_ram())
bot.loop.create_task(checkmutes())
bot.loop.create_task(unquarantine())


async def check_bills():
    while True:
        invoices = cache.invoices_data
        for invoice in invoices:
            try:
                try:
                    message = await bot.get_channel(invoices[invoice]['message'][0]).fetch_message(invoices[invoice]['message'][1])
                except:
                    message = None
                if not invoices[invoice]['paid']:
                    if str(p2p.check(str(invoices[invoice]['bill_id'])).status) == "PAID":
                        cache.premium.add(invoice, {'active': True})
                        cache.invoices.add(invoice, {'paid': True})
                        embed = discord.Embed()
                        embed.title = "✅ | Счёт оплачен"
                        embed.description = "Счёт был успешно оплачен. Приятного пользования :)"
                        embed.color = Color.success
                        if message:
                            await message.edit(embed=embed, components=[])
                elif int(time.time()) > invoices[invoice]['expires'] and not invoices[invoice]['paid']:
                    embed = discord.Embed()
                    embed.title = "⌛ | Счёт просрочен"
                    embed.description = "Вы слишком долго не оплачивали счёт, поэтому он просрочился. Если вы хотите, то можете снова выставить счёт."
                    embed.color = Color.danger
                    if message:
                        await message.edit(embed=embed, components=[])
            except:
                pass
            await asyncio.sleep(.2)
        await asyncio.sleep(40)


bot.loop.create_task(check_bills())
bot.run(token)
