# Imports
from sys import exec_prefix
from pyvirtualdisplay import Display
import time
import json
import os
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options as ChromeOptions

# Variables globales
path_driver = ''
amazon_url = ''
amazon_user = ''
amazon_pass = ''
driver = None
folder_local = ''
folder_save = ''
vars = None
data = []

# Función que carga las variables
def loadVars():
    global path_driver
    global amazon_url
    global amazon_user
    global amazon_pass
    global folder_local
    global folder_save
    global vars

    json_path = 'vars/vars.json'
    with open(json_path) as json_file:
        vars = json.load(json_file)
    
    path_driver = vars['path_driver']
    amazon_url = vars['amazon_url']
    amazon_user = vars['amazon_user']
    amazon_pass = vars['amazon_pass']
    folder_save = vars['folder_save']

# Función que inicial el driver para navegar en chrome
def initDriver():
    global driver
    # Preparación del driver de chrome
    options = webdriver.ChromeOptions()
    options.add_argument('--enable-extensions')
    options.add_argument('--start-maximized')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(path_driver, chrome_options = options)

# Función para hacer login en amazon
def login():
    # Abre la pagina de amazon
    driver.get(amazon_url)
    time.sleep(2)

    # Hacemos click para hacer login
    login_select = driver.find_element_by_id('nav-link-accountList')
    login_select.click()
    time.sleep(2)

    # Se introduce el usaurio y continuamos
    input_user = driver.find_element_by_id('ap_email')
    input_user.send_keys(amazon_user)
    time.sleep(2)
    continue_btn = driver.find_element_by_id('continue')
    continue_btn.click()

    # Introduccimos la contraseña e iniciamos sesion
    input_pass = driver.find_element_by_id('ap_password')
    input_pass.send_keys(amazon_pass)
    time.sleep(2)
    log_in_btn = driver.find_element_by_id('signInSubmit')
    log_in_btn.click()

# Funcion que captura los datos de los 8 productos de la url indicada y los guarda en un JSON
def captureUrl(url, file_name):
    # Variable para guardar la url de los 8 productos a escanear
    urls = []
    time.sleep(2)

    # Abro la url
    driver.get(url)
    time.sleep(2)

    # Recojo la web y lo convierto en un objeto BeautifulSoup
    body = driver.execute_script("return document.body")
    source = body.get_attribute('innerHTML')
    soup = BeautifulSoup(source, "html.parser")

    # Busco los productos y de los 8 primeros cojo el link para obtener la información
    products = soup.find_all("li", {"class": "zg-item-immersion"})
    for i in  range(8):
        link = products[i].find("a", {"class": "a-link-normal"}, href=True )
        urls.append('https://www.amazon.es' + link['href'])
    
    # Accedo a las url de los productos, escaneo los datos y los guardo en el array de datos
    for url in urls:
        scan(url)
    saveFile(file_name)

# Recoge los datos de los productos de sus urls
def scan(url):
    driver.get(url)
    time.sleep(2)
    # Recojo la web y lo convierto en un objeto BeautifulSoup
    body = driver.execute_script("return document.body")
    source = body.get_attribute('innerHTML')
    soup = BeautifulSoup(source, "html.parser")
    product = {}

    # Captura el titulo
    try:
        title = soup.find("span", {"id": "productTitle"}).getText().strip().replace('"', '\"').replace(u'\xa0', ' ')
    except:
        title = "Nombre no disponible"

    # Captura la descripción
    try:
        descriptions = soup.find("div", {"id": "feature-bullets"})
        children = descriptions.findChildren("span", {"class": "a-list-item"})
        description = ''
        for i in range(1, len(children)):
            if i != 0:
                description = (description + children[i].getText().strip()).replace(u'\xa0', ' ')
    except:
        description = 'Descripción no disponible'
    # Si la descripción llega vacia se modifica
    if description == '':
        description = 'Descripción no disponible'

    # Captura el precio, sino tiene precio normal, capturo la oferta
    try:
        price = soup.find("span", {"class": "a-color-price"}).getText().strip().replace(u'\xa0', ' ')
    except:
        price = 0

    # Captura la imagen
    try:
        img = soup.find("img", {"id": "landingImage"})
    except:
        img = 'asset/images/dummy.png'

    # Captura la puntuacion
    try:
        rating_aux = soup.find("i", {"class": "averageStarRating"}).getText().strip().split(' ')
        rating = rating_aux[0].replace(',', '.')
    except:
        rating = 0
    
    # Captura el link de afiliado
    link_btn = driver.find_element_by_xpath('//a[@title="Texto"]')
    link_btn.click()
    time.sleep(2)
    link = driver.find_element_by_id('amzn-ss-text-shortlink-textarea').get_attribute('value')
    
    # Se crea una entrada con los datos en el array de datos
    product['title'] = title
    product['description'] = description
    product['price'] = price
    product['img'] = img['src']
    product['rating'] = rating
    product['link'] = link
    data.append(product)
    print(product)

# Guarda el archivo
def saveFile(file_name):
    global folder_save
    with open(os.path.join(folder_save, file_name), 'w+') as file:
        json.dump(data, file)

# Control principal del script
def main():
    global data
    # Cargamos variables
    loadVars()
    # Creamos un display virtual
    #display = Display(visible=0, size=(1920, 1080))
    #display.start()
    # Inicializamos el driver de chrome
    initDriver()
    # Accedemos a la web
    login()
    # Dormimos el proceso por si salta la seguridad de amazon 
    time.sleep(10)
    # Escameamos cada una de las url que llegan en las variables y creamos un json con los datos
    for file_name, url in vars['urlsTop'].items():
        data = []
        captureUrl(url, file_name)

if __name__ == "__main__":
    main()