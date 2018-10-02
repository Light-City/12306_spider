import requests
class login_spider(object):
    def __init__(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
        }
        sess = requests.Session()
        self.headers=headers
        self.sess = sess

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
    def downloadCode(self):
        code_url = 'https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand&0.5579044251920726'
        res = self.sess.get(code_url, headers=self.headers)
        if res.status_code == 200:
            with open('img_code/code.jpg', "wb") as f:
                f.write(res.content)
                print("验证码下载成功")
                return True
        else:
            print("图片下载失败,正在重试....")
            self.downloadCode()
    def main_Login(self):
        login_url = 'https://kyfw.12306.cn/passport/web/login'
        data_post = {
            "username":"输入您的用户名",
            "password": "输入您的密码",
            "appid": "otn"
        }
        res = self.sess.post(login_url, headers=self.headers, data=data_post)
        print(res.json())

    def login(self):
        login_url = 'https://kyfw.12306.cn/otn/index/initMy12306'
        res = self.sess.get(login_url,headers=self.headers)
        print(res)

    def main(self):
        self.downloadCode()
        res = self.verifi_Code()
        if res==True:
            self.main_Login()
            self.tk_Auth()
            self.login()
        else:
            print("验证失败！")
# 测试登陆
# ls = login_spider()
# ls.main()