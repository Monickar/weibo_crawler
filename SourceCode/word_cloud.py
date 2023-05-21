import re
import os
import jieba
import pymysql
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from datetime import datetime




def wordcloud_ten(current_time, image_file):
    conn = pymysql.connect(host='localhost', user='root', password='root', database='weibo')
    cursor = conn.cursor()

    # 从数据库中读取数据
    cursor.execute('SELECT comment_text FROM comment')
    results = cursor.fetchall()

    # 使用jieba分词并统计词频
    word_counts = {}
    for result in results:
        content = re.sub(r'[^\u4e00-\u9fa5]+', '', result[0])
        words = jieba.lcut(content)
        for word in words:
            if len(word) > 1:
                word_counts[word] = word_counts.get(word, 0) + 1

    # 生成词云图
    wordcloud = WordCloud(font_path='simhei.ttf',
                          background_color='white',
                          max_words=90,
                          max_font_size=90,
                          width=700,
                          height=700).generate_from_frequencies(word_counts)

    # 显示词云图
    plt.imshow(wordcloud, interpolation='bilinear')

    plt.axis('off')

    save_folder = "pic_wdcd"
    os.makedirs(save_folder, exist_ok=True)
    save_file = os.path.join(save_folder, f"{current_time}.jpg")
    wordcloud.to_file(save_file)

    # 提交修改并关闭连接
    conn.commit()
    cursor.close()
    conn.close()
