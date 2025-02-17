from seleniumbase import Driver

def take_screenshot():
    driver = Driver(uc=True, headless=True)  # Undetected Chrome, Headless mode
    driver.get("https://www.google.com")
    
    # Save screenshot
    screenshot_path = "/app/google_screenshot.png"
    driver.save_screenshot(screenshot_path)
    print(f"Screenshot saved at: {screenshot_path}")
    
    driver.quit()

if __name__ == "__main__":
    take_screenshot()
