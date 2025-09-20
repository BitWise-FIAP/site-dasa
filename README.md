# site-dasa

Este projeto é uma aplicação desenvolvida para facilitar o controle de insumos hospitalares, permitindo que funcionários insiram dados de maneira simples e prática, enquanto gestores podem visualizar e manipular essas informações em tempo real. O sistema utiliza Python e Streamlit.

## Objetivo
O objetivo principal do projeto é permitir que funcionários insiram dados sobre o controle de insumos hospitalares de forma simples, prática e segura, enquanto gestores têm acesso em tempo real para visualizar, analisar e manipular essas informações, facilitando a tomada de decisão, previsão e gestão dos insumos.

## Funcionalidades
 - **Inserção de Dados de Insumos**: Funcionários podem inserir dados sobre o controle de insumos hospitalares de forma prática.
 - **Visualização e Manipulação de Dados**: Gestores podem visualizar e manipular os dados inseridos, facilitando a gestão e tomada de decisão.
 - **Controle de Nível de Acesso**: O sistema de usuários serve exclusivamente para definir permissões: funcionários têm acesso apenas à inserção de dados, enquanto gestores podem visualizar e manipular as informações.
 - **Interface Gráfica**: Utiliza Streamlit para criar uma interface web interativa e fácil de usar.
 - **Recursos Visuais**: Inclui ícones personalizados localizados na pasta `assets/icons` para melhorar a experiência do usuário.

## Como executar
1. Instale as dependências listadas em `requirements.txt`.
2. Execute o arquivo `app.py` utilizando o Streamlit:
   ```powershell
   streamlit run app.py
   ```
3. Acesse a interface web pelo navegador para utilizar as funcionalidades.

## Estrutura do Projeto
 - `app.py`: Código principal da aplicação.
 - `banco_dasa.xlsx`: Base de dados dos insumos hospitalares.
 - `users.json`: Controle de usuários para definir nível de acesso (funcionário ou gestor).
 - `assets/icons/`: Ícones utilizados na interface.
 - `requirements.txt`: Dependências do projeto.

## Requisitos
- Python 3.7+
- Streamlit
- Pandas

## Conclusão
O principal objetivo do projeto é permitir que funcionários insiram dados sobre o controle de insumos hospitalares de maneira simples e prática, enquanto gestores podem visualizar e manipular essas informações em tempo real. O controle de usuários garante que cada perfil tenha acesso apenas às funcionalidades adequadas, tornando o processo de gestão mais eficiente, transparente e seguro para todos os envolvidos.

## Autor
BitWise-FIAP

---
Este projeto é destinado para fins acadêmicos e demonstração de funcionalidades de visualização e manipulação de dados.