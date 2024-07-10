from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from time import sleep
import pulp
import itertools
import pandas as pd
import googlemaps
from dotenv import load_dotenv
import os



load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')

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
    wait = WebDriverWait(driver, timeout=8)
    botao_rotas = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    botao_rotas.click()

    xpath = '//button[@aria-label="Fechar rotas"]'
    wait = WebDriverWait(driver, timeout=8)
    botao_rotas = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))

def adciona_caixa_destino():
    xpath = '//span[text()="Adicionar destino"]'
    wait = WebDriverWait(driver, timeout=8)
    wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
    botao_adciona_destino = driver.find_element(By.XPATH, xpath)
    botao_adciona_destino.click()

def seleciona_tipo_conducao(tipo_conducao="Carro"):
    xpath = f'//img[@aria-label="{tipo_conducao}"]'
    wait = WebDriverWait(driver, timeout=8)
    botao_conducao = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    botao_conducao.click()

def retorna_tempo_total():
    xpath = '//div[@id="section-directions-trip-0"]//div[contains(text(),"min")]'
    wait = WebDriverWait(driver, timeout=10)
    elemento_tempo = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    return float(elemento_tempo.text.replace(' min', ''))

def retorna_distancia_total():
    xpath = '//div[@id="section-directions-trip-0"]//div[contains(text(),"km")]'
    wait = WebDriverWait(driver, timeout=8)
    elemento_tempo = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    return float(elemento_tempo.text.replace(' km', '').replace(',', '.'))


def gera_pares_distancia(enderecos):
    distancia_pares = {}
    driver.get('https://www.google.com/maps')
    adciona_destino(enderecos[0], 1)
    abre_rotas()
    seleciona_tipo_conducao(tipo_conducao='Carro')

    for i, end1 in enumerate(enderecos):
        adciona_destino(end1, 1)
        for j, end2 in enumerate(enderecos):
            if i != j:
                adciona_destino(end2, 2)
                tempo_par = retorna_tempo_total()
                distancia_pares[f'{i}_{j}'] = tempo_par
    
    return distancia_pares

def gera_otimizacao(enderecos, distancia_pares):

    def distancia(end1, end2):
        return distancia_pares[f'{end1}_{end2}']
    
    prob = pulp.LpProblem('TSP', pulp.LpMinimize)

    x = pulp.LpVariable.dicts('x', [(i, j) for i in range(len(enderecos)) for j in range(len(enderecos)) if i != j], cat="Binary")

    prob += pulp.lpSum([distancia(i, j) * x[(i, j)]for i in range(len(enderecos)) for j in range(len(enderecos)) if i != j])

    for i in range(len(enderecos)):
        prob += pulp.lpSum([x[(i, j)] for j in range(len(enderecos)) if i != j]) == 1
        prob += pulp.lpSum([x[(j, i)] for j in range(len(enderecos)) if i != j]) == 1

    for k in range(len(enderecos)):
        for S in range(2, len(enderecos)):
            for subset in itertools.combinations([i for i in range(len(enderecos)) if i != k], S):
                prob += pulp.lpSum([x[(i, j)] for i in subset for j in subset if i != j]) <= len(subset) - 1

    prob.solve(pulp.PULP_CBC_CMD())
    
    solucao = []
    cidade_inicial = 0
    proxima_cidade = cidade_inicial
    while True:
        for j in range(len(enderecos)):
            if j != proxima_cidade and x[(proxima_cidade, j)].value()== 1:
                solucao.append((proxima_cidade, j))
                proxima_cidade = j
                break
        if proxima_cidade == cidade_inicial:
            break

    print('Rota: ' )
    for i in range(len(solucao)):
        print(solucao[i][0], '-->>>', solucao[i][1]) 

    return solucao


def mostra_rota_otimizada(enderecos, solucao):
    driver.get('https://www.google.com/maps')
    adciona_destino(enderecos[0], 1)
    abre_rotas()

    for i in range(len(solucao)):
        adciona_destino(enderecos[solucao[i][0]], i+1)
        adciona_caixa_destino()
    
    adciona_destino(enderecos[0], len(enderecos) + 1)


def pega_enderecos():
    df = pd.read_csv("data.csv", sep=';')
    df.drop([0, df.index[-1]], inplace=True)
    df['Número'] = df['Número'].astype(str) 


    enderecos = []

    for index, row in df.iterrows():
        endereco = f"{row['Logradouro']}, {row['Número']} - {row['Bairro']} - {row['Cidade']} - BA, 44700-000"
        enderecos.append(endereco)

    return enderecos


def transforma_endereco_em_coordenada(endereco):
    gmaps = googlemaps.Client(key=api_key)
    geocode_result = gmaps.geocode(endereco)
    if geocode_result:
        location = geocode_result[0]['geometry']['location']
        return f"{location['lat']}, {location['lng']}"
    else:
        return None

