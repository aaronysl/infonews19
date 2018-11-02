import time
from datetime import datetime, timedelta

from flask import render_template, request, current_app, redirect, url_for, session, g, abort, jsonify

from info.constants import ADMIN_USER_PAGE_MAX_COUNT, QINIU_DOMIN_PREFIX
from info.utils.common import user_login_data, file_upload
from info.models import User, News, Category
from info.modules.admin import admin_blu


# 后台登录
from info.utils.response_code import RET, error_map


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

    user = g.user

    return render_template("admin/index.html", user=user.to_dict())


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

    # 记录日注册人数    注册时间 >= 某日0点, < 次日0点
    active_count = []
    # 记录统计时间
    active_time = []
    # 获取 前30天 每日的注册人数 (注册日期 >= 某日0点, <次日0点)
    for i in range(0, 30):
        begin_date = date_day - timedelta(days=i)
        end_date = date_day + timedelta(days=1) - timedelta(days=i)
        # end_date = date_day + timedelta(days=1-i)
        try:
            one_day_count = User.query.filter(User.is_admin == False, User.create_time >= begin_date, User.create_time < end_date).count()
            active_count.append(one_day_count)

            # 日期对象 转为 日期字符串
            one_day_str = begin_date.strftime("%Y-%m-%d")
            active_time.append(one_day_str)

        except BaseException as e:
            current_app.logger.error(e)

    #列表反转
    active_count.reverse()
    active_time.reverse()
    data = {
        "total_count": total_count,
        "mon_count": mon_count,
        "day_count": day_count,
        "active_count": active_count,
        "active_time": active_time
    }

    return render_template("admin/user_count.html", data=data)


#用户列表
@admin_blu.route('/user_list')
def user_list():
    # 获取参数
    p = request.args.get("p", 1)

    # 校验参数
    try:
        p = int(p)
    except BaseException as e:
        current_app.logger.error(e)
        return abort(403)

    # 查询 所有的用户数据
    try:
        pn = User.query.filter(User.is_admin == False).paginate(p, ADMIN_USER_PAGE_MAX_COUNT)
    except BaseException as e:
        current_app.logger.error(e)
        return abort(500)

    data = {
        "user_list": [user.to_admin_dict() for user in pn.items],
        "cur_page": p,
        "total_page": pn.pages
    }

    # 模板渲染
    return render_template("admin/user_list.html", data=data)


#新闻审核列表
@admin_blu.route('/news_review')
def news_review():
    # 获取参数
    p = request.args.get("p", 1)
    keyword = request.args.get("keyword")

    # 校验参数
    try:
        p = int(p)
    except BaseException as e:
        current_app.logger.error(e)
        return abort(403)

    filter_list = []
    if keyword:  # 搜索
        filter_list.append(News.title.contains(keyword))

    # 查询 所有的新闻数据
    try:
        pn = News.query.filter(*filter_list).paginate(p, ADMIN_USER_PAGE_MAX_COUNT)
    except BaseException as e:
        current_app.logger.error(e)
        return abort(500)

    data = {
        "news_list": [news.to_review_dict() for news in pn.items],
        "cur_page": p,
        "total_page": pn.pages
    }

    # 模板渲染
    return render_template("admin/news_review.html", data=data)


#新闻审核详情
@admin_blu.route('/news_review_detail/<int:news_id>')
def news_review_detail(news_id):    #参数接收路由变量
    #查询新闻数据
    try:
        news=News.query.get(news_id)
    except BaseException as e:
        current_app.logger.error(e)
        return abort(500)

    if not news:
        return abort(403)


    #模板渲染
    return render_template('admin/news_review_detail.html',news=news.to_dict())


@admin_blu.route('/news_review_action', methods=['POST'])
def news_review_action():
    # 获取参数
    action = request.json.get("action")
    news_id = request.json.get("news_id")

    # 校验参数
    if not all([action, news_id]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    if action not in ["accept", "reject"]:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    try:
        news_id = int(news_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 查询新闻数据
    try:
        news = News.query.get(news_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    if not news:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 根据action设置新闻的状态
    if action == "accept":
        news.status = 0
    else:
        reason = request.json.get("reason")
        if not reason:
            return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
        news.status = -1
        news.reason = reason

    # json返回结果
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])

#新闻编辑列表
@admin_blu.route('/news_edit')
def news_edit():
    #获取参数
    p = request.args.get("p", 1)
    keyword = request.args.get("keyword")

    # 校验参数
    try:
        p = int(p)
    except BaseException as e:
        current_app.logger.error(e)
        return abort(403)

    filter_list = []
    if keyword:  # 搜索
        filter_list.append(News.title.contains(keyword))

    #查询所有的新闻数据
    try:
        pn = News.query.filter(*filter_list).paginate(p, ADMIN_USER_PAGE_MAX_COUNT)
    except BaseException as e:
        current_app.logger.error(e)
        return abort(500)

    data = {
        "news_list": [news.to_review_dict() for news in pn.items],
        "cur_page": p,
        "total_page": pn.pages
    }

    # 模板渲染
    return render_template("admin/news_edit.html", data=data)

#新闻编辑详情
@admin_blu.route('/news_edit_detail')
def news_edit_detail():
    news_id = request.args.get('news_id')
    try:
        news_id = int(news_id)
    except BaseException as e:
        current_app.logger.error(e)
        return abort(403)

    # 查询新闻数据
    try:
        news = News.query.get(news_id)
    except BaseException as e:
        current_app.logger.error(e)
        return abort(500)

    if not news:
        return abort(403)

    # 查询所有的的分类
    try:
        categories = Category.query.filter(Category.id != 1).all()
    except BaseException as e:
        current_app.logger.error(e)
        return abort(500)

    # 标出新闻对应的当前分类
    category_list = []
    for category in categories:
        category_dict = category.to_dict()
        is_selected = False
        # 判断该分类是否为当前新闻的分类
        if category.id == news.category_id:
            is_selected = True

        category_dict["is_selected"] = is_selected
        category_list.append(category_dict)

    # 模板渲染
    return render_template("admin/news_edit_detail.html", news=news.to_dict(), category_list=category_list)


@admin_blu.route('/news_edit_detail', methods=['POST'])
def news_edit_action():  # 同一个蓝图实现的视图函数名不能相同, 函数标记会冲突
    # 获取参数
    news_id = request.form.get("news_id")
    title = request.form.get("title")
    category_id = request.form.get("category_id")
    digest = request.form.get("digest")
    content = request.form.get("content")
    index_image = request.files.get("index_image")
    # 校验参数
    if not all([news_id, title, category_id, digest, content]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 查询新闻模型
    try:
        news_id = int(news_id)
        news = News.query.get(news_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    if not news:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 修改新闻数据
    news.title = title
    news.digest = digest
    news.content = content
    news.category_id = category_id
    if index_image:  # 修改图片
        try:
            img_bytes = index_image.read()
            file_name = file_upload(img_bytes)
            news.index_image_url = QINIU_DOMIN_PREFIX + file_name
        except BaseException as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.THIRDERR, errmsg=error_map[RET.THIRDERR])

    # json返回
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])





