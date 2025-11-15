# Steam Game Scraper
Um bot em Python que busca automaticamente informações de jogos na Steam.

## 🎮 O que faz
Digite o nome de um jogo e o programa mostra:
- Preço e se está em promoção
- Avaliações dos usuários
- Data de lançamento
- Desenvolvedor e publicadora
- Gêneros, tags e idiomas
- Descrição do jogo

## 🚀 Como usar
### 1. Instale o Python (versão 3.8 ou superior)

### 2. Instale o Selenium
```bash
pip install selenium
```

### 3. Baixe o ChromeDriver
- Acesse: https://chromedriver.chromium.org/
- Baixe a versão compatível com seu Google Chrome
- Coloque o arquivo na pasta do projeto

### 4. Execute o programa
```bash
python game_scraper.py
```

### 5. Digite o nome de um jogo
Exemplo:
```
Digite o nome do jogo: Minecraft
```

## 📊 Exemplo de resultado
```
======================================
RESULTADO DA BUSCA - MINECRAFT
======================================
Preço                | R$ 89,99
Status               | Preço normal
Classificação        | Muito Positivas
Data Lançamento      | 18 Nov, 2011
Desenvolvedor        | Mojang
Publicadora          | Mojang
Gênero               | Aventura, Indie
Tags                 | Sandbox, Sobrevivência
Idiomas              | Português, Inglês
Descrição            | Construa e explore mundos...
======================================
```

## ⚙️ Tecnologias
- Python
- Selenium WebDriver
- ChromeDriver

## 📁 Arquivos
- **game_scraper.py** — Código principal
- **chromedriver.exe** — Driver do Chrome

## ❗ Problemas comuns
### ChromeDriver não encontrado
- Verifique se o arquivo está na pasta correta
- Confirme se a versão é compatível com seu Chrome

### Site não carrega
- Aumente o tempo de espera no código
- Verifique sua internet

## 🎯 Desenvolvido para
Projeto da disciplina **Automação e Programabilidade em Redes** — Demonstração de automação web com Python.