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
        for i in range(1,74):
            html = requests.get("https://www.dahuatech.com/product/lists/13/%d.html#"%i)
            html.encoding = 'utf-8'
            etree_html = etree.HTML(html.text)
            for j in range(1, 10):
                model = etree_html.xpath('/html/body/div[1]/div[2]/div[3]/ul/li[%d]/span/a/h3/text()'%j)
                if not model:
                    pass
                else:
                    insert_model = model[0]
                    describe = etree_html.xpath('/html/body/div[1]/div[2]/div[3]/ul/li[%d]/span/a/p[1]/text()'%j)
                    insert_description = describe[0]
                brandcn = '大华'
                branden = 'Dahua'
                insert_type = '监控摄像机'
                value = (str(insert_type),str(brandcn),str(branden),str(insert_model),str(insert_description))
                insertsql(value)
    connection.commit()
finally:
    connection.close()