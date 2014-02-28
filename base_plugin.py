import asyncio

from utilities import DotDict


class BaseMeta(type):
    def __new__(mcs, name, bases, clsdict):
        for key, value in clsdict.items():
            if callable(value) and (
                        value.__name__.startswith("on_") or hasattr(value,
                                                                    "_command")):
                clsdict[key] = asyncio.coroutine(value)
        c = type.__new__(mcs, name, bases, clsdict)
        return c


class BasePlugin(metaclass=BaseMeta):
    """
    Defines an interface for all plugins to inherit from. Note that the __init__
    method should generally not be overrode; all setup work should be done in
    activate() if possible. If you do override __init__, remember to super()!
    
    Note that only one instance of each plugin will be instantiated for *all*
    connected clients. self.protocol will be changed by the plugin manager to
    the current protocol.
    
    You may access the factory if necessary via self.factory.protocols
    to access other clients, but this "Is Not A Very Good Idea" (tm)

    `name` *must* be defined in child classes or else the plugin manager will
    complain quite thoroughly.
    """

    name = "Base Plugin"
    description = "The common class for all plugins to inherit from."
    version = ".1"
    depends = ()
    plugins = DotDict({})
    auto_activate = True

    def __init__(self):
        self.loop = asyncio.get_event_loop()

    def activate(self):
        pass

    def deactivate(self):
        pass


    def on_protocol_version(self, data, protocol):
        return True


    def on_server_disconnect(self, data, protocol):
        return True


    def on_handshake_challenge(self, data, protocol):
        return True


    def on_chat_received(self, data, protocol):
        return True


    def on_universe_time_update(self, data, protocol):
        return True


    def on_handshake_response(self, data, protocol):
        return True


    def on_client_context_update(self, data, protocol):
        return True


    def on_world_start(self, data, protocol):
        return True


    def on_world_stop(self, data, protocol):
        return True


    def on_tile_array_update(self, data, protocol):
        return True


    def on_tile_update(self, data, protocol):
        return True


    def on_tile_liquid_update(self, data, protocol):
        return True


    def on_tile_damage_update(self, data, protocol):
        return True


    def on_tile_modification_failure(self, data, protocol):
        return True


    def on_give_item(self, data, protocol):
        return True


    def on_swap_in_container_result(self, data, protocol):
        return True


    def on_environment_update(self, data, protocol):
        return True


    def on_entity_interact_result(self, data, protocol):
        return True


    def on_modify_tile_list(self, data, protocol):
        return True


    def on_damage_tile(self, data, protocol):
        return True


    def on_damage_tile_group(self, data, protocol):
        return True


    def on_request_drop(self, data, protocol):
        return True


    def on_spawn_entity(self, data, protocol):
        return True


    def on_entity_interact(self, data, protocol):
        return True


    def on_connect_wire(self, data, protocol):
        return True


    def on_disconnect_all_wires(self, data, protocol):
        return True


    def on_open_container(self, data, protocol):
        return True


    def on_close_container(self, data, protocol):
        return True


    def on_swap_in_container(self, data, protocol):
        return True


    def on_item_apply_in_container(self, data, protocol):
        return True


    def on_start_crafting_in_container(self, data, protocol):
        return True


    def on_stop_crafting_in_container(self, data, protocol):
        return True


    def on_burn_container(self, data, protocol):
        return True


    def on_clear_container(self, data, protocol):
        return True


    def on_world_update(self, data, protocol):
        return True


    def on_entity_create(self, data, protocol):
        return True


    def on_entity_update(self, data, protocol):
        return True


    def on_entity_destroy(self, data, protocol):
        return True


    def on_status_effect_request(self, data, protocol):
        return True


    def on_update_world_properties(self, data, protocol):
        return True


    def on_heartbeat(self, data, protocol):
        return True


    def on_connect_response(self, data, protocol):
        return True


    def on_chat_sent(self, data, protocol):
        return True


    def on_damage_notification(self, data, protocol):
        return True


    def on_client_connect(self, data, protocol):
        return True


    def on_client_disconnect(self, data, protocol):
        return True


    def on_warp_command(self, data, protocol):
        return True

    def __repr__(self):
        return "<Plugin instance: %s (version %s)>" % (self.name, self.version)


class CommandNameError(Exception):
    """
    Raised when a command name can't be found from the `commands` list in a
    `SimpleCommandPlugin` instance.
    """


def command(*aliases, role=None, roles=None, doc=None, syntax=None):
    rs = roles
    r = role
    if isinstance(syntax, str):
        syntax = (syntax,)
    if rs is None:
        rs = set()
    elif not isinstance(roles, set):
        rs = {x for x in rs}
    if role is not None:
        rs.add(r)
    rs = {x.__name__ for x in rs}

    def wrapper(f):
        def wrapped(self, data, protocol):
            try:
                for z in rs:
                    if z not in protocol.player.roles:
                        raise PermissionError
                if syntax is None:
                    f.syntax = ""
                else:
                    f.syntax = " ".join(syntax)
                f.__doc__ = doc
                return f(self, data, protocol)
            except PermissionError:
                asyncio.Task(protocol.send_message(
                    "You don't have permissions to do that."))

        wrapped._command = True
        wrapped._aliases = aliases
        wrapped.__doc__ = doc
        wrapped.roles = rs
        if syntax is None:
            wrapped.syntax = ""
        else:
            wrapped.syntax = " ".join(syntax)
        return wrapped

    return wrapper


class SimpleCommandPlugin(BasePlugin):
    name = "simple_command_plugin"
    description = "Provides a simple parent class to define chat commands."
    version = "0.1"
    depends = ["command_dispatcher"]
    auto_activate = True

    def activate(self):
        super().activate()
        for name, attr in [(x, getattr(self, x)) for x in self.__dir__()]:
            if hasattr(attr, "_command"):
                for alias in attr._aliases:
                    self.plugins['command_dispatcher'].register(attr, alias)


class MetaRole(type):
    roles = {}

    def __new__(mcs, name, bases, clsdict):
        if name in mcs.roles:
            return mcs.roles[name]
        clsdict['roles'] = set()
        clsdict['superroles'] = set()
        print("Adding role", name)
        c = type.__new__(mcs, name, bases, clsdict)
        if name != "Role":
            for b in c.mro()[1:]:
                if issubclass(b, Role) and b is not Role:
                    print("Adding", name, "to", b.__name__)
                    b.roles.add(c)
                    c.superroles.add(b)
        mcs.roles[name] = c
        return c


class Role(metaclass=MetaRole):
    is_meta = False