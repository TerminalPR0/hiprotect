import discord
from discord.ext import commands
from config import Color
import messages
import cache
import punishments
import asyncio
import word
import time
import datetime
from config import Other
from profilactic import measures
from dislash.slash_commands import *
from dislash.interactions import *
import typing

async def audit_user(guild, action):
    e = await guild.audit_logs(limit=1, action=action).get()
    return e.user

slash = Other.slash

default_whitelist = [
    159985870458322944, 
    752367350657056851, 
    310848622642069504, 
    292953664492929025, 
    458276816071950337, 
    784760819997081600, 
    240254129333731328, 
    472911936951156740, 
    557628352828014614, 
    722196398635745312, 
    501982335076532224, 
    511786918783090688, 
    511967838559272992, 
    755645853590356099, 
    704967695036317777, 
    795551166393876481, 
    204255221017214977, 
    620689014910877719, 
    282859044593598464, 
    740540209896095864
]
times = 0


def smart_wl(guild, user, action):
    measures.add(what=3)
    mean = {
        discord.AuditLogAction.channel_create: "channel_create",
        discord.AuditLogAction.channel_delete: "channel_delete",
        discord.AuditLogAction.role_create: "role_create",
        discord.AuditLogAction.role_delete: "role_delete",
        discord.AuditLogAction.role_update: "role_admin",
        discord.AuditLogAction.kick: "kick",
        discord.AuditLogAction.ban: "ban",
        discord.AuditLogAction.guild_update.name: "guild_update"
    }
    if not guild.id in cache.whitelist_data:
        return False
    else:
        allowed = False
        w = cache.whitelist_data[guild.id]
        if str(user.id) in w:
            allowed = w[str(user.id)][mean[action]]
        try:
            role_list = [str(r.id) for r in user.roles]
            for r in role_list:
                if r in w:
                    if w[r][mean[action]] and not allowed:
                        allowed = True
        except:
            pass

        return allowed

async def restore_channel(self, guild, dictionary):
    await asyncio.sleep(.3)
    ctype = dictionary['ctype']
    if ctype == 'category':
        await guild.create_category(
            name=dictionary['name'],
            overwrites=dictionary['overwrites'],
            position=dictionary['position'],
            reason="Восстановление удалённой категории"
        )
    elif ctype == 'text':
        if dictionary['category']:
            c = await guild.create_text_channel(
                name=dictionary['name'],
                topic=dictionary['topic'],
                nsfw=dictionary['nsfw'],
                slowmode_delay=dictionary['slowmode_delay'],
                overwrites=dictionary['overwrites'],
                position=dictionary['position'],
                reason="Восстановление удалённого канала",
                category=discord.utils.get(guild.categories, name=dictionary['category'])
            )
        else:
            c = await guild.create_text_channel(
                name=dictionary['name'],
                topic=dictionary['topic'],
                nsfw=dictionary['nsfw'],
                slowmode_delay=dictionary['slowmode_delay'],
                overwrites=dictionary['overwrites'],
                position=dictionary['position'],
                reason="Восстановление удалённого канала",
            )
        self.bot.loop.create_task(move2category(c, dictionary['category']))
    elif ctype == 'voice':
        if dictionary['category']:
            c = await guild.create_voice_channel(
                name=dictionary['name'],
                bitrate=dictionary['bitrate'],
                user_limit=dictionary['user_limit'],
                overwrites=dictionary['overwrites'],
                position=dictionary['position'],
                reason="Восстановление удалённого канала",
                category=discord.utils.get(guild.categories, name=dictionary['category'])
            )            
        else:
            c = await guild.create_voice_channel(
                name=dictionary['name'],
                bitrate=dictionary['bitrate'],
                user_limit=dictionary['user_limit'],
                overwrites=dictionary['overwrites'],
                position=dictionary['position'],
                reason="Восстановление удалённого канала",
            )
        self.bot.loop.create_task(move2category(c, dictionary['category']))
        
async def move2category(channel, category_name):
    await asyncio.sleep(8)
    try:
        await channel.edit(category = discord.utils.get(channel.guild.categories, name=category_name))
    except:
        pass

