from logging.handlers import RotatingFileHandler

import logging
from flask import Flask
from flask_migrate import Migrate
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis

from config import config_dict

#定义函数、封装应用的创建配置     工厂函数(调用者提供生产物料，函数内部封装创建过程)


#将数据库链接对象全局化（方便其他文件使用）

db = None   #type:SQLAlchemy
sr = None   #type:StrictRedis


#日志配置（将日志保存到文件中）
def setup_log():
    # 设置日志的记录等级
    logging.basicConfig(level=logging.DEBUG)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(pathname)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def create_app(config_type):
    app = Flask(__name__)


    #根据配置类型取出配置类
    config_class = config_dict.get(config_type)

    #从对象加载配置信息
    app.config.from_object(config_class)

    # 声明全局变量
    global db,sr

    #创建数据库链接对象
    db = SQLAlchemy(app)

    #创建redis链接对象
    sr = StrictRedis(host=config_class.REDIS_HOST,port=config_class.REDIS_PORT,decode_responses=True)

    #初始化session存储对象
    Session(app)

    #初始化迁移器
    Migrate(app,db)

    #针对某些只使用一次的内容，在使用前导入即可（需要时才导入）这样可以有效避免循环导入
    from info.modules.home import home_blu
    #注册蓝图
    app.register_blueprint(home_blu)


    from info.modules.passport import passport_blu
    # 注册蓝图
    app.register_blueprint(passport_blu)


    from info.modules.news import news_blu
    app.register_blueprint(news_blu)

    from info.modules.user import user_blu
    app.register_blueprint(user_blu)
    

    #配置日志
    setup_log()

    #import * 这种语法不能在函数/方法中使用
    # from info.models import *
    import info.models

    #添加过滤器
    from info.utils.common import func_index_convert
    app.add_template_filter(func_index_convert, "index_convert")

    return app