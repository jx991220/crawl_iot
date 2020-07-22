from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pymysql.cursors
import re
import Levenshtein


def judgetype(banner, ftbl):                          # 设备类型判断
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


def judgeprinterbrand(cursor, ftbl, ftbbl):            # 打印机品牌判断
    brand_list = []
    sql = "select brand_chinese,brand_english from printer_brand"
    cursor.execute(sql)
    result = cursor.fetchall()
    for e in ftbl:
        for i in range(0, len(result)):
            res = result[i]
            eng = res['brand_english']
            chn = res['brand_chinese']
            if e == eng:
                brand_list.append(chn)
                break
            if i == len(result) - 1:
                ftbbl.append(e)
    brand = max(brand_list, key=brand_list.count)       # 返回列表中重复最多的元素（防止同时出现两个品牌关键词）
    return brand


def judgenvrbrand(cursor, ftbl, ftbbl):                 # 监控摄像机品牌判断
    brand_list = []
    sql = "select brand_chinese,brand_english from nvr_brand"
    cursor.execute(sql)
    result = cursor.fetchall()
    for e in ftbl:
        for i in range(0, len(result)):
            res = result[i]
            eng = res['brand_english']
            chn = res['brand_chinese']
            if e == eng:
                brand_list.append(chn)
                break
            if i == len(result)-1:
                ftbbl.append(e)
    brand = max(brand_list, key=brand_list.count)        # 返回列表中重复最多的元素（防止同时出现两个品牌关键词）
    return brand


def judgeemptybrand(cursor, ftbl, ftbbl, type):          # 设备类型未知时的品牌判断
    brand_list = []
    sql = "select brand_chinese,brand_english,type from empty_brand"
    cursor.execute(sql)
    result = cursor.fetchall()
    for e in ftbl:
        for i in range(0, len(result)):
            res = result[i]
            eng = res['brand_english']
            chn = res['brand_chinese']
            brand_type = res['type']
            if e == eng:
                brand_list.append(chn)
                type = brand_type
                break
            if i == len(result)-1:
                ftbbl.append(e)
    brand = max(brand_list, key=brand_list.count)        # 返回列表中重复最多的元素（防止同时出现两个品牌关键词）
    return brand, type


def sift(type, brand, cursor):                           # 从数据库中筛选出对应品牌或类型的设备
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


def judgerepeat(list, element):                # 判断关于设备型号的描述词是否重复
    for e in list:
        if e == element:
            return 0, list
    list.append(element)
    return 1, list


def preselectmodel(ftbll, list):            # 选出设备型号描述词并按顺序组合
    model = ''
    ifrepeat = []
    for everyftbll in ftbll:
        judge, ifrepeat = judgerepeat(ifrepeat, everyftbll)
        if judge == 0:
            continue
        else:
            for everylist in list:
                if everyftbll == everylist:
                    if model:
                        model = model + ' ' + everyftbll
                    else:
                        model = model + everyftbll
                    ftbll.remove(everyftbll)
    return model, ftbll


def judgemodel(ftbll, premodel, srm):                # 判断设备型号
    model = '未知'
    tms = 0.7
    for everyftbll in ftbll:
        if premodel:
            preadd = premodel + ' ' + everyftbll
        else:
            preadd = premodel + everyftbll
        for everysrm in srm:
            if Levenshtein.ratio(preadd, everysrm) > tms:             # 选取相似度最高的型号
                model = everysrm
                tms = Levenshtein.ratio(preadd, everysrm)
    return model


def getallinfo(type, brand, model, cursor):                       # 通过已知信息获取其余信息
    description = '未知'
    sql = "select product_type,brand_chinese,product_model,description from crawl_iot"
    cursor.execute(sql)
    result = cursor.fetchall()
    for res in result:
        if model is not '未知':
            if res['product_model'] == model:
                type = res['product_type']
                brand = res['brand_chinese']
                description = res['description']
    return type, brand, model, description


def main():                                          # 程序主函数
    stop_words = stopwords.words('english')          # 引入停用词
    list =['deskjet', 'mfp', 'business', 'qms', 'gepro', 'gicolor', 'inkjet', 'laserjet', 'officejet', 'pagepro',
           'magicolor', 'pagewide', 'photosmart', 'color', 'pro', 'optra', 'aficio', 'designjet', 'docucentre',
           'docuprint', 'ipsio', 'plus', 'workcentre', 'phaser', 'stylus', 'photo', 'inter', 'xd', 'sp', 'aculaser',
           'sty', 'office', 'pixma', 'imageclass']    # 设备型号描述词列表
    for w in ['td', 'border', 'view', 'taboff', 'content-type', 'post', 'settings', 'product', 'web',
              'services', 'tabs', 'en', '1.0', 'script', 'id', 'mfp', 'top', 'number', 'write', 'edge', 'gzip', 'gmt',
              'read', '1.1', 'language', 'get', 'put', 'doctype', 'status', 'menu', 'info', 'information', 'page',
              'pages', 'click', 'use', 'value', 'links', 'install', 'device', '0px', 'name', 'tr', 'div', 'table',
              'text', 'type', 'javascript', 'body', 'html', 'http', 'style', 'h3', 'nbsp', 'src', 'href', 'form', 'h1',
              'title', 'width', 'item', 'ssi', 'class', 'tab', 'img', 'head', 'xml', 'ip', 'version', 'utf-8', 'public',
              'content', 'server', 'charset', 'u003e', 'u003c', 'timestamp', 'data', 'ftp', 'input', 'print', 'colspan',
              'css', 'rel', 'link', 'support', 'supplies', 'auth', 'subtitle', 'order', 'submit', 'network', 'summary',
              'index.htm', 'method', 'memory', 'banner']:              # 剔除无用词
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
    connection = pymysql.connect(**config)                         # 连接数据库
    try:
        with connection.cursor() as cursor:
            sql = "select ip,banner from get_banner"
            cursor.execute(sql)
            result = cursor.fetchall()
            for i in range(0, 7):
                res = result[i]
                ip = res['ip']
                example = res['banner']
                example_lower = example.lower()                  # 转化成小写
                word_tokens = word_tokenize(example_lower)       # tokenize分词
                banner = []
                ftbl = []
                ftbll = []
                for eve in word_tokens:
                    ever = re.split(r'[=\\/]', eve)               # 将\=/三种特殊符号删去并由此分割开
                    for w in ever:
                        if bool(re.search(r'\d', w)) or bool(re.search('[a-z]', w)):  # 判断字符串中是否含有数字或字母，没有的直接删去
                            if w not in stop_words:             # 去除停用词
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
                premodel, ftbll = preselectmodel(ftbll, list)
                model = judgemodel(ftbll, premodel, srm)
                type, brand, model, description = getallinfo(type, brand, model, cursor)
                print('\nIP地址%s对应的设备信息如下：' % ip)
                print('设备类型:%s' % type)
                print('设备品牌:%s' % brand)
                print("设备型号:%s" % model)
                print("描述信息:%s" % description)
            connection.commit()

    finally:
        connection.close()


if __name__ == "__main__":
    main()
