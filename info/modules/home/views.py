from info import sr
from info.models import User
from info.modules.home import home_blu
import logging      #python 内置日志模块，将日志信息在控制台输出，并且可以将日志保存在文件中
#flask 中的默认日志也是集成的logging模块，但是没有将日志保存在文件中

from flask import current_app, render_template, session  # 在其他文件中使用app    导入render 后端模版渲染


#2.使用蓝图注册路由
@home_blu.route('/')
def index():

    #logging.error('error found')    # logging 默认的输出不包含错误位置，显示效果不好，可以使用flask内置的日志输出语法来代替

    # current_app.logger.error('error found')
    # 在根路由中判断用户是否登录
    user_id = session.get("user_id")

    user = None  # type: User
    if user_id:  # 已登录
        # 查询用户信息
        try:
            user = User.query.get(user_id)
        except BaseException as e:
            current_app.logger.error(e)

    # 将模型转为字典
    user = user.to_dict() if user else None

    # TODO 将用户信息传入模板渲染
    return render_template("index.html", user=user)





@home_blu.route('/favicon.ico')
def favicon():
    #网站小图标的请求是有浏览器发起的，只需要实现该路由并返回图标对应图片即可
    #flask中内置了返回静态文件的语法send_static_file，flask 访问静态文件的路由底层也是调用该方法
    return current_app.send_static_file('news/favicon.ico')