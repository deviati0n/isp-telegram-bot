import re
from datetime import timedelta

from parsel import Selector
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from database.models.db_users import Users
from database.users_class import UsersFunction
from project.project_context import ProjectContext
from utils.data_classes import BillingReport

context = ProjectContext()
users = UsersFunction()


class BillingFunction:
    """
    A class for parsing data from a billing system
    """

    @staticmethod
    def auth(url: str, driver: 'webdriver.Chrome') -> 'webdriver.Chrome':
        """
        User authorization to the billing system
        :param url: url of the billing system
        :param driver: instance of the chrome driver
        :return: instance of the chrome driver
        """
        driver.get(url)

        try:
            login = context.billing_config.login
            password = context.billing_config.password

            auth_bar = driver.find_element(By.NAME, 'user')
            auth_bar.clear()
            auth_bar.send_keys(login)

            auth_bar = driver.find_element(By.NAME, 'passwd')
            auth_bar.clear()
            auth_bar.send_keys(password)

            auth_bar.send_keys(Keys.RETURN)
        except NoSuchElementException:
            pass

        return driver

    def req_connecting_sub(self, driver: 'webdriver.Chrome', date_bill: str) -> list:
        """
        Gathers the number of connection requests for the day and from the beginning of the month
        :param driver: instance of the chrome driver
        :param date_bill: input date
        :return: list of the number of connection requests for each period
        """
        start_date = date_bill[:len(date_bill) - 2] + '01'
        driver = self.auth(context.billing_config.url + f'admin/index.cgi?index=178&search=1&type=178&PRIORITY=0'
                                                        f'&root_index=8&TO_DATE={date_bill}&'
                                                        f'search_form=1&PAGE_ROWS=100&FROM_DATE={start_date}&'
                                                        f'ALL_MSGS=1&pg=0', driver)

        req_connect_subs_day = driver.find_elements(By.PARTIAL_LINK_TEXT, date_bill)
        req_connect_subs_period = 0
        page = 100

        while True:
            req_connect_subs = driver.find_elements(By.PARTIAL_LINK_TEXT, date_bill[:len(date_bill) - 2])
            req_connect_subs_period += len(req_connect_subs)

            if len(req_connect_subs) < 100:
                break
            else:
                driver.find_element(By.XPATH, f'//*/a[@title = {page}]').click()
                page += 100

        return [len(req_connect_subs_day), req_connect_subs_period]

    def connecting_sub(self, driver: 'webdriver.Chrome', date_bill: str) -> list:
        """
        Gathers the number of ready connection for the day and from the beginning of the month
        :param driver: instance of the chrome driver
        :param date_bill: input date
        :return: list of the number of ready connections for each period
        """
        start_date = date_bill[:len(date_bill) - 2] + '01'
        driver = self.auth(context.billing_config.url + f'admin/index.cgi?index=22&search_form=1&LOGIN=&'
                                                        f'PAGE_ROWS=&FROM_DATE={start_date}&TO_DATE={date_bill}&'
                                                        f'ADMIN=&ACTION=&TYPE=7&MODULE=&IP=&search=1', driver)

        connect_table = driver.find_element(By.ID, 'p_')
        connect_subs = connect_table.find_element(By.TAG_NAME, 'b')

        connect_subs_day = driver.find_elements(By.XPATH, f".//*[@id='ADMIN_ACTIONS_']//td[contains(., '{date_bill}')]")

        return [len(connect_subs_day), connect_subs.text]

    def calculate_payment(self, driver: 'webdriver.Chrome', date_bill: str) -> list:
        """
        Gathers the amount of money transfers for the day and from the beginning of the month
        :param driver: instance of the chrome driver
        :param date_bill: input date
        :return: list of the amount of money transfers for each period
        """
        start_date = date_bill[:len(date_bill) - 2] + '01'

        driver = self.auth(context.billing_config.url + f'admin/index.cgi?index=42', driver)

        list_of_payment_systems = ('Банк', 'Payberry', 'RNCB', 'GenBank', '24Alltime')
        for el in list_of_payment_systems:
            driver.find_element(By.XPATH, f"//td[contains( text(), '{el}')]/input").click()

        date_to_date = driver.find_element(By.NAME, 'FROM_DATE_TO_DATE')
        date_to_date.clear()
        date_to_date.send_keys(start_date + '/' + date_bill)

        driver.find_element(By.CLASS_NAME, 'breadcrumb').click()

        driver.find_element(By.NAME, 'show').click()

        sum_table = driver.find_element(By.ID, 'p_')
        sum_payment = sum_table.find_element(By.XPATH, '//*/table/tbody/tr/td[3]/b')
        sum_day = driver.find_element(By.XPATH, '//*/table[@id = "REPORTS_PAYMENTS_"]/tbody/tr[last()]/td[4]')

        return [sum_day.text, sum_payment.text]

    def report_acc_bill(self, date_bill: dict):
        """
        Makes a monthly report for each payment systems
        :param date_bill: input date
        :return: final report
        """
        driver = webdriver.Chrome(context.path)
        driver = self.auth(context.billing_config.url + f'admin/index.cgi?index=42', driver)

        msg_list = []
        list_of_payment_systems = ['RNCB', 'Payberry', 'GenBank', '24Alltime']

        for el in list_of_payment_systems:
            driver.find_element(By.XPATH, f"//td[contains(text(), '{el}')]/input").click()

            date_to_date = driver.find_element(By.NAME, 'FROM_DATE_TO_DATE')
            date_to_date.clear()
            date_to_date.send_keys(str(date_bill['first_date']) + '/' + str(date_bill['last_date']))

            driver.find_element(By.CLASS_NAME, 'breadcrumb').click()
            driver.find_element(By.NAME, 'show').click()

            sum_table = driver.find_element(By.ID, 'p_')
            sum_payment = sum_table.find_element(By.XPATH, '//*/table/tbody/tr/td[3]/b').text

            driver.find_element(By.XPATH, f"//td[contains(text(), '{el}')]/input").click()
            msg_list.append(f'{el} - {sum_payment}')

        return '\n'.join(msg_list)

    @staticmethod
    def update_dict_bill(requests: list, connections: list, sum_payments: list,
                         bill: dict[str, float]) -> dict[str, float]:
        """
        Updates the dict with new data
        :param requests: list of the number of connection requests for each period
        :param connections: list of the number of ready connections for each period
        :param sum_payments: list of the amount of money transfers for each period
        :param bill: dict with the received data
        :return: updated dict
        """
        bill['dayReq'] += int(requests[0])
        bill['periodReq'] = max(int(requests[1]), int(bill['periodReq']))

        bill['dayCon'] += int(connections[0])
        bill['periodCon'] = max(int(connections[1]), int(bill['periodCon']))

        bill['daySum'] += float(sum_payments[0])
        bill['periodSum'] = max(float(sum_payments[1]), bill['periodSum'])

        return bill

    def billing_report(self, date_bill: dict) -> str:
        """
        Preparations of a daily report
        :param date_bill: dict with start and end date
        :return: final report
        """
        driver = webdriver.Chrome(context.path)

        bill = {'dayReq': 0, 'periodReq': 0, 'dayCon': 0, 'periodCon': 0, 'daySum': 0, 'periodSum': 0, 'percent': 0.0}

        while date_bill['first_date'] <= date_bill['last_date']:
            req = self.req_connecting_sub(driver, str(date_bill['first_date']))
            con = self.connecting_sub(driver, str(date_bill['first_date']))
            sum_payments = self.calculate_payment(driver, str(date_bill['first_date']))

            bill = self.update_dict_bill(req, con, sum_payments, bill)
            date_bill['first_date'] = date_bill['first_date'] + timedelta(days=1)

        bill['percent'] = round((float(bill['periodSum']) * 100) / context.billing_config.plan, 1)
        driver.close()

        report: str = BillingReport(bill).report()
        return report

    def receive_user_data(self):
        """
        Gathers all users from the billing system
        """
        driver = webdriver.Chrome(context.path)
        driver = self.auth(context.billing_config.url + f'admin/index.cgi?index=11&pg=0', driver)

        all_user = driver.find_element(By.XPATH, '//*[@id="_"]/tbody/tr[1]/td[2]/b').text
        pages = round(int(all_user) + 50, -2)

        driver.get(context.billing_config.url + f'admin/index.cgi?index=11&PAGE_ROWS={pages}')
        py_source = driver.find_element(By.XPATH, '//*[@id="USERS_LIST_"]/tbody').get_attribute('outerHTML')

        selector = Selector(text=py_source)

        users_login = selector.xpath('//tbody/tr[*]/td[2]/a[2]/text()').getall()
        users_balance = selector.xpath('//tbody/tr[*]/td[4]//text()').getall()
        users_date_contract = selector.xpath('//tbody/tr[*]/td[9]/text()').getall()
        users_last_payment = selector.xpath('//tbody/tr[*]/td[10]').getall()
        users_group = selector.xpath('//tbody/tr[*]/td[12]').getall()

        print(f"[+] Got all elements of table: {len(users_login)}, {len(users_balance)}, "
              f"{len(users_date_contract)}, {len(users_last_payment)}, {len(users_group)}")

        not_empty_tag = r'^<td>([а-яА-я]+|([\d\s:-]+))</td>$'
        list_of_users: list['Users'] = []

        for login, balance, contract, last_payment, group in zip(users_login, users_balance, users_date_contract,
                                                                 users_last_payment, users_group):
            check_l_p = re.match(not_empty_tag, last_payment)
            check_g = re.match(not_empty_tag, group)

            last_payment = check_l_p.group(1) if check_l_p else None
            group = check_g.group(1) if check_g else None

            list_of_users.append(Users(
                login=login,
                balance=balance,
                date_contract=contract,
                date_last_payment=last_payment,
                group=group
            ))

        print("[+] Created list with models")

        users.add_user(list_of_users)
        print("[+] Added data to the table")

    def receive_active_users(self):
        """
        Gathers all active users from the billing system
        """
        users.clear_all_active()

        driver = webdriver.Chrome(context.path)
        driver = self.auth(context.billing_config.url + f'admin/index.cgi?index=150', driver)

        list_of_servers = [1, 2, 90]

        for nas_id in list_of_servers:
            driver.get(context.billing_config.url + f'admin/index.cgi?index=150&NAS_ID={nas_id}&pg=0')

            users_login = driver.find_elements(By.XPATH, '//*[@id="INTERNET_ONLINE_"]/tbody/tr[*]/td[1]/a')

            for login in users_login:
                login = login.text
                if users.find_users(login):
                    users.update_active_status(login)
