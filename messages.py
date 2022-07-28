import discord
from discord.ext import commands
from config import Color
import datetime
import pytz
import matplotlib.pyplot as plt
import os
import matplotlib.font_manager as font_manager
import random
import cache
import punishments

async def send_graph(
    ctx, x, y, title="Простой график, ничего необычного", label_color="white", background_color="#181818", line_color="#7e57c2", xlabel="Время", ylabel="Величина", xfields=None, yfields=None
):
    fe = font_manager.FontEntry(
        fname='/home/container/fonts/Rubik-Light.ttf',
        name='Rubik')
    font_manager.fontManager.ttflist.insert(0, fe)
    plt.rcParams['text.color'] = label_color
    plt.rcParams['axes.labelcolor'] = label_color
    plt.rcParams['xtick.color'] = label_color
    plt.rcParams['ytick.color'] = label_color
    plt.rcParams['font.family'] = fe.name
    plt.rcParams['font.size'] = 12
    fig, ax1 = plt.subplots(1, 1)
    ax1.set_facecolor(background_color)
    fig.patch.set_facecolor(background_color)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    ax1.plot(x, y, color=line_color)
    fig.canvas.draw()
    labels = [item.get_text() for item in ax1.get_xticklabels()]
    ax1.set_title(title)
    if xfields:
        labels = [datetime.datetime.fromtimestamp(i, pytz.timezone("Europe/Moscow")).strftime('%H:%M') for i in x]
        ax1.set_xticklabels(labels)
    labels = [item.get_text() for item in ax1.get_yticklabels()]
    if yfields:
        labels = [int(float(i)) for i in labels]
        ax1.set_yticklabels(labels)
    code = ''.join(random.choices("abcdef0123456789", k = 6))
    plt.savefig(f"/home/container/{code}.png")
    await ctx.send(file=discord.File(f"{code}.png"))
    os.remove(f"/home/container/{code}.png")

async def err(ctx, message, reset_cooldown=False):
    embed = discord.Embed(
        title = "❌ | Упс, ошибка",
        description = message,
        color = Color.danger
    )
    embed.set_footer(icon_url=ctx.author.avatar_url, text=ctx.author)
    await ctx.send(embed=embed)
    if reset_cooldown:
        ctx.command.reset_cooldown(ctx)

async def only_owner(ctx):
    embed = discord.Embed(
        title = "✋ | Недостаточно прав",
        description = 'Данную команду может использовать только владелец сервера. Если вы являетесь таковым, просто подождите несколько минут и заново введите её.',
        color = Color.danger
    )
    embed.set_footer(icon_url=ctx.author.avatar_url, text=ctx.author)
    await ctx.send(embed=embed)

async def only_admin(ctx):
    embed = discord.Embed(
        title = "✋ | Недостаточно прав",
        description = 'Данную команду могут использовать только высшие администраторы (роль которых выше большинства других ролей).',
        color = Color.danger
    )
    embed.set_footer(icon_url=ctx.author.avatar_url, text=ctx.author)
    await ctx.send(embed=embed)

'''def reaction_check(reaction, user):
    return reaction.message.id == msg.id and user == ctx.author

def message_check(author):
    def inner_check(message): 
        if message.author != author:
            return False
        try: 
            message.content
            return True 
        except ValueError: 
            return False
    return inner_check'''

def is_admin(member):
    roles = [r for r in member.guild.roles if not r.managed]
    if member == member.guild.owner: return True
    if member.top_role.position > len(roles) - 5 and member.guild_permissions.administrator: return True
    return False

async def send_logs(self, guild, embed):
    if not guild.id in cache.configs_data: return
    if not "log-channel" in cache.configs_data[guild.id]: return
    channel = self.bot.get_channel(cache.configs_data[guild.id]['log-channel'])
    if not channel: return
    await channel.send(embed=embed)

async def nukep(self, member, reason):
    if member.bot: a = 'pu-bot'
    else: a = 'pu-user'

    try: 
        data = cache.configs_data[member.guild.id][a]
    except:
        if member.bot:
            data = {"type": "kick", "duration": 0}
        else:
            data = {"type": "ban", "duration": 0}
    if data['duration'] == 0: data['duration'] = 228133722

    if data['type'] == 'ban':
        await member.ban(reason=reason)
        await punishments.tempban(member, member, data['duration'], ignore_ndm=True)
    elif data['type'] == 'kick':
        await member.kick(reason=reason)
    elif data['type'] == 'lock':
        await punishments.lockbot(member, member, data['duration'])
    elif data['type'] == 'quarantine':
        await punishments.add_qua(member.guild, self.bot.user, member, data['duration'], reason)

def get_command(bot, name: str):
    name = name.lower()
    c = {}
    for i in bot.commands:
        c[i.name] = i.aliases
    for n, a in c.items():
        if name == n or name in a:
            return n

class HasNoRoles(commands.CheckFailure):
    pass

class HasDeniedRoles(commands.CheckFailure):
    pass

class NotAllowedChannel(commands.CheckFailure):
    pass

class DeniedChannel(commands.CheckFailure):
    pass

class NoPerms(commands.CheckFailure):
    pass

