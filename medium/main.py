# -*- coding: utf-8 -*-

def main():
    driver = getDriver()
    
    #get list page
    url = "https://medium.com/search?q=google%20analytics"
    driver.get(url)
    
    links = scroll(driver)
    for link in links:
        data = [getData(link, driver)]
        writeJSON(data, "medium__google_analytics")
            
def getDriver():
    from selenium import webdriver
    import json    
    CONFIG_file = open("config.json","r")
    CONFIG = json.load(CONFIG_file)    
    profile_path = "user-data-dir=" + CONFIG["user_profile"]["profile_path"]
    profile_directory = "--profile-directory=" + CONFIG["user_profile"]["profile_directory"]
    profile_user_agent = "--user-agent=" + CONFIG["user_profile"]["vitual_user_agent"]
    
    options = webdriver.ChromeOptions()
    options.add_argument(profile_path)
    options.add_argument(profile_directory)
    options.add_argument(profile_user_agent)
    #options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    return driver


def scroll(driver):
    #init scroll method
    import json
    wait_seconds = 3
    CONFIG_file = open("config.json","r")
    CONFIG = json.load(CONFIG_file)
    max_position = driver.execute_script("return document.body.scrollHeight")
    current_position = CONFIG["scroll"]["first_current_position"]
    speed = CONFIG["scroll"]["speed"]
    buffer = CONFIG["scroll"]["buffer"]
    
    #init get data method
    data_size = CONFIG["data"]["size"]
    
    #TEST
    if CONFIG["test"] == 1:
        links = getLinks(driver)
        return links
    
    #scroll list page
    while current_position < max_position:
        print("current_position:",current_position , "max_position:",max_position, "speed:",speed)
        driver.execute_script("window.scrollTo(0, "+str(current_position)+");")
        current_position += speed
        if max_position - current_position < buffer:
            max_position += buffer
    #get links
        links = getLinks(driver)
        get_link_size = len(links)
        print("get_link_size:",get_link_size)
        if(get_link_size > data_size):
            break
    return links

def getLinks(driver):
    #init get links method
    parent_node_selector = '.js-postListHandle'
    target_nodes_selector = '.postArticle-readMore a'
    #get links
    parent_node = driver.find_element_by_css_selector(parent_node_selector)
    target_nodes = parent_node.find_elements_by_css_selector(target_nodes_selector)
    links = list(map(lambda x:x.get_attribute('href'), target_nodes))
    return links


def getData(url, driver):
    #import datetime
    import re
    from time import sleep    
    wait_seconds = 3
    
    driver.get(url)    
    sleep(wait_seconds)
    
    url = driver.current_url
    title = driver.title.replace('\u2014', '')
    title_sub =  driver.find_element_by_css_selector('h2').text.replace('\u2014', '')
    description = driver.find_element_by_css_selector('meta[name="description"]').get_attribute('content').replace('\u2014', '')

    published_date_str = driver.find_element_by_css_selector('meta[property="article:published_time"]').get_attribute('content').split("T")[0]
    #published_date = datetime.datetime.strptime(published_time, '%Y-%m-%d')
    
    categories = []
    tags = driver.find_elements_by_css_selector('a')
    regex = re.compile( "^https:\/\/.*\/tag.*" )
    for tag in tags:
        href = tag.get_attribute("href")
        if regex.search(href):
            categories.append(tag.text)
            
    data = {
        "url": url,
        "title": title,
        "title_sub": title_sub,
        "description": description,
        "published_date": published_date_str,
        "categories": [categories],
    }
    print(data)
    return data


def writeJSON(data, name):
    import jsonlines
    with jsonlines.open(name+".json", 'a') as writer:
        writer.write_all(data)
        #https://cloud.google.com/bigquery/docs/loading-data-cloud-storage-json?hl=ja#json_options
        #>改行で区切られた JSON 形式は、JSON Lines と同じ形式になります。
        #https://stackoverflow.com/questions/38915183/python-conversion-from-json-to-jsonl
        

if __name__ == "__main__":
    main()
