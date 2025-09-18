# Trabalho feito pelo aluno Felipe Pimentel Augusto (sem duplas)

# Inicialmente trabalho feito sem uso de IA
# Depois de enfrentar dificuldade para usar o pacote pyRAPL, consultei o ChatGPT para ajudar
# a criar o decorador que mede tempo e energia, e também para ajudar a integrar o código
# com o pyRAPL. O código do decorador mede_energia foi gerado com ajuda do ChatGPT.
# Depois alguns comentarios de metodos que estavam sem docstring foram gerados com
# ajuda do ChatGPT.

# Infelizmente não consegui rodar o pyRAPL no meu Windows 10, mesmo com WSL2.
# A versão do meu windows é 26100.6584, do 24H2. O pyRAPL funciona em Linux
# e WSL2, mas precisa que o esteja exposto. No meu caso, não consegui fazer
# funcionar. Portanto, a medição de energia não funcionou, mas o código está
# pronto para funcionar em um ambiente adequado.

"""Exemplo simples demonstrando o uso de laços for em Python
chamado a partir da função main.

Execute:
    python main.py
"""
from __future__ import annotations

import random
import time
from typing import Any, Callable, TypeVar, cast

# ---- Integração opcional com pyRAPL (medição de energia) ----
try:  # pyRAPL só funciona de forma confiável em Linux/WSL com RAPL exposto
    import pyRAPL  # type: ignore
    pyRAPL.setup()  # inicializa leitura de RAPL
    PYRAPL_AVAILABLE = True
except Exception:  # noqa: BLE001 - qualquer falha desabilita medição de energia
    pyRAPL = None  # type: ignore
    PYRAPL_AVAILABLE = False

F = TypeVar("F", bound=Callable[..., Any])

def mede_energia(func: F) -> F:
    """Decorador que mede tempo e energia (se pyRAPL disponível) de uma função.

    Para funções recursivas (ex: mergesort) evita medições internas usando um
    *guard* simples que só mede a chamada de nível mais alto.
    Imprime os resultados ao final e adiciona atributo ``_ultima_medicao`` ao wrapper.
    """
    em_execucao = {"flag": False}

    def wrapper(*args: Any, **kwargs: Any):  # type: ignore[override]
        if em_execucao["flag"]:  # chamada interna (recursão) -> não medir de novo
            return func(*args, **kwargs)
        em_execucao["flag"] = True
        inicio = time.perf_counter()
        if PYRAPL_AVAILABLE:
            med = pyRAPL.Measurement(func.__name__)  # type: ignore[attr-defined]
            med.begin()
            resultado = func(*args, **kwargs)
            med.end()
        else:
            med = None
            resultado = func(*args, **kwargs)
        duracao = time.perf_counter() - inicio
        if PYRAPL_AVAILABLE and med is not None:
            # Cada medida retorna listas por socket. Somamos para simplificar.
            pkg_uJ = sum(getattr(med.result, "pkg", []) or [])  # type: ignore[assignment]
            dram_uJ = sum(getattr(med.result, "dram", []) or [])  # type: ignore[assignment]
            print(f"[ENERGIA] {func.__name__}: tempo={duracao*1000:.2f} ms | CPU(pkg)={pkg_uJ} uJ | DRAM={dram_uJ} uJ")
            setattr(wrapper, "_ultima_medicao", {"tempo_s": duracao, "pkg_uJ": pkg_uJ, "dram_uJ": dram_uJ})
        else:
            print(f"[ENERGIA] {func.__name__}: tempo={duracao*1000:.2f} ms | Energia: pyRAPL indisponível (execute em Linux/WSL com 'pip install pyRAPL').")
            setattr(wrapper, "_ultima_medicao", {"tempo_s": duracao, "pkg_uJ": None, "dram_uJ": None})
        em_execucao["flag"] = False
        return resultado

    return cast(F, wrapper)

def processa_numeros(numeros: list[int]) -> dict[str, float]:
    """Percorre a lista com um laço for, imprime e calcula métricas.

    Args:
        numeros: lista de inteiros.
    Returns:
        dicionário com quantidade, soma e média.
    """
    soma = 0
    # Laço for enumerado para ter índice (começando em 1)
    for i, n in enumerate(numeros, start=1):
        print(f"[{i}] valor = {n}")
        soma += n

    quantidade = len(numeros)
    media = soma / quantidade if quantidade else 0
    return {"quantidade": quantidade, "soma": soma, "media": media}

# --- Funções para números primos ---

