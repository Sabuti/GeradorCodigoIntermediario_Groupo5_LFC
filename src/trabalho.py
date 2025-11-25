# Integrantes do grupo:
# Ana Maria Midori Rocha Hinoshita - anamariamidori
# Lucas Antonio Linhares - Sabuti
#
# Nome do grupo no Canvas: RA4 5

import sys
import math
import json

EPS = 'E'

# ========================================
# CONTADORES GLOBAIS PARA TAC
# ========================================
TEMP_COUNTER = 0
LABEL_COUNTER = 0

def novo_temp():
    """Gera uma nova variável temporária única (t0, t1, t2, ...)"""
    global TEMP_COUNTER
    TEMP_COUNTER += 1
    return f"t{TEMP_COUNTER}"

def novo_label():
    """Gera um novo rótulo único (L0, L1, L2, ...)"""
    global LABEL_COUNTER
    LABEL_COUNTER += 1
    return f"L{LABEL_COUNTER}"

def resetar_contadores_tac():
    """Reseta os contadores de temporários e labels (útil para testes)"""
    global TEMP_COUNTER, LABEL_COUNTER
    TEMP_COUNTER = 0
    LABEL_COUNTER = 0

# ========================================
# FUNÇÕES ANTERIORES (Fases 1-3)
# ========================================

def lerArquivo(nomeArquivo):
    """Lê um arquivo linha por linha, removendo espaços extras e ignorando linhas vazias."""
    linhas = []
    try:
        with open(nomeArquivo, 'r', encoding='utf-8') as file:
            for linha in file:
                linha = linha.strip()
                if linha:
                    linhas.append(linha)
    except FileNotFoundError:
        print(f"Erro: arquivo '{nomeArquivo}' não encontrado.")
        return None
    except Exception as e:
        print(f"Erro ao ler o arquivo: {e}")
        return None
    return linhas

## FASE 1: ANÁLISE LÉXICA

def parseExpressao(linha, _tokens_):
    token = ""
    parenteses = 0
    i = 0

    while i < len(linha):
        char = linha[i]

        if char.isspace():
            if token:
                _tokens_.append(token)
                token = ""

        elif char in "()":
            if token:
                _tokens_.append(token)
                token = ""
            _tokens_.append(char)

            if char == "(":
                parenteses += 1
            else:
                parenteses -= 1
                if parenteses < 0:
                    raise ValueError("Erro Sintático: parêntese fechado sem correspondente.")

        elif char in "+-*/%^":
            if token:
                _tokens_.append(token)
                token = ""
            _tokens_.append(char)

        elif char == '|':
            if token:
                _tokens_.append(token)
                token = ""
            _tokens_.append(char)

        elif char in "><=!":
            if token:
                _tokens_.append(token)
                token = ""

            if i + 1 < len(linha) and linha[i + 1] == '=':
                _tokens_.append(char + '=')
                i += 1
            else:
                _tokens_.append(char)

        else:
            token += char

        i += 1

    if token:
        _tokens_.append(token)

    if parenteses != 0:
        raise ValueError("Erro Sintático: parêntese aberto sem correspondente.")

    return True

def estadoNumero(token):
    if not token:
        return False
    if token.count(".") > 1:
        return False
    try:
        if token.count(".") == 1:
            float(token)
        else:
            int(token)
        return True
    except ValueError:
        return False

def estadoOperador(token):
    return token in ["+", "-", "*", "|", "/", "%", "^"]

def estadoParenteses(token):
    return token in ["(", ")"]

def estadoComparador(token):
    return token in ["<", ">", "<=", ">=", "==", "!="]

def RESorMEM(token: str) -> bool:
    if not token:
        return False
    estado = "Q0"
    for ch in token:
        if estado == "Q0":
            if ch.isalpha() and ch.isupper():
                estado = "QID"
            else:
                return False
        elif estado == "QID":
            if not (ch.isalpha() and ch.isupper()) and not ch.isdigit():
                return False
    return estado == "QID"

def analisadorLexico(tokens_originais: list[str]) -> tuple[list[str], list]:
    tokens_convertidos: list[str] = []
    tokens_valores: list = []

    for token in tokens_originais:
        if estadoParenteses(token):
            tokens_convertidos.append(token)
            tokens_valores.append(token)
            continue

        if estadoOperador(token):
            tokens_convertidos.append(token)
            tokens_valores.append(token)
            continue

        if estadoComparador(token):
            tokens_convertidos.append(token)
            tokens_valores.append(token)
            continue

        if estadoNumero(token):
            if token.count(".") == 1:
                tokens_convertidos.append("float")
                tokens_valores.append(float(token))
            else:
                tokens_convertidos.append("int")
                tokens_valores.append(int(token))
            continue

        if RESorMEM(token):
            if token == "RES":
                tokens_convertidos.append("res")
                tokens_valores.append(token)
            elif token == "IF":
                tokens_convertidos.append("if")
                tokens_valores.append(token)
            elif token == "WHILE":
                tokens_convertidos.append("while")
                tokens_valores.append(token)
            else:
                tokens_convertidos.append("ident")
                tokens_valores.append(token)
            continue

        raise ValueError(f"Erro Léxico: token inválido -> {token}")

    return tokens_convertidos, tokens_valores

## FASE 2: ANÁLISE SINTÁTICA

def analisadorSintatico(tokens: list[str], tabelaLL1: dict) -> list[tuple[str, list[str]]]:
    stack: list[str] = ['$', 'LINHA']
    derivation: list[tuple[str, list[str]]] = []
    index = 0

    nonterminals = {A for (A, _) in tabelaLL1.keys()}

    def is_nonterminal(sym: str) -> bool:
        return sym in nonterminals

    while stack:
        top = stack.pop()
        current_token = tokens[index] if index < len(tokens) else '$'

        if top == current_token == '$':
            return derivation

        if not is_nonterminal(top):
            if top == current_token:
                index += 1
            else:
                raise ValueError(f"Erro Sintático: esperado '{top}', encontrado '{current_token}'")
        else:
            key = (top, current_token)
            if key in tabelaLL1:
                production: list[str] = tabelaLL1[key]
                derivation.append((top, production))
                for sym in reversed(production):
                    if sym != EPS:
                        stack.append(sym)
            else:
                raise ValueError(f"Erro Sintático: não há produção para {top}, '{current_token}'")

    raise ValueError("Erro Sintático: pilha vazia antes do fim dos tokens")

## FASE 3: ANÁLISE SEMÂNTICA

def inicializarTabelaSimbolos() -> dict:
    return {}

def adicionarSimbolo(tabela: dict, nome: str, tipo: str = 'desconhecido', inicializada: bool = False,
    valor=None, linha: int = 0, escopo: str = 'global') -> dict:
    if nome in tabela:
        tabela[nome]['tipo'] = tipo
        tabela[nome]['inicializada'] = inicializada
        tabela[nome]['valor'] = valor
        if not tabela[nome].get('linha_declaracao'):
            tabela[nome]['linha_declaracao'] = linha
    else:
        tabela[nome] = {
            'tipo': tipo,
            'inicializada': inicializada,
            'valor': valor,
            'linha_declaracao': linha,
            'escopo': escopo,
            'usada': False,
            'linhas_uso': []
        }
    return tabela

def buscarSimbolo(tabela: dict, nome: str):
    return tabela.get(nome, None)

def marcarSimboloUsado(tabela: dict, nome: str, linha: int) -> None:
    if nome in tabela:
        tabela[nome]['usada'] = True
        if 'linhas_uso' not in tabela[nome]:
            tabela[nome]['linhas_uso'] = []
        if linha not in tabela[nome]['linhas_uso']:
            tabela[nome]['linhas_uso'].append(linha)

def definirGramaticaAtributos() -> dict:
    regras_semanticas = {
        'operadores_aritmeticos': {
            '+': {'aceita': ['int', 'float'], 'retorna': 'promover'},
            '-': {'aceita': ['int', 'float'], 'retorna': 'promover'},
            '*': {'aceita': ['int', 'float'], 'retorna': 'promover'},
            '|': {'aceita': ['int', 'float'], 'retorna': 'float'},
            '/': {'aceita': ['int'], 'retorna': 'int'},
            '%': {'aceita': ['int'], 'retorna': 'int'},
            '^': {
                'aceita_base': ['int', 'float'],
                'aceita_exp': ['int'],
                'retorna': 'promover'
            }
        },
        'operadores_relacionais': {
            '<': {'aceita': ['int', 'float'], 'retorna': 'booleano'},
            '>': {'aceita': ['int', 'float'], 'retorna': 'booleano'},
            '<=': {'aceita': ['int', 'float'], 'retorna': 'booleano'},
            '>=': {'aceita': ['int', 'float'], 'retorna': 'booleano'},
            '==': {'aceita': ['int', 'float'], 'retorna': 'booleano'},
            '!=': {'aceita': ['int', 'float'], 'retorna': 'booleano'}
        },
        'estruturas_controle': {
            'if': {'condicao': 'booleano', 'retorna': 'tipo_ramos'},
            'while': {'condicao': 'booleano', 'retorna': 'tipo_corpo'}
        },
        'comandos_especiais': {
            'res': {'parametro': 'int', 'retorna': 'tipo_resultado'},
            'mem_atrib': {'valor': ['int', 'float'], 'retorna': 'tipo_valor'},
            'mem_leitura': {'retorna': 'tipo_memoria'}
        }
    }
    return regras_semanticas

