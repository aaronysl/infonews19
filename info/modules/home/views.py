from info import sr
from info.modules.home import home_blu
import logging      #python 内置日志模块，将日志信息在控制台输出，并且可以将日志保存在文件中
#flask 中的默认日志也是集成的logging模块，但是没有将日志保存在文件中

from flask import current_app,render_template   #在其他文件中使用app    导入render 后端模版渲染


#2.使用蓝图注册路由
@home_blu.route('/')
def index():

    #logging.error('error found')    # logging 默认的输出不包含错误位置，显示效果不好，可以使用flask内置的日志输出语法来代替

    # current_app.logger.error('error found')


    return render_template('index.html')


@home_blu.route('/favicon.ico')
def favicon():
    #网站小图标的请求是有浏览器发起的，只需要实现该路由并返回图标对应图片即可
    #flask中内置了返回静态文件的语法send_static_file，flask 访问静态文件的路由底层也是调用该方法
    return current_app.send_static_file('news/favicon.ico')