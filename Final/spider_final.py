from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import json


class Spider:
    def __init__(self):
        self.browser = webdriver.Chrome()
        self.country_infos = {}
        pass

    def get_country_urls(self):
        URL = "http://wx.wind.com.cn/WindSariWeb/sari/message.html?lan=cn"
        BUTTON_SELECTOR = "#root > div > div > div.layout-header > div.telecom > ul > li:nth-child(3) > div > a"
        TABLE_SELECTOR = "#root > div > div > div:nth-child(16) > div > div.w-card-body > span > div > div.w-table-wrapper > div > div > div > div > div > table > tbody"
        self.browser.get(URL)
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
            self.country_infos[country_name] = {}
            self.country_infos[country_name]["url"] = url
        print("urls reading completed")

    def get_country_statics(self, country_name, url):
        print("getting statics for {}".format(country_name))
        self.country_infos[country_name]["new_infected"] = {}
        NEW_INFECTED_SELECTOR = "#root > div > div:nth-child(2) > div > div > div:nth-child({}) > div > div.w-card-body > div:nth-child(2) > div"
        # ALL_INFECTED_SELECTOR = "#root > div > div:nth-child(2) > div > div > div:nth-child(5) > div > div.w-card-body > div:nth-child(4) > div > div:nth-child(1) > canvas"
        if (country_name == "美国"):    # 美国有地图! :(
            NEW_INFECTED_SELECTOR = NEW_INFECTED_SELECTOR.format(4)
        else:
            NEW_INFECTED_SELECTOR = NEW_INFECTED_SELECTOR.format(3)
        self.browser.get(url)
        new_infected_canvas: WebElement = self.browser.find_element(
            By.CSS_SELECTOR, NEW_INFECTED_SELECTOR)
        WIDTH = new_infected_canvas.size["width"]
        HEIGHT = new_infected_canvas.size["height"]
        for x_offset in range(int(WIDTH / 2)):
            mouse_move: ActionChains = ActionChains(self.browser)
            mouse_move.move_to_element_with_offset(new_infected_canvas,
                                                   int(WIDTH / 2) + x_offset, int(HEIGHT / 2))
            mouse_move.perform()
            if len(new_infected_canvas.text) == 0:
                break
            INFO = new_infected_canvas.text.split('\n')
            new = int(INFO[1][5:].replace(',', ''))
            self.country_infos[country_name]["new_infected"][INFO[0]] = new

        # all_infected_canvas: WebElement = self.browser.find_element(
        #     By.CSS_SELECTOR, NEW_INFECTED_SELECTOR)
        # WIDTH = all_infected_canvas.size["width"]
        # HEIGHT = all_infected_canvas.size["height"]
        # for x_offset in range(int(WIDTH / 2)):
        #     mouse_move: ActionChains = ActionChains(self.browser)
        #     mouse_move.move_to_element_with_offset(all_infected_canvas,
        #                                            int(WIDTH / 2) + x_offset, int(HEIGHT / 2))
        #     mouse_move.perform()
        #     if len(all_infected_canvas.text) == 0:
        #         break
        #     INFO = all_infected_canvas.text.split('\n')
        #     new = int(INFO[1][5:].replace(',', ''))
        #     self.country_infos[country_name]["new_infected"][INFO[0]] = new

    def write_json(self, path: str):
        with open(path, "w") as f:
            json.dump(self.country_infos, f, indent=4, ensure_ascii=False)

    def read_json(self, path: str):
        with open(path, "r") as f:
            self.country_infos = json.load(f)


if __name__ == "__main__":
    spider = Spider()
    spider.get_country_urls()
    for country_name, country_info in spider.country_infos.items():
        spider.get_country_statics(country_name, country_info["url"])
        spider.write_json("res.json")
