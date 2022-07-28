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

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['mr'])
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.check(messages.check_perms)
    async def muterole(self, ctx, role: discord.Role = None):
        measures.add(what=10)
        if role is None:
            try:
                mr = ctx.guild.get_role(cache.configs_data[ctx.guild.id]['muterole']).mention
            except:
                mr = 'Не указана'
            embed = discord.Embed(color=Color.primary)
            embed.description = f'Текущая роль мьюта: {mr}.'
            await ctx.send(embed = embed)
        else:
            if role >= ctx.guild.get_member(self.bot.user.id).top_role:
                await messages.err(ctx, "Роль находится не ниже моей.", True)
            elif role.managed:
                await messages.err(ctx, "Роль является интеграцией. Я не смогу выдавать её.", True)
            else:
                cache.configs.add(ctx.guild.id, {'muterole': role.id})
                embed = discord.Embed(color=Color.success)
                embed.title = '✅ | Готово'
                embed.description = f'Роль {role.mention} помечена как мьют-роль.'
                await ctx.send(embed=embed)
                for i in ctx.guild.text_channels:
                    await i.set_permissions(role, send_messages=False, add_reactions=False)
                for i in ctx.guild.voice_channels:
                    await i.set_permissions(role, speak=False)
        
    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def nuker(self, ctx, punishment, t = "0s"):
        measures.add(what=10)
        if messages.is_admin(ctx.author):
            punishments = {
                'none': 'Отсутствует',
                'kick': 'Кик',
                'ban': 'Бан'
            }
            if punishment.lower() in list(punishments) or punishment.lower() == 'show':
                try:
                    p = cache.configs_data[ctx.guild.id]['nuker-type']
                    ti = cache.configs_data[ctx.guild.id]['nuker-time']
                except:
                    p, ti = 'none', 0
                n = {'nuker-type': 'none', 'nuker-time': 0}
                if punishment.lower() == 'show':
                    if ti > 0:
                        await ctx.send(f'⚠ Наказание для пригласившего краш-бота: **{punishments[p]}** на **{word.hms2(ti)}**.')
                    else:
                        await ctx.send(f'⚠ Наказание для пригласившего краш-бота: **{punishments[p]}**.')
                elif punishment.lower() == 'kick':
                    if word.string_to_seconds(t) == 0:
                        n['nuker-type'] = 'kick'
                        await ctx.send('✅ Теперь пригласившего краш-бота ждёт **кик**.')
                    else:
                        await ctx.send('❌ Кик не имеет настройки по времени.')
                elif punishment.lower() == 'ban':
                    n['nuker-type'] = 'ban'
                    n['nuker-time'] = word.string_to_seconds(t)
                    if word.string_to_seconds(t) > 0:
                        blob = f' на **{word.hms2(word.string_to_seconds(t))}**'
                    else:
                        blob = ''
                    await ctx.send(f'✅ Теперь пригласившего краш-бота ждёт **бан**{blob}.')
                elif punishment.lower() == 'none':
                    if word.string_to_seconds(t) == 0:
                        n['nuker-type'] = 'none'
                        await ctx.send('✅ Теперь пригласившего краш-бота ничего не ждёт.')
                    else:
                        await ctx.send('❌ Отсутствие наказания не имеет настройки по времени.')
            else:
                await ctx.send('❌ Неизвестная опция.')
            cache.configs.add(ctx.guild.id, n)
        else:
            await messages.only_admin(ctx)
    
    @commands.command(aliases=['rp', 'pr', 'protectrole', 'roleprotect', 'role-protect'])
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def role_protect(self, ctx, option = None):
        measures.add(what=10)
        if messages.is_admin(ctx.author):
            if not ctx.guild.id in cache.configs_data:
                rp = 0
            else:
                data = cache.configs_data[ctx.guild.id]
                if not 'roleprotect' in data:
                    rp = 0
                else:
                    rp = data['roleprotect']
            if option is None:
                embed = discord.Embed(title = "🛡 | Защита ролей")
                if rp == 0:
                    embed.color = Color.danger
                    embed.description = "Текущее состояние защиты: **Отключена**."
                else:
                    embed.color = Color.success
                    embed.description = "Текущее состояние защиты: **Включена**."
                await ctx.send(embed=embed)
            else:
                option = option.lower()
                if option == 'on':
                    if rp == 0:
                        rp = 75
                        cache.configs.add(ctx.guild.id, {"roleprotect": rp})
                        embed = discord.Embed(color=Color.success)
                        embed.title = "✅ | Готово"
                        embed.description = "Защита ролей была включена."
                        await ctx.send(embed=embed)
                    else:
                        await messages.err(ctx, "Защита ролей уже включена.")
                elif option == 'off':
                    if rp == 75:
                        if ctx.guild.id in cache.configs_data:
                            rp = 0
                            cache.configs.add(ctx.guild.id, {"roleprotect": rp})
                            embed = discord.Embed(color=Color.success)
                            embed.title = "✅ | Готово"
                            embed.description = "Защита ролей была выключена."
                            await ctx.send(embed=embed)
                    else:
                        await messages.err(ctx, "Защита ролей уже выключена.")
                else:
                    await messages.err(ctx, "Неизвестная опция.", True)
        else:
            await messages.only_admin(ctx)

    @commands.group(aliases=['wa', 'warnactions', 'warn-actions'])
    @commands.check(messages.check_perms)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def warn_actions(self, ctx):
        measures.add(what=10)
        if ctx.invoked_subcommand is None:
            wa = {}
            try:
                wa = cache.warns_data[ctx.guild.id]['actions']
            except:
                pass
            p = ctx.prefix
            embed = discord.Embed(color=Color.primary)
            embed.title = "⚠ | Наказания за предупреждения"
            embed.description = f'''
`<обязательный параметр>` `[необязательный параметр]`
**Не используйте скобочки при указании параметров**

`{p}warn_actions set <№ предупр-я> <none | mute | kick | ban> [Длительность]` – Добавить наказание
`{p}warn_actions reset` – Сбросить все наказания
            '''
            if wa != {}:
                w, a = [], []
                actions = {
                    'none':'❌ Ничего',
                    'mute':'🔇 Мьют',
                    'kick':'👢 Кик',
                    'ban':'🔨 Бан'
                }
                for action in wa:
                    ac = wa[action]
                    w.append(f'`{action}` ⚠')
                    if ac['duration'] > 0:
                        a.append(f"{actions[ac['punishment']]} на {word.hms2(float(ac['duration']))}")
                    else:
                        a.append(f"{actions[ac['punishment']]}")
                str_w = '\n'.join(w)
                str_p = '\n'.join(a)
                embed.add_field(name='Предупреждения:', value=str_w)
                embed.add_field(name='Наказания:', value=str_p)
            await ctx.send(embed=embed)

    @warn_actions.command()
    async def set(self, ctx, warn: int, punishment, duration = "0s"):
        punishment = punishment.lower()
        available_actions = ['none', 'mute', 'kick', 'ban']
        converted = word.string_to_seconds(duration)
        if not punishment in available_actions:
            await messages.err(ctx, 'Пожалуйста, укажите одно из следующих действий: `none`, `mute`, `kick` или `ban`.', True)
        elif warn < 1:
            await messages.err(ctx, 'Предупреждение не может быть меньше `1`.', True)
        else:
            if not ctx.guild.id in cache.warns_data:
                w = {"case": 1, "actions": {}, "members": {}}
                cache.warns.add(ctx.guild.id, w)
            else:
                w = cache.warns_data[ctx.guild.id]
            #print(w)
            if not "case" in w:
                w = {"case":1, "members":{}, "actions": {}}
            if not "actions" in w:
                w['actions'] = {}
            if punishment in ['none', 'kick'] and converted > 0:
                converted = 0
            w['actions'][str(warn)] = {'punishment':punishment, 'duration':converted}
            cache.warns.add(ctx.guild.id, w)
            embed = discord.Embed(color=Color.success)
            embed.title = "✅ | Готово"
            embed.description = "Наказание было сохранено."
            await ctx.send(embed=embed)

    @warn_actions.command()
    async def reset(self, ctx):
        if ctx.guild.id in cache.warns_data:
            w = cache.warns_data[ctx.guild.id]
            #print(w)
            if 'actions' in w:
                cache.warns.delete(ctx.guild.id, {'actions': True})
                embed = discord.Embed(color=Color.success)
                embed.title = "✅ | Готово"
                embed.description = "Наказания были сброшены."
                await ctx.send(embed=embed)
            else:
                await messages.err(ctx, 'Наказаний нет.', True)
        else:
            await messages.err(ctx, 'Наказаний нет.', True)

    @commands.command(aliases=['ar'])
    @commands.check(messages.check_perms)
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def antiraid(self, ctx, joins: int = None, interval = None):
        measures.add(what=10)
        if joins is not None and interval is not None:
            t = word.string_to_seconds(interval)
            if joins < 0:
                await messages.err(ctx, "Минимальное значение заходов – **1**.")
            elif t < 0:
                await messages.err(ctx, "Минимальное Длительность для заходов – **1 секунда**.")
            else:
                if joins == 0 and t == 0:
                    turn = 0
                else:
                    turn = 1
                cache.antiraid.add(ctx.guild.id, {"joins": joins, "interval": t, "turn": turn})
                embed = discord.Embed(color = Color.success, title = "✅ | Готово")
                if turn == 0:
                    embed.description = 'Защита от рейдов была выключена.'
                else:
                    embed.description = f'Теперь на сервер можно зайти максимум {joins} {word.word_correct(joins, "раз", "раза", "раз")} за {word.hms(float(t))}.\nЕсли вы хотите отключить защиту от рейдов, напишите `{ctx.prefix}antiraid 0 0`.'
                await ctx.send(embed = embed)
        else:
            try:
                ar = cache.antiraid_data[ctx.guild.id]
                turn = ar['turn']
                j = ar['joins']
                i = ar['interval']
            except:
                turn, j, i = 0, 0, 0

            embed = discord.Embed(title = "✋ | Защита от рейдов", color = Color.primary)
            if turn == 0:
                embed.description = "Защита выключена."
            else:
                embed.description = f'На сервер можно зайти максимум {j} {word.word_correct(j, "раз", "раза", "раз")} за {word.hms(float(i))}.\nЕсли вы хотите отключить защиту от рейдов, напишите `{ctx.prefix}antiraid 0 0`.'
            await ctx.send(embed = embed)

    @commands.group()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def perms(self, ctx):
        if not messages.is_admin(ctx.author):
            return await messages.only_admin(ctx)
        if ctx.invoked_subcommand is None:
            await ctx.send(f"Чтобы узнать больше о команде, напишите `{ctx.prefix}help perms`.")

    @perms.command()
    async def ar(self, ctx, cmd, *, r):
        if cmd != "*":
            cmd = messages.get_command(self.bot, cmd)
            if not cmd:
                return await messages.err(ctx, "Команда не найдена.")
        try:
            alr = cache.perms_data[ctx.guild.id][cmd]["roles"]["allowed"]
        except: alr = []

        try:
            der = cache.perms_data[ctx.guild.id][cmd]["roles"]["denied"]
        except: der = []

        try:
            cc = cache.perms_data[ctx.guild.id][cmd]["channels"]
        except: cc = {}

        r = r.strip("<@&>").replace(">", "").replace("<", "").replace("@", "").replace("&", "")
        if not r.lower() in ["нет", "no", "none"]:
            for i in r.split():
                if ctx.guild.get_role(int(i)):
                    if int(i) in der:
                        der.pop(der.index(int(i)))
                    if not int(i) in alr:
                        alr.append(int(i))
            result = '\n'.join([ctx.guild.get_role(int(a)).mention for a in r.strip("<@&>").replace(">", "").replace("<", "").replace("@", "").replace("&", "").split() if ctx.guild.get_role(int(a))])
        else:
            alr = []

        cache.perms.add(ctx.guild.id, {cmd: {"roles": {"allowed": alr, "denied": der}, "channels": cc}})
        embed = discord.Embed(title="✅ | Готово", color=Color.success)
        if cmd == "*":
            if r.lower() in ["нет", "no", "none"]:
                embed.description = "Вы убрали все разрешённые роли для всех команд"
            else:
                embed.description = f"Вы указали следующие разрешённые роли для всех команд: \n>>> {result}"
        else:
            if r.lower() in ["нет", "no", "none"]:
                embed.description = f"Вы убрали все разрешённые роли для команды `{ctx.prefix}{cmd}`."
            else:
                embed.description = f"Вы указали следующие разрешённые роли для команды `{ctx.prefix}{cmd}`: \n>>> {result}"
        await ctx.send(embed=embed)

    @perms.command()
    async def dr(self, ctx, cmd, *, r):
        if cmd != "*":
            cmd = messages.get_command(self.bot, cmd)
            if not cmd:
                return await messages.err(ctx, "Команда не найдена.")
        try:
            alr = cache.perms_data[ctx.guild.id][cmd]["roles"]["allowed"]
        except: alr = []

        try:
            der = cache.perms_data[ctx.guild.id][cmd]["roles"]["denied"]
        except: der = []

        try:
            cc = cache.perms_data[ctx.guild.id][cmd]["channels"]
        except: cc = {}

        r = r.strip("<@&>").replace(">", "").replace("<", "").replace("@", "").replace("&", "")
        if not r.lower() in ["нет", "no", "none"]:
            for i in r.split():
                if ctx.guild.get_role(int(i)):
                    if int(i) in alr:
                        alr.pop(alr.index(int(i)))
                    if not int(i) in der:
                        der.append(int(i))
            result = '\n'.join([ctx.guild.get_role(int(a)).mention for a in r.strip("<@&>").replace(">", "").replace("<", "").replace("@", "").replace("&", "").split() if ctx.guild.get_role(int(a))])
        else:
            der = []

        cache.perms.add(ctx.guild.id, {cmd: {"roles": {"allowed": alr, "denied": der}, "channels": cc}})
        embed = discord.Embed(title="✅ | Готово", color=Color.success)
        if cmd == "*":
            if r.lower() in ["нет", "no", "none"]:
                embed.description = "Вы убрали все запрещённые роли для всех команд"
            else:
                embed.description = f"Вы указали следующие запрещённые роли для всех команд: \n>>> {result}"
        else:
            if r.lower() in ["нет", "no", "none"]:
                embed.description = f"Вы убрали все запрещённые роли для команды `{ctx.prefix}{cmd}`."
            else:
                embed.description = f"Вы указали следующие запрещённые роли для команды `{ctx.prefix}{cmd}`: \n>>> {result}"
        await ctx.send(embed=embed)

    @perms.command()
    async def ac(self, ctx, cmd, *, r):
        if cmd != "*":
            cmd = messages.get_command(self.bot, cmd)
            if not cmd:
                return await messages.err(ctx, "Команда не найдена.")
        try:
            alr = cache.perms_data[ctx.guild.id][cmd]["channels"]["allowed"]
        except: alr = []

        try:
            der = cache.perms_data[ctx.guild.id][cmd]["channels"]["denied"]
        except: der = []

        try:
            cc = cache.perms_data[ctx.guild.id][cmd]["roles"]
        except: cc = {}

        r = r.strip("<@#>").replace(">", "").replace("<", "").replace("@", "").replace("#", "")
        if not r.lower() in ["нет", "no", "none"]:
            for i in r.split():
                if ctx.guild.get_channel(int(i)):
                    if int(i) in der:
                        der.pop(der.index(int(i)))
                    if not int(i) in alr:
                        alr.append(int(i))
            result = '\n'.join([ctx.guild.get_channel(int(a)).mention for a in r.strip("<@#>").replace(">", "").replace("<", "").replace("@", "").replace("#", "").split() if ctx.guild.get_channel(int(a))])
        else:
            alr = []

        cache.perms.add(ctx.guild.id, {cmd: {"channels": {"allowed": alr, "denied": der}, "roles": cc}})
        embed = discord.Embed(title="✅ | Готово", color=Color.success)
        if cmd == "*":
            if r.lower() in ["нет", "no", "none"]:
                embed.description = "Вы убрали все разрешённые каналы для всех команд"
            else:
                embed.description = f"Вы указали следующие разрешённые каналы для всех команд: \n>>> {result}"
        else:
            if r.lower() in ["нет", "no", "none"]:
                embed.description = f"Вы убрали все разрешённые каналы для команды `{ctx.prefix}{cmd}`."
            else:
                embed.description = f"Вы указали следующие разрешённые каналы для команды `{ctx.prefix}{cmd}`: \n>>> {result}"
        await ctx.send(embed=embed)

    @perms.command()
    async def dc(self, ctx, cmd, *, r):
        if cmd != "*":
            cmd = messages.get_command(self.bot, cmd)
            if not cmd:
                return await messages.err(ctx, "Команда не найдена.")
        try:
            alr = cache.perms_data[ctx.guild.id][cmd]["channels"]["allowed"]
        except: alr = []

        try:
            der = cache.perms_data[ctx.guild.id][cmd]["channels"]["denied"]
        except: der = []

        try:
            cc = cache.perms_data[ctx.guild.id][cmd]["roles"]
        except: cc = {}

        r = r.strip("<@#>").replace(">", "").replace("<", "").replace("@", "").replace("#", "")
        if not r.lower() in ["нет", "no", "none"]:
            for i in r.split():
                if ctx.guild.get_channel(int(i)):
                    if int(i) in alr:
                        alr.pop(alr.index(int(i)))
                    if not int(i) in der:
                        der.append(int(i))
            result = '\n'.join([ctx.guild.get_channel(int(a)).mention for a in r.strip("<@#>").replace(">", "").replace("<", "").replace("@", "").replace("#", "").split() if ctx.guild.get_channel(int(a))])
        else:
            der = []

        cache.perms.add(ctx.guild.id, {cmd: {"channels": {"allowed": alr, "denied": der}, "roles": cc}})
        embed = discord.Embed(title="✅ | Готово", color=Color.success)
        if cmd == "*":
            if r.lower() in ["нет", "no", "none"]:
                embed.description = "Вы убрали все запрещённые каналы для всех команд"
            else:
                embed.description = f"Вы указали следующие запрещённые каналы для всех команд: \n>>> {result}"
        else:
            if r.lower() in ["нет", "no", "none"]:
                embed.description = f"Вы убрали все запрещённые каналы для команды `{ctx.prefix}{cmd}`."
            else:
                embed.description = f"Вы указали следующие запрещённые каналы для команды `{ctx.prefix}{cmd}`: \n>>> {result}"
        await ctx.send(embed=embed)

    @perms.command()
    async def show(self, ctx, cmd):
        if cmd != "*":
            cmd = messages.get_command(self.bot, cmd)
            if not cmd:
                return await messages.err(ctx, "Команда не найдена.")
        try:
            alr = cache.perms_data[ctx.guild.id][cmd]["roles"]["allowed"]
        except: alr = []

        try:
            der = cache.perms_data[ctx.guild.id][cmd]["roles"]["denied"]
        except: der = []

        try:
            alc = cache.perms_data[ctx.guild.id][cmd]["channels"]["allowed"]
        except: alc = []

        try:
            dlc = cache.perms_data[ctx.guild.id][cmd]["channels"]["denied"]
        except: dlc = []

        alr = [a for a in alr if ctx.guild.get_role(a)]
        der = [a for a in der if ctx.guild.get_role(a)]

        alc = [a for a in alc if ctx.guild.get_channel(a)]
        dlc = [a for a in dlc if ctx.guild.get_channel(a)]

        embed = discord.Embed(color=Color.primary)
        if cmd != "*": embed.title = f"👮‍♂️ | Права для команды `{ctx.prefix}{cmd}`"
        else: embed.title = "👮‍♂️ | Права для всех команд"
        if alr == [] and der == [] and alc == [] and dlc == []:
            embed.description = "Всё по умолчанию, никто не ограничивал эту команду."
        else:
            if len(alr) == 0: alr = "Отсутствуют"
            else: alr = '\n'.join([ctx.guild.get_role(a).mention for a in alr])

            if len(der) == 0: der = "Отсутствуют"
            else: der = '\n'.join([ctx.guild.get_role(a).mention for a in der])

            if len(alc) == 0: alc = "Отсутствуют"
            else: alc = '\n'.join([ctx.guild.get_channel(a).mention for a in alc])

            if len(dlc) == 0: dlc = "Отсутствуют"
            else: dlc = '\n'.join([ctx.guild.get_channel(a).mention for a in dlc])

            embed.add_field(inline=False, name="Разрешённые роли", value=f">>> {alr}")
            embed.add_field(inline=False, name="Запрещённые роли", value=f">>> {der}")
            embed.add_field(inline=False, name="Разрешённые каналы", value=f">>> {alc}")
            embed.add_field(inline=False, name="Запрещённые каналы", value=f">>> {dlc}")

        await ctx.send(embed=embed)

    @commands.command(aliases=['ndm', 'notify-dm'])
    @commands.check(messages.check_perms)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def notify_dm(self, ctx, option=None):
        if option:
            option = option.lower()

        try:
            curopt = cache.configs_data[ctx.guild.id]["notify-dm"]
        except KeyError:
            curopt = False

        embed = discord.Embed(title="📣 | Оповещения о наказаниях в личку", color=Color.primary)
        if not option:
            embed.description = f"Я {messages.rebool(curopt, 'оповещаю', 'не оповещаю')} о наказаниях."
            return await ctx.send(embed=embed)

        if option == "on":
            cache.configs.add(ctx.guild.id, {"notify-dm": True})
            embed.title = "✅ | Готово"
            embed.color = Color.success
            embed.description = "Теперь я буду оповещать о наказаниях в личку."
            return await ctx.send(embed=embed)
        if option == "off":
            cache.configs.add(ctx.guild.id, {"notify-dm": False})
            embed.title = "✅ | Готово"
            embed.color = Color.success
            embed.description = "Теперь я не буду оповещать о наказаниях в личку."
            return await ctx.send(embed=embed)
        return await messages.err(ctx, "Опция не найдена!")

    @commands.command()
    @commands.check(messages.check_perms)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def score(self, ctx, option=None, amount: int=None):
        if not option:
            sc = messages.default_scores

            if ctx.guild.id in cache.antinuke_data:
                for i in list(messages.default_scores):
                    if i in cache.antinuke_data[ctx.guild.id]:
                        sc[i] = cache.antinuke_data[ctx.guild.id][i]

            try: max = cache.configs_data[ctx.guild.id]["maxscore"]
            except: max = 20

            embed = discord.Embed(title="🎚️ | Баллы за краш")
            embed.description = f"Используйте команду `{ctx.prefix}help score`, чтобы получить справку о команде."
            embed.color = Color.primary

            embed.add_field(inline=False, name="Текущие значения (баллы)", value=f"""
**Удаление каналов:** {sc['channel_delete']}
**Удаление ролей:** {sc['role_delete']}
**Создание каналов:** {sc['channel_create']}
**Создание ролей:** {sc['role_create']}
**Бан участников:** {sc['ban']}
**Кик участников:** {sc['kick']}
**Изменение сервера:** {sc['guild_update']}

**Максимум:** {max}
            """)
            return await ctx.send(embed=embed)
        elif option.lower() == "help":
            embed = discord.Embed(title="❔ | Справка по фильтрам")
            embed.description = """
`channel_create` – создание каналов
`channel_delete` – удаление каналов
`role_create` – создание ролей
`role_delete` – удаление ролей
`ban` – бан
`kick` - кик
`guild_update` - изменение сервера
`max` – максимум (при превышении этого значения включается анти-краш)
            """
            embed.color = Color.primary
            return await ctx.send(embed=embed)
        
        if not amount:
            return await messages.err(ctx, "Вам следует указать значение.")
        if option.lower() == "max":
            if amount < 10:
                return await messages.err(ctx, "Значение не должно быть меньше 10.")
            if amount > 200:
                return await messages.err(ctx, "Значение не должно быть больше 200.")
            cache.configs.add(ctx.guild.id, {"maxscore": amount})
            embed = discord.Embed()
            embed.title = "✅ | Готово"
            embed.color = Color.success
            embed.description = f"Теперь анти-краш включается при превышении порога в **{amount} {word.word_correct(amount, 'балл', 'балла', 'баллов')}**."
            return await ctx.send(embed=embed)
        elif option.lower().replace("-", "_") in list(messages.default_scores):
            if amount < 0:
                return await messages.err(ctx, "Значение не должно быть меньше 0.")
            if amount > 50:
                return await messages.err(ctx, "Значение не должно быть больше 50.")
            cache.antinuke.add(ctx.guild.id, {option.lower().replace("-", "_"): amount})
            embed = discord.Embed()
            embed.title = "✅ | Готово"
            embed.color = Color.success
            embed.description = f"Теперь за это действие даётся **{amount} {word.word_correct(amount, 'балл', 'балла', 'баллов')}**."
            return await ctx.send(embed=embed)
        else:
            return await messages.err(ctx, "Фильтр не найден. Стоит попробовать ещё раз?")

def setup(bot):
    bot.add_cog(Settings(bot))