@mede_energia
def gerar_primos(limite: int) -> list[int]:
    """Gera todos os números primos até 'limite' (inclusivo) usando o Crivo de Eratóstenes.

    Args:
        limite: valor máximo (>=2) a verificar.
    Returns:
        Lista de números primos em ordem crescente.
    """
    if limite < 2:
        return []
    # Crivo: True assume primo inicialmente
    eh_primo = [True] * (limite + 1)
    eh_primo[0] = eh_primo[1] = False
    p = 2
    while p * p <= limite:
        if eh_primo[p]:
            for multiplo in range(p * p, limite, p):
                eh_primo[multiplo] = False
        p += 1
    return [i for i, flag in enumerate(eh_primo) if flag]

def resumo_primos(limite: int) -> dict[str, object]:
    """Retorna resumo contendo lista e quantidade de primos até limite.
    """
    primos = gerar_primos(limite)
    return {"limite": limite, "quantidade": len(primos), "primos": primos}

# --- Função fatorial ---

@mede_energia
def fatorial(n: int) -> int:
    """Calcula n! de forma iterativa.
    0! = 1 por definição.
    Levanta ValueError para n negativo.
    """
    if n < 0:
        raise ValueError("n deve ser >= 0")
    resultado = 1
    for i in range(2, n + 1):
        resultado *= i
    return resultado

# --- Ordenação ---

def gerar_lista_aleatoria(tamanho: int, minimo: int = 0, maximo: int = 10_000) -> list[int]:
    """Gera lista de inteiros aleatórios no intervalo [minimo, maximo]."""
    return [random.randint(minimo, maximo) for _ in range(tamanho)]

@mede_energia
def mergesort(lst: list[int]) -> list[int]:
    """Implementação recursiva de Merge Sort retornando nova lista ordenada."""
    if len(lst) <= 1:
        return lst
    meio = len(lst) // 2
    esquerda = mergesort(lst[:meio])
    direita = mergesort(lst[meio:])
    # Intercala
    i = j = 0
    resultado: list[int] = []
    while i < len(esquerda) and j < len(direita):
        if esquerda[i] <= direita[j]:
            resultado.append(esquerda[i])
            i += 1
        else:
            resultado.append(direita[j])
            j += 1
    if i < len(esquerda):
        resultado.extend(esquerda[i:])
    if j < len(direita):
        resultado.extend(direita[j:])
    return resultado

def benchmark_ordenacao(tamanho: int) -> dict[str, float]:
    """Compara tempo do mergesort com list.sort() nativo."""
    dados = gerar_lista_aleatoria(tamanho)

    copia1 = list(dados)
    inicio = time.perf_counter()
    ordenada_merge = mergesort(copia1)
    tempo_merge = time.perf_counter() - inicio

    copia2 = list(dados)
    inicio = time.perf_counter()
    copia2.sort()
    tempo_nativo = time.perf_counter() - inicio

    # Validação simples
    assert ordenada_merge == copia2, "Mergesort produziu resultado incorreto"

    return {"tamanho": tamanho, "tempo_mergesort": tempo_merge, "tempo_sort_nativo": tempo_nativo}

# --- Busca em lista ordenada (Busca Binária) ---

@mede_energia
def busca_binaria(lista: list[int], alvo: int) -> int:
    """Retorna o índice de 'alvo' em 'lista' (ordenada asc) ou -1 se não encontrado."""
    inicio = 0
    fim = len(lista) - 1
    while inicio <= fim:
        meio = (inicio + fim) // 2
        valor = lista[meio]
        if valor == alvo:
            return meio
        if valor < alvo:
            inicio = meio + 1
        else:
            fim = meio - 1
    return -1

@mede_energia
def calcular_pi(metros: int) -> float:
    """Calcula uma aproximação de PI usando a série de Leibniz."""
    pi = 0.0
    for k in range(metros):
        pi += ((-1) ** k) / (2 * k + 1)
    return pi * 4

