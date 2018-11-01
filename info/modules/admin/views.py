import time
from datetime import datetime

from flask import render_template, request, current_app, redirect, url_for, session, g

from info.utils.common import user_login_data
from info.models import User
from info.modules.admin import admin_blu


# 后台登录
@admin_blu.route('/login', methods=['GET', "POST"])
def login():

    if request.method == 'GET': # 显示页面
        # 取出session中的数据, 如果已登录, 则直接重定向到后台首页
        user_id = session.get("user_id")
        is_admin = session.get("is_admin")
        if user_id and is_admin:
            return redirect(url_for("admin.index"))

        return render_template("admin/login.html")

    # POST处理
    username = request.form.get("username")
    password = request.form.get("password")

    if not all([username, password]):
        return render_template("admin/login.html", errmsg="参数不完整")

    # 取出用户模型
    try:
        user = User.query.filter(User.mobile==username, User.is_admin==True).first()
    except BaseException as e:
        current_app.logger.error(e)
        return render_template("admin/login.html", errmsg="数据库错误")

    if not user:
        return render_template("admin/login.html", errmsg="该管理员不存在")

    # 校验密码
    if not user.check_password(password):
        return render_template("admin/login.html", errmsg="用户名/密码错误")

    # session记录状态信息
    session["user_id"] = user.id
    session["is_admin"] = True

    # 重定向到后台首页
    return redirect(url_for("admin.index"))



# 后台首页
@admin_blu.route('/index')
@user_login_data
def index():

    return render_template("admin/index.html", user=g.user.to_dict())


# 后台退出登录
@admin_blu.route('/logout')
def logout():
    session.pop("user_id", None)
    session.pop("is_admin", None)
    return redirect(url_for("home.index"))


# 用户统计
@admin_blu.route('/user_count')
def user_count():
    # 用户总数
    total_count = 0
    try:
        total_count = User.query.filter(User.is_admin == False).count()
    except BaseException as e:
        current_app.logger.error(e)

    # 月新增人数
    mon_count = 0

    # 获取当前时间的 年 和 月
    t = time.localtime()
    # 构建目标日期字符串  2018-10-01
    date_mon_str = "%d-%02d-01" % (t.tm_year, t.tm_mon)
    # 日期字符串 转为 日期对象
    date_mon = datetime.strptime(date_mon_str, "%Y-%m-%d")

    try:  # 用户注册日期 >= 当月1号0点
        mon_count = User.query.filter(User.is_admin == False, User.create_time >= date_mon).count()
    except BaseException as e:
        current_app.logger.error(e)

    # 日新增人数
    day_count = 0
    # 构建目标日期字符串
    date_day_str = "%d-%02d-%02d" % (t.tm_year, t.tm_mon, t.tm_mday)
    # 日期字符串 转为 日期对象
    date_day = datetime.strptime(date_day_str, "%Y-%m-%d")

    try:  # 用户注册日期 >= 某月某日0点
        day_count = User.query.filter(User.is_admin == False, User.create_time >= date_day).count()
    except BaseException as e:
        current_app.logger.error(e)

    data = {
        "total_count": total_count,
        "mon_count": mon_count,
        "day_count": day_count
    }

    return render_template("admin/user_count.html", data=data)