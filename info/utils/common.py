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


# 上传文件
def file_upload(data):
    """
    上传文件
    :param data:  要上传的二进制数据
    :return: 文件服务器中的文件名称
    """

    import qiniu

    access_key = "kJ8wVO7lmFGsdvtI5M7eQDEJ1eT3Vrygb4SmR00E"
    secret_key = "rGwHyAvnlLK7rU4htRpNYzpuz0OHJKzX2O1LWTNl"
    bucket_name = "infonews" # 空间名称

    q = qiniu.Auth(access_key, secret_key)
    key = None  # 设置上传文件名, 如果设置None则生成随机名称

    token = q.upload_token(bucket_name)
    # 上传文件
    ret, info = qiniu.put_data(token, key, data)
    if ret is not None:  # 上传成功, 返回文件名
        return ret.get("key")
    else:
       raise BaseException(info)
