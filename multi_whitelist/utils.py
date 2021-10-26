from mcdreforged.api.command import *
from mcdreforged.api.rtext import *
from mcdreforged.api.types import *

from multi_whitelist.resources import *


def tr(key, *args) -> str:
    return ServerInterface.get_instance().tr(f"{plugin}.{key}", *args)


def help_formatter(mcdr_prefix, command, first_msg, click_msg, use_command=None):
    if use_command is None:
        use_command = command
    msg = f'{mcdr_prefix} {command} §a{first_msg}§r'
    return rtext_cmd(msg, f'{tr("click_msg")} {click_msg}', f'{mcdr_prefix} {use_command}')


def rtext_cmd(txt, click_msg, cmd):
    return RText(txt).h(click_msg).c(RAction.run_command, cmd)


def permission_check(src: CommandSource, cmd):
    if src.get_permission_level() >= permission[cmd]:
        return True
    else:
        return False


def fox_literal(msg):
    return Literal(msg).requires(lambda src: permission_check(src, msg))
