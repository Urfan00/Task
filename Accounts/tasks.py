from celery import shared_task
from selenium import webdriver
from .models import Instagram
import time


@shared_task
def update_instagram_account_info():
    for account in Instagram.objects.all():

        # Instagram'a giriş
        driver = webdriver.Chrome()
        driver.get('https://www.instagram.com/')
        driver.implicitly_wait(5)
        username_input = driver.find_element('name', 'username')
        username_input.send_keys(account.username)
        password_input = driver.find_element('name', 'password')
        password_input.send_keys(account.password)
        login_button = driver.find_element("css selector",'#loginForm > div > div:nth-child(3) > button > div')
        login_button.click()
        time.sleep(3)

        # Follower & following count
        driver.get("https://www.instagram.com/" + account.username + '/')
        time.sleep(5)

        try:
            followers = driver.find_element("css selector", '.x78zum5 li:nth-child(2) button span').text
            following = driver.find_element("css selector", '.x78zum5 li:nth-child(3) button span').text
        except:
            followers = driver.find_element("xpath", '//a[contains(@href,"/followers")]/span').text
            following = driver.find_element("xpath", '//a[contains(@href,"/following")]/span').text

        account.follower = int(followers)
        account.following = int(following)
        account.save()

        driver.quit()
