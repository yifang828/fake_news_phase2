請先在MySQL執行以下sql create table post, stock_post, reply
### Create table sql
create table post(
	post_id int not null,
	author_id int,
	author_name VARCHAR(255),
	content VARCHAR(1500),
	reply_count int,
	like_count int,
	postdate datetime,
	PRIMARY KEY (post_id)
);

create table reply(
	reply_id int not null,
	post_id int,
	author_id int,
	author_name VARCHAR(255),
	content VARCHAR(1500),
	like_count int,
	replydate datetime,
	PRIMARY KEY (reply_id)
);

create table stock_post(
	id int not null AUTO_INCREMENT,
	stock_id VARCHAR(20),
	stock_name VARCHAR(10),
	post_id int,
	postdate datetime,
	PRIMARY KEY (id)
);

create index idx_postid on reply (post_id);
create index idx_postid on stock_post (post_id);
create index idx_stockid on stock_post (stock_id);
### Restore database (這邊已DBeaver操作為例)
1. 對要restore的database按右鍵 > 工具 > restore database


### 爬蟲
熱門爆料-最熱排序url:https://www.cmoney.tw/follow/channel/getdata/GetHotStocks?sortType=popular&fetchCount=15&isIncludeLimitedAskArticle=false&baseArticleId=0&skipCount=0&_=1628412971459

熱門爆料-最新排序url:https://www.cmoney.tw/follow/channel/getdata/GetHotStocks?sortType=latest&fetchCount=15&isIncludeLimitedAskArticle=false&baseArticleId=0&skipCount=0&_=1628413359264

baseArticleId填入上一次查詢最後一個post的Id

ArtId  Post id
ChlId  留言者id
ChlCap 留言者名稱
MemberLevel 留言者等級
ArtLkdCnt 讚數
ArtRepdCnt 回應數
ArtCtn Post內容
ArtCteTm 日期

貼文留言:https://www.cmoney.tw/follow/channel/getdata/ArticleListReplied?articleId=129546315&size=3&_=1628414038626
更多回應:https://www.cmoney.tw/follow/channel/getdata/ArticleListMoreReplied?articleId=129544622&smallestArticleId=129571710&size=10&_=1628420344604

ArtId  Post id
ChlId  留言者id
ChlCap 留言者名稱
MemberLevel 留言者等級
ArtLkdCnt 讚數
ArtRepdCnt 回應數
ArtCtn 留言內容 包含相關個股以及留言
ArtCteTm 日期

### DB
##### Table Post
postid INT pk
authorid INT
authorname VARCHAR(255)
content VARCHAR(1500)
replycnt INT
likecnt INT
postdate datetime
##### Table Reply
reply_id INT pk
postid INT
authorid INT
authorname VARCHAR(10)
content VARCHAR(1500)
likecnt INT
replydate datetime
##### Table StockPost
id INT pk
stockid VARCHAR(20)
stockname VARCHAR(50)
postid INT
postdate datetime