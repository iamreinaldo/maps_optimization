import utils

if __name__ == '__main__':

    enderecos = utils.pega_enderecos()
    coordenadas_lista = ["Rua Melchior Dias, 9 - Jacobina, BA - 44700000"]
    for endereco in enderecos:
        coordenadas = utils.transforma_endereco_em_coordenada(endereco)
        coordenadas_lista.append(coordenadas)
    
    distancia_pares = utils.gera_pares_distancia(coordenadas_lista)
    solucao = utils.gera_otimizacao(coordenadas_lista, distancia_pares)
    utils.mostra_rota_otimizada(coordenadas_lista, solucao)

    print("A aplicação está rodando. Pressione Ctrl+C para sair...")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Aplicação encerrada.")