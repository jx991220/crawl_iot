from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pymysql.cursors
import re
import Levenshtein


def judgetype(banner, ftbl):
    type = ''
    for every in banner:
        if every == 'printer':
            type = '打印机'
            continue
        if every == 'nvr':
            type = '监控摄像机'
            continue
        else:
            ftbl.append(every)
    return type


def judgeprinterbrand(cursor, ftbl, ftbbl):
    brand = ''
    sql = "select brand_chinese,brand_english from printer_brand"
    cursor.execute(sql)
    result = cursor.fetchall()
    for e in ftbl:
        for i in range(0, len(result)):
            res = result[i]
            eng = res['brand_english']
            chn = res['brand_chinese']
            if e == eng:
                brand = chn
                break
            if i == len(result) - 1:
                ftbbl.append(e)
    return brand


def judgenvrbrand(cursor, ftbl, ftbbl):
    brand = ''
    sql = "select brand_chinese,brand_english from nvr_brand"
    cursor.execute(sql)
    result = cursor.fetchall()
    for e in ftbl:
        for i in range(0, len(result)):
            res = result[i]
            eng = res['brand_english']
            chn = res['brand_chinese']
            if e == eng:
                brand = chn
                break
            if i == len(result)-1:
                ftbbl.append(e)
    return brand


def judgeemptybrand(cursor, ftbl, ftbbl, type):
    brand = ''
    sql = "select brand_chinese,brand_english,type from empty_brand"
    cursor.execute(sql)
    result = cursor.fetchall()
    for e in ftbl:
        for i in range(0,len(result)):
            res = result[i]
            eng = res['brand_english']
            chn = res['brand_chinese']
            brand_type = res['type']
            if e == eng:
                brand = chn
                type = brand_type
                break
            if i == len(result)-1:
                ftbbl.append(e)
    return brand, type


def sift(type,brand,cursor):
    srm = []
    sql = "select product_type,brand_chinese,product_model from crawl_iot"
    cursor.execute(sql)
    result = cursor.fetchall()
    if type and brand:
        for res in result:
            if type == res['product_type'] and brand == res['brand_chinese']:
                srm.append(res['product_model'])
    if type and not brand:
        for res in result:
            if type == res['product_type']:
                srm.append(res['product_model'])
    if brand and not type:
        for res in result:
            if brand == res['brand_chinese']:
                srm.append(res['product_model'])
    return srm

def main():
    stop_words = stopwords.words('english')
    for w in ['td', 'border', 'view', 'taboff', 'content-type', 'post', 'settings', 'product', 'web',
              'services', 'tabs', 'en', '1.0', 'script', 'id', 'mfp', 'top', 'number', 'write', 'edge', 'gzip', 'gmt',
              'read', '1.1', 'language', 'get', 'put', 'doctype', 'status', 'menu', 'info', 'information', 'page', 'pages',
              'click', 'use', 'value', 'links', 'install', 'device', '0px', 'name', 'tr', 'div', 'table', 'text', 'type',
              'javascript', 'body', 'html', 'http', 'style', 'h3', 'nbsp', 'src', 'href', 'form', 'h1', 'title', 'width',
              'item', 'ssi', 'class', 'tab', 'img', 'head', 'xml', 'ip', 'version', 'utf-8', 'public', 'content', 'server', 'charset',
              'u003e', 'u003c', 'timestamp', 'data', 'ftp', 'input', 'print', 'colspan', 'css', 'rel', 'link', 'support',
              'supplies', 'auth', 'subtitle', 'order', 'submit', 'network', 'summary', 'index.htm', 'method', 'memory', 'banner']:
        stop_words.append(w)
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
            sql = "select ip,banner from get_banner"
            cursor.execute(sql)
            result = cursor.fetchall()
            for i in range(0, 1):
                res = result[i]
                ip = res['ip']
                example = res['banner']
                example_lower = example.lower()
                word_tokens = word_tokenize(example_lower)
                banner = []
                ftbl = []
                ftbll = []
                for eve in word_tokens:
                    ever = re.split(r'[=\\/]',eve)
                    for w in ever:
                        if bool(re.search(r'\d', w)) or bool(re.search('[a-z]', w)):  #判断字符串中是否含有数字或字母，没有的直接删去
                            if w not in stop_words:             #去除停用词
                                if len(w) > 1:
                                    banner.append(w)
                type = judgetype(banner, ftbl)
                if not type:
                    type = '未知'
                if type == '打印机':
                    brand = judgeprinterbrand(cursor, ftbl, ftbll)
                if type == '监控摄像机':
                    brand = judgenvrbrand(cursor, ftbl, ftbll)
                if type == '未知':
                    brand, type = judgeemptybrand(cursor, ftbl, ftbll, type)
                if not brand:
                    brand = '未知'
                srm = sift(type, brand, cursor)
                print(ftbll)
                print('IP地址%s对应的设备信息如下：' % ip)
                print('设备类型:%s' % type)
                print('设备品牌:%s' % brand)
            connection.commit()

    finally:
        connection.close()


if __name__ == "__main__":
     main()