from info import sr
from info.modules.home import home_blu
import logging      #python 内置日志模块，将日志信息在控制台输出，并且可以将日志保存在文件中
#flask 中的默认日志也是集成的logging模块，但是没有将日志保存在文件中

from flask import current_app   #在其他文件中使用app
#2.使用蓝图注册路由
@home_blu.route('/')
def index():

    #logging.error('error found')    # logging 默认的输出不包含错误位置，显示效果不好，可以使用flask内置的日志输出语法来代替

    current_app.logger.error('error found')
    return 'index'
