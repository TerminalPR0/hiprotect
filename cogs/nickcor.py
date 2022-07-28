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
from word import ago
from discord.utils import get
from profilactic import measures

async def checknick(member):
    allowed = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 '
    norm = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    bold = '𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐱𝐲𝐳𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗'
    italic = '𝘈𝘉𝘊𝘋𝘌𝘍𝘎𝘏𝘐𝘑𝘒𝘓𝘔𝘕𝘖𝘗𝘘𝘙𝘚𝘛𝘜𝘝𝘞𝘟𝘠𝘡𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻'
    struck = '𝔸𝔹ℂ𝔻𝔼𝔽𝔾ℍ𝕀𝕁𝕂𝕃𝕄ℕ𝕆ℙℚℝ𝕊𝕋𝕌𝕍𝕎𝕏𝕐ℤ𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕟𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫𝟘𝟙𝟚𝟛𝟜𝟝𝟞𝟟𝟠𝟡'
    old = '𝕬𝕭𝕮𝕯𝕰𝕱𝕲𝕳𝕴𝕵𝕶𝕷𝕸𝕹𝕺𝕻𝕼𝕽𝕾𝕿𝖀𝖁𝖂𝖃𝖄𝖅𝖆𝖇𝖈𝖉𝖊𝖋𝖌𝖍𝖎𝖏𝖐𝖑𝖒𝖓𝖔𝖕𝖖𝖗𝖘𝖙𝖚𝖛𝖜𝖝𝖞𝖟𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗'
    squares = '🅰🅱🅲🅳🅴🅵🅶🅷🅸🅹🅺🅻🅼🅽🅾🅿🆀🆁🆂🆃🆄🆅🆆🆇🆈🆉🅰🅱🅲🅳🅴🅵🅶🅷🅸🅹🅺🅻🅼🅽🅾🅿🆀🆁🆂🆃🆄🆅🆆🆇🆈🆉𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗'
    circles = 'ⒶⒷⒸⒹⒺⒻⒼⒽⒾⒿⓀⓁⓂⓃⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏⓐⓑⓒⓓⓔⓕⓖⓗⓘⓙⓚⓛⓜⓝⓞⓟⓠⓡⓢⓣⓤⓥⓦⓧⓨⓩ0①②③④⑤⑥⑦⑧⑨'
    japanese = '卂乃匚ᗪ乇千Ꮆ卄丨ﾌҜㄥ爪几ㄖ卩Ɋ尺丂ㄒㄩᐯ山乂ㄚ乙卂乃匚ᗪ乇千Ꮆ卄丨ﾌҜㄥ爪几ㄖ卩Ɋ尺丂ㄒㄩᐯ山乂ㄚ乙'
    aest = 'ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ０１２３４５６７８９'
    ancient = 'ꍏꌃꉓꀸꍟꎇꁅꃅꀤꀭꀘ꒒ꎭꈤꂦᖘꆰꋪꌗ꓄ꀎᐯꅏꊼꌩꁴꍏꌃꉓꀸꍟꎇꁅꃅꀤꀭꀘ꒒ꎭꈤꂦᖘꆰꋪꌗ꓄ꀎᐯꅏꊼꌩꁴ0123456789'
    circles2 = '🅐🅑🅒🅓🅔🅕🅖🅗🅘🅙🅚🅛🅜🅝🅞🅟🅠🅡🅢🅣🅤🅥🅦🅧🅨🅩🅐🅑🅒🅓🅔🅕🅖🅗🅘🅙🅚🅛🅜🅝🅞🅟🅠🅡🅢🅣🅤🅥🅦🅧🅨🅩⓿❶❷❸❹❺❻❼❽❾'
    script = '𝓐𝓑𝓒𝓓𝓔𝓕𝓖𝓗𝓘𝓙𝓚𝓛𝓜𝓝𝓞𝓟𝓠𝓡𝓢𝓣𝓤𝓥𝓦𝓧𝓨𝓩𝓪𝓫𝓬𝓭𝓮𝓯𝓰𝓱𝓲𝓳𝓴𝓵𝓶𝓷𝓸𝓹𝓺𝓻𝓼𝓽𝓾𝓿𝔀𝔁𝔂𝔃0123456789'
    currency = '₳฿₵ĐɆ₣₲ⱧłJ₭Ⱡ₥₦Ø₱QⱤ₴₮ɄV₩ӾɎⱫ₳฿₵ĐɆ₣₲ⱧłJ₭Ⱡ₥₦Ø₱QⱤ₴₮ɄV₩ӾɎⱫ0123456789'
    dline = 'A͟͟͟͞͞͞B͟͟͟͞͞͞C͟͟͟͞͞͞D͟͟͟͞͞͞E͟͟͟͞͞͞F͟͟͟͞͞͞G͟͟͟͞͞͞H͟͟͟͞͞͞I͟͟͟͞͞͞J͟͟͟͞͞͞K͟͟͟͞͞͞L͟͟͟͞͞͞M͟͟͟͞͞͞N͟͟͟͞͞͞O͟͟͟͞͞͞P͟͟͟͞͞͞Q͟͟͟͞͞͞R͟͟͟͞͞͞S͟͟͟͞͞͞T͟͟͟͞͞͞U͟͟͟͞͞͞V͟͟͟͞͞͞W͟͟͟͞͞͞X͟͟͟͞͞͞Y͟͟͟͞͞͞Z͟͟͟͞͞͞a͟͟͟͞͞͞b͟͟͟͞͞͞c͟͟͟͞͞͞d͟͟͟͞͞͞e͟͟͟͞͞͞f͟͟͟͞͞͞g͟͟͟͞͞͞h͟͟͟͞͞͞i͟͟͟͞͞͞j͟͟͟͞͞͞k͟͟͟͞͞͞l͟͟͟͞͞͞m͟͟͟͞͞͞n͟͟͟͞͞͞o͟͟͟͞͞͞p͟͟͟͞͞͞q͟͟͟͞͞͞r͟͟͟͞͞͞s͟͟͟͞͞͞t͟͟͟͞͞͞u͟͟͟͞͞͞v͟͟͟͞͞͞w͟͟͟͞͞͞x͟͟͟͞͞͞y͟͟͟͞͞͞z͟͟͟͞͞͞0͟͟͟͞͞͞1͟͟͟͞͞͞2͟͟͟͞͞͞3͟͟͟͞͞͞4͟͟͟͞͞͞5͟͟͟͞͞͞6͟͟͟͞͞͞7͟͟͟͞͞͞8͟͟͟͞͞͞9͟͟͟͞͞͞'
    curves = 'ᗩᗷᑕᗪEᖴGᕼIᒍKᒪᗰᑎOᑭᑫᖇSTᑌᐯᗯ᙭YZᗩᗷᑕᗪEᖴGᕼIᒍKᒪᗰᑎOᑭᑫᖇSTᑌᐯᗯ᙭YZ0123456789'
    monospace = '𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿'
    small = 'ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ0123456789'
    nick = member.display_name
    for symbol in member.display_name:
        if not symbol.upper() in allowed and symbol != '!' and symbol != "ǃ":
            if symbol in bold:
                nick = nick.replace(symbol, norm[bold.index(symbol)])
            if symbol in italic:
                nick = nick.replace(symbol, norm[italic.index(symbol)])
            if symbol in struck:
                nick = nick.replace(symbol, norm[struck.index(symbol)])
            if symbol in old:
                nick = nick.replace(symbol, norm[old.index(symbol)])
            if symbol in squares:
                nick = nick.replace(symbol, norm[squares.index(symbol)])
            if symbol in circles:
                nick = nick.replace(symbol, norm[circles.index(symbol)])
            if symbol in japanese:
                nick = nick.replace(symbol, norm[japanese.index(symbol)])
            if symbol in aest:
                nick = nick.replace(symbol, norm[aest.index(symbol)])
            if symbol in ancient:
                nick = nick.replace(symbol, norm[ancient.index(symbol)])
            if symbol in circles2:
                nick = nick.replace(symbol, norm[circles2.index(symbol)])
            if symbol in script:
                nick = nick.replace(symbol, norm[script.index(symbol)])
            if symbol in currency:
                nick = nick.replace(symbol, norm[currency.index(symbol)])
            if symbol in dline:
                nick = nick.replace(symbol, norm[dline.index(symbol)])
            if symbol in curves:
                nick = nick.replace(symbol, norm[curves.index(symbol)])
            if symbol in monospace:
                nick = nick.replace(symbol, norm[monospace.index(symbol)])
            if symbol in small:
                nick = nick.replace(symbol, norm[small.index(symbol)])
            nick = nick.replace(symbol, '')
    nick = nick.replace('!', 'ǃ')
    if len(nick.strip(' ')) == 0:
        nick = "Name"
    await member.edit(nick=nick)


