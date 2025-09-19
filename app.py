from dotenv import load_dotenv
import os
import psycopg2
import mysql.connector
import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib as plt
import plotly.express as px
import numpy as np
from io import BytesIO
import unicodedata
import re
import difflib
import json
from datetime import datetime, timedelta
import streamlit.components.v1 as components
import xlsxwriter
import hashlib
import json

st.set_page_config(layout="wide")
@st.cache_data
def carregando_processando_dados():
    teste = 0
    return teste

# Loadando usuários
usuarios_dict = {}
with open("users.json","r",encoding="utf-8") as f:
    usuarios_dict = json.load(f)

# Criando tabela (atualizada a cada interação)
tabela = pd.read_excel("banco_dasa.xlsx")
tabela["Data"] = pd.to_datetime(tabela["Data"])

# Recebendo dados do cache
teste = carregando_processando_dados()

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap');
        *{
            padding: 0;
            margin: 0;
            box-sizing: border-box;
            font-family: 'Poppins','sans-serif';
        }
    </style>
""",unsafe_allow_html=True)

st.markdown("""
    <style>
        .bloco-borda {
            border: 2px solid #1B3A57;
            border-radius: 12px;
            padding: 18px 20px;
            margin-bottom: 18px;
            background: #F5FAFF;
        }
    </style>
