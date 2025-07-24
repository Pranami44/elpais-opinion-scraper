# test_el_pais_opinion.py
import os
import json
import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By

@pytest.fixture(scope="session")
def driver():
    # BrowserStack remote is handled by SDK; you just call webdriver.Chrome()
    driver = webdriver.Chrome()
    yield driver
    driver.quit()

def test_opinion_page_loads(driver):
    # set session name
    driver.execute_script("browserstack_executor: " + json.dumps({
        "action": "setSessionName", "arguments": {"name": "Opinion page load"} }))
    driver.get("https://elpais.com/opinion/")
    time.sleep(3)
    assert "Opinión" in driver.title
    # mark test status
    driver.execute_script("browserstack_executor: " + json.dumps({
        "action": "setSessionStatus", "arguments": {"status": "passed", "reason": "Title matched Opinión"} }))
