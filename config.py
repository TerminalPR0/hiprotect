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
        "debug":"NzQwNTQwMjA5ODk2MDk1ODY0.GZ8c5r.qajFFH9xJbe2_Y9VFd94lY54Fh9PWox_jbfOFI",
        "release": "NzQwNTQwMjA5ODk2MDk1ODY0.GZ8c5r.qajFFH9xJbe2_Y9VFd94lY54Fh9PWox_jbfOFI"
    }
    mongo_auth = {
        "url":"",
        "username":"",
        "auth":{
            "debug":"",
            "release": ""
        }
    }
    qiwi_auth = ""

class Other:
    shard_count = 1
    slash = None
    premium_cost = 99
    invoice_lifetime = 360 # в минутах
    p2p = None
    uptime = 0
