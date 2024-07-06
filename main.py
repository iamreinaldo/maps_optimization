from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from time import sleep


service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
driver.implicitly_wait(2)

driver.get('https://www.google.com/maps')

def esta_na_aba_de_rotas():
    xpath = '//button[@aria-label="Fechar rotas"]'
    botao_rotas = driver.find_elements(By.XPATH, xpath)
    return len(botao_rotas) > 0


def adciona_destino(endereco, num_caixa=1):
    if not esta_na_aba_de_rotas():
        barra_vazia = driver.find_element(By.ID, 'searchboxinput')
        barra_vazia.clear()
        barra_vazia.send_keys(endereco)
        barra_vazia.send_keys(Keys.RETURN)
    else:
        xpath = '//div[contains(@id, "directions-searchbox")]//input'
        caixas = driver.find_elements(By.XPATH, xpath)
        caixas = [c for c in caixas if c.is_displayed()]
        if len(caixas) >= num_caixa:
            caixa_endereco = caixas[num_caixa-1]
            caixa_endereco.send_keys(Keys.CONTROL + 'a')
            caixa_endereco.send_keys(Keys.DELETE)
            caixa_endereco.send_keys(endereco)
            caixa_endereco.send_keys(Keys.RETURN)
        else:
            print(f'não coonseguimos adcionar o endereço {len(caixas)} | {num_caixa}')

def abre_rotas():
    xpath = '//button[@data-value="Rotas"]'
    wait = WebDriverWait(driver, timeout=5)
    botao_rotas = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    botao_rotas.click()

    xpath = '//button[@aria-label="Fechar rotas"]'
    wait = WebDriverWait(driver, timeout=5)
    botao_rotas = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))

def adciona_caixa_destino():
    xpath = '//span[text()="Adicionar destino"]'
    wait = WebDriverWait(driver, timeout=3)
    wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
    botao_adciona_destino = driver.find_element(By.XPATH, xpath)
    botao_adciona_destino.click()



if __name__ == '__main__':

    enderecos = [
                'Rua Melchior Dias, 9 - Centro, Jacobina - BA, 44700-000', #Newnet
                'Rua Florisvaldo Barberino, 347 - Félix Tomaz, Jacobina - BA, 44700-000', #Paulo
                'SESC - Unidade Jacobina, R. Antônio A Mesquita, 243 - Vila Feliz, Jacobina - BA, 44700-000' #Sesc
                ]
    adciona_destino(enderecos[0], 1)
    abre_rotas()

    adciona_destino(enderecos[0], 1)
    adciona_destino(enderecos[1], 2)

    adciona_caixa_destino()
    adciona_destino(enderecos[2], 3)

    sleep(600)



