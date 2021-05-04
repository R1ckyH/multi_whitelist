# multi_whitelist
-----
[中文](https://github.com/rickyhoho/multi_whitelist/blob/master/README_cn.md)

A plugin for [MCDReforged](https://github.com/Fallen-Breath/MCDReforged) which can control whitelist in multi servers

It work with whitelist function in normal minecraft server

To use this plugin, you have to open rcon function of your server.

Type `!!whitelist` or `!!wlist` to see the help page

You have to fill configure file `MCDR/config/multi_whitelist.json`

# permission

`user` or above permission can use help command and check for whitelist list
  
`helper` or above permission can use all of the command
  
# config
-----
|name|type|example|funtion|
|---|---|---|---|
|"folder_name"|`str`|`"creative"`|The floder name of mcdr server|
|"rcon_ip"|`str`|`"127.0.0.1"`|The rcon ip of server|
|"rcon_port"|`int`|`"12345"`|The rcon port of server|
|"rcon_password"|`str`|`"password"`|The rcon password of server|
|"same_directory"|`bool`|`"true"`|The server exist in same directory or not (Please use `lower case letter for true and false`)|
