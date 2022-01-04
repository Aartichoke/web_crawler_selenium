# scrape() function courtesy of https://github.com/scrapehero-code/amazon-scraper

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selectorlib import Extractor
import requests
import json
import time

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))


def main():
    link = 'https://www.amazon.com/s?i=tools&bbn=10158976011&rh=n%3A10158976011%2Cn%3A228013%2Cn%3A3754161%2Cn%3A680350011%2Cn%3A6871439011%2Cn%3A13749901&dc&qid=1639444612&rnid=10158976011&ref=sr_nr_n_1'
    pages = search_amazon(link) # <------ search query goes here.

    # Create an Extractor by reading from the YAML file
    e = Extractor.from_yaml_file('search_results.yml')

    # product_data = []
    with open("search_results_urls.txt",'r') as urllist, open('search_results_output.jsonl','w') as outfile:
        for url in urllist.read().splitlines():
            for page in pages:
                data = e.extract(page)
                for product in data['products']:
                    product['search_url'] = url
                    product['link'] = "amazon.com" + product['url'].split('/ref=')[0] + '/&qid' + product['url'].split('&qid')[1]
                    print(product['link'])
                    #product['new_price'] = get_page(product['link'])
                    print("Saving Product: %s"%product['title'].encode('utf8'))
                    if float(product['price'].replace('$', '')) > 20:
                        json.dump(product, outfile)
                        outfile.write("\n")

def get_page(link):
    driver.get(link)
    driver.implicitly_wait(5)
    src = driver.page_source
    e = Extractor.from_yaml_file('amazon_new.yml')
    data = e.extract(src)
    print("QQQ", data['product']['price'])
    return data['product']['price']




def search_amazon(link):
    driver.get(link)
    #search_box = driver.find_element_by_id('twotabsearchtextbox').send_keys(link)
    #search_button = driver.find_element_by_id("nav-search-submit-text").click()

    driver.implicitly_wait(5)

    try:
        num_page = driver.find_element_by_xpath('//*[@class="a-pagination"]/li[6]')
    except NoSuchElementException:
        num_page = driver.find_element_by_class_name('a-last').click()

    driver.implicitly_wait(10)

    url_list = []
    out = []

    # navigate through pages
    for i in range(int(num_page.text)):
        page_ = i + 1
        url_list.append(driver.current_url)
        driver.implicitly_wait(6)
        out.append(driver.page_source)
        click_next = driver.find_element_by_class_name('a-last').click()
        print("Page " + str(page_) + " grabbed")
        time.sleep(2)

    driver.quit()

    with open('search_results_urls.txt', 'w') as filehandle:
        for result_page in url_list:
            filehandle.write('%s\n' % result_page)

    return out

def scrape(url, e):
    headers = {
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.amazon.com/',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    }

    # Download the page using requests
    print("Downloading %s"%url)
    r = requests.get(url, headers=headers)
    # Simple check to check if page was blocked (Usually 503)
    if r.status_code > 500:
        if "To discuss automated access to Amazon data please contact" in r.text:
            print("Page %s was blocked by Amazon. Please try using better proxies\n"%url)
        else:
            print("Page %s must have been blocked by Amazon as the status code was %d"%(url,r.status_code))
        return None
    # Pass the HTML of the page and create
    print(r.text)
    #try:
    return e.extract(r.text)
    #except:
    #    pass

if __name__ == '__main__':
    main()
