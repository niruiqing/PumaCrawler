#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用Selenium的Puma商品信息爬虫
用于处理需要JavaScript渲染的页面
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json
import time
import logging
from dataclasses import asdict
from puma_scraper import ProductInfo

logger = logging.getLogger(__name__)

class PumaSeleniumScraper:
    """使用Selenium的Puma商品爬虫"""
    
    def __init__(self, headless=True):
        self.driver = None
        self.wait = None
        self.headless = headless
    
    def setup_driver(self):
        """设置Chrome驱动器"""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 15)
            logger.info("Chrome驱动器设置成功")
            return True
            
        except Exception as e:
            logger.error(f"设置Chrome驱动器失败: {e}")
            return False
    
    def scrape_product_selenium(self, url: str) -> ProductInfo:
        """使用Selenium爬取商品信息"""
        product = ProductInfo()
        
        try:
            logger.info(f"使用Selenium访问: {url}")
            self.driver.get(url)
            
            # 等待页面加载
            time.sleep(3)
            
            # 商品名称
            try:
                name_selectors = [
                    "h1[data-testid='product-name']",
                    "h1.product-name",
                    "h1.pdp-product-name",
                    ".product-title h1",
                    "h1"
                ]
                
                for selector in name_selectors:
                    try:
                        element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                        product.name = element.text.strip()
                        if product.name:
                            break
                    except TimeoutException:
                        continue
                        
            except Exception as e:
                logger.warning(f"获取商品名称失败: {e}")
            
            # 价格信息
            try:
                price_selectors = [
                    "[data-testid='product-price']",
                    ".price-current",
                    ".product-price .price",
                    ".price-container .price",
                    ".pdp-price"
                ]
                
                for selector in price_selectors:
                    try:
                        price_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        product.price = price_element.text.strip()
                        if product.price:
                            break
                    except NoSuchElementException:
                        continue
                        
            except Exception as e:
                logger.warning(f"获取价格失败: {e}")
            
            # 原价
            try:
                original_price_selectors = [
                    ".price-original",
                    ".price-was",
                    ".strikethrough",
                    "[data-testid='product-original-price']"
                ]
                
                for selector in original_price_selectors:
                    try:
                        original_price_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        product.original_price = original_price_element.text.strip()
                        if product.original_price:
                            break
                    except NoSuchElementException:
                        continue
                        
            except Exception as e:
                logger.warning(f"获取原价失败: {e}")
            
            # 颜色信息
            try:
                color_selectors = [
                    "[data-testid='color-name']",
                    ".color-name",
                    ".selected-color",
                    ".color-label"
                ]
                
                for selector in color_selectors:
                    try:
                        color_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        product.color = color_element.text.strip()
                        if product.color:
                            break
                    except NoSuchElementException:
                        continue
                        
            except Exception as e:
                logger.warning(f"获取颜色信息失败: {e}")
            
            # 尺码信息
            try:
                size_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                    "[class*='size'], [class*='Size'], [data-testid*='size'], [data-testid*='Size']")
                
                for element in size_elements:
                    size_text = element.text.strip()
                    if size_text and size_text not in product.sizes and len(size_text) < 10:
                        product.sizes.append(size_text)
                        
            except Exception as e:
                logger.warning(f"获取尺码信息失败: {e}")
            
            # 商品描述
            try:
                desc_selectors = [
                    "[data-testid='product-description']",
                    ".product-description",
                    ".pdp-description",
                    ".product-details-description"
                ]
                
                for selector in desc_selectors:
                    try:
                        desc_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        product.description = desc_element.text.strip()
                        if product.description:
                            break
                    except NoSuchElementException:
                        continue
                        
            except Exception as e:
                logger.warning(f"获取商品描述失败: {e}")
            
            # 图片信息
            try:
                img_selectors = [
                    ".product-images img",
                    ".pdp-images img", 
                    ".gallery img",
                    "[data-testid='product-image'] img"
                ]
                
                for selector in img_selectors:
                    try:
                        img_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for img in img_elements:
                            src = img.get_attribute('src') or img.get_attribute('data-src')
                            if src and src not in product.images:
                                product.images.append(src)
                    except NoSuchElementException:
                        continue
                        
            except Exception as e:
                logger.warning(f"获取图片信息失败: {e}")
            
            # 从URL提取产品ID
            try:
                current_url = self.driver.current_url
                import re
                match = re.search(r'/(\d+)(?:\?|$)', current_url)
                if match:
                    product.product_id = match.group(1)
            except Exception as e:
                logger.warning(f"获取产品ID失败: {e}")
            
            # 库存状态
            try:
                availability_selectors = [
                    "[data-testid='availability']",
                    ".stock-status",
                    ".availability",
                    ".inventory-status"
                ]
                
                for selector in availability_selectors:
                    try:
                        availability_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        product.availability = availability_element.text.strip()
                        if product.availability:
                            break
                    except NoSuchElementException:
                        continue
                        
            except Exception as e:
                logger.warning(f"获取库存状态失败: {e}")
            
            logger.info(f"Selenium爬取完成: {product.name}")
            
        except Exception as e:
            logger.error(f"Selenium爬取过程中出错: {e}")
        
        return product
    
    def close_driver(self):
        """关闭驱动器"""
        if self.driver:
            self.driver.quit()
            logger.info("驱动器已关闭")
    
    def scrape_with_selenium(self, url: str) -> ProductInfo:
        """完整的Selenium爬取流程"""
        if not self.setup_driver():
            logger.error("无法设置驱动器")
            return ProductInfo()
        
        try:
            product = self.scrape_product_selenium(url)
            return product
        finally:
            self.close_driver()


def main_selenium():
    """使用Selenium的主函数"""
    url = "https://us.puma.com/us/en/pd/evospeed-mid-distance-nitro-elite-3-track--field-distance-spikes/312637?swatch=01"
    
    scraper = PumaSeleniumScraper(headless=True)
    product = scraper.scrape_with_selenium(url)
    
    if product and product.name:
        print("\n" + "="*50)
        print("Selenium爬取结果")
        print("="*50)
        print(f"商品名称: {product.name}")
        print(f"价格: {product.price}")
        print(f"原价: {product.original_price}")
        print(f"颜色: {product.color}")
        print(f"可用尺码: {', '.join(product.sizes)}")
        print(f"商品ID: {product.product_id}")
        print(f"库存状态: {product.availability}")
        print(f"图片数量: {len(product.images)}")
        print(f"描述: {product.description[:100]}..." if len(product.description) > 100 else f"描述: {product.description}")
        
        # 保存到文件
        try:
            with open("product_info_selenium.json", 'w', encoding='utf-8') as f:
                json.dump(asdict(product), f, ensure_ascii=False, indent=2)
            print("信息已保存到 product_info_selenium.json")
        except Exception as e:
            print(f"保存文件失败: {e}")
    else:
        print("Selenium爬取失败")


if __name__ == "__main__":
    main_selenium()