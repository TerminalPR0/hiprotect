import discord
from discord.ext import commands
from discord.ext.commands.core import cooldown
from dislash.interactions.message_components import ActionRow, Button, ButtonStyle, SelectMenu, SelectOption
from pymongo import settings
from config import Color, Other
import messages
import word
import asyncio
import time
import pytz
import json
from word import ago
import cache
import datetime

cooldowns = {}


async def reset(id, delay):
    global cooldowns
    await asyncio.sleep(delay)
    try: del cooldowns[id]
    except: pass

class Cmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['h', 'helo', 'hwlp'])
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.check(messages.check_perms)
    async def help(self, ctx, category = None):
        if category is None:
            embed = discord.Embed(
                title="📖 | Список команд",
                description=f"`<обязательный параметр>` `[необязательный параметр]`\n**Не используйте скобочки при указании параметров**\n\nИспользуйте `{ctx.prefix}help [команда]` для получения подробной информации о команде",
                color=Color.primary
            )
            embed.add_field(
                name=f"Информация",
                value="`info` `invite` `ping` `server` `user`",
                inline=False
            )
            embed.add_field(
                name=f"Модерация",
                value="`addroles` `ban` `bans` `correct` `correct-all` `kick` `lock-bot` `mute` `mutes` `purge` `quarantine` `remroles` `unban` `unlock-bot` `unmute` `unwarn` `warn` `warns`",
                inline=False
            )
            embed.add_field(
                name=f"Администрация",
                value="`delspamchannels` `delspamroles` `echo` `lock` `massban` `unlock`",
                inline=False
            )
            embed.add_field(
                name=f"Весёлости",
                value="`8ball`",
                inline=False
            )
            embed.add_field(
                name=f"Для владельца сервера",
                value="`alertcrash` `reset-all`",
                inline=False
            )
            embed.add_field(
                name=f"Настройка",
                value="`antiraid` ~~`antiflood`~~ `antiinvite` `muterole` `nickcorrector` `notify-dm` `np` `nuker` `perms` `prefix` `role-protect` `score` `warn-actions` `whitelist`",
                inline=False
            )
            embed.add_field(
                name=f"Роли за реакции",
                value="`addsingle` `delsingle`",
                inline=False
            )
            embed.add_field(
                name=f"Прочее",
                value="`avatar` `backup` `discrim`",
                inline=False
            )
            embed.add_field(
                name=f"Hi Plus",
                value="`invoices` `plus`",
                inline=False
            )
            infoe = discord.Embed(color=Color.primary, title="ℹ | Список команд: Информация", description=f"""
`{ctx.prefix}info` – информация о боте
`{ctx.prefix}invite` – пригласить бота на свой сервер
`{ctx.prefix}ping` – пинг бота
`{ctx.prefix}server` – информация о сервере
`{ctx.prefix}user` – информация о пользователе
            """)
            modere = discord.Embed(color=Color.primary, title="👮‍♂️ | Список команд: Модерация", description=f"""
`{ctx.prefix}addroles` – выдать всем роль
`{ctx.prefix}ban` – забанить пользователя
`{ctx.prefix}bans` – список действующих банов
`{ctx.prefix}correct` – исправить никнейм указанным участникам
`{ctx.prefix}correct-all` – исправить никнейм всем участникам
`{ctx.prefix}kick` – кикнуть участника
`{ctx.prefix}lock-bot` – заблокировать бота
`{ctx.prefix}mute` – замьютить участника
`{ctx.prefix}mutes` – список действующих мьютов
`{ctx.prefix}purge` – очистить чат
`{ctx.prefix}quarantine` – управление карантином
`{ctx.prefix}remroles` – забрать роль у всех участников
`{ctx.prefix}unban` – разбанить пользователя
`{ctx.prefix}unlock-bot` – разблокировать бота
`{ctx.prefix}unmute` – размьютить участника
`{ctx.prefix}unwarn` – снять предупреждение у участника
`{ctx.prefix}warn` – выдать предупреждение участнику
`{ctx.prefix}warns` – посмотреть свои или чужие предупреждения
            """)
            admine = discord.Embed(color=Color.primary, title="🛠 | Список команд: Администрация", description=f"""
`{ctx.prefix}delspamchannels` – удалить каналы с одинаковым названием
`{ctx.prefix}delspamroles` – удалить роли с одинаковым названием
`{ctx.prefix}echo` – сказать что-нибудь от лица бота
`{ctx.prefix}lock` – заблокировать канал
`{ctx.prefix}massban` – забанить сразу несколько пользователей
`{ctx.prefix}unlock` – разблокировать канал
            """)
            fune = discord.Embed(color=Color.primary, title="😃 | Список команд: Весёлости", description=f"""
`{ctx.prefix}8ball` – задать вопрос магическому шару
            """)
            ownere = discord.Embed(color=Color.primary, title="👑 | Список команд: Для владельца сервера", description=f"""
`{ctx.prefix}alertcrash` – снять всех администраторов и модераторов
`{ctx.prefix}reset-all` – сбросить **все** настройки бота
            """)
            settingse = discord.Embed(color=Color.primary, title="⚙ | Список команд: Настройка", description=f"""
`{ctx.prefix}antiraid` – настройка анти-рейда
~~`{ctx.prefix}antiflood` – настройка анти-флуда~~
`{ctx.prefix}antiinvite` – настройка анти-приглашений
`{ctx.prefix}muterole` – указать роль мьюта
`{ctx.prefix}nickcorrector` – корректор никнеймов
`{ctx.prefix}notify-dm` – оповещения о наказаниях в личку
`{ctx.prefix}np` – наказание за краш
`{ctx.prefix}nuker` – наказание за приглашение краш-бота
`{ctx.prefix}perms` – ограничить команду по каналам и ролям
`{ctx.prefix}prefix` – изменить префикс бота
`{ctx.prefix}role-protect` – защита роли участника от изменения прав
`{ctx.prefix}score` – управление баллами за краш
`{ctx.prefix}warn-actions` – наказания за предупреждения
`{ctx.prefix}whitelist` – белый список
            """)
            rre = discord.Embed(color=Color.primary, title="🚩 | Список команд: Роли за реакции", description=f"""
`{ctx.prefix}addsingle` – добавить роль за реакцию
`{ctx.prefix}delsingle` – удалить роль за реакцию
            """)
            othere = discord.Embed(color=Color.primary, title="💾 | Список команд: Прочее", description=f"""
`{ctx.prefix}avatar` – получить аватар пользователя
`{ctx.prefix}backup` – управление резервными копиями сервера
`{ctx.prefix}discrim` – поиск участников с определённым Discord тегом
            """)
            cpplus = discord.Embed(color=Color.primary, title="⭐ | Список команд: Управление подпиской HiProtect Plus", description=f"""
`{ctx.prefix}invoices` – выставленные счета
`{ctx.prefix}plus` – подробнее о подписке
            """)
            selectmenu = SelectMenu(
                custom_id="cmds",
                placeholder="Выберите категорию",
                options=[
                    SelectOption("Информация", "Информационные команды", emoji="ℹ"),
                    SelectOption("Модерация", "Команды модерации", emoji="👮‍♂️"),
                    SelectOption("Администрация", "Команды администраторов", emoji="🛠"),
                    SelectOption("Весёлости", "Команды для веселья", emoji="😃"),
                    SelectOption("Для владельца сервера", "Команды, доступные только владельцу сервера", emoji="👑"),
                    SelectOption("Настройка", "Команды для настройки бота", emoji="⚙"),
                    SelectOption("Роли за реакции", "Команды для ролей за реакции", emoji="🚩"),
                    SelectOption("Прочее", "Прочие команды", emoji="💾"),
                    SelectOption("Hi Plus", "Управление подпиской HiProtect Plus", emoji="⭐")
                ]
            )
            button = ActionRow(
                Button(
                    style=ButtonStyle.red,
                    custom_id="back",
                    label="Назад"
                )
            )
            msg = await ctx.send(embed=embed, components=[selectmenu])
            def check(inter):
                return inter.message.id == msg.id and ctx.author == inter.author
            for i in range(20):
                inter = await msg.wait_for_dropdown(check=check, timeout=300)
                embeds = {
                    "Информация": infoe,
                    "Модерация": modere,
                    "Весёлости": fune,
                    "Для владельца сервера": ownere,
                    "Настройка": settingse,
                    "Прочее": othere,
                    "Роли за реакции": rre,
                    "Администрация": admine,
                    "Hi Plus": cpplus
                }
                await inter.create_response(type=6)
                await msg.edit(embed=embeds[inter.select_menu.selected_options[0].label])
        else:
            cmd = messages.get_command(self.bot, category)
            if not cmd:
                return await ctx.send("Мы обыскали всё вдоль и поперёк, но так и не смогли найти эту команду.")
            with open("json/commandinfo.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            if not cmd in data:
                return await ctx.send("Об этой команде совсем ничего не известно, так как мой ленивый разработчик не добавил информацию о ней. Используйте на свой страх и риск.")
            embed = discord.Embed(title=f"❔ | О команде `{ctx.prefix}{cmd}`", color=Color.primary)
            embed.description = """
`<обязательный параметр>` `[необязательный параметр]`
**Не используйте скобочки при указании параметров**
            """
            embed.add_field(inline=False, name="Описание", value=">>> " + data[cmd]["description"] + ".")
            if len(data[cmd]["args"]):
                embed.add_field(inline=False, name="Параметры", value=">>> " + "\n".join([f"`{a}`" for a in data[cmd]["args"]]))
            if len(data[cmd]["examples"]):
                embed.add_field(inline=False, name="Примеры использования", value=">>> " + "\n".join([f"`{ctx.prefix}{a}`" for a in data[cmd]["examples"]]))
            if len(discord.utils.get(self.bot.commands, name=cmd).aliases):
                embed.add_field(inline=False, name="Алиасы (синонимы)", value=">>> " + ", ".join([f"`{a}`" for a in discord.utils.get(self.bot.commands, name=cmd).aliases]))
            await ctx.send(embed=embed)
    @commands.command()
    @commands.check(messages.check_perms)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def invite(self, ctx):
        embed = discord.Embed(title="🔗 | Ссылки", color=Color.primary)
        embed.description = '''
[🤖 Пригласить бота](https://discord.com/oauth2/authorize?client_id=740540209896095864&scope=applications.commands%20bot&permissions=8)
[❔ Поддержка](https://discord.gg/U4ge8Fup5u)
[🌐 Сайт](https://hiprotect.tk)
        '''
        await ctx.send(embed=embed)
    @commands.command(aliases=['serverinfo', 'server-info', 'server_info', 'si'])
    @commands.check(messages.check_perms)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def server(self, ctx):
        months = {
            1: "января",
            2: "февраля",
            3: "марта",
            4: "апреля",
            5: "мая",
            6: "июня",
            7: "июля",
            8: "августа",
            9: "сентября",
            10: "октября",
            11: "ноября",
            12: "декабря"
        }
        embed = discord.Embed(title=f'🌍 | Информация о сервере **{ctx.guild.name}**', color=Color.primary)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        rgs = {
            'brazil':':flag_br: Бразилия',
            'europe':':flag_eu: Европа',
            'hongkong':':flag_hk: Гонконг',
            'india':':flag_in: Индия',
            'japan':':flag_jp: Япония',
            'russia':':flag_ru: Россия',
            'singapore':':flag_sg: Сингапур',
            'southafrica':':flag_za: ЮАР',
            'sydney':':flag_au: Сидней',
            'us-central':':flag_us: Центральная Америка',
            'us-east':':flag_us: Восточное побережье США',
            'us-south':':flag_us: Америка (Юг)',
            'us-west':':flag_us: Западное побережье США',
            'deprecated':'Убран'
        }
        vlevels = {
            'none':':white_circle: Отсутствует',
            'low':':green_circle: Низкий',
            'medium':':yellow_circle: Средний',
            'high':':orange_circle: Высокий',
            'extreme':':red_circle: Самый высокий'
        }
        embed.add_field(name='Роли', value=f'''
> Всего: **{len(ctx.guild.roles)}**
> С правами администратора: **{len([r for r in ctx.guild.roles if r.permissions.administrator])}**
> С правами модератора: **{len([r for r in ctx.guild.roles if r.permissions.kick_members])}**
> Интеграций: **{len([r for r in ctx.guild.roles if r.managed])}**
        ''')
        embed.add_field(name='Каналы', value=f'''
> Всего: **{len([c for c in ctx.guild.channels if not isinstance(c, discord.CategoryChannel)])}**
> Текстовых: **{len(ctx.guild.text_channels)}**
> Голосовых: **{len(ctx.guild.voice_channels)}**
> Категорий: **{len(ctx.guild.categories)}**
        ''')
        embed.add_field(name='Участники', inline=False, value=f'''
> Всего: **{len(ctx.guild.members)}**
> Людей: **{len([m for m in ctx.guild.members if not m.bot])}**
> Ботов: **{len([m for m in ctx.guild.members if m.bot])}**
> Админов: **{len([m for m in ctx.guild.members if m.guild_permissions.administrator])}**
> Модераторов: **{len([m for m in ctx.guild.members if m.guild_permissions.kick_members])}**
        ''')
        dt = ctx.guild.created_at.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)
        if not ctx.guild.owner:
            oww = "**Не кэширован**"
        else:
            oww = f"**{ctx.guild.owner}** ({ctx.guild.owner.mention})"
        embed.add_field(name='Прочее', value=f'''
> Владелец: {oww}
> Уровень проверки: **{vlevels[str(ctx.guild.verification_level)]}**
> Дата создания сервера: <t:{int(dt.timestamp())}> (<t:{int(dt.timestamp())}:R>)
        ''')
        if messages.has_premium(ctx.guild.id):
            embed.add_field(name="HiProtect Plus активен!", value="Спасибо за поддержку HiProtect :heart:", inline=False)
        embed.set_footer(text=f'ID: {ctx.guild.id} | Шард {ctx.guild.shard_id}')
        await ctx.send(embed=embed)

    @commands.command(aliases=['userinfo', 'user-info', 'user_info', 'u'])
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.check(messages.check_perms)
    async def user(self, ctx, user: discord.User = None):
        months = {
            1: "января",
            2: "февраля",
            3: "марта",
            4: "апреля",
            5: "мая",
            6: "июня",
            7: "июля",
            8: "августа",
            9: "сентября",
            10: "октября",
            11: "ноября",
            12: "декабря"
        }
        if user is None:
            user = ctx.author
        embed = discord.Embed(color=Color.primary)
        if user.bot:
            embed.title = f"🤖 | Информация о боте **{user}**"
        else:
            embed.title = f"👤 | Информация о пользователе **{user}**"
        embed.set_thumbnail(url=user.avatar_url)
        embed.set_footer(text=f'ID: {user.id}')
        if ctx.guild.get_member(user.id):
            user = ctx.guild.get_member(user.id)
            if user.bot:
                try:
                    dob_id = int(cache.invited_data[ctx.guild.id][str(user.id)])
                    dob_u = self.bot.get_user(dob_id)
                    if dob_u:
                        embed.add_field(name="Кто добавил", value=dob_u, inline=False)
                except:
                    pass
            embed.add_field(inline=False, name="Роли", value=f'Всего: **{len(user.roles)}**, наивысшая: {user.top_role.mention}')
            if user == ctx.guild.owner:
                embed.add_field(inline=True, name="Владелец сервера?", value='✅ Да')
            else:
                embed.add_field(inline=True, name="Владелец сервера?", value='❌ Нет')
                if user.guild_permissions.administrator:
                    embed.add_field(inline=True, name="Администратор?", value='✅ Да')
                else:
                    embed.add_field(inline=True, name="Администратор?", value='❌ Нет')
            ja = user.joined_at.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)
            embed.add_field(inline=False, name="Дата присоединения к серверу", value=f'<t:{int(ja.timestamp())}> (<t:{int(ja.timestamp())}:R>)')
        ca = user.created_at
        embed.add_field(inline=False, name="Дата создания аккаунта", value=f'<t:{int(ca.timestamp())}> (<t:{int(ca.timestamp())}:R>)')
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.check(messages.check_perms)
    async def prefix(self, ctx, prefix):
        if prefix.lower() in ["reset", "сброс", "hi."]:
            if ctx.guild.id in cache.configs_data:
                if "prefix" in cache.configs_data[ctx.guild.id]:
                    cache.configs.delete(ctx.guild.id, {"prefix": True})
                    await ctx.send(embed = discord.Embed(
                        title="✅ | Готово",
                        description="Префикс успешно сброшен.",
                        color=Color.success
                    ))
                else:
                    await messages.err(ctx, "Префикс и так стоит по умолчанию.", True)
            else:
                await messages.err(ctx, "Префикс и так стоит по умолчанию.", True)
        else:
            if len(prefix) > 6:
                await messages.err(ctx, "Максимальная длина префикса — **6**.", True)
            else:
                cache.configs.add(ctx.guild.id, {"prefix": prefix})
                await ctx.send(embed = discord.Embed(
                    title="✅ | Готово",
                    description=f"Новый префикс — `{prefix}`.",
                    color=Color.success
                ))

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            if message.content.startswith(f'<@{self.bot.user.id}>') or message.content.startswith(f'<@!{self.bot.user.id}>'):
                try:
                    prefix = cache.configs_data[message.guild.id]['prefix']
                except:
                    prefix = 'hi.'
                await message.channel.send(f'{message.author.mention}, мой префикс – `{prefix}`. Для просмотра списка команд введи `{prefix}help`.')

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.check(messages.check_perms)
    async def info(self, ctx):
        if Other.uptime == 0:
            uptime2 = 0
        else:
            uptime2 = int(time.time()) - Other.uptime
        embed = discord.Embed(title="ℹ | Информация", description="Привет! Я – анти-краш бот, который защищает сервера от краша.", color=Color.primary)
        embed.add_field(
            name="Система",
            inline=False,
            value=f'''
🛰 Средняя задержка бота: **{int(self.bot.latency * 1000)} мс**
⏳ Аптайм: **{word.hms(uptime2)}**
🖥 Шардов: **{len(self.bot.shards)}**
🆔 ID шарда этого сервера: **{ctx.guild.shard_id}**
💬 Команд выполнено: **{cache.botstats_data[self.bot.user.id]["commands_completed"]}**
            '''
        )
        embed.add_field(
            name="Серверы",
            inline=False,
            value=f'''
🌐 Количество: **{len(self.bot.guilds)}**
🏆 Крупных серверов (1000+): **{len([g for g in self.bot.guilds if g.member_count >= 1000])}**
👥 Пользователей: **{len(self.bot.users)}**
            '''
        )
        embed.add_field(
            name="Прочее",
            inline=False,
            value=f'''
📆 Дата создания: **10 мая 2022 года**
🐍 Версия Python: **3.10**
📄 Версия: **1.4 (13 мая 2022 года)**
👨‍💻 Разработчики: **Artem Bay#0547**, **самсунг ассистент#0205**
            '''
        )
        embed.add_field(
            name="Ссылки",
            inline=False,
            value=f'''
[Пригласить бота](https://discord.com/oauth2/authorize?client_id=740540209896095864&scope=applications.commands%20bot&permissions=8)
[Сервер поддержки](https://discord.gg/U4ge8Fup5u)
[Сайт бота](https://www.hiprotect.tk/)
            '''
        )
        embed.add_field(
            name="Благодарность",
            inline=False,
            value=f'''
**Cymon#4380** - за оригинальный код бота и аватарку боту. Жалко краш протекта
            '''
        )
        embed.set_footer(text="© 2022, Artem Bay | Все права защищены ботом HiProtect", icon_url=self.bot.get_user(356737308898099201).avatar_url)
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.check(messages.check_perms)
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def ping(self, ctx):
        embed = discord.Embed(title="🏓 | Понг!", description=f'Средняя задержка: **{int(self.bot.latency * 1000)} мс**', color=Color.primary)
        embed.add_field(inline=False, name="По шардам:", value=f'''
Шард **0**: **{int(self.bot.get_shard(0).latency) * 1000}мс**
Шард **1**: **None мс**
Шард **2**: **None мс**
Шард **3**: **None мс**
Шард **4**: **None мс**
Шард **5**: **None мс**
Шард **6**: **None мс**
Шард **7**: **None мс**
        ''')
        embed.set_footer(text=f'ID вашего шарда: {ctx.guild.shard_id}')
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(
                title="⏳ | Команда перезаряжается",
                description=f'Попробуйте снова через **{word.hms2(error.retry_after)}**.',
                color=Color.primary
            )
            await ctx.send(embed=embed)
        elif isinstance(error, commands.MissingRequiredArgument):
            await messages.err(ctx, f"В команде указано слишком мало аргументов. Если вы хотите посмотреть подробную справку о команде, напишите `{ctx.prefix}help {ctx.command.name}`.", True)
        elif isinstance(error, commands.CommandInvokeError):
            pass
        elif isinstance(error, messages.HasNoRoles):
            embed = discord.Embed(title="✋ | Недостаточно прав")
            embed.color = Color.danger
            embed.add_field(name="Вам нужно иметь хотя бы одну из этих ролей:", value=f'>>> {str(error)}')
            await ctx.send(embed=embed)
        elif isinstance(error, messages.HasDeniedRoles):
            embed = discord.Embed(title="✋ | Недостаточно прав")
            embed.color = Color.danger
            embed.add_field(name="Данная роль препятствует выполнению команды:", value=f'>>> {str(error)}')
            await ctx.send(embed=embed)
        elif isinstance(error, messages.NotAllowedChannel):
            embed = discord.Embed(title="❌ | Не тот канал")
            embed.color = Color.danger
            embed.add_field(name="Команду можно выполнить только в этих каналах:", value=f'>>> {str(error)}')
            await ctx.send(embed=embed)
        elif isinstance(error, messages.DeniedChannel):
            embed = discord.Embed(title="❌ | Не тот канал")
            embed.color = Color.danger
            embed.description = "Команду нельзя выполнить в этом канале."
            await ctx.send(embed=embed)
        elif isinstance(error, messages.NoPerms):
            embed = discord.Embed(title="✋ | Недостаточно прав")
            embed.color = Color.danger
            embed.add_field(name="Вы должны иметь следующее право:", value=f'>>> {str(error)}')
            await ctx.send(embed=embed)
        elif isinstance(error, commands.MemberNotFound):
            await messages.err(ctx, "Такой участник не найден.", True)
        elif isinstance(error, commands.UserNotFound):
            await messages.err(ctx, "Такой пользователь не найден.", True)
        elif isinstance(error, commands.ChannelNotFound):
            await messages.err(ctx, "Такой канал не найден.", True)
        elif isinstance(error, commands.RoleNotFound):
            await messages.err(ctx, "Такая роль не найдена.", True)
        elif isinstance(error, commands.BadArgument) or isinstance(error, commands.BadUnionArgument):
            await messages.err(ctx, "Указан неправильный аргумент при написании команды.", True)
        elif isinstance(error, commands.CommandNotFound):
            pass
        else:
            raise error

def setup(bot):
    bot.add_cog(Cmd(bot))