""", unsafe_allow_html=True)

# Início da página
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = False

if not st.session_state.usuario_logado:
    # Criando campos de login
    col1, _, col2 = st.columns([1, 3, 1])  # colunas com espaço no meio
    with col1:
        st.image("assets/icons/bitwise.png", width=360)
        teste=0
    with col2:
        st.image("assets/icons/dasa.png", width=90)
        teste=0

    with st.form("login_form"):
        st.title("DASA - Analytics BITWISE.")
        usuario = st.text_input("Usuário:").lower()
        senha = st.text_input("Senha:", type="password")
        submit = st.form_submit_button("Entrar")
        if submit:
           # Inserir lógica de buscar usuario/senha no dotenv

            if usuario in usuarios_dict and usuarios_dict[usuario]["senha"] == senha:
                st.success(f"Bem-vindo, {usuario}!")
                st.session_state.usuario_logado = True
                st.session_state.usuario = usuario
                st.session_state.acesso = usuarios_dict[usuario]["acesso"]
                print(usuarios_dict[usuario]["acesso"])
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos!")

# Verificando credenciais 
if st.session_state.usuario_logado:
    usuario = st.session_state.get("usuario")
    acesso = st.session_state.acesso

    if acesso==2 or acesso==1:
        # Exibir conteúdo protegido após login
        # Logo do sidebar
        with st.sidebar:
            st.image("assets/icons/bitwise.png", width=300)
            st.markdown("----------------")
            container_bar = st.container()  # Criando containers para deixar gráficos lado a lado
            colbar1,colbar2 = container_bar.columns(2)
        
        if "filtro_data_inicial" or "filtro_data_final" not in st.session_state:
            # Pegar data inicial e final da tabela (delimitar o max e min)
            st.session_state.filtro_data_inicial = tabela["Data"].min() # Primeiro valor apresentado
            st.session_state.filtro_data_final = tabela["Data"].max()
            data_inicio = tabela["Data"].min()
            data_fim = tabela["Data"].max()
        if "date_input_key" not in st.session_state:
            st.session_state.date_input_key = 0
        with st.sidebar:
            with colbar1:
                data_inicial = st.date_input(
                    "Data inicial:",
                    value=st.session_state.filtro_data_inicial,
                    min_value=data_inicio,
                    max_value=data_fim,
                    format="DD/MM/YYYY",
                    key=f"filtro_data_inicial{st.session_state.date_input_key}",  # muda a chave dinamicamente
                )
            with colbar2:
                data_final = st.date_input(
                    "Data final:",
                    value=st.session_state.filtro_data_final,
                    min_value=data_inicio,
                    max_value=data_fim,
                    format="DD/MM/YYYY",
                    key=f"filtro_data_final{st.session_state.date_input_key}",  # muda a chave dinamicamente
                )

        if data_inicial > data_final:
            lista_datas = [data_inicial, data_final]
            data_inicial = min(lista_datas)
            data_final = max(lista_datas)

        if data_inicial != st.session_state.filtro_data_inicial:
            st.session_state.filtro_data_inicial = data_inicial
        
        if data_final != st.session_state.filtro_data_final:
            st.session_state.filtro_data_final = data_final

        # Aplica o filtro no DataFrame
        tabela = tabela[
            (tabela["Data"].dt.date >= st.session_state.filtro_data_inicial) &
            (tabela["Data"].dt.date <= st.session_state.filtro_data_final)
        ]

        # Filtro dos insumos no sidebar
        insumos_unicos = sorted(tabela["Insumo"].unique(), key=str) # Obtendo valores únicos
        insumos_selecionado = st.sidebar.multiselect("Filtrar por insumo:", ["Todos"] + insumos_unicos, default="Todos")
        if "Todos" in insumos_selecionado:
            tabela = tabela[
                tabela["Insumo"].isin(insumos_unicos)
            ]     
        else:
            tabela = tabela[
                tabela["Insumo"].isin(insumos_selecionado)
            ]

        # Ordenação de data no sidebar 
        st.sidebar.markdown("Ordenar período: ")
        ordem_crescente = st.sidebar.button("Crescente")
        ordem_decrescente = st.sidebar.button("Decrescente")
        if ordem_crescente:
            tabela = tabela.sort_values(by="Data", ascending=True)
        elif ordem_decrescente:
            tabela = tabela.sort_values(by="Data", ascending=False)
        
        # Selecionando o período completo
        st.sidebar.markdown("Selecionar período completo:")
        todas_ocorrencias = st.sidebar.button("Todos os registros")
        if todas_ocorrencias:
            st.session_state.date_input_key += 1
            st.rerun()

        # Mostra o botão de logout na barra lateral
        st.sidebar.markdown("Encerrar sessão: ")
        if st.sidebar.button("Sair"):
            st.session_state.usuario_logado = False
            st.session_state.nome_usuario = None
            del st.session_state["filtro_data_inicial"]
            del st.session_state["filtro_data_final"]
            del st.session_state["date_input_key"]
            st.rerun()  # Reinicia o app para voltar à tela de login

        tabela_final = tabela.copy()
        tabela_final["Data"] = tabela_final["Data"].dt.strftime("%d/%m/%Y") # Ajustando padrão da data antes de apresentar a tabela
        tabela_final = tabela_final.reset_index(drop=True)
        total_registros = len(tabela_final)

        # Criando gráficos na mão com python
        # Tons de azul pulando para mais claro
        cores_pizza = [
            '#00193E',  # Azul escuro principal
            '#005DB6',  # Azul claro
            '#3399FF',  # Azul mais claro
            '#66B2FF',  # Azul pastel
            '#B3D8FF',  # Azul muito claro
            '#E6F4FF',  # Azul quase branco
        ]

        df_contagem = tabela_final.groupby('Insumo')['Consumo'].sum().reset_index()
        df_contagem.columns = ['Categoria', 'Total']

        # Cria a label para mostrar no gráfico
        df_contagem['label'] = df_contagem.apply(
            lambda row: f"{row['Categoria']}: {row['Total']}", axis=1
        )

        # Ordena as fatias para que as maiores fiquem com os tons mais escuros
        def ordenar_cores_por_valor(df, cores):
            df_sorted = df.sort_values(by='Total', ascending=False).reset_index(drop=True)
            cor_map = {cat: cores[i % len(cores)] for i, cat in enumerate(df_sorted['Categoria'])}
            return [cor_map[cat] for cat in df['Categoria']]

        # Para gráfico de insumos por categoria
        cores_pizza_ordenadas = ordenar_cores_por_valor(df_contagem, cores_pizza)

        insumos = px.pie(
            df_contagem,
            values='Total',
            names='Categoria',
            title='Controle de insumos'
        )
        insumos.update_traces(
            marker=dict(colors=cores_pizza_ordenadas),
            textinfo='none',  # esconde o padrão
            texttemplate='%{label} %{value} (%{percent})',
            textfont_size=11,
            textposition='outside',  # coloca o texto fora da fatia
            showlegend=False,
        )
        insumos.update_layout(
            margin=dict(t=60, b=50, l=110, r=110),
            height=280,
            paper_bgcolor='#E6F4FF',     # Fundo geral (visual de azul claro)
            plot_bgcolor='#F5FAFF',      # Parte central (pouco visível no pie, mas útil em barra)
            title_font_color='#1B3A57',  # Azul mais escuro pro título
            font_color='#1B3A57',
        )

        # Gráfico 2 - Qtd de insumos por setor (agrupando por setor)
        df_setor = tabela_final.groupby('Setor')['Consumo'].sum().reset_index()
        df_setor.columns = ['Setor', 'Total']
        df_setor['label'] = df_setor.apply(lambda row: f"{row['Setor']}: {row['Total']}", axis=1)

        def ordenar_cores_por_valor_setor(df, cores):
            df_sorted = df.sort_values(by='Total', ascending=False).reset_index(drop=True)
            cor_map = {setor: cores[i % len(cores)] for i, setor in enumerate(df_sorted['Setor'])}
            return [cor_map[setor] for setor in df['Setor']]

        cores_pizza_setor_ordenadas = ordenar_cores_por_valor_setor(df_setor, cores_pizza)

        insumos2 = px.pie(
            df_setor,
            values='Total',
            names='Setor',
            title='Qtd de insumos por setor'
        )
        insumos2.update_traces(
            marker=dict(colors=cores_pizza_setor_ordenadas),
            textinfo='none',
            texttemplate='%{label} %{value} (%{percent})',
            textfont_size=11,
            textposition='outside',
            showlegend=False,
        )
        insumos2.update_layout(
            margin=dict(t=60, b=50, l=110, r=110),
            height=280,
            paper_bgcolor='#E6F4FF',
            plot_bgcolor='#F5FAFF',
            title_font_color='#1B3A57',
            font_color='#1B3A57',
        )

        # Gráfico 3 - Qtd de insumos por hora (agrupando em HH:00)
        # Extrai a hora no formato HH:00
        tabela_final['HoraFormatada'] = pd.to_datetime(tabela_final['Hora'], format='%H:%M:%S', errors='coerce').dt.strftime('%H:00')
        df_hora = tabela_final.groupby('HoraFormatada')['Consumo'].sum().reset_index()
        df_hora.columns = ['Hora', 'Total']
        df_hora['label'] = df_hora.apply(lambda row: f"{row['Hora']}: {row['Total']}", axis=1)

        # Para gráfico de insumos por hora
        def ordenar_cores_por_valor_hora(df, cores):
            df_sorted = df.sort_values(by='Total', ascending=False).reset_index(drop=True)
            cor_map = {hora: cores[i % len(cores)] for i, hora in enumerate(df_sorted['Hora'])}
            return [cor_map[hora] for hora in df['Hora']]

        cores_pizza_hora_ordenadas = ordenar_cores_por_valor_hora(df_hora, cores_pizza)

        insumos3 = px.pie(
            df_hora,
            values='Total',
            names='Hora',
            title='Qtd de insumos por hora'
        )
        insumos3.update_traces(
            marker=dict(colors=cores_pizza_hora_ordenadas),
            textinfo='none',
            texttemplate='%{label} %{value} (%{percent})',
            textfont_size=11,
            textposition='outside',
            showlegend=False,
        )
        insumos3.update_layout(
            margin=dict(t=60, b=50, l=110, r=110),
            height=280,
            paper_bgcolor='#E6F4FF',
            plot_bgcolor='#F5FAFF',
            title_font_color='#1B3A57',
            font_color='#1B3A57',
        )

        # Garante que todas as horas de 00:00 até 23:00 estejam presentes no gráfico
        horas_completas = [f"{h:02d}:00" for h in range(24)]
        df_hora_completo = pd.DataFrame({'Hora': horas_completas})
        df_hora_completo = df_hora_completo.merge(df_hora, on='Hora', how='left').fillna({'Total': 0, 'label': ''})

        # Gráfico 4 - Qtd de insumos por hora em colunas (bar chart)
        insumos4 = px.bar(
            df_hora_completo,
            x='Hora',
            y='Total',
            text='Total',
            title='Qtd de insumos por hora',
            color='Hora',
            color_discrete_sequence=cores_pizza_hora_ordenadas
        )
        insumos4.update_traces(
            texttemplate='%{y}',
            textposition='outside',  # Valor fora da barra, no topo
            textfont=dict(color='#1B3A57'),  # Azul escuro para texto
            marker_line_width=0,  # Remove bordas das barras
        )
        insumos4.update_layout(
            margin=dict(t=45, b=5, l=5, r=5),  # Margens mínimas
            height=280,  # Menor altura para barras menos altas
            paper_bgcolor='#E6F4FF',
            plot_bgcolor='#F5FAFF',
            title_font_color='#1B3A57',
            font_color='#1B3A57',
            xaxis_title='Hora',
            yaxis_title='Total',
            showlegend=False,
            xaxis=dict(
                tickmode='array',
                tickvals=horas_completas,
                ticktext=horas_completas,
                tickfont=dict(color='#1B3A57', size=13),
                showgrid=False,
                showline=True,
                linecolor='#1B3A57',
            ),
            yaxis=dict(
                showgrid=False,
                showline=True,
                linecolor='#1B3A57',
            ),
            bargap=0.01,  # Barras mais largas
        )

        # Página
        st.markdown(
            f"<h2>Intervalo selecionado: {st.session_state.filtro_data_inicial.strftime('%d/%m/%Y')}  até  {st.session_state.filtro_data_final.strftime('%d/%m/%Y')}</h2>"        
        ,unsafe_allow_html=True)
        st.write(f"Bem-vindo de volta, {usuario}!")

        container = st.container()  # Criando containers para deixar gráficos lado a lado
        col1,col2 = container.columns(2)

        col1.plotly_chart(insumos, use_container_width=True)
        col2.plotly_chart(insumos2, use_container_width=True)

        # Gráfico de barras esticado abaixo dos dois gráficos de pizza
        st.plotly_chart(insumos4, use_container_width=True)
        # Ajusta altura das barras para ficarem mais visíveis e o gráfico menor
        insumos4.update_layout(
            height=120,  # altura menor para barras mais proporcionais e visualização melhor
            margin=dict(t=5, b=5, l=5, r=5),
            paper_bgcolor='#E6F4FF',
            plot_bgcolor='#F5FAFF',
            title_font_color='#1B3A57',
            font_color='#1B3A57',
            xaxis_title='Hora',
            yaxis_title='Total',
            showlegend=False,
            xaxis=dict(
                tickmode='array',
                tickvals=horas_completas,
                ticktext=horas_completas,
                tickfont=dict(color='#1B3A57', size=13),
                showgrid=False,
                showline=True,
                linecolor='#1B3A57',
            ),
            yaxis=dict(
                showgrid=False,
                showline=True,
                linecolor='#1B3A57',
            ),
            bargap=0.05,
        )

        st.subheader("Relatório")
        st.dataframe(tabela_final, height=350)
        st.markdown(f"📌 Total de registros: {total_registros}")
        def to_excel(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Tabela')
            return output.getvalue()

        st.subheader("Exportar para Excel")
        excel_file = to_excel(tabela_final)
        # Obtendo dia mes e ano atual para nomear arquivo
        agora = datetime.now()
        dia = agora.day
        mes = agora.month
        ano = agora.year
        st.download_button(
            label="📥 Baixar planilha",
            data=excel_file,
            file_name=f"Planilha_{usuario}_{dia}/{mes}/{ano}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    if acesso==2 or acesso==0:
        # Exibir conteúdo protegido após login            
        for chave in ["valor_seringa", "valor_algodao","valor_gazes","valor_luvas"]:
            if chave not in st.session_state:
                st.session_state[chave] = 0

        # Criando formulário para adicionar uso dos insumos
        container = st.container()
        col1, col2, col3 = container.columns([1, 2, 1])  # proporções ajustadas

        setores = ["Enfermagem", "UTI", "Centro Cirúrgico", "Farmácia", "Consultórios","Limpeza"]
        if "setor_selecionado" not in st.session_state:
            st.session_state.setor_selecionado = setores[0]

        with col2:
            if st.session_state.get("show_confirm_box", False):
                st.warning("Deseja realmente registrar os insumos?")
                insumos = st.session_state.insumos_confirmacao
                setor = st.session_state.setor_confirmacao
                st.write("<b>Insumos a serem registrados:</b>", unsafe_allow_html=True)
                for nome, valor in insumos.items():
                    if valor > 0:
                        st.write(f"- {nome}: {valor}")
                st.write(f"<b>Setor:</b> {setor}", unsafe_allow_html=True)
                col_confirm, col_cancel = st.columns([1,1])
                confirm_clicked = col_confirm.button("Confirmar Registro")
                cancel_clicked = col_cancel.button("Cancelar")
                if confirm_clicked:
                    data = datetime.now().strftime("%d/%m/%Y")
                    hora = datetime.now().strftime("%H:%M:%S")
                    for insumo, valor in insumos.items():
                        if valor > 0:
                            tabela.loc[len(tabela)] = [str(usuario), insumo, valor, str(setor), hora, data]
                    tabela.to_excel("banco_dasa.xlsx", index=False)
                    st.success("Registros salvos com sucesso!")
                    for chave in ["valor_seringa", "valor_algodao","valor_gazes","valor_luvas"]:
                        st.session_state[chave] = 0
                    st.session_state.show_confirm_box = False
                    del st.session_state.insumos_confirmacao
                    del st.session_state.setor_confirmacao
                    st.rerun()
                elif cancel_clicked:
                    # Restaura os valores nos inputs
                    st.session_state.valor_seringa = insumos["seringa"]
                    st.session_state.valor_algodao = insumos["algodão"]
                    st.session_state.valor_gazes = insumos["gazes"]
                    st.session_state.valor_luvas = insumos["luvas"]
                    st.session_state.setor_selecionado = setor
                    st.session_state.show_confirm_box = False
                    del st.session_state.insumos_confirmacao
                    del st.session_state.setor_confirmacao
                    st.rerun()
            else:
                st.markdown("----------------------------------------------")
                st.subheader("Menu de Insumos")
                st.number_input("SERINGA", key="valor_seringa", step=1, format="%d")
                st.number_input("ALGODÃO", key="valor_algodao", step=1, format="%d")
                st.number_input("GAZES", key="valor_gazes", step=1, format="%d")
                st.number_input("LUVAS", key="valor_luvas", step=1, format="%d")
                setor_selecionado = st.selectbox("Selecione o setor", setores, index=setores.index(st.session_state.setor_selecionado))
                registrar_clicked = st.button("Registrar")
                if registrar_clicked:
                    st.session_state.insumos_confirmacao = {
                        "seringa": st.session_state.valor_seringa,
                        "algodão": st.session_state.valor_algodao,
                        "gazes": st.session_state.valor_gazes,
                        "luvas": st.session_state.valor_luvas
                    }
                    st.session_state.setor_confirmacao = setor_selecionado
                    st.session_state.setor_selecionado = setor_selecionado
                    st.session_state.show_confirm_box = True
                    st.rerun()
                st.markdown("----------------------------------------------")
                if acesso == 0 and st.button("Sair"):
                    st.session_state.usuario_logado = False
                    st.session_state.nome_usuario = None
                    st.rerun()
