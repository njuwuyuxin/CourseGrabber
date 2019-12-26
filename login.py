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
    files = os.listdir()
    # print(files)
    if "user.cfg" in files:
        with open("user.cfg",'r') as f:
            for line in f:
                items = line.split(":")
                items[1]=items[1].replace('\n','').replace('\r','')
                login_data[items[0]]=items[1]
    else:
        print("请输入用户名")
        login_data['userName']=input()
        print("请输入密码")
        login_data['password']=input()
    login_data['retrunURL']="null"
    # print(login_data)

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

def GetCourseList():
    #构造拉取课程信息的请求体
    courseList_reqdata={}
    courseList_reqdata['method']="specialityCourseList"
    courseList_reqdata['specialityCode']="221"
    courseList_reqdata['courseGrade']="2017"
    courseList = s.post(host+"student/elective/courseList.do",courseList_reqdata)
    # print(courseList.content.decode('utf-8'))

#接受两个参数，第一个为课程ID，第二个为每次抢课时间间隔
def GrabCourse(courseID,interval=0):
    while(True):
        selectCourse_reqdata={}
        selectCourse_reqdata['method']="addSpecialitySelect"
        selectCourse_reqdata['classId']=str(courseID)
        selectResult = s.post(host+'student/elective/selectCourse.do',selectCourse_reqdata)
        soup = BeautifulSoup(selectResult.content,"html.parser",from_encoding='utf-8')
        for tag in soup.find_all('div'):
            if tag.get('id')=="successMsg":
                print("抢课成功！")
                return
            elif tag.get('id')=="errMsg":
                if tag.string.find("已经")!=-1:
                    print("您已经抢到该课程啦~")
                    exit()
                else:
                    print("当前班级已满，仍在为您持续抢课")
            else:
                pass
        if interval!=0:
            time.sleep(interval)
        # print(selectResult.content.decode('utf-8'))

if __name__ == '__main__':
    s = requests.session()  # 确保申请验证码的session和登陆时为一致的，所以写在了这里
    if not login(s):
        exit()

    GetCourseList()
    print("请输入需要抢课的课程ID")
    courseID = input()
    GrabCourse(courseID,0)