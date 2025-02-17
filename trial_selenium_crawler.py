from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import os


driver = webdriver.Chrome() 
driver.get("https://www.google.com")
time.sleep(2)
button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'alle ablehnen')]"))
    )
button.click()
time.sleep(3)
textarea = driver.find_element(By.XPATH, "//textarea[@title='Suche']")
textarea.click()
time.sleep(1)
textarea.send_keys("mann stürzt in der Arbeit")
textarea.send_keys(Keys.RETURN)
time.sleep(2) 
results = driver.find_elements(By.CSS_SELECTOR, "div.tF2Cxc")[0:10]
links = [result.find_element(By.TAG_NAME, "a").get_attribute("href") for result in results]
    
if not os.path.exists("scraped_news"):
    os.makedirs("scraped_news")

zustimmen_keywords = ["zustimmen", "ich bin einverstanden","akzeptieren und weiter","einwilligen und weiter"]
cookies_keywords = ["nur notwendige cookies","nur essenzielle cookies","alle ablehnen", "alles akzeptieren","alle akzeptieren","einstellungen speichern","ablehnen"]


for i, link in enumerate(links):
    driver.get(link)
    time.sleep(3)
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
            print(f"this is the {count} frame")
            print(iframe.get_attribute('title'))
            driver.switch_to.frame(iframe)     
            time.sleep(2)
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
    time.sleep(2)
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
    time.sleep(2)
    
    try:
        paragraphs = driver.find_elements(By.TAG_NAME, "p")
        content = "\n".join([p.text for p in paragraphs if p.text.strip()])
        prefix = link.replace("https://", "").replace("www","").replace("http://", "").replace("//", "").replace("/", "_").replace(".", "_")[0:16]
        date = 0
        try:
            date = driver.find_element(By.XPATH, "//time[@data-manual='date']").get_attribute("datetime").split()[0]  
        except Exception:
            print("problem with date") 
        with open(f"scraped_news1/news_{prefix}_{i+1}_{date}.txt", "w", encoding="utf-8") as file:
            file.write(content)

        print(f"Scraped and saved news_{prefix}_{i+1}_{date}.txt")
    except Exception as e:
        print(f"Failed to scrape {link}: {e}")
input('print sth to quit')
            
driver.quit()