def promoverTipo(tipo1: str, tipo2: str) -> str:
    if tipo1 == 'float' or tipo2 == 'float':
        return 'float'
    if tipo1 == 'int' and tipo2 == 'int':
        return 'int'
    if tipo1 == 'booleano' or tipo2 == 'booleano':
        return 'booleano'
    return 'desconhecido'

def construirGramatica() -> tuple:
    def is_nonterminal(simbolo: str, G: dict) -> bool:
        return simbolo in G

    def calcularFirst(G: dict) -> dict:
        FIRST = {A: set() for A in G}
        alterou = True
        while alterou:
            alterou = False
            for A in G:
                for producao in G[A]:
                    if len(producao) == 0:
                        if EPS not in FIRST[A]:
                            FIRST[A].add(EPS)
                            alterou = True
                        continue
                    pode_gerar_epsilon = True
                    for simbolo in producao:
                        if simbolo == EPS:
                            if EPS not in FIRST[A]:
                                FIRST[A].add(EPS)
                                alterou = True
                            pode_gerar_epsilon = False
                            break
                        if not is_nonterminal(simbolo, G):
                            if simbolo not in FIRST[A]:
                                FIRST[A].add(simbolo)
                                alterou = True
                            pode_gerar_epsilon = False
                            break
                        tamanho_antes = len(FIRST[A])
                        FIRST[A].update(s for s in FIRST[simbolo] if s != EPS)
                        if len(FIRST[A]) != tamanho_antes:
                            alterou = True
                        if EPS in FIRST[simbolo]:
                            pode_gerar_epsilon = True
                        else:
                            pode_gerar_epsilon = False
                            break
                    if pode_gerar_epsilon:
                        if EPS not in FIRST[A]:
                            FIRST[A].add(EPS)
                            alterou = True
        return FIRST

    def first_of_sequence(seq: list, FIRST: dict, G: dict) -> set:
        resultado = set()
        if len(seq) == 0:
            resultado.add(EPS)
            return resultado
        pode_gerar_epsilon = True
        for simbolo in seq:
            if simbolo == EPS:
                resultado.add(EPS)
                pode_gerar_epsilon = False
                break
            if not is_nonterminal(simbolo, G):
                resultado.add(simbolo)
                pode_gerar_epsilon = False
                break
            resultado.update(s for s in FIRST[simbolo] if s != EPS)
            if EPS in FIRST[simbolo]:
                pode_gerar_epsilon = True
            else:
                pode_gerar_epsilon = False
                break
        if pode_gerar_epsilon:
            resultado.add(EPS)
        return resultado

    def calcularFollow(G: dict, FIRST: dict, start: str = 'LINHA') -> dict:
        FOLLOW = {A: set() for A in G}
        FOLLOW[start].add('$')
        alterou = True
        while alterou:
            alterou = False
            for A in G:
                for producao in G[A]:
                    for i, B in enumerate(producao):
                        if not is_nonterminal(B, G):
                            continue
                        beta = producao[i + 1:]
                        first_beta = first_of_sequence(beta, FIRST, G)
                        tamanho_antes = len(FOLLOW[B])
                        FOLLOW[B].update(s for s in first_beta if s != EPS)
                        if EPS in first_beta or len(beta) == 0:
                            FOLLOW[B].update(FOLLOW[A])
                        if len(FOLLOW[B]) != tamanho_antes:
                            alterou = True
        return FOLLOW

    def construirTabelaLL1(G: dict, FIRST: dict, FOLLOW: dict) -> tuple:
        tabela = {}
        conflitos = []
        for A in G:
            for producao in G[A]:
                first_prod = first_of_sequence(producao, FIRST, G)
                for a in (first_prod - {EPS}):
                    chave = (A, a)
                    if chave in tabela and tabela[chave] != producao:
                        conflitos.append((chave, tabela[chave], producao))
                    else:
                        tabela[chave] = producao
                if EPS in first_prod:
                    for b in FOLLOW[A]:
                        chave = (A, b)
                        if chave in tabela and tabela[chave] != producao:
                            conflitos.append((chave, tabela[chave], producao))
                        else:
                            tabela[chave] = producao
        return tabela, conflitos

    G = {
        'LINHA': [['EXPR']],
        'EXPR': [['(', 'ITEMS', ')']],
        'ITEMS': [['ITEM', 'ITEMS'], [EPS]],
        'ITEM': [['NUMERO'], ['IDENT'], ['OPERADOR'], ['IFKW'], ['WHILEKW'], ['EXPR']],
        'NUMERO': [['float'], ['int']],
        'IDENT': [['ident'], ['res']],
        'OPERADOR': [
            ['+'], ['-'], ['*'], ['/'], ['%'], ['^'], ['|'],
            ['>'], ['<'], ['>='], ['<='], ['=='], ['!=']
        ],
        'IFKW': [['if']],
        'WHILEKW': [['while']]
    }

    FIRST = calcularFirst(G)
    FOLLOW = calcularFollow(G, FIRST)
    tabelaLL1, conflitos = construirTabelaLL1(G, FIRST, FOLLOW)

    if conflitos:
        for (A, a), p1, p2 in conflitos:
            print(f"Conflito LL(1) em ({A}, {a}): {p1} / {p2}")
        raise ValueError("Gramática não é LL(1).")

    return G, FIRST, FOLLOW, tabelaLL1

def coletar_atribuicoes(tokens_valores: list) -> set:
    atribuicoes = set()
    profundidade = 0
    elementos_expr = []

    for token in tokens_valores:
        if token == '(':
            if profundidade == 0:
                elementos_expr = []
            profundidade += 1
            continue

        if token == ')':
            profundidade -= 1
            if profundidade == 0 and len(elementos_expr) == 2:
                tipo1, _ = elementos_expr[0]
                tipo2, nome2 = elementos_expr[1]
                if tipo2 == 'ident' and nome2 is not None:
                    if tipo1 in ['int', 'float', 'ident', 'res', 'subexpr']:
                        atribuicoes.add(nome2)
            elementos_expr = []
            continue

        if profundidade == 1:
            if isinstance(token, int):
                elementos_expr.append(('int', None))
            elif isinstance(token, float):
                elementos_expr.append(('float', None))
            elif isinstance(token, str):
                tl = token.lower()
                if tl in ['res', 'if', 'while']:
                    elementos_expr.append((tl, None))
                elif token in ['+', '-', '*', '/', '%', '^', '|',
                               '<', '>', '<=', '>=', '==', '!=']:
                    elementos_expr.append(('op', token))
                else:
                    elementos_expr.append(('ident', token))

    return atribuicoes

def criar_contexto() -> dict:
    return {
        'erros': [],
        'arvore_anotada': [],
        'pilha_tipos': [],
        'pilha_valores': [],
        'idx_valor': 0,
        'memorias_decl_nesta_linha': set()
    }

def tokens_processaveis_de(tokens_valores: list) -> list:
    return [v for v in tokens_valores if v not in ('(', ')')]

def consumir_literal(ctx: dict, tokens_proc: list, tipo: str, linha: int) -> None:
    if ctx['idx_valor'] >= len(tokens_proc):
        ctx['erros'].append(
            f"ERRO SEMÂNTICO [Linha {linha}]: Literal esperado, mas tokens acabaram."
        )
        return

    valor = tokens_proc[ctx['idx_valor']]
    ctx['idx_valor'] += 1

    ctx['pilha_tipos'].append(tipo)
    ctx['pilha_valores'].append(valor)

    ctx['arvore_anotada'].append({
        'tipo_no': 'LITERAL',
        'tipo_inferido': tipo,
        'valor': valor,
        'linha': linha
    })

def processar_identificador(ctx: dict, tokens_proc: list, tabela_simbolos: dict, atribuicoes: set, linha: int) -> dict:
    if ctx['idx_valor'] >= len(tokens_proc):
        ctx['erros'].append(
            f"ERRO SEMÂNTICO [Linha {linha}]: Token inesperado ao processar identificador."
        )
        return tabela_simbolos

    nome = tokens_proc[ctx['idx_valor']]
    ctx['idx_valor'] += 1

    if nome in ['(', ')', '+', '-', '*', '/', '%', '^', '|',
                '<', '>', '<=', '>=', '==', '!=', 'IF', 'WHILE', 'RES', 'res']:
        ctx['erros'].append(
            f"ERRO SEMÂNTICO [Linha {linha}]: Token '{nome}' não é identificador válido."
        )
        return tabela_simbolos

    if nome in atribuicoes:
        if not ctx['pilha_tipos']:
            ctx['erros'].append(
                f"ERRO SEMÂNTICO [Linha {linha}]: Atribuição sem valor para '{nome}'."
            )
            return tabela_simbolos

        tipo_valor = ctx['pilha_tipos'].pop()
        valor = ctx['pilha_valores'].pop() if ctx['pilha_valores'] else None

        tabela_simbolos = adicionarSimbolo(
            tabela_simbolos, nome, tipo_valor, True, valor, linha
        )

        ctx['memorias_decl_nesta_linha'].add(nome)

        ctx['pilha_tipos'].append(tipo_valor)
        ctx['pilha_valores'].append(valor)

        ctx['arvore_anotada'].append({
            'tipo_no': 'ATRIBUICAO',
            'tipo_inferido': tipo_valor,
            'nome': nome,
            'valor': valor,
            'linha': linha
        })

        return tabela_simbolos

    info = buscarSimbolo(tabela_simbolos, nome)

    if info is None:
        ctx['erros'].append(
            f"ERRO SEMÂNTICO [Linha {linha}]: Variável '{nome}' usada sem declaração."
        )
        tipo = 'desconhecido'
        valor = 'X'
        tabela_simbolos = adicionarSimbolo(tabela_simbolos, nome, tipo, False, valor, linha)

    elif not info.get('inicializada', False):
        ctx['erros'].append(
            f"ERRO SEMÂNTICO [Linha {linha}]: Variável '{nome}' usada sem inicialização."
        )
        tipo = info.get('tipo', 'desconhecido')
        valor = 'X'

    else:
        tipo = info.get('tipo', 'desconhecido')
        valor = info.get('valor')
        marcarSimboloUsado(tabela_simbolos, nome, linha)

    ctx['pilha_tipos'].append(tipo)
    ctx['pilha_valores'].append(valor)

    ctx['arvore_anotada'].append({
        'tipo_no': 'LEITURA_VARIAVEL',
        'tipo_inferido': tipo,
        'nome': nome,
        'linha': linha
    })

    return tabela_simbolos

