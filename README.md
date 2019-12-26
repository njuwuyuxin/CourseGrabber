## 南京大学教务网抢课系统

#### 工具依赖
脚本中使用了一些python库，主要有
- requests
- beautifulsoup

可以使用pip进行安装
```
pip install requests
pip install bs4
```
如果发现有其他依赖缺失，按提示自行安装即可

#### 配置文件
使用该软件登陆系统可以使用配置文件存储用户信息避免重复输入
在根目录下创建user.cfg，格式如下
```
userName:181220000
password:abcDEF
```