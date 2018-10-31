from flask import Flask,session
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from info import create_app


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


if __name__ == '__main__':
    mgr.run()