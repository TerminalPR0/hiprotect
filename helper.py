import cache

async def is_owner(ctx):
    if not ctx.author.id in [356737308898099201, 685837803413962806]:
        await ctx.send("This command is only available to bot owners!")
        return False
    return True

def get_bonus_data(user_id, nostr=False):
    d = {
        "balance": 0.0,
        "pay-period": 0,
        "guilds": [],
    }
    if not nostr:
        d["strbal"] = "0.00"
    if not user_id in cache.bonus_data:
        return d

    data = cache.bonus_data[user_id]
    print(cache.bonus_data)

    if "balance" in data:
        d["balance"] = data["balance"]
    if "pay-period" in data:
        d["pay-period"] = data["pay-period"]
    if "guilds" in data:
        d["guilds"] = data["guilds"]
    if not nostr:
        d["strbal"] = "{:.2f}".format(d["balance"])

    return d