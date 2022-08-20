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
        "debug":"NzQwNTQwMjA5ODk2MDk1ODY0.GZ8c5r.qajFFH9xJbe2_Y9VFd94lY54Fh9PWox_jbfOFI", #discord bot debug token
        "release": "NzQwNTQwMjA5ODk2MDk1ODY0.GZ8c5r.qajFFH9xJbe2_Y9VFd94lY54Fh9PWox_jbfOFI" #you can enter token from debug
    }
    mongo_auth = {
        "url":"", #mongo db url like "cluster1.free.mongodb.com"
        "username":"", #mongo db username. exmaple "ArtemBay"
        "auth":{
            "debug":"", #mongo db password. looks like random symbols
            "release": "" #same password with debug
        }
    }
    qiwi_auth = "" #https://qiwi.com/p2p-admin/transfers/api

class Other:
    shard_count = 1
    slash = None #dont enable this PLS
    premium_cost = 99 #in rub
    invoice_lifetime = 360 # in minutes
    p2p = None #dont touch this
    uptime = 0