def processar_res(ctx: dict, tokens_processaveis: list, historico_resultados: list, numero_linha: int) -> None:
    if ctx['idx_valor'] >= len(tokens_processaveis):
        ctx['erros'].append(
            f"ERRO SEMÂNTICO [Linha {numero_linha}]: Token inesperado (fim da linha)"
        )
        return

    token = tokens_processaveis[ctx['idx_valor']]

    if token not in ['RES', 'res']:
        ctx['erros'].append(
            f"ERRO SEMÂNTICO [Linha {numero_linha}]: Esperado 'RES', encontrado '{token}'"
        )
        ctx['idx_valor'] += 1
        return

    ctx['idx_valor'] += 1

    if len(ctx['pilha_tipos']) < 1:
        ctx['erros'].append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: RES requer um parâmetro na pilha")
        ctx['pilha_tipos'].append('desconhecido')
        ctx['pilha_valores'].append(None)
        ctx['arvore_anotada'].append({
            'tipo_no': 'RES',
            'tipo_inferido': 'desconhecido',
            'parametro': None,
            'linha': numero_linha
        })
        return

    tipo_param = ctx['pilha_tipos'].pop()
    n_valor = ctx['pilha_valores'].pop() if ctx['pilha_valores'] else None

    if tipo_param != 'int':
        ctx['erros'].append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: RES requer parâmetro inteiro; recebeu '{tipo_param}'")
        ctx['pilha_tipos'].append('desconhecido')
        ctx['pilha_valores'].append(None)
        ctx['arvore_anotada'].append({
            'tipo_no': 'RES',
            'tipo_inferido': 'desconhecido',
            'parametro': 0,
            'linha': numero_linha
        })
        return

    if not isinstance(n_valor, int):
        ctx['erros'].append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: RES parâmetro inválido: {n_valor}")
        ctx['pilha_tipos'].append('desconhecido')
        ctx['pilha_valores'].append(None)
        ctx['arvore_anotada'].append({
            'tipo_no': 'RES',
            'tipo_inferido': 'desconhecido',
            'parametro': 0,
            'linha': numero_linha
        })
        return

    n = int(n_valor)

    if n < 0:
        ctx['erros'].append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: RES requer N >= 0")
        tipo_resultado = 'desconhecido'
    elif n >= len(historico_resultados):
        ctx['erros'].append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: RES({n}) fora do alcance do histórico")
        tipo_resultado = 'desconhecido'
    else:
        idx_resultado = len(historico_resultados) - 1 - n
        tipo_resultado = historico_resultados[idx_resultado].get('tipo', 'desconhecido')

    ctx['pilha_tipos'].append(tipo_resultado)
    ctx['pilha_valores'].append(None)

    ctx['arvore_anotada'].append({
        'tipo_no': 'RES',
        'tipo_inferido': tipo_resultado,
        'parametro': n,
        'linha': numero_linha
    })

def processar_operador_aritmetico(ctx: dict, simbolo: str, regras_semanticas: dict, numero_linha: int) -> None:
    regra = regras_semanticas.get('operadores_aritmeticos', {}).get(simbolo, {'aceita': [], 'aceita_base': []})

    ctx['idx_valor'] += 1

    if len(ctx['pilha_tipos']) < 2:
        ctx['erros'].append(
            f"ERRO SEMÂNTICO [Linha {numero_linha}]: "
            f"Operador '{simbolo}' requer dois operandos (insuficientes)"
        )
        return

    tipo2 = ctx['pilha_tipos'].pop()
    tipo1 = ctx['pilha_tipos'].pop()

    if ctx['pilha_valores']:
        ctx['pilha_valores'].pop()
    if ctx['pilha_valores']:
        ctx['pilha_valores'].pop()

    if simbolo == '^':
        base_valida = tipo1 in regra.get('aceita_base', [])
        exp_valido = tipo2 == 'int'

        if not base_valida:
            ctx['erros'].append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: Base inválida para '^' ({tipo1})")
        if not exp_valido:
            ctx['erros'].append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: Expoente deve ser int (recebido '{tipo2}')")

        tipo_resultado = promoverTipo(tipo1, 'int')

    elif simbolo in ['/', '%']:
        if tipo1 != 'int' or tipo2 != 'int':
            ctx['erros'].append(
                f"ERRO SEMÂNTICO [Linha {numero_linha}]: "
                f"Operador '{simbolo}' exige inteiros ({tipo1}, {tipo2})"
            )
        tipo_resultado = 'int'

    elif simbolo == '|':
        if tipo1 not in regra['aceita'] or tipo2 not in regra['aceita']:
            ctx['erros'].append(
                f"ERRO SEMÂNTICO [Linha {numero_linha}]: "
                f"Operador '|' exige operandos numéricos"
            )
        tipo_resultado = 'float'

    else:
        if tipo1 not in regra['aceita'] or tipo2 not in regra['aceita']:
            ctx['erros'].append(
                f"ERRO SEMÂNTICO [Linha {numero_linha}]: "
                f"Tipos incompatíveis para '{simbolo}' ({tipo1}, {tipo2})"
            )
        tipo_resultado = promoverTipo(tipo1, tipo2)

    ctx['pilha_tipos'].append(tipo_resultado)
    ctx['pilha_valores'].append(None)

    ctx['arvore_anotada'].append({
        'tipo_no': 'OPERACAO',
        'operador': simbolo,
        'tipo_inferido': tipo_resultado,
        'operandos': [tipo1, tipo2],
        'linha': numero_linha
    })

def processar_comparacao(ctx: dict, simbolo: str, regras_semanticas: dict, numero_linha: int) -> None:
    regra = regras_semanticas.get('operadores_relacionais', {}).get(simbolo, {'aceita': []})

    ctx['idx_valor'] += 1

    if len(ctx['pilha_tipos']) < 2:
        ctx['erros'].append(
            f"ERRO SEMÂNTICO [Linha {numero_linha}]: "
            f"Comparação '{simbolo}' requer dois operandos"
        )
        return

    tipo2 = ctx['pilha_tipos'].pop()
    tipo1 = ctx['pilha_tipos'].pop()

    if ctx['pilha_valores']:
        ctx['pilha_valores'].pop()
    if ctx['pilha_valores']:
        ctx['pilha_valores'].pop()

    if tipo1 not in regra['aceita'] or tipo2 not in regra['aceita']:
        ctx['erros'].append(
            f"ERRO SEMÂNTICO [Linha {numero_linha}]: "
            f"Comparação '{simbolo}' inválida entre '{tipo1}' e '{tipo2}'"
        )

    tipo_resultado = 'booleano'

    ctx['pilha_tipos'].append(tipo_resultado)
    ctx['pilha_valores'].append(None)

    ctx['arvore_anotada'].append({
        'tipo_no': 'COMPARACAO',
        'operador': simbolo,
        'tipo_inferido': tipo_resultado,
        'operandos': [tipo1, tipo2],
        'linha': numero_linha
    })

