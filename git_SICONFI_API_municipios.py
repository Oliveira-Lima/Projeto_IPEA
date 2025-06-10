import requests
import pandas as pd
import time

# Caminho do CSV com os municípios
csv_path = r"C:\Users\PC Gamer\Desktop\Ipea Web scrapping\municipios.csv"

# Leitura do CSV
df = pd.read_csv(csv_path)

# Parâmetros fixos
anos = [2024, 2025]
meses = list(range(1, 14))
url = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/msc_orcamentaria"

# Loop sobre todos os municípios
for _, row in df.iterrows():
    cod_ibge = row['cod_ibge']
    
    for ano in anos:
        for mes in meses:
            params = {
                "id_ente": cod_ibge,
                "an_exercicio": ano,
                "me_referencia": mes,
                "co_tipo_matriz": "MSCC",
                "classe_conta": 6,
                "id_tv": "period_change"
            }

            print(f"🔍 Buscando: cod_ibge={cod_ibge}, ano={ano}, mes={mes}")
            try:
                response = requests.get(url, params=params)

                if response.status_code == 200:
                    data = response.json()
                    registros = data.get("items", [])
                    for i, item in enumerate(registros[:5]):
                        print(f"Registro {i+1}:")
                        for k, v in item.items():
                            print(f"  {k}: {v}")
                        print("-" * 40)
                else:
                    print(f"⚠️ Erro {response.status_code} para cod_ibge {cod_ibge}, ano {ano}, mes {mes}")
            except Exception as e:
                print(f"❌ Exceção: {e}")

            time.sleep(1)  # Respeita limite da API
