import requests
from urllib import request
from http import cookiejar
import time
from PIL import Image
import os
from bs4 import BeautifulSoup

host = "http://elite.nju.edu.cn/jiaowu/"
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
def login(session):
    # 获取cookie
    cookie = cookiejar.CookieJar()
    handler = request.HTTPCookieProcessor(cookie)
    openner = request.build_opener(handler)
    openner.open(host) 

    #构造登陆请求体
    login_data={}
    with open("user.cfg",'r') as f:
        for line in f:
            items = line.split(":")
            items[1]=items[1].replace('\n','').replace('\r','')
            login_data[items[0]]=items[1]
    login_data['retrunURL']="null"
    print(login_data)

    # 取得验证码图片
    now_time = str(int(time.time()))
    pic_url = host + 'ValidateCode.jsp'
    pic = session.get(pic_url).content
    filename = '' + now_time + '.jpg'  
    with open(filename, 'wb') as f:
        f.write(pic)
    print("请输入验证码(Please enter the ValidateCode)")
    vcode=input()
    os.remove(filename) #输入完验证码后自动删除本地图片   
    login_data['ValidateCode']=vcode

    #尝试使用OCR自动识别验证码，但是由于验证码干扰较多，不能正确识别，因此采用手动输入方式
    # img = Image.open(filename)
    # img=img.convert('L')
    # vcode = pytesseract.image_to_string(img)  # 使用ocr技术将图片中的验证码读取出来
    # time.sleep(0.3) 
    # print(vcode)

    #发送登录请求
    response = session.post(host+"login.do",login_data)
    if response.content.__len__() > 1100:
        print("登陆成功!")
        return True
    else:
        print("登录失败，请检查账号密码及验证码")
        return False

if __name__ == '__main__':
    s = requests.session()  # 确保申请验证码的session和登陆时为一致的，所以写在了这里
    if not login(s):
        exit()

    #构造拉取课程信息的请求体
    courseList_reqdata={}
    courseList_reqdata['method']="specialityCourseList"
    courseList_reqdata['specialityCode']="221"
    courseList_reqdata['courseGrade']="2017"
    courseList = s.post(host+"student/elective/courseList.do",courseList_reqdata)
    print(courseList.content.decode('utf-8'))

    selectCourse_reqdata={}
    selectCourse_reqdata['method']="addSpecialitySelect"
    selectCourse_reqdata['classId']="92454"
    selectResult = s.post(host+'student/elective/selectCourse.do',selectCourse_reqdata)
    print(selectResult.content.decode('utf-8'))