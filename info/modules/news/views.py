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

    # 正常情况下, 查询到某个数据后, 关系属性会将该数据的所有关联数据都查询出来(如果不需要关联数据,会很影响性能)
    # 可以给关系属性设置lazy参数="dynamic", 这样关系属性就不会自动查询关联数据, 而是使用具体查询查询条件时才会查询(all/count/first)
    # 查询哪些评论被当前用户点过赞
    comment_list = []
    for comment in comments:
        comment_dict = comment.to_dict()
        is_like = False

        if user:  # 用户已登录
            # 该评论是否被"我"点赞
            # 设置了lazy的关系属性在和in联用时, 会自动进行all()查询
            if comment in user.like_comments:
                is_like = True

        # 定义键值对记录是否被当前用户点过赞
        comment_dict["is_like"] = is_like
        comment_list.append(comment_dict)

    # 查询作者是否被当前用户关注
    is_followed = False  # 记录是否已关注
    # 当前已登录, 并且新闻有作者
    if user and news.user:
        # 作者是否被当前用户关注
        if news.user in user.followed:
            is_followed = True

    # 将模型转为字典
    user = user.to_dict() if user else None

    # 将数据传入模板渲染
    return render_template("detail.html", news=news.to_dict(), news_list=news_list, user=user,
                           is_collected=is_collected, comments=comment_list,is_followed=is_followed)


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


# 评论点赞
@news_blu.route('/comment_like', methods=['POST'])
@user_login_data
def comment_like():
    # 判断用户是否登录
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg=error_map[RET.SESSIONERR])

    # 获取参数
    comment_id = request.json.get("comment_id")
    action = request.json.get("action")
    # 校验参数
    if not all([comment_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    if action not in ["add", "remove"]:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    try:  # 格式转换
        comment_id = int(comment_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 查询并校验是否存在该评论
    try:
        comment = Comment.query.get(comment_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    if not comment:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 根据action执行点赞/取消点赞  (使用关系属性来建立/解除关系)
    if action == "add":  # 点赞
        user.like_comments.append(comment)
        comment.like_count += 1
    else:  # 取消点赞
        user.like_comments.remove(comment)
        comment.like_count -= 1

    # json返回结果
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])


# 关注作者
@news_blu.route('/followed_user', methods=['POST'])
@user_login_data
def followed_user():
    # 判断用户是否登录
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg=error_map[RET.SESSIONERR])

    # 获取参数
    author_id = request.json.get("user_id")
    action = request.json.get("action")
    # 校验参数
    if not all([author_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    if action not in ["follow", "unfollow"]:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    try:  # 格式转换
        author_id = int(author_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 查询并校验是否存在该作者
    try:
        author = User.query.get(author_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    if not author:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 根据action执行滚珠/取消关注  (使用关系属性来建立/解除关系)
    if action == "follow":  # 关注
        user.followed.append(author)
    else:  # 取消关注
        user.followed.remove(author)

    # json返回结果
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])