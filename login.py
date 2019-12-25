import requests
from urllib import request
from http import cookiejar
import time
from PIL import Image
import os


if __name__ == '__main__':
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
    host = "http://elite.nju.edu.cn/jiaowu/"
    cookie = cookiejar.CookieJar()
    handler = request.HTTPCookieProcessor(cookie)
    openner = request.build_opener(handler)
    openner.open(host)
    # 获取cookie
    # print(cookie)

    s = requests.session()  # 确保申请验证码的session和登陆时为一致的，所以写在了这里
    now_time = str(int(time.time()))
    pic_url = host + 'ValidateCode.jsp'
    # 取得验证码图片
    pic = s.get(pic_url).content
    filename = '' + now_time + '.jpg'  # 以后可能还是要用到手动输入验证码，所以先保存图片吧
    with open(filename, 'wb') as f:
        f.write(pic)

    #尝试使用OCR自动识别验证码，但是由于验证码干扰较多，不能正确识别，因此采用手动输入方式
    # img = Image.open(filename)
    # img=img.convert('L')
    # vcode = pytesseract.image_to_string(img)  # 使用ocr技术将图片中的验证码读取出来
    # time.sleep(0.3) 

    # print(vcode)
    print("请输入验证码(Please enter the ValidateCode)")
    vcode=input()
    os.remove(filename)
    login_data={}
    login_data['userName']="161290019"
    login_data['password']="Wyx199812"
    login_data['retrunURL']="null"
    login_data['ValidateCode']=vcode
    response = s.post(host+"login.do",login_data)
    HomePage = response.content
    HomePage.decode('utf-8')
    print(response.content.decode('utf-8'))
    with open("jw.html",'w') as f:
        f.write(str(response.content.decode('utf-8')))
    if response.content.__len__() > 1100:
        print("Login success!")
    else:
        print("Login failed")

    # vcode_list = confirm_vcode(vcode)  # 检验验证码有效性，并输出更好的验证码队列



    # response = requests.get("http://elite.nju.edu.cn/jiaowu/ValidateCode.jsp")
    # print(response.text.encode('GBK','ignore'))