from flask import render_template, current_app, abort, session, g, request, jsonify

from info import db
from info.models import News, User, Comment
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

    # 查询当前用户是否收藏了新闻
    user = g.user
    is_collected = False  # 记录是否收藏
    if user:  # 用户登录
        if news in user.collection_news:
            is_collected = True

    # 查询该新闻的所有评论  按照生成日期排序
    comments = []
    try:
        comments = news.comments.order_by(Comment.create_time.desc()).all()
    except BaseException as e:
        current_app.logger.error(e)

    # 将模型转为字典
    user = user.to_dict() if user else None

    # 将数据传入模板渲染
    return render_template("detail.html", news=news.to_dict(), news_list=news_list, user=user,
                           is_collected=is_collected, comments=[comment.to_dict() for comment in comments])


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


# 新闻评论/子评论
@news_blu.route('/news_comment', methods=['POST'])
@user_login_data
def news_comment():
    # 判断用户是否登录
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg=error_map[RET.SESSIONERR])

    # 获取参数
    comment_content = request.json.get("comment")
    news_id = request.json.get("news_id")
    parent_id = request.json.get("parent_id")
    # 校验参数
    if not all([comment_content, news_id]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 校验新闻是否存在
    try:
        news_id = int(news_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    try:
        news = News.query.get(news_id)
    except BaseException as e:
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    if not news:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 生成评论模型
    comment = Comment()
    comment.content = comment_content
    comment.user_id = user.id
    comment.news_id = news.id
    if parent_id:  # 子评论
        try:
            parent_id = int(parent_id)
            comment.parent_id = parent_id
        except BaseException as e:
            current_app.logger.error(e)

    try:
        db.session.add(comment)
        db.session.commit()  # 此处必须主动提交, 否则不会生成评论id, 无法回传给前端评论id

    except BaseException as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    # 返回json  需要返回评论数据
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK], data=comment.to_dict())