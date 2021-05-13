# coding: utf8
import json
import os
import shutil

from mcdreforged.api.rcon import *
from mcdreforged.api.types import *
from mcdreforged.api.command import *
from mcdreforged.api.rtext import *
from mcdreforged.api.decorator import new_thread


PLUGIN_METADATA = {
    'id': 'multi_whitelist',
    'version': '2.4.1-cn',
    'name': 'multi_whitelist',
    'description': 'A plugin can control whitelist with multi servers.',
    'author': 'ricky',
    'link': 'https://github.com/rickyhoho/multi_whitelist',
    'dependencies': {
        'mcdreforged': '>=1.3.0'
    }
}


permission = {
    "help" : 1,
    "list" : 1,
    "reload" : 1,
    "add" : 2,
    "del" : 2,
    "addall" : 2,
    "delall" : 2,
    "sync" : 2,
    "on" : 3,
    "off" : 3,
}


plugin = 'multi_whitelist'
prefix = '!!whitelist'
prefix1 = '!!wlist'

path = 'config/' + plugin + '.json'
server_path = 'server/'
local_path = server_path + 'whitelist.json'
 
last_player = 'test'
target_player = 'test'
server_listen = 0
to_server = 0
disable_multi_server = False

systemreturn = '''§b[§rMulti_Whitelist§b] §r'''
error = systemreturn + '''§cError: '''
error_unknown_command = error + '''未知命令§r
输入 §7!!whitelist help§r 获取更多资讯'''
error_syntax = error + '''格式错误
输入 §7!!whitelist help§r 获取更多资讯'''
error_permission = error + '你没有权限使用此指令'
help = '''§b-----------§fMulti Whitelist§b-----------§r
''' + prefix + ' / ' + prefix1 + ''' §a显示帮助信息§r
''' + prefix + ''' on/off §a开关白名单§r
''' + prefix + ''' list §a显示白名单列表§r
''' + prefix + ''' add/del/remove + §b[PlayerID]§r§a 管理本地玩家白名单§r
''' + prefix + ''' addall/delall/removeall + §b[PlayerID]§r§a 管理多服务器玩家白名单§r
''' + prefix + ''' sync §a同步本地服务器白名单 §c(只能在本地服务器生效)§r
''' + prefix + ''' reload §a重载本服务器的whitelist.json§r
§b-----------------------------------§r
'''

@new_thread('wlist_process')
def help_msg(src : CommandSource):
    src.reply(help)


def permission_check(src : CommandSource, cmd):
    if src.get_permission_level() >= permission[cmd]:
        return True
    else:
        return False


@new_thread('wlist_process')
def error_msg(server, info, num, error_info = ''):
    if num == 0:
        server.tell(info.player, error_unknown_command)
    elif num == 1:
        server.tell(info.player, error_syntax)
    elif num == 2:
        server.tell(info.player, error_permission)
    elif num == 3:
        server.tell(info.player, error + '服务器 §d[' + error_info + ']§c 不存在§r')
    elif num == 4:
        server.tell(info.player, error + 'Rcon 连接 §d[' + error_info + ']§c 服务器失败§r' + '''
检查文件夹 config/multi_whitelist.json 去确认服务器数据是正确的''')
    elif num == 5:
        server.tell(last_player, error + info_change_cn(3))
    elif num == 6:
        server.tell(last_player, error + info_change_cn(4))
    elif num == 7:
        server.tell(last_player, error + info_change_cn(7))
    elif num == 8:
        server.tell(last_player, error + info_change_cn(8))


@new_thread('wlist_cmd')
def run_cmd(src : CommandSource, cmd):
    global server_listen, last_player
    server_listen = 1
    last_player = src.get_info().player
    src.get_server().execute(cmd)


@new_thread('wlist_cmd')
def cmd_all_server(src : CommandSource, cmd, player):
    if disable_multi_server:
        src.reply(error + "多服务器功能以禁止")
        return
    global target_player, to_server
    to_server = 1
    target_player = player
    run_cmd(src, cmd + player)


@new_thread('wlist_cmd')
def edit(src : CommandSource, player, num):
    global target_player
    target_player = player
    if num == 1:
        msg = " add "
    else:
        msg = " remove "
    run_cmd(src, 'whitelist' + msg + player)


def rcon_send(server : ServerInterface, info : Info, sub_server_info, cmd):
    sub_server_rcon = RconConnection(sub_server_info["rcon_ip"], int(sub_server_info["rcon_port"]), sub_server_info["rcon_password"])
    try:
        sub_server_rcon.connect()
        iserror = 0
    except ConnectionRefusedError:
        error_msg(server = server, info = info, num = 4, error_info = sub_server_info["folder_name"])
        iserror = 1
    if not iserror:
        sub_server_rcon.send_command(cmd)
        sub_server_rcon.disconnect()
        return False
    else:
        sub_server_rcon.disconnect()
        return True


def read_config():
    with open(path, 'r') as f:
        js = json.load(f)
    return js


@new_thread('wlist_process')
def sync(src : CommandSource):
    if disable_multi_server:
        src.reply(error + "多服务器功能以禁止")
        return
    sub_server_info = read_config()["servers"]
    for i in range(len(sub_server_info)):
        if sub_server_info[i]["same_directory"] == 'true':
            if not os.path.exists("../" + sub_server_info[i]["folder_name"] + "/" + local_path):
                error_msg(src, 3, sub_server_info[i]["folder_name"])
            else:
                shutil.copyfile('./' + local_path, "../" + sub_server_info[i]["folder_name"] + "/" + local_path)
                if not rcon_send(src.get_server, src.getinfo, sub_server_info[i], 'whitelist reload'):
                    src.reply(systemreturn + '同步白名单至 §d[' + sub_server_info[i]["folder_name"] + ']§r 服务器')
        else:
            src.reply(systemreturn+ '§d[' + sub_server_info["folder_name"] + ']§r 不是本地服务器')


