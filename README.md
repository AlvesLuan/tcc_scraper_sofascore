# Análise de Desempenho do C13 contra o diferentes adversarios (2015–2025)

Aplicação em Python que utiliza Playwright para coletar dados do SofaScore e analisar o desempenho de times do Clube dos 13(C13) contra diferentes equipes do Campeonato Brasileiro, análise feita no período de 2015 a 2025.

---

<br>

# Funcionalidades

- Coleta automática de dados do SofaScore
- Identificação dos times do Z4 de cada temporada
- Filtragem apenas de partidas do Brasileirão Série A
- Cálculo de:
  - vitórias
  - empates
  - derrotas
  - total de partidas contra o Z4
  - total de pontos perdidos contra o z4
  - media de pontos perdidos por jogo
  - desvio padrao dos pontos perdidos
- Exportação dos resultados para CSV

---
<br>

# Tecnologias utilizadas

- Python
- Playwright

---
<br>

# Estrutura do projeto

```txt
tcc_g13_stats/
│
├── app/
│   ├── analysis.py
│   ├── config.py
│   ├── main.py
│   ├── main_detalhado_geral.py
|   ├── main_detalhado.py
│   └── scraper.py
│
├── data/
│   └── exports/
│
├── .gitignore
├── README.md
└── requirements.txt
```
<br>

# Instalação
## 1. Clone o repositório
```txt
git clone <link-aqui>
```

## 2. Entre na pasta do projeto
```txt
cd tcc_scraper_sofascore
```

## 3. Crie o ambiente virtual
```txt
py -m venv .venv
```

## 4. Ative o ambiente virtual pelo terminal
```txt
.\.venv\Scripts\Activate.ps1
```

## 5. Instale as dependências
```txt
pip install -r requirements.txt
```

## 6. Instale os navegadores do Playwright
```txt
py -m playwright install chromium
```

<br>
<br>

# Como executar
### Na raiz do projeto:
```txt
py app/main.py
#para a tabela geral.

py app/main_detalhado.py   
#para a tabela com detalhes das partidas contra o z4.

py app/main_detalhado_geral.py   
#para a tabela com detalhes de TODAS as partidas no período, ATENÇÃO, a execução demorará mais.
```

<br>
<br>

# Configuração
### O time analisado pode ser alterado no arquivo:
```txt
app/config.py
```
### Basta descomentar o time desejado.
### Exemplo:
```txt
TIME_ALVO = ("Atlético Mineiro",1977)
```
Também é possível alterar:
- temporadas analisadas;
- delay entre requisições;
- caminho do CSV de saída;

# Saída
### Os resultados são salvos em:
```txt
data/exports/resultados_c13.csv
data/exports/detalhados_c13.csv
data/exports/detalhados_c13_geral.csv
```

<br>
<br>
<br>
<br>

# Objetivo acadêmico
### Este projeto foi desenvolvido como parte de um Trabalho de Conclusão de Curso (TCC) de Sistemas de Informação, com foco em:

- web scraping
- análise de dados esportivos
- automação com Playwright
- processamento de estatísticas do futebol brasileiro
