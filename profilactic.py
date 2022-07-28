import time

class meass:
    def __init__(self):
        self.links = 0
        self.backups = 0
        self.add_bot = 0
        self.antiraid = 0
        self.nickcorr = 0
        self.rr = 0
        self.anticrash = 0
        self.automod = 0
        self.invite = 0
        self.bot_invite = 0
        self.settings = 0
        self.begin = time.time()

    def add(self, what):
        define = {
            0: self.links,
            1: self.backups,
            2: self.add_bot,
            3: self.antiraid,
            4: self.nickcorr,
            5: self.rr,
            6: self.anticrash,
            7: self.automod,
            8: self.invite,
            9: self.bot_invite,
            10: self.settings
        }
        define[what] += 1
        #print(what, define[what])

    def begin_time(self):
        return int(time.time() - self.begin)

measures = meass()