def checknc(guild):
    measures.add(what = 4)
    if not guild.id in cache.configs_data:
        return False
    else:
        w = cache.configs_data[guild.id]
        try:
            return w['nickcor']
        except:
            return False

class NickCorrector(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['nickcorr', 'nickcor', 'nc'])
    @commands.check(messages.check_perms)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def nickcorrector(self, ctx, option = None):
        a = checknc(ctx.guild)
        if option is None:
            embed = discord.Embed(color = Color.primary)
            embed.title = "📝 | Корректор никнеймов"
            if a:
                embed.description = "Корректор никнеймов сейчас включён."
            else:
                embed.description = "Корректор никнеймов сейчас выключен."
            await ctx.send(embed = embed)
        else:
            option = option.lower()
            if option == 'on':
                if not a:
                    cache.configs.add(ctx.guild.id, {"nickcor": True})
                    embed = discord.Embed(title = '✅ | Готово', color = Color.success)
                    embed.description = 'Теперь я буду исправлять никнеймы пользователей.'
                    await ctx.send(embed=embed)
                else:
                    await messages.err(ctx, "Корректор никнеймов уже включён.")
            elif option == 'off':
                if a:
                    cache.configs.add(ctx.guild.id, {"nickcor": False})
                    embed = discord.Embed(title = '✅ | Готово', color = Color.success)
                    embed.description = 'Теперь я не буду исправлять никнеймы пользователей.'
                    await ctx.send(embed=embed)
                else:
                    await messages.err(ctx, "Корректор никнеймов уже выключен.")
            else:
                await messages.err(ctx, "Неизвестная опция.", True)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if checknc(member.guild) and not member.bot:
            await checknick(member)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.display_name != after.display_name:
            async for e in after.guild.audit_logs(limit = 1):
                if e.action == discord.AuditLogAction.member_update:
                    if e.user != self.bot.user and not e.user.bot and not e.user.guild_permissions.administrator and not after.bot:
                        if checknc(after.guild):
                            await checknick(after)

    @commands.command()
    @commands.check(messages.check_perms)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def correct(self, ctx, members: commands.Greedy[discord.Member]):
        corrected = 0
        with ctx.channel.typing():
            for member in members:
                if member.top_role < ctx.author.top_role and member.top_role < ctx.guild.get_member(self.bot.user.id).top_role:
                    try:
                        await checknick(member)
                        corrected += 1
                    except discord.Forbidden:
                        pass
        embed = discord.Embed()
        if corrected > 0:
            embed.title = "✅ | Готово"
            embed.description = f"Изменено никнеймов: **{corrected}** из **{len(members)}**."
            embed.color = Color.success
        else:
            embed.title = "❌ | Не получилось"
            embed.description = "Я не смог изменить никнеймы пользователей."
            embed.color = Color.danger
        await ctx.send(embed = embed)

    @commands.command(aliases=['ca', 'c-a', 'correctall', 'call', 'correct-all'])
    @commands.check(messages.check_perms)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def correct_all(self, ctx):
        corrected = 0
        with ctx.channel.typing():
            for member in ctx.guild.members:
                if member.top_role < ctx.author.top_role and member.top_role < ctx.guild.get_member(self.bot.user.id).top_role and not member.bot:
                    try:
                        await checknick(member)
                        corrected += 1
                    except discord.Forbidden:
                        pass
        embed = discord.Embed()
        if corrected > 0:
            embed.title = "✅ | Готово"
            embed.description = f"Изменено никнеймов: **{corrected}**."
            embed.color = Color.success
        else:
            embed.title = "❌ | Не получилось"
            embed.description = "Я не смог изменить никнеймы пользователей."
            embed.color = Color.danger
        await ctx.send(embed = embed)

def setup(bot):
    bot.add_cog(NickCorrector(bot))
