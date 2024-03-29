import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import io
import plotly.graph_objects as go

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

# Função para importar a base de dados
def importar_base():
    bd = pd.read_excel('BD_empregabilidade.xlsx')
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

if check_password():
    st.set_page_config(layout="wide")

    # Carregue a base de dados
    bd = importar_base()
    filtered_data = bd

    # Título
    st.title('Análise empregabilidade')

    # Título lateral
    st.sidebar.title('O que deseja ver?')

    # Filtro do que aparece na página
    pagina = st.sidebar.radio('Selecione o que deseja ver:', ['Gráfico', 'Dataframe'], index=0)
    st.sidebar.title('Filtros')

    # Filtros selecionados
    aluno_meta = st.sidebar.radio('Selecione a opção de meta:', ['Estão na meta', 'Não estão na meta', 'Ambas'], index=2)
    ano_termino = st.sidebar.radio('Selecione o ano de término:', ['Alunos que estão no último ano', 'Alunos que estão no penúltimo ano', 'Todos os anos'], index=2)
    oportunidade = st.sidebar.multiselect('Selecione a opção de status da oportunidade:', bd['Status meta'].unique(), default=bd['Status meta'].unique())

    # Define todas as opções possíveis para o filtro de tipos de oportunidade
    todas_opcoes = bd['Tipo de oportunidade'].unique()

    # Inicializa selected_groups com todas as opções
    selected_groups = todas_opcoes

    # Cria um espaço reservado para o filtro selected_groups
    placeholder_selected_groups = st.sidebar.empty()

    # Condição para mostrar ou "ocultar" o filtro selected_groups
    if "Oportunidade Não Validada" in oportunidade or "Oportunidade Validada" in oportunidade:
        # Mostra o filtro e atualiza selected_groups com a seleção do usuário
        selected_groups = placeholder_selected_groups.multiselect(
            'Selecione o(s) tipo(s) de oportunidade:', 
            todas_opcoes, 
            default=todas_opcoes
        )
    else:
        # "Oculta" o filtro mantendo selected_groups com todas as opções
        placeholder_selected_groups.empty()
        selected_groups = todas_opcoes

    selected_status = st.sidebar.multiselect('Selecione o(s) status:', bd['Status'].unique(), default=bd['Status'].unique())

    # Aplicar filtro com base na opção do aluno_meta
    if aluno_meta == 'Estão na meta':
        filtered_data = filtered_data[filtered_data['Classificação_Meta'] == 'Meta']
    elif aluno_meta == 'Não estão na meta':
        filtered_data = filtered_data[filtered_data['Classificação_Meta'] != 'Meta']

    # Aplicar filtro com base na opção do ano_termino
    if ano_termino == 'Alunos que estão no último ano':
        filtered_data = filtered_data[filtered_data['Ano_termino'] == 2023]
    elif ano_termino == 'Alunos que estão no pnúltimo ano':
        filtered_data = filtered_data[filtered_data['Ano_termino'] == 2024]

    # Aplicar filtro com base nas outras seleções
    filtered_data = filtered_data[
        (filtered_data['Tipo de oportunidade'].isin(selected_groups)) &
        (filtered_data['Status'].isin(selected_status)) &
        (filtered_data['Status meta'].isin(oportunidade))
    ]

    #Filtro boxplot
    setores_desejados = ['1º Setor (Público)', '2º Setor (Privado)', '3º Setor (Sem fins lucrativos)']
    filtered_data_boxPlot = filtered_data[filtered_data['Setor'].isin(setores_desejados)].sort_values('Setor')

    #Cores
    cores_setor = {
    '1º Setor (Público)': '#00BDF2',
    '2º Setor (Privado)': '#008ED4',
    '3º Setor (Sem fins lucrativos)': '#002561',
    '-': 'Red',
    '2.5º setor':'Red'
}

    # Contagem de ocorrências de cada setor
    setor_counts = filtered_data_boxPlot['Setor'].value_counts().reset_index()
    setor_counts.columns = ['Setor', 'Quantidade']

    # Criar um gráfico de pizza
    pizza = px.pie(setor_counts, names='Setor', values='Quantidade')
    pizza.update_traces(marker=dict(colors=[cores_setor[setor] for setor in setor_counts['Setor']]))
    pizza.update_traces(textfont=dict(color='white'))


    # Personalizar o layout do gráfico de pizza
    pizza.update_layout(
        showlegend=True,  # Mostrar legendaa
        legend=dict(  # Personalizar a legenda
            title='',  # Título da legenda
            font=dict(size=22, color="Gray"),  # Tamanho da fonte da legenda
        ),
        font=dict(size=20, color='white'),  # Tamanho da fonte do gráfico
        height=400,  # Defina a altura desejada
    )   

    # Contagem de ocorrências de cada setor
    setor_counts = filtered_data['Turno'].value_counts().reset_index()
    setor_counts.columns = ['Turno', 'Quantidade']

    # Cria segundo Gráfico de pizza
    pizza2 = px.pie(setor_counts, names='Turno', values='Quantidade', color_discrete_sequence=['#002561', '#008ED4'])

    # Personalizar o layout do gráfico de pizza
    pizza2.update_layout(
        showlegend=True,  # Mostrar legenda
        legend=dict(  # Personalizar a legenda
            title='',  # Título da legenda
            font=dict(size=22, color="Gray"),  # Tamanho da fonte da legenda
        ),
        font=dict(size=20, color='white'),  # Tamanho da fonte do gráfico
        height=400,  # Defina a altura desejada
    )

    pizza2.update_traces(textfont=dict(color='white'))
 
