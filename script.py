from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import requests
import re
import json

#siglas_UF = {'AC','AL','AM','AP','BA','CE','DF','ES','GO','MA','MG','MS','MT','PA','PB','PE','PI','PR','RJ','RN','RO','RR','RS','SC','SE','SP','TO'}
siglas_UF = {'AC'}
pagina_principal= 'https://venda-imoveis.caixa.gov.br/listaweb/Lista_imoveis_UF.htm'
pagina_consulta_imovel = 'https://venda-imoveis.caixa.gov.br/sistema/detalhe-imovel.asp?hdnOrigem=index&hdnimovel=n_imovel'

for uf in siglas_UF:
    try:
        _request_principal = requests.get(pagina_principal.replace('UF',uf))

    except requests.exceptions.ConnectionError as e:
        print('Erro conexao, UF:{_uf}'.format(_uf=uf))

    except requests.exceptions.ConnectTimeout as e:
        print('Erro de TimeOut')

    else:

        html_tabela = BeautifulSoup(_request_principal.text,'html.parser').find('table')
        df= pd.read_html(str(html_tabela),header=0)[0]
        df['link'] = [link.get('href') for link in html_tabela.find_all('a',string = re.compile('Detalhes'))]
        df['N Imovel'] = [''.join(re.findall('[\d]+',link)) for link in df['link']]
        df['Situacao'] = ""
        df['tpImovel'] = ""
        df['endereco'] = ""
        df['cep'] = ""

        matiz_dados =  df.to_numpy()

        for i in range(len(matiz_dados)):

            imovel=matiz_dados[i][12]

            try:
                _request_secundario = requests.get(pagina_consulta_imovel.replace('n_imovel',imovel))

            except requests.exceptions.ConnectionError as e:
                print('Erro conexao, Imovel:{_imovel}'.format(_imovel=imovel))

            except requests.exceptions.ConnectTimeout as e:
                print('Erro de TimeOut')
            
            else:
                
                html_form = BeautifulSoup(_request_secundario.text,'html.parser').find('form')
                
                if len(html_form.find_all('p'))==1:
                    continue

                _situacao = html_form.find_all('span')[1].text
                _tipodeimovel = html_form.find_all('span')[0].text
                _endereco = html_form.find_all('p')[3].text

                matiz_dados[i][13] = _situacao.replace('Situação:','')
                matiz_dados[i][14] = _tipodeimovel.replace('Tipo de imóvel:','')
                matiz_dados[i][15] = _endereco.replace('Endereço:','')
                matiz_dados[i][16] = ''.join(re.findall(r'\d{5}-\d{3}',_endereco))
                
                _request_secundario.close

        _request_principal.close
        df = pd.DataFrame(matiz_dados)
        df.to_csv('arquivo.csv',encoding='utf-8',mode='a',index=False)
