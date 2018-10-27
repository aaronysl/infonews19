# 过滤器的本质: 函数   1.必须设置参数接收模板变量  2> 将转换后的结果返回
def func_index_convert(index):

    index_dict = {1: "first", 2: "second", 3: "third"}

    return index_dict.get(index, "")