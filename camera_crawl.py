#-*- coding:utf-8 -*-
import requests
from lxml import etree
import pymysql.cursors

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
        for i in range(1,2):
            html = requests.get("http://detail.zol.com.cn/printer_advSearch/subcate792_1_m84_9_1_0_%d.html?#showc"%i)
            html.encoding = 'GBK'
            etree_html = etree.HTML(html.text)
            for j in range(1, 17):
                model = etree_html.xpath('/html/body/div[3]/form/div/div[2]/ul/li[%d]/dl/dt/a/text()'%j)
                if not model:
                    pass
                else:
                    insert_model = model[0][2:]
                    des1 = etree_html.xpath('/html/body/div[3]/form/div/div[2]/ul/li[%d]/dl/dd[1]/div/ul[1]/li[2]/text()' % j)
                    if not des1:
                        des1 = etree_html.xpath('/html/body/div[3]/form/div/div[2]/ul/li[%d]/dl/dd[1]/div/ul[1]/li[2]/text()' % j)
                    else:
                        insert_description = des1[0]
                brandcn = '松下'
                branden = 'panasonic'
                insert_type = '打印机'
                value = (str(insert_type),str(brandcn),str(branden),str(insert_model),str(insert_description))
                insertsql(value)
    connection.commit()
finally:
    connection.close()