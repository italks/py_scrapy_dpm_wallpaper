import os

import scrapy


class DpmSpider(scrapy.Spider):
    name = "dpm"
    allowed_domains = ["dpm.org.cn"]
    ("https://www.dpm.org.cn/searchs/royalb.html?"
     "0.1966713757279901&category_id=624&p=1&pagesize=16&title=&is_pc=1&is_wap=0&is_calendar=0&is_four_k=0")
    search={
        "category_id":624,
        "p":1,
        "pagesize":16,
        "title":"",
        "is_pc":0,
        "is_wap":0,
        "is_calendar":0,
        "is_four_k":0,
    }
    start_urls = ["https://www.dpm.org.cn/lights/royal/"]
    total=0

    # 获取图片列表
    def parse(self, response):
        # divList=response.xpath("//div[4]/div[2]/div[2]/div/div[2]/div[2]/div[1]/div/div/a/img")
        # for div in divList:
        #     print('image=',div.xpath("./@src").get())

        elements = response.xpath('//*[@id="datalist"]//div[@data-key]')
        self.total=response.xpath('/html/body/div[4]/div[2]/div[2]/div/div[3]/div/div/a[6]')
        for element in elements:
            # 提取 data-key 属性的值
            data_key = element.xpath('@data-key').get()
            array = data_key.split(",")
            for item in array:
                yield scrapy.Request("https://www.dpm.org.cn/light/" + item + ".html", self.parse_item)
            # yield {
            #     'image_urls': ["https://www.dpm.org.cn/light/"+item+".html" for item in array]
            # }

    # 抓取图片地址
    def parse_item(self, response):
        elements = response.xpath("/html/body/div[2]/img")
        for element in elements:
            src = element.xpath('@src').get()
            print('下载地址', src)
            yield scrapy.Request(src, self.save_image)

    # 下载图片
    def save_image(self, response):
        path = response.url.split('/')[-1]
        root_path=os.getcwd()
        subdir =r'py_scrapy\spiders\images'
        path=os.path.join(root_path,subdir,path)
        print(path)
        with open(path, 'wb') as f:
            f.write(response.body)