def processar_estrutura_controle(ctx: dict, simbolo: str, numero_linha: int) -> None:
    ctx['idx_valor'] += 1

    if simbolo == 'if':
        if len(ctx['pilha_tipos']) < 3:
            ctx['erros'].append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: IF incompleto")
            return

        tipo_else = ctx['pilha_tipos'].pop()
        tipo_then = ctx['pilha_tipos'].pop()
        tipo_cond = ctx['pilha_tipos'].pop()

        if ctx['pilha_valores']:
            ctx['pilha_valores'].pop()
        if ctx['pilha_valores']:
            ctx['pilha_valores'].pop()
        if ctx['pilha_valores']:
            ctx['pilha_valores'].pop()

        if tipo_cond != 'booleano':
            ctx['erros'].append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: IF requer condição booleana")

        tipo_resultado = promoverTipo(tipo_then, tipo_else)

        ctx['pilha_tipos'].append(tipo_resultado)
        ctx['pilha_valores'].append(None)

        ctx['arvore_anotada'].append({
            'tipo_no': 'CONDICIONAL_IF',
            'tipo_inferido': tipo_resultado,
            'tipo_condicao': tipo_cond,
            'tipos_ramos': [tipo_then, tipo_else],
            'linha': numero_linha
        })
        return

    if simbolo == 'while':
        if len(ctx['pilha_tipos']) < 2:
            ctx['erros'].append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: WHILE incompleto")
            return

        tipo_corpo = ctx['pilha_tipos'].pop()
        tipo_cond = ctx['pilha_tipos'].pop()

        if ctx['pilha_valores']:
            ctx['pilha_valores'].pop()
        if ctx['pilha_valores']:
            ctx['pilha_valores'].pop()

        if tipo_cond != 'booleano':
            ctx['erros'].append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: WHILE requer condição booleana")

        tipo_resultado = tipo_corpo

        ctx['pilha_tipos'].append(tipo_resultado)
        ctx['pilha_valores'].append(None)

        ctx['arvore_anotada'].append({
            'tipo_no': 'LOOP_WHILE',
            'tipo_inferido': tipo_resultado,
            'tipo_condicao': tipo_cond,
            'tipo_corpo': tipo_corpo,
            'linha': numero_linha
        })
        return

def analisarSemantica(derivacao: list, tokens_valores: list, tabela_simbolos: dict, regras_semanticas: dict, historico_resultados: list, numero_linha: int):
    ctx = criar_contexto()
    atribuicoes_nomes = coletar_atribuicoes(tokens_valores)
    tokens_processaveis = tokens_processaveis_de(tokens_valores)
    memorias_declaradas_nesta_linha = ctx['memorias_decl_nesta_linha']
    eps = globals().get('EPS', None)

    for nao_terminal, producao in derivacao:
        if not producao:
            continue
        if eps is not None and producao == [eps]:
            continue

        for simbolo in producao:
            if simbolo in ['(', ')']:
                continue

            if simbolo == 'int':
                consumir_literal(ctx, tokens_processaveis, 'int', numero_linha)
            elif simbolo == 'float':
                consumir_literal(ctx, tokens_processaveis, 'float', numero_linha)
            elif simbolo == 'ident':
                tabela_simbolos = processar_identificador(ctx, tokens_processaveis, tabela_simbolos, atribuicoes_nomes, numero_linha)
            elif simbolo == 'res':
                processar_res(ctx, tokens_processaveis, historico_resultados, numero_linha)
            elif simbolo in ['+', '-', '*', '/', '%', '^', '|']:
                processar_operador_aritmetico(ctx, simbolo, regras_semanticas, numero_linha)
            elif simbolo in ['<', '>', '<=', '>=', '==', '!=']:
                processar_comparacao(ctx, simbolo, regras_semanticas, numero_linha)
            elif simbolo == 'if':
                processar_estrutura_controle(ctx, 'if', numero_linha)
            elif simbolo == 'while':
                processar_estrutura_controle(ctx, 'while', numero_linha)

    tipo_final = ctx['pilha_tipos'][-1] if ctx['pilha_tipos'] else 'desconhecido'
    memorias_declaradas_nesta_linha = ctx['memorias_decl_nesta_linha']

    return (tabela_simbolos, ctx['erros'], ctx['arvore_anotada'], tipo_final, memorias_declaradas_nesta_linha)

def analisarSemanticaMemoria(tabela_simbolos: dict, numero_linha: int, memorias_declaradas_nesta_linha: list[str]) -> list[str]:
    erros = []
    for nome in memorias_declaradas_nesta_linha:
        if nome in ['(', ')', '+', '-', '*', '/', '%', '^', '|',
            '<', '>', '<=', '>=', '==', '!=']:
            continue
        info = tabela_simbolos.get(nome)
        if not info:
            continue
        if info.get('linha_declaracao') == numero_linha:
            continue
    return erros

def analisarSemanticaControle(arvore_anotada: list[dict], numero_linha: int) -> list[str]:
    erros = []
    for no in arvore_anotada:
        tipo_no = no.get('tipo_no')
        tipo_cond = no.get('tipo_condicao')

        if tipo_no == 'CONDICIONAL_IF':
            if tipo_cond != 'booleano':
                erros.append(
                    f"ERRO SEMÂNTICO [Linha {numero_linha}]: "
                    "IF com condição não booleana."
                )
        elif tipo_no == 'LOOP_WHILE':
            if tipo_cond != 'booleano':
                erros.append(
                    f"ERRO SEMÂNTICO [Linha {numero_linha}]: "
                    "WHILE com condição não booleana."
                )
    return erros

def gerarArvoreAtribuida(arvore_anotada: list[dict], tipo_final: str, numero_linha: int) -> dict:
    arvore_atribuida = {
        'tipo_no': 'PROGRAMA',
        'tipo_inferido': tipo_final,
        'linha': numero_linha,
        'filhos': arvore_anotada
    }
    return arvore_atribuida

# ========================================
# FASE 4: GERAÇÃO DE CÓDIGO INTERMEDIÁRIO (TAC)
# Responsabilidade do Aluno 1
# ========================================

def gerarTAC(arvore_atribuida: dict) -> list[dict]:
    """
    Gera código intermediário em formato Three Address Code (TAC) a partir da árvore
    sintática abstrata atribuída.
    
    Parâmetros:
        arvore_atribuida: Árvore sintática abstrata com anotações de tipo da Fase 3
        
    Retorna:
        Lista de instruções TAC no formato:
        {
            'op': operador,
            'a': operando1 (opcional),
            'b': operando2 (opcional),
            'dest': destino,
            'tipo': tipo do resultado,
            'tipo_a': tipo do operando a (opcional),
            'tipo_b': tipo do operando b (opcional)
        }
    """
    tac = []
    
    # Processa a árvore atribuída
    resultado = processar_no_tac(arvore_atribuida, tac)
    
    return tac

def processar_no_tac(no: dict, tac: list) -> dict:
    """
    Processa recursivamente um nó da árvore e gera instruções TAC.
    
    Retorna um dicionário com informações sobre o resultado:
    {
        'temp': nome da variável/temporário que contém o resultado,
        'tipo': tipo do resultado,
        'kind': 'temp', 'var' ou 'imm' (temporário, variável ou imediato)
    }
    """
    tipo_no = no.get('tipo_no')
    
    if tipo_no == 'PROGRAMA':
        # Processa todos os filhos
        resultado = None
        for filho in no.get('filhos', []):
            resultado = processar_no_tac(filho, tac)
        return resultado if resultado else {'temp': None, 'tipo': 'desconhecido', 'kind': 'temp'}
    
    elif tipo_no == 'LITERAL':
        # Literais retornam valores imediatos
        valor = no.get('valor')
        tipo = no.get('tipo_inferido', 'int')
        return {
            'temp': valor,
            'tipo': tipo,
            'kind': 'imm'
        }
    
    elif tipo_no == 'LEITURA_VARIAVEL':
        # Leitura de variável retorna o nome da variável
        nome = no.get('nome')
        tipo = no.get('tipo_inferido', 'int')
        return {
            'temp': nome,
            'tipo': tipo,
            'kind': 'var'
        }
    
    elif tipo_no == 'ATRIBUICAO':
        # Atribuição: não gera instrução TAC aqui (já foi processada pela operação anterior)
        nome = no.get('nome')
        tipo = no.get('tipo_inferido', 'int')
        return {
            'temp': nome,
            'tipo': tipo,
            'kind': 'var'
        }
    
    elif tipo_no == 'OPERACAO':
        # Operação aritmética binária
        return gerar_tac_operacao(no, tac)
    
    elif tipo_no == 'COMPARACAO':
        # Operação relacional
        return gerar_tac_comparacao(no, tac)
    
    elif tipo_no == 'CONDICIONAL_IF':
        # Estrutura condicional IF
        return gerar_tac_if(no, tac)
    
    elif tipo_no == 'LOOP_WHILE':
        # Estrutura de repetição WHILE
        return gerar_tac_while(no, tac)
    
    elif tipo_no == 'RES':
        # Comando especial RES
        return gerar_tac_res(no, tac)
    
    else:
        # Nó desconhecido
        return {'temp': None, 'tipo': 'desconhecido', 'kind': 'temp'}

def gerar_tac_operacao(no: dict, tac: list) -> dict:
    """
    Gera TAC para operações aritméticas binárias.
    Suporta conversão automática de int para float quando necessário.
    """
    operador = no.get('operador')
    tipos_operandos = no.get('operandos', ['int', 'int'])
    tipo_resultado = no.get('tipo_inferido', 'int')
    
    # Como estamos em RPN, os operandos já foram processados
    # Precisamos recuperá-los da estrutura da árvore
    # Por simplificação, assumimos que temos acesso aos operandos na ordem correta
    
    # Cria temporário para o resultado
    temp_resultado = novo_temp()
    
    # Adiciona instrução TAC
    tac.append({
        'op': operador,
        'dest': temp_resultado,
        'tipo': tipo_resultado,
        'tipo_a': tipos_operandos[0] if len(tipos_operandos) > 0 else 'int',
        'tipo_b': tipos_operandos[1] if len(tipos_operandos) > 1 else 'int',
        'comment': f'{operador} operation'
    })
    
    return {
        'temp': temp_resultado,
        'tipo': tipo_resultado,
        'kind': 'temp'
    }

