import discord
from discord import permissions
from discord.ext import commands
import word
import messages
import time
import typing
import cache
from config import Color
import punishments
from config import Other
from dislash.slash_commands import *
from dislash.interactions import *

slash = Other.slash

class Quarantine(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=["q", "qua"])
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.check(messages.check_perms)
    async def quarantine(self, ctx):
        if ctx.invoked_subcommand is None:
            try: data = cache.quarantine_data[ctx.guild.id]
            except: data = {}

            try: role = ctx.guild.get_role(data['role']).mention
            except: role = "Не указана"

            embed = discord.Embed()
            embed.title = "☣ | Карантин"
            p = ctx.prefix
            embed.description = f'''
`<обязательный параметр>` `[необязательный параметр]`
**Не используйте скобочки при указании параметров**

`{p}quarantine add <@пользователь>` – Закрыть пользователя на карантин
`{p}quarantine remove <@пользователь>` – Удалить пользователя из карантина
`{p}quarantine role <@роль>` – Указать карантинную роль
`{p}quarantine user <@пользователь>` – Посмотреть информацию о пользователе
`{p}quarantine users` – Полный список пользователей на карантине

**Вы также можете закрывать на карантин ботов.**
            '''
            embed.color = Color.primary
            embed.add_field(name = "Карантинная роль", value = role)
            await ctx.send(embed=embed)

    @quarantine.command(aliases=['role'])
    async def __role(self, ctx, role: discord.Role):
        try: old_role = cache.quarantine_data[ctx.guild.id]['role']
        except: old_role = 0

        if role.id == old_role:
            return await messages.err(ctx, "Новая роль не может совпадать со старой.")

        await role.edit(permissions=discord.Permissions.none())
        cache.quarantine.add(ctx.guild.id, {"role": role.id})
        embed = discord.Embed()
        embed.title = "✅ | Готово"
        embed.description = f"Роль {role.mention} помечена как карантинная."
        embed.color = Color.success
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @quarantine.command()
    async def add(self, ctx, user: discord.User, time1: typing.Optional[str] = '0s', *, reason = None):
        if messages.is_admin(ctx.author):
            member = ctx.guild.get_member(user.id)
            if user == ctx.author:
                return await messages.err(ctx, "Вы не можете закрыть на карантин себя.")
            elif user == self.bot.user:
                return await messages.err(ctx, "Вы не можете закрыть на карантин меня.")
            if member:
                user = member
                if user.top_role >= ctx.author.top_role:
                    return await messages.err(ctx, "Вы не можете закрыть на карантин пользователя, роль которого не ниже вашей.")

            try: data = cache.quarantine_data[ctx.guild.id]
            except: data = {}

            if str(user.id) in data:
                return await messages.err(ctx, "Пользователь уже находится на карантине.")

            if word.ishs(time1):
                tc = word.string_to_seconds(time1)
            else:
                tc = 0
                if reason is not None:
                    reason = time1 + ' ' + reason
                else:
                    reason = time1

            if reason is None:
                reason1 = 'Не указана'
            else:
                reason1 = reason

            await punishments.add_qua(ctx.guild, ctx.author, user, tc, reason1)
            embed = discord.Embed()
            embed.color = Color.warning
            embed.title = "☣ | Карантин"
            embed.description = f'''
**Пользователь:** {user} ({user.mention})
**Администратор:** {ctx.author} ({ctx.author.mention})
**Причина:** {reason1}
'''
            if tc > 0:
                embed.description += f'''
**Длительность:** {word.hms(float(tc))}
**На карантине до:** <t:{int(time.time()) + tc}:f>'''
            await ctx.send(embed=embed)
        else:
            await messages.only_admin(ctx)

    @quarantine.command(aliases=['rem', 'delete'])
    async def remove(self, ctx, user: discord.User):
        if messages.is_admin(ctx.author):
            member = ctx.guild.get_member(user.id)
            if user == ctx.author:
                return await messages.err(ctx, "Вы не можете удалить из карантина себя.")
            elif user == self.bot.user:
                return await messages.err(ctx, "Вы не можете удалить из карантина меня.")
            if member:
                user = member
                if user.top_role >= ctx.author.top_role:
                    return await messages.err(ctx, "Вы не можете удалить из карантина пользователя, роль которого не ниже вашей.")

            try: data = cache.quarantine_data[ctx.guild.id]
            except: data = {}

            if not str(user.id) in data:
                return await messages.err(ctx, "Пользователь не находится на карантине.")

            await punishments.rem_qua(ctx.guild, user.id)
            embed = discord.Embed()
            embed.color = Color.success
            embed.title = "☣ | Удаление из карантина"
            embed.description = f'''
**Пользователь:** {user} ({user.mention})
**Администратор:** {ctx.author} ({ctx.author.mention})
'''
            await ctx.send(embed=embed)
        else:
            await messages.only_admin(ctx)

    @quarantine.command(aliases=['us'])
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.has_permissions(view_audit_log = True)
    async def users(self, ctx):
        pages = [{}]
        total = 0
        index = 0

        if ctx.guild.id in cache.quarantine_data:
            bd = cache.quarantine_data[ctx.guild.id]
            if "_id" in bd: del bd['_id']
        else:
            bd = {}

        for ban in bd:
            if ban.isdigit():
                user = self.bot.get_user(int(ban))
                u2 = user
                if user:
                    if len(pages[-1]) > 10:
                        pages.append({})
                    pages[-1][str(user)] = bd[ban]
                    total += 1

        embed = discord.Embed(title = "☣ | Сидящие на карантине", color = Color.primary)
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        if not total:
            embed.description = "Никого нет :)"
            return await ctx.send(embed=embed)

        embed.title += f" ({total})"

        def refresh_buttons():
            if len(pages) > 1:
                buttons = [
                    ActionRow(
                        Button(
                            style=ButtonStyle.blurple,
                            custom_id="back",
                            emoji="<:back2:873132612850425876>",
                            disabled=index==0
                        ),
                        Button(
                            style=ButtonStyle.blurple,
                            custom_id="forward",
                            emoji="<:forward2:873132612938502164>",
                            disabled=index==len(pages) - 1
                        ),
                        Button(
                            style=ButtonStyle.red,
                            custom_id="close",
                            emoji="<:close2:873131831657111572>"
                        )
                    )
                ]
            else:
                    buttons = [
                    ActionRow(
                        Button(
                            style=ButtonStyle.red,
                            custom_id="close",
                            emoji="<:close2:873131831657111572>"
                        )
                    )
                ]
            return buttons

        def refresh_embed():
            embed.clear_fields()
            embed.set_footer(text=f"{ctx.author} | Страница {index+1} из {len(pages)}", icon_url=ctx.author.avatar_url)
            for user in pages[index]:
                if u2:
                    embed.add_field(name=user, value=f"> `{ctx.prefix}quarantine user {u2.id}`", inline=False)

        refresh_embed()
        msg = await ctx.send(embed = embed, components=refresh_buttons())
        async def refresh_all():
            refresh_embed()
            await msg.edit(embed=embed, components=refresh_buttons())
        
        def check(inter):
            return inter.message.id == msg.id

        while time.time() < time.time() + 600:
            inter = await ctx.wait_for_button_click(check)
            if inter.author != ctx.author:
                await inter.reply("403 Forbidden", ephemeral=True)
            else:
                if inter.clicked_button.custom_id == "begin":
                    index = 0
                    await refresh_all()
                    await inter.create_response(type=6)
                elif inter.clicked_button.custom_id == "back":
                    index -= 1
                    await refresh_all()
                    await inter.create_response(type=6)
                if inter.clicked_button.custom_id == "forward":
                    index += 1
                    await refresh_all()
                    await inter.create_response(type=6)
                if inter.clicked_button.custom_id == "end":
                    index = len(pages) - 1
                    await refresh_all()
                    await inter.create_response(type=6)
                if inter.clicked_button.custom_id == "close":
                    break

        await msg.delete()

    @quarantine.command(aliases=['u'])
    @commands.has_permissions(view_audit_log = True)
    async def user(self, ctx, user: discord.User):
        try: qua = cache.quarantine_data[ctx.guild.id]
        except: qua = {}

        if not str(user.id) in qua:
            return await messages.err(ctx, f"**{user}** не сидит на карантине.")
        
        data = qua[str(user.id)]
        embed = discord.Embed()
        embed.title = "👤 | Пользователь на карантине"
        if user.bot: embed.title = "🤖 | Бот на карантине"
        
        embed.color = Color.primary
        embed.set_thumbnail(url=user.avatar_url)
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)

        if data['end'] >= 1800000000: end = "лучших времен :)"
        else: end = f"<t:{data['end']}:f> (<t:{data['end']}:R>)"

        if self.bot.get_user(data['orderly']): orderly = f"{self.bot.get_user(data['orderly'])}"
        else: orderly = '???'

        if ctx.guild.get_member(data['orderly']): orderly += f" ({self.bot.get_user(data['orderly']).mention})"

        embed.description = f'''
**Дата занесения:** <t:{data['begin']}:f> (<t:{data['begin']}:R>)
**На карантине до:** {end}
**Администратор:** {orderly}
**Причина:** {data['reason']}
        '''
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.roles != after.roles:
            if after.guild.id in cache.quarantine_data:
                data = cache.quarantine_data[after.guild.id]
                if str(after.id) in data:
                    roles = []
                    for r in after.roles:
                        if not r in before.roles:
                            roles.append(r)
                    for r in roles:
                        if r.permissions.view_audit_log or r.permissions.kick_members:
                            await after.remove_roles(r)
                    if after.guild.get_role(data['role']):
                        if not after.guild.get_role(data['role']) in after.roles:
                            await after.add_roles(after.guild.get_role(data['role']))
                    
                    

def setup(bot):
    bot.add_cog(Quarantine(bot))