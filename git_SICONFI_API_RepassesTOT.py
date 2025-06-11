import requests
import pandas as pd
from datetime import datetime
import os
import time

def extrair_dados_municipios():
    dir_base = r'C:\Users\PC Gamer\Desktop\Ipea Web scrapping'
    arquivo_municipios = os.path.join(dir_base, 'taxa_de_mortalidade_municípios_centro_oeste.csv')
    dir_saida = os.path.join(dir_base, 'Dados_Receitas_Completo')

    an_referencia = 2022
    co_tipo_matriz = 'MSCC'
    classe_conta = 6
    id_tv = 'ending_balance'
    base_url = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt//msc_orcamentaria"

    try:
        os.makedirs(dir_saida, exist_ok=True)
        print(f" Diretório de saída verificado: {dir_saida}")
    except Exception as e:
        print(f" Erro ao acessar/criar diretório: {e}")
        return False

    try:
        municipios_df = pd.read_csv(arquivo_municipios, sep=',')
        codigos_ibge = municipios_df.iloc[:, 0].astype(str).str.strip()
        print(f" {len(codigos_ibge)} municípios carregados do arquivo")
    except Exception as e:
        print(f" Erro ao ler arquivo de municípios: {e}")
        return False

    for i, cod_ibge in enumerate(codigos_ibge, 1):
        print(f" Processando município {i}/{len(codigos_ibge)} - Código IBGE: {cod_ibge}")
        
        dados_consolidados = []

        for me_referencia in range(1, 12):
            params = {
                'id_ente': cod_ibge,
                'an_referencia': an_referencia,
                'me_referencia': me_referencia,
                'co_tipo_matriz': co_tipo_matriz,
                'classe_conta': classe_conta,
                'id_tv': id_tv
            }

            try:
                time.sleep(1)
                response = requests.get(base_url, params=params, timeout=45)
                response.raise_for_status()
                dados = response.json()

                if 'items' in dados and dados['items']:
                    df_mes = pd.DataFrame(dados['items'])

                    
                    df_mes = df_mes[
                        df_mes['natureza_receita'].notna() & 
                        df_mes['natureza_receita'].astype(str).str.startswith('1711') #Agrega as receitas provenientes de recursos financeiros recebidos da União ou de suas entidades
                    ]

                    if not df_mes.empty:
                        df_mes['me_referencia'] = me_referencia
                        df_mes['cod_ibge'] = cod_ibge
                        dados_consolidados.append(df_mes)
                        print(f" {me_referencia:02d}/{an_referencia}", end=' ', flush=True)
                    else:
                        print(f" {me_referencia:02d}/{an_referencia} (sem dados válidos)", end=' ', flush=True)
                else:
                    print(f" {me_referencia:02d}/{an_referencia} (vazio)", end=' ', flush=True)

            except requests.exceptions.RequestException as e:
                print(f" {me_referencia:02d}/{an_referencia} (erro: {e})", end=' ', flush=True)
                continue
            except KeyboardInterrupt:
                print("\n\n Processamento interrompido pelo usuário")
                return False

        if dados_consolidados:
            df_final = pd.concat(dados_consolidados, ignore_index=True)
            nome_arquivo = f"dados_tesouro_{cod_ibge}_{an_referencia}_Receita.csv"
            caminho_completo = os.path.join(dir_saida, nome_arquivo)

            try:
                df_final.to_csv(caminho_completo, index=False, encoding='utf-8-sig', sep=';')
                print(f"\n Arquivo salvo: {nome_arquivo}")
                print(f"   Registros: {len(df_final)} | Caminho: {caminho_completo}")
            except Exception as e:
                print(f"\n Erro ao salvar arquivo: {e}")
        else:
            print("\n Nenhum dado válido obtido para este município")

    print("\nProcessamento concluído para todos os municípios")
    return True

if __name__ == "__main__":
    print("=== Extração de Dados do Tesouro Nacional para Múltiplos Municípios ===")
    print(f"Data/hora de início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    try:
        sucesso = extrair_dados_municipios()
        if sucesso:
            print("\nRelatório final:")
            print("- Todos os municípios foram processados")
            print("- Arquivos salvos em: Dados_Receitas_Completo")
        else:
            print("\nO processamento foi interrompido devido a erros.")
    except Exception as e:
        print(f"\nErro inesperado: {e}")
    finally:
        print(f"\nData/hora de término: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
