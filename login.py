import requests
from urllib import request,error
from http import cookiejar
import time
from PIL import Image
from io import BytesIO
import os
import re
from bs4 import BeautifulSoup

host = "http://elite.nju.edu.cn/jiaowu/"
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
def login(session):
    #获取cookie，如果本地有cookie，尝试使用cookie登录
    c = GetCookie(session)
    session.cookies.update(c)
    if c:
        rs = requests.models.Response()
        try:
            rs = session.get("http://elite.nju.edu.cn/jiaowu/student/index.do")
        except requests.exceptions.ConnectionError:
            print("连接失败，请检查您的网络连接")
            exit()
        if rs.content.__len__() > 5000:
            print("登陆成功!")
            return True
        else:
            print("登录已过期，请重新登录")

    #构造登陆请求体
    login_data={}
    files = os.listdir()
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

    # 取得验证码图片
    now_time = str(int(time.time()))
    pic_url = host + 'ValidateCode.jsp'
    pic = session.get(pic_url).content
    im = Image.open(BytesIO(pic))
    im.show()
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
    if response.content.__len__() > 6000:
        print("登陆成功!")
        SaveCookie(session)         #保存此次登录的cookie
        return True
    else:
        print("登录失败，请检查账号密码及验证码")
        return False

def SaveCookie(session):
    with open(".cookie",'w') as f:
        for key,val in session.cookies.get_dict().items():
            f.write(key+":"+val+'\n')

def GetCookie(session):
    cookie = {}
    if ".cookie" not in os.listdir():
        return cookie
    with open(".cookie",'r') as f:
        for line in f:
            line = line.replace('\n','').replace('\r','')
            item = line.split(':')
            cookie[item[0]] = item[1]
    return cookie

#拉取专业课课表
def GetSpecialCourseList(session):
    #获取专业选课页面，用以获得院系编号
    selectPage = session.post(host+"student/elective/courseList.do",{'method':'specialityCourseList'})
    selectPageSoup = BeautifulSoup(selectPage.content,"html.parser",from_encoding='utf-8')
    majorID = selectPageSoup.find('select',{'id':'specialityList'}).find('option')['value']
    
    #返回的课程列表，存储课程编号对应的courseID
    courseIdList=[]
    #构造拉取课程信息的请求体
    courseList_reqdata={}
    courseList_reqdata['method']="specialityCourseList"
    courseList_reqdata['specialityCode']=majorID     #专业代号，计科为221
    print("请输入对应年级(如2019)")
    grade = input()
    courseList_reqdata['courseGrade']=grade
    courseList = requests.models.Response()
    while True:
        try:
            courseList = session.post(host+"student/elective/courseList.do",courseList_reqdata)
        except requests.exceptions.ConnectionError:
            print("连接超时，正在尝试重新连接")
            time.sleep(1)
        else:
            break
    soup = BeautifulSoup(courseList.content,"html.parser",from_encoding='utf-8')
    trs = soup.find_all('tr',{'class':'TABLE_TR_01'})
    print("序号\t课程号\t\t课程名\t\t\t学分\t学时\t类型\t开课院系")
    for tr in trs:
        tds = tr.find_all('td')
        courseNo = tds[0].find('a').find('u').string
        if(tds[1].string.__len__()<=7):
            print(str(trs.index(tr)+1)+'\t'+courseNo+'\t'+tds[1].string+'\t\t'+tds[2].string+'\t'+tds[3].string+'\t'+tds[4].string+'\t'+tds[6].string)
        else:
            print(str(trs.index(tr)+1)+'\t'+courseNo+'\t'+tds[1].string+'\t'+tds[2].string+'\t'+tds[3].string+'\t'+tds[4].string+'\t'+tds[6].string)
        click_td = tr.find('td',{'onclick':True})
        if click_td==None:
            courseIdList.append("")
            pass
        else:
            js = click_td['onclick']
            args = js.split(',')
            courseID = args[4][0:5]
            courseIdList.append(courseID)
    return courseIdList

#拉取通识课课表
def GetDiscussRenewCourseList(session):
    selectPage = session.get(host+"student/elective/courseList.do?method=discussRenewCourseList&campus=%E4%BB%99%E6%9E%97%E6%A0%A1%E5%8C%BA")
    soup = BeautifulSoup(selectPage.content,"html.parser",from_encoding='utf-8')

    #返回的课程列表，存储课程编号对应的courseID
    courseIdList = []
    trs = soup.find_all('tr',re.compile('TABLE_TR_0[12]'))
    print("序号\t课程号\t\t课程名\t\t\t\t\t\t学分\t限额\t已选")
    for tr in trs:
        tds = tr.find_all('td')
        courseNo = tds[0].find('a').find('u').string
        if(tds[2].string.__len__()<=7):
            print(str(trs.index(tr)+1)+'\t'+courseNo+'\t'+tds[2].string+'\t\t\t\t\t'+tds[3].string+'\t'+tds[6].string+'\t'+tds[7].string)
        elif(tds[2].string.__len__()<=11):
            print(str(trs.index(tr)+1)+'\t'+courseNo+'\t'+tds[2].string+'\t\t\t\t'+tds[3].string+'\t'+tds[6].string+'\t'+tds[7].string)
        elif(tds[2].string.__len__()<=15):
            print(str(trs.index(tr)+1)+'\t'+courseNo+'\t'+tds[2].string+'\t\t\t'+tds[3].string+'\t'+tds[6].string+'\t'+tds[7].string)
        else:
            print(str(trs.index(tr)+1)+'\t'+courseNo+'\t'+tds[2].string+'\t\t'+tds[3].string+'\t'+tds[6].string+'\t'+tds[7].string)
        arg1 = tds[0].find('a')['href'].split('(')
        arg2 = arg1[1].split(',')
        courseIdList.append(arg2[0])
    return courseIdList


