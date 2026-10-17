"""Utilitários compartilhados pelos módulos de gráficos."""

import matplotlib.pyplot as plt


def salvar(caminho_saida):
    """Ajusta o layout, salva a figura atual em PNG e a fecha."""
    plt.tight_layout()
    plt.savefig(caminho_saida, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Salvo: {caminho_saida}")
