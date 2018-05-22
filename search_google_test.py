import pytest
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.fixture
def driver(request):
    options = webdriver.ChromeOptions()
    #options.add_argument('--start-fullscreen')
    wd = webdriver.Chrome('chromedriver.exe', chrome_options=options)

    #wd = webdriver.Ie( capabilities={'ignoreZoomSetting': True})
    wd.maximize_window()
    print(wd.capabilities)
    request.addfinalizer(wd.quit)
    return wd


def test_add_new_project(driver):
    driver.get('http://shipovalov.net')
    driver.find_element_by_name('username').send_keys('student')
    driver.find_element_by_name('password').send_keys('luxoft')
    driver.find_element_by_css_selector('.button').click()

    WebDriverWait(driver, 5).until(EC.title_contains('Mantis'))

    driver.find_element_by_link_text('Manage').click()
    driver.find_element_by_link_text('Manage Projects').click()

    driver.find_element_by_css_selector('td.form-title > form > input.button-small').click()

    driver.find_element_by_name('name').send_keys('test-mir-project')
    driver.find_element_by_css_selector('textarea').send_keys('test description')
    driver.find_element_by_class_name('button').click()



