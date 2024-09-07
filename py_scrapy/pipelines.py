# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import os

import scrapy
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json

# 配置 Scrapy 项目
from scrapy.pipelines.images import ImagesPipeline
class PyScrapyPipeline(ImagesPipeline):
    def open_spider(self, spider):
        super().open_spider(spider)
        # 获取 IMAGES_STORE 配置
        self.images_store = spider.settings.get('IMAGES_STORE')
        spider.logger.warning(f'IMAGES_STORE is set to: {self.images_store}')

    def process_item(self, item, spider):
        print(f'Processing item: {item}')
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        # 使用 self.images_store 获取配置路径
        image_name = request.url.split('/')[-1]
        # 返回自定义路径
        return os.path.join('custom_directory', image_name)

    def get_media_requests(self, item, info):
        # 从 item 中获取图片 URL 并请求下载
        for image_url in item.get('image_urls', []):
            print(image_url)
            yield scrapy.Request(image_url,ImagesPipeline)

    def item_completed(self, results, item, info):
        # 图片下载完成后的处理逻辑
        item['image_paths'] = [result['path'] for ok, result in results if ok]
        print(item)
        return item
# class LoggingPipeline:
#     def process_item(self, item, spider):
#         # 打印日志
#         spider.logger.warning(f'Logging item: {item}')
#         # 将 item 传递给下一个管道
#         return item
#
# class JsonPipeline:
#     def open_spider(self, spider):
#         self.file = open('items.json', 'w', encoding='utf-8')
#         self.exporter = json.JSONEncoder()
#
#     def close_spider(self, spider):
#         self.file.close()
#
#     def process_item(self, item, spider):
#         line = self.exporter.encode(item) + '\n'
#         self.file.write(line)
#         return item