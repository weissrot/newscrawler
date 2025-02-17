from seleniumbase import Driver
from datetime import datetime

# Function to take screenshot using SeleniumBase Driver with undetected Chrome
def take_screenshot():
    # Create an undetected ChromeDriver instance in headless mode
    driver = Driver(uc=True, headless=True)

    # Go to Google
    driver.get("https://www.google.com")

    # Create a timestamp for the screenshot filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    screenshot_path = f"/Users/ying/Desktop/google_screenshot_{timestamp}.png"

    # Save screenshot
    driver.save_screenshot(screenshot_path)

   
    driver.quit()
take_screenshot()