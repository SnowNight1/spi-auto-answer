#!/bin/bash

# 启动虚拟显示服务器
Xvfb :99 -screen 0 1024x768x24 -ac +extension GLX +render -noreset &

# 等待X服务器启动
sleep 2

# 启动应用
exec "$@"
