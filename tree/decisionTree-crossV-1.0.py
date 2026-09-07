import pandas as pd
from sklearn.tree import export_text, DecisionTreeClassifier, plot_tree
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_val_predict, cross_validate
from sklearn.metrics import (
    accuracy_score, balanced_accuracy_score, f1_score,
    classification_report, confusion_matrix
)
import matplotlib.pyplot as plt
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "..", "data", "exports", "z4-atletico-base_detalhada_geral_publico.csv")

print("cwd =", os.getcwd())

# =========================
# 1. Ler o CSV
# =========================
df = pd.read_csv(CSV_PATH)

# =========================
# 2. Checagem de nulos
# =========================
nulos = df.isnull().sum()
nulos = nulos[nulos > 0]
if not nulos.empty:
    print("ATENÇÃO - colunas com valores nulos:")
    print(nulos)

# =========================
# 3. Definir alvo
# =========================
y = df["resultado"]

# =========================
# 4. Remover colunas que não devem ser usadas
# =========================
X = df.drop(columns=[
    "resultado",
    "gols_favor",
    "gols_sofridos",
    "data",
    "horario",
    "desvio_idade_media_time",
    "desvio_altura_media_time",
    "desvio_idade_media_adv",
    "desvio_altura_media_adv",
    "time",
    "adversario",
    "estadio",
    "arbitro",
])

# =========================
# 4.5 Corrigir colunas numéricas que vieram como texto
# =========================
colunas_numericas = [
    "idade_media_titular_time",
    "altura_media_titular_time",
    "idade_media_titular_adv",
    "altura_media_titular_adv",
    "publico",
]

for col in colunas_numericas:
    X[col] = pd.to_numeric(X[col].astype(str).str.strip(), errors="coerce")

print("Valores não convertidos (NaN) por coluna:")
print(X[colunas_numericas].isnull().sum())

X = X.dropna(subset=colunas_numericas)
y = y.loc[X.index]

print("Registros após limpeza:", len(X))

# =========================
# 5. Converter variáveis categóricas
# =========================
X = pd.get_dummies(X, drop_first=True)
print("Atributos após get_dummies:", X.shape[1])

# =========================
# 6. Configurar validação cruzada
# =========================
# Não há mais separação fixa treino/teste (70/30). Em vez disso, a base
# inteira participa da validação cruzada: em cada uma das k rodadas, um
# pedaço diferente dos dados fica de fora para servir de teste, e ao final
# cada registro da base foi testado exatamente uma vez, sem nunca ter sido
# usado para treinar o modelo que o avaliou naquela rodada.
N_SPLITS = 10

cv = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=42)

# =========================
# 7. GridSearch para escolher os melhores hiperparâmetros
# =========================
# O GridSearchCV já usa validação cruzada internamente (cv=cv) para testar
# cada combinação de parâmetros. Aqui usamos a base inteira (X, y) em vez de
# só X_train, já que não existe mais um conjunto de teste separado.
param_grid = {
    #"criterion": ["entropy", "gini"],
    "criterion": ["entropy"],
    #"max_depth": [3, 4, 5, 6, 8, 10],
    #"max_depth": [5, 10],
    "max_depth": [10],
    #"min_samples_leaf": [1, 5, 10, 20],
    "min_samples_leaf": [5],
    #"min_samples_split": [2, 10, 20],
    "min_samples_split": [2],
}

grid = GridSearchCV(
    DecisionTreeClassifier(random_state=42),
    param_grid,
    scoring="balanced_accuracy",
    cv=cv,
    n_jobs=-1,
)

grid.fit(X, y)

melhores_parametros = grid.best_params_
print("Melhores parâmetros:", melhores_parametros)

# =========================
# 8. Avaliação por validação cruzada (out-of-fold)
# =========================
# Recriamos um modelo do zero com os melhores parâmetros encontrados, e
# usamos cross_val_predict para gerar previsões "out-of-fold": cada
# previsão em y_pred vem de um modelo que NÃO viu aquele registro durante
# o treino daquela rodada. Isso simula testar em dados nunca vistos, mas
# aproveitando 100% da base para gerar essas previsões (em vez de só 30%).
modelo_final_config = DecisionTreeClassifier(
    random_state=42,
    **melhores_parametros
)

y_pred = cross_val_predict(modelo_final_config, X, y, cv=cv, n_jobs=-1)

# cross_validate também nos dá as métricas fold a fold, úteis para reportar
# a variabilidade do resultado (média ± desvio padrão) entre os 5 folds.
scoring_multiplo = {
    "accuracy": "accuracy",
    "balanced_accuracy": "balanced_accuracy",
    "f1_macro": "f1_macro",
}
resultados_cv = cross_validate(
    modelo_final_config, X, y, cv=cv, scoring=scoring_multiplo, n_jobs=-1
)

acuracia = accuracy_score(y, y_pred)
bal_acuracia = balanced_accuracy_score(y, y_pred)
f1_macro = f1_score(y, y_pred, average="macro")
matriz = confusion_matrix(y, y_pred)
relatorio = classification_report(y, y_pred, digits=3)

