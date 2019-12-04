import json
import threading
import time

from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

pages = []
isFinished = False
data = {}


class myThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global isFinished, pages, data
        ua = UserAgent()
        a = ua.random
        user_agent = a
        options = Options()
        options.add_argument(f'user-agent={user_agent}')
        browser = webdriver.Chrome(options=options)
        while isFinished is False or len(pages) > 0:
            if len(pages) > 0:
                url = pages.pop()
                browser.get(url)

                name = browser.find_element_by_tag_name('h1').text
                td = browser.find_elements_by_tag_name('td')[0]
                ingredient = td.find_elements_by_tag_name('li')
                instructions = td.find_element_by_tag_name('p').text
                all_ingredients = [x.text for x in ingredient]
                only_ingredients = [x.find_element_by_class_name('ingr').text for x in ingredient]
                category = \
                    browser.find_element_by_xpath("//*[text()='Category:']/../..").find_elements_by_tag_name('small')[
                        1].text
                alcohol = \
                    browser.find_element_by_xpath("//*[text()='Alcohol:']/../..").find_elements_by_tag_name('small')[
                        1].text
                glass = \
                    browser.find_element_by_xpath("//*[text()='Serve in:']/../..").find_elements_by_tag_name('small')[
                        1].text
                try:
                    rating = \
                        browser.find_element_by_xpath("//*[text()='Rating:']/../..").find_elements_by_tag_name('small')[
                            1].find_element_by_tag_name('b').text
                except:
                    rating = "not rated"
                data[name] = {'instructions': instructions, 'ingredients': only_ingredients,
                              'ingredientsWithAmount': all_ingredients, 'category': category, 'alcohol': alcohol,
                              'glass': glass, 'rating': rating, 'name': name}
            else:
                time.sleep(2)
        browser.quit()


class myIndexCrawler(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global isFinished, pages
        ua = UserAgent()
        a = ua.random
        user_agent = a
        options = Options()
        options.add_argument('user-agent={user_agent}')
        browser = webdriver.Chrome(options=options)
        url = "https://www.webtender.com/db/browse?level=2&dir=drinks&char=%2A&start=1"
        browser.get(url)

        next = browser.find_element_by_xpath("//*/a[text()='Next']")
        while next is not None:
            cocktails = browser.find_elements_by_tag_name('li')
            cocktails = [x.find_element_by_tag_name('a').get_attribute('href') for x in cocktails]
            pages.extend(cocktails)
            next.click()
            try:
                next = browser.find_element_by_xpath("//*/a[text()='Next']")
            except:
                print('err')
                next = None
        isFinished = True
        browser.quit()


threads = []

pagesSearch = myIndexCrawler()
pagesSearch.start()
threads.append(pagesSearch)

for i in range(11):
    current = myThread()
    current.start()
    threads.append(current)

for t in threads:
    t.join()

export = []

for i in data.keys():
    export.append(data[i])

with open("details.json", 'w') as f:
    json.dump(export, f)