async def check_perms(ctx):

    default_perms = {
        "addroles": [ctx.author.guild_permissions.administrator, "Администратор"],
        "ban": [ctx.author.guild_permissions.ban_members, "Банить участников"],
        "bans": [ctx.author.guild_permissions.ban_members, "Банить участников"],
        "correct": [ctx.author.guild_permissions.manage_nicknames, "Управлять никнеймами"],
        "correct_all": [ctx.author.guild_permissions.manage_nicknames, "Управлять никнеймами"],
        "kick": [ctx.author.guild_permissions.kick_members, "Выгонять участников"],
        "lock_bot": [ctx.author.guild_permissions.administrator, "Администратор"],
        "mute": [ctx.author.guild_permissions.manage_roles, "Управлять ролями"],
        "mutes": [ctx.author.guild_permissions.manage_roles, "Управлять ролями"],
        "purge": [ctx.author.guild_permissions.manage_messages, "Управлять сообщениями"],
        "quarantine": [ctx.author.guild_permissions.administrator, "Администратор"],
        "remroles": [ctx.author.guild_permissions.administrator, "Администратор"],
        "unban": [ctx.author.guild_permissions.ban_members, "Банить участников"],
        "unlock_bot": [ctx.author.guild_permissions.administrator, "Администратор"],
        "unmute": [ctx.author.guild_permissions.manage_roles, "Управлять ролями"],
        "unwarn": [ctx.author.guild_permissions.kick_members, "Выгонять участников"],
        "warn": [ctx.author.guild_permissions.kick_members, "Выгонять участников"],
        "echo": [ctx.author.guild_permissions.administrator, "Администратор"],
        "lock": [ctx.author.guild_permissions.administrator, "Администратор"],
        "mass_ban": [ctx.author.guild_permissions.administrator, "Администратор"],
        "unlock": [ctx.author.guild_permissions.administrator, "Администратор"],
        "antiraid": [ctx.author.guild_permissions.administrator, "Администратор"],
        "antiflood": [ctx.author.guild_permissions.administrator, "Администратор"],
        "antiinvite": [ctx.author.guild_permissions.administrator, "Администратор"],
        "muterole": [ctx.author.guild_permissions.manage_roles, "Управлять ролями"],
        "nickcorrector": [ctx.author.guild_permissions.manage_nicknames, "Управлять никнеймами"],
        "prefix": [ctx.author.guild_permissions.administrator, "Администратор"],
        "np": [ctx.author.guild_permissions.administrator, "Администратор"],
        "warn_actions": [ctx.author.guild_permissions.administrator, "Администратор"],
        "addsingle": [ctx.author.guild_permissions.manage_roles, "Управлять ролями"],
        "delsingle": [ctx.author.guild_permissions.manage_roles, "Управлять ролями"],
        "rr_list": [ctx.author.guild_permissions.manage_roles, "Управлять ролями"],
        "backup": [ctx.author.guild_permissions.administrator, "Администратор"],
        "notify_dm": [ctx.author.guild_permissions.administrator, "Администратор"],
        "log_channel": [ctx.author.guild_permissions.administrator, "Администратор"],
        "wl": [is_admin(ctx.author), "Высший администратор"],
        "score": [is_admin(ctx.author), "Высший администратор"],
        "perms": [is_admin(ctx.author), "Высший администратор"]
    }

    aa = ctx.command.name

    if ctx.guild.id in cache.perms_data:
        if "*" in cache.perms_data[ctx.guild.id]:
            aa = "*"

    aroles, droles = [], []
    achannels, dchannels = [], []
    try: aroles = cache.perms_data[ctx.guild.id][aa]["roles"]["allowed"]
    except: aroles = []
    try: droles = cache.perms_data[ctx.guild.id][aa]["roles"]["denied"]
    except: droles = []

    try: achannels = cache.perms_data[ctx.guild.id][aa]["channels"]["allowed"]
    except: achannels = []
    try: dchannels = cache.perms_data[ctx.guild.id][aa]["channels"]["denied"]
    except: dchannels = []


    aroles = [a for a in aroles if ctx.guild.get_role(a)]
    droles = [a for a in droles if ctx.guild.get_role(a)]

    achannels = [a for a in achannels if ctx.guild.get_channel(a)]
    dchannels = [a for a in dchannels if ctx.guild.get_channel(a)]

    if not len(achannels) and not len(dchannels) and not len(aroles) and not len(droles):
        if ctx.command.name in default_perms:
            if not default_perms[ctx.command.name][0]:
                raise NoPerms(default_perms[ctx.command.name][1])

    if len(aroles) or len(droles):
        found = False
        for r in ctx.author.roles:
            if r.id in droles:
                raise HasDeniedRoles(r.mention)
            if r.id in aroles: found = True
        if not found:
            raise HasNoRoles('\n'.join([ctx.guild.get_role(a).mention for a in aroles]))
    
    if (len(dchannels) or len(achannels)) and not (len(aroles) and len(droles)):
        if ctx.command.name in default_perms:
            if not default_perms[ctx.command.name][0]:
                raise NoPerms(default_perms[ctx.command.name][1])

    if len(achannels) or len(dchannels):
        if ctx.channel.id in dchannels:
            raise DeniedChannel(ctx.channel.mention)
        if not ctx.channel.id in achannels:
            if achannels != []:
                raise NotAllowedChannel('\n'.join([ctx.guild.get_channel(a).mention for a in achannels]))

    return True

def rebool(bool: bool, true_return, false_return=None):
    if bool: return true_return
    return false_return

default_scores = {
    "channel_delete": 6,
    "channel_create": 3,
    "role_delete": 5,
    "role_create": 2,
    "ban": 5,
    "kick": 4,
    "guild_update": 6,

}

def generate_progressbar(amount):
    amount = int(amount * 100)
    bar = "<:progress_begin_unfill:910102173780705310>"
    if amount >= 10:
        bar = "<:progress_begin_fill:910102173747138601>"
    bar += "<:progress_middle_fill:910102173625516083>" * (amount//10)
    bar += "<:progress_middle_unfill:910102173839409193>" * (9-(amount//10))
    if amount >= 100:
        bar += "<:progress_end_fill:910102173805854751>"
    else:
        bar += "<:progress_end_unfill:910102173881335818>"
    return bar

def has_premium(guild_id):
    return guild_id in cache.premium_data