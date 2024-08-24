import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
title = "YM Business Intelligence"
st.set_page_config(page_title=title, page_icon=":bar_chart:", layout="wide")

# Dados iniciais dos custos estimados por etapa
custo_estimado_por_etapa = {
    "Serv. Preliminares": 3500.00,
    "Projeto": 3600.00,
    "Fundação": 26000.00,
    "Fabricação": 110000.00,
    "Movimentação": 6500.00,
    "Transporte": 6000.00,
    "Montagem": 13000.00,
    "Acabamento": 10000.00,
    "Administrativo": 6000.00
}

fornecedores = ["Aguas de Joinville", "YUMA"]
subetapas = ["Produto", "Serviço"]
hasData = False


# Inicializa a lista para armazenar os dados, o valor de venda e o custo realizado por etapa
if 'data' not in st.session_state:
    st.session_state['data'] = []
if 'valor_venda' not in st.session_state:
    st.session_state['valor_venda'] = 0.0
if 'custo_realizado_por_etapa' not in st.session_state:
    st.session_state['custo_realizado_por_etapa'] = {etapa: 0.0 for etapa in custo_estimado_por_etapa.keys()}

# Função para adicionar um novo registro
def add_record(data):
    st.session_state['data'].append(data)
    etapa = data["Etapa"]
    custo_realizado = data["Custo Realizado"]
    if etapa in st.session_state['custo_realizado_por_etapa']:
        st.session_state['custo_realizado_por_etapa'][etapa] += custo_realizado

# Função para calcular o saldo do custo estimado por etapa
def calcular_saldo_por_etapa():
    return {etapa: custo_estimado - st.session_state['custo_realizado_por_etapa'].get(etapa, 0.0)
            for etapa, custo_estimado in custo_estimado_por_etapa.items()}

# Função para exibir o dataframe formatado
def format_currency(df, columns):
    for column in columns:
        df[column] = df[column].apply(lambda x: f"R$ {x:,.2f}")
    return df

# Título da aplicação
st.title(title)

# Campo para Valor de Venda
with st.expander('Valor de venda'):
    valor_venda = st.number_input("Valor de Venda", min_value=0.0, format="%.2f")
    if st.button('Salvar Valor de Venda'):
        st.session_state['valor_venda'] = valor_venda
        st.success("Valor de Venda salvo com sucesso!")

# Tabela de Custo Estimado por Etapa
with st.expander('Custo estimado por etapa da obra'):
    st.subheader('Custos Estimados por Etapa')
    custo_estimado_df = pd.DataFrame(list(custo_estimado_por_etapa.items()), columns=['CUSTO ETAPA', 'CUSTO ESTIMADO'])
    custo_estimado_df = format_currency(custo_estimado_df, ['CUSTO ESTIMADO'])
    st.data_editor(custo_estimado_df, use_container_width=True)

# Formulário de Cadastro
with st.expander('Cadastrar despesa', expanded=True):
    with st.form(key='project_form'):
        col1, col2 = st.columns(2)  # Divide o layout em duas colunas
        
        with col1:
            data = st.date_input("Data")
            descricao = st.text_input("Descrição")
            etapa = st.selectbox("Etapa", options=custo_estimado_por_etapa.keys())
        
        with col2:
            subetapa = st.selectbox("Produto ou serviço?", options=subetapas)
            fornecedor = st.selectbox("Fornecedor", options=fornecedores)
            custo_realizado = st.number_input("Custo Realizado", min_value=0.0, format="%.2f")
        
        if st.form_submit_button(label="Adicionar Registro"):
            new_record = {
                "Data": data,
                "Descrição": descricao,
                "Etapa": etapa,
                "Subetapa": subetapa,
                "Fornecedor": fornecedor,
                "Custo Realizado": custo_realizado
            }
            add_record(new_record)
            st.success("Registro adicionado com sucesso!")

# Atualiza a tabela de Custo Realizado por Etapa
with st.expander('Registros'):
    st.subheader('Custos Realizados por Etapa')
    custo_realizado_df = pd.DataFrame(list(st.session_state['custo_realizado_por_etapa'].items()), columns=['CUSTO ETAPA', 'CUSTO REALIZADO'])
    custo_realizado_df['CUSTO ESTIMADO'] = custo_realizado_df['CUSTO ETAPA'].map(custo_estimado_por_etapa)
    custo_realizado_df['SALDO'] = custo_realizado_df['CUSTO ESTIMADO'] - custo_realizado_df['CUSTO REALIZADO']
    custo_realizado_df = format_currency(custo_realizado_df, ['CUSTO REALIZADO', 'CUSTO ESTIMADO', 'SALDO'])
    st.dataframe(custo_realizado_df, use_container_width=True)

    # Visualizando a Tabela de Dados
    st.subheader('Dados do Projeto')

    if st.session_state['data']:
        df = pd.DataFrame(st.session_state['data'])
        df = format_currency(df, ['Custo Realizado'])
        st.dataframe(df, use_container_width=True)
        hasData = True

    else:
        st.write("Nenhum dado inserido ainda.")

with st.expander('Resumo do Projeto', expanded=hasData):
# Análise de Custos
    st.subheader('Análise de Custos')

    if st.session_state['data']:
        df = pd.DataFrame(st.session_state['data'])
        
        # Verifique se a coluna 'Custo Realizado' está no formato float
        df['Custo Realizado'] = df['Custo Realizado'].astype(float)
        
        # Calcular o custo realizado total
        custo_realizado_total = df['Custo Realizado'].sum()

        # Calcular o custo estimado total com base nas etapas inseridas no DataFrame
        custo_estimado_total = df['Etapa'].apply(lambda x: custo_estimado_por_etapa.get(x, 0.0)).sum()
        
        # Calcular o saldo total
        saldo_total = custo_estimado_total - custo_realizado_total

        # Exibir os resultados
        st.metric("Custo Realizado Total", f"R$ {custo_realizado_total:,.2f}")
        st.metric("Custo Estimado Total", f"R$ {custo_estimado_total:,.2f}")
        st.metric("Saldo", f"R$ {saldo_total:,.2f}")



    # Gráfico de Burndown por Categoria (Etapa)
    if st.session_state['data']:
        # Preparando os dados para o gráfico
        burndown_data = []
        for etapa, custo_estimado in custo_estimado_por_etapa.items():
            custo_realizado = st.session_state['custo_realizado_por_etapa'].get(etapa, 0.0)
            burndown_data.append({'Etapa': etapa, 'Tipo': 'Estimado', 'Custo': custo_estimado})
            burndown_data.append({'Etapa': etapa, 'Tipo': 'Realizado', 'Custo': custo_realizado})

        burndown_df = pd.DataFrame(burndown_data)

        # Criando o gráfico de burndown por categoria (etapa)
        fig = px.line(burndown_df, x='Etapa', y='Custo', color='Tipo',
                    labels={"Custo": "R$ Custo", "Etapa": "Categoria"},
                    title="Custo Estimado x Custo Realizado por Etapa",
                    markers=True)

        # Adicionando um indicador para destacar se o custo realizado extrapolar o estimado
        for _, row in burndown_df.iterrows():
            if row['Tipo'] == 'Realizado' and row['Custo'] > custo_estimado_por_etapa[row['Etapa']]:
                fig.add_scatter(x=[row['Etapa']],
                                y=[row['Custo']],
                                mode='markers',
                                marker=dict(color='red', size=10),
                                name='Extrapolado')

        st.plotly_chart(fig, use_container_width=True)
