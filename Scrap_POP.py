from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from unidecode import unidecode
import pandas as pd
import os
import re
import time

csv_entrada = r'C:\Users\mathe\OneDrive\Ambiente de Trabalho\Ipea Web scrapping\municipios.csv'
csv_saida = r'C:\Users\mathe\OneDrive\Ambiente de Trabalho\Ipea Web scrapping\População\Pop 2022.csv'

df_municipios = pd.read_csv(csv_entrada)

uf_filtradas = ['DF', 'MS', 'MT', 'GO']
df_municipios_filtrado = df_municipios[df_municipios['uf'].isin(uf_filtradas)]

municipios = df_municipios_filtrado['ente'].dropna().unique()

options = Options()
options.add_argument("--headless")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 10)

resultados = []

for nome_original in municipios:
    nome_formatado = unidecode(nome_original).lower().replace(' ', '-').replace("'", "")
    url = f'https://cidades.ibge.gov.br/brasil/go/{nome_formatado}/panorama' 
    estados = ['go', 'mt', 'ms', 'df']

    populacao = None
    for estado in estados:
        url_estado = f'https://cidades.ibge.gov.br/brasil/{estado}/{nome_formatado}/panorama'
        driver.get(url_estado)

        try:
            valor_element = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class,'indicador__valor') and contains(., 'pessoas')]")
            ))
            texto = valor_element.text
            match = re.search(r'(\d[\d\.]*)\s+pessoas', texto)
            if match:
                pop_str = match.group(1).replace('.', '')
                populacao = int(pop_str)
                print(f"{nome_original} ({estado.upper()}): {populacao}")
                break
        except:
            continue  

    if populacao is None:
        print(f"Não foi possível obter dados de {nome_original}")
        populacao = 'N/D'

    resultados.append({
        'Cidade': nome_original,
        'População 2022': populacao
    })

    time.sleep(0.5)  

driver.quit()

df_resultado = pd.DataFrame(resultados)
os.makedirs(os.path.dirname(csv_saida), exist_ok=True)
df_resultado.to_csv(csv_saida, index=False, encoding='utf-8-sig')

print(f"Salvo em: {csv_saida}")
