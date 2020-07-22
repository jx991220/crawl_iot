import pymysql.cursors
import Levenshtein


def main():
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
            sql = "select brand_chinese,product_model from crawl_iot"
            cursor.execute(sql)
            result = cursor.fetchall()
            brand_list = ['海康威视', '大华', '萤石', '乔安', '华为', '宇视', '创维', '小米', '普联', '360', '欧瑞博',
                          '乐橙', '三星', '索尼', '全瑞威视', '松下', '科达', '联想', 'LG', '惠普', '爱普生', '兄弟',
                          '佳能', '富士施乐', '奔图', '理光', 'OKI', '京瓷', '利盟', '柯尼卡美能达', '方正']
            srm = []
            pp = []
            count = 0
            for res in result:
                    if brand_list[19] == res['brand_chinese']:
                        srm.append(res['product_model'])
            for res in result:
                if Levenshtein.ratio(srm[1], res['product_model'])>=1:
                    pp.append(res['product_model'])
            print("*")
            print(len(pp))
            for p in pp:
                for sr in srm:
                    if p == sr:
                        count = count + 1
            print("交集")
            print(count)

    finally:
        connection.close()


if __name__ == "__main__":
     main()
