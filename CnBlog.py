# 需要安装如下库：
# pip install requests -i http://pypi.douban.com/simple --trusted-host pypi.douban.com
# pip install BeautifulSoup4 -i http://pypi.douban.com/simple --trusted-host pypi.douban.com
# pip install xlrd -i http://pypi.douban.com/simple --trusted-host pypi.douban.com
# pip install xlwt -i http://pypi.douban.com/simple --trusted-host pypi.douban.com
# pip install lxml -i http://pypi.douban.com/simple --trusted-host pypi.douban.com
# pip install html5lib -i http://pypi.douban.com/simple --trusted-host pypi.douban.com
import requests
import re
import json
import time
import bs4
from bs4 import BeautifulSoup
import xlrd
import xlwt

def downloadPage():
    CRAWLING_URL = 'https://www.cnblogs.com/'
    """获取页面内容"""
    print('获取页面内容用时')
    url = CRAWLING_URL

    res = requests.get(url).text
    html = BeautifulSoup(res, 'lxml')

    data = {}
    postList = html.find_all(class_='post_item_foot')
    for postInfo in postList:
        content = postInfo.contents
        # 发布时间字符串
        timeStr = content[2][11:27]

        localTime = time.localtime(time.mktime(
            time.strptime(timeStr, '%Y-%m-%d %H:%M')))
        # 以2018-11-01 15 格式时间 作为 key
        timeIndex = time.strftime("%Y-%m-%d %H", localTime)
        viewStr = content[4].contents[0].contents[0]
        commontStr = content[3].contents[0].contents[0]

        # 浏览量
        view = int(re.findall("\d+", viewStr)[0])
        # 评论量
        commont = int(re.findall("\d+", commontStr)[0])

        if timeIndex in data:
            data[timeIndex]['view'] += view
            data[timeIndex]['commont'] += commont
            data[timeIndex]['postCount'] += 1
        else:
            data[timeIndex] = {
                'view': view,
                'commont': commont,
                'postCount': 1
            }
    print('返回：%s' %(data))
    return data

def crawlData(page, data):
    CRAWLING_URL = 'https://www.cnblogs.com/mvc/AggSite/PostList.aspx'
    """获取页面内容"""
    url = CRAWLING_URL
    data = {}
    headers = {
        'Content-Type': 'application/json',
    }
    params = json.dumps({
        'CategoryId': 808,
        'CategoryType': "SiteHome",
        'ItemListActionName': "PostList",
        'PageIndex': page,
        'ParentCategoryId': 0,
        'TotalPostCount': 4000,
    })
    data = requests.post(url, data=params, headers=headers, verify=False).text
    return data

def main():
    pageNum = 11
    data = {}
    # 获取所有数据
    for page in range(1, pageNum):
        data = crawlData(page)
        print('已完成: %s/%s' % (page, pageNum - 1))
        page += 1

    # excel 表格存储
    wb = xlwt.Workbook(encoding='utf-8', style_compression=0)
    ws1 = wb.add_sheet('test', cell_overwrite_ok=True)
    col = 2
    ws1['A1'] = '日期'
    ws1['B1'] = '查看人数'
    ws1['C1'] = '评论人数'
    ws1['D1'] = '发布数量'
    for postCount in data:
        col_A = 'A%s' % col
        col_B = 'B%s' % col
        col_C = 'C%s' % col
        col_D = 'D%s' % col
        ws1[col_A] = postCount
        ws1[col_B] = data[postCount]['view']
        ws1[col_C] = data[postCount]['commont']
        ws1[col_D] = data[postCount]['postCount']
        col += 1

    wb.save(filename='c:\temp1234.xls')
    print('-------------SUCCESS--------------')

if(__name__=="__main__"):
    downloadPage()