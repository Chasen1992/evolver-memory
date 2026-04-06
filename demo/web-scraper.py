#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网页数据抓取工具 - 示例项目
功能：抓取网页数据、表格、列表信息
作者：进化者 (The Evolver)
联系：caijun2019@qq.com
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
from urllib.parse import urljoin, urlparse

class WebScraper:
    """网页数据抓取工具"""
    
    def __init__(self, base_url, delay=1):
        self.base_url = base_url
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_page(self, url):
        """获取页面内容"""
        try:
            time.sleep(self.delay)  # 礼貌延迟
            response = self.session.get(url)
            response.encoding = response.apparent_encoding
            return response.text
        except Exception as e:
            print(f"获取页面失败: {e}")
            return None
    
    def parse_tables(self, html):
        """解析页面中的所有表格"""
        soup = BeautifulSoup(html, 'html.parser')
        tables = soup.find_all('table')
        
        results = []
        for i, table in enumerate(tables):
            try:
                df = pd.read_html(str(table))[0]
                results.append({
                    'index': i,
                    'data': df.to_dict('records'),
                    'columns': list(df.columns)
                })
            except:
                continue
        
        return results
    
    def parse_links(self, html, filter_pattern=None):
        """解析页面中的所有链接"""
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all('a', href=True)
        
        results = []
        for link in links:
            href = link['href']
            full_url = urljoin(self.base_url, href)
            
            if filter_pattern and filter_pattern not in full_url:
                continue
            
            results.append({
                'text': link.get_text(strip=True),
                'url': full_url
            })
        
        return results
    
    def parse_text(self, html, selector=None):
        """解析文本内容"""
        soup = BeautifulSoup(html, 'html.parser')
        
        if selector:
            elements = soup.select(selector)
        else:
            # 移除脚本和样式
            for script in soup(['script', 'style']):
                script.decompose()
            elements = [soup]
        
        texts = []
        for elem in elements:
            text = elem.get_text(separator='\n', strip=True)
            if text:
                texts.append(text)
        
        return '\n\n'.join(texts)
    
    def save_to_csv(self, data, filename):
        """保存数据到CSV"""
        if isinstance(data, list) and len(data) > 0:
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            return True
        return False
    
    def save_to_json(self, data, filename):
        """保存数据到JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True


def main():
    """示例用法"""
    print("网页数据抓取工具")
    print("=" * 50)
    print("功能：")
    print("1. 抓取网页表格数据")
    print("2. 提取页面链接")
    print("3. 获取文本内容")
    print("4. 导出CSV/JSON")
    print("=" * 50)
    print("联系：caijun2019@qq.com")
    print("定制开发：¥300-800")
    
    # 使用示例
    # scraper = WebScraper("https://example.com")
    # html = scraper.fetch_page("https://example.com/data")
    # tables = scraper.parse_tables(html)
    # scraper.save_to_csv(tables[0]['data'], "output.csv")


if __name__ == "__main__":
    main()
