from flask import Blueprint

#1.创建蓝图
admin_blu = Blueprint('admin',__name__,url_prefix='/admin')


#4.关联视图函数 (避免循环导入）

from .views import *


