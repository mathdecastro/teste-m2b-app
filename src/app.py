import pandas as pd
from funcoes import criar_dataframe_ofertas, criar_dataframe_tratativas
import altair as alt
import streamlit as st

if 'df_ofertas' not in st.session_state and 'df_tratativas' not in st.session_state and 'df_ofertas_10000' not in st.session_state:
    st.session_state['df_ofertas'] = None
    st.session_state['df_tratativas'] = None
    st.session_state['df_ofertas_10000'] = None

# TITULO
st.sidebar.title('Teste Mobi2buy')
st.sidebar.markdown('Teste para o cargo de Analista de Operações e Performance Pleno na Mobi2buy')

arquivo_ofertas = st.sidebar.file_uploader('Envie o arquivo de ofertas (em csv)', type = 'csv')
arquivo_tratativas = st.sidebar.file_uploader('Envie o arquivo de tratativas (em csv)', type = 'csv')

if arquivo_ofertas and arquivo_tratativas:
    if st.sidebar.button('Criar relatório'):
        with st.spinner('Criando o relatório. Por favor, aguarde.'):
            # CRIANDO UM DATAFRAME PANDAS PARA CADA BASE
            df_base_teste = pd.read_csv(arquivo_ofertas, sep = '|')
            df_tratativas_teste = pd.read_csv(arquivo_tratativas, sep = '|')

            ofertas = criar_dataframe_ofertas(dataframe_ofertas = df_base_teste)
            tratativas = criar_dataframe_tratativas(dataframe_tratativas = df_tratativas_teste)

            df_merged = tratativas.merge(ofertas, left_on = 'MSISDN', right_on = 'NUM_TELEFONE', how = 'left')
            df_tratativas = df_merged[~df_merged['NUM_TELEFONE'].isna()][tratativas.columns]

            df_merged = ofertas.merge(tratativas, left_on = 'NUM_TELEFONE', right_on = 'MSISDN', how = 'left')
            df_ofertas = df_merged[df_merged['MSISDN'].isna()][ofertas.columns]

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

            # SELECIONANDO OS 10.000 CONTATOS COM AS MELHORES OFERTAS
            df_ofertas_10000 = df_ofertas.assign(
                FLG_ESPECIAL_RANKING = df_ofertas['FLG_ESPECIAL'].map(ordem_flg_especial),
                PLANO_INDICADO_RANKING = df_ofertas['PLANO_INDICADO'].map(ordem_plano_indicado),
                DESCONTO_DESTINO_RANKING = df_ofertas['DESCONTO_DESTINO'].map(ordem_desconto_destino),
                CLUSTER_RANKING = df_ofertas['CLUSTER'].map(ordem_cluster)
            ).sort_values(
                by = ['FLG_ESPECIAL_RANKING', 'PLANO_INDICADO_RANKING', 'DESCONTO_DESTINO_RANKING', 'CLUSTER_RANKING'],
                ascending = [False, False, False, False]
            ).drop(
                columns = ['FLG_ESPECIAL_RANKING', 'PLANO_INDICADO_RANKING', 'DESCONTO_DESTINO_RANKING', 'CLUSTER_RANKING']
            ).reset_index(
                drop = True
            )[:10000]
        
        st.session_state['df_ofertas'] = df_ofertas
        st.session_state['df_tratativas'] = df_tratativas
        st.session_state['df_ofertas_10000'] = df_ofertas_10000

