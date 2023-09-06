import seleniumwire.undetected_chromedriver.v2 as webdriver
from selenium_stealth import stealth

from dotenv import load_dotenv, find_dotenv
from selenium.webdriver.common.by import By

load_dotenv(find_dotenv())


def get_chromedriver(proxy_setup=False, user_agent=None):
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--ignore-ssl-errors=yes')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--disable-crash-reporter')
    # chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # chrome_options.add_experimental_option('useAutomationExtension', False)
    
    if user_agent:
        chrome_options.add_argument(f'--user-agent={user_agent}')
    
    if proxy_setup:
        seleniumwire_options = {
            'proxy': {
                'http': f'http://{proxy_setup}',
                'https': f'http://{proxy_setup}',
                # 'no_proxy': 'localhost,127.0.0.1'  # excludes
            },
            'verify_ssl': False
        }
        driver = webdriver.Chrome(options=chrome_options, seleniumwire_options=seleniumwire_options)
        driver.get('http://httpbin.org/ip')
        print(driver.find_element(By.TAG_NAME, 'body').text)  # { "origin": "185.199.229.156" }

        stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )
        
        # driver.maximize_window()
        
        return driver

    driver = webdriver.Chrome(options=chrome_options)
    # driver.get('http://httpbin.org/ip')
    # print(driver.find_element(By.TAG_NAME, 'body').text)  # { "origin": "185.199.229.156" }
    #
    return driver

#
# if __name__ == '__main__':
#     main()
#
    # ------------------------------------------------------------------------------------

    



