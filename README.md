# Investigação do impacto do nível do adversário no desempenho de equipes do futebol brasileiro (2015–2025)

Aplicação em Python que coleta dados do Sofascore e do FBref e analisa o desempenho dos clubes do Clube dos 13 (C13) no Campeonato Brasileiro Série A entre 2015 e 2025, com foco nos jogos contra os quatro times que terminaram cada temporada na zona de rebaixamento (Z4). Os resultados são interpretados com árvores de decisão (*scikit-learn*) como **associações**, e não como relações de causa e efeito.

Este repositório acompanha o artigo *"O desempenho dos times do Clube dos 13 contra equipes que foram rebaixadas no Campeonato Brasileiro: uma análise baseada em dados"*.

---

<br>

# Funcionalidades

- Coleta automática de dados do Sofascore (resultados, escalações, árbitro, estádio etc.)
- Extração offline do público presente a partir de páginas salvas do FBref
- Identificação dos times do Z4 de cada temporada
- Filtragem apenas de partidas do Brasileirão Série A
- Base agregada por clube (jogos contra o Z4), com:
  - vitórias, empates e derrotas;
  - total de partidas contra o Z4;
  - total de pontos perdidos;
  - aproveitamento;
  - média de pontos perdidos por jogo;
  - desvio padrão da média de pontos perdidos por jogo entre as temporadas.
- Base detalhada, com uma linha por partida do ponto de vista de cada clube do C13, incluindo médias e desvios padrão de idade e altura dos titulares dos dois times
- Exportação de todos os resultados para CSV

---
<br>

# Tecnologias utilizadas

- Python
- Playwright (e Patchright) para automação do navegador
- BeautifulSoup para leitura das páginas HTML do FBref
- pandas para limpeza e organização dos dados
- scikit-learn para as árvores de decisão
- matplotlib para as figuras

---
<br>

# Estrutura do projeto

```txt
tcc_g13_stats/
│
├── app/
│   ├── analysis.py
│   ├── config.py
│   ├── fbref-extrator-offline.py
│   ├── main_detalhado_geral.py
│   ├── main_detalhado_vs_z4.py
│   ├── main.py
│   └── scraper.py
│
├── data/
│   ├── exports/
│   │   ├── base_detalhada_geral.csv
│   │   ├── base_detalhada_geral_publico.csv
│   │   ├── base_detalhada_geral_vs_z4.csv
│   │   └── resultados_c13.csv
│   └── fbref-pages-html/
│       └── páginas do FBref (HTML salvo)
│
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

<br>

# Instalação

## 1. Clone o repositório
```txt
git clone https://github.com/AlvesLuan/tcc_scraper_sofascore
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

# Como executar

> A coleta pode levar horas. Recomenda-se rodar **um time por vez**.

## 1. Configuração

O time e as temporadas analisados são definidos em:

```txt
app/config.py
```

Basta descomentar os times e as temporadas desejados.

Exemplo:
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
Nesse exemplo rodariam apenas Atlético Mineiro e Vasco da Gama, nas temporadas de 2018 e 2019. É preciso deixar pelo menos um time e uma temporada descomentados.

Também é possível alterar:
- as temporadas analisadas;
- o intervalo entre as requisições (**não diminua**: o Sofascore chegou a bloquear o IP de máquinas que usaram intervalos curtos; no artigo foram usados 10 segundos);
- o caminho do CSV de saída.

## 2. Base agregada (jogos contra o Z4)

```txt
py app/main.py
```

## 3. Base detalhada (todas as partidas)

> **Atenção:** a execução demora mais.

```txt
py app/main_detalhado_geral.py
```

Ou, para apenas as partidas contra o Z4:

```txt
py app/main_detalhado_vs_z4.py
```

Esses comandos geram o arquivo `base_detalhada_geral.csv`, **sem** a coluna de público.

## 4. Adicionar o público (FBref)

Com a base detalhada já criada, rode:

```txt
py app/fbref-extrator-offline.py
```

Isso gera o arquivo `base_detalhada_geral_publico.csv`, com a coluna `publico`. Na pasta `data/fbref-pages-html` já estão as páginas HTML do FBref, então **não é necessária nenhuma coleta manual ou automática** nessa etapa (o FBref é restritivo com extração automática de dados).

<br>
<br>

# Saída

Os resultados são salvos em `data/exports/`:

| Arquivo | Conteúdo |
|---|---|
| `resultados_c13.csv` | Base agregada: desempenho de cada clube do C13 contra os times do Z4 |
| `base_detalhada_geral.csv` | Uma linha por partida (do ponto de vista de cada clube), sem o público |
| `base_detalhada_geral_publico.csv` | Igual à anterior, com a coluna `publico` (base usada nas árvores) |
| `base_detalhada_geral_vs_z4.csv` | Base detalhada apenas das partidas contra o Z4 |

### Colunas da base detalhada

`time`, `temporada`, `rodada`, `data`, `horario`, `dia_semana`, `mes`, `adversario`, `resultado`, `gols_favor`, `gols_sofridos`, `condicao`, `arbitro`, `idade_media_titular_time`, `desvio_idade_media_time`, `altura_media_titular_time`, `desvio_altura_media_time`, `idade_media_titular_adv`, `desvio_idade_media_adv`, `altura_media_titular_adv`, `desvio_altura_media_adv`, `estadio`, `publico`.

Observações sobre os dados:
- Quando dois clubes do C13 se enfrentam, o jogo aparece em **duas linhas** (uma para cada clube). Por isso os 4.898 registros correspondem a 3.498 partidas únicas.
- No CSV, idade, altura e público estão como texto (vírgula decimal e separador de milhar). A conversão para número é feita no pré-processamento descrito no artigo.

<br>

# Aviso sobre os dados

Os dados foram coletados do **Sofascore** e do **FBref** exclusivamente para fins acadêmicos. A licença deste repositório cobre apenas o **código**; os dados continuam sujeitos aos termos e direitos das fontes originais. Quem for reutilizar os dados deve consultar os termos de uso dessas plataformas.

<br>

# Licença

O código está sob a licença [MIT](LICENSE).

<br>

# Objetivo acadêmico

Este projeto foi desenvolvido como parte de um Trabalho de Conclusão de Curso (TCC) de Sistemas de Informação, com foco em:

- Web scraping
- Análise de dados esportivos
- Automação com Playwright
- Inteligência estatística do futebol brasileiro
- Mineração de dados e aprendizado de máquina com árvore de decisão

<br>

## **Informações para contato**
+ luankauan10@gmail.com
+ **[LinkedIn](https://www.linkedin.com/in/luan-kauan-santos-31b057239/)**

<h6 align="right"> qualquer dúvida manda uma msg, eu sempre olho os emails ;) </h6>
