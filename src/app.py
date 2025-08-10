import pandas as pd
import streamlit as st

# TITULO
st.sidebar.title('Teste Mobi2Buy')

arquivo_ofertas = st.sidebar.file_uploader('Envie o arquivo de ofertas (em csv)', type = 'csv')
arquivo_tratativas = st.sidebar.file_uploader('Envie o arquivo de tratativas (em csv)', type = 'csv')

if arquivo_ofertas and arquivo_tratativas:
    if st.sidebar.button('Criar relatório'):
        with st.spinner('Criando o relatório. Por favor, aguarde.'):
            # CRIANDO UM DATAFRAME PANDAS PARA CADA BASE
            df_base_teste = pd.read_csv('C:/Users/Antonio Mailson/Desktop/projetos/m2bteste/data/base_teste.csv', sep = '|')
            df_tratativas_teste = pd.read_csv('C:/Users/Antonio Mailson/Desktop/projetos/m2bteste/data/tratativas_teste.csv', sep = '|')

            # FILTRANDO A BASE PARA TRAZER SOMENTE OS CONTATOS EM QUE O TELEFONE TENHA 11 DÍGITOS
            filtro_11_digitos = df_base_teste['NUM_TELEFONE'].apply(lambda numero: len(str(numero)) == 11)
            df_base_teste = df_base_teste[filtro_11_digitos]

            # FILTRANDO A BASE PARA TRAZER SOMENTE OS CONTATOS EM QUE O DDD SEJA VÁLIDO
            lista_ddds_int = [11, 12, 13, 14, 15, 16, 17, 18, 19,
                            21, 22, 24, 27, 28,
                            31, 32, 33, 34, 35, 37, 38,
                            41, 42, 43, 44, 45, 46, 47, 48, 49,
                            51, 53, 54, 55,
                            61, 62, 63, 64, 65, 66, 67, 68, 69,
                            71, 73, 74, 75, 77, 79,
                            81, 82, 83, 84, 85, 86, 87, 88, 89,
                            91, 92, 93, 94, 95, 96, 97, 98, 99]
            lista_ddds_str = [str(ddd) for ddd in lista_ddds_int]
            filtro_ddd = df_base_teste['NUM_TELEFONE'].apply(lambda numero: str(numero)[:2] in lista_ddds_str)
            df_base_teste = df_base_teste[filtro_ddd]

            # FILTRANDO A BASE PARA TRAZER SOMENTE OS CONTATOS EM QUE TELEFONE TENHA O ALGARISMO 9 NA TERCEIRA POSIÇÃO DA ESQUERDA PRA DIREITA
            filtro_algarismo_9 = df_base_teste['NUM_TELEFONE'].apply(lambda numero: str(numero)[2] == '9')
            df_base_teste = df_base_teste[filtro_algarismo_9]

            # RETIRANDO OS CASOS QUE JÁ CONVERTERAM
            df_merged = df_base_teste.merge(df_tratativas_teste, left_on = 'NUM_TELEFONE', right_on = 'MSISDN', how = 'left')
            df_base_teste = df_merged[df_merged['MSISDN'].isna()][df_base_teste.columns]

            # TRANSFORMANDO '20+20GB' EM '20GB+20GB' NA COLUNA DE BONUS_DESTINO
            df_base_teste['BONUS_DESTINO'] = df_base_teste['BONUS_DESTINO'].apply(lambda bonus: '20GB+20GB' if bonus == '20+20GB' else bonus)

            # TRATANDO TELEFONES DUPLICADOS
            def retirar_duplicados(dataframe, coluna_chave, lista_criterios, lista_ordens, valor_excecao = None):
                """
                REMOVE DUPLICADOS DE UMA COLUNA-CHAVE MANTENDO O REGISTRO COM MAIOR PRIORIDADE
                DE ACORDO COM N CRITÉRIOS.
                
                PARÂMETROS:
                - dataframe: DATAFRAME
                - coluna_chave: COLUNA QUE DEVE TER VALORES ÚNICOS (EX: TELEFONE)
                - lista_criterios: LISTA COM OS NOMES DAS COLUNAS DE CRITÉRIO EM ORDEM DE PRIORIDADE
                - lista_ordens: LISTA COM DICIONÁRIOS DE PRIORIDADE CORRESPONDENTES AOS CRITÉRIOS
                - valor_excecao: VALOR ESPECIAL NO PRIMEIRO CRITÉRIO PARA INVERTER PRIORIDADE COM O SEGUNDO CRITÉRIO
                """
                
                # CRIANDO CÓPIA DO DATAFRAME
                df = dataframe.copy()

                # CRIAR COLUNAS DE RANKING NUMÉRICO PARA CADA CRITÉRIO
                for indice, (coluna, ordem) in enumerate(zip(lista_criterios, lista_ordens)):
                    df[f"rank_{indice}"] = df[coluna].map(ordem)
                
                # CRIAR CHAVE DE ORDENAÇÃO COM EXCEÇÃO DO valor_excecao
                def chave_ordenacao(linha):
                    ranks = [linha[f"rank_{indice}"] for indice in range(len(lista_criterios))]
                    
                    # SE valor_excecao DEFINIDO E ENCONTRADO NO PRIMEIRO CRITÉRIO, INVERTER 1º E 2º
                    if valor_excecao is not None and linha[lista_criterios[0]] == valor_excecao and len(ranks) > 1:
                        ranks[0], ranks[1] = ranks[1], ranks[0]
                    
                    return tuple(ranks)
                
                df["ordem"] = df.apply(chave_ordenacao, axis=1)
                
                # ORDENAR E REMOVER DUPLICADOS
                df = df.sort_values(
                        by = [coluna_chave, "ordem"],
                        ascending = [True, False]
                    ).drop_duplicates(
                        subset = coluna_chave,
                        keep = 'first'
                    ).drop(
                        columns = [f"rank_{indice}" for indice in range(len(lista_criterios))] + ["ordem"]
                    ).reset_index(
                        drop = True
                    )
                
                return df

            # ORDENS DE VARIÁVEIS DE REGRA. A FUNÇÃO SEMPRE ESCOLHERÁ O NÚMERO EM QUE O VALOR DA ORDEM SEJA O MAIOR
            ordem_idade = {
                'NI' : 1,
                'ATE 30' : 2,
                '31 A 45' : 3,
                'ACIMA DE 45' : 4
            }
            ordem_flg_frescor = {
                'M-3' : 1,
                'M-2' : 2,
                'M-1' : 3,
                'Fresh_>3' : 4,
                'Fresh_<3' : 5
            }
            ordem_flg_especial = {
                0 : 1,
                1 : 2
            }
            ordem_plano_indicado = {
                'C' : 1,
                'B' : 2,
                'A' : 3,
                'L' : 4,
                'S' : 5
            }
            ordem_desconto_destino = {
                '00 NFIDEL' : 1,
                '5%' : 2,
                '15%' : 3,
                '17 NFIDEL' : 4,
                '20 NFIDEL' : 5,
                '25 NFIDEL' : 6,
                '28 NFIDEL' : 7,
                '37 NFIDEL' : 8,
                '40 NFIDEL' : 9,
                '41 NFIDEL' : 10,
                '43 NFIDEL' : 11
            }
            ordem_cluster = {
                'REPROVADO' : 1,
                'APROVADO + ADIMPLENTE' : 2
            }

            # RETIRANDO TELEFONES DUPLICADOS UTILIZANDO A REGRA PROPOSTA
            df_base_teste = retirar_duplicados(
                dataframe = df_base_teste,
                coluna_chave = 'NUM_TELEFONE',
                lista_criterios = ['IDADE', 'FLG_FRESCOR', 'FLG_ESPECIAL', 'PLANO_INDICADO', 'DESCONTO_DESTINO', 'CLUSTER'],
                lista_ordens = [ordem_idade, ordem_flg_frescor, ordem_flg_especial, ordem_plano_indicado, ordem_desconto_destino, ordem_cluster],
                valor_excecao = 'NI'
            )

            # FUNÇÃO PARA CRIAR UMA COLUNA DE UF DO NÚMERO DE TELEFONE
            def uf(numero):
                """
                RETORNA A UF RELACIONADA AO DDD DO NÚMERO DE TELEFONE
                
                PARÂMETROS:
                - numero: NÚMERO DE TELEFONE
                """

                # DDD DO NÚMERO DE TELEFONE
                ddd = int(str(numero)[:2])

                if ddd in [11, 12, 13, 14, 15, 16, 17, 18, 19]:
                    return 'SP'
                elif ddd in [21, 22, 24]:
                    return 'RJ'
                elif ddd in [27, 28]:
                    return 'ES'
                elif ddd in [31, 32, 33, 34, 35, 37, 38]:
                    return 'MG'
                elif ddd in [41, 42, 43, 44, 45, 46]:
                    return 'PR'
                elif ddd in [47, 48, 49]:
                    return 'SC'
                elif ddd in [51, 53, 54, 55]:
                    return 'RS'
                elif ddd in [61]:
                    return 'DF'
                elif ddd in [62, 64]:
                    return 'GO'
                elif ddd in [63]:
                    return 'TO'
                elif ddd in [65, 66]:
                    return 'MT'
                elif ddd in [67]:
                    return 'MS'
                elif ddd in[68]:
                    return 'AC'
                elif ddd in [69]:
                    return 'RO'
                elif ddd in [71, 73, 74, 75, 77]:
                    return 'BA'
                elif ddd in [79]:
                    return 'SE'
                elif ddd in [81, 87]:
                    return 'PE'
                elif ddd in [82]:
                    return 'AL'
                elif ddd in [83]:
                    return 'PB'
                elif ddd in [84]:
                    return 'RN'
                elif ddd in [85, 88]:
                    return 'CE'
                elif ddd in [86, 89]:
                    return 'PI'
                elif ddd in [91, 93, 94]:
                    return 'PA'
                elif ddd in [92, 97]:
                    return 'AM'
                elif ddd in [95]:
                    return 'RR'
                elif ddd in [96]:
                    return 'AP'
                elif ddd in [98, 99]:
                    return 'MA'
                else:
                    return 'DDD INVALIDO/DDD OU TELEFONE NAO INFORMADO'

            # CRIANDO COLUNA DE UF
            df_base_teste['UF'] = df_base_teste['NUM_TELEFONE'].map(uf)

            # FUNÇÃO PARA CRIAR UMA COLUNA DE REGIÃO RELACIONADA À UF DO NÚMERO DE TELEFONE
            def regiao(uf):
                """
                RETORNA A REGIÃO RELACIONADA À UF DO NÚMERO DE TELEFONE
                
                PARÂMETROS:
                - uf: UF DO NÚMERO DE TELEFONE
                """

                if uf in ['SP', 'RJ', 'MG', 'ES']:
                    return 'SUDESTE'
                elif uf in ['PR', 'SC', 'RS']:
                    return 'SUL'
                elif uf in ['AC', 'AM', 'PA', 'RR', 'AP', 'RO', 'TO']:
                    return 'NORTE'
                elif uf in ['DF', 'MT', 'MS', 'GO']:
                    return 'CENTRO-OESTE'
                elif uf in ['AL', 'BA', 'CE', 'MA', 'PB', 'RN', 'SE', 'PE', 'PI']:
                    return 'NORDESTE'
                else:
                    return 'DDD INVALIDO/DDD OU TELEFONE NAO INFORMADO'

            # CRIANDO COLUNA DE REGIÃO
            df_base_teste['REGIAO'] = df_base_teste['UF'].map(regiao)

            # SELECIONANDO OS 10.000 CONTATOS COM AS MELHORES OFERTAS
            df_base_teste_10000 = df_base_teste.assign(
                FLG_ESPECIAL_RANKING = df_base_teste['FLG_ESPECIAL'].map(ordem_flg_especial),
                PLANO_INDICADO_RANKING = df_base_teste['PLANO_INDICADO'].map(ordem_plano_indicado),
                DESCONTO_DESTINO_RANKING = df_base_teste['DESCONTO_DESTINO'].map(ordem_desconto_destino),
                CLUSTER_RANKING = df_base_teste['CLUSTER'].map(ordem_cluster)
            ).sort_values(
                by = ['FLG_ESPECIAL_RANKING', 'PLANO_INDICADO_RANKING', 'DESCONTO_DESTINO_RANKING', 'CLUSTER_RANKING'],
                ascending = [False, False, False, False]
            ).drop(
                columns = ['FLG_ESPECIAL_RANKING', 'PLANO_INDICADO_RANKING', 'DESCONTO_DESTINO_RANKING', 'CLUSTER_RANKING']
            ).reset_index(
                drop = True
            ).copy()[:10000]

        st.title('Relatório de Clientes')

        st.subheader('As 10.000 melhores ofertas')
        st.dataframe(df_base_teste_10000)

        st.subheader('Quantidade de Clientes por UF')
        st.bar_chart(data = df_base_teste[['UF', 'REGIAO']].value_counts().to_frame().reset_index(), x = 'UF', y = 'count', color = 'REGIAO', x_label = 'UF', y_label = 'Quantidade')

        st.subheader('Quantidade de Clientes por Região')
        st.bar_chart(data = df_base_teste[['REGIAO']].value_counts().to_frame().reset_index(), x = 'REGIAO', y = 'count', color = 'REGIAO', x_label = 'Região', y_label = 'Quantidade')

        st.subheader('Quantidade de Clientes por Idade')
        st.bar_chart(data = df_base_teste[['IDADE']].value_counts().to_frame().reset_index(), x = 'IDADE', y = 'count', x_label = 'Idade', y_label = 'Quantidade')
        
        st.subheader('Distribuição da Faixa de Recarga nos Últimos 3 Meses')
        st.bar_chart(data = df_base_teste[['FAIXA_RECARGA']].value_counts().to_frame().reset_index(), x = 'FAIXA_RECARGA', y = 'count', x_label = 'Recarga (em R$)', y_label = 'Quantidade')