async def restore_role(guild, dictionary):
    await asyncio.sleep(.3)
    await guild.create_role(
        name=dictionary['name'],
        permissions=dictionary['perms'],
        colour=dictionary['color'],
        hoist=dictionary['hoist'],
        mentionable=dictionary['mentionable'],
        reason='Анти краш - восстановление удалённой роли'
    )

async def who_added(b, guild, bot):
    if guild.id in cache.invited_data:
        a = cache.invited_data[guild.id]
        if str(bot.id) in a:
            mm = guild.get_member(int(a[str(bot.id)]))
            try:
                nuker = cache.configs_data[guild.id]
                t = nuker['nuker-type']
                ti = nuker['nuker-time']
                if ti == 0:
                    ti = 228133722
            except:
                t, ti = 'none', 0
            if t == 'kick':
                await mm.kick(reason="Пригласил краш-бота")
            elif t == 'ban':
                await mm.ban(reason="Пригласил краш-бота")
                await punishments.tempban(bot, mm, ti, "Приглашение краш-бота на сервер")
raids = {}
nukes = {}

def get_score(guild, t):
    event_score = messages.default_scores[t]
    max_score = 20
    reset_in = 10
    
    try: event_score = cache.antinuke_data[guild.id][t]
    except KeyError: pass

    try: max_score = cache.configs_data[guild.id]["maxscore"]
    except KeyError: pass

    try: reset_in = cache.configs_data[guild.id]["reset-in"]
    except KeyError: pass

    return {
        "event": event_score,
        "max": max_score,
        "reset": reset_in
    }

async def reset_antinuke(guild):
    global nukes
    if not guild.id in nukes: return
    if time.time() < nukes[guild.id]["reset-ts"]: return
    await asyncio.sleep(get_score(guild, "channel_delete")["reset"])
    try: del nukes[guild.id]
    except: pass

def handle_antinuke(self, guild, event, data):
    global nukes
    gs = get_score(guild, event.replace('-', '_'))
    if not guild.id in nukes:
        nukes[guild.id] = {
            "reset-ts": time.time(),
            "current-score": 0,
            "is-recovering": False,
            "for-recovering": []
        }
    if nukes[guild.id]["is-recovering"]: return
    nukes[guild.id]["current-score"] += gs["event"]
    if nukes[guild.id]["reset-ts"] < time.time():
        nukes[guild.id]["reset-ts"] += gs["reset"]
    nukes[guild.id]["for-recovering"].append(data)
    #print(nukes[guild.id])
    #print(gs)
    self.bot.loop.create_task(reset_antinuke(guild))

    if nukes[guild.id]["current-score"] > gs["max"]:
        #print("GS!")
        return True
    return False


async def recover_items(self, guild):
    global nukes
    if not guild.id in nukes: return
    if nukes[guild.id]["is-recovering"]: return

    nukes[guild.id]["is-recovering"] = True
    for i in nukes[guild.id]["for-recovering"]:
        if i['ctype'] in ['text', 'voice', 'category']:
            await restore_channel(self, guild, i)
        elif i['ctype'] == 'role':
            await restore_role(guild, i)
        elif i['ctype'] in ['channel-delete', 'role-delete']:
            await i['target'].delete()
        elif i['ctype'] == 'ban':
            euser = await audit_user(guild, discord.AuditLogAction.ban)
            if euser != self.bot.user and euser != guild.owner:
                await guild.unban(i['target'])
    try: del nukes[guild.id]
    except: pass

