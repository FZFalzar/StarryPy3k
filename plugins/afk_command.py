#===========================================================
#   afk_plugin
#   Author: FZFalzar of Brutus.SG Starbound
#   Version: v0.2 - py3
#   Description: Simple AFK command with configurable messages
#===========================================================
import asyncio
from base_plugin import SimpleCommandPlugin
from utilities import Command
from plugins.player_manager import Guest

__author__ = "FZFalzar"

class AFKCommand(SimpleCommandPlugin):
    name = "AFKCommand"
    auto_activate = True
    afk_list = dict()

    def activate(self):
        super().activate()
        self.load_config()

    def load_config(self):
        try:
            self.afk_message = self.config.config.afk["afk_msg"]
            self.afkreturn_message = self.config.config.afk["afkreturn_msg"]
            self.logger.info("Configuration loaded")
            print("[%s] Configuration loaded successfully" % self.name)
        except Exception as e:
            self.logger.info("Configuration failed to load! Error: %s" % e)
            self.afk_message = "^gray;is now AFK."
            self.afkreturn_message = "^gray;has returned."

    @Command("afk", role=Guest, doc="Marks/unmarks your status as Away From Keyboard (AFK)")
    def afk(self, data, protocol):
        """ Marks a user as AFK (Away From Keyboard) Syntax: /afk"""
        if protocol.player.name in self.afk_list:
            if self.afk_list[protocol.player.name] == True:
                yield from self.unset_afk_status(protocol.player.name)
            else:
                yield from self.set_afk_status(protocol.player.name)
        else:
            yield from self.set_afk_status(protocol.player.name)

    @asyncio.coroutine
    def set_afk_status(self, name):
        if name in self.afk_list:
            if self.afk_list[name] == False:
                #self.factory.broadcast("%s %s" % (self.player_manager.get_by_name(name).colored_name(self.config.colors), self.afk_message))
                yield from self.factory.broadcast("%s %s" % (name, self.afk_message))
                self.afk_list[name] = True
        else:
            self.afk_list[name] = True
            yield from self.factory.broadcast("%s %s" % (name, self.afk_message))
            yield from self.set_afk_status(name)

    @asyncio.coroutine
    def unset_afk_status(self, name):
        if name in self.afk_list:
            if self.afk_list[name] == True:
                #self.factory.broadcast("%s %s" % (self.player_manager.get_by_name(name).colored_name(self.config.colors), self.afkreturn_message))
                yield from self.factory.broadcast("%s %s" % (name, self.afkreturn_message))
                self.afk_list[name] = False
        else:
            self.afk_list[name] = False
            yield from self.factory.broadcast("%s %s" % (name, self.afkreturn_message))
            yield from self.unset_afk_status(name)

    #if player disconnects, remove him from list!
    #def on_client_disconnect(self, player):
    #def on_client_disconnect(self, data, protocol):
    #    asyncio.Task(self.unset_afk_status(protocol.player.name))
    #    self.afk_list.pop(protocol.player.name, None)

    #if player does any of these, unmark him from afk!
    #def on_chat_sent(self, data, protocol):
    #    asyncio.Task(self.unset_afk_status(protocol.player.name))

    #def on_entity_create(self, data, protocol):
    #    asyncio.Task(self.unset_afk_status(protocol.player.name))

    #def on_entity_interact(self, data, protocol):
    #    asyncio.Task(self.unset_afk_status(protocol.player.name))
