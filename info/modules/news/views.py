from flask import render_template, current_app, abort, session, g

from info.models import News, User
from info.modules.news import news_blu


# 新闻详情
from info.utils.common import user_login_data


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