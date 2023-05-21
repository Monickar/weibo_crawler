import PySimpleGUI as sg   
from tkinter import messagebox 
import threading 
import datetime 
from lxml import etree
import json
import random
import os
import re  
import jieba 
import base64
from PIL import Image
from wordcloud import WordCloud 
import word_cloud
import matplotlib.pyplot as plt 
from datetime import datetime
import requests
import pymysql
import get_comment
# 建立数据库连接
def search():
    cnx = pymysql.connect(host='localhost', port=3306, user='root', password='root',
                        db='weibo', charset='utf8mb4')

    # 创建游标
    cursor = cnx.cursor()

    # 如果有表则删除
    drop_table_sql = '''
        drop table if exists hot_search;
    '''
    cursor.execute(drop_table_sql)

    # 创建一个名为hot_search的表
    create_table_sql = '''
        CREATE TABLE hot_search (
        date DATE NOT NULL,
        time TIME NOT NULL,
        hot_index INT NOT NULL,
        name VARCHAR(255) NOT NULL,
        raw_hot INT NOT NULL,
        label_name VARCHAR(255) NOT NULL,
        url VARCHAR(255) NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    '''
    cursor.execute(create_table_sql)
    # UA池
    ua_all = [
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/531.2 (KHTML, like Gecko) Chrome/41.0.872.0 Safari/531.2",
        "Mozilla/5.0 (compatible; MSIE 8.0; Windows CE; Trident/4.0)",
        "Mozilla/5.0 (Windows; U; Windows NT 6.0) AppleWebKit/531.11.4 (KHTML, like Gecko) Version/5.0.2 Safari/531.11.4",
        "Mozilla/5.0 (compatible; MSIE 7.0; Windows 98; Trident/3.1)",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 10.0; Trident/5.1)",
        "Opera/8.89.(Windows NT 10.0; lb-LU) Presto/2.9.175 Version/10.00",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/532.2 (KHTML, like Gecko) Chrome/51.0.800.0 Safari/532.2",
        "Opera/8.35.(Windows 98; Win 9x 4.90; sc-IT) Presto/2.9.186 Version/11.00",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.0 (KHTML, like Gecko) Chrome/55.0.809.0 Safari/535.0",
        "Opera/9.50.(Windows NT 6.0; xh-ZA) Presto/2.9.180 Version/10.00",
        "Mozilla/5.0 (compatible; MSIE 5.0; Windows NT 6.2; Trident/5.1)",
        "Opera/9.28.(Windows NT 5.0; yi-US) Presto/2.9.165 Version/11.00"]

    header = {
        "referer": "https://weibo.com/hot/search",
        "sec-ch-ua": "\"Chromium\";v=\"112\", \"Google Chrome\";v=\"112\", \"Not:A-Brand\";v=\"99\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "server-version": "v2023.04.13.2",
        "User-Agent": random.choice(ua_all),
        "x-requested-with": "XMLHttpRequest"
    }

    now = datetime.now()
    year = now.year
    month = str(now.month).zfill(2)
    day = str(now.day).zfill(2)
    hour = str(now.hour).zfill(2)
    minute = str(now.minute).zfill(2)
    second = str(now.second).zfill(2)
    date = f'{year}-{month}-{day}'
    time = f'{hour}:{minute}:{second}'
    
    response = requests.get('https://weibo.com/ajax/statuses/hot_band', headers=header)
    data = json.loads(response.text)['data']['band_list']
    
    for i in data:
        name = i['word']
        
        if 'raw_hot' in i:
            hot_index = i['realpos']
            raw_hot = i['raw_hot']
            label_name = i['label_name']
            detail_name = str(i['word_scheme']).replace('#', '%23')
            url = f'https://s.weibo.com/weibo?q={detail_name}'
            
            data = {
                'date': date,
                'time': time,
                'hot_index': hot_index,
                'name': name,
                'raw_hot': raw_hot,
                'label_name': label_name,
                'url': url
            }
            
            data_tuple = tuple(data.values())
            
            add_data = "INSERT INTO hot_search (date, time, hot_index, name, raw_hot, label_name, url) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(add_data, data_tuple)
            cnx.commit()
        else:
            pass
    # 关闭游标和数据库连接
    cursor.close()
    cnx.close()


def generate_wordcloud():     
    save_folder = "pic_wdcd" 
    current_time = datetime.now().strftime("%Y%m%d%H%M%S") 
    image_file = os.path.join(save_folder, f"{current_time}.jpg") 
    

    word_cloud.wordcloud_ten(current_time, image_file)
    # 读取2.jpg图片文件并转为base64编码       
    if os.path.exists(image_file):         
        img = plt.imread(image_file)         
        plt.imshow(img)         
        plt.axis("off")         
        plt.show()




