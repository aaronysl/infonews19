from datetime import timedelta

from flask import Flask,session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_session import Session
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand

from config import ProductConfig

app = Flask(__name__)


#从对象加载配置信息
app.config.from_object(ProductConfig)

#创建数据库链接对象
db = SQLAlchemy(app)

#创建redis链接对象
sr = StrictRedis(host=ProductConfig.REDIS_HOST,port=ProductConfig.REDIS_PORT)

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