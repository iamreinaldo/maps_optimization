import utils
from time import sleep
import pandas as pd

if __name__ == '__main__':

    enderecos = []
    enderecos = utils.pega_enderecos()
    
    distancia_pares = utils.gera_pares_distancia(enderecos)
    solucao = utils.gera_otimizacao(enderecos, distancia_pares)
    utils.mostra_rota_otimizada(enderecos, solucao)

    sleep(600)



