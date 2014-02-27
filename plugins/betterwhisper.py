#===========================================================
#   BetterWhisper
#   Author: FZFalzar of Brutus.SG Starbound
#   Version: v0.2 - py3
#   Description: A better whisper plugin with reply and SocialSpy
#===========================================================
import asyncio
from base_plugin import SimpleCommandPlugin, command
from plugins.player_manager import Admin, Guest, Owner

__author__ = "FZFalzar"


class BetterWhisper(SimpleCommandPlugin):
    name = "BetterWhisper"
    depends = ['player_manager']
    auto_activate = True

    def activate(self):
        super().activate()
        self.player_manager = self.plugins['player_manager']
        self.reply_history = dict()
        self.sspy_enabled_dict = dict()

    @command("whisper", "w", role=Guest, doc="Sends a message to target player", syntax=("[name]", "[msg]"))
    def whisper(self, data, protocol):
        """Sends a message to target player. Syntax: /whisper [player name] [msg]"""
        if len(data) == 0:
            raise SyntaxWarning
        try:
            target_name = data[0]
            message = " ".join(data[1:])
            yield from self.send_whisper(target_name, message, protocol)
            return
        except:
            raise SyntaxWarning

    @command("reply", "r", role=Guest, doc="Replies to last player who whispered you", syntax="[msg]")
    def reply(self, data, protocol):
        """Replies to last player who whispered you. Syntax: /r [msg]"""
        if len(data) == 0:
            raise SyntaxWarning

        #retrieve your own history, using your name as key
        try:
            target = self.reply_history[protocol.player.name]
            yield from self.send_whisper(target, " ".join(data), protocol)
        except:
            yield from protocol.send_message("You have no one to reply to!")

    @asyncio.coroutine
    def send_whisper(self, target_name, message, protocol):
        target_player = self.player_manager.get_player_by_name(target_name, True)
        if target_player is None:
            yield from protocol.send_message("Couldn't send a message to %s" % target_name)
            return
        else:
            #show yourself the message
            str_msgto = "[To: %s^#00FF00;] %s" % (target_name,
                                                  message)
            yield from protocol.send_message(str_msgto)

            #show target the message
            target_protocol = target_player.protocol
            str_msgfrom = "[From: %s^#00FF00;] %s" % (target_protocol.player.name,
                                                      message)
            yield from protocol.send_message(str_msgfrom)

            self.logger.info("[%s] Message to %s from %s: %s" % (self.name,
                                                                 target_name,
                                                                 protocol.player.name,
                                                                 message))

            #store your last sent history, so the other player can reply
            #store your name using your target's name as key, so he can use his name to find you
            self.reply_history[target_name] = protocol.player.name

            #send message to people with socialspy on
            for key, value in self.sspy_enabled_dict.items():
                sspy_player = self.player_manager.get_player_by_name(key, True)
                if sspy_player is not None:
                    if sspy_player.protocol.player.check_role(Admin) and value:
                        yield from sspy_player.protocol.send_message("^#00FFFF;[SS] [^#00FF00;%s -> %s^#00FF00;] %s" %
                                                                     (protocol.player.name,
                                                                     target_name,
                                                                     message))

    @command("socialspy", role=Admin, doc="Enables the viewing of messages sent by other players")
    def socialspy(self, data, protocol):
        try:
            if protocol.player.name in self.sspy_enabled_dict.keys():
                self.sspy_enabled_dict[protocol.player.name] = not self.sspy_enabled_dict[protocol.player.name]
            else:
                self.sspy_enabled_dict[protocol.player.name] = True
            yield from protocol.send_message("SocialSpy Enabled: %s" % self.sspy_enabled_dict[protocol.player.name])
            self.logger.info("[%s] %s toggled SocialSpy: %s" % (self.name,
                                                                protocol.player.name,
                                                                self.sspy_enabled_dict[protocol.player.name]))
        except:
            raise KeyError