def gerar_tac_comparacao(no: dict, tac: list) -> dict:
    """Gera TAC para operações relacionais."""
    operador = no.get('operador')
    tipos_operandos = no.get('operandos', ['int', 'int'])
    
    temp_resultado = novo_temp()
    
    tac.append({
        'op': operador,
        'dest': temp_resultado,
        'tipo': 'booleano',
        'tipo_a': tipos_operandos[0],
        'tipo_b': tipos_operandos[1],
        'comment': f'comparison {operador}'
    })
    
    return {
        'temp': temp_resultado,
        'tipo': 'booleano',
        'kind': 'temp'
    }

def gerar_tac_if(no: dict, tac: list) -> dict:
    """
    Gera TAC para estrutura condicional IF.
    Formato: (condição then else IF)
    """
    tipo_resultado = no.get('tipo_inferido', 'int')
    
    # Cria labels
    label_else = novo_label()
    label_end = novo_label()
    
    # Temporário para o resultado final
    temp_resultado = novo_temp()
    
    # Instrução de salto condicional
    tac.append({
        'op': 'ifFalse',
        'dest': label_else,
        'tipo': 'booleano',
        'comment': 'if condition check'
    })
    
    # Ramo then (será processado posteriormente)
    tac.append({
        'op': '=',
        'dest': temp_resultado,
        'tipo': tipo_resultado,
        'comment': 'then branch result'
    })
    
    # Salto para o fim
    tac.append({
        'op': 'goto',
        'dest': label_end,
        'comment': 'skip else branch'
    })
    
    # Label do else
    tac.append({
        'op': 'label',
        'dest': label_else,
        'comment': 'else branch'
    })
    
    # Ramo else
    tac.append({
        'op': '=',
        'dest': temp_resultado,
        'tipo': tipo_resultado,
        'comment': 'else branch result'
    })
    
    # Label do fim
    tac.append({
        'op': 'label',
        'dest': label_end,
        'comment': 'end if'
    })
    
    return {
        'temp': temp_resultado,
        'tipo': tipo_resultado,
        'kind': 'temp'
    }

def gerar_tac_while(no: dict, tac: list) -> dict:
    """
    Gera TAC para estrutura de repetição WHILE.
    Formato: (condição corpo WHILE)
    """
    tipo_resultado = no.get('tipo_inferido', 'int')
    
    # Cria labels
    label_inicio = novo_label()
    label_fim = novo_label()
    
    # Temporário para o resultado
    temp_resultado = novo_temp()
    
    # Label de início do loop
    tac.append({
        'op': 'label',
        'dest': label_inicio,
        'comment': 'while loop start'
    })
    
    # Avaliação da condição
    tac.append({
        'op': 'ifFalse',
        'dest': label_fim,
        'tipo': 'booleano',
        'comment': 'while condition check'
    })
    
    # Corpo do loop (será processado posteriormente)
    tac.append({
        'op': '=',
        'dest': temp_resultado,
        'tipo': tipo_resultado,
        'comment': 'loop body result'
    })
    
    # Salto de volta para o início
    tac.append({
        'op': 'goto',
        'dest': label_inicio,
        'comment': 'repeat loop'
    })
    
    # Label de fim do loop
    tac.append({
        'op': 'label',
        'dest': label_fim,
        'comment': 'while loop end'
    })
    
    return {
        'temp': temp_resultado,
        'tipo': tipo_resultado,
        'kind': 'temp'
    }

def gerar_tac_res(no: dict, tac: list) -> dict:
    """
    Gera TAC para comando RES.
    RES recupera o resultado de N linhas anteriores.
    """
    parametro = no.get('parametro', 0)
    tipo_resultado = no.get('tipo_inferido', 'int')
    
    temp_resultado = novo_temp()
    
    tac.append({
        'op': 'res',
        'a': parametro,
        'dest': temp_resultado,
        'tipo': tipo_resultado,
        'comment': f'RES({parametro})'
    })
    
    return {
        'temp': temp_resultado,
        'tipo': tipo_resultado,
        'kind': 'temp'
    }

def salvar_tac(tac: list, nome_arquivo: str = 'tac.txt') -> None:
    """
    Salva o TAC gerado em um arquivo de texto legível.
    """
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("THREE ADDRESS CODE (TAC)\n")
        f.write("=" * 60 + "\n\n")
        
        for i, inst in enumerate(tac):
            op = inst.get('op')
            
            if op == 'label':
                f.write(f"{inst['dest']}:\n")
            
            elif op == 'goto':
                f.write(f"  goto {inst['dest']}\n")
            
            elif op == 'ifFalse':
                f.write(f"  ifFalse {inst.get('a', '?')} goto {inst['dest']}\n")
            
            elif op == '=':
                a = inst.get('a', '?')
                dest = inst.get('dest')
                f.write(f"  {dest} = {a}\n")
            
            elif op in ['+', '-', '*', '/', '|', '%', '^']:
                a = inst.get('a', '?')
                b = inst.get('b', '?')
                dest = inst.get('dest')
                f.write(f"  {dest} = {a} {op} {b}\n")
            
            elif op in ['<', '>', '<=', '>=', '==', '!=']:
                a = inst.get('a', '?')
                b = inst.get('b', '?')
                dest = inst.get('dest')
                f.write(f"  {dest} = {a} {op} {b}\n")
            
            elif op == 'res':
                a = inst.get('a')
                dest = inst.get('dest')
                f.write(f"  {dest} = RES({a})\n")
            
            else:
                f.write(f"  {inst}\n")
            
            # Adiciona comentário se existir
            comment = inst.get('comment')
            if comment:
                f.write(f"    ; {comment}\n")
        
        f.write("\n" + "=" * 60 + "\n")

# ========================================
# OTIMIZAÇÃO DE TAC (Aluno 2)
# ========================================

def otimizarTAC(tac: list) -> list:
    """
    Aplica técnicas de otimização no código TAC.
    
    Implementa:
    1. Constant Folding (avaliação de expressões constantes)
    2. Constant Propagation (propagação de constantes)
    3. Dead Code Elimination (eliminação de código morto)
    4. Eliminação de Saltos Redundantes
    
    Cada otimização é aplicada em múltiplas passagens até não haver mais mudanças.
    """
    tac_otimizado = list(tac)  # Cópia para não modificar original
    
    mudou = True
    iteracao = 0
    max_iteracoes = 10  # Previne loops infinitos
    
    while mudou and iteracao < max_iteracoes:
        mudou = False
        tamanho_antes = len(tac_otimizado)
        
        # Aplica otimizações em ordem
        tac_otimizado = constant_folding(tac_otimizado)
        tac_otimizado = constant_propagation(tac_otimizado)
        tac_otimizado = dead_code_elimination(tac_otimizado)
        tac_otimizado = eliminar_saltos_redundantes(tac_otimizado)
        
        # Verifica se houve mudança
        if len(tac_otimizado) != tamanho_antes:
            mudou = True
        
        iteracao += 1
    
    return tac_otimizado

# ========================================
# 1. CONSTANT FOLDING
# ========================================

def constant_folding(tac: list) -> list:
    """
    Avalia expressões constantes em tempo de compilação.
    
    Exemplos:
        t1 = 2 + 3  →  t1 = 5
        t2 = 4 * 5  →  t2 = 20
        t3 = 10 / 2 →  t3 = 5
    """
    tac_otimizado = []
    
    for inst in tac:
        op = inst.get('op')
        
        # Operações aritméticas binárias
        if op in ['+', '-', '*', '/', '|', '%', '^']:
            a = inst.get('a')
            b = inst.get('b')
            
            # Verifica se ambos operandos são constantes numéricas
            if eh_constante_numerica(a) and eh_constante_numerica(b):
                try:
                    resultado = avaliar_operacao(op, a, b)
                    
                    # Substitui operação por atribuição direta
                    tac_otimizado.append({
                        'op': '=',
                        'a': resultado,
                        'dest': inst.get('dest'),
                        'tipo': inst.get('tipo', 'int'),
                        'comment': f'constant folding: {a} {op} {b} = {resultado}'
                    })
                    continue
                except:
                    # Se houver erro (divisão por zero, etc), mantém instrução original
                    pass
        
        # Operações relacionais
        elif op in ['<', '>', '<=', '>=', '==', '!=']:
            a = inst.get('a')
            b = inst.get('b')
            
            if eh_constante_numerica(a) and eh_constante_numerica(b):
                try:
                    resultado = avaliar_comparacao(op, a, b)
                    
                    tac_otimizado.append({
                        'op': '=',
                        'a': 1 if resultado else 0,  # booleano como inteiro
                        'dest': inst.get('dest'),
                        'tipo': 'booleano',
                        'comment': f'constant folding: {a} {op} {b} = {resultado}'
                    })
                    continue
                except:
                    pass
        
        # Mantém instrução original se não foi otimizada
        tac_otimizado.append(inst)
    
    return tac_otimizado

def eh_constante_numerica(valor) -> bool:
    """Verifica se um valor é uma constante numérica (int ou float)."""
    return isinstance(valor, (int, float))

