import random
import re

from flask import request, abort, current_app, make_response, Response, jsonify

from info import sr
from info.lib.captcha.pic_captcha import captcha
from info.lib.yuntongxun.sms import CCP
from info.modules.passport import passport_blu


#获取图片验证
from info.utils.response_code import RET,error_map


@passport_blu.route('/get_img_code')
def get_img_code():

    #获取参数
    img_code_id = request.args.get('img_code_id')
    #校验参数
    if not img_code_id:
        return abort(403)   #403是拒绝访问
    #生成图片验证码
    img_name,img_text,img_bytes = captcha.generate_captcha()
    #保存验证码文字和图片     redis
    try:
        sr.set('img_code_id'+ img_code_id,img_text,ex=300)
    except BaseException as e:
        current_app.logger.error(e)
        return abort(500)   #500 服务器错误


    #自定义响应对象，设置响应头的content-type 为image/jpeg
    response = make_response(img_bytes)     #type:Response
    response.content_type = 'image/jpeg'
    return response


#获取短信验证码
@passport_blu.route('/get_sms_code',methods =['POST'])
def get_sms_code():
    #获取参数
    print('22222222222')
    img_code_id = request.json.get('img_code_id')
    img_code = request.json.get('img_code')
    mobile = request.json.get('mobile')
    #校验参数
    if not all([img_code_id,img_code,mobile]):
        return jsonify(errno=RET.PARAMERR,errmsg=error_map[RET.PARAMERR])

    #校验手机格式
    if not re.match(r"1[35678]\d{9}$",mobile):
        return jsonify(errno=RET.PARAMERR,errmsg=error_map[RET.PARAMERR])
    #校验图片验证码    根据图片key取出真实验证码文字
    try:
        real_img_code =  sr.get('img_code_id'+img_code_id)
        print('sssss')
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(RET.DBERR,error_map=error_map[RET.DBERR])

    if real_img_code != img_code.upper():

        return jsonify(errno=RET.PARAMERR,errmsg=error_map[RET.PARAMERR])

    #生成随机验证码
    rand_num = "%04d" % random.randint(0,9999)

    #打印验证码
    current_app.logger.info('短信验证码为：%s'% rand_num)

    #发送短信
    response_code = CCP().send_template_sms(mobile, [rand_num, 5], 1)
    if response_code != 0:
        return jsonify(errno=RET.THIRDERR,errmsg=error_map[RET.THIRDERR])

    #保存短信验证码
    try:
        sr.set('sms_code_id_'+mobile,rand_num,ex=60)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg=error_map[RET.DBERR])

    #返回json结果
    return jsonify(errno=RET.OK,error_map=error_map[RET.OK])