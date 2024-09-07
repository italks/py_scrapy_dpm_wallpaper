import scrapy
import random
from urllib.parse import urlencode
import os
from urllib.parse import urlparse, parse_qs

class DpmSearchSpider(scrapy.Spider):
    name = "dpm_search"
    allowed_domains = ["dpm.org.cn"]
    start_urls = ["https://www.dpm.org.cn/lights/royal/"]
    total = 0

    def parse(self, response):
        sc=response.xpath('/html/body/div[4]/div[2]/div[2]/div/div[3]')
        divlist=sc.xpath('//a[@data-key]')
        for element in divlist:
            if int(element.xpath('@data-key').get()) > self.total:
                self.total=int(element.xpath('@data-key').get())
        print("total",self.total)
        #所有页面
        for p in range(1,self.total+1):
            search = {
                "category_id": 624,
                "p": p,
                "pagesize": 16,
                "title": "",
                "is_pc": 0,
                "is_wap": 0,
                "is_calendar": 0,
                "is_four_k": 0,
            }
            base_url = 'https://www.dpm.org.cn/searchs/royalb.html'
            url = f'{base_url}?{random.random()}&{urlencode(search)}'
            # print('url',url)
            yield scrapy.Request(url,self.parse_web)
        # 单个网页
        # search = {
        #     "category_id": 624,
        #     "p": 1,
        #     "pagesize": 16,
        #     "title": "",
        #     "is_pc": 0,
        #     "is_wap": 0,
        #     "is_calendar": 0,
        #     "is_four_k": 0,
        # }
        # base_url = 'https://www.dpm.org.cn/searchs/royalb.html'
        # url = f'{base_url}?{random.random()}&{urlencode(search)}'
        # # print(url)
        # yield scrapy.Request(url, self.parse_web)

    def parse_web(self, response):
        request_url = response.url
        parsed_url = urlparse(request_url)
        query_params = parse_qs(parsed_url.query)
        p = query_params.get('p', [''])[0]
        print("处理第N页",p)
        elements = response.xpath('//*[@id="datalist"]//div[@data-key]')
        self.total=response.xpath('/html/body/div[4]/div[2]/div[2]/div/div[3]/div/div/a[6]')
        for element in elements:
            # 提取 data-key 属性的值
            data_key = element.xpath('@data-key').get()
            array = data_key.split(",")
            for item in array:
                yield scrapy.Request("https://www.dpm.org.cn/light/" + item + ".html", self.parse_item)

    def parse_item(self, response):
        elements = response.xpath("/html/body/div[2]/img")
        for element in elements:
            src = element.xpath('@src').get()
            # print('下载地址', src)
            yield scrapy.Request(src, self.save_image)

    def save_image(self, response):
        path = response.url.split('/')[-1]
        root_path=os.getcwd()
        subdir =r'py_scrapy\spiders\all_images'
        path=os.path.join(root_path,subdir,path)
        # print(path)
        with open(path, 'wb') as f:
            f.write(response.body)




