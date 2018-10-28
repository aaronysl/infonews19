# 过滤器的本质: 函数   1.必须设置参数接收模板变量  2> 将转换后的结果返回
import functools

from flask import session, current_app, g

from info.models import User


def func_index_convert(index):

    index_dict = {1: "first", 2: "second", 3: "third"}

    return index_dict.get(index, "")



# 获取用户的登录信息
def user_login_data(f):  # f = news_detail

    @functools.wraps(f)  # 该装饰器会让闭包函数使用指定函数的信息(如函数名, 函数注释)
    def wrapper(*args, **kwargs):
        # 判断用户是否登录
        user_id = session.get("user_id")

        user = None  # type: User
        if user_id:  # 已登录
            # 查询用户信息
            try:
                user = User.query.get(user_id)
            except BaseException as e:
                current_app.logger.error(e)

        g.user = user

        return f(*args, **kwargs)

    return wrapper