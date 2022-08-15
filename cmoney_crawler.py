import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import bs4
import json
import re
from datetime import datetime
import mysql.connector

class CmoneyCrawler():
    LATEST_HOT_BUZZ_URL = 'https://www.cmoney.tw/follow/channel/getdata/GetHotStocks?sortType=latest&fetchCount='
    POST_REPLIES = 'https://www.cmoney.tw/follow/channel/getdata/ArticleListReplied?articleId='
    CHROMEDRIVER_PATH = 'D:/Software/chromedriver.exe'
    def __init__(self):
        self.mydb = mysql.connector.connect(
            host="localhost",
            user="yourusername",
            password="yourpassword",
            database="yourdatabase"
        )
        self.cursor = self.mydb.cursor()
        ### 解決您的連線不是私人連線
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options, executable_path=self.CHROMEDRIVER_PATH)

    def get_html_data(self, postId, size, is_hot_buzz=False):
        if is_hot_buzz:
            self.driver.get(self.LATEST_HOT_BUZZ_URL + size + '&isIncludeLimitedAskArticle=false&baseArticleId=' + postId + '&skipCount=0')
        else:
            self.driver.get(self.POST_REPLIES + postId + '&size=' + size)
        ### 解決網頁瀏覽遭到拒絕
        try:
            WebDriverWait(self.driver, 0.2).until(EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "網頁瀏覽遭到拒絕"))
            self.driver.find_element_by_name('ok').click()
        except:
            print('No URL block.')
        ### 有時可能會找不到留言，catch回傳'[]'
        try:
            WebDriverWait(self.driver, 0.2).until(EC.presence_of_element_located((By.TAG_NAME, "pre")))
        except:
            print('selenium.common.exceptions.NoSuchElementException: Message: no such element: Unable to locate element: {"method":"css selector","selector":"pre"}')
            return '[]'
        return self.driver.find_element_by_tag_name('pre').text

    def get_reply_content(self, content):
        soup = bs4.BeautifulSoup(content, "html.parser")
        content = ' '.join(soup.stripped_strings)
        content_list = re.findall(r'[\w\u4e00-\u9fa5]*', content)
        result=''
        for c in content_list:
            if c:
                result = result+c
            else:
                continue
        return result[:1500]

    def get_all_replies(self, postId, size):
        rspns = ''
        result = []
        rspns = self.get_html_data(postId, size, is_hot_buzz=False)
        rspns = json.loads(rspns)
        for rspn in rspns:
            reply_dic = {}
            reply_dic['replyId'] = int(rspn['ArtId'])
            reply_dic['postId'] = int(postId)
            reply_dic['replyContent'] = self.get_reply_content(rspn['ArtCtn'])
            reply_dic['authorId'] = int(rspn['ChlId'])
            reply_dic['authorName'] = rspn['ChlCap']
            reply_dic['likeCount'] = int(rspn['ArtLkdCnt'])
            reply_dic['replyDate'] = rspn['ArtCteTm']
            result.append(reply_dic)
        return result

    def get_stock_post_dict(self, tags, post_id, post_date):
        result = []
        for tag in tags:
            stock_dict = {}
            stock_dict['stockId'] = tag['CommKey']
            stock_dict['stockName'] = tag['CommName']
            stock_dict['postId'] = post_id
            stock_dict['postDate'] = post_date
            result.append(stock_dict)
        return result

    def get_post_content(self, content):
        soup = bs4.BeautifulSoup(content, "html.parser")
        content = soup.find("div", class_="main-content").get_text()
        content_list = re.findall(r'[-%\.\+\w\u4e00-\u9fa5\/]*', content)
        result=''
        for c in content_list:
            if c:
                result = result+c
            else:
                continue
        return result[:1500]

    def get_latest_hot_buzz_after_datetime(self, rspns, date_str):
    # def get_latest_hot_buzz_after_datetime(self, rspns, stopId):
        posts = []
        replies = []
        stocks = []
        date = datetime.strptime(date_str, '%Y/%m/%d %H:%M')
        for rspn in rspns:
            id = int(rspn['ArtId'])
            print('post id: ', id)
            rspn_date = datetime.strptime(rspn['ArtCteTm'], '%Y/%m/%d %H:%M')
            if date <= rspn_date:
            # if stopId < id:
                reply_dic = {}
                reply_dic['postId'] = id
                reply_dic['content'] = self.get_post_content(rspn['ArtCtn'])
                reply_dic['authorId'] = int(rspn['ChlId'])
                reply_dic['authorName'] = rspn['ChlCap']
                reply_dic['likeCount'] = int(rspn['ArtLkdCnt'])
                reply_dic['replyCount'] = int(rspn['ArtRepdCnt'])
                reply_dic['postDate'] = rspn['ArtCteTm']
                posts.append(reply_dic)
                # 有留言才爬
                if reply_dic['replyCount'] > 0:
                    replies.append(self.get_all_replies(rspn['ArtId'], rspn['ArtRepdCnt']))
                    time.sleep(1.5)
                #  有tag 才爬
                if len(rspn['MentionTags']) >0:
                    stocks.append(self.get_stock_post_dict(rspn['MentionTags'], reply_dic['postId'], reply_dic['postDate']))
        return posts, replies, stocks, id
    
    def insert_posts(self, posts):
        insert_post_sql = "INSERT INTO post (post_id, author_id, author_name, content, reply_count, like_count, postdate) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        val = []
        for post in posts:
            post_tuple = (post['postId'], post['authorId'], post['authorName'], post['content'], post['replyCount'], post['likeCount'], post['postDate'])
            val.append(post_tuple)

        self.cursor.executemany(insert_post_sql, val)
        self.mydb.commit()

    def insert_reply(self, replies):
        insert_reply_sql = "INSERT INTO reply (reply_id, post_id, author_id, author_name, content, like_count, replydate) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        val = []
        for reply in replies:
            for r in reply:
                reply_tuple = (r['replyId'], r['postId'], r['authorId'], r['authorName'], r['replyContent'], r['likeCount'], r['replyDate'])
                val.append(reply_tuple)

        self.cursor.executemany(insert_reply_sql, val)
        self.mydb.commit()

    def insert_stock_post(self, stocks):
        insert_stock_sql = "INSERT INTO stock_post (stock_id, stock_name, post_id, postdate) VALUES (%s, %s, %s, %s)"
        val = []
        for stock in stocks:
            for s in stock:
                stock_tuple = (s['stockId'], s['stockName'], s['postId'], s['postDate'])
                val.append(stock_tuple)
        self.cursor.executemany(insert_stock_sql, val)
        self.mydb.commit()
    
def main():
    # 計時開始
    start_time = time.time()
    cmoney = CmoneyCrawler()
    post_id = '108666970'
    limit = '500'
    while True:
        rspns = cmoney.get_html_data(str(post_id), limit, is_hot_buzz=True)
        rspns = json.loads(rspns)
        if len(rspns) == 0:
            print("=================No Post: ", post_id)
            print("At time: ", str(datetime.now().strftime("%Y%m%d_%Hh%Mm%Ss")))
            break
        else:
            # posts, replies, stocks, last_id= cmoney.get_latest_hot_buzz_after_datetime(rspns, 129952900)
            posts, replies, stocks, last_id= cmoney.get_latest_hot_buzz_after_datetime(rspns, '2021/01/01 00:00')
            post_id = str(last_id)
            if len(posts) == 0:
                break
            cmoney.insert_posts(posts)
            cmoney.insert_reply(replies)
            cmoney.insert_stock_post(stocks)
            print("=========SLEEP 2 SECS========")
            time.sleep(2)
    end_time = time.time()
    print('execute_time: ', str(end_time-start_time))
    ## 關閉資料庫連線
    cmoney.cursor.close()
    cmoney.mydb.close()

if __name__=='__main__':
    main()