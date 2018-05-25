import os
import re
import time
import pytest
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.fixture
def context():
    return {
        'selenium_grid_hub': 'http://127.0.0.1:4444/wd/hub',
        'driver_desired_capabilities': DesiredCapabilities.CHROME,
        'page_load_timeout': 5,
        'screenshots_dir': f'{os.path.join(os.environ["TEMP"], "SeleniumScreenshots")}',
        'base_url': 'http://shipovalov.net',
        'login': 'student',
        'password': 'luxoft',
        'test_project_name': 'test-mir-project'
    }

@pytest.fixture
def driver(context):
    wd = webdriver.Remote(context['selenium_grid_hub'], desired_capabilities=context['driver_desired_capabilities'])
    wd.maximize_window()
    yield wd
    wd.quit()

@pytest.fixture
def login(driver, context):
    def do_login():
        driver.get(context['base_url'])
        driver.find_element_by_name('username').send_keys(context['login'])
        driver.find_element_by_name('password').send_keys(context['password'])
        driver.find_element_by_css_selector('.button').click()
        WebDriverWait(driver, context['page_load_timeout']).until(EC.title_contains('Mantis'))
    return do_login


@pytest.fixture
def switch_project(driver):
    def do_switch_project(project_name):
        project_select = Select(driver.find_element_by_css_selector('select[name=project_id]'))
        project_select.select_by_visible_text(project_name)
        button_switch = driver.find_element_by_css_selector('.login-info-right input.button-small')
        button_switch.click()
    return do_switch_project


@pytest.fixture
def add_new_issue(driver, context):
    def do_add_new_issue(summary, description, category_index=1):
        report_bug_page_url = f'{context["base_url"]}/bug_report_page.php'
        driver.get(report_bug_page_url)

        WebDriverWait(driver, context['page_load_timeout']).until(EC.title_contains('Report Issue'))

        category_select = Select(driver.find_element_by_css_selector('form [name=category_id]'))

        category_select.select_by_index(category_index)

        summary_field = driver.find_element_by_css_selector('form[name=report_bug_form] [name=summary]')
        summary_field.send_keys(summary)

        description_field = driver.find_element_by_css_selector('form[name=report_bug_form] [name=description]')
        description_field.send_keys(description)

        submit_button = driver.find_element_by_css_selector('form[name=report_bug_form] input.button')
        submit_button.click()

        WebDriverWait(driver, context["page_load_timeout"]).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'body>div:nth-of-type(2)')))

        message = driver.find_element_by_css_selector('body>div:nth-of-type(2)').text
        m = re.match(r'Operation successful\.\n\[ View Submitted Issue (\d+) \]', message)

        assert m, 'ID of created issue is not found in "Operation successful" message'

        return int(m.group(1))


    return do_add_new_issue


@pytest.fixture
def all_issues(driver, context):
    def do_get_issues_list(save_screenshots=False):
        view_issues_url = f'{context["base_url"]}/view_all_bug_page.php'
        driver.get(view_issues_url)
        if save_screenshots:
            driver.save_screenshot(f'{context["screenshots_dir"]}\\issue_list_page_{time.time()}.png')
        issues_table = driver.find_element_by_css_selector('form[name=bug_action]>table#buglist')
        issues_on_page = {}

        for table_row_elem in issues_table.find_elements_by_css_selector('tbody>tr'):
            if not table_row_elem.find_elements_by_css_selector('input[name=bug_arr\\[\\]]'):
                continue
            issue_id = int(table_row_elem.find_element_by_css_selector('td:nth-child(4)>a').text)
            issue_summary = table_row_elem.find_element_by_css_selector('td.left').text
            issues_on_page[issue_id] = issue_summary
        return issues_on_page
    return do_get_issues_list

@pytest.mark.skip('Skipped. Test will fail as a project is already created')
def test_add_new_project(driver, context, login):
    login(driver, context)

    driver.find_element_by_link_text('Manage').click()
    driver.find_element_by_link_text('Manage Projects').click()

    driver.find_element_by_css_selector('td.form-title > form > input.button-small').click()

    driver.find_element_by_name('name').send_keys(context['test_project_name'])
    driver.find_element_by_css_selector('textarea').send_keys('test description')
    driver.find_element_by_class_name('button').click()




def test_new_issue_is_created(context, login, switch_project, add_new_issue, all_issues):

    expected_summary = 'Test. Summary for issue'
    expected_description = 'Test. Description for issue'

    login()
    switch_project(project_name=context['test_project_name'])
    issue_id = add_new_issue(summary=expected_summary, description=expected_description)

    issues = all_issues(save_screenshots=True)

    assert issue_id in issues, 'Issue ID is not found in all issues list'
    assert issues[issue_id] == expected_summary, 'Issue summary field is not the same'



