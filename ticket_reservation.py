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
ts = ticker_Spider()

pt = ts.print_TicketInfo()
print(pt)






