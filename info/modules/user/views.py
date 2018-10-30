from flask import render_template

from info.modules.user import user_blu

#个人中心
@user_blu.route('/user_info')
def user_info():

    return render_template("user.html")