def demonstracao_medicoes() -> None:
    """Executa várias funções medindo tempo/energia com inputs moderados.

    Pensado para mostrar a saída do decorador de forma rápida.
    Ajuste os parâmetros conforme necessário para workloads maiores.
    """
    print("\n== Demonstração de medições ==")
    gerar_primos(50_000)  # pode aumentar, mas cuidado com tempo
    fatorial(5000)        # fatorial iterativo cresce rápido em custo para n grande
    # Para mergesort, gerar lista de exemplo
    lista = gerar_lista_aleatoria(50_000)
    mergesort(lista)
    # Busca binária em lista ordenada
    ordenada = sorted(lista)
    alvo = ordenada[len(ordenada)//2]
    busca_binaria(ordenada, alvo)
    calcular_pi(200_000)  # série de Leibniz é lenta para convergir
    print("== Fim da demonstração ==\n")

def main() -> None:
    # Menu simples
    print("Escolha uma opção:")
    print("1 - Processar lista de números 1..10")
    print("2 - Gerar números primos até um limite")
    print("3 - Calcular fatorial de n")
    print("4 - Benchmark ordenação lista aleatória")
    print("5 - Busca binária em lista ordenada")
    print("6 - Cálculo do PI (individual)")
    print("7 - Demonstração de medições (tempo/energia)")
    opcao = input("Opção (1/2/3/4/5/6/7): ").strip()

    if opcao == "1":
        numeros = list(range(1, 11))
        print("Processando lista de números:\n")
        resultado = processa_numeros(numeros)
        print("\nResumo:")
        for chave, valor in resultado.items():
            print(f"{chave}: {valor}")
    elif opcao == "2":
        while True:
            entrada = input("Informe o limite (inteiro >= 2): ").strip()
            if not entrada.isdigit():
                print("Digite apenas números inteiros positivos.")
                continue
            limite = int(entrada)
            if limite < 2:
                print("Limite deve ser >= 2.")
                continue
            break
        resumo = resumo_primos(limite)
        print(f"\nForam encontrados {resumo['quantidade']} números primos até {resumo['limite']}:")
        # Imprimir em linhas de até 15 primos
        linha = []
        for i, p in enumerate(resumo['primos'], start=1):
            linha.append(f"{p:>4}")
            if i % 15 == 0:
                print(" ".join(linha))
                linha = []
        if linha:
            print(" ".join(linha))
    elif opcao == "3":
        while True:
            entrada = input("Informe n (inteiro >= 0): ").strip()
            if not (entrada.isdigit()):
                print("Digite um inteiro não negativo.")
                continue
            n = int(entrada)
            break
        print(f"\nCalculando {n}! ...")
        print(f"Resultado: {n}! = {fatorial(n)}")
    elif opcao == "4":
        while True:
            entrada = input("Informe o tamanho da lista (> 1000): ").strip()
            if not entrada.isdigit():
                print("Digite um inteiro válido.")
                continue
            tamanho = int(entrada)
            if tamanho <= 1000:
                print("Tamanho deve ser > 1000.")
                continue
            break
        print("\nGerando dados e executando benchmarks...")
        resultado = benchmark_ordenacao(tamanho)
        print("\nResultados:")
        print(f"Tamanho: {resultado['tamanho']}")
        print(f"MergeSort: {resultado['tempo_mergesort']*1000:.2f} ms")
        print(f"Sort nativo: {resultado['tempo_sort_nativo']*1000:.2f} ms")
        fator = resultado['tempo_mergesort']/resultado['tempo_sort_nativo'] if resultado['tempo_sort_nativo'] else float('inf')
        print(f"Razão (merge/nativo): {fator:.2f}x")
    elif opcao == "5":
        while True:
            entrada = input("Informe o tamanho da lista ordenada (>= 1): ").strip()
            if not entrada.isdigit():
                print("Digite um inteiro válido.")
                continue
            tamanho = int(entrada)
            if tamanho < 1:
                print("Tamanho deve ser >= 1.")
                continue
            break
        lista = sorted(gerar_lista_aleatoria(tamanho))
        while True:
            alvo_txt = input("Informe o valor a buscar: ").strip()
            if not alvo_txt.lstrip('-').isdigit():
                print("Digite um inteiro (pode ser negativo, se quiser).")
                continue
            alvo = int(alvo_txt)
            break
        indice = busca_binaria(lista, alvo)
        if tamanho <= 50:
            print(f"Lista: {lista}")
        if indice >= 0:
            print(f"Valor {alvo} encontrado no índice {indice}.")
        else:
            print(f"Valor {alvo} não encontrado.")
    elif opcao == "6":
        while True:
            entrada = input("Informe o número de termos para calcular PI (>= 1): ").strip()
            if not entrada.isdigit():
                print("Digite um inteiro válido.")
                continue
            termos = int(entrada)
            if termos < 1:
                print("Número de termos deve ser >= 1.")
                continue
            break
        pi_aproximado = calcular_pi(termos)
        print(f"\nAproximação de PI usando {termos} termos: {pi_aproximado}")
    elif opcao == "7":
        demonstracao_medicoes()
    else:
        print("Opção inválida.")

if __name__ == "__main__":
    main()
