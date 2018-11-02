from flask import Flask,session
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from info import create_app

import datetime
import random

#创建应用


app = create_app('dev')

#创建管理器
mgr = Manager(app)

#管理生成迁移命令
mgr.add_command('mc',MigrateCommand)

# 生成管理员(生成一个用户模型, is_admin=True)
@mgr.option("-u",dest='username')   # python main.py create_superuser -u admin -p 123456
@mgr.option("-p",dest='password')
def create_superuser(username,password):
    from info import db
    from info.models import User
    if not all([username,password]):
        print('参数不足')
        return
    #创建用户模型
    user = User()
    user.mobile = username
    user.password = password
    user.nick_name = username
    user.is_admin = True
    try:
        db.session.add(user)    # 添加到数据库
        db.session.commit()
    except BaseException as e:
        app.logger.error(e)
        print('数据库操作失败')
    print('生成管理员成功')

#添加测试数据
def add_test_users():
    from info import db
    from info.models import User
    users = []
    now = datetime.datetime.now()
    for num in range(0, 10000):
        try:
            user = User()
            user.nick_name = "%011d" % num
            user.mobile = "%011d" % num
            user.password_hash = "pbkdf2:sha256:50000$SgZPAbEj$a253b9220b7a916e03bf27119d401c48ff4a1c81d7e00644e0aaf6f3a8c55829"
            user.create_time = now - datetime.timedelta(seconds=random.randint(0, 2678400))
            users.append(user)
            print(user.mobile)
        except Exception as e:
            print(e)
    db.session.add_all(users)
    db.session.commit()
    print('OK')

if __name__ == '__main__':
    mgr.run()
    # add_test_users()
