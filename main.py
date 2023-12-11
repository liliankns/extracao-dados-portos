import requests
import time
from tabulate import tabulate
import pandas as pd
from bs4 import BeautifulSoup

# Método utilizado para extrair as tabelas presentes nos sites
def extrair_tabelas(targetUrl):
    url = targetUrl
    res = requests.get(url)
    html_page = res.text
    soup = BeautifulSoup(html_page, 'html.parser')
    soup.prettify()
    tabelas = soup.find_all('table')
    return tabelas

def extrair_dados_paranagua():
    tabelas = extrair_tabelas('https://www.appaweb.appa.pr.gov.br/appaweb/pesquisa.aspx?WCI=relLineUpRetroativo')

    tabela_esperados = None

    # Verificação para extrair somente a tabela de Esperados
    for tabela in tabelas:
        if 'ESPERADOS' in str(tabela):
            tabela_esperados = tabela
            break

    dicionario = {}
    tbody = tabela_esperados.find('tbody')
    linhas = tbody.find_all('tr')

    for linha in linhas:
        colunas = linha.find_all('td')

        # Verificação para os casos em que dentro de uma linha existe mais de uma mercadoria
        if len(colunas) != 17:
            sentido = colunas[0].text.strip()
            mercadoria = colunas[3].text.strip()
            data = colunas[4].text.strip()
            volume = float(colunas[6].text.strip().split(' ')[0].replace('.', '').replace(',', '.'))
        else:
            sentido = colunas[8].text.strip()
            mercadoria = colunas[11].text.strip()
            data = colunas[12].text.strip().split(' ')[0]
            volume = float(colunas[14].text.strip().split(' ')[0].replace('.', '').replace(',', '.'))

        # Indicando a existência de 4 atributos para a chave
        chave = (mercadoria, sentido, data, 'Paranagua')

        # Caso uma mesma chave já exista, o volume será somado ao volume atual da chave
        if chave in dicionario:
            dicionario[chave] += volume
        else:
            dicionario[chave] = volume

    # Criação da tabela correspondente aos dados de Paranaguá
    table_data = [[key[0], key[1], key[2], key[3], value] for key, value in dicionario.items()]

    return pd.DataFrame(table_data)

def extrair_dados_santos():
    tabelas = extrair_tabelas('https://www.portodesantos.com.br/informacoes-operacionais/operacoes-portuarias/navegacao-e-movimento-de-navios/navios-esperados-carga/')

    dicionario = {}

    for tabela in tabelas:
        tbody = tabela.find('tbody')
        linhas = tbody.find_all('tr')

        for linha in linhas:
            colunas = linha.find_all('td')

            data = colunas[4].text.strip().split(' ')[0]
            sentido = colunas[7].text.strip()
            mercadoria = colunas[8].text.strip()
            volume = sum([float(valor.strip()) for valor in colunas[9].stripped_strings])

            # Padronizando os termos de importação e exportação
            if sentido == 'EMB':
                sentido = 'Exp'
            elif sentido == 'DESC':
                sentido = 'Imp'
            else:
                sentido = 'Imp/Exp'

            # Indicando a existência de 4 atributos para a chave
            chave = (mercadoria, sentido, data, 'Santos')

            # Caso uma mesma chave já exista, o volume será somado ao volume atual da chave
            if chave in dicionario:
                dicionario[chave] += volume
            else:
                dicionario[chave] = volume

    # Criação da tabela correspondente aos dados de Santos
    tabela_santos = [[key[0], key[1], key[2], key[3], value] for key, value in dicionario.items()]

    return pd.DataFrame(tabela_santos)

def exibir_dados():
    tabela_santos = extrair_dados_santos()
    tabela_paranagua = extrair_dados_paranagua()
    tabelas_combinadas = pd.concat([tabela_santos, tabela_paranagua], ignore_index=True)


    headers = ["Mercadoria", "Sentido", "Data", "Porto", "Volume Total"]
    print(tabulate(tabelas_combinadas, headers=headers, tablefmt="pretty"))

while True:
    exibir_dados()

    # Fazendo uma nova busca dos dados a cada 20 segundos
    time.sleep(20)