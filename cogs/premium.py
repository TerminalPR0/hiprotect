import discord
from discord.ext import commands
from dislash.interactions.message_components import ActionRow, Button, ButtonStyle, SelectMenu, SelectOption
from config import Color, Other, Auth
from pyqiwip2p import QiwiP2P
import word
import messages
import cache
import time
from pycbrf.toolbox import ExchangeRates

p2p = Other.p2p

class Premium(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['premium', 'bonus'])
    @commands.cooldown(1, 20, commands.BucketType.guild)
    async def plus(self, ctx):
        #msg = await ctx.send("Получение информации о курсе валют...")
        #er = ExchangeRates()
        #cost = int(er['USD'].value * 2)
        cost = Other.premium_cost
        embed = discord.Embed()
        embed.title = '⭐ | Немного о HiProtect Plus'
        embed.description = f'''
        Если вы хотите поддержать проект или разблокировать доступ к некоторым функциям, самое время приобрести HiProtect Plus для сервера.
Это можно сделать для любого сервера всего за **{cost} {word.word_correct(cost, 'рубль', 'рубля', 'рублей')}**.
Платить каждый месяц не придётся - платёж пока что одноразовый.
Деньги пойдут на оплату хостинга для бота, чтобы он продолжал защищать ваш прекрасный сервер.
        '''
        embed.color = Color.blurple
        embed.add_field(name='Что даёт HiProtect Plus?', value='''
Так как мы активно работаем над ботом, список привилегий будет пополняться.

- Снятие ограничения белого списка в 25 записей
- Роль "Купил HiPlus" на дискорд сервере бота. (Роль выдается только создателю сервера)
        ''')
        row = ActionRow(
            Button(
                style=ButtonStyle.green,
                label="Купить HiProtect Plus для этого сервера",
                custom_id="buy"
            )
        )

        msg = await ctx.send(content=None, embed=embed, components=[row])
        on_click = msg.create_click_listener(timeout=300)

        @on_click.not_from_user(ctx.author, cancel_others=True, reset_timeout=True)
        async def on_wrong_user(inter):
            await inter.reply("Тихо! Не лезь в чужое! Лучше сам напиши команду.", ephemeral=True)

        @on_click.matching_id("buy")
        async def on_buy_click(inter):
            embed2 = discord.Embed()
            embed2.color = Color.warning
            embed2.title = "⚠️ | Внимание!"
            embed2.description = f"Сейчас вам будет выставлен счёт на сумму {cost} руб. Оплата производится через платёжную систему QIWI. Пожалуйста, убедитесь, что я могу отправлять вам личные сообщения. После нажмите кнопку \"Выставить счёт\"."
            row2 = ActionRow(
                Button(
                        style=ButtonStyle.green,
                        label="Выставить счёт",
                        custom_id="bill"
                    ),
                Button(
                        style=ButtonStyle.red,
                        label="Ой, я передумал",
                        custom_id="cancel"
                    )
                )
            await msg.edit(embed=embed2, components=[row2])
            await inter.create_response(type=6)

        @on_click.matching_id("bill")
        async def on_bill_click(inter):
            await inter.create_response(type=6)
            await msg.delete()
            if messages.has_premium(inter.guild.id):
                return await messages.err(ctx, "На этом сервере уже активирован HiProtect Plus.")
            
            invoices = cache.invoices_data
            if inter.guild.id in invoices:
                if invoices[inter.guild.id]['paid'] or int(time.time()) < invoices[inter.guild.id]['expires']:
                    return await messages.err(ctx, f"На этот сервер уже был выставлен счёт. Когда он просрочится, а его не оплатят (<t:{invoices[inter.guild.id]['expires']}:R>), вы сможете повторить попытку.")
            try:
                message = await inter.author.send("Пожалуйста, подождите. Идёт выставление счёта...")
            except:
                return await messages.err(ctx, "Не удалось отправить сообщение. Откройте ЛС и повторите попытку.")
            try:
                invoice_id = len(list(invoices))
                comment = f"Покупка HiProtect Plus для сервера {inter.guild.name} (ID: {inter.guild.id})"
                bill = p2p.bill(amount=cost, lifetime=Other.invoice_lifetime, comment=comment)
                cache.invoices.add(inter.guild.id, {
                    'bill_id': bill.bill_id,
                    'author': inter.author.id,
                    'invoice_id': invoice_id,
                    'expires': int(time.time()) + Other.invoice_lifetime * 60,
                    'message': [message.channel.id, message.id],
                    'paid': False
                    })
                embed3 = discord.Embed()
                embed3.title = "⏳ | Счёт ждёт оплаты"
                embed3.description = f"Вам был выставлен счёт на сумму {cost} руб. Он действует **6 часов** с момента создания. Для перехода на страницу оплаты нажмите на кнопку ниже.\n"
                embed3.description += "HiProtect Plus активируется в течение двух минут с момента оплаты."
                embed3.color = Color.warning
                row3 = ActionRow(
                    Button(
                        style=ButtonStyle.link,
                        label="Оплатить",
                        url=bill.pay_url
                    )
                )
                await message.edit(content=None, embed=embed3, components=[row3])

            except:
                await message.edit(content="Упс, что-то пошло не так. Повторите попытку позже.")

        @on_click.matching_id("cancel")
        async def on_cancel_click(inter):
            return await msg.delete()

        @on_click.timeout
        async def on_timeout():
            await msg.edit(components=[])

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def invoices(self, ctx):
        invoices = cache.invoices_data
        a = []
        for i in invoices:
            if invoices[i]['author'] == ctx.author.id:
                status = "Ожидает оплаты"
                if invoices[i]["paid"]:
                    status = "Оплачен"
                elif int(time.time()) > invoices[i]["expires"]:
                    status = "Просрочен"
                a.append(f"ID счёта: {invoices[i]['invoice_id']} | ID сервера: {i} | Статус: {status}")
                embed = discord.Embed(title="💳 | Выставленные счета", color=Color.primary)
                embed.description = '\n'.join(a)
        if len(a) == 0:
            embed = discord.Embed(title="💳 | Выставленные счета", color=Color.primary)
            embed.description = "Упс, счетов нет :("
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Premium(bot))