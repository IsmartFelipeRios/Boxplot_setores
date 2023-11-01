import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import io

def check_password():
    """Returns `True` if the user had a correct password."""
 
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if (
            st.session_state["username"] in st.secrets["passwords"]
            and st.session_state["password"]
            == st.secrets["passwords"][st.session_state["username"]]
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store username + password
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False
 
    if "password_correct" not in st.session_state:
        # First run, show inputs for username + password.
        st.text_input("Usuário", on_change=password_entered, key="username")
        st.text_input(
            "Senha", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input("Usuário", on_change=password_entered, key="username")
        st.text_input(
            "Senha", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Usuário desconhecido ou senha incorreta.")
        return False
    else:
        # Password correct.
        return True
 
if check_password():
    # Função para importar a base de dados
    def importar_base():
        bd = pd.read_excel(r'C:\ISMART\OneDrive - Ismart - Instituto Social M.A.R.T\Documentos\Python Scripts\Boxplot_comparativo_entre_os_3_setores.xlsx')
        return bd

    # Função para baixar o DataFrame em formato CSV
    def download_csv():
        csv = filtered_data.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # Converte para base64
        href = f"data:file/csv;base64,{b64}"
        st.markdown(f'<a href="{href}" download="dataframe.csv">Baixar CSV</a>', unsafe_allow_html=True)

    # Função para baixar o DataFrame em formato Excel
    def download_excel():
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as excel_writer:
            filtered_data.to_excel(excel_writer, index=False)
        excel_binary = output.getvalue()
        b64 = base64.b64encode(excel_binary).decode()
        href = f"data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}"
        st.markdown(f'<a href="{href}" download="dataframe.xlsx">Baixar Excel</a>', unsafe_allow_html=True)

    # Carregue a base de dados
    bd = importar_base()

    # Título lateral
    st.sidebar.title('Filtros')

    # Filtro do que aparece na página
    pagina = st.sidebar.radio('Selecione o que deseja ver:', ['Gráfico', 'Dataframe'], index=0)

    # Criar um filtro de seleção múltipla para o tipo de oportunidade
    selected_groups = st.sidebar.multiselect('Selecione o(s) tipo(s) de oportunidade:', bd['Tipo de oportunidade'].unique(), default=bd['Tipo de oportunidade'].unique())

    # Criar um filtro de seleção múltipla para o tipo de status
    selected_status = st.sidebar.multiselect('Selecione o(s) status:', bd['Status'].unique(), default=bd['Status'].unique())

    # Criar um filtro de rádio para a opção de meta
    aluno_meta = st.sidebar.radio('Selecione a opção de meta:', ['Estão na meta', 'Não estão na meta', 'Ambas'], index=2)

    # Criar um filtro de rádio para a opção de oportunidade
    oportunidade = st.sidebar.radio('Selecione a opção de status da oportunidade:', ['Oportunidade validada', 'Oportunidade não validada', 'Ambas'], index=2)

    # Filtrar os dados com base nos filtros selecionados
    filtered_data = bd[bd['Tipo de oportunidade'].isin(selected_groups) &
                        bd['Status'].isin(selected_status) &
                        ((aluno_meta == 'Estão na meta' and bd['Classificação_Meta'] == 'Meta') |
                            (aluno_meta == 'Não estão na meta' and bd['Classificação_Meta'] == 'Geral') |
                            (aluno_meta == 'Ambas')) &
                        ((oportunidade == 'Oportunidade validada' and bd['Status meta'] == 'Oportunidade validada') |
                            (oportunidade == 'Oportunidade não validada' and bd['Status meta'] == 'Oportunidade não validada') |
                            (oportunidade == 'Ambas'))]

    # Contagem de ocorrências de cada setor
    setor_counts = filtered_data['Setor'].value_counts().reset_index()
    setor_counts.columns = ['Setor', 'Quantidade']

    # Criar um gráfico de pizza
    pizza = px.pie(setor_counts, names='Setor', values='Quantidade')

    # Personalizar o layout do gráfico de pizza
    pizza.update_layout(
        showlegend=True,  # Mostrar legenda
        legend=dict(  # Personalizar a legenda
            title='',  # Título da legenda
            font=dict(size=18),  # Tamanho da fonte da legenda
        ),
        font=dict(size=20, color='white'),  # Tamanho da fonte do gráfico
        height=400,  # Defina a altura desejada
    )

    pizza.update_traces(textfont=dict(color='white'))

    # Criar um boxplot interativo com os dados filtrados usando Plotly
    boxplot = px.box(filtered_data, x="Setor", y="Remuneração", color="Setor", boxmode='overlay', hover_data=["Nome", "Curso", "Universidade", "Tipo de oportunidade", "Organizacao", "Status meta", "Status"])
    boxplot.update_traces(
        hovertemplate='<b>Setor:</b> %{x}' +
                        '<br><b>Remuneração:</b> %{y}' +
                        '<br><b>Nome do aluno:</b> %{customdata[0]}' +
                        '<br><b>Curso:</b> %{customdata[1]}' +
                        '<br><b>Universidade:</b> %{customdata[2]}' +
                        '<br><b>Tipo de oportunidade:</b> %{customdata[3]}'
                        '<br><b>Organização:</b> %{customdata[4]}'
                        '<br><b>Status meta:</b> %{customdata[5]}'
                        '<br><b>Status:</b> %{customdata[6]}'
    )

    boxplot.update_traces(boxpoints='all', 
                            jitter=0.7, 
                            pointpos=-2, 
                            boxmean=True,
                            showlegend=False,
                            )

    boxplot.update_layout(height=600, xaxis_title='')

    # Defina seus próprios valores para as marcas (ticks) no eixo y
    boxplot.update_yaxes(tickvals=[1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000], title="Remuneração")

    # Exibir
    if pagina == 'Dataframe':
        # Exibir o título do aplicativo
        st.title('DataFrame de empregabilidade')
        # Exibir o DataFrame dos dados
        st.dataframe(filtered_data)

        # Criar duas colunas para alinhar os botões lado a lado
        col1, col2, col3, col4, col5, col6 = st.columns(6)

        # Botões para baixar em CSV e Excel
        with col1:
            download_csv()
        with col2:
            download_excel()
        with col6:
            st.markdown('**10/10/2023**')

    else:
        # Exibir o título do aplicativo
        st.title('Boxplot setores')
        
        # Exibir o boxplot no Streamlit
        st.plotly_chart(boxplot, use_container_width=True)
        st.title('Gráfico pizza da quantidade de alunos por setor')
        st.plotly_chart(pizza, use_container_width=True)
