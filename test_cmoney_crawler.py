import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from cmoney_crawler import CmoneyCrawler
import json

class Cmoney(unittest.TestCase):
    # def setUp(self) -> None:
    '''
        測試post id:129654328的所有回應
        reply=[{replyId: 129660825, postId: 129654328, replyContent: 你是幾天沒大便了滿腦子都是賽還看營收, authorId: 9639359, authorName: OGzyhVX27D, likeCount: 1, replyDate:'2021/08/09 14:35'}, {...}, ...]
    '''
    def test_get_all_replies(self):
        print("\033[93m START test_get_all_replies...\033[0m")
        cmoney = CmoneyCrawler()
        replies = cmoney.get_all_replies('129654328', '7')
        self.assertEqual(7, len(replies))
        self.assertEqual(129660825, replies[0]['replyId'])
        self.assertEqual(129654328, replies[0]['postId'])
        self.assertEqual('你是幾天沒大便了滿腦子都是賽還看營收', replies[0]['replyContent'])
        self.assertEqual(9639359, replies[0]['authorId'])
        self.assertEqual('OGzyhVX27D', replies[0]['authorName'])
        self.assertEqual(1, replies[0]['likeCount'])
        self.assertEqual('2021/08/09 14:35', replies[0]['replyDate'])
        print("\033[92m FINISH test_get_all_replies=====OK\033[0m")

    '''
        測試post id:129654341 之後的post且時間在2021/08/09 13:56之後(包含)，是post id:129654328, 129654313
        posts=[{'postId': 129654328, 'content': '月減明天肯定有戲', 'authorId': 4294364, 'authorName': '棋靈王', 'likeCount': 7, 'replyCount': 7, \
            'postDate': '2021/08/09 13:56'}, {'postId': 129654313, 'content': '哎呀亮晶晶跌到我眼冒星星只有84號損益是正的', 'authorId': 6207466, \
            'authorName': 'iN', 'likeCount': 5, 'replyCount': 0, 'postDate': '2021/08/09 13:56'}]
        replies=[[{replyId: 129660825, postId: 129654328, replyContent: 你是幾天沒大便了滿腦子都是賽還看營收, authorId: 9639359, authorName: OGzyhVX27D,\
             likeCount: 1, replyDate:'2021/08/09 14:35'}, {...}, ...], [...], ...]
        stock_posts=[[{'stockId': '2409', 'stockName': '友達', 'postId': 129654328, 'postDate': '2021/08/09 13:56'}], [{'stockId': '6116', \
            'stockName': '彩晶', 'postId': 129654313, 'postDate': '2021/08/09 13:56'}]]
    '''
    def test_get_latest_hot_buzz_after_datetime(self):
        print("\033[93m START test_get_latest_hot_buzz_after_datetime...\033[0m")
        cmoney = CmoneyCrawler()
        rspns = cmoney.get_html_data('129654341', '15', is_hot_buzz=True)
        rspns = json.loads(rspns)
        posts, replies, stocks, _ = cmoney.get_latest_hot_buzz_after_datetime(rspns, '2021/08/09 13:56')
        self.assertEqual(2, len(posts))
        self.assertEqual(1, len(replies))
        self.assertEqual(2, len(stocks))
        self.assertEqual(129654328, posts[0]['postId'])
        self.assertEqual(4294364, posts[0]['authorId'])
        self.assertEqual('棋靈王', posts[0]['authorName'])
        self.assertEqual('月減明天肯定有戲', posts[0]['content'])
        self.assertEqual(7, posts[0]['replyCount'])
        self.assertEqual(7, posts[0]['likeCount'])
        self.assertEqual('2021/08/09 13:56', posts[0]['postDate'])
        self.assertEqual(7, len(replies[0]))
        self.assertEqual(129660825, replies[0][0]['replyId'])
        self.assertEqual(129654328, replies[0][0]['postId'])
        self.assertEqual('你是幾天沒大便了滿腦子都是賽還看營收', replies[0][0]['replyContent'])
        self.assertEqual(9639359, replies[0][0]['authorId'])
        self.assertEqual('OGzyhVX27D', replies[0][0]['authorName'])
        self.assertEqual(1, replies[0][0]['likeCount'])
        self.assertEqual('2021/08/09 14:35', replies[0][0]['replyDate'])
        self.assertEqual('2409', stocks[0][0]['stockId'])
        self.assertEqual('友達', stocks[0][0]['stockName'])
        print("\033[92m FINISH test_get_latest_hot_buzz_after_datetime =====OK\033[0m")

if __name__ == "__main__":
    # unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(Cmoney('test_get_all_replies'))
    suite.addTest(Cmoney('test_get_latest_hot_buzz_after_datetime'))
    # suite.addTest(Cmoney('test_insert_posts'))
    unittest.TextTestRunner().run(suite)