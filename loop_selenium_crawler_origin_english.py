from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import json
import time
import os

tasks = ["arbeit","haushalt","freizeit"]
with open('unfall.json') as f:
    unfall_keywords = json.load(f)

for task in tasks: 
    if not os.path.exists(f"scraped_news_3/{task}"):
        os.makedirs(f"scraped_news_3/{task}")

zustimmen_keywords = ["zustimmen", "ich bin einverstanden","akzeptieren und weiter","einwilligen und weiter","akzeptieren","einverstanden"]
cookies_keywords = ["nur notwendige cookies","nur essenzielle cookies","alle ablehnen", "alles akzeptieren","alle akzeptieren","einstellungen speichern","ablehnen","verbieten","nein,danke","nein, danke","schließen"]



#options.add_argument('--headless')
#driver = webdriver.Chrome(options=options)
#driver = webdriver.Chrome()
import undetected_chromedriver as uc
#options = uc.ChromeOptions()
#options.headless = True
#driver = uc.Chrome(options=options)
driver = uc.Chrome(enable_cdp_events=True,version_main= 133)

def google_search(driver, keyword, task):
    driver.get("https://www.google.com")
    try: 
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'alle ablehnen')]"))
        )
        button.click()
        time.sleep(1)
    except Exception:
        pass
    textarea = driver.find_element(By.XPATH, "//textarea[@title='Search']")
    textarea.click()
    time.sleep(1)
    textarea.send_keys(keyword)
    textarea.send_keys(Keys.RETURN)
    time.sleep(1) 
    results = driver.find_elements(By.CSS_SELECTOR, "div.tF2Cxc")[0:5]
    print("the length of result is " + str(len(results)))
    links = [result.find_element(By.TAG_NAME, "a").get_attribute("href") for result in results]
    links = [link for link in links if ".de" in link] # only visit german websites
    for i, link in enumerate(links):
        driver.get(link)
        time.sleep(1)
        windows = driver.window_handles
        driver.switch_to.window(windows[-1])
        time.sleep(1)
        buttons = driver.find_elements(By.TAG_NAME, "button")
        try:
            for button in buttons:
                if any(keyword in button.get_attribute("innerHTML").lower() for keyword in zustimmen_keywords):
                    button.click()
                    break
        except Exception:
            pass
       
        try:
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            print(len(iframes))
            count = 0 
            original_window = driver.current_window_handle  
            for iframe in iframes:
                if count < 5:
                    print(f"this is the {count} frame")
                    print(iframe.get_attribute('title'))
                    driver.switch_to.frame(iframe)     
                    time.sleep(1)
                    buttons = driver.find_elements(By.TAG_NAME, "button")
                    for button in buttons:
                        print(button.get_attribute("title"))
                        if any(keyword in button.get_attribute("innerHTML").lower() for keyword in zustimmen_keywords):
                            print(button.get_attribute("title"))
                            driver.execute_script("arguments[0].click();", button)
                    count = count + 1         
                    driver.switch_to.window(original_window)
                    time.sleep(1)
                
        except Exception:
            pass
        time.sleep(1)
        windows = driver.window_handles
        driver.switch_to.window(windows[-1])
        time.sleep(1)
        buttons = driver.find_elements(By.TAG_NAME, "button")
        try:
            for button in buttons:
                if any(keyword in button.get_attribute("innerHTML").lower() for keyword in cookies_keywords):
                    button.click()
                    break
        except Exception:
            pass
        try:
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            print(len(iframes))
            count = 0 
            original_window = driver.current_window_handle  
            for iframe in iframes:
                if count < 5:
                    print(f"this is the {count} frame")
                    print(iframe.get_attribute('title'))
                    driver.switch_to.frame(iframe)     
                    time.sleep(1)
                    buttons = driver.find_elements(By.TAG_NAME, "button")
                    for button in buttons:
                        print(button.get_attribute("title"))
                        if any(keyword in button.get_attribute("innerHTML").lower() for keyword in cookies_keywords):
                            print(button.get_attribute("title"))
                            driver.execute_script("arguments[0].click();", button)
                    count = count + 1         
                    driver.switch_to.window(original_window)
                    time.sleep(1)
            
        except Exception:
            pass
        time.sleep(1)
        time_element = None
        try:
            paragraphs = driver.find_elements(By.TAG_NAME, "p")
            try: 
                time_element = driver.find_element(By.TAG_NAME, "time").text
            except Exception:
                pass
            if not time_element:
                try:
                    time_element = driver.find_element_by_xpath("//span[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'aktualisiert')]")
                except Exception:
                    pass
            if time_element:
                content = time_element + "\n" + "\n".join([p.text for p in paragraphs if p.text.strip()])
            else: 
                content = "\n".join([p.text for p in paragraphs if p.text.strip()])
            prefix = link.replace("https://", "").replace("www","").replace("http://", "").replace("//", "").replace("/", "_").replace(".", "_")[0:10]
            date = 0
            try:
                date = driver.find_element(By.XPATH, "//time[@data-manual='date']").get_attribute("datetime").split()[0]  
            except Exception:
                print("problem with date") 
            current_url = driver.current_url
            news_title = current_url.split('/')[-1]
            with open(f"scraped_news_3/{task}/news_{prefix}_{i+1}_{news_title}_{date}.txt", "w", encoding="utf-8") as file:
                file.write(content)

            print(f"Scraped and saved news_{prefix}_{i+1}_{date}.txt")
        except Exception as e:
            print(f"Failed to scrape {link}: {e}")
        
        time.sleep(1)
    
          
def main():
    for task in tasks:
        for keyword in unfall_keywords[task]:
            google_search(driver, keyword, task)
                

if __name__ == "__main__":
    main()
    driver.quit()
        