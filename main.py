from flask import Flask,session
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from info import create_app


#创建应用
app = create_app('pro')

#创建管理器
mgr = Manager(app)

#管理生成迁移命令
mgr.add_command('mc',MigrateCommand)




if __name__ == '__main__':
    mgr.run()