#接受两个参数，第一个为课程ID，第二个为每次抢课时间间隔
def GrabSpecialCourse(courseID,interval=0):
    connectionFailedFlag = False
    while(True):
        selectCourse_reqdata={}
        selectCourse_reqdata['method']="addSpecialitySelect"
        selectCourse_reqdata['classId']=str(courseID)
        selectResult = requests.models.Response()
        while True:
            try:
                selectResult = s.post(host+'student/elective/selectCourse.do',selectCourse_reqdata)
            except requests.exceptions.ConnectionError:
                connectionFailedFlag=True
                print("连接超时，正在尝试重新连接")
                time.sleep(1)
            else:
                if connectionFailedFlag:
                    connectionFailedFlag=False
                    print("重连成功，继续为您抢课")
                break
        soup = BeautifulSoup(selectResult.content,"html.parser",from_encoding='utf-8')
        for tag in soup.find_all('div'):
            if tag.get('id')=="successMsg":
                print("抢课成功！")
                return
            elif tag.get('id')=="errMsg":   
                if tag.string.find("已经")!=-1:
                    print("您已经抢到该课程啦~")
                    exit()
                elif tag.string.find("错误")!=-1:
                    print("出现错误，添加失败")
                    exit()
                else:
                    print("当前班级已满，仍在为您持续抢课")
            else:
                pass
        if interval!=0:
            time.sleep(interval)

#接受两个参数，第一个为课程ID，第二个为每次抢课时间间隔
def GrabDiscussRenewCourse(courseID,interval=0):
    connectionFailedFlag = False
    while(True):
        selectResult = requests.models.Response()
        while True:
            try:
                selectResult = s.get(host+'student/elective/courseList.do?method=submitDiscussRenew&classId='+str(courseID)+'&campus=%E4%BB%99%E6%9E%97%E6%A0%A1%E5%8C%BA')
            except requests.exceptions.ConnectionError:
                connectionFailedFlag=True
                print("连接超时，正在尝试重新连接")
                time.sleep(1)
            else:
                if connectionFailedFlag:
                    connectionFailedFlag=False
                    print("重连成功，继续为您抢课")
                break
        soup = BeautifulSoup(selectResult.content,"html.parser",from_encoding='utf-8')
        script = soup.find_all('script')[1]
        # print(str(script))
        if re.search("班级已满",str(script)) is not None:
            print("当前班级已满，仍在为您持续抢课")
        elif re.search("你已经选过这个班级了",str(script)) is not None:
            print("添加失败，你已经选过这个班级了")
            exit()
        elif re.search("操作成功",str(script)) is not None:
            print("抢课成功！课程存在时间冲突，已自动生成免修不免考申请")
            exit()
        elif re.search("课程选择成功",str(script)) is not None:
            print("抢课成功！")
            exit()
        if interval!=0:
            time.sleep(interval)

if __name__ == '__main__':
    s = requests.session()
    if not login(s):
        exit()

    print("请选择课程类型：")
    print("1.通识课 2.公选课 3.专业课")
    courseType = input()
    courseIdList = []
    if int(courseType) == 1:
        courseIdList = GetDiscussRenewCourseList(s)
    elif int(courseType) == 2:
        courseIdList = GetSpecialCourseList(s)
    elif int(courseType) == 3:
        courseIdList = GetSpecialCourseList(s)
    else:
        print("课程类型输入有误")
        exit()

    print("请输入需要抢课的课程序号（非课程号）")
    courseNo = input()
    if int(courseNo)<=0 or int(courseNo)>courseIdList.__len__():
        print("输入序号有误，请重新输入")
    else:
        courseID = courseIdList[int(courseNo)-1]
        if courseID=="":
            print("你已经选过该门课啦~换个课程吧")
        else:
            if int(courseType) == 1:
                GrabDiscussRenewCourse(courseID,3)
            if int(courseType) == 2:
                GrabSpecialCourse(courseID,300)
            if int(courseType) == 3:
                GrabSpecialCourse(courseID,300)