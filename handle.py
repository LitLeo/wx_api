# -*- coding: utf-8 -*-
# filename: handle.py
import hashlib
import reply
import receive
import web
import time
from MySQL import MySQL
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

#数据库连接参数
dbconfig = {'host':'localhost',
	'port': 3306,
	'user':'root',
	'passwd':'831900ywg_3E',
	'db':'sport',
	'charset':'utf8'}

class SportInfo(object):
    def __init__(self):
        self.date = ""
        self.sport_type = ""
        self.num = 0.0
        self.db_name = "sport_info"

    def convert_to_query(self, sport_type, num):
        self.date = time.strftime("%Y-%m-%d", time.localtime())
        self.sport_type = sport_type
        self.num = num
        query = "insert into " + self.db_name + " (date, type, num) values ('" + self.date + "', '"+ self.sport_type+"', '"+ self.num  +"');"
        return query

class Handle(object):
    def __init__(self):
        self.log_file = open("msg.log", "a")
        self.sport_info = SportInfo()
        self.mysql_handle = MySQL(dbconfig)

    def month_report(self):
        date_month = time.strftime("%Y-%m", time.localtime())
        q = "SELECT count(*) from sport_info WHERE date_format(date,'%Y-%m')='"+date_month+"' "
       #  print(q)
        self.mysql_handle.query(q)
        report = date_month + ": 运动次数 " + str(self.mysql_handle.fetchOneRow()[0]) + "\n"

        q = "SELECT type, sum(num) from sport_info WHERE date_format(date,'%Y-%m')='"+date_month+"' GROUP BY type"
        #print(q)
        self.mysql_handle.query(q)
        results = self.mysql_handle.fetchAllRows()
        item_report = ""
        for row in results :
            item_report = item_report + row[0] + ": " + str(int(row[1])) + "\n"

        return report + item_report

    def POST(self):
        try:
            webData = web.data()
            print "Handle Post webdata is ", webData
            #后台打日志
            recMsg = receive.parse_xml(webData)
            if isinstance(recMsg, receive.Msg) and recMsg.MsgType == 'text':
                toUser = recMsg.FromUserName
                fromUser = recMsg.ToUserName
                content = recMsg.Content
                # print(content)

                reply_content = ""
                split_res = content.split()
                if len(split_res) <> 2 :
                    reply_content = "format is wrong!"
                else :
                    # content to mysql_query
                    query = self.sport_info.convert_to_query(split_res[0], split_res[1])
                    #print(query)
                    # self.log_file.write("query:" + query)
                    if query <> "" :
                        res =  self.mysql_handle.insert(query)
                        #if self.mysql_handle.insert(query) <> False:
                        if res :
                            reply_content = self.month_report()
                        else :
                            reply_content = "insert db failed!"

                date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                self.log_file.write(date + ": " + content + "\n")
                replyMsg = reply.TextMsg(toUser, fromUser, reply_content)
                return replyMsg.send()
            else:
                print "暂且不处理"
                return "success"
        except Exception, Argment:
            return Argment

#si = SportInfo()
#print(si.convert_to_query("骑车 10"))
h = Handle()
print (h.month_report())
