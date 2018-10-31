from info import sr
from info.constants import HOME_PAGE_MAX_NEWS
from info.models import User, News, Category
from info.modules.home import home_blu
import logging  # python内置的日志模块  将日志信息在控制台中输出, 并且可以将日志保存到文件中
# flask中的默认日志也是集成的logging模块, 但是没有将日志保存到文件中
from flask import current_app, render_template, session, request, jsonify, g

# 2.使用蓝图注册路由
from info.utils.common import user_login_data
from info.utils.response_code import RET, error_map


@home_blu.route('/')
@user_login_data
def index():

    # 按照`点击量`查询`前10条`新闻数据
    news_list = []
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(10).all()
    except BaseException as e:
        current_app.logger.error(e)

    news_list = [news.to_dict() for news in news_list]


    # 查询所有的分类数据, 后端模板渲染
    categories = []
    try:
        categories = Category.query.all()
    except BaseException as e:
        current_app.logger.error(e)


    # 将模型转为字典
    user = g.user.to_dict() if g.user else None

    # 将用户信息传入模板渲染
    return render_template("news/index.html", user=user, news_list=news_list, categories=categories)


@home_blu.route('/favicon.ico')
def favicon():
    # 网站小图标的请求是由浏览器自动发起的, 只需要实现该路由并返回图标对应图片即可
    # flask中内置了获取静态文件的语法send_static_file, flask访问静态文件的路由底层也是调用该方法
    return current_app.send_static_file("news/favicon.ico")


@home_blu.route('/get_news_list')
def get_news_list():
    # 获取参数
    cid = request.args.get("cid")
    cur_page = request.args.get("cur_page")
    per_count = request.args.get("per_count", HOME_PAGE_MAX_NEWS)
    # 校验参数
    if not all([cid, cur_page]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    # 格式转换
    try:
        cid = int(cid)
        cur_page = int(cur_page)
        per_count = int(per_count)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    filter_list = [News.status == 0]  # 只有审核通过的新闻才能显示
    filter_list = []
    if cid != 1:  # 不是"最新"
        filter_list.append(News.category_id == cid)

    # 根据参数查询目标新闻  按照发布时间和分类和页码查询新闻数据
    try:
        pn = News.query.filter(*filter_list).order_by(News.create_time.desc()).paginate(cur_page, per_count)
        news_list = [news.to_dict() for news in pn.items]
        total_page = pn.pages

    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    data = {
        "news_list": news_list,
        "total_page": total_page
    }

    # 将新闻封装到json返回
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK], data=data)
