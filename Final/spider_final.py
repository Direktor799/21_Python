from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import datetime

country_urls = []

URL = "http://wx.wind.com.cn/WindSariWeb/sari/message.html?lan=cn"


class Spider:
    def __init__(self):
        self.browser = webdriver.Chrome()
        pass

    def get_country_urls(self):
        self.browser.get(URL)
        BUTTON_SELECTOR = "#root > div > div > div.layout-header > div.telecom > ul > li:nth-child(3) > div > a"
        TABLE_SELECTOR = "#root > div > div > div:nth-child(16) > div > div.w-card-body > span > div > div.w-table-wrapper > div > div > div > div > div > table > tbody"
        self.browser.find_element(
            By.CSS_SELECTOR, BUTTON_SELECTOR).click()   # 国外疫情
        table: WebElement = self.browser.find_element(
            By.CSS_SELECTOR, TABLE_SELECTOR)
        WebDriverWait(self.browser, 60).until(
            expected_conditions.presence_of_element_located((By.CSS_SELECTOR, TABLE_SELECTOR + " > tr:nth-child(2)")))
        print("reading urls")
        for i in range(100):
            line: WebElement = table.find_element(
                By.CSS_SELECTOR, "tr:nth-child({})".format(i + 1))
            country_name = line.find_element(
                By.CSS_SELECTOR, "td.w-table-cell.w-table-align-left.w-table-header-align-center > span").text
            url = line.find_element(
                By.CSS_SELECTOR, "td.w-table-cell.w-table-align-center.w-table-header-align-right.w-table-last-column > a").get_attribute("href")
            country_urls.append((country_name, url))
        print("urls reading completed")
        return country_urls

    def get_graph_data(self, country_name, url):
        dict = {}
        GRAPH_SELECTOR = "#root > div > div:nth-child(2) > div > div > div:nth-child(4) > div > div.w-card-body > div:nth-child(2) > div"
        self.browser.get(url)
        canvas: WebElement = self.browser.find_element(
            By.CSS_SELECTOR, GRAPH_SELECTOR)
        WIDTH = canvas.size["width"]
        mouse_action: ActionChains = ActionChains(self.browser)
        mouse_action.move_to_element(canvas)
        mouse_action.perform()
        for _ in range(int(WIDTH / 2)):
            mouse_action.move_by_offset(1, 0).perform()
            INFO = canvas.text.split('\n')
            date = datetime.datetime.strptime(INFO[0], "%m-%d")
            date = date.date().replace(2021)
            new = int(INFO[1][5:].replace(',', ''))
            dict[date] = new
        print(dict)


if __name__ == "__main__":
    spider = Spider()
    country_urls = spider.get_country_urls()
    for country, url in country_urls:
        spider.get_graph_data(country, url)
