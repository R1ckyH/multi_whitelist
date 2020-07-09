# multi_whitelist
-----
[中文](https://github.com/rickyhoho/multi_whitelist/blob/master/README_cn.md)

A plugin for [MCDReforged](https://github.com/Fallen-Breath/MCDReforged) which can control whitelist in multi servers

It work with whitelist function in normal minecraft server

To use this plugin, you have to open rcon function of your server.

Type `!!whitelist` or `!!wlist` to use this plugin

You have to fill configure file `MCDR/config/multi_whitelist.json`

# config
-----
`"local_server_file_name" : "name"`   The file name of this server
|name|type|example|funtion|
|---|---|---|---|
|"name"|`str`|`"creative"`|The file name of server|
|"rcon_ip"|`str`|`"127.0.0.1"`|The rcon ip of server|
|"rcon_port"|`int`|`"12345"`|The rcon port of server|
|"rcon_password"|`str`|`"password"`|The rcon password of server|
|"local_server"|`bool`|`"true"`|The server exist in local path or not (Please use `lower case letter`)|
