
# 实时车票查询及登陆CTC

![](http://p20tr36iw.bkt.clouddn.com/terminal_res.png)

## 0.说在前面

又是一年国庆节，祝福各位国庆节快乐，玩的开心！

从大学至今，唯一一个宅的国庆，让自己多点思考，少点外出。

这几天也没更文，忙于之前的小游戏pygame的开发，这方面的软文，随后几日更新。

前两天老表发了个12306软文，忽然想起，自己的公众号也好久没更新爬虫系列了，今天就开始琢磨一下，本次的爬虫主要有两大方面的功能。

【**第一**】 如何登陆12306

【**第二**】 如何做到实时车票查询

当你们在排队等候服务器响应的时候，我已经买下票了；

当你们在抢购最后一张车票的时候，已经没了；

当你们在等待放票的时候，我已经调整好买票方案了。

哈哈，有点难拉仇恨。。那么没事，学好接下来的操作，会有助于你解决车票麻烦。

**车票查到了，离心中的远方还远？** 

**Clos To Close**

## 1.项目架构

![](http://p20tr36iw.bkt.clouddn.com/12306_main1.png)

```python
login_spider        # 登陆类 用于12306全局登陆与管理 
    downloadCode    # 用于下载验证码
    verifi_Code     # 用于验证验证码是否输入成功
    main_Login      # 用于账户登陆
    get_Tk          # 登陆不成功的uamtk获取
    tk_Auth         # uamtk验证
    Login           # 真实登陆的跳转页面
    main            # 对上述代码的调用
ticker_spider
	get_StationName_En  # 获取出发站(抵达站)的字母简写
    search_Ticket       # 余票查询
    get_StationName     # 获取真实的中文表示的站点
    print_TicketInfo    # 打印余票查询结果
```

## 2.模拟登陆

### 2.1 登陆分析

【**验证码**】

分为以下几种情况：

第一种情况：验证码失败，会发现如下图校验结果，并且没有login的相关信息。

![](http://p20tr36iw.bkt.clouddn.com/login_failed.png)

第二种情况：用户名或密码错误，验证码正确，此时会出现login的信息

![](http://p20tr36iw.bkt.clouddn.com/login_preview.png)

![](http://p20tr36iw.bkt.clouddn.com/login.png)

第三种情况：登陆成功

![](http://p20tr36iw.bkt.clouddn.com/login_pre.png)

综上对于登陆的流程为，先下载验证码，手动验证，然后传入正确的用户名与密码，再进行登陆。

在登陆之前，12306会对你的验证码做校验，如果失败了，则直接不用管你的用户名与密码，所以先对验证码进行手动验证。然后再去用账户名与密码进行POST提交。

就这么简单？

当然不是，在你登陆后，最后会发现并未成功，搜索你的姓名并未发现，那么就得继续抓包。最后发现页面上需要uamtk验证，然后才可以进行正常的爬取操作。

接下来我们进入实战环节。

### 2.2 登陆实现

上述的页面访问较多，未了更方便的操作，本次采用requests里面的Session统一进行管理Cookie!

【**封装**】

```python
import requests
class login_spider(object):
    def __init__(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
        }
        sess = requests.Session()
        self.headers=headers
        self.sess = sess

```

【**验证码识别**】

当我们把图中的八个验证码进行点击的时候，会出现如下的坐标位置，那么我们只要将上述的坐标放进list中，当出现是哪个数据时候，就输入相应位置即可。输入的范围未(0~7) ,index从0开始！并且当验证码中有多个满足条件时候，输入一定要连着输入。

![](http://p20tr36iw.bkt.clouddn.com/all_verificode.png)

```python
def verifi_Code(self):
    verifi_url = 'https://kyfw.12306.cn/passport/captcha/captcha-check'
    verifi_axis = ['36,46','109,44','181,47','254,44','33,112','105,116','186,116','253,115']
    axis = input("请输入验证码坐标>> ")
    verifi_list = []
    for point in axis:
        verifi_list.append(verifi_axis[int(point)])
    axis_pos = ','.join(verifi_list)
    post_data = {
        "answer": axis_pos,
        "login_site": "E",
        "rand": "sjrand",
    }
    res = self.sess.post(url=verifi_url,headers=self.headers,data=post_data)
    res_json = res.json()
    if not res_json['result_code']=='4':
        print("验证失败")
        return False
    print(res_json)
    return True
```

【**登陆**】

```python
def main_Login(self):
    login_url = 'https://kyfw.12306.cn/passport/web/login'
    data_post = {
        "username":"输入您的用户名",
        "password": "输入您的密码",
        "appid": "otn"
    }
    res = self.sess.post(login_url, headers=self.headers, data=data_post)
    print(res.json())
```

【**登陆后验证**】

```python
def get_Tk(self):
    url_uamtk = 'https://kyfw.12306.cn/passport/web/auth/uamtk'
    data_uamtk = {"appid":"otn"}
    res = self.sess.post(url_uamtk,headers=self.headers,data=data_uamtk)
    print(res)
    res_json = res.json()
    data_verifi = {"tk":res_json["newapptk"]}
    return data_verifi
def tk_Auth(self):
    uamauthclient_url = "https://kyfw.12306.cn/otn/uamauthclient"
    res = self.sess.post(uamauthclient_url,headers=self.headers,data=self.get_Tk())
    print(res)
```

## 3.余票查询

### 3.1 查询分析

余票查询可以使用之前的Session管理的cookie用账户权限去抓取，也可以不用登陆就可以！

【**难点**】

- 查询的结果在哪
- 结果如何处理
- 查询途中的站点名字与字母简写如何处理

对于第一个难点，直接打开f12检查即可，会发现，如下图所示结果：

![](http://p20tr36iw.bkt.clouddn.com/res_res.png)

上图中的result里面的就是余票查询结果！

但是问题来了，查询出来的数据是这么的乱，那么怎么处理呢？到底哪一块表示始发站，硬座，软卧等？

这个处理是直接打开12306随机去是个查询结果，然后到了这个页面后，去搜索相应的车次，然后对应的一行就是显示界面的数据，最后发现各条数据之前从`|预订|`开始后面所有的数据是很规则的，那么前面的所有东西我直接通过正则匹配以`|预订|`分开，然后得到一个list，取index=1的数据即为我们需要的完整的数据，然后将其与页面数据进行匹配，最后就可以锁定哪个index表示硬座，软卧等。

在前面去请求数据的时候，会发现请求的数据并不是你所输入的中文，比如要查询重庆到成都，那么按照我们正常思路是直接用原字符串重庆与成都访问，但是实际不是，如下图：

![](http://p20tr36iw.bkt.clouddn.com/get_station.png)

看到了没，重庆对应CQW，成都对应CDW，中文又是怎么变为这些英文字母的呢？

针对这个问题，想必又是js作祟，于是打开js筛选，找到了有关station_name的相关js，如下两图：

![](http://p20tr36iw.bkt.clouddn.com/js_get.png)

![](http://p20tr36iw.bkt.clouddn.com/js_name.png)

发现了js里面中文后的下一个便是请求的英文字符串，那么我可以不费吹灰之力便可以拿到页面的js，然后先将`var='`去掉，并将js的末尾字符去掉，保留中间需要的，然后通过split对字符串分割成list，直接找到list当中请求的中文站点名字对应的index，然后加1获取真实的英文字符，然后再去请求相应的url即可！

![](http://p20tr36iw.bkt.clouddn.com/station_js.png)

![](http://p20tr36iw.bkt.clouddn.com/station_js_tail.png)

### 3.2 查询实现

【**封装**】

```python
import re
from prettytable import PrettyTable
from login_spider import login_spider
class ticker_Spider(object):
    def __init__(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
        }
        search_url = 'https://kyfw.12306.cn/otn/index/init'
        ls = login_spider()
        self.headers = headers
        self.ls = ls
        self.search_url = search_url
```

【**真实的站点名字**】

```python
def get_StationName_En(self,name):
    # 此处可以不需要session操作即可
    url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9069'
    res = self.ls.sess.get(url,headers=self.headers).text
    # print(res)
    with open('name.txt', 'w', encoding='utf-8') as f:
        # 去掉js的开头与结尾
        res = res.replace('var station_names =', '').replace('\'', '').replace(';', '')
        f.write(res)
    with open('name.txt', 'r', encoding='utf-8') as f:
        line = f.read()
        # print(line)
        sn_list = line.split('|')
        # print(sn_list)
        # print(sn_list.index(name))
        name_index = sn_list.index(name) + 1
        return sn_list[name_index]
```

【**余票查询**】

相应位置对应的数据信息表

```python
    '''
    1-车次  checi
    2/4-始发站 from_station
    3/5-终点站 to_station
    6-出发时间 from_time
    7-到达时间 to_time
    8-历时 total_time
    11-出发日期 from_datetime
    -16-高级软卧 high_soft
    -14-软卧 common_soft
    -11-无座 no_seat
    -4-动卧 move_down
    -5-商务座(特等座) special_seat
    -6-一等座 first_seat
    -7-二等座 second_seat
    -9-硬卧 hard_seat
    '''
```
```python
def search_Ticket(self):
    self.ls.main()
    # 'leftTicketDTO.train_date=2018-10-04&leftTicketDTO.from_station=CQW&leftTicketDTO.to_station=SHH&purpose_codes=ADULT'
    print("时间输入格式为>> 2018-10-02")
    raw_from_station = input("请输入出发地>> ")
    raw_to_station = input("请输入目的地>> ")
    train_date = input("请输入出发日>> ")
    # back_train_date = input("请输入返程日>> ")
    base_url = 'https://kyfw.12306.cn/otn/leftTicket/queryA?'
    from_station_En = self.get_StationName_En(raw_from_station)
    to_station_En = self.get_StationName_En(raw_to_station)

    url = base_url + 'leftTicketDTO.train_date=' + train_date + '&leftTicketDTO.from_station=' + from_station_En + '&leftTicketDTO.to_station=' + to_station_En + '&purpose_codes=ADULT'
    res = self.ls.sess.get(url,headers=self.headers).json()
    tick_res = res['data']['result']
    print(len(tick_res))
    search_res = len(tick_res)
    checi = []
    from_station = []
    to_station = []
    from_time = []
    to_time = []
    total_time = []
    from_datetime = []
    no_seat = []
    high_soft = []
    common_soft = []
    special_seat = []
    move_down = []
    first_seat = []
    second_seat = []
    hard_seat = []
    for each in tick_res:
        print("-----")
        # print(i)
        # a = i.find('预订')

        need_data = re.split(r'\|预订\|', each)[1]
        need_data = need_data.split('|')
        print(need_data)
        checi.append(need_data[1])
        from_station.append(self.get_StationName(need_data[2]))
        to_station.append(self.get_StationName(need_data[3]))
        from_time.append(need_data[6])
        to_time.append(need_data[7])
        total_time.append(need_data[8])
        from_datetime.append(need_data[11])
        high_soft.append(need_data[-16])
        common_soft.append(need_data[-14])
        no_seat.append(need_data[-11])
        move_down.append(need_data[-4])
        special_seat.append(need_data[-5])
        first_seat.append(need_data[-6])
        second_seat.append(need_data[-7])
        hard_seat.append(need_data[-9])
    return search_res,raw_from_station,raw_to_station,checi,from_station,to_station,from_time,to_time,total_time,from_datetime,high_soft,common_soft,no_seat,move_down,special_seat,second_seat,first_seat,hard_seat
```

【**余票展示**】

```python
def get_StationName(self,name):
    with open('name.txt', 'r', encoding='utf-8') as f:
        line = f.read()
        # print(line)
        sn_list = line.split('|')
        # print(sn_list)
        # print(sn_list.index(name))
        name_index = sn_list.index(name) - 1
        return sn_list[name_index]

def print_TicketInfo(self):
    search_res, raw_from_station, raw_to_station,checi, from_station, to_station, from_time, to_time, total_time, from_datetime, high_soft, common_soft, no_seat, move_down, special_seat, second_seat, first_seat, hard_seat = self.search_Ticket()

    pt = PrettyTable()
    print("---------从" + str(raw_from_station) + '到' + str(raw_to_station) + '共' + str(search_res) + '个车次'+ '---------')
    pt.add_column('车次', checi)
    pt.add_column('始发站', from_station)
    pt.add_column('终点站', to_station)
    pt.add_column('出发时间', from_time)
    pt.add_column('到达时间', to_time)
    pt.add_column('历时', total_time)
    pt.add_column('出发日期', from_time)
    pt.add_column('高级软卧', high_soft)
    pt.add_column('软卧', common_soft)
    pt.add_column('无座', no_seat)
    pt.add_column('动卧', move_down)
    pt.add_column('商务座', special_seat)
    pt.add_column('一等座', first_seat)
    pt.add_column('二等座', second_seat)
    pt.add_column('硬卧', hard_seat)
    return pt
```

## 4.运行展示

![](http://p20tr36iw.bkt.clouddn.com/terminal_res1.png)

![](http://p20tr36iw.bkt.clouddn.com/terminal_res.png)

![](http://p20tr36iw.bkt.clouddn.com/terminal_data.png)

验证上述查询结果，对比之后，正确！