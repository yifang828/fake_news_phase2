from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib.request as req

LATEST_HOT_BUZZ_URL = 'https://www.cmoney.tw/follow/channel/getdata/GetHotStocks?sortType=latest&fetchCount='
POST_REPLIES = 'https://www.cmoney.tw/follow/channel/getdata/ArticleListReplied?articleId='
CHROMEDRIVER_PATH = 'D:/Software/chromedriver.exe'

### 解決您的連線不是私人連線
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--headless')
driver = webdriver.Chrome(options=options, executable_path=CHROMEDRIVER_PATH)
def getHtmlData(url):
    request=req.Request(url, headers={
        "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",
        "Referer":"https://www.cmoney.tw/follow/channel/hot-buzz"
    })
    with req.urlopen(request) as resp:
        data=resp.read().decode("utf-8")
    return data

id = 111800378
while True:
    driver.get(LATEST_HOT_BUZZ_URL + '15&isIncludeLimitedAskArticle=false&baseArticleId=' + str(id) + '&skipCount=0')
    ### 解決網頁瀏覽遭到拒絕
    try:
        WebDriverWait(driver, 0.2).until(EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "網頁瀏覽遭到拒絕"))
        driver.find_element_by_name('ok').click()
    except:
        print('No URL block.')
    id = id - 1
    print(getHtmlData(LATEST_HOT_BUZZ_URL + '15&isIncludeLimitedAskArticle=false&baseArticleId=0&skipCount=0'))
    try:
        WebDriverWait(driver, 0.2).until(EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "哎呀！真抱歉..."))
    except:
        print(id)
        break