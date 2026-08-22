import pandas as pd
from sklearn.tree import export_text, DecisionTreeClassifier, plot_tree
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.metrics import (
    accuracy_score, balanced_accuracy_score, f1_score,
    classification_report, confusion_matrix
)
import matplotlib.pyplot as plt
from datetime import datetime
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "..", "data", "exports", "z4-todos-base_detalhada_geral_publico.csv")


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
# - resultado, gols_favor, gols_sofridos: vazamento direto (definem o alvo)
# - data, horario: já capturados por dia_semana/mes/rodada
# - desvio_*: descartados por decisão de projeto
# - time, adversario, estadio, arbitro: identificadores de alta cardinalidade
#   que fazem o modelo decorar entidades específicas em vez de aprender
#   fatores generalizáveis (idade, altura, mando, público etc.)
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
X = pd.get_dummies(X)
print("Atributos após get_dummies:", X.shape[1])

# =========================
# 6. Separar treino e teste (com stratify)
# =========================
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.3,
    random_state=42,
    stratify=y
)

# =========================
# 7. GridSearch com validação cruzada
# =========================
param_grid = {
    "criterion": ["entropy", "gini"],
    #"max_depth": [3, 4, 5, 6, 8, None],
    #"max_depth": [5, 10],
    "max_depth": [10],
    #"max_depth": [10],
    "min_samples_leaf": [1, 5, 10, 20],
    "min_samples_split": [2, 10, 20],
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

grid = GridSearchCV(
    DecisionTreeClassifier(random_state=42),
    param_grid,
    scoring="balanced_accuracy",
    cv=cv,
    n_jobs=-1,
)

grid.fit(X_train, y_train)

arvore = grid.best_estimator_
print("Melhores parâmetros:", grid.best_params_)

# =========================
# 8. Previsões e avaliação
# =========================
y_pred = arvore.predict(X_test)

acuracia = accuracy_score(y_test, y_pred)
bal_acuracia = balanced_accuracy_score(y_test, y_pred)
f1_macro = f1_score(y_test, y_pred, average="macro")
matriz = confusion_matrix(y_test, y_pred)
relatorio = classification_report(y_test, y_pred, digits=3)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

with open("resultado_arvore.txt", "a", encoding="utf-8") as f:
    f.write("\n" + "=" * 80 + "\n")
    f.write(f"Execução: {datetime.now()}\n\n")

    f.write("CONFIGURAÇÃO (melhor combinação via GridSearchCV)\n")
    for k, v in grid.best_params_.items():
        f.write(f"{k}={v}\n")
    f.write("\n")

    f.write(f"Registros (após limpeza): {len(X)}\n")
    f.write(f"Atributos após get_dummies: {X.shape[1]}\n\n")

    f.write("===== ACURÁCIA =====\n")
    f.write(f"Acurácia simples: {acuracia}\n")
    f.write(f"Acurácia balanceada: {bal_acuracia}\n")
    f.write(f"F1 macro: {f1_macro}\n\n")

    f.write("===== MATRIZ DE CONFUSÃO =====\n")
    f.write(f"Classes (ordem): {list(arvore.classes_)}\n")
    f.write(str(matriz))
    f.write("\n\n")

    f.write("===== RELATÓRIO =====\n")
    f.write(relatorio)
    f.write("\n")

print("Resultado salvo em resultado_arvore.txt")

# =========================
# 9. Importância das variáveis 
# =========================
importancias = pd.Series(
    arvore.feature_importances_, index=X.columns
).sort_values(ascending=False)

arquivo_importancias = f"importancia_variaveis_{timestamp}.txt"
with open(arquivo_importancias, "w", encoding="utf-8") as f:
    f.write("IMPORTÂNCIA DAS VARIÁVEIS (feature_importances_)\n")
    f.write("=" * 80 + "\n\n")
    for nome, valor in importancias.items():
        if valor > 0:
            f.write(f"{nome}: {valor:.4f}\n")

print(f"Importâncias salvas em {arquivo_importancias}")
print(importancias.head(15))

# =========================
# 10. Regras da árvore
# =========================
regras = export_text(arvore, feature_names=list(X.columns))

arquivo_regras = f"arvore_regras_{timestamp}.txt"
with open(arquivo_regras, "w", encoding="utf-8") as f:
    f.write("CONFIGURAÇÃO (melhor combinação via GridSearchCV)\n")
    for k, v in grid.best_params_.items():
        f.write(f"{k}={v}\n")
    f.write("\n")
    f.write("REGRAS DA ÁRVORE\n")
    f.write("=" * 80 + "\n\n")
    f.write(regras)

print(f"Regras salvas em {arquivo_regras}")

# =========================
# 11. Mostrar e salvar árvore
# =========================
plt.figure(figsize=(36, 18))
plot_tree(
    arvore,
    feature_names=X.columns,
    class_names=[str(c) for c in arvore.classes_],
    filled=True,
    rounded=True,
    fontsize=7,
)

arquivo_imagem = f"arvore_{timestamp}.png"
plt.savefig(arquivo_imagem, dpi=300, bbox_inches="tight")
print(f"Imagem salva em {arquivo_imagem}")

plt.show()