def avaliar_operacao(op: str, a, b):
    """Avalia uma operação aritmética entre duas constantes."""
    a = float(a) if isinstance(a, (int, float)) else 0
    b = float(b) if isinstance(b, (int, float)) else 0
    
    if op == '+':
        return a + b
    elif op == '-':
        return a - b
    elif op == '*':
        return a * b
    elif op == '/':
        if b == 0:
            raise ValueError("Divisão por zero")
        return int(a // b)  # Divisão inteira
    elif op == '|':
        if b == 0:
            raise ValueError("Divisão por zero")
        return a / b  # Divisão float
    elif op == '%':
        if b == 0:
            raise ValueError("Divisão por zero")
        return int(a % b)
    elif op == '^':
        return a ** b
    else:
        raise ValueError(f"Operador desconhecido: {op}")

def avaliar_comparacao(op: str, a, b) -> bool:
    """Avalia uma comparação entre duas constantes."""
    a = float(a) if isinstance(a, (int, float)) else 0
    b = float(b) if isinstance(b, (int, float)) else 0
    
    if op == '<':
        return a < b
    elif op == '>':
        return a > b
    elif op == '<=':
        return a <= b
    elif op == '>=':
        return a >= b
    elif op == '==':
        return abs(a - b) < 1e-9  # Comparação com tolerância para floats
    elif op == '!=':
        return abs(a - b) >= 1e-9
    else:
        raise ValueError(f"Operador de comparação desconhecido: {op}")

# ========================================
# 2. CONSTANT PROPAGATION
# ========================================

def constant_propagation(tac: list) -> list:
    """
    Propaga valores constantes através do código.
    
    Exemplos:
        t1 = 5
        t2 = t1 + 3  →  t2 = 5 + 3  →  t2 = 8
    """
    tac_otimizado = []
    constantes = {}  # Mapa de variáveis → valores constantes conhecidos
    
    for inst in tac:
        op = inst.get('op')
        
        # Atribuição de constante
        if op == '=':
            a = inst.get('a')
            dest = inst.get('dest')
            
            # Se atribui constante, registra no mapa
            if eh_constante_numerica(a):
                constantes[dest] = a
                tac_otimizado.append(inst)
            
            # Se atribui variável que é constante conhecida, propaga
            elif a in constantes:
                valor_constante = constantes[a]
                constantes[dest] = valor_constante
                
                tac_otimizado.append({
                    'op': '=',
                    'a': valor_constante,
                    'dest': dest,
                    'tipo': inst.get('tipo', 'int'),
                    'comment': f'constant propagation: {a} → {valor_constante}'
                })
            else:
                # Variável não é constante, remove do mapa se existir
                if dest in constantes:
                    del constantes[dest]
                tac_otimizado.append(inst)
        
        # Operações binárias
        elif op in ['+', '-', '*', '/', '|', '%', '^', '<', '>', '<=', '>=', '==', '!=']:
            a = inst.get('a')
            b = inst.get('b')
            dest = inst.get('dest')
            
            # Substitui operandos por valores constantes se conhecidos
            a_substituido = constantes.get(a, a) if not eh_constante_numerica(a) else a
            b_substituido = constantes.get(b, b) if not eh_constante_numerica(b) else b
            
            nova_inst = dict(inst)
            nova_inst['a'] = a_substituido
            nova_inst['b'] = b_substituido
            
            # Se operandos mudaram, adiciona comentário
            if a_substituido != a or b_substituido != b:
                nova_inst['comment'] = f'constant propagation: {a}→{a_substituido}, {b}→{b_substituido}'
            
            tac_otimizado.append(nova_inst)
            
            # Destino não é mais constante conhecida
            if dest in constantes:
                del constantes[dest]
        
        # Saltos condicionais
        elif op in ['ifFalse', 'if']:
            a = inst.get('a')
            
            if a and not eh_constante_numerica(a) and a in constantes:
                nova_inst = dict(inst)
                nova_inst['a'] = constantes[a]
                nova_inst['comment'] = f'constant propagation: {a} → {constantes[a]}'
                tac_otimizado.append(nova_inst)
            else:
                tac_otimizado.append(inst)
        
        # Labels e outros: mantém e limpa conhecimento de constantes (conservador)
        elif op == 'label':
            constantes.clear()  # Labels podem ser alvos de saltos, invalida análise
            tac_otimizado.append(inst)
        
        else:
            tac_otimizado.append(inst)
    
    return tac_otimizado

# ========================================
# 3. DEAD CODE ELIMINATION
# ========================================

def dead_code_elimination(tac: list) -> list:
    """
    Remove código morto (instruções cujo resultado nunca é usado).
    
    Implementa análise de liveness básica:
    1. Identifica quais variáveis são usadas
    2. Remove atribuições a variáveis nunca usadas
    """
    # Primeira passagem: identifica todas as variáveis usadas
    variaveis_usadas = set()
    variaveis_importantes = set()  # Variáveis que não podem ser removidas
    
    for inst in tac:
        op = inst.get('op')
        
        # Marca operandos como usados
        if op in ['+', '-', '*', '/', '|', '%', '^', '<', '>', '<=', '>=', '==', '!=']:
            a = inst.get('a')
            b = inst.get('b')
            if a and not eh_constante_numerica(a):
                variaveis_usadas.add(a)
            if b and not eh_constante_numerica(b):
                variaveis_usadas.add(b)
        
        elif op == '=':
            a = inst.get('a')
            if a and not eh_constante_numerica(a):
                variaveis_usadas.add(a)
        
        elif op in ['ifFalse', 'if', 'return']:
            a = inst.get('a')
            if a and not eh_constante_numerica(a):
                variaveis_usadas.add(a)
                variaveis_importantes.add(a)  # Condições são importantes
        
        # RES e chamadas são sempre importantes
        elif op in ['res', 'call']:
            dest = inst.get('dest')
            if dest:
                variaveis_importantes.add(dest)
    
    # Segunda passagem: remove código morto
    tac_otimizado = []
    
    for inst in tac:
        op = inst.get('op')
        dest = inst.get('dest')
        
        # Atribuições a variáveis nunca usadas podem ser removidas
        if op in ['=', '+', '-', '*', '/', '|', '%', '^', '<', '>', '<=', '>=', '==', '!=']:
            # Se é temporário não usado E não é importante, remove
            if dest and dest.startswith('t') and dest not in variaveis_usadas and dest not in variaveis_importantes:
                # Código morto detectado, não adiciona à saída
                continue
        
        # Mantém instrução
        tac_otimizado.append(inst)
    
    return tac_otimizado

# ========================================
# 4. ELIMINAÇÃO DE SALTOS REDUNDANTES
# ========================================

def eliminar_saltos_redundantes(tac: list) -> list:
    """
    Remove saltos redundantes e labels não utilizados.
    
    Otimizações:
    1. goto L1 seguido imediatamente por L1: → remove goto
    2. Labels nunca referenciados → remove label
    3. Sequências de gotos → simplifica
    """
    # Primeira passagem: identifica labels referenciados
    labels_referenciados = set()
    
    for inst in tac:
        op = inst.get('op')
        
        if op in ['goto', 'ifFalse', 'if']:
            dest = inst.get('dest')
            if dest:
                labels_referenciados.add(dest)
    
    # Segunda passagem: remove saltos e labels redundantes
    tac_otimizado = []
    i = 0
    
    while i < len(tac):
        inst = tac[i]
        op = inst.get('op')
        
        # Caso 1: goto seguido imediatamente pelo label alvo
        if op == 'goto' and i + 1 < len(tac):
            proximo = tac[i + 1]
            if proximo.get('op') == 'label' and proximo.get('dest') == inst.get('dest'):
                # Salto redundante, não adiciona
                i += 1
                continue
        
        # Caso 2: Label nunca referenciado
        if op == 'label':
            dest = inst.get('dest')
            if dest not in labels_referenciados:
                # Label não usado, não adiciona
                i += 1
                continue
        
        # Mantém instrução
        tac_otimizado.append(inst)
        i += 1
    
    return tac_otimizado

# ========================================
# ANÁLISE E RELATÓRIO DE OTIMIZAÇÕES
# ========================================

def gerar_relatorio_otimizacoes(tac_original: list, tac_otimizado: list, nome_arquivo: str = 'otimizacoes.md') -> None:
    """
    Gera um relatório detalhado das otimizações aplicadas.
    """
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        f.write("# Relatório de Otimizações\n\n")
        
        # Estatísticas gerais
        f.write("## Estatísticas Gerais\n\n")
        f.write(f"- **Instruções TAC original**: {len(tac_original)}\n")
        f.write(f"- **Instruções TAC otimizado**: {len(tac_otimizado)}\n")
        
        reducao = len(tac_original) - len(tac_otimizado)
        percentual = (reducao / len(tac_original) * 100) if len(tac_original) > 0 else 0
        f.write(f"- **Instruções removidas**: {reducao} ({percentual:.1f}%)\n\n")
        
        # Conta temporários
        temps_original = contar_temporarios(tac_original)
        temps_otimizado = contar_temporarios(tac_otimizado)
        f.write(f"- **Temporários no TAC original**: {temps_original}\n")
        f.write(f"- **Temporários no TAC otimizado**: {temps_otimizado}\n")
        f.write(f"- **Temporários eliminados**: {temps_original - temps_otimizado}\n\n")
        
        # Técnicas de otimização
        f.write("## Técnicas de Otimização Implementadas\n\n")
        
        f.write("### 1. Constant Folding\n")
        f.write("Avalia expressões constantes em tempo de compilação.\n\n")
        f.write("**Exemplo:**\n```\n")
        f.write("Antes:  t1 = 2 + 3\n")
        f.write("Depois: t1 = 5\n```\n\n")
        
        f.write("### 2. Constant Propagation\n")
        f.write("Propaga valores constantes através do código.\n\n")
        f.write("**Exemplo:**\n```\n")
        f.write("Antes:  t1 = 5\n")
        f.write("        t2 = t1 + 3\n")
        f.write("Depois: t1 = 5\n")
        f.write("        t2 = 5 + 3  →  t2 = 8\n```\n\n")
        
        f.write("### 3. Dead Code Elimination\n")
        f.write("Remove código que não afeta o resultado do programa.\n\n")
        f.write("**Exemplo:**\n```\n")
        f.write("Antes:  t1 = 5\n")
        f.write("        t2 = 3      ; t2 nunca é usado\n")
        f.write("        t3 = t1 + 2\n")
        f.write("Depois: t1 = 5\n")
        f.write("        t3 = t1 + 2\n```\n\n")
        
        f.write("### 4. Eliminação de Saltos Redundantes\n")
        f.write("Remove saltos desnecessários e labels não utilizados.\n\n")
        f.write("**Exemplo:**\n```\n")
        f.write("Antes:  goto L1\n")
        f.write("        L1:\n")
        f.write("Depois: L1:\n```\n\n")
        
        # Análise detalhada
        f.write("## Comparação TAC Original vs Otimizado\n\n")
        f.write("### TAC Original\n```\n")
        for inst in tac_original[:20]:  # Primeiras 20 instruções
            f.write(formatar_instrucao_tac(inst) + "\n")
        if len(tac_original) > 20:
            f.write(f"... ({len(tac_original) - 20} instruções omitidas)\n")
        f.write("```\n\n")
        
        f.write("### TAC Otimizado\n```\n")
        for inst in tac_otimizado[:20]:
            f.write(formatar_instrucao_tac(inst) + "\n")
        if len(tac_otimizado) > 20:
            f.write(f"... ({len(tac_otimizado) - 20} instruções omitidas)\n")
        f.write("```\n\n")

def contar_temporarios(tac: list) -> int:
    """Conta o número de variáveis temporárias únicas no TAC."""
    temporarios = set()
    
    for inst in tac:
        dest = inst.get('dest')
        if dest and dest.startswith('t'):
            temporarios.add(dest)
        
        a = inst.get('a')
        if a and isinstance(a, str) and a.startswith('t'):
            temporarios.add(a)
        
        b = inst.get('b')
        if b and isinstance(b, str) and b.startswith('t'):
            temporarios.add(b)
    
    return len(temporarios)

def formatar_instrucao_tac(inst: dict) -> str:
    """Formata uma instrução TAC para exibição legível."""
    op = inst.get('op')
    
    if op == 'label':
        return f"{inst['dest']}:"
    elif op == 'goto':
        return f"  goto {inst['dest']}"
    elif op == 'ifFalse':
        return f"  ifFalse {inst.get('a', '?')} goto {inst['dest']}"
    elif op == '=':
        return f"  {inst['dest']} = {inst.get('a', '?')}"
    elif op in ['+', '-', '*', '/', '|', '%', '^', '<', '>', '<=', '>=', '==', '!=']:
        return f"  {inst['dest']} = {inst.get('a', '?')} {op} {inst.get('b', '?')}"
    elif op == 'res':
        return f"  {inst['dest']} = RES({inst.get('a')})"
    else:
        return f"  {inst}"

def salvar_tac_otimizado(tac: list, nome_arquivo: str = 'tac_otimizado.txt') -> None:
    """Salva o TAC otimizado (mesmo formato do TAC original)."""
    salvar_tac(tac, nome_arquivo)

# ========================================
# PREPARAÇÃO PARA GERAÇÃO DE ASSEMBLY (Aluno 3)
# ========================================

def gerarAssembly(tacOtimizado: list, tabela_simbolos: dict) -> list:
    """
    Gera código Assembly AVR a partir do TAC otimizado.
    
    Esta função será implementada pelo Aluno 3.
    
    Parâmetros:
        tacOtimizado: Lista de instruções TAC após otimização
        tabela_simbolos: Tabela de símbolos com informações de variáveis
        
    Retorna:
        Lista de linhas de código Assembly
    """
    # TODO: Implementar geração de Assembly (Aluno 3)
    assembly = []
    assembly.append("; Assembly AVR para Arduino Uno (ATmega328P)")
    assembly.append("; TODO: Implementar geração de código")
    return assembly

# ========================================
# FUNÇÃO MAIN (Aluno 4)
# ========================================

def main():
    """
    Função principal que orquestra todas as fases do compilador.
    Gera todos os relatórios e arquivos intermediários necessários.
    """
    if len(sys.argv) < 2:
        print("Uso correto: python trabalho.py <arquivo_de_entrada>")
        print("Exemplo: python trabalho.py fatorial.txt")
        return 1

    caminho = sys.argv[1]
    nome_base = caminho.rsplit('.', 1)[0]  # Remove extensão para usar como base

    # Lê o arquivo de entrada
    linhas = lerArquivo(caminho)
    if linhas is None:
        return 1

    # Estruturas principais
    tabela_simbolos = inicializarTabelaSimbolos()
    historico_resultados = []
    todos_erros = []
    todas_arvores = []
    tac_completo = []
    todos_tokens = []  # Para relatório léxico
    todas_derivacoes = []  # Para relatório sintático

    # Define as regras semânticas
    regras_semanticas = definirGramaticaAtributos()

    # Constrói a gramática LL(1)
    try:
        G, FIRST, FOLLOW, tabelaLL1 = construirGramatica()
        print("✓ Gramática LL(1) construída com sucesso.")
    except Exception as e:
        print(f"✗ Erro ao construir a gramática: {e}")
        return 1

    print("\n" + "="*60)
    print("INICIANDO COMPILAÇÃO")
    print("="*60)

    # Processa cada linha do arquivo
    for numero_linha, linha in enumerate(linhas, start=1):
        print(f"\n--- Linha {numero_linha}: {linha}")

        try:
            # Fase 1: Análise Léxica
            tokens_originais = []
            parseExpressao(linha, tokens_originais)
            tokens, tokens_valores = analisadorLexico(tokens_originais)
            
            todos_tokens.append({
                'linha': numero_linha,
                'codigo': linha,
                'tokens': tokens,
                'valores': tokens_valores
            })
            
            print(f"  ✓ Léxico: {len(tokens)} tokens")

            # Fase 2: Análise Sintática
            derivacao = analisadorSintatico(tokens, tabelaLL1)
            
            todas_derivacoes.append({
                'linha': numero_linha,
                'derivacao': derivacao
            })
            
            print(f"  ✓ Sintático: {len(derivacao)} produções")

            # Fase 3: Análise Semântica
            tabela_simbolos, erros, arvore_anotada, tipo_final, memorias_declaradas_nesta_linha = analisarSemantica(
                derivacao, tokens_valores, tabela_simbolos,
                regras_semanticas, historico_resultados, numero_linha
            )

            erros.extend(analisarSemanticaMemoria(tabela_simbolos, numero_linha, memorias_declaradas_nesta_linha))
            erros.extend(analisarSemanticaControle(arvore_anotada, numero_linha))

            arvore_atribuida = gerarArvoreAtribuida(arvore_anotada, tipo_final, numero_linha)
            todas_arvores.append(arvore_atribuida)

            historico_resultados.append({
                'linha': numero_linha,
                'tipo': tipo_final,
                'arvore': arvore_atribuida
            })

            if erros:
                print(f"  ✗ Semântico: {len(erros)} erro(s)")
                for e in erros:
                    todos_erros.append(e)
            else:
                print(f"  ✓ Semântico: OK (tipo: {tipo_final})")

            # Fase 4: Geração de TAC
            resetar_contadores_tac()
            tac_linha = gerarTAC(arvore_atribuida)
            tac_completo.extend(tac_linha)
            print(f"  ✓ TAC: {len(tac_linha)} instruções")

        except ValueError as e:
            msg = str(e)
            todos_erros.append(msg)
            print(f"  ✗ {msg}")

    # ========================================
    # GERAÇÃO DE RELATÓRIOS E ARQUIVOS
    # ========================================
    
    print("\n" + "="*60)
    print("GERANDO RELATÓRIOS")
    print("="*60)
    
    # 1. Relatório Léxico
    gerar_relatorio_lexico(todos_tokens, f'{nome_base}_tokens.txt')
    print(f"✓ Relatório léxico: {nome_base}_tokens.txt")
    
    # 2. Relatório Sintático
    gerar_relatorio_sintatico(todas_derivacoes, f'{nome_base}_derivacoes.txt')
    print(f"✓ Relatório sintático: {nome_base}_derivacoes.txt")
    
    # 3. Relatório Semântico (Árvore Atribuída)
    gerar_relatorio_semantico(todas_arvores, tabela_simbolos, f'{nome_base}_arvore.txt')
    print(f"✓ Relatório semântico: {nome_base}_arvore.txt")
    
    # 4. TAC Original
    salvar_tac(tac_completo, f'{nome_base}_tac.txt')
    print(f"✓ TAC original: {nome_base}_tac.txt")

    # 5. Otimização de TAC
    tac_otimizado = otimizarTAC(tac_completo)
    salvar_tac_otimizado(tac_otimizado, f'{nome_base}_tac_otimizado.txt')
    print(f"✓ TAC otimizado: {nome_base}_tac_otimizado.txt")
    
    # 6. Relatório de Otimizações
    gerar_relatorio_otimizacoes(tac_completo, tac_otimizado, f'{nome_base}_otimizacoes.md')
    print(f"✓ Relatório otimizações: {nome_base}_otimizacoes.md")
    
    # 7. Tabela de Símbolos
    gerar_relatorio_tabela_simbolos(tabela_simbolos, f'{nome_base}_simbolos.txt')
    print(f"✓ Tabela de símbolos: {nome_base}_simbolos.txt")

    # ========================================
    # RESUMO FINAL
    # ========================================
    
    print("\n" + "="*60)
    print("RESUMO DA COMPILAÇÃO")
    print("="*60)
    print(f"Arquivo processado: {caminho}")
    print(f"Linhas de código: {len(linhas)}")
    print(f"Tokens gerados: {sum(len(t['tokens']) for t in todos_tokens)}")
    print(f"Instruções TAC originais: {len(tac_completo)}")
    print(f"Instruções TAC otimizadas: {len(tac_otimizado)}")
    
    if len(tac_completo) > 0:
        reducao = len(tac_completo) - len(tac_otimizado)
        percentual = (reducao / len(tac_completo) * 100)
        print(f"Otimização: {reducao} instruções removidas ({percentual:.1f}%)")
    
    print(f"Variáveis declaradas: {len(tabela_simbolos)}")
    print(f"Erros encontrados: {len(todos_erros)}")
    
    if todos_erros:
        print("\n" + "="*60)
        print("ERROS DETECTADOS")
        print("="*60)
        for i, erro in enumerate(todos_erros, 1):
            print(f"{i}. {erro}")
        print("\n⚠ Compilação concluída COM ERROS")
        return 1
    else:
        print("\n✓ Compilação concluída COM SUCESSO")
        print("Todos os relatórios foram gerados.")
        return 0

# ========================================
# FUNÇÕES DE GERAÇÃO DE RELATÓRIOS
# ========================================

def gerar_relatorio_lexico(todos_tokens: list, nome_arquivo: str) -> None:
    """Gera relatório detalhado da análise léxica."""
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("RELATÓRIO DE ANÁLISE LÉXICA\n")
        f.write("=" * 60 + "\n\n")
        
        for item in todos_tokens:
            f.write(f"Linha {item['linha']}: {item['codigo']}\n")
            f.write("-" * 60 + "\n")
            f.write(f"Total de tokens: {len(item['tokens'])}\n\n")
            
            f.write("Tokens identificados:\n")
            for i, (tipo, valor) in enumerate(zip(item['tokens'], item['valores']), 1):
                f.write(f"  {i:2d}. Tipo: {tipo:10s} | Valor: {valor}\n")
            
            f.write("\n")

def gerar_relatorio_sintatico(todas_derivacoes: list, nome_arquivo: str) -> None:
    """Gera relatório detalhado da análise sintática."""
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("RELATÓRIO DE ANÁLISE SINTÁTICA\n")
        f.write("=" * 60 + "\n\n")
        
        for item in todas_derivacoes:
            f.write(f"Linha {item['linha']}:\n")
            f.write("-" * 60 + "\n")
            f.write(f"Total de produções: {len(item['derivacao'])}\n\n")
            
            f.write("Derivação (produções aplicadas):\n")
            for i, (nao_terminal, producao) in enumerate(item['derivacao'], 1):
                prod_str = ' '.join(producao) if producao else 'ε'
                f.write(f"  {i:2d}. {nao_terminal:10s} → {prod_str}\n")
            
            f.write("\n")

def gerar_relatorio_semantico(todas_arvores: list, tabela_simbolos: dict, nome_arquivo: str) -> None:
    """Gera relatório detalhado da análise semântica com árvore atribuída."""
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("RELATÓRIO DE ANÁLISE SEMÂNTICA\n")
        f.write("=" * 60 + "\n\n")
        
        for arvore in todas_arvores:
            f.write(f"Linha {arvore['linha']}:\n")
            f.write("-" * 60 + "\n")
            f.write(f"Tipo inferido: {arvore['tipo_inferido']}\n\n")
            
            f.write("Árvore Sintática Abstrata Atribuída:\n")
            imprimir_arvore_recursiva(f, arvore, 0)
            f.write("\n")
        
        f.write("=" * 60 + "\n")
        f.write("TABELA DE SÍMBOLOS (resumo)\n")
        f.write("=" * 60 + "\n\n")
        
        if tabela_simbolos:
            f.write(f"{'Nome':<15} {'Tipo':<10} {'Inicializada':<12} {'Linha':<6} {'Usada':<6}\n")
            f.write("-" * 60 + "\n")
            for nome, info in sorted(tabela_simbolos.items()):
                tipo = info.get('tipo', 'N/A')
                inic = 'Sim' if info.get('inicializada') else 'Não'
                linha = info.get('linha_declaracao', 0)
                usada = 'Sim' if info.get('usada') else 'Não'
                f.write(f"{nome:<15} {tipo:<10} {inic:<12} {linha:<6} {usada:<6}\n")
        else:
            f.write("(Nenhuma variável declarada)\n")

def imprimir_arvore_recursiva(f, no: dict, nivel: int) -> None:
    """Imprime a árvore de forma recursiva e indentada."""
    indent = "  " * nivel
    tipo_no = no.get('tipo_no', 'DESCONHECIDO')
    tipo_inferido = no.get('tipo_inferido', 'N/A')
    
    f.write(f"{indent}[{tipo_no}] tipo: {tipo_inferido}\n")
    
    # Informações adicionais dependendo do tipo de nó
    if tipo_no == 'LITERAL':
        valor = no.get('valor')
        f.write(f"{indent}  valor: {valor}\n")
    
    elif tipo_no in ['ATRIBUICAO', 'LEITURA_VARIAVEL']:
        nome = no.get('nome')
        f.write(f"{indent}  nome: {nome}\n")
    
    elif tipo_no == 'OPERACAO':
        operador = no.get('operador')
        operandos = no.get('operandos', [])
        f.write(f"{indent}  operador: {operador}\n")
        f.write(f"{indent}  operandos: {operandos}\n")
    
    elif tipo_no == 'COMPARACAO':
        operador = no.get('operador')
        operandos = no.get('operandos', [])
        f.write(f"{indent}  comparador: {operador}\n")
        f.write(f"{indent}  operandos: {operandos}\n")
    
    elif tipo_no == 'RES':
        parametro = no.get('parametro')
        f.write(f"{indent}  parâmetro: {parametro}\n")
    
    elif tipo_no == 'CONDICIONAL_IF':
        tipo_cond = no.get('tipo_condicao')
        tipos_ramos = no.get('tipos_ramos', [])
        f.write(f"{indent}  condição tipo: {tipo_cond}\n")
        f.write(f"{indent}  ramos tipos: {tipos_ramos}\n")
    
    elif tipo_no == 'LOOP_WHILE':
        tipo_cond = no.get('tipo_condicao')
        tipo_corpo = no.get('tipo_corpo')
        f.write(f"{indent}  condição tipo: {tipo_cond}\n")
        f.write(f"{indent}  corpo tipo: {tipo_corpo}\n")
    
    # Processa filhos recursivamente
    filhos = no.get('filhos', [])
    if filhos:
        f.write(f"{indent}  filhos:\n")
        for filho in filhos:
            imprimir_arvore_recursiva(f, filho, nivel + 2)

def gerar_relatorio_tabela_simbolos(tabela_simbolos: dict, nome_arquivo: str) -> None:
    """Gera relatório completo da tabela de símbolos."""
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("TABELA DE SÍMBOLOS\n")
        f.write("=" * 60 + "\n\n")
        
        if not tabela_simbolos:
            f.write("(Nenhuma variável declarada)\n")
            return
        
        for nome, info in sorted(tabela_simbolos.items()):
            f.write(f"Símbolo: {nome}\n")
            f.write("-" * 40 + "\n")
            f.write(f"  Tipo: {info.get('tipo', 'N/A')}\n")
            f.write(f"  Inicializada: {'Sim' if info.get('inicializada') else 'Não'}\n")
            f.write(f"  Valor: {info.get('valor', 'N/A')}\n")
            f.write(f"  Linha declaração: {info.get('linha_declaracao', 0)}\n")
            f.write(f"  Escopo: {info.get('escopo', 'global')}\n")
            f.write(f"  Usada: {'Sim' if info.get('usada') else 'Não'}\n")
            
            linhas_uso = info.get('linhas_uso', [])
            if linhas_uso:
                f.write(f"  Linhas de uso: {', '.join(map(str, linhas_uso))}\n")
            
            f.write("\n")

if __name__ == "__main__":
    sys.exit(main() or 0)
