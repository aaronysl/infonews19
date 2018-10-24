from datetime import timedelta

from flask import Flask,session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_session import Session
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand

app = Flask(__name__)

class Config:   #定义配置类  封装所有的配置 方便对代码统一管理
    #定义和配置同名的类属性
    DEBUG = True    #设置调试模式
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:macmysql@127.0.0.1:3306/info19" #数据库链接地址
    SQLALCHEMY_TRACK_MODIFICATIONS = False  #设置追踪数据库变化
    REDIS_HOST = '127.0.0.1'    #redis 的IP
    REDIS_PORT = 6379   #redis的端口
    SESSION_TYPE = 'redis'  #session存储类型
    SESSION_REDIS = StrictRedis(host=REDIS_HOST,port=REDIS_PORT)    #redis链接对象
    SESSION_USE_SIGNER = True   #设置session id 加密    如果加密必须设置应用密钥
    SECRET_KEY = 'RcNV5mPppxDtmpVJgPXGGT4/ezUS5Wh95yzl5g3bn3q+zZ/+NWbVb7Ik2I3gmGaa' #设置应用密钥
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)  #设置session过期时间  默认支持过期时间
#从对象加载配置信息
app.config.from_object(Config)

#创建数据库链接对象
db = SQLAlchemy(app)

#创建redis链接对象
sr = StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT)

#初始化session存储对象
Session(app)

#创建管理器
mgr = Manager(app)

#初始化迁移器
Migrate(app,db)

#管理生成迁移命令
mgr.add_command('mc',MigrateCommand)


@app.route('/')
def index():

    session['age'] = 18
    return 'index'


if __name__ == '__main__':
    mgr.run()