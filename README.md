# Análise de Desempenho do G13 contra o Z4 (2015–2025)

Aplicação em Python que utiliza Playwright para coletar dados do SofaScore e analisar o desempenho de times do G13 contra equipes da zona de rebaixamento (Z4) do Campeonato Brasileiro entre 2015 e 2025.

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
playwright install
```

<br>
<br>

# Como executar
### Na raiz do projeto:
```txt
py app/main.py
```

<br>
<br>

# Configuração
### O time analisado pode ser alterado no arquivo:
```txt
app/config.py
```
Exemplo:
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