class AntiCrash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        d = cache.configs_data[before.id]
        if handle_antinuke(self, before, 'guild_update', d):
            global wl, default_whitelist
            euser = await audit_user(before, discord.AuditLogAction.guild_update)
            if not smart_wl(before, euser, discord.AuditLogAction.guild_update) and euser != before.owner and not euser.id in default_whitelist:
                print(str(euser.id in default_whitelist))
                try:
                    await messages.nukep(self, euser, "Попытка краша сервера (смена аватара сервера или его названия)")
                except:
                    pass
                if euser.bot:
                    await who_added(self.bot, before, euser)
                try: await before.edit(name=before.name)
                except Exception as e:
                    print(e)
                try: await before.edit(icon=before.icon)
                except Excepion as e:
                    print(e)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        if not member.bot:
            measures.add(what=3)
            if member.guild.id in cache.configs_data:
                d = cache.configs_data[member.guild.id]
                try:
                    muterole = member.guild.get_role(d['muterole'])
                    if str(member.id) in cache.mutes_data[member.guild.id]:
                        await member.add_roles(muterole)
                except:
                    pass
                global raids
                if member.guild.id in cache.antiraid_data:
                    if str(member.guild.id) in raids:
                        try:
                            joins = cache.antiraid_data[member.guild.id]['joins']
                            interval = cache.antiraid_data[member.guild.id]['interval']
                            turn = cache.antiraid_data[member.guild.id]['turn']
                        except:
                            joins, interval, turn = 0, 0, 0
                        if joins != 0 and interval !=  0 and turn != 0:
                            try:
                                curj = raids[str(guild.id)]['joins']
                                nextt = raids[str(guild.id)]['next']
                            except:
                                raids[str(guild.id)]['joins'] = 1
                                raids[str(guild.id)]['next'] = 0
                                curj = raids[str(guild.id)]['joins']
                                nextt = raids[str(guild.id)]['next']
                            if int(time.time()) > nextt:
                                raids[str(guild.id)]['next'] = int(time.time()) + interval
                                raids[str(guild.id)]['joins'] = 1
                            else:
                                raids[str(guild.id)]['joins'] = curj + 1
                                if curj >= joins:
                                    await member.kick(reason='Защита от рейдов')
                else:
                    raids[str(guild.id)] = {}
        else:
            measures.add(what=9)
            e = await member.guild.audit_logs(limit=1, action=discord.AuditLogAction.bot_add).get()
            cache.invited.add(member.guild.id, {str(member.id): str(e.user.id)})

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        guild = channel.guild
        if isinstance(channel, discord.TextChannel):
            if channel.category:
                category = channel.category.name
            else:
                category = None
            d = {
                'name':channel.name,
                'topic':channel.topic,
                'nsfw':channel.nsfw,
                'slowmode_delay':channel.slowmode_delay,
                'position':channel.position,
                'overwrites':channel.overwrites,
                'ctype':'text',
                'category': category
            }
        elif isinstance(channel, discord.VoiceChannel):
            if channel.category:
                category = channel.category.name
            else:
                category = None
            d = {
                'name':channel.name,
                'bitrate':channel.bitrate,
                'user_limit':channel.user_limit,
                'position':channel.position,
                'overwrites':channel.overwrites,
                'ctype':'voice',
                'category': category
            }
        elif isinstance(channel, discord.CategoryChannel):
            d = {
                'name':channel.name,
                'position':channel.position,
                'overwrites':channel.overwrites,
                'ctype':'category'
            }
        if handle_antinuke(self, guild, 'channel_delete', d):
            euser = await audit_user(guild, discord.AuditLogAction.channel_delete)
            global wl, default_whitelist
            if not smart_wl(guild, euser, discord.AuditLogAction.channel_delete) and euser != guild.owner and not euser.id in default_whitelist:
                print(str(euser.id in default_whitelist))
                try:
                    await messages.nukep(self, euser, "Попытка краша сервера (удаление каналов)")
                except:
                    pass
                if euser.bot:
                    await who_added(self.bot, guild, euser)
                await recover_items(self, guild)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        guild = channel.guild
        d = {"ctype": "channel-delete", "target": channel}
        if handle_antinuke(self, guild, 'channel_create', d):
            euser = await audit_user(guild, discord.AuditLogAction.channel_create)
            global wl, default_whitelist
            if not smart_wl(guild, euser, discord.AuditLogAction.channel_create) and euser != guild.owner and not euser.id in default_whitelist:
                try:
                    await messages.nukep(self, euser, "Попытка засорения сервера (создание каналов)")
                except:
                    pass
                if euser.bot:
                    await who_added(self.bot, guild, euser)
                await asyncio.sleep(5)
                await recover_items(self, guild)

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        if before.permissions != after.permissions:
            guild = after.guild
            euser = await audit_user(guild, discord.AuditLogAction.role_update)
            if euser != guild.owner:
                try:
                    rp = cache.automoderation_data[guild.id]['roleprotect']
                except:
                    rp = 0
                if rp == 75:
                    global wl, default_whitelist
                    if not smart_wl(guild, euser, discord.AuditLogAction.role_update) and euser != guild.owner and not euser.id in default_whitelist:
                        try:
                            await after.edit(permissions=before.permissions)
                        except:
                            pass
            

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        if role.managed: return
        guild = role.guild
        d = {"ctype": "role-delete", "target": role}
        if handle_antinuke(self, guild, 'role_create', d):
            euser = await audit_user(guild, discord.AuditLogAction.role_create)
            global wl, default_whitelist
            if not smart_wl(guild, euser, discord.AuditLogAction.role_create) and euser != guild.owner and not euser.id in default_whitelist:
                try:
                    await messages.nukep(self, euser, "Попытка засорения сервера (создание ролей)")
                except:
                    pass
                if euser.bot:
                    await who_added(self.bot, guild, euser)
                await asyncio.sleep(5)
                await recover_items(self, guild)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        if role.managed: return
        guild = role.guild
        d = {
            'name':role.name,
            'perms':role.permissions,
            'hoist':role.hoist,
            'mentionable':role.mentionable,
            'color':role.colour,
            'ctype': 'role'
        }
        if handle_antinuke(self, guild, 'role_delete', d):
            euser = await audit_user(guild, discord.AuditLogAction.role_delete)
            global wl, default_whitelist
            if not smart_wl(guild, euser, discord.AuditLogAction.role_delete) and euser != guild.owner and not euser.id in default_whitelist:
                try:
                    await messages.nukep(self, euser, "Попытка краша сервера (удаление ролей)")
                except:
                    pass
                if euser.bot:
                    await who_added(self.bot, guild, euser)
                await recover_items(self, guild)
                

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        d = {"ctype": "ban", "target": user}
        if handle_antinuke(self, guild, 'ban', d):
            euser = await audit_user(guild, discord.AuditLogAction.ban)
            global wl, default_whitelist
            if not smart_wl(guild, euser, discord.AuditLogAction.ban) and euser != guild.owner and not euser.id in default_whitelist:
                try:
                    await messages.nukep(self, euser, "Попытка краша сервера (бан участников)")
                except:
                    pass
                if euser.bot:
                    await who_added(self.bot, guild, euser)
                await recover_items(guild, d)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild = member.guild
        async for entry in guild.audit_logs(limit = 1):
            if entry.action == discord.AuditLogAction.kick:
                euser = entry.user
                global wl, default_whitelist
                if not smart_wl(guild, euser, discord.AuditLogAction.kick) and euser != guild.owner and not euser.id in default_whitelist:
                    global times
                    if times < 3:
                        times += 1
                    else:
                        try:
                            await messages.nukep(self, euser, "Попытка краша сервера (кик участников)")
                        except:
                            pass
                        times = 0
                        if euser.bot:
                            await who_added(self.bot, guild, euser)

    # Команды
    @commands.command(aliases=['whitelist'])
    @commands.check(messages.check_perms)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def wl(self, ctx, option, user: typing.Union[discord.User, discord.Role] = None):
        option = option.lower()
        measures.add(what=3)
        global default_whitelist
        if messages.is_admin(ctx.author):
            uuc = f"**{user}**"
            if isinstance(user, discord.Role):
                uuc = user.mention
            if option == 'add':
                if user is not None:
                    if user.id != self.bot.user.id:
                        try: w = cache.whitelist_data[ctx.guild.id]
                        except: w = {}
                        old = w
                        
                        if user.id in default_whitelist:
                            return await messages.err(ctx, "Вы не можете изменить права пользователя из стандартного белого списка.")
                        
                        if isinstance(user, discord.Role):
                            if user == ctx.guild.default_role:
                                return await messages.err(ctx, "Нельзя изменить права роли everyone.")

                        icons = {False: "🚫 Запрещено", True: "✅ Разрешено"}
                        try: perms = w[str(user.id)]
                        except: perms = {
                            "channel_delete": False,
                            "channel_create": False,
                            "role_delete": False,
                            "role_create": False,
                            "role_admin": False,
                            "kick": False,
                            "ban": False,
                            "guild_update": False

                        }
                        if str(user.id) in w and list(perms.values()).count(True) > 0:
                            if isinstance(user, discord.User):
                                label = f"Изменить права **{user}**"
                            else:
                                label = f"Изменить права роли **{user.name}**"
                        else:
                            label = f"Добавить **{user}** в белый список"
                            try:
                                btw = cache.whitelist_data[ctx.guild.id]
                            except KeyError:
                                btw = {}
                            if "_id" in btw:
                                del btw["_id"]
                            if len([m for m in btw if list(btw[m].values()).count(True) > 0]) >= 25 and not messages.has_premium(ctx.guild.id):
                                embed = discord.Embed(title="🙁 | Ой...", description="Кажется, место под записи в белом списке для этого сервера закончилось - максимум 25 штук.", color=Color.blurple)
                                embed.add_field(name="Хочу снять ограничение!", value=f"Приобретите подписку **HiProtect Plus** всего за {Other.premium_cost} руб. навсегда.")
                                embed.set_footer(text=f"Подробнее: {ctx.prefix}plus")
                                return await ctx.send(embed=embed)

                        embed = discord.Embed(color = Color.primary, title = "📝 | " + label)
                        embed.description = "При помощи кнопок ниже (если их нет, обновите Discord) укажите права для этого пользователя/этой роли – что он(-а) может делать, а что – нет.\nЕсли кнопка горит красным, при нажатии на неё, право будет разрешено. Зелёным – запрещено."
                        def list_of_perms():
                            return f'''
**Удаление каналов:** {icons[perms['channel_delete']]}
**Создание каналов:** {icons[perms['channel_create']]}
**Удаление ролей:** {icons[perms['role_delete']]}
**Создание ролей:** {icons[perms['role_create']]}
**Изменение прав ролей:** {icons[perms['role_admin']]}
**Кик:** {icons[perms['kick']]}
**Бан:** {icons[perms['ban']]}
**Изменение информации о сервере:** {icons[perms['guild_update']]}
                            '''
                        embed.add_field(name = "Права", value=list_of_perms())
                        def get_buttons():
                            colors = {True: ButtonStyle.green, False: ButtonStyle.red}
                            buttons = [
                                ActionRow(
                                    Button(style=colors[perms['channel_delete']], label="Удаление каналов", custom_id="channel_delete"),
                                    Button(style=colors[perms['channel_create']], label="Создание каналов", custom_id="channel_create"),
                                    Button(style=colors[perms['role_delete']], label="Удаление ролей", custom_id="role_delete"),
                                    Button(style=colors[perms['role_create']], label="Создание ролей", custom_id="role_create")
                                ),
                                ActionRow(
                                    Button(style=colors[perms['role_admin']], label="Изменение прав ролей", custom_id="role_admin"),
                                    Button(style=colors[perms['kick']], label="Кик", custom_id="kick"),
                                    Button(style=colors[perms['ban']], label="Бан", custom_id="ban"),
                                    Button(style=colors[perms['guild_update']], label="Изменение информации о сервере", custom_id="guild_update")
                                ),
                                ActionRow(
                                    Button(style=ButtonStyle.blurple, label="Все права", custom_id="all"),
                                    Button(style=ButtonStyle.green, label="Готово", custom_id="done")
                                )
                            ]
                            return buttons
                        msg = await ctx.send(embed=embed, components=get_buttons())
                        next = 0
                        def check(inter):
                            return inter.message.id == msg.id and inter.author == ctx.author
                        async def editmsg():
                            embed.clear_fields()
                            embed.add_field(name = "Права", value=list_of_perms())
                            await msg.edit(embed=embed, components=get_buttons())
                        while next < 21:
                            inter = await ctx.wait_for_button_click(check)
                            if inter.author == ctx.author:
                                next += 1
                            if inter.clicked_button.custom_id == "cancel":
                                await msg.delete()
                                
                                w = old
                                
                                del w
                                embed = discord.Embed(title = "🚫 | Отказ", color = Color.danger)
                                embed.description = "Занесение в белый список было отменено."
                                return await ctx.send(embed = embed)
                            if inter.clicked_button.custom_id in list(perms):
                                perms[inter.clicked_button.custom_id] = not perms[inter.clicked_button.custom_id]
                                
                                await editmsg()
                                await inter.create_response(type=6)
                            elif inter.clicked_button.custom_id == "all":
                                perms = dict.fromkeys(perms, True)
                                await editmsg()
                                await inter.create_response(type=6)
                            elif inter.clicked_button.custom_id == "done":
                                await msg.delete()
                                
                                cache.whitelist.add(ctx.guild.id, {str(user.id): perms})
                                embed = discord.Embed(title = "✅ | Готово", color=Color.success)
                                if list(perms.values()).count(True) > 0:
                                    if list(perms.values()).count(True) < 7:
                                        embed.description = f"Теперь {list(perms.values()).count(True)} из 7 действий {uuc} игнорируются."
                                    else:
                                        embed.description = f"Теперь все действия {uuc} игнорируются."
                                else:
                                    embed.description = f"Теперь действия {uuc} не игнорируются, так как все права были запрещены."
                                return await ctx.send(embed = embed)
                        await msg.delete()
                        return await ctx.send("Превышено максимальное количество нажатий (20). Введите команду еще раз.")
                    else:
                        await messages.err(ctx, 'Меня нельзя занести в белый список.', True)
                else:
                    await messages.err(ctx, 'Пожалуйста, укажите пользователя или роль.', True)
            elif option == 'remove':
                if user is not None:
                    if user.id != self.bot.user.id:
                        if not ctx.guild.id in cache.whitelist_data:
                            await messages.err(ctx, 'Такого пользователя/такой роли нет в белом списке.', True)
                        else:
                            w = cache.whitelist_data[ctx.guild.id]
                            try: perms = w[str(user.id)]
                            except: perms = {
                                    "channel_delete": False,
                                    "channel_create": False,
                                    "role_delete": False,
                                    "role_create": False,
                                    "role_admin": False,
                                    "kick": False,
                                    "ban": False,
                                    "guild_update": False
                                }
                            if str(user.id) in w and list(perms.values()).count(True) > 0:
                                cache.whitelist.add(ctx.guild.id, {str(user.id):{
                                    "channel_delete": False,
                                    "channel_create": False,
                                    "role_delete": False,
                                    "role_create": False,
                                    "role_admin": False,
                                    "kick": False,
                                    "ban": False,
                                    "guild_update": False
                                }})
                                embed = discord.Embed(title = '✅ | Готово', color = Color.success)
                                embed.description = f'Теперь действия {uuc} не будут игнорироваться.'
                                await ctx.send(embed=embed)
                            else:
                                await messages.err(ctx, 'Такого пользователя/такой роли нет в белом списке.', True)
                    else:
                        await messages.err(ctx, 'Меня нельзя удалить из белого списка.', True)
                else:
                    await messages.err(ctx, 'Пожалуйста, укажите пользователя или роль.', True)

            elif option == 'list':
                embed = discord.Embed(title="📖 | Белый список", color=Color.primary)
                if not ctx.guild.id in cache.whitelist_data:
                    embed.description = 'Записей нет.'
                else:
                    a, b = 'Для экономии места права были представлены в виде 0 и 1. 1 – разрешено; 0 – запрещено.\nПрава слева направо: удаление каналов, создание каналов, удаление ролей, создание ролей, изменение прав ролей, кик, бан.\n\n', 0
                    w = cache.whitelist_data[ctx.guild.id]
                    if "_id" in w:
                        del w["_id"]
                    numbers = {True: "1", False: "0"}
                    for i in w:
                        us = self.bot.get_user(int(i))
                        r = ctx.guild.get_role(int(i))
                        if r is None: u = us
                        else: u = r
                        if u is not None:
                            if list(w[i].values()).count(True) > 0:
                                perms = "".join(numbers[v] for v in w[i].values())
                                b += 1
                                if r is not None:
                                    a += f'`{b}.` {u.mention} (`ID: {u.id}`) – `{perms}`\n'
                                else:
                                    a += f'`{b}.` {u} (`ID: {u.id}`) – `{perms}`\n'
                    if b == 0:
                        embed.description = 'Записей нет.'
                    else:
                        embed.description = a
                await ctx.send(embed=embed)
            else:
                await messages.err(ctx, 'Опция не найдена.', True)
        else:
            await messages.only_admin(ctx)
            
    @commands.group()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def np(self, ctx):
        if not messages.is_admin(ctx.author):
            return await messages.only_admin(ctx)
        
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(color=Color.primary)
            embed.title = "⚠ | Наказания за краш"
            decode = {
                "ban": "Бан",
                "kick": "Кик",
                "lock": "Блокировка",
                "quarantine": "Карантин"
            }
            try: pu_user = cache.configs_data[ctx.guild.id]['pu-user']
            except: pu_user = {"type": "ban", "duration": 0}

            try: pu_bot = cache.configs_data[ctx.guild.id]['pu-bot']
            except: pu_bot = {"type": "kick", "duration": 0}

            puu = decode[pu_user['type']]
            if pu_user["duration"] > 0: puu += f" на {word.hms(float(pu_user['duration']))}"

            pub = decode[pu_bot['type']]
            if pu_bot["duration"] > 0: pub += f" на {word.hms(float(pu_bot['duration']))}"

            embed.description = "`<обязательный параметр>` `[необязательный параметр]`\n**Не используйте скобочки при указании параметров**"
            embed.add_field(inline=False, name="Команды", value=f"""
`{ctx.prefix}np <bot | user> <наказание> [время]` – Установить наказание
            """)
            embed.add_field(inline=False, name="Расшифровка наказаний", value=f"""
`ban` – Бан (только для пользователей)
`kick` – Кик
`lock` – Блокировка (только для ботов)
`quarantine` – Карантин (то же, что и блокировка, но доступно для всех, и права нельзя вернуть просто так)
            """)
            embed.add_field(inline=False, name="Наказания", value=f"""
**Для бота:** {pub}
**Для пользователя:** {puu}
            """)
            await ctx.send(embed=embed)

    @np.command(aliases=['bot'])
    async def _bot(self, ctx, type, duration="0s"):
        type = type.lower()
        if not type in ['kick', 'lock', 'quarantine', 'qua']:
            return await messages.err(ctx, "Наказание не найдено.")
        
        duration = word.string_to_seconds(duration)

        if type == 'kick': duration = 0

        try: old_pu = cache.configs_data[ctx.guild.id]['pu-bot']
        except: old_pu = {"type": "kick", "duration": 0}

        if type == old_pu['type'] and duration == old_pu['duration']:
            return await messages.err(ctx, "Новое наказание не может совпадать со старым.")
        if type == "qua": type += "rantine"
        decode = {
            "ban": "Бан",
            "kick": "Кик",
            "lock": "Блокировка",
            "quarantine": "Карантин"
        }
        p = decode[type]
        if duration > 0: p += f" на {word.hms(float(duration))}"
        cache.configs.add(ctx.guild.id, {"pu-bot": {"type": type, "duration": duration}})
        embed = discord.Embed(color = Color.success)
        embed.title = "✅ | Готово"
        embed.description = f"Новое наказание за краш для ботов: {p}."
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @np.command(aliases=['user'])
    async def ___user(self, ctx, type, duration="0s"):
        type = type.lower()
        if not type in ['kick', 'ban', 'quarantine', 'qua']:
            return await messages.err(ctx, "Наказание не найдено.")
        
        duration = word.string_to_seconds(duration)

        if type == 'kick': duration = 0

        try: old_pu = cache.configs_data[ctx.guild.id]['pu-user']
        except: old_pu = {"type": "ban", "duration": 0}

        if type == old_pu['type'] and duration == old_pu['duration']:
            return await messages.err(ctx, "Новое наказание не может совпадать со старым.")

        if type == "qua": type += "rantine"
        decode = {
            "ban": "Бан",
            "kick": "Кик",
            "lock": "Блокировка",
            "quarantine": "Карантин"
        }
        p = decode[type]
        if duration > 0: p += f" на {word.hms(float(duration))}"
        cache.configs.add(ctx.guild.id, {"pu-user": {"type": type, "duration": duration}})
        embed = discord.Embed(color = Color.success)
        embed.title = "✅ | Готово"
        embed.description = f"Новое наказание за краш для пользователей: {p}."
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(AntiCrash(bot))
