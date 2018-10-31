from flask import request, render_template, current_app, redirect, url_for, session

from info.models import User
from info.modules.admin import admin_blu

#后台登陆
@admin_blu.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        # 取出session中的数据, 如果已登录, 则直接重定向到后台首页
        user_id = session.get("user_id")
        is_admin = session.get("is_admin")
        if user_id and is_admin:
            return redirect(url_for("admin.index"))
        return render_template('admin/login.html')

    #post处理
    username = request.form.get('username')
    password = request.form.get('password')

    #校验参数
    if not all([username,password]):
        return render_template('admin/login.html',errmsg='参数不足')

    #根据username查询用户信息
    try:
        user=User.query.filter(User.mobile==username,User.is_admin == True).first()
    except BaseException as e:
        current_app.logger.error(e)
        return render_template('admin/login.html',errmsg='数据库操作失败')

    if not user:
        return render_template('admin/login.html',errmsg='管理员不存在')


    #校验密码
    if not user.check_password(password):
        return render_template('admin/login.html',errmsg='用户名/密码错误')

    # session记录状态信息
    session["user_id"] = user.id
    session["is_admin"] = True

    #重定向到后台首页
    return redirect(url_for('admin.index'))

#后台首页
@admin_blu.route('/index')
def index():

    return render_template('admin/index.html')


#后台退出登陆
@admin_blu.route('/logout')
def logout():
    session.pop("user_id", None)
    session.pop("is_admin", None)
    return redirect(url_for("home.index"))