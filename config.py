import os

class Color:
    primary = 0x3EE2B7
    transparent = 0x2F3136
    blurple_old = 0x7289DA
    blurple = 0x5865F2
    danger = 0xE92323
    warning = 0xE9B623
    success = 0x44E923

class Auth:
    discord_auth = {
        "debug": os.getenv("discord_token"), #discord bot debug token
        "release": os.getenv("discord_token") #you can enter token from debug
    }
    mongo_auth = {
        "url": os.getenv("mongo_cluster_url"), #mongo db url like "cluster1.free.mongodb.com"
        "username": os.getenv("mongodb_username"), #mongo db username. exmaple "ArtemBay"
        "auth":{
            "debug": os.getenv("mongodb_password"), #mongo db password. looks like random symbols
            "release": os.getenv("mongodb_password") #same password with debug
        }
    }
    qiwi_auth = os.getenv("qiwi_2p2_token") #https://qiwi.com/p2p-admin/transfers/api

class Other:
    shard_count = 1
    slash = None #dont enable this PLS
    premium_cost = 99 #in rub
    invoice_lifetime = 360 # in minutes
    p2p = None #dont touch this
    uptime = 0
