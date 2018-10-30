from flask import render_template, g, redirect, url_for

from info.modules.user import user_blu
from info.utils.common import user_login_data


# 个人中心
@user_blu.route('/user_info')
@user_login_data
def user_info():
    user = g.user
    if not user:  # 用户未登录, 直接跳转到首页
        return redirect(url_for("home.index"))

    return render_template("user.html", user=user.to_dict())


# 基本资料
@user_blu.route('/base_info')
def base_info():

    return render_template("user_base_info.html")