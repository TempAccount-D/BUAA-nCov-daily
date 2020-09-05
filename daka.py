# -*- coding: utf-8 -*-
import requests, json, re
import time, datetime, os, sys
import getpass
from halo import Halo
from apscheduler.schedulers.blocking import BlockingScheduler

class DaKa(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.login_url = "https://app.buaa.edu.cn/uc/wap/login/check" #?redirect=https%3A%2F%2Fapp.buaa.edu.cn%2Fsite%2Fncov%2Fxisudailyup"
        self.base_url = "https://app.buaa.edu.cn/site/ncov/xisudailyup"
        self.save_url = "https://app.buaa.edu.cn/xisuncov/wap/open-report/save"
        self.sess = requests.Session()

    def check(self):
        data = {
            'username': self.username,
            'password': self.password
            # 'execution': execution,
            # '_eventId': 'submit'
        }
        info = {
            'sfzx': 1,
            'tw': 1,
            'area': u"北京市 海淀区",
            'city': u"北京市",
            'province': u"北京市",
            'address': u"北京市海淀区花园路街道北京航空航天大学电子科学与技术系北京航空航天大学学院路校区",
            'geo_api_info': u"{\"type\":\"complete\",\"info\":\"SUCCESS\",\"status\":1,\"VDa\":\"jsonp_903390_\",\"position\":{\"Q\":39.9804,\"R\":116.35097000000002,\"lng\":116.35097,\"lat\":39.9804},\"message\":\"Get ipLocation success.Get address success.\",\"location_type\":\"ip\",\"accuracy\":null,\"isConverted\":true,\"addressComponent\":{\"citycode\":\"010\",\"adcode\":\"110108\",\"businessAreas\":[{\"name\":\"五道口\",\"id\":\"110108\",\"location\":{\"Q\":39.99118,\"R\":116.34157800000003,\"lng\":116.341578,\"lat\":39.99118}},{\"name\":\"牡丹园\",\"id\":\"110108\",\"location\":{\"Q\":39.977965,\"R\":116.37172700000002,\"lng\":116.371727,\"lat\":39.977965}}],\"neighborhoodType\":\"生活服务;生活服务场所;生活服务场所\",\"neighborhood\":\"北京航空航天大学\",\"building\":\"北京航空航天大学电子科学与技术系\",\"buildingType\":\"科教文化服务;学校;高等院校\",\"street\":\"学院路\",\"streetNumber\":\"37号\",\"country\":\"中国\",\"province\":\"北京市\",\"city\":\"\",\"district\":\"海淀区\",\"township\":\"花园路街道\"},\"formattedAddress\":\"北京市海淀区花园路街道北京航空航天大学电子科学与技术系北京航空航天大学学院路校区\",\"roads\":[],\"crosses\":[],\"pois\":[]}",
            'sfcyglq': 0,
            'sfyzz': 0,
            'qtqk': "",
            'askforleave': 0
        }

        res1 = self.sess.post(url=self.login_url, data=data)
        tt = res1.content.decode()
        while '操作成功' not in res1.content.decode():
            time.sleep(15)
            res1 = self.sess.post(url=self.login_url, data=data)
        info_json = info #json.dumps(info)
        res = self.sess.post(self.save_url, data=info_json)
        while '操作成功' not in res.content.decode() and '还未到打卡时间' not in res.content.decode():
            time.sleep(15)
            res = self.sess.post(self.save_url, data=info_json)
        print('打卡成功')
        return self.sess

    # def _rsa_encrypt(self, password_str, e_str, M_str):
    #     password_bytes = bytes(password_str, 'ascii')
    #     password_int = int.from_bytes(password_bytes, 'big')
    #     e_int = int(e_str, 16)
    #     M_int = int(M_str, 16)
    #     result_int = pow(password_int, e_int, M_int)
    #     return hex(result_int)[2:].rjust(128, '0')


# Exceptions 
class LoginError(Exception):
    """Login Exception"""
    pass

class RegexMatchError(Exception):
    """Regex Matching Exception"""
    pass

class DecodeError(Exception):
    """JSON Decode Exception"""
    pass


def main(username, password):
    print("\n[Time] %s" %datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print(" 打卡任务启动")
    spinner = Halo(text='Loading', spinner='dots')
    spinner.start('正在新建打卡实例...')
    dk = DaKa(username, password)
    spinner.succeed('已新建打卡实例')

    dk.check()


if __name__=="__main__":
    if os.path.exists('./config.json'):
        configs = json.loads(open('./config.json', 'r').read())
        username = configs["username"]
        password = configs["password"]
        hour = configs["schedule"]["hour"]
        minute = configs["schedule"]["minute"]
    else:
        username = input("👤 北航统一认证用户名: ")
        password = getpass.getpass('🔑 北航统一认证密码: ')
        print("⏲  请输入定时时间（默认每天7:05）")
        hour = input("\thour: ") or '7,11,18'
        minute = input("\tminute: ") or 5

    # Schedule task
    scheduler = BlockingScheduler()
    scheduler.add_job(main, 'cron', args=[username, password], hour=hour, minute=minute)
    print('⏰ 已启动定时程序，每天 ',hour, ': %02d 为您打卡' %(int(minute)))
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
