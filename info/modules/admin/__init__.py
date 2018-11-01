from flask import Blueprint

#1.创建蓝图
admin_blu = Blueprint('admin',__name__,url_prefix='/admin')


# 给蓝图设置请求钩子 (只会拦截该蓝图注册的路由)
@admin_blu.before_request
def check_superuser():
    is_admin = session.get("is_admin")
    # 判断管理员是否登录, 如果没登录, 重定向到前台首页
    if not is_admin and not request.url.endswith('admin/login'): # 没有登录 并且 不是 后台登录请求
        return redirect(url_for('home.index'))

#4.关联视图函数 (避免循环导入）

from .views import *


