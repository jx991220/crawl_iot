#-*- coding:utf-8 -*-
import requests
from lxml import etree
import pymysql.cursors

def getpage(i):
    connection = pymysql.connect(**config)
    with connection.cursor() as cursor:
        try:
            sql = "select page from haikang_page"
            cursor.execute(sql)
            result = cursor.fetchall()
            res = result[i]
            cookie = res['page']
            return cookie
            connection.commit()

        finally:
            connection.close()

def insertsql(data):
    data_sql = 'INSERT INTO crawl_iot(product_type,brand_chinese,brand_english,product_model,description) VALUES (%s,%s,%s,%s,%s)'
    cursor.execute(data_sql, data)

config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '1111',
    'db': 'iot',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
}
connection = pymysql.connect(**config)
try:
    with connection.cursor() as cursor:
       for i in range(0,98):
            page = getpage(i)
            html = requests.get("https://www.hikvision.com/cn/prlb_%s.html"%page)
            html.encoding = 'utf-8'
            etree_html = etree.HTML(html.text)
            for k in range(5,60,2):
                for j in range(1, 30):
                    model = etree_html.xpath('/html/body/div[5]/div/div[2]/div[%d]/div[2]/div[%d]/div[1]/div[2]/div[1]/text()'%(k,j))
                    if not model:
                        pass
                    else:
                        insert_model = model[0]
                        describe = etree_html.xpath(
                            '/html/body/div[5]/div/div[2]/div[%d]/div[2]/div[%d]/div[1]/div[2]/div[2]/text()'%(k,j))
                        insert_description = describe[0]
                    brandcn = '海康威视'
                    branden = 'hikvision'
                    insert_type = '监控摄像机'
                    value = (str(insert_type),str(brandcn),str(branden),str(insert_model),str(insert_description))
                    insertsql(value)
    connection.commit()
finally:
    connection.close()