baseline_majoritario = y.value_counts(normalize=True).max()

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

with open("resultado_arvore.txt", "a", encoding="utf-8") as f:
    f.write("\n" + "=" * 80 + "\n")
    f.write(f"Execução: {datetime.now()}\n\n")

    f.write("MÉTODO: Validação cruzada (StratifiedKFold)\n")
    f.write(f"Numero de folds: {N_SPLITS}\n\n")

    f.write("CONFIGURAÇÃO (melhor combinação via GridSearchCV)\n")
    for k, v in melhores_parametros.items():
        f.write(f"{k}={v}\n")
    f.write("\n")

    f.write(f"Registros (após limpeza): {len(X)}\n")
    f.write(f"Atributos após get_dummies: {X.shape[1]}\n")
    f.write(f"Baseline (classe majoritaria): {baseline_majoritario:.3f}\n\n")

    f.write("===== MÉTRICAS OUT-OF-FOLD (base inteira, cada linha testada 1x) =====\n")
    f.write(f"Acurácia simples: {acuracia}\n")
    f.write(f"Acurácia balanceada: {bal_acuracia}\n")
    f.write(f"F1 macro: {f1_macro}\n\n")

    f.write("===== MÉTRICAS POR FOLD (média ± desvio padrão) =====\n")
    for nome_metrica in scoring_multiplo:
        valores = resultados_cv[f"test_{nome_metrica}"]
        f.write(f"{nome_metrica}: {valores.mean():.3f} ± {valores.std():.3f}  (folds: {[round(v,3) for v in valores]})\n")
    f.write("\n")

    f.write("===== MATRIZ DE CONFUSÃO (out-of-fold) =====\n")
    f.write(f"Classes (ordem): {sorted(y.unique())}\n")
    f.write(str(matriz))
    f.write("\n\n")

    f.write("===== RELATÓRIO (out-of-fold) =====\n")
    f.write(relatorio)
    f.write("\n")

print("Resultado salvo em resultado_arvore.txt")
print(f"\nBaseline (classe majoritária): {baseline_majoritario:.3f}")
print(f"Acurácia simples (out-of-fold): {acuracia:.3f}")
print(f"F1 macro (out-of-fold): {f1_macro:.3f}")

# =========================
# 9. Treinar o modelo final com TODOS os dados
# =========================
# As métricas acima (out-of-fold) já nos dizem como o modelo se comporta em
# dados não vistos. Para gerar UMA árvore final para interpretar (regras,
# importância de variáveis, imagem), treinamos agora com 100% da base,
# usando os melhores parâmetros encontrados. Essa árvore não deve ser usada
# para reportar métricas de desempenho (ela já viu todos os dados) — serve
# apenas para extrair e visualizar os padrões aprendidos.


arvore = DecisionTreeClassifier(random_state=42,  **melhores_parametros)
arvore.fit(X, y)

# =========================
# 10. Importância das variáveis
# =========================
importancias = pd.Series(
    arvore.feature_importances_, index=X.columns
).sort_values(ascending=False)

arquivo_importancias = f"importancia_variaveis_{timestamp}.txt"
with open(arquivo_importancias, "w", encoding="utf-8") as f:
    f.write("IMPORTÂNCIA DAS VARIÁVEIS (feature_importances_)\n")
    f.write("Modelo treinado com 100% dos dados, usando os melhores parametros do GridSearchCV\n")
    f.write("=" * 80 + "\n\n")
    for nome, valor in importancias.items():
        if valor > 0:
            f.write(f"{nome}: {valor:.4f}\n")

print(f"Importâncias salvas em {arquivo_importancias}")
print(importancias.head(15))

# =========================
# 11. Regras da árvore
# =========================
regras = export_text(arvore, feature_names=list(X.columns))

arquivo_regras = f"arvore_regras_{timestamp}.txt"
with open(arquivo_regras, "w", encoding="utf-8") as f:
    f.write("CONFIGURAÇÃO (melhor combinação via GridSearchCV)\n")
    for k, v in melhores_parametros.items():
        f.write(f"{k}={v}\n")
    f.write("\n")
    f.write("Modelo treinado com 100% dos dados (ver secao 9 do script)\n\n")
    f.write("REGRAS DA ÁRVORE\n")
    f.write("=" * 80 + "\n\n")
    f.write(regras)

print(f"Regras salvas em {arquivo_regras}")

# =========================
# 12. Mostrar e salvar árvore
# =========================
plt.figure(figsize=(30, 15))
plot_tree(
    arvore,
    feature_names=X.columns,
    class_names=[str(c) for c in arvore.classes_],
    filled=True,
    rounded=True,
    fontsize=7,
)
plt.tight_layout()

arquivo_imagem = f"arvore_{timestamp}.png"
plt.savefig(arquivo_imagem, dpi=300, bbox_inches="tight")
print(f"Imagem salva em {arquivo_imagem}")

plt.show()