if st.session_state['df_ofertas'] is not None and st.session_state['df_tratativas'] is not None and st.session_state['df_ofertas_10000'] is not None:
    df_ofertas = st.session_state['df_ofertas']
    df_tratativas = st.session_state['df_tratativas']
    df_ofertas_10000 = st.session_state['df_ofertas_10000']

    with st.expander('Descrição do teste e considerações gerais'):
        st.caption("""
            # DESCRIÇÃO DO TESTE

            SELECIONAR 10.000 CASOS COM AS SEGUINTES EXIGÊNCIAS:
            - RETIRAR CASOS EM QUE O TELEFONE É INVÁLIDO
            - RETIRAR CASOS QUE JÁ CONVERTERAM -> FAZER UM JOIN COM A BASE DE TRATATIVAS PARA SELECIONAR OS CASOS QUE JÁ CONVERTERAM
            - SELECIONAR OS CASOS COM AS MELHORES OFERTAS -> BASICAMENTE, SÃO CASOS EM QUE ESTAS COLUNAS TÊM OS MELHORES VALORES NESTA ORDEM: FLG_ESPECIAL > PLANO_INDICADO > DESCONTO_DESTINO > CLUSTER

            ==========================================================================================

            # TELEFONE

            EM RELAÇÃO AOS NÚMEROS, CONSIDEREI QUE ELE SÓ SERÁ VÁLIDO SE, E SOMENTE SE, ATENDER OS SEGUINTES REQUISITOS:
            - TIVER UM TOTAL DE 11 DÍGITOS. EXEMPLO: (21) 98282-3737 -> O TOTAL DE DÍGITOS DE 21982823737 É 11
            - O CÓDIGO DE ÁREA FOR VÁLIDO. EXEMPLO: (21) 98282-3737 -> 21 É UM CÓDIGO VÁLIDO
            - TIVER O ALGARISMO 9 NA TERCEIRA POSIÇÃO DA ESQUERDA PRA DIREITA. EXEMPLO: (21) 98282-3737 -> 21982823737 -> NA TERCEIRA POSIÇÃO, DA ESQUERDA PRA DIREITA, HÁ O ALGARISMO 9

            EM RELAÇÃO AOS NÚMEROS DUPLICADOS, QUE SÓ ESTÃO PRESENTES NA BASE DE TESTE, UTILIZAREI A SEGUINTE ABORDAGEM:
            - MANTER NA BASE O CASO EM QUE A IDADE DO CONTATO É A MAIOR -> EM DOIS CASOS COM O MESMO NÚMERO, UM CASO PODE TER A 'IDADE' CLASSIFICADA EM '31 A 45' E O OUTRO CASO PODE TER A IDADE CLASSIFICADA EM 'ACIMA DE 45'. NESTE CASO, SERÁ MANTIDO SOMENTE O CASO EM QUE A IDADE É 'ACIMA DE 45'
            - CONSIDERANDO QUE A CLASSIFICAÇÃO DE IDADE SEJA A MESMA NOS CASOS DUPLICADOS, MANTER NA BASE O CASO EM QUE O CONTATO PELA M2B SEJA O MAIS RECENTE -> UTILIZAR 'FLG_FRESCOR' PARA ESTA REGRA
            - EM CASOS DUPLICADOS QUE HAJA IGUALDADE NAS VARIÁVEIS 'IDADE' E 'FLG_FRESCOR', MANTER O CASO COM A MELHOR OFERTA -> FLG_ESPECIAL > PLANO_INDICADO > DESCONTO_DESTINO > CLUSTER

            ==========================================================================================

            # OFERTAS

            APÓS UMA ANÁLISE DOS DADOS, ENCONTREI AS SEGUINTES RELAÇÕES ENTRE COLUNAS:

            Se FLG_ESPECIAL = 1:

            - Se PLANO_INDICADO = A, então:
                - BONUS_DESTINO: 14GB
                - DESCONTO_DESTINO: 15%

            - Se PLANO_INDICADO = L, então:
                - BONUS_DESTINO: 10GB + 20GB
                - DESCONTO_DESTINO: 17 NFIDEL ou 20 NFIDEL

            - Se PLANO_INDICADO = S, então:
                - BONUS_DESTINO: 20GB + 20GB
                - DESCONTO_DESTINO: 25 NFIDEL, 28 NFIDEL, 37 NFIDEL, 40 NFIDEL, 41 NFIDEL ou 43 NFIDEL

            Se FLG_ESPECIAL = 0:

            - Se PLANO_INDICADO = C, então:
                - BONUS_DESTINO: 20GB
                - DESCONTO_DESTINO: 00 NFIDEL

            - Se PLANO_INDICADO = B, então:
                - BONUS_DESTINO: 20GB
                - DESCONTO_DESTINO: 00 NFIDEL

            - Se PLANO_INDICADO = A, então:
                - BONUS_DESTINO: 9GB
                - DESCONTO_DESTINO: 5% ou 15%

            - Se PLANO_INDICADO = L, então:
                - BONUS_DESTINO: 20GB
                - DESCONTO_DESTINO: 17 NFIDEL ou 20 NFIDEL

            - Se PLANO_INDICADO = S, então:
                - BONUS_DESTINO: 10GB + 20GB
                - DESCONTO_DESTINO: 25 NFIDEL, 28 NFIDEL, 37 NFIDEL, 40 NFIDEL, 41 NFIDEL ou 43 NFIDEL
        """)
    
    st.title('Dashboard Ofertas')

    st.subheader('As 10.000 melhores ofertas')
    st.dataframe(df_ofertas_10000)

    st.markdown('#### Filtros')
    categorias_flg_especial = st.segmented_control('FLG_ESPECIAL', options = df_ofertas['FLG_ESPECIAL'].unique(), default = df_ofertas['FLG_ESPECIAL'].unique(), selection_mode = 'multi')
    categorias_plano_indicado = st.segmented_control('PLANO_INDICADO', options = df_ofertas['PLANO_INDICADO'].unique(), default = df_ofertas['PLANO_INDICADO'].unique(), selection_mode = 'multi')
    categorias_bonus_destino = st.segmented_control('BONUS_DESTINO', options = df_ofertas['BONUS_DESTINO'].unique(), default = df_ofertas['BONUS_DESTINO'].unique(), selection_mode = 'multi')
    categorias_desconto_destino = st.segmented_control('DESCONTO_DESTINO', options = df_ofertas['DESCONTO_DESTINO'].unique(), default = df_ofertas['DESCONTO_DESTINO'].unique(), selection_mode = 'multi')
    categoria_idade = st.segmented_control('IDADE', options = df_ofertas['IDADE'].unique(), default = df_ofertas['IDADE'].unique(), selection_mode = 'multi')
    categoria_flg_frescor = st.segmented_control('FLG_FRESCOR', options = df_ofertas['FLG_FRESCOR'].unique(), default = df_ofertas['FLG_FRESCOR'].unique(), selection_mode = 'multi')
    filtro = (df_ofertas['FLG_ESPECIAL'].isin(categorias_flg_especial) &
              df_ofertas['PLANO_INDICADO'].isin(categorias_plano_indicado) &
              df_ofertas['BONUS_DESTINO'].isin(categorias_bonus_destino) &
              df_ofertas['DESCONTO_DESTINO'].isin(categorias_desconto_destino) &
              df_ofertas['IDADE'].isin(categoria_idade) &
              df_ofertas['FLG_FRESCOR'].isin(categoria_flg_frescor))

    col1, col2 = st.columns(2)

    with col1:
        st.subheader('Quantidade de Clientes por UF')
        st.bar_chart(data = df_ofertas[filtro][['UF', 'REGIAO']].value_counts().to_frame().reset_index(), x = 'UF', y = 'count', color = 'REGIAO', x_label = 'UF', y_label = 'Quantidade')

    with col2:
        st.subheader('Quantidade de Clientes por Região')
        st.bar_chart(data = df_ofertas[filtro][['REGIAO']].value_counts().to_frame().reset_index(), x = 'REGIAO', y = 'count', color = 'REGIAO', x_label = 'Região', y_label = 'Quantidade')

    col3, col4 = st.columns(2)

    with col3:
        st.subheader('Quantidade de Clientes por Idade')
        st.bar_chart(data = df_ofertas[filtro][['IDADE']].value_counts().to_frame().reset_index(), x = 'IDADE', y = 'count', x_label = 'Idade', y_label = 'Quantidade')

    with col4:
        st.subheader('Distribuição da Faixa de Recarga nos Últimos 3 Meses')
        st.bar_chart(data = df_ofertas[filtro][['FAIXA_RECARGA']].value_counts().to_frame().reset_index(), x = 'FAIXA_RECARGA', y = 'count', x_label = 'Recarga (em R$)', y_label = 'Quantidade')

    col5, col6, col7 = st.columns(3)

    with col5:
        st.subheader('Quantidade de Clientes por Plano Indicado')
        st.bar_chart(data = df_ofertas[filtro][['PLANO_INDICADO']].value_counts().to_frame().reset_index(), x = 'PLANO_INDICADO', y = 'count', x_label = 'Plano Indicado', y_label = 'Quantidade')

    with col6:
        st.subheader('Quantidade de Clientes por Bônus da Oferta')
        st.bar_chart(data = df_ofertas[filtro][['BONUS_DESTINO']].value_counts().to_frame().reset_index(), x = 'BONUS_DESTINO', y = 'count', x_label = 'Bônus da Oferta', y_label = 'Quantidade')

    with col7:
        st.subheader('Quantidade de Clientes por Desconto da Oferta')
        st.bar_chart(data = df_ofertas[filtro][['DESCONTO_DESTINO']].value_counts().to_frame().reset_index(), x = 'DESCONTO_DESTINO', y = 'count', x_label = 'Desconto da Oferta', y_label = 'Quantidade')

    st.title('Dashboard Tratativas')

    col8, col9 = st.columns(2)

    with col8:
        st.subheader('Quantidade de Clientes por Produto')
        st.altair_chart(
            alt.Chart(
                data = df_tratativas[['PRODUTO']].value_counts().to_frame().reset_index(drop = False)
            ).mark_arc(
            ).encode(
                theta = 'count',
                color = 'PRODUTO'
            )
        )
    
    with col9:
        st.subheader('Quantidade de Clientes por Produto Ofertado')
        st.bar_chart(data = df_tratativas[['PRODUTO', 'PRODUTO OFERTADO']].value_counts().to_frame().reset_index(drop = False), x = 'PRODUTO OFERTADO', y = 'count', color = 'PRODUTO', x_label = 'Produto Ofertado', y_label = 'Quantidade')