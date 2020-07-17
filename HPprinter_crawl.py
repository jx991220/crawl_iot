import requests
from lxml import etree
import pymysql.cursors
import re


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
        for i in range(1,10):
            html = requests.get("https://www.hpstore.cn/catalogsearch/result/index/?cat=8&p=%d&q=打印机"%i)
            html.encoding = 'utf-8'
            for j in range(1,13):
                data = etree.HTML(html.text).xpath('/html/body/div[2]/main/div[3]/div[1]/div[3]/div[2]/ol/li[%d]/div/div[2]/strong/a/text()'%j)
                if not data:
                    pass
                else:
                    str = data[0]
                    patt1 = re.compile(r"(HP)(.*)")
                    filter1 = re.findall(patt1, str)[0]
                    patt2 = re.compile(r"[^\u4e00-\u9fa5]+")
                    patt3 = re.compile(r"[\u4e00-\u9fa5]+")
                    filter2 = re.findall(patt2, filter1[1])[0]
                    description = re.findall(patt3, filter1[1])
                    insert_description = description[0]
                    branden = 'HP'
                    brandcn = '惠普'
                    insert_model = filter2
                    insert_type = '打印机'
                    data_sql = 'INSERT INTO crawl_iot(product_type,brand_chinese,brand_english,product_model,description) VALUES (%s,%s,%s,%s,%s)'
                    cursor.execute(data_sql, (insert_type,brandcn,branden,insert_model,insert_description))
    connection.commit()
finally:
    connection.close()
