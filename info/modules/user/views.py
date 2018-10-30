from flask import render_template, g, redirect, url_for, abort, request, jsonify

from info.modules.user import user_blu
from info.utils.common import user_login_data

# 个人中心
from info.utils.response_code import RET, error_map


@user_blu.route('/user_info')
@user_login_data
def user_info():
    user = g.user
    if not user:  # 用户未登录, 直接跳转到首页
        return redirect(url_for("home.index"))

    return render_template("user.html", user=user.to_dict())


# 基本资料
@user_blu.route('/base_info', methods=['GET', "POST"])
@user_login_data
def base_info():
    user = g.user
    if not user:
        return abort(403)  # 拒绝访问

    if request.method == 'GET':
        return render_template("user_base_info.html", user=user.to_dict())
    # POST处理
    signature = request.json.get("signature")
    nick_name = request.json.get("nick_name")
    gender = request.json.get("gender")

    # 校验参数
    if not all([signature, nick_name, gender]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    if gender not in ["MAN", "WOMAN"]:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 修改用户模型
    user.signature = signature
    user.nick_name = nick_name
    user.gender = gender

    # json返回  需要传入用户信息, 以便前端进行渲染
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK], data=user.to_dict())