# Criar um boxplot interativo com os dados filtrados usando Plotly
    # Filtro para identificar os pontos que devem ser destacados
    pontos_destacados = filtered_data_boxPlot[filtered_data_boxPlot['Top_empresa'] == 'Sim']
    filtered_data_boxPlot = filtered_data_boxPlot[filtered_data_boxPlot['Top_empresa'] == 'Não']

    # Crie um boxplot interativo com os dados filtrados usando Plotly
    boxplot = go.Figure()

    for setor, data in filtered_data_boxPlot.groupby('Setor'):
        boxplot.add_trace(
            go.Box(
                y=data['Remuneração'],
                name=setor,
                boxpoints='all',
                jitter=0.7,
                pointpos=-2,
                marker_color=cores_setor[setor],
                customdata=data[['Nome', 'Curso', 'Universidade', 'Tipo de oportunidade', 'Organizacao', 'Status meta', 'Status']],
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
        )

    # Adicione os pontos destacados ao boxplot
    boxplot.add_trace(
        go.Box(
            y=pontos_destacados['Remuneração'],
            boxpoints='all',
            jitter=0.7,
            pointpos=-2,
            marker_color='#F2665E',
            customdata=pontos_destacados[['Nome', 'Curso', 'Universidade', 'Tipo de oportunidade', 'Organizacao', 'Status meta', 'Status']],
            hovertemplate='<b>Remuneração:</b> %{y}' +
                            '<br><b>Nome do aluno:</b> %{customdata[0]}' +
                            '<br><b>Curso:</b> %{customdata[1]}' +
                            '<br><b>Universidade:</b> %{customdata[2]}' +
                            '<br><b>Tipo de oportunidade:</b> %{customdata[3]}' +
                            '<br><b>Organização:</b> %{customdata[4]}' +
                            '<br><b>Status meta:</b> %{customdata[5]}' +
                            '<br><b>Status:</b> %{customdata[6]}',
            name='Top Empresas'  # Defina o nome desejado para a legenda x
        )
    )

    # Atualize o layout do boxplot
    boxplot.update_layout(
        height=600,
        xaxis_title='',
        yaxis_title='Remuneração',
        boxmode='overlay',
        showlegend=False,
        yaxis=dict(
            tickfont=dict(
                size=16  # Defina o tamanho da fonte desejado
            )
        ),
        xaxis=dict(
        tickfont=dict(
            size=16  # Defina o tamanho da fonte desejado
            )
        )
    )

    # Defina seus próprios valores para as marcas (ticks) no eixo y
    boxplot.update_yaxes(tickvals=[1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000])

# Filtrar os dados para pegar os anos 2023 e 2024
    meta_counts = filtered_data[filtered_data['Ano_termino'].isin([2023, 2024])]

    # Criar um DataFrame com a contagem dos anos
    meta_counts = meta_counts['Ano_termino'].value_counts().reset_index()
    meta_counts.columns = ['Ano_termino', 'Quantidade']

    # Mapear os valores da coluna 'Ano_termino' para rótulos personalizados
    ano_labels = {2023: 'Penúltimo ano', 2024: 'Último ano'}
    meta_counts['Ano_termino'] = meta_counts['Ano_termino'].map(ano_labels)

    # Cria o gráfico de pizza para os anos 2023 e 2024
    pizza3 = px.pie(meta_counts, names='Ano_termino', values='Quantidade', color_discrete_sequence=['#002561', '#008ED4'])

    # Personalizar o layout do gráfico de pizza
    pizza3.update_layout(
        showlegend=True,  # Mostrar legenda
        legend=dict(  # Personalizar a legenda
            title='',  # Título da legenda
            font=dict(size=22, color="Gray"),  # Tamanho da fonte da legenda
        ),
        font=dict(size=20, color='white'),  # Tamanho da fonte do gráfico
        height=400,  # Defina a altura desejada
    )

    pizza3.update_traces(textfont=dict(color='white'))

# Contagem de ocorrências de cada universidade
    universidade_counts = filtered_data['Universidade'].value_counts().reset_index()
    universidade_counts.columns = ['Universidade', 'Quantidade']

    # Classificar as universidades em ordem decrescente de contagem
    universidade_counts = universidade_counts.sort_values(by='Quantidade', ascending=False)

    # Selecionar as 10 principais universidades
    top_10_universidades = universidade_counts.head(10)

    # Criar o gráfico de barras
    bar_chart_universidades = px.bar(top_10_universidades, x='Universidade', y='Quantidade', color_discrete_sequence=['#002561'])

    # Personalizar o layout do gráfico de barras
    bar_chart_universidades.update_layout(
    xaxis_title='',
    yaxis_title='',
    title='',
    xaxis=dict(
        tickfont=dict(
            size=16  # Defina o tamanho da fonte desejado
            )
        ),
    height=600
    )

    bar_chart_universidades.update_traces(
    texttemplate='%{y}', 
    textposition='outside',
    textfont=dict(size=16)  # Defina o tamanho da fonte desejado
    )

    bar_chart_universidades.update_traces(texttemplate='%{y}', textposition='outside')
    bar_chart_universidades.update_yaxes(showticklabels=False, showgrid=False)
    
# Contagem de ocorrências de cada curso
    curso_counts = filtered_data['Curso'].value_counts().reset_index()
    curso_counts.columns = ['Curso', 'Quantidade']

    # Classificar os cursos em ordem decrescente de contagem
    curso_counts = curso_counts.sort_values(by='Quantidade', ascending=False)

    # Selecionar os 10 principais cursos
    top_10_cursos = curso_counts.head(10)

    # Criar o gráfico de barras
    bar_chart_cursos = px.bar(top_10_cursos, x='Curso', y='Quantidade', color_discrete_sequence=['#002561'])

    # Personalizar o layout do gráfico de barras
    bar_chart_cursos.update_layout(
    xaxis_title='',
    yaxis_title='',
    title='',
    xaxis=dict(
        tickfont=dict(
            size=16  # Defina o tamanho da fonte desejado
        )
    ),
    height=600
)
    bar_chart_cursos.update_traces(
    texttemplate='%{y}', 
    textposition='outside',
    textfont=dict(size=16)  # Defina o tamanho da fonte desejado
)

    bar_chart_cursos.update_traces(texttemplate='%{y}', textposition='outside')
    bar_chart_cursos.update_yaxes(showticklabels=False, showgrid=False)

    # Contagem de ocorrências de cada cidade
    cidades_counts = filtered_data['Cidade'].value_counts().reset_index()
    cidades_counts.columns = ['Cidade', 'Quantidade']

    # Classificar as cidades em ordem decrescente de contagem
    cidades_counts = cidades_counts.sort_values(by='Quantidade', ascending=False)

    # Selecionar as 10 principais cidades
    top_10_cidades = cidades_counts.head(10)

    # Criar o gráfico de barras
    bar_chart_cidades = px.bar(top_10_cidades, x='Cidade', y='Quantidade', color_discrete_sequence=['#002561'])

    # Personalizar o layout do gráfico de barras
    bar_chart_cidades.update_layout(
        xaxis_title='',  # Defina o título do eixo X, se necessário
        yaxis_title='',  # Defina o título do eixo Y, se necessário
        title='',  # Defina o título principal, se necessário
        xaxis=dict(tickfont=dict(size=16)),  # Tamanho da fonte do eixo X
        height=600  # Altura do gráfico
    )

    # Atualizar traces para exibir valores fora das barras
    bar_chart_cidades.update_traces(
        texttemplate='%{y}', 
        textposition='outside',
        textfont=dict(size=16)  # Tamanho da fonte dos valores
    )

    # Ocultar as etiquetas do eixo Y e a grade
    bar_chart_cidades.update_yaxes(showticklabels=False, showgrid=False)

    # Criar um DataFrame com a contagem de ocorrências das cidades
    cidade_counts = filtered_data['Cidade'].value_counts().reset_index()
    cidade_counts.columns = ['Cidade', 'Quantidade']

    # Classificar as cidades em ordem decrescente de contagem
    cidade_counts = cidade_counts.sort_values(by='Quantidade', ascending=False)

    # Filtrar as cidades de "São Paulo" e "Rio de Janeiro"
    sp_rio_cidades = cidade_counts[cidade_counts['Cidade'].isin(['São Paulo', 'Rio de Janeiro'])]

    # Calcular a contagem total de outras cidades
    outras_cidades_count = cidade_counts[~cidade_counts['Cidade'].isin(['São Paulo', 'Rio de Janeiro'])]['Quantidade'].sum()

    # Criar um DataFrame para "Outros"
    outros_cidades = pd.DataFrame({'Cidade': ['Outros'], 'Quantidade': [outras_cidades_count]})

    # Concatenar os DataFrames de "São Paulo", "Rio de Janeiro" e "Outros"
    cidade_counts_final = pd.concat([sp_rio_cidades, outros_cidades])

    # Criar o gráfico de pizza
    pie_chart_cidades = px.pie(cidade_counts_final, names='Cidade', values='Quantidade', color_discrete_sequence=['#002561', '#008ED4', '#00BDF2'])

    # Personalizar o layout do gráfico de pizza
    pie_chart_cidades.update_layout(
        showlegend=True,
        legend=dict(
            title='',
            font=dict(size=22, color="Gray"),
        ),
        font=dict(size=20, color='white'),
        height=400,
    )

    # Personalizar as porcentagens
    pie_chart_cidades.update_traces(
        textposition='inside',
        textinfo='percent',
        insidetextfont=dict(color='white', size=20),  # Defina o tamanho e a cor da fonte interna
    )

    # Personalizar as porcentagens
    pie_chart_cidades.update_traces(
        textposition='inside',
        textinfo='percent',
        insidetextfont=dict(color='white', size=20),  # Defina o tamanho e a cor da fonte interna
    )
   

# Criar um DataFrame com a contagem de ocorrências de Gênero
    genero_counts = filtered_data['Gênero'].value_counts().reset_index()
    genero_counts.columns = ['Gênero', 'Quantidade']

    # Classificar as cidades em ordem decrescente de contagem
    genero_counts = genero_counts.sort_values(by='Quantidade', ascending=False)

    # Filtrar as cidades de "São Paulo" e "Rio de Janeiro"
    f_m = genero_counts[genero_counts['Gênero'].isin(['Feminino', 'Masculino'])]

    # Calcular a contagem total de outras cidades
    outras_generos_count = genero_counts[~genero_counts['Gênero'].isin(['Feminino', 'Masculino'])]['Quantidade'].sum()

    # Criar um DataFrame para "Outros"
    outros_generos = pd.DataFrame({'Gênero': ['Outros'], 'Quantidade': [outras_generos_count]})

    # Concatenar os DataFrames de "São Paulo", "Rio de Janeiro" e "Outros"
    generos_counts_final = pd.concat([f_m, outros_generos])

    # Criar o gráfico de pizza
    pie_chart_generos = px.pie(generos_counts_final, names='Gênero', values='Quantidade', color_discrete_sequence=['#002561', '#008ED4', '#00BDF2'])

    # Personalizar o layout do gráfico de pizza
    pie_chart_generos.update_layout(
        showlegend=True,  # Mostrar legenda
        legend=dict(  # Personalizar a legenda
            title='',  # Título da legenda
            font=dict(size=22, color="Gray"),  # Tamanho da fonte da legenda
        ),
        font=dict(size=20, color='white'),  # Tamanho da fonte do gráfico
        height=400,  # Defina a altura desejada
    )

# Contagem de ocorrências de cada raça
    status_conts = filtered_data['Status meta'].value_counts().reset_index()
    status_conts.columns = ['Status meta', 'Quantidade']

    # Criar um gráfico de pizza
    pie_chart_status = px.pie(status_conts, names='Status meta', values='Quantidade', color_discrete_sequence=['#002561', '#008ED4', '#00BDF2'])

    # Personalizar o layout do gráfico de pizza
    pie_chart_status.update_layout(
        showlegend=True,  # Mostrar legenda
        legend=dict(  # Personalizar a legenda
            title='',  # Título da legenda
            font=dict(size=22, color="Gray"),  # Tamanho da fonte da legenda
        ),
        font=dict(size=20, color='white'),  # Tamanho da fonte do gráfico
        height=400,  # Defina a altura desejada
    )

    pie_chart_status.update_traces(textfont=dict(color='white'))

# Contagem de ocorrências de cada raça
    cursoapoiado_conts = filtered_data['Curso apoiado?'].value_counts().reset_index()
    cursoapoiado_conts.columns = ['Curso apoiado?', 'Quantidade']

    # Criar um gráfico de pizza
    pie_chart_cursoapoiado = px.pie(cursoapoiado_conts, names='Curso apoiado?', values='Quantidade', color_discrete_sequence=['#002561', '#008ED4', '#00BDF2'])

    # Personalizar o layout do gráfico de pizza
    pie_chart_cursoapoiado.update_layout(
        showlegend=True,  # Mostrar legenda
        legend=dict(  # Personalizar a legenda
            title='',  # Título da legenda
            font=dict(size=22, color="Gray"),  # Tamanho da fonte da legenda
        ),
        font=dict(size=20, color='white'),  # Tamanho da fonte do gráfica
        height=400,  # Defina a altura desejada
    )

    pie_chart_cursoapoiado.update_traces(textfont=dict(color='white'))

    # Contagem de ocorrências de cada raça
    raca_counts = filtered_data['Raça'].value_counts().reset_index()
    raca_counts.columns = ['Raça', 'Quantidade']

    # Criar um gráfico de pizza
    pizza_raca = px.pie(raca_counts, names='Raça', values='Quantidade', color_discrete_sequence=['#002561', '#008ED4', '#00BDF2'])

    # Personalizar o layout do gráfico de pizza
    pizza_raca.update_layout(
        showlegend=True,  # Mostrar legenda
        legend=dict(  # Personalizar a legenda
            title='',  # Título da legenda
            font=dict(size=22, color="Gray"),  # Tamanho da fonte da legenda
        ),
        font=dict(size=20, color='white'),  # Tamanho da fonte do gráfico
        height=400,  # Defina a altura desejada
    )

    pizza_raca.update_traces(textfont=dict(color='white'))


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
            st.markdown('**05/01/2024**')

    else:
        # Exibir o boxplot no topo
        st.title('Setores')
        st.plotly_chart(boxplot, use_container_width=True)

        # Criar colunas para os gráficos de pizza
        col1, col2 = st.columns(2)

        # Exibir o segundo gráfico de pizza na coluna 1
        with col1:
            st.title('alunos por Turno')
            st.plotly_chart(pizza2, use_container_width=True)

        # Exibir o terceiro gráfico de pizza na coluna 2
        with col2:
            st.title('Alunos da meta')
            st.plotly_chart(pizza3, use_container_width=True)

        with col1:
            # Exibir o primeiro gráfico de pizza
            st.title('alunos por setor')
            st.plotly_chart(pizza, use_container_width=True)
        with col2:
            # Exibir o gráfico de pizza
            st.title('Cidades')
            st.plotly_chart(pie_chart_cidades, use_container_width=True)

        # Exibir o primeiro gráfico de barras 
        st.title('Top Universidades (Quantidade de alunos)')
        st.plotly_chart(bar_chart_universidades, use_container_width=True)

        # Exibir o segundo gráfico de barras
        st.title('Top Cursos (Quantidade de alunos)')
        st.plotly_chart(bar_chart_cursos, use_container_width=True)

        st.title('Top Cidades (Quantidade de alunos)')
        st.plotly_chart(bar_chart_cidades, use_container_width=True) 

        with col1:
            st.title('Gêneros')
            st.plotly_chart(pie_chart_generos , use_container_width=True)

        with col2:
            st.title('Raça')
            st.plotly_chart(pizza_raca , use_container_width=True)
        
        with col1:
            st.title('Status meta')
            st.plotly_chart(pie_chart_status , use_container_width=True)

        with col2:
            st.title('Curso apoiado?')
            st.plotly_chart(pie_chart_cursoapoiado , use_container_width=True)
            
