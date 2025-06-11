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

# Configuração dos arquivos de entrada/saída
csv_entrada = r'C:\Users\mathe\OneDrive\Ambiente de Trabalho\Ipea Web scrapping\municipios.csv'
csv_saida = r'C:\Users\mathe\OneDrive\Ambiente de Trabalho\Ipea Web scrapping\Mortalidade_Infantil\Mortalidade_2022.csv'

# Carregar dados de entrada e filtrar por UF
df_municipios = pd.read_csv(csv_entrada)
uf_filtradas = ['DF', 'MS', 'MT', 'GO']
df_municipios_filtrado = df_municipios[df_municipios['uf'].isin(uf_filtradas)]
municipios = df_municipios_filtrado['ente'].dropna().unique()

# Configuração do Selenium (modo headless)
options = Options()
options.add_argument("--headless")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 10)

resultados = []

for nome_original in municipios:
    nome_formatado = unidecode(nome_original).lower().replace(' ', '-').replace("'", "")
    estados = ['go', 'mt', 'ms', 'df']
    mortalidade_infantil = None

    for estado in estados:
        url = f'https://cidades.ibge.gov.br/brasil/{estado}/{nome_formatado}/panorama'
        driver.get(url)

        try:
            # Aguardar e extrair o valor da mortalidade infantil
            valor_element = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class, 'indicador__valor') and contains(., 'óbitos por mil nascidos vivos')]")
            ))
            texto = valor_element.text
            match = re.search(r'(\d+,\d+)\s+óbitos por mil nascidos vivos', texto)
            
            if match:
                mortalidade_infantil = match.group(1).replace(',', '.')  # Convertendo para float
                print(f"{nome_original} ({estado.upper()}): {mortalidade_infantil}")
                break

        except Exception as e:
            continue  # Tentar próximo estado se falhar

    if mortalidade_infantil is None:
        print(f"Não foi possível obter dados de {nome_original}")
        mortalidade_infantil = 'N/D'

    resultados.append({
        'Cidade': nome_original,
        'Taxa de Mortalidade Infantil (2022)': mortalidade_infantil
    })

    time.sleep(0.5)  # Evitar bloqueio

driver.quit()

# Salvar resultados em CSV
df_resultado = pd.DataFrame(resultados)
os.makedirs(os.path.dirname(csv_saida), exist_ok=True)
df_resultado.to_csv(csv_saida, index=False, encoding='utf-8-sig')

print(f"Dados salvos em: {csv_saida}")
