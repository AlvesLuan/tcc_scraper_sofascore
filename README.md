# [em desenvolvimento] Análise de Desempenho dos times do C13 contra diferentes adversários (2015–2025)

Aplicação em Python que utiliza Playwright para coletar dados do SofaScore e Fbref e analisar o desempenho de times do Clube dos 13 (C13) contra diferentes equipes do Campeonato Brasileiro, análise feita no período de 2015 a 2025.

---

<br>

# Funcionalidades

- Coleta automática de dados do SofaScore
- Identificação dos times do Z4 de cada temporada
- Filtragem apenas de partidas do Brasileirão Série A
- Cálculo de:
  - vitórias;
  - empates;
  - derrotas;
  - total de partidas contra o Z4;
  - total de pontos perdidos contra o Z4;
  - média de pontos perdidos por jogo;
  - desvio padrão dos pontos perdidos;
  - médias de alturas juntamente com desvio padrão;
  - médias de idade juntamente com desvio padrão;
  - ...
- Exportação dos resultados para CSV

---
<br>

# Tecnologias utilizadas

- Python
- Playwright
- xxxxxxxx

---
<br>

# Estrutura do projeto

```txt
tcc_g13_stats/
│
├── app/
│   ├── analysis.py
│   ├── config.py
│   ├── fbref-extrator-offline
│   ├── main_detalhado_geral.py
│   ├── main_detalhado_vs_z4.py
│   ├── main.py
│   └── scraper.py
│
├── data/
│   └── exports/
│             └── detalhado_c13_geral_publico.csv
│             └── detalhado_c13_geral.csv
│             └── resultados_c13.csv
│   └── fbref-pages-html/
│             └── páginas específicas do fbref
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
py -m playwright install firefox
```

<br>
<br>

# Como executar:
### No config.py descomente os times e as temporadas que você quer que rode, (recomendo que use 1 time por vez, a execução pode levar horas).


## 1. Configuração
### O time analisado pode ser alterado no arquivo:
```txt
app/config.py
```
### Basta descomentar os time desejados na execução e as temporadas desejadas.
### Exemplo:
```txt
TIMES_ALVO = [
    # ("Palmeiras",        1963),
    ("Vasco da Gama",    1974),
    ("Atlético Mineiro", 1977),
    # ("Cruzeiro",         1954)
]

SEASONS = {
    # 2015: 10173,
    # 2016: 11429,
    # 2017: 13100,
    2018: 16183,
    2019: 22931,
    # 2020: 27591,  # edição 20/21 (pandemia)
    # 2021: 36166,
}
```
No exemplo rodará apenas Atlético Mineiro e Vasco da Gama nas temporadas de 2028 e 2019, obviamente no mínimo um time e uma temporada deve estar descomentado.

Também é possível alterar:
- temporadas analisadas;
- delay entre requisições (recomendado deixar em 7, já ocorreu ban no IP de máquinas que usaram tempos menores);
- caminho do CSV de saída;

### Para rodar a tabela geral de dados contra o z4 rode com:
```txt
py app/main.py
```
 
### Para a tabela com detalhes de TODAS as partidas no período, ATENÇÃO, a execução demorará mais.
```txt
py app/main_detalhado_geral.py 

Ou para apenas as partidas contra o z4:

py app/main_detalhado_vs_z4.py 

```
#### Você terá um arquivo _base_detalhada_geral_publico.csv_ sem a coluna de publico. 
#### Para adicionar o publico na tabela com detalhes, rode (a tabela com detalhes deve existir):
```txt
py app/fbref-extrator-offline.py
```
Na pasta _fbref-pages-html_ eu já disponibilizei os HTML da página, então não será necessário nenhuma retirada de dados manual ou automática (o fbref é um dos maiores odiadores de extratores de dados ).

<br>
<br>



# Saída
### Os resultados são salvos em:
<br>

#### data/exports/base_detalhada_geral.csv
#### data/exports/base_detalhada_geral_publico.csv
#### data/exports/base_detalhada_geral_vs_z4.csv.csv


<br>
<br>
<br>
<br>

# Objetivo acadêmico
### Este projeto foi desenvolvido como parte de um Trabalho de Conclusão de Curso (TCC) de Sistemas de Informação, com foco em:

- Web scraping
- Análise de dados esportivos
- Automação com Playwright
- Inteligência estatística do futebol brasileiro
- Mineração de dados e aprendizado de máquina com árvore de decisão.
- Entre outros.


## **Informações para contato:**
+ ### luankauan10@gmail.com
+ ### **[LinkedIn](https://www.linkedin.com/in/luan-kauan-santos-31b057239/)**
<h6 align="right"> qualquer duvida manda uma msg, eu sempre olho os emails ;) </h6>