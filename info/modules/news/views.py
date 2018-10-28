from flask import render_template, current_app, abort

from info.models import News
from info.modules.news import news_blu


# 新闻详情
@news_blu.route('/<int:news_id>')  # 路由变量接收新闻id
def news_detail(news_id):
    # 根据新闻id查询该新闻数据
    try:
        news = News.query.get(news_id)
    except BaseException as e:
        current_app.logger.error(e)
        abort(500)

    # 将数据传入模板渲染
    return render_template("detail.html", news=news.to_dict())