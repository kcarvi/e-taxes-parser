# -*- coding: UTF-8 -*-

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import sys, os, time, csv


LOGIN_URL = 'https://login.e-taxes.gov.az/login/'

print('[+] Введите код пользователя:')
USERNAME = input()

print('[+] Введите пароль:')
PASSWORD2 = input()

print('[+] Введите шифр:')
PASSWORD1 = input()


''' CMD '''
#driver = webdriver.Chrome()

''' INSTALLER '''
chromedriver_path = os.path.join(sys._MEIPASS, "chromedriver.exe")
driver = webdriver.Chrome(chromedriver_path)

''' Список всех ссылок на документы '''
doc_list = []

''' Авторизация на сайте '''
def login():
    print('[INFO] Авторизация...')

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="tab"]//a[@href="#Section2"]'))).click()
    time.sleep(1)

    username_input = driver.find_element_by_id('username')
    username_input.clear()
    username_input.send_keys(USERNAME)
    time.sleep(1)

    password2_input = driver.find_element_by_id('password2')
    password2_input.clear()
    password2_input.send_keys(PASSWORD2)
    time.sleep(1)

    password1_input = driver.find_element_by_id('password1')
    password1_input.clear()
    password1_input.send_keys(PASSWORD1)
    time.sleep(1)

    driver.find_element_by_xpath("//select[@name='idare']/option[text()='E-qaimə']").click()
    time.sleep(1)

    driver.find_element_by_xpath("//div[@id='Section2']//button[@class='login-btn']").click()
    time.sleep(1)

''' Выход из аккаунта '''
def logout():
    print('[INFO] Выход...')

    driver.find_element_by_id('logout').click()
    time.sleep(5)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='sweet-alert showSweetAlert visible']//button[@class='cancel']"))).click()
    time.sleep(1)
    
    print('[FINAL] Скрипт закончил работу, проверьте файл.')
    time.sleep(1)

''' Проверка на наличие элемента в DOM '''
def check_exists_by_xpath(xpath):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True

''' Формируем ссылки на документы и добавляем их в массив doc_list '''
def append_doc(docs):
    for doc in docs:
        doc_id = doc.get_attribute('data-docoid')
        doc_no = doc.get_attribute('data-docno')
        company_voen = doc.get_attribute('data-toorgid')
        company_name = doc.find_element_by_xpath('td[7]').text

        doc_url = 'https://qaime.e-taxes.gov.az/getDocData?docOid={}&docNo={}'.format(
            doc.get_attribute('data-docoid'), doc.get_attribute('data-docno'))

        doc = {}
        doc['doc_id'] = doc_id
        doc['doc_no'] = doc_no
        doc['company_voen'] = company_voen
        doc['company_name'] = company_name
        doc['doc_url'] = doc_url

        doc_list.append(doc)

''' Получем список всех документов на странице и добавляем их в массив '''
def get_elements():
    doc_webelement_list = driver.find_elements_by_xpath("//div[@id='resultArea']//table/tbody/tr")
    time.sleep(2)
    append_doc(doc_webelement_list)

''' Увеличиваем количество отображаемых на странице элементов до 200 '''
def increase_showed_elements():
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[@id='pagingCombo']//select/option[text()='200']"))).click()

''' Проверяем есть ли пагинация и если есть переходим на него '''
def get_next_page():
    if check_exists_by_xpath('//a[@class="btn nextButton"]'):
        #print('Есть пагинация')
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//a[@class="btn nextButton"]'))).click()
        time.sleep(5)
        get_elements()
        get_next_page()
    else:
        #print('Нет пагинации')
        return

def reload_page():
    if not check_exists_by_xpath('//a[@id="logout"]'):
        driver.refresh()
        time.sleep(5)
        print('[ERROR] Reload Page...')
        reload_page()




try:
    print('[START] Перехожу по ссылке: ', LOGIN_URL)
    driver.get(LOGIN_URL)
    driver.minimize_window()
    time.sleep(1)
    driver.refresh()
    time.sleep(1)

    login()

    if check_exists_by_xpath("//a[@id='logout']"):
        print('[INFO] Успешная авторизация.')
    else:
        print('[INFO] Ошибка при авторизации, повторите через 10 минут.')
        exit()

    INCOMING_URL = 'https://qaime.e-taxes.gov.az/getDocList'
    OUTGOING_URL = 'https://qaime.e-taxes.gov.az/getAllDocList'

    print('[+] Введите "1" чтобы получить приходные или "2" чтобы получить расходные:')
    get_doc_url = input()

    if get_doc_url == '1':
        driver.get(INCOMING_URL)
        reload_page()
    else:
        driver.get(OUTGOING_URL)
        reload_page()

    print('[+] Введите начальную дату в фомате деньмесяцгод (пример: 01012021):')
    startDate = input()
    startDate = startDate[4:8] + startDate[2:4] + startDate[0:2] + '000000'

    print('[+] Введите конечную дату в фомате деньмесяцгод (пример: 01012021):')
    endDate = input()
    endDate = endDate[4:8] + endDate[2:4] + endDate[0:2] + '235959'

    driver.get(driver.current_url + '?fromDate='+startDate+'&toDate='+endDate+'&')
    time.sleep(5)
    
    reload_page()

    increase_showed_elements()

    time.sleep(5)

    get_elements()

    time.sleep(1)

    get_next_page()

    time.sleep(1)


    if doc_list:
        print('[INFO] Найдено документов:', len(doc_list))
    else:
        print('[INFO] Документы не найдены')



    ''' Создаем файл и открываем его для записи данных '''

    with open('e-taxes.csv', 'w', newline='', encoding='utf-8') as file:

        writer = csv.writer(file, delimiter=';')
        time.sleep(1)
        writer.writerow([
            'Seriya nömrəsi',
            'Ödəyici adı',
            'VÖEN',
            'Mal kodu',
            'Mal adı',
            'Barkod',
            'Ölçü vahidi',
            'Malın miqdarı',
            'Malın buraxılış qiyməti',
            'Cəmi qiyməti',
            'Aksiz dərəcəsi',
            'Aksiz məbləği',
            'Cəmi məbləğ',
            'ƏDV-yə cəlb edilən məbləğ',
            'ƏDV-yə cəlb edilməyən məbləğ',
            'ƏDV-dən azad olunan',
            'ƏDV-yə 0 dərəcə ilə cəlb edilən məbləğ',
            'Ödənilməli ƏDV',
            'Yol vergisi məbləği',
            'Yekun məbləğ'
        ])
        time.sleep(1)

        # Обходим массив со ссылками
        for doc in doc_list:
            
            try:
              driver.get(doc['doc_url'])
            except Exception as ex:
              print(ex)

            reload_page()

            time.sleep(1)
            
            try:
            
              while not check_exists_by_xpath('//section[@id="areaApp"]//iframe'):
                time.sleep(1)
                reload_page()
                
              iframe = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//section[@id="areaApp"]//iframe')))
              
              time.sleep(1)
              driver.switch_to.frame(iframe)
              time.sleep(1)
              
              product_list = driver.find_elements_by_xpath('//tbody[@class="productTable"]/tr')

              print('[INFO] Документ: ', doc['doc_no'],
                    '| Товаров: ', len(product_list), 
                    '| Осталось документов: ', len(doc_list) - doc_list.index(doc) - 1)
              
            except Exception as ex:
              print(ex)

            time.sleep(2)

            #print('Начинаем обход product_list')
            for product in product_list:
                if check_exists_by_xpath('//tbody[@class="productTable"]/tr'):
                    time.sleep(1)
                    td_list = product.find_elements_by_xpath('td')

                    row = []

                    # Добавляем данные о документе
                    row.append(doc['doc_no'])
                    row.append(doc['company_name'])
                    row.append(doc['company_voen'])

                    # Получаем данные о товаре и добавляем их в массив
                    for td in td_list:
                        row.append(td.text)

                    # Записываем данные в файл
                    writer.writerow(row)
                    time.sleep(1)

                else:
                    print('[ERROR] Не смог прочитать данные о товаре...')
            #print('Вышел из цикла product_list')
            


    driver.switch_to.default_content()

    time.sleep(2)

    logout()

except Exception as ex:
    print(ex)
    print('[ERROR] Ошибка на сайте, запустите скрипт позже.')
finally:
    driver.close()
    driver.quit()




