import scrapy
import random
from urllib.parse import urlencode
import os
from urllib.parse import urlparse, parse_qs
import urllib.parse
class DpmSearchSpider(scrapy.Spider):
    name = "dpm_search"
    allowed_domains = ["dpm.org.cn"]
    start_urls = ["https://www.dpm.org.cn/lights/royal/"]
    total = 0
    is_pc="0"
    is_wap="0"
    is_calendar="0"
    is_four_k="0"
    #默认大小
    # 1280 x 800=2
    # 1680 x 1050=3
    # 1920 x 1080=4
    # 1080 x 1920=6
    # 1125 x 2436=7
    # 1125 x 2436=8
    # 1248 x 2778=9
    # 1248 x 2778=11
    # 2560 x 1440=12
    size_name={
        "2":"1280 x 800",
        "3":"1680 x 1050",
        "4":"1920 x 1080",
        "6":"1080 x 1920",
        "7":"1125 x 2436",
        "8":"1125 x 2436",
        "9":"1248 x 2778",
        "11":"1248 x 2778",
        "12":"2560 x 1440",
    }
    size=4

    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        kwargs.setdefault("is_pc",0)
        kwargs.setdefault("is_wap",0)
        kwargs.setdefault("is_calendar",0)
        kwargs.setdefault("is_four_k",0)
        kwargs.setdefault("size",4)

        self.is_pc=int(kwargs.get("is_pc"))
        self.is_wap=int(kwargs.get("is_wap"))
        self.is_calendar=int(kwargs.get("is_calendar"))
        self.is_four_k=int(kwargs.get("is_four_k"))
        print(f'启动参数self.is_pc={self.is_pc},self.is_wap={self.is_wap},self.is_calendar={self.is_calendar},self.is_four_k={self.is_four_k}')

    def filter_num(self):
        print("筛选请求")
        search = {
            "category_id": 624,
            "p": 1,
            "pagesize": 16,
            "title": "",
            "is_pc": self.is_pc,
            "is_wap": self.is_wap,
            "is_calendar": self.is_calendar,
            "is_four_k": self.is_four_k,
        }
        base_url = 'https://www.dpm.org.cn/searchs/royalb.html'
        url = f'{base_url}?{random.random()}&{urlencode(search)}'
        # print('url',url)
        yield scrapy.Request(url, self.parse_webNum)

    def down(self):
        # 所有页面
        for p in range(1, self.total + 1):
            search = {
                "category_id": 624,
                "p": p,
                "pagesize": 16,
                "title": "",
                "is_pc": self.is_pc,
                "is_wap": self.is_wap,
                "is_calendar": self.is_calendar,
                "is_four_k": self.is_four_k,
            }
            base_url = 'https://www.dpm.org.cn/searchs/royalb.html'
            url = f'{base_url}?{random.random()}&{urlencode(search)}'
            # print('url',url)
            yield scrapy.Request(url, self.parse_web)
        # 单个网页
        # search = {
        #     "category_id": 624,
        #     "p": 1,
        #     "pagesize": 16,
        #     "title": "",
        #     "is_pc": self.is_pc,
        #     "is_wap": self.is_wap,
        #     "is_calendar": self.is_calendar,
        #     "is_four_k": self.is_four_k,
        # }
        # base_url = 'https://www.dpm.org.cn/searchs/royalb.html'
        # url = f'{base_url}?{random.random()}&{urlencode(search)}'
        # # print(url)
        # yield scrapy.Request(url, self.parse_web)

    def parse(self, response):
        sc=response.xpath('/html/body/div[4]/div[2]/div[2]/div/div[3]')
        divlist=sc.xpath('//a[@data-key]')
        for element in divlist:
            if int(element.xpath('@data-key').get()) > self.total:
                self.total=int(element.xpath('@data-key').get())
        print("总页数",self.total,self.is_pc!=0 or self.is_wap!=0 or self.is_calendar!=0 or self.is_four_k!=0)
        if self.is_pc!=0 or self.is_wap!=0 or self.is_calendar!=0 or self.is_four_k!=0:
            yield from self.filter_num()
        else:
            yield from self.down()



    def parse_webNum(self,response):
        buttons = response.xpath('//div/div/div/div/button')
        self.total=int(buttons.xpath('@data-max').get())
        print('筛选后页数',self.total)
        yield from self.down()
        # for button in buttons:


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
                # yield scrapy.Request("https://www.dpm.org.cn/light/" + item + ".html", self.parse_item)
                yield scrapy.Request(f'https://www.dpm.org.cn/download/lights_image/id/{item}/img_size/{self.size}.html',
                                     self.save_image,
                                     errback=self.errback,
                                     meta={"name":f'{item}_{self.size}.png'}
                                     )

    def errback(self, failure):
        print(failure)

    #获取网址内容中所有图片地址
    def parse_item(self, response):
        elements = response.xpath("/html/body/div[2]/img")
        for element in elements:
            src = element.xpath('@src').get()
            # print('下载地址', src)
            yield scrapy.Request(src, self.save_image)

    def save_image(self, response):
        name=response.meta['name']
        content_disposition=response.headers['Content-Disposition'].decode('utf-8')
        filename_part = content_disposition.split("filename*=utf-8''")[1]
        filename = urllib.parse.unquote_plus(filename_part)
        if filename:
            path=filename
        else:
            path = response.url.split('/')[-1]
        root_path=os.getcwd()
        subdir =r'py_scrapy\spiders\all_images'
        if self.is_pc != 0 or self.is_wap != 0 or self.is_calendar != 0 or self.is_four_k != 0:
            if self.is_pc!=0 and self.is_wap==0 and self.is_calendar==0 and self.is_four_k==0:
                subdir=subdir+r'\pc'
            if self.is_wap!=0 and self.is_pc==0 and self.is_calendar==0 and self.is_four_k==0:
                subdir=subdir+r'\wap'
            if self.is_calendar!=0 and self.is_pc==0 and self.is_wap==0 and self.is_four_k==0:
                subdir=subdir+r'\calendar'
            if self.is_four_k!=0 and self.is_pc==0 and self.is_calendar==0 and self.is_wap==0:
                subdir=subdir+r'\four_k'
        dir=os.path.join(root_path,subdir)
        if not os.path.exists(dir):
            os.makedirs(dir)
        path=os.path.join(root_path,subdir,path)
        # print(path)
        with open(path, 'wb') as f:
            f.write(response.body)




