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
            sql = "select brand,model from tms"
            cursor.execute(sql)
            result = cursor.fetchall()
            Qs =['ids-2pt7t20mx-d4/t3(11-77mm)', 'dh-ipc-hfw4433k-i6', 'c3w-1b2wfr',
                 'laser 108a ', 'l15168', 'dcp-7190dw', 'lbp613cdw', '2108b',
                 'ja-c9c', 'd2120-10-i-p', 'ipc-s214-ir', 'tl-ipc42a-4', 'snz-5200p',
                 'ssc-dc488p', 'wv-cp504ch', 'lvc-sx811hp', 'lj6100', 'cp9502dn', 'c5400n', 'x5150']
            xmn =[]
            for res in result:
                model = res['model']
                if Levenshtein.ratio(model, Qs[18])>=0.9:
                    xmn.append(model)
            print(xmn)
            print(len(xmn))
    finally:
        connection.close()


if __name__ == "__main__":
     main()