def get_hot_search_names():     
    search()
    # 连接数据库     
    connection = pymysql.connect(         
        host='127.0.0.1',         
        user='root',         
        password='root',         
        database='weibo'     )          
    try:         
        
        # 创建游标对象         
        cursor = connection.cursor()          
        
        # 查询 hot_search 表中的 name 字段         
        sql = "SELECT name FROM hot_search"         
        cursor.execute(sql)          
        
        # 获取查询结果         
        results = cursor.fetchall()         
        
         # 将查询结果写入文件         
        with open("2.txt", "w") as file:             
            for row in results:                 
                name = row[0]                 
                file.write(name + "\n")   

        print("数据已成功写入2.txt文件")      
    except Exception as e:         
        print("发生错误:", e)

    finally:         # 关闭游标和数据库连接         
        cursor.close()         
        connection.close()

def get_hot_commnet_content():     
    # 连接数据库     
    connection = pymysql.connect(         
        host='127.0.0.1',         
        user='root',         
        password='root',         
        database='weibo'     )          
    try:         
        
        # 创建游标对象         
        cursor = connection.cursor()          
        
        # 查询 hot_search 表中的 name 字段         
        sql = "SELECT comment_text FROM comment"         
        cursor.execute(sql)          
        
        # 获取查询结果         
        results = cursor.fetchall()         
        
         # 将查询结果写入文件         
        with open("2.txt", "w") as file:             
            for row in results:                 
                name = row[0]                 
                file.write(name + "\n")   

        print("评论已成功写入2.txt文件")      
    except Exception as e:         
        print("发生错误:", e)

    finally:         # 关闭游标和数据库连接         
        cursor.close()         
        connection.close()
    
    with open("2.txt", "r") as file:         
        content = file.read()     

    return content

def remove_html_tags(text):     
    # 定义要匹配的 HTML 标签的正则表达式模式          
    pattern = r'<.*?>'     # 使用 re.sub 函数替换匹配到的标签为空字符串          
    result = re.sub(pattern, '', text)               
    return result  # 要处理的文本内容 

# 读取 当前目录下的sms.txt 文件中的内容并返回
def get_sms():
    content = " # 使用指南\n本程序 用于对微博热搜 及其 热评内容的爬取\n## 搜索 ：爬去并且展示 微博热搜\n## 获取评论：请在 url 框里填入热搜关键词的url, 例如 https://s.weibo.com/weibo?q=%23男双%23 \n## 生成词云图：对选定 热搜的评论内容进行爬取，并且展示，注意，获取评论后 才能 生成词云图\n在使用此程序前，请确保 mysql已经在本地运行，账号：root， 密码：root，端口默认：3306 \n # 新建数据库\n CREATE DATABASE weibo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    return content

def task_a():     
    get_hot_search_names()

    with open("2.txt", "r") as file:         
        content = file.read()     

    return content
    
if __name__ == "__main__":
    
    layout = [     
    [sg.Text('url'), sg.Input(size=(67, 1), key='-INPUT-')],
    [sg.Image(key="-IMAGE-")],
    [sg.Text("热搜榜单:", justification="center")],     
    [sg.Multiline(size=(80, 15), key="-OUTPUT-")],  
    [sg.Button("搜索", key="run_button"), 
    sg.Button("获取评论", key="-BUTTON-"),
    sg.Button("生成词云图", key="wordcloud_button"),
    sg.Button("使用指南", key="sms"),
    sg.Button("关闭", key="close_button")] ] 


    sg.theme("Dark")
    # 创建窗口 
    
    window = sg.Window("微博热搜爬虫", layout, size=(600, 350)) 
    # 事件循环 
    while True:     
        
        event, values = window.read()      
        if event == sg.WINDOW_CLOSED or event == "close_button":         
            break    
        elif event == "run_button":         
            output = task_a()         
            window["-OUTPUT-"].update(output)
        elif event == "wordcloud_button":         
            generate_wordcloud()
        elif event == '-BUTTON-':         
            text = values['-INPUT-']         
            get_comment.get_the_comment(url=text)
            content = get_hot_commnet_content()
            content = remove_html_tags(text=content)
            window["-OUTPUT-"].update(content)
        elif event == "sms":         
            content = get_sms()
            window["-OUTPUT-"].update(content)
    window.close()