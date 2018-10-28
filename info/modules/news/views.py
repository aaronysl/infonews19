from flask import render_template, current_app, abort, session, g, request, jsonify

from info.models import News, User
from info.modules.news import news_blu

# 新闻详情
from info.utils.common import user_login_data
from info.utils.response_code import RET, error_map


@news_blu.route('/<int:news_id>')  # 路由变量接收新闻id
@user_login_data  # 装饰器形式来封装用户信息的查询  news_detail = user_login_data(news_detail)
def news_detail(news_id):
    # 根据新闻id查询该新闻数据
    try:
        news = News.query.get(news_id)
    except BaseException as e:
        current_app.logger.error(e)
        abort(500)

    # 按照`点击量`查询`前10条`新闻数据
    news_list = []
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(10).all()
    except BaseException as e:
        current_app.logger.error(e)

    news_list = [news.to_dict() for news in news_list]

    # 点击量加1
    news.clicks += 1

    # 将模型转为字典
    user = g.user.to_dict() if g.user else None

    # 将数据传入模板渲染
    return render_template("detail.html", news=news.to_dict(), news_list=news_list, user=user)


# 新闻收藏
@news_blu.route('/news_collect', methods=['POST'])
@user_login_data
def news_collect():
    # 判断用户是否登录
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg=error_map[RET.SESSIONERR])

    # 获取参数
    news_id = request.json.get("news_id")
    action = request.json.get("action")
    # 校验参数
    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    if action not in ["collect", "cancel_collect"]:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    try:  # 格式转换
        news_id = int(news_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 查询并校验是否存在该新闻
    try:
        news = News.query.get(news_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    if not news:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 根据action执行收藏/取消收藏  (使用关系属性来建立/解除关系)
    if action == "collect":  # 收藏
        user.collection_news.append(news)
    else:  # 取消收藏
        user.collection_news.remove(news)

    # json返回结果
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])