@new_thread('wlist_process')
def to_other_server(server : ServerInterface, info : Info, cmd = ''):
    sub_server_info = read_config()["servers"]
    for i in range(len(sub_server_info)):
        if not rcon_send(server, info, sub_server_info[i], cmd + target_player):
            if cmd == 'whitelist add ':
                server.tell(info.player, systemreturn + '增加 ' + target_player + ' 至 §d[' + sub_server_info[i]["folder_name"] + ']§r 服务器的白名单')
            elif cmd == 'whitelist remove ':
                server.tell(info.player, systemreturn + '移除 ' + target_player + ' 至 §d[' + sub_server_info[i]["folder_name"] + ']§r 服务器的白名单')
        else:
            server.tell(info.player, "ERROR")


@new_thread('wlist_process')
def to_other_server_confirm(server : ServerInterface, info : Info, cmd = ''):
    global to_server
    info.player = last_player
    if to_server == 1:
        to_server = 0
        to_other_server(server, info, cmd)


def info_change_cn(num, str = ''):
    if num == 0:
        str = str.replace('There are ', '这里有')
        str = str.replace(' whitelisted players', '个白名单玩家')
    elif num == 1:
        str = '已将' + target_player + '列入白名单'
    elif num == 2:
        str = '已将' + target_player + '移出白名单'
    elif num == 3:
        str = '玩家' + target_player + '已经在白名单了'
    elif num == 4:
        str = '玩家' + target_player + '不是白名单成员'
    elif num == 5:
        str = '白名单已开启'
    elif num == 6:
        str = '白名单已关闭'
    elif num == 7:
        str = '白名单早就开启了'
    elif num == 8:
        str = '白名单早就关闭了'
    elif num == 9:
        str = '白名单已经重新加载'
    return str


@new_thread('wlist_cmd')
def reply(server : ServerInterface, info : Info):
    global to_server, server_listen
    if info.content.startswith('There are'):
        server.tell(last_player, systemreturn + info_change_cn(0, info.content))
    elif info.content.startswith('Added'):
        server.tell(last_player, systemreturn + info_change_cn(1))
        to_other_server_confirm(server, info, 'whitelist add ')
    elif info.content.startswith('Removed'):
        server.tell(last_player, systemreturn + info_change_cn(2))
        to_other_server_confirm(server, info, 'whitelist remove ')
    elif info.content.startswith('Player is already'):
        to_server = 0
        error_msg(server, info, 5)
    elif info.content.startswith('Player is not'):
        to_server = 0
        error_msg(server, info, 6)
    elif info.content.startswith('Whitelist is now turned on'):
        server.tell(last_player, systemreturn + info_change_cn(5))
    elif info.content.startswith('Whitelist is now turned off'):
        server.tell(last_player, systemreturn + info_change_cn(6))
    elif info.content.startswith('Whitelist is already turned on'):
        error_msg(server, info, 7)
    elif info.content.startswith('Whitelist is already turned off'):
        error_msg(server, info, 8)
    elif info.content.startswith('Reloaded'):
        server.tell(last_player, systemreturn + info_change_cn(9))
    else:
        server_listen = 1


def fox_literal(msg):
    return Literal(msg).requires(lambda src : permission_check(src, msg))


def register_command(server : ServerInterface, prefix_use):
    server.register_command(
        Literal(prefix_use).
        requires(lambda src : permission_check(src, 'help')).
        runs(help_msg).
        on_child_error(UnknownArgument, lambda src : src.reply(error_unknown_command), handled = True).
        on_child_error(RequirementNotMet, lambda src : src.reply(error_permission), handled = True).
        then(
            fox_literal('help').
            runs(help_msg)
        ).then(
            fox_literal('list').
            runs(lambda src : run_cmd(src, 'whitelist list'))
        ).then(
            fox_literal('reload').
            runs(lambda src : run_cmd(src, 'whitelist reload'))
        ).then(
            fox_literal('on').
            runs(lambda src : run_cmd(src, 'whitelist on'))
        ).then(
            fox_literal('off').
            runs(lambda src : run_cmd(src, 'whitelist off'))
        ).then(
            fox_literal('sync').
            runs(sync)
        ).then(
            fox_literal('add').
            then(
                Text('player').
                runs(lambda src, cmdict : edit(src, cmdict['player'], 1))
            )
        ).then(
            fox_literal('del').
            then(
                Text('player').
                runs(lambda src, cmdict : edit(src, cmdict['player'], 2))
            )
        ).then(
            fox_literal('addall').
            then(
                Text('player').
                runs(lambda src, cmdict : cmd_all_server(src, 'whitelist add ', cmdict['player']))
            )
        ).then(
            fox_literal('delall').
            then(
                Text('player').
                runs(lambda src, cmdict : cmd_all_server(src, 'whitelist remove ', cmdict['player']))
            )
        )
    )



def on_info(server : ServerInterface, info : Info):
    global server_listen , last_player, target_player
    if server_listen == 1:
        server_listen = 0
        info.player = last_player
        reply(server, info)


def on_load(server : ServerInterface, old):
    register_command(server, prefix)
    register_command(server, prefix1)
    server.register_help_message('!!whitelist/!!wlist','A whitelist plugin with multi server')