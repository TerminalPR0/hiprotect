from mongo import db

class Collection:
    def __init__(self, collection):
        self.collection = db[collection]
        print(collection, "loaded")
        self.cached = {}

    def add(self, id, data):
        idict = {"_id": id}
        self.collection.update_one(idict, {"$set": data}, upsert=True)
        if not id in self.cached:
            self.cached[id] = {}
        for i in data:
            self.cached[id][i] = data[i]

    def remove(self, id):
        idict = {"_id": id}
        self.collection.delete_one(idict)
        del self.cached[id]

    def delete(self, id, data):
        idict = {"_id": id}
        self.collection.update_one(idict, {"$unset": data})
        for i in data:
            del self.cached[id][i]

    def load_data(self):
        results = self.collection.find({})
        for res in results:
            self.cached[res["_id"]] = res
        return self.cached


configs = Collection(collection = "config")
configs_data = configs.load_data()

antiflood = Collection(collection = "antiflood")
antiflood_data = antiflood.load_data()

antiinvite = Collection(collection = "antiinvite")
antiinvite_data = antiinvite.load_data()

antiraid = Collection(collection = "antiraid")
antiraid_data = antiraid.load_data()

bans = Collection(collection = "bans")
bans_data = bans.load_data()

locks = Collection(collection = "locks")
locks_data = locks.load_data()

mutes = Collection(collection = "mutes")
mutes_data = mutes.load_data()

warns = Collection(collection = "warns")
warns_data = warns.load_data()

invited = Collection(collection = "invited")
invited_data = invited.load_data()

perms = Collection(collection = "perms")
perms_data = perms.load_data()

rr = Collection(collection = "rr-new")
rr_data = rr.load_data()

whitelist = Collection(collection = "whitelist")
whitelist_data = whitelist.load_data()

quarantine = Collection(collection = "quarantine")
quarantine_data = quarantine.load_data()

bl = Collection(collection = "bot-bl")
bl_data = bl.load_data()

logs = Collection(collection = "logs")
logs_data = logs.load_data()

bonus = Collection(collection = "bonus")
bonus_data = bonus.load_data()

antinuke = Collection(collection = "antinuke")
antinuke_data = antinuke.load_data()

botstats = Collection(collection = "bot_stats")
botstats_data = botstats.load_data()

premium = Collection(collection = "premium")
premium_data = premium.load_data()

invoices = Collection(collection = "invoices")
invoices_data = invoices.load_data()

allowed = Collection(collection = "allowed")
allowed_data = allowed.load_data()