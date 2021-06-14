# Imports
from sys import exec_prefix
from pyvirtualdisplay import Display
import time
import json
import requests
import csv
import os
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options as ChromeOptions

# Variables globales
path_driver = ''
driver = None
folder_local = ''
folder_save = ''
vars = None
urls_scan = set()
results_scan = []

# Función que carga las variables
def loadVars():
    global path_driver
    global folder_local
    global vars

    json_path = 'vars/vars_test.json'
    with open(json_path) as json_file:
        vars = json.load(json_file)
    
    path_driver = vars['path_driver']

# Función que inicial el driver para navegar en chrome
def initDriver():
    global driver
    # Preparación del driver de chrome
    options = webdriver.ChromeOptions()
    options.add_argument("--user-agent=something")
    options.add_argument('--enable-extensions')
    options.add_argument('--start-maximized')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(path_driver, chrome_options = options)

def getURLS(name, url):
    driver.get(url)
    body = driver.execute_script("return document.body")
    source = body.get_attribute('innerHTML')
    soup = BeautifulSoup(source, "html.parser")
    links = soup.find_all(href=True)
    for link in links:
        if link.get('href') and link.get('href')[0:4]=='http':
            url_aux = (name, link['href'])
            urls_scan.add(url_aux)

def scanURL(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
    }
    r = requests.get(url[1], headers = headers)
    report = str(r.status_code)
    result = (url[0], url[1], report)
    results_scan.append(result)

def saveCsv():
    with open('results.csv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter = ';')
        writer.writerows(results_scan)

# Control principal del script
def main():
    # Cargamos variables
    loadVars()
    # Creamos un display virtual
    display = Display(visible=0, size=(1920, 1080))
    display.start()

    # Inicializamos el driver de chrome
    initDriver()

    # Iteramos en las urls para obtener los enlaces
    for name, url in vars['urls_test'].items():
        time.sleep(2)
        getURLS(name, url)

    print(urls_scan)

    for url in urls_scan:
        time.sleep(1)
        scanURL(url)

    saveCsv()

    print(results_scan)


if __name__ == "__main__":
    main()