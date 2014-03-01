import asyncio
import random
from base_plugin import SimpleCommandPlugin
from utilities import Command
from plugins.player_manager import Owner

__author__ = 'FZFalzar'

class ServerAds(SimpleCommandPlugin):
    name = "ServerAds"
    #depends = ["player_manager"]

    #activate is main entry point for plugin
    def activate(self):
        super().activate()
        self.load_config()
        self.prevMsgIdx = 0
        self.rNum = 0
        self.broadcast = asyncio.Task(self.broadcast_thread())

    @asyncio.coroutine
    def broadcast_thread(self):
        while True:
            yield from asyncio.sleep(self.interval)
            #make sure we do not re-broadcast the last message, for variety
            if len(self.serverads_list) > 1:
                while self.rNum == self.prevMsgIdx:
                    #randomly pick from the array
                    self.rNum = random.randint(0, len(self.serverads_list) - 1)
                    #override previous index
                self.prevMsgIdx = self.rNum
                print("[%s] %s %s" % (self.name, self.serverads_prefix, self.serverads_list[self.rNum]))
                yield from self.factory.broadcast("%s ^#00FF00;%s" % (self.serverads_prefix, self.serverads_list[self.rNum]))
            elif len(self.serverads_list) <= 1:
                print("[%s] %s %s" % (self.name, self.serverads_prefix, self.serverads_list[0]))
                yield from self.factory.broadcast("%s ^#00FF00;%s" % (self.serverads_prefix, self.serverads_list[0]))

    @Command("ads_interval", role=Owner, doc="Sets interval for display of serverads", syntax=("[interval]",))
    def ads_interval(self, data, protocol):
        """Sets interval for display of serverads. Syntax: /ads_interval [duration in seconds]"""
        if len(data) == 0:
            yield from protocol.send_message(self.ads_interval.__doc__)
            yield from protocol.send_message("Current interval: %s seconds" % self.interval)
            return
        num = data[0]
        try:
            self.interval = int(num)
            yield from self.save_config()
            yield from protocol.send_message("Interval set -> %s seconds" % self.interval)
        except:
            yield from protocol.send_message("Invalid input! %s" % num)
            yield from protocol.send_message(self.ads_interval.__doc__)
            return

    @Command("ads_reload", role=Owner, doc="Reloads configuration values")
    def ads_reload(self, data, protocol):
        """Reloads configuration values. Syntax: /ads_reload"""
        yield from self.load_config()
        yield from protocol.send_message("ServerAds reloaded!")


#===============================================================================
    def load_config(self):
        try:
            self.serverads_list = self.config.config.serverads['serverads_list']
            self.serverads_prefix = self.config.config.serverads['serverads_prefix']
            self.interval = self.config.config.serverads['serverads_interval']
            self.logger.info("Configuration loaded")
            print("[%s] Configuration loaded successfully" % self.name)
        except Exception as e:
            self.logger.warning("Configuration failed to load! Error: %s" % e)
            print("[%s] Error occured! %s" % (self.name, "Failed to load config values!"))
            self.serverads_list = ["Welcome to the server!", "Have a nice stay!"]
            self.serverads_prefix = "[SA]"
            self.interval = 30

    @asyncio.coroutine
    def save_config(self):
        self.config.config.serverads['serverads_list'] = self.serverads_list
        self.config.config.serverads['serverads_prefix'] = self.serverads_prefix
        self.config.config.serverads['serverads_interval'] = self.interval
        self.config.save_config()
        print("[%s] Configuration saved successfully" % self.name)