from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
app = Flask(__name__)

class Config:   #定义配置类  封装所有的配置 方便对代码统一管理
    #定义和配置同名的类属性
    DEBUG = True    #设置调试模式
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:macmysql@127.0.0.1:3306/info19" #数据库链接地址
    SQLALCHEMY_TRACK_MODIFICATIONS = False  #设置追踪数据库变化
    REDIS_HOST = '127.0.0.1'    #redis 的IP
    REDIS_PORT = 6379   #redis的端口
#从对象加载配置信息
app.config.from_object(Config)

#创建数据库链接对象
db = SQLAlchemy(app)

#创建redis链接对象
sr = StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT)
@app.route('/')
def index():

    sr.set('name','jack')
    return 'index'


if __name__ == '__main__':
    app.run(debug=True)