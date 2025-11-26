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
    linha = linha.strip()

    while i < len(linha):
        char = linha[i]

        if char.isspace():
            if token:
                _tokens_.append(token)
                token = ""
                i += 1
                continue

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

        if estadoOperador(token) and not estadoComparador(token):
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
    # ESTRATÉGIA MELHORADA: Procura por padrões de atribuição em RPN
    # Padrão: número seguido de identificador (dentro de parênteses)
    
    i = 0
    while i < len(tokens_valores):
        token = tokens_valores[i]
        
        if token == '(':
            # Dentro de parênteses, procura por padrão: valor identificador
            j = i + 1
            while j < len(tokens_valores) and tokens_valores[j] != ')':
                if (isinstance(tokens_valores[j], (int, float)) and 
                    j + 1 < len(tokens_valores) and 
                    isinstance(tokens_valores[j + 1], str) and
                    tokens_valores[j + 1] not in ['(', ')', '+', '-', '*', '/', '<=', '>=', 'WHILE', 'IF']):
                    
                    atribuicoes.add(tokens_valores[j + 1])
                    j += 2
                else:
                    j += 1
            i = j
        else:
            i += 1

    return atribuicoes

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

    no_literal = {
        'tipo_no': 'LITERAL',
        'tipo_inferido': tipo,
        'valor': valor,
        'linha': linha
    }

    ctx['pilha_nos'].append(no_literal)
    ctx['pilha_tipos'].append(tipo)
    ctx['pilha_valores'].append(valor)
    ctx['arvore_anotada'].append(no_literal)

def processar_identificador(ctx, tokens_processaveis, tabela_simbolos, atribuicoes, linha):
    """Processa identificadores (variáveis), tratando atribuição e leitura."""

    # Consome próximo token
    if ctx['idx_valor'] >= len(tokens_processaveis):
        ctx['erros'].append(
            f"ERRO SEMÂNTICO [Linha {linha}]: Identificador esperado, mas tokens acabaram."
        )
        return tabela_simbolos

    ident = tokens_processaveis[ctx['idx_valor']]
    ctx['idx_valor'] += 1

    # Se for atribuição detectada em coletar_atribuicoes
    if ident in atribuicoes:
        no_ident = {
            'tipo_no': 'ATRIBUICAO',
            'nome': ident,
            'linha': linha
        }
        ctx['pilha_nos'].append(no_ident)
        ctx['pilha_tipos'].append('int')
        ctx['pilha_valores'].append(None)
        ctx['arvore_anotada'].append(no_ident)

        # Registro na tabela de símbolos
        tabela_simbolos = adicionarSimbolo(
            tabela_simbolos,
            ident,
            tipo='int',
            inicializada=True,
            valor=None,
            linha=linha
        )

        return tabela_simbolos

    # Caso contrário: leitura de variável
    info = buscarSimbolo(tabela_simbolos, ident)

    if info is None:
        ctx['erros'].append(
            f"ERRO SEMÂNTICO [Linha {linha}]: Variável '{ident}' usada sem declaração."
        )
        tabela_simbolos = adicionarSimbolo(
            tabela_simbolos,
            ident,
            tipo='desconhecido',
            inicializada=False,
            linha=linha
        )
        tipo = 'desconhecido'
        valor = None

    else:
        tipo = info.get('tipo', 'desconhecido')
        valor = info.get('valor')
        marcarSimboloUsado(tabela_simbolos, ident, linha)

    no_leitura = {
        'tipo_no': 'LEITURA_VARIAVEL',
        'nome': ident,
        'tipo_inferido': tipo,
        'linha': linha
    }

    ctx['pilha_nos'].append(no_leitura)
    ctx['pilha_tipos'].append(tipo)
    ctx['pilha_valores'].append(valor)
    ctx['arvore_anotada'].append(no_leitura)

    return tabela_simbolos

    # Leitura de variável: se não declarada, adicionar com tipo desconhecido (mantém pilha coerente)
    info = buscarSimbolo(tabela_simbolos, nome)
    if info is None:
        ctx['erros'].append(f"ERRO SEMÂNTICO [Linha {linha}]: Variável '{nome}' usada sem declaração.")
        tipo = 'desconhecido'
        valor = 'X'
        tabela_simbolos = adicionarSimbolo(tabela_simbolos, nome, tipo, False, valor, linha)
    elif not info.get('inicializada', False):
        ctx['erros'].append(f"ERRO SEMÂNTICO [Linha {linha}]: Variável '{nome}' usada sem inicialização.")
        tipo = info.get('tipo', 'desconhecido')
        valor = 'X'
    else:
        tipo = info.get('tipo', 'desconhecido')
        valor = info.get('valor')
        marcarSimboloUsado(tabela_simbolos, nome, linha)

    no_leitura = {
        'tipo_no': 'LEITURA_VARIAVEL',
        'tipo_inferido': tipo,
        'nome': nome,
        'linha': linha
    }

    ctx['pilha_nos'].append(no_leitura)
    ctx['pilha_tipos'].append(tipo)
    ctx['pilha_valores'].append(valor)
    ctx['arvore_anotada'].append(no_leitura)

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

    no_res = {
        'tipo_no': 'RES',
        'tipo_inferido': tipo_resultado,
        'parametro': n,
        'linha': numero_linha
    }

    ctx['pilha_nos'].append(no_res)
    ctx['arvore_anotada'].append(no_res)
    ctx['pilha_tipos'].append(tipo_resultado)
    ctx['pilha_valores'].append(None)

    ctx['arvore_anotada'].append({
        'tipo_no': 'RES',
        'tipo_inferido': tipo_resultado,
        'parametro': n,
        'linha': numero_linha
    })

def processar_operador_aritmetico(ctx: dict, simbolo: str, regras_semanticas: dict, linha: int) -> None:
    # Consumir o token do operador do stream de valores (alinha idx_valor).
    if 'idx_valor' in ctx:
        ctx['idx_valor'] += 1

    # Desempilha operandos (topo = direita)
    if len(ctx['pilha_nos']) < 2 or len(ctx['pilha_tipos']) < 2:
        ctx['erros'].append(
            f"ERRO SEMÂNTICO [Linha {linha}]: Operador '{simbolo}' requer dois operandos."
        )
        # empilha nó desconhecido para seguir análise
        ctx['pilha_nos'].append({'tipo_no': 'OPERACAO', 'operador': simbolo, 'tipo_inferido': 'desconhecido', 'operandos': [], 'linha': linha})
        ctx['pilha_tipos'].append('desconhecido')
        ctx['pilha_valores'].append(None)
        ctx['arvore_anotada'].append({'tipo_no': 'OPERACAO', 'operador': simbolo, 'tipo_inferido': 'desconhecido', 'operandos': [], 'linha': linha})
        return

    no_direita = ctx['pilha_nos'].pop()
    no_esquerda = ctx['pilha_nos'].pop()

    tipo_direita = ctx['pilha_tipos'].pop()
    tipo_esquerda = ctx['pilha_tipos'].pop()

    # Verifica compatibilidade ESTRITA (modelo Fase 4)
    if tipo_esquerda != 'int' or tipo_direita != 'int':
        ctx['erros'].append(
            f"ERRO SEMÂNTICO [Linha {linha}]: Operador '{simbolo}' inválido para '{tipo_esquerda}' e '{tipo_direita}'."
        )

        no_op = {
            'tipo_no': 'OPERACAO',
            'operador': simbolo,
            'tipo_inferido': 'desconhecido',
            'operandos': [no_esquerda, no_direita],
            'linha': linha
        }

        ctx['pilha_nos'].append(no_op)
        ctx['pilha_tipos'].append('desconhecido')
        ctx['pilha_valores'].append(None)
        ctx['arvore_anotada'].append(no_op)
        return

    # Operação válida
    no_op = {
        'tipo_no': 'OPERACAO',
        'operador': simbolo,
        'tipo_inferido': 'int',
        'operandos': [no_esquerda, no_direita],
        'linha': linha
    }

    ctx['pilha_nos'].append(no_op)
    ctx['pilha_tipos'].append('int')
    ctx['pilha_valores'].append(None)
    ctx['arvore_anotada'].append(no_op)

def processar_estrutura_controle(ctx, simbolo, numero_linha):
    """
    FUNCIONAMENTO CORRIGIDO para WHILE:
    Em RPN, a estrutura é: (condição corpo WHILE)
    Portanto, na pilha temos: [corpo, condição] (corpo no TOPO)
    """
    if 'idx_valor' in ctx:
        ctx['idx_valor'] += 1

    pilha_nos = ctx.get('pilha_nos', [])
    pilha_tipos = ctx.get('pilha_tipos', [])
    pilha_vals = ctx.get('pilha_valores', [])

    if simbolo == 'while':
        print("\n" + "="*60)
        print("PROCESSANDO WHILE - ESTRUTURA RPN")
        print("="*60)

        print(f"Pilha ANTES do WHILE ({len(pilha_nos)} nós):")
        for i, no in enumerate(pilha_nos):
            tipo = no.get('tipo_no')
            info = no.get('operador', no.get('nome', '?'))
            tipo_inf = no.get('tipo_inferido')
            print(f"  [{i}] {tipo} - {info} : {tipo_inf}")

        # Precisamos ao menos de dois nós (corpo + condição)
        if len(pilha_nos) < 2:
            ctx['erros'].append(f"ERRO [Linha {numero_linha}]: WHILE incompleto")
            return

        # Encontra a condição: procura do topo para baixo por nó booleano/COMPARACAO
        no_condicao = None
        idx_condicao = None
        for i in range(len(pilha_nos) - 1, -1, -1):
            no = pilha_nos[i]
            tipo_inf = no.get('tipo_inferido')
            if tipo_inf == 'booleano' or no.get('tipo_no') == 'COMPARACAO':
                no_condicao = no
                idx_condicao = i
                break

        # Se não encontrou nó booleano/COMPARACAO, use o topo como fallback (último nó)
        if no_condicao is None:
            idx_condicao = len(pilha_nos) - 1
            no_condicao = pilha_nos[idx_condicao]

        print(f"✓ Condição identificada (índice {idx_condicao}): {no_condicao.get('tipo_no')}({no_condicao.get('tipo_inferido')})")

        # corpo_nos = nós anteriores à condição (em RPN corpo vem antes da condição)
        corpo_nos = pilha_nos[:idx_condicao]
        print(f"✓ Corpo: {len(corpo_nos)} nós")

        # Remova da pilha todos os nós até (e incluindo) a condição.
        # Depois, empilhe um nó LOOP_WHILE representando a estrutura
        restante_apos = pilha_nos[idx_condicao+1:] if idx_condicao+1 <= len(pilha_nos) else []
        ctx['pilha_nos'] = restante_apos

        # Sincroniza pilha_tipos e pilha_valores removendo itens correspondentes
        # Calcula quantos nós foram removidos
        removidos = idx_condicao + 1
        if len(pilha_tipos) >= removidos:
            ctx['pilha_tipos'] = pilha_tipos[removidos:]
        else:
            ctx['pilha_tipos'] = []

        if len(pilha_vals) >= removidos:
            ctx['pilha_valores'] = pilha_vals[removidos:]
        else:
            ctx['pilha_valores'] = []

        # Detecta atribuições no corpo em padrão RPN (expr seguido de LEITURA_VARIAVEL)
        atribuicoes = []
        i = 0
        while i < len(corpo_nos):
            no_atual = corpo_nos[i]
            if i + 1 < len(corpo_nos):
                no_proximo = corpo_nos[i + 1]
                if (no_atual.get('tipo_no') in ['OPERACAO', 'LEITURA_VARIAVEL', 'LITERAL'] and
                    no_proximo.get('tipo_no') == 'LEITURA_VARIAVEL' and
                    no_proximo.get('nome') not in ['(', ')', '+', '-', '*', '/', '<=', 'WHILE']):
                    var_dest = no_proximo.get('nome')
                    atribuicoes.append({
                        'tipo': 'atribuicao',
                        'variavel': var_dest,
                        'expressao': no_atual
                    })
                    print(f"  ✓ Atribuição detectada: {var_dest} = {no_atual.get('tipo_no')}")
                    i += 2
                    continue
            i += 1

        # Validação final da condição: aceita se tipo_inferido == 'booleano' OR nó é COMPARACAO
        tipo_cond = no_condicao.get('tipo_inferido') if isinstance(no_condicao, dict) else None

        no_while = {
            'tipo_no': 'LOOP_WHILE',
            'tipo_inferido': 'void',
            'condicao': no_condicao,
            'tipo_condicao': tipo_cond,    # <-- ADICIONADO: campo que analisarSemanticaControle usa
            'corpo': atribuicoes,
            'corpo_nos': corpo_nos,
            'linha': numero_linha
        }


        ctx['pilha_nos'].append(no_while)
        ctx['pilha_tipos'].append('void')
        ctx['arvore_anotada'].append(no_while)

        print(f"✓ WHILE criado com {len(atribuicoes)} atribuições no corpo")
        return

    # --- IF permanece como já estava, apenas sincronizamos consumo de token se necessário ---
    elif simbolo == 'if':
        # caso IF: manter lógica anterior (consumir token já feito no topo)
        if len(ctx['pilha_nos']) < 3 or len(ctx['pilha_tipos']) < 3:
            ctx['erros'].append(
                f"ERRO SEMÂNTICO [Linha {numero_linha}]: IF incompleto"
            )
            return

        no_else = ctx['pilha_nos'].pop()
        no_then = ctx['pilha_nos'].pop()
        no_cond = ctx['pilha_nos'].pop()

        tipo_else = ctx['pilha_tipos'].pop() if ctx['pilha_tipos'] else 'desconhecido'
        tipo_then = ctx['pilha_tipos'].pop() if ctx['pilha_tipos'] else 'desconhecido'
        tipo_cond = ctx['pilha_tipos'].pop() if ctx['pilha_tipos'] else 'desconhecido'

        if tipo_cond != 'booleano':
            ctx['erros'].append(
                f"ERRO SEMÂNTICO [Linha {numero_linha}]: IF requer condição booleana"
            )

        tipo_resultado = promoverTipo(tipo_then, tipo_else)

        no_if = {
            'tipo_no': 'CONDICIONAL_IF',
            'tipo_inferido': tipo_resultado,
            'tipo_condicao': tipo_cond,
            'tipos_ramos': [tipo_then, tipo_else],
            'filhos': [no_cond, no_then, no_else],
            'linha': numero_linha
        }

        ctx['pilha_nos'].append(no_if)
        ctx['pilha_tipos'].append(tipo_resultado)
        ctx['arvore_anotada'].append(no_if)

        return

def processar_relacional(op, no1, no2, tac):
    t1 = no1['temp']
    t2 = no2['temp']
    t3 = novo_temp()

    tac.append(f"{t3} = {t1} {op} {t2}")

    return {
        'temp': t3,
        'tipo': 'bool'
    }

def analisarSemantica(derivacao: list, tokens_valores: list, tabela_simbolos: dict, regras_semanticas: dict, historico_resultados: list, numero_linha: int):
    ctx = criar_contexto()
    atribuicoes_nomes = coletar_atribuicoes(tokens_valores)
    tokens_processaveis = tokens_processaveis_de(tokens_valores)
    memorias_declaradas_nesta_linha = ctx['memorias_decl_nesta_linha']
    eps = globals().get('EPS', 'E')

    for i, (nt, prod) in enumerate(derivacao[:30], 1):
        prod_str = ' '.join(str(p) for p in prod) if prod else 'ε'
        print(f"      {i:2d}. {nt:10s} → {prod_str}")
    if len(derivacao) > 30:
        print(f"      ... ({len(derivacao) - 30} produções omitidas)")
    print()

    # Processa todas as produções em ordem
    for idx_derivacao, (nao_terminal, producao) in enumerate(derivacao):
        if not producao:
            continue
        
        # Ignora produções epsilon/vazias e símbolos estruturais
        is_epsilon = (producao == ['E'] or producao == [eps] or 
                     (len(producao) == 1 and producao[0] in ['E', eps]))
        
        if is_epsilon:
            continue

        for simbolo in producao:
            # Ignora símbolos estruturais da gramática
            if simbolo in ['(', ')', 'LINHA', 'EXPR', 'ITEMS', 'ITEM', 'NUMERO', 
                          'IDENT', 'OPERADOR', 'IFKW', 'WHILEKW']:
                continue

            # DEBUG: Mostra estado atual antes de processar cada símbolo
            if simbolo in ['+', '-', '*', '/', '<=', 'WHILE']:
                print(f"    [DEBUG ANTES {simbolo}] Pilha: {len(ctx['pilha_nos'])} nós, {ctx['pilha_tipos']}")

            if simbolo == 'int':
                consumir_literal(ctx, tokens_processaveis, 'int', numero_linha)
            elif simbolo == 'float':
                consumir_literal(ctx, tokens_processaveis, 'float', numero_linha)
            elif simbolo == 'ident':
                tabela_simbolos = processar_identificador(
                    ctx, tokens_processaveis, tabela_simbolos, atribuicoes_nomes, numero_linha
                )
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

    return (tabela_simbolos, ctx['erros'], ctx['arvore_anotada'], 
            tipo_final, memorias_declaradas_nesta_linha)

def criar_contexto() -> dict:
    return {
        'erros': [],
        'arvore_anotada': [],
        'pilha_nos': [],
        'pilha_tipos': [],
        'pilha_valores': [],
        'idx_valor': 0,
        'memorias_decl_nesta_linha': set()
    }

def processar_comparacao(ctx: dict, simbolo: str, regras_semanticas: dict, numero_linha: int) -> None:
    regra = regras_semanticas.get('operadores_relacionais', {}).get(simbolo, {'aceita': []})

    # Consumir o token do comparador do stream de valores (alinha o idx_valor).
    # Isso evita que o mesmo símbolo seja lido mais tarde como 'ident'.
    if 'idx_valor' in ctx:
        ctx['idx_valor'] += 1

    print(f"    [DEBUG CMP {simbolo}] Pilha antes: {len(ctx['pilha_nos'])} nós")

    # VERIFICAÇÃO ROBUSTA: Garante que há operandos suficientes
    if len(ctx['pilha_tipos']) < 2 or len(ctx['pilha_nos']) < 2:
        ctx['erros'].append(
            f"ERRO SEMÂNTICO [Linha {numero_linha}]: "
            f"Comparação '{simbolo}' requer dois operandos (pilha tem {len(ctx['pilha_tipos'])})."
        )

        # Recuperação: empilha tipo booleano para continuar análise
        ctx['pilha_tipos'].append('booleano')
        ctx['pilha_nos'].append({
            'tipo_no': 'COMPARACAO',
            'operador': simbolo,
            'tipo_inferido': 'booleano',
            'operandos': [],
            'linha': numero_linha
        })
        return

    # Desempilha: topo (direita) primeiro, depois base (esquerda)
    no_direita = ctx['pilha_nos'].pop()
    no_esquerda = ctx['pilha_nos'].pop()

    tipo_direita = ctx['pilha_tipos'].pop()
    tipo_esquerda = ctx['pilha_tipos'].pop()

    print(f"    [DEBUG CMP {simbolo}] Operandos:")
    print(f"      Esquerda: {no_esquerda.get('tipo_no')}({tipo_esquerda})")
    print(f"      Direita: {no_direita.get('tipo_no')}({tipo_direita})")

    # Validação
    if tipo_esquerda not in regra['aceita'] or tipo_direita not in regra['aceita']:
        ctx['erros'].append(
            f"ERRO SEMÂNTICO [Linha {numero_linha}]: "
            f"Comparação '{simbolo}' inválida entre '{tipo_esquerda}' e '{tipo_direita}'"
        )

    # Cria nó com ordem correta
    no_comparacao = {
        'tipo_no': 'COMPARACAO',
        'operador': simbolo,
        'tipo_inferido': 'booleano',
        'operandos': [no_esquerda, no_direita],
        'linha': numero_linha
    }

    ctx['pilha_nos'].append(no_comparacao)
    ctx['pilha_tipos'].append('booleano')
    ctx['arvore_anotada'].append(no_comparacao)

    print(f"    [DEBUG CMP {simbolo}] Resultado: booleano empilhado")
    
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
        resultado = None
        for filho in no.get('filhos', []):
            resultado = processar_no_tac(filho, tac)
        return resultado if resultado else {'temp': None, 'tipo': 'desconhecido', 'kind': 'temp'}
    
    elif tipo_no == 'LITERAL':
        return {
            'temp': no.get('valor'),
            'tipo': no.get('tipo_inferido', 'int'),
            'kind': 'imm'
        }
    
    elif tipo_no == 'LEITURA_VARIAVEL':
        return {
            'temp': no.get('nome'),
            'tipo': no.get('tipo_inferido', 'int'),
            'kind': 'var'
        }
    
    elif tipo_no == 'ATRIBUICAO':
        # Atribuições simples (fora de loops)
        nome = no.get('nome')
        tipo = no.get('tipo_inferido', 'int')
        valor = no.get('valor')
        
        if valor is not None:
            tac.append({
                'op': '=',
                'a': valor,
                'dest': nome,
                'tipo': tipo,
                'comment': f'atribuição inicial: {nome} = {valor}'
            })
        
        return {
            'temp': nome,
            'tipo': tipo,
            'kind': 'var'
        }
    
    elif tipo_no == 'OPERACAO':
        return gerar_tac_operacao(no, tac)
    
    elif tipo_no == 'COMPARACAO':
        return gerar_tac_comparacao(no, tac)
    
    elif tipo_no == 'LOOP_WHILE':
        return gerar_tac_while(no, tac)
    
    elif tipo_no == 'CONDICIONAL_IF':
        return gerar_tac_if(no, tac)
    
    elif tipo_no == 'RES':
        return gerar_tac_res(no, tac)
    
    else:
        return {'temp': None, 'tipo': 'desconhecido', 'kind': 'temp'}

def gerar_tac_operacao(no: dict, tac: list) -> dict:
    """
    Gera TAC para operações aritméticas binárias.
    Suporta conversão automática de int para float quando necessário.
    """
    operador = no.get('operador')
    operandos = no.get('operandos', [])
    tipo_resultado = no.get('tipo_inferido', 'int')
    
    if len(operandos) >= 2:
        info1 = processar_no_tac(operandos[0], tac)
        info2 = processar_no_tac(operandos[1], tac)
        
        temp1 = info1.get('temp')
        temp2 = info2.get('temp')
    else:
        temp1 = '?'
        temp2 = '?'
    
    temp_result = novo_temp()
    
    tac.append({
        'op': operador,
        'a': temp1,
        'b': temp2,
        'dest': temp_result,
        'tipo': tipo_resultado,
        'comment': f'{operador} operation'
    })
    
    return {
        'temp': temp_result,
        'tipo': tipo_resultado,
        'kind': 'temp'
    }

def gerar_tac_comparacao(no: dict, tac: list) -> dict:
    """Gera TAC para operações relacionais."""
    operador = no.get('operador')
    operandos = no.get('operandos', [])
    
    if len(operandos) >= 2:
        info1 = processar_no_tac(operandos[0], tac)
        info2 = processar_no_tac(operandos[1], tac)
        
        temp1 = info1.get('temp')
        temp2 = info2.get('temp')
    else:
        temp1 = '?'
        temp2 = '?'
    
    temp_result = novo_temp()
    
    tac.append({
        'op': operador,
        'a': temp1,
        'b': temp2,
        'dest': temp_result,
        'tipo': 'booleano',
        'comment': f'comparison {operador}'
    })
    
    return {
        'temp': temp_result,
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

def gerar_tac_while(no, tac):
    """
    Gera TAC para estrutura de repetição WHILE.
    Processa TODOS os nós do corpo, incluindo incrementos.
    
    Estrutura esperada em RPN:
    (condição corpo WHILE)
    
    Onde corpo contém pares: [expressão] [variável] para cada atribuição
    """

    # Extrai condição e corpo
    no_condicao = no.get('condicao')
    corpo_nos = no.get('corpo_nos', [])
    
    if not no_condicao:
        print("    [ERRO] WHILE sem condição")
        return {'temp': None, 'tipo': 'void', 'kind': 'temp'}
    
    print(f"    [DEBUG] Condição: {no_condicao.get('tipo_no')}")
    print(f"    [DEBUG] Total de nós no corpo: {len(corpo_nos)}")
    
    # Debug: mostra estrutura do corpo
    for i, n in enumerate(corpo_nos):
        print(f"    [DEBUG] Corpo[{i}]: {n.get('tipo_no')} - {n.get('nome', n.get('operador', '?'))}")
    
    # Labels para o loop
    label_inicio = novo_label()
    label_fim = novo_label()
    
    # Label de início do loop
    tac.append({
        'op': 'label',
        'dest': label_inicio,
        'comment': 'início do while'
    })
    
    # Avalia condição
    info_cond = processar_no_tac(no_condicao, tac)
    temp_cond = info_cond.get('temp')
    
    # Salta para fim se condição for falsa
    tac.append({
        'op': 'ifFalse',
        'a': temp_cond,
        'dest': label_fim,
        'tipo': 'booleano',
        'comment': 'se condição falsa, sair do loop'
    })
    
    # CORREÇÃO PRINCIPAL: Processa TODOS os nós do corpo em pares
    # Em RPN, atribuições aparecem como: [expressão] [variável]
    i = 0
    atribuicoes_geradas = 0
    
    while i < len(corpo_nos):
        if i + 1 < len(corpo_nos):
            no_expr = corpo_nos[i]
            no_var = corpo_nos[i + 1]
            
            # Se próximo nó é ATRIBUICAO ou LEITURA_VARIAVEL, é atribuição
            if no_var.get('tipo_no') in ['ATRIBUICAO', 'LEITURA_VARIAVEL']:
                var_nome = no_var.get('nome')
                
                # Ignora operadores e palavras-chave
                if var_nome not in ['(', ')', '+', '-', '*', '/', '<=', '>=', 'WHILE', 'IF', '<', '>', '==', '!=']:
                    # Processa a expressão (pode ser operação, literal ou leitura)
                    info_expr = processar_no_tac(no_expr, tac)
                    temp_expr = info_expr.get('temp')
                    tipo_expr = info_expr.get('tipo', 'int')
                    
                    # Gera atribuição
                    tac.append({
                        'op': '=',
                        'a': temp_expr,
                        'dest': var_nome,
                        'tipo': tipo_expr,
                        'comment': f'atribuição no loop: {var_nome} = {temp_expr}'
                    })
                    
                    atribuicoes_geradas += 1
                    print(f"    [DEBUG] Gerado: {var_nome} = {temp_expr}")
                    i += 2
                    continue
        
        # Se não formar par de atribuição, apenas processa o nó
        # (pode ser parte de expressões complexas)
        processar_no_tac(corpo_nos[i], tac)
        i += 1
    
    # Volta para início do loop
    tac.append({
        'op': 'goto',
        'dest': label_inicio,
        'comment': 'voltar para verificar condição'
    })
    
    # Label de fim do loop
    tac.append({
        'op': 'label',
        'dest': label_fim,
        'comment': 'fim do while'
    })
    
    print(f"    [DEBUG] TAC WHILE gerado com {atribuicoes_geradas} atribuições")
    
    return {
        'temp': None,
        'tipo': 'void',
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
                a = formatar_operando_tac(inst.get('a'))
                f.write(f"  ifFalse {a} goto {inst['dest']}\n")
            
            elif op == '=':
                a = formatar_operando_tac(inst.get('a'))
                dest = inst.get('dest')
                f.write(f"  {dest} = {a}\n")
            
            elif op in ['+', '-', '*', '/', '|', '%', '^', '<', '>', '<=', '>=', '==', '!=']:
                a = formatar_operando_tac(inst.get('a'))
                b = formatar_operando_tac(inst.get('b'))
                dest = inst.get('dest')
                f.write(f"  {dest} = {a} {op} {b}\n")
            
            elif op == 'res':
                a = inst.get('a')
                dest = inst.get('dest')
                f.write(f"  {dest} = RES({a})\n")
            
            elif op == 'print':
                a = formatar_operando_tac(inst.get('a'))
                f.write(f"  print {a}\n")
            
            else:
                f.write(f"  {inst}\n")
            
            # Adiciona comentário se existir
            comment = inst.get('comment')
            if comment:
                f.write(f"    ; {comment}\n")
        
        f.write("\n" + "=" * 60 + "\n")

def formatar_operando_tac(operando) -> str:
    """Formata um operando para exibição no TAC."""
    if operando is None:
        return "None"
    elif isinstance(operando, (int, float)):
        return str(operando)
    elif isinstance(operando, str):
        return operando
    else:
        return str(operando)
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

TEMP_COUNTER = 0
def novo_temp():
    global TEMP_COUNTER
    TEMP_COUNTER += 1
    return f"t{TEMP_COUNTER}"

# seção dados e helpers
def mapear_variaveis(tac, tabela_simbolos):
    """Mapeia todas as variáveis usadas no TAC"""
    vars_map = {}
    
    for inst in tac:
        # Verifica todos os campos que podem conter variáveis
        for campo in ["a", "b", "dest"]:
            val = inst.get(campo)
            
            if val and isinstance(val, str):
                # Ignora labels, registradores e operadores
                if (not val.startswith('L') and 
                    not val.startswith('r') and
                    val not in ['label', 'goto', 'ifFalse', 'print'] and
                    len(val) > 0):
                    
                    # Adiciona variável ao mapa
                    if val not in vars_map:
                        vars_map[val] = ".word 0"
    
    # Adiciona variáveis da tabela de símbolos
    for var_name in tabela_simbolos.keys():
        if var_name not in vars_map:
            vars_map[var_name] = ".word 0"
    
    return vars_map

def gerar_secao_dados(vars_map):
    data_lines = ["\n"] 
    data_lines.append(".data")
    
    for var_name, var_init in vars_map.items():
        # Remove ponto inicial se houver
        clean_name = var_name.lstrip('.')
        data_lines.append(f"{clean_name}: .word 0  ; variável {clean_name}")
    
    data_lines.append("\n; === SEÇÃO DE CÓDIGO ===")
    data_lines.append(".text")
    
    return "\n".join(data_lines)

# gerar carregamento de operando
def carregar_operando(op, regL, regH):
    """Gera código para mover variável/imediato → registradores"""
    if isinstance(op, (int, float)):
        # Números - carrega como imediato
        if isinstance(op, float):
            ieee_value = float_to_ieee754_half(op)
            lo = ieee_value & 0xFF
            hi = (ieee_value >> 8) & 0xFF
        else:
            lo = op & 0xFF
            hi = (op >> 8) & 0xFF
        return f"\n    ldi {regL}, 0x{lo:02X}\n    ldi {regH}, 0x{hi:02X}\n"
    else:
        # Qualquer outra coisa (strings como 'I', 'FATORIAL', 't1', etc) - carrega da memória
        return f"\n    lds {regL}, {op}\n    lds {regH}, {op}+1\n"

# rotinas aritméticas já previstas (simplificadas)
def gerar_mul16(regAL, regAH, regBL, regBH, regRL, regRH):
    """Multiplicação 16-bit"""
    return f"""
    ; MUL16: {regAH}:{regAL} * {regBH}:{regBL} => {regRH}:{regRL}
    clr  {regRL}
    clr  {regRH}
    mul  {regAL}, {regBL}
    mov  {regRL}, r0
    mov  {regRH}, r1
    mul  {regAH}, {regBL}
    add  {regRH}, r0
    mul  {regAL}, {regBH}
    add  {regRH}, r0
    clr  r1
"""

def gerar_div16(regAL, regAH, regBL, regBH, regRL, regRH):
    """Divisão 16-bit"""
    label_loop = f"div_loop_{regRL}"
    label_done = f"div_done_{regRL}"
    return f"""
    ; DIV16
    clr  {regRL}
    clr  {regRH}
{label_loop}:
    cp   {regAL}, {regBL}
    cpc  {regAH}, {regBH}
    brlo {label_done}
    sub  {regAL}, {regBL}
    sbc  {regAH}, {regBH}
    inc  {regRL}
    brne {label_loop}
    inc  {regRH}
    rjmp {label_loop}
{label_done}:
    movw r24, {regRL}
"""

def gerar_pow16():
    return """
    ; --- POW16: A^B, A=r22:r23, B=r24:r25 ---
    ; implementação simples por multiplicações sucessivas (assume Expoente 8-bit)
    ldi r20, 1
    ldi r21, 0
    tst r25
    brne pow_loop
    tst r24
    breq pow_end
pow_loop:
    ; multiplicar r20:r21 *= r22:r23
    ; salva ret em r26:r27 e A em r28:r29 para uso do mul sequence
    movw r26, r20
    movw r28, r22

    clr r20
    clr r21

    mul r27, r29
    mov r20, r0
    mov r21, r1

    mul r26, r29
    add r21, r0

    mul r27, r28
    add r21, r0

    clr r1

    ; decrementa expoente (r24:r25)
    subi r24, 1
    sbci r25, 0
    tst r24
    brne pow_loop
    tst r25
    brne pow_loop
pow_end:
"""

# Routines UART / print hex (16-bit)
ROTINAS_UART = r"""
UART_init:
    ldi r16, 0
    sts UBRR0H, r16
    ldi r16, 103              ; baud 9600 para 16MHz
    sts UBRR0L, r16
    ldi r16, (1<<TXEN0)       ; ativa transmissor
    sts UCSR0B, r16
    ldi r16, (1<<UCSZ01)|(1<<UCSZ00) ; 8N1
    sts UCSR0C, r16
    ret

UART_sendByte:
WaitTX:
    lds r18, UCSR0A
    sbrc r18, 5               ; UDRE0 bit 5 = buffer vazio?
    rjmp UART_doSend
    rjmp WaitTX
UART_doSend:
    sts UDR0, r24
    ret

UART_printHexNibble:
    andi r24, 0x0F
    cpi r24, 10
    brlo DigitHex
    subi r24, 10
    ldi r18, 55               ; 'A' - 10
    add r24, r18
    rcall UART_sendByte
    ret
DigitHex:
    ldi r18, 48               ; '0'
    add r24, r18
    rcall UART_sendByte
    ret

UART_printHex8:
    push r18
    push r19
    mov r19, r24              ; salva original
    swap r24
    andi r24, 0x0F
    rcall UART_printHexNibble
    mov r24, r19
    andi r24, 0x0F
    rcall UART_printHexNibble
    pop r19
    pop r18
    ret

UART_printHex16:
    push r18
    push r19
    ; High byte
    mov r24, r25
    rcall UART_printHex8
    ; Espaço
    ldi r24, ' '
    rcall UART_sendByte
    ; Low byte
    rcall UART_printHex8
    pop r19
    pop r18
    ret
"""

ROTINA_PRINT_IEEE754 = r"""
; Imprime valor IEEE 754 half-precision como decimal
; Entrada: r24:r25 = valor IEEE 754 half (little-endian)
UART_printIEEE754:
    push r18
    push r19
    push r20
    push r21
    push r22
    push r23
    push r26
    push r27
    
    ; r24 = low byte, r25 = high byte
    ; Extrai sinal (bit 15)
    mov r18, r25
    andi r18, 0x80
    breq ieee_positive
    
    ; Imprime sinal negativo
    ldi r24, '-'
    rcall UART_sendByte
    
ieee_positive:
    ; Extrai expoente (bits 10-14) e mantissa (bits 0-9)
    mov r19, r25        ; high byte
    mov r20, r24        ; low byte
    
    ; Caso especial: zero
    andi r19, 0x7F      ; remove sinal
    or r19, r20
    breq ieee_print_zero
    
    ; Verifica se é zero (expoente e mantissa = 0)
    mov r19, r25
    andi r19, 0x7C      ; bits 10-14 (expoente >> 2)
    breq ieee_print_zero
    
    ; Converte para decimal aproximado (simplificado)
    ; Para valores pequenos, usa conversão direta
    ; Para produção, implementar conversão completa IEEE 754
    
    ; Implementação simplificada: usa tabela de lookup ou aproximação
    ; Por ora, imprime em hexadecimal com prefixo
    ldi r24, '0'
    rcall UART_sendByte
    ldi r24, 'x'
    rcall UART_sendByte
    
    mov r24, r25
    rcall UART_printHex8
    mov r24, r20
    rcall UART_printHex8
    
    rjmp ieee_end
    
ieee_print_zero:
    ldi r24, '0'
    rcall UART_sendByte
    ldi r24, '.'
    rcall UART_sendByte
    ldi r24, '0'
    rcall UART_sendByte
    
ieee_end:
    pop r27
    pop r26
    pop r23
    pop r22
    pop r21
    pop r20
    pop r19
    pop r18
    ret

; Converte int16 para IEEE 754 half-precision
; Entrada: r22:r23 = inteiro (little-endian)
; Saída: r20:r21 = IEEE 754 half
int_to_ieee754:
    push r18
    push r19
    push r24
    push r25
    
    ; Verifica se é zero
    or r22, r23
    breq int_ieee_zero
    
    ; Extrai sinal
    clr r18             ; sinal = 0 (positivo)
    mov r19, r23
    andi r19, 0x80
    breq int_ieee_pos
    
    ; Negativo: complemento de 2
    ldi r18, 0x80       ; sinal = 1
    com r22
    com r23
    inc r22
    brne int_ieee_pos
    inc r23
    
int_ieee_pos:
    ; Encontra bit mais significativo (normaliza)
    ; Simplificação: assume valores pequenos (< 1024)
    ; Expoente = 15 + posição do MSB
    
    ldi r24, 15 + 10    ; expoente base + offset mantissa
    mov r25, r23
    
    ; Conta zeros à esquerda (simplificado para 8 bits)
ieee_norm_loop:
    sbrc r25, 7
    rjmp ieee_norm_done
    lsl r22
    rol r23
    dec r24
    rjmp ieee_norm_loop
    
ieee_norm_done:
    ; Monta IEEE 754
    ; r24 = expoente, r22:r23 = mantissa normalizada
    ; Remove bit implícito (MSB)
    lsl r22
    rol r23
    
    ; r20 = low byte, r21 = high byte
    mov r20, r22
    mov r21, r23
    lsr r21
    lsr r21             ; ajusta mantissa para 10 bits
    
    ; Insere expoente
    mov r25, r24
    lsl r25
    lsl r25             ; expoente << 2
    or r21, r25
    
    ; Insere sinal
    or r21, r18
    
    rjmp int_ieee_end
    
int_ieee_zero:
    clr r20
    clr r21
    
int_ieee_end:
    pop r25
    pop r24
    pop r19
    pop r18
    ret
"""

OPERACOES_IEEE754 = r"""
; Operações IEEE 754 half-precision - adaptadas à convenção:
; Temporários: r16..r23
; Parâmetros/Retorno: r24:r25
; Entrada para cada binary op: A em r18:r19, B em r20:r21
; Internamente rotinas usam r22:r23 (A) e r24:r25 (B) como antes;
; No retorno, resultado ficará em r24:r25.

; -----------------------------
; f16_extract (sem alteração de ABI interna)
; entrada: r22:r23
; saídas temporárias usadas: r26..r31
; retorna:
;  r26 = sign (0/1)
;  r27 = exponent (0..31)
;  r28:r29 = mantissa (10 bits)
; -----------------------------
f16_extract:
    ; r22 = low, r23 = high
    mov r26, r23
    andi r26, 0x80
    lsr r26
    lsr r26
    lsr r26
    lsr r26
    lsr r26
    lsr r26
    lsr r26
    lsr r26

    mov r27, r23
    andi r27, 0x7C
    lsr r27
    lsr r27
    lsr r27
    lsr r27
    lsr r27

    andi r23, 0x03
    mov r28, r22
    mov r29, r23
    ret

; --------------------------------------------------
; f16_pack (sem alteração importante)
; Empacota sign (r26), exponent (r27), mantissa r28:r29 -> r22:r23
; --------------------------------------------------
f16_pack:
    mov r30, r27
    lsl r30
    lsl r30
    lsl r30
    lsl r30
    lsl r30
    mov r31, r27
    lsl r31
    lsl r31
    lsl r31
    lsl r31
    mov r30, r27
    lsl r30
    lsl r30
    andi r30, 0xF8
    mov r31, r29
    andi r31, 0x03
    lsl r31
    lsl r31
    mov r29, r26
    lsl r29
    lsl r29
    lsl r29
    lsl r29
    lsl r29
    lsl r29
    lsl r29
    mov r22, r28
    mov r23, r30
    or r23, r31
    or r23, r29
    ret

; --------------------------------------------------
; f16_add
; agora: espera A em r18:r19 e B em r20:r21; retorna em r24:r25
; interna: trabalha em r22:r23 (A) e r24:r25 (B) como antes
; --------------------------------------------------
; --------------------------------------------------
; f16_add (versão com branches long-safe)
; espera A em r18:r19 e B em r20:r21; retorna em r24:r25
; --------------------------------------------------
f16_add:
    push r18
    push r19
    push r20
    push r21
    push r26
    push r27
    push r28
    push r29

    ; copiar entradas para convenção interna da rotina (r22:r23 = A, r24:r25 = B)
    mov r22, r18
    mov r23, r19
    mov r24, r20
    mov r25, r21

    ; --- rotina original (sem outras modificações) ---
    ; save A
    mov r30, r22
    mov r31, r23
    mov r22, r30
    mov r23, r31
    rcall f16_extract
    mov r16, r26
    mov r17, r27
    mov r18, r28
    mov r19, r29
    mov r22, r24
    mov r23, r25
    rcall f16_extract
    mov r20, r26
    mov r21, r27
    mov r22, r28
    mov r23, r29

    or r18, r19
    ; if equal (all zero) -> return_b  (original: breq .return_b)
    brne .skip1
    rjmp .return_b
.skip1:
    or r22, r23
    ; if equal -> return_a  (original: breq .return_a)
    brne .skip2
    rjmp .return_a
.skip2:
    cp r17, r21
    ; if greater or equal -> align_done  (original: brge .align_done)
    brlt .skip3
    rjmp .align_done
.skip3:
    mov r26, r16
    mov r16, r20
    mov r20, r26
    mov r26, r17
    mov r17, r21
    mov r21, r26
    mov r26, r18
    mov r18, r22
    mov r22, r26
    mov r26, r19
    mov r19, r23
    mov r23, r26

.align_done:
    mov r26, r17
    sub r26, r21
    tst r26
    ; if equal -> no_shift  (original: breq .no_shift)
    brne .skip4
    rjmp .no_shift
.skip4:

.shift_loop:
    lsr r22
    ror r23
    dec r26
    ; original: breq .skip_shift_loop  ; we invert and use rjmp
    brne .skip5
    rjmp .skip_shift_loop
.skip5:
    rjmp .shift_loop
.skip_shift_loop:
.no_shift:
    tst r17
    ; original: breq .a_denorm
    brne .skip6
    rjmp .a_denorm
.skip6:

    ori r19, (1<<2)
.a_denorm:
    tst r21
    ; original: breq .b_denorm
    brne .skip7
    rjmp .b_denorm
.skip7:

    ori r23, (1<<2)
.b_denorm:
    cp r16, r20
    ; original: breq .do_add
    brne .skip8
    rjmp .do_add
.skip8:

    mov r26, r19
    cp r26, r23
    ; original: brne .cmp_done
    breq .skip9
    rjmp .cmp_done
.skip9:
    mov r26, r18
    cp r26, r22
.cmp_done:
    ; original: brlt .do_sub_swapped
    brge .skip10
    rjmp .do_sub_swapped
.skip10:

    sub r18, r22
    sbc r19, r23
    mov r16, r16
    rjmp .normalize

.do_sub_swapped:
    sub r22, r18
    sbc r23, r19
    mov r18, r22
    mov r19, r23
    mov r16, r20
    rjmp .normalize

.do_add:
    add r18, r22
    adc r19, r23
    mov r16, r16

.normalize:
    ldi r26, 4
    cp r19, r26
    ; original: brlo .norm_shift_left
    brsh .skip11
    rjmp .norm_shift_left
.skip11:

    lsr r18
    ror r19
    inc r17
    rjmp .pack_result

.norm_shift_left:
    tst r19
    ; original: brne .pack_result
    breq .skip12
    rjmp .pack_result
.skip12:

    lsl r18
    rol r19
    dec r17
    ; original: brne .norm_shift_left
    breq .skip13
    rjmp .norm_shift_left
.skip13:

.pack_result:
    mov r28, r18
    mov r29, r19
    mov r26, r16
    mov r27, r17
    mov r22, r28
    mov r23, r29
    rcall f16_pack
    ; resultado está em r22:r23 (interno)
    ; mover resultado para convenção externa (r24:r25)
    mov r24, r22
    mov r25, r23
    rjmp .end

.return_a:
    mov r24, r30
    mov r25, r31
    rjmp .end

.return_b:
    mov r24, r24
    mov r25, r25
    rjmp .end

.end:
    pop r29
    pop r28
    pop r27
    pop r26
    pop r21
    pop r20
    pop r19
    pop r18
    ret

; --------------------------------------------------
; f16_mul
; espera A em r18:r19, B em r20:r21; retorna em r24:r25
; --------------------------------------------------
f16_mul:
    push r18
    push r19
    push r20
    push r21
    push r26
    push r27
    push r28
    push r29

    ; copiar entradas
    mov r22, r18
    mov r23, r19
    mov r24, r20
    mov r25, r21

    ; rotina original (aproximada)
    mov r30, r22
    mov r31, r23
    rcall f16_extract
    mov r16, r26
    mov r17, r27
    mov r18, r28
    mov r19, r29
    mov r22, r24
    mov r23, r25
    rcall f16_extract
    mov r20, r26
    mov r21, r27
    mov r22, r28
    mov r23, r29
    or r18, r19
    breq .zero_a
    or r22, r23
    breq .zero_b
    eor r16, r20
    mov r26, r17
    add r26, r21
    subi r26, 15
    ori r19, (1<<2)
    ori r23, (1<<2)
    mov r24, r18
    mov r25, r22
    mul r24, r25
    mov r26, r0
    mov r27, r1
    clr r0
    clr r1
    mov r22, r26
    mov r23, r27
    mov r17, r26
    mov r26, r16
    mov r28, r22
    mov r29, r23
    mov r27, r17
    rcall f16_pack
    mov r24, r22
    mov r25, r23
    jmp .mul_end
.zero_a:
    ldi r24, 0x00
    ldi r25, 0x00
    jmp .mul_end
.zero_b:
    ldi r24, 0x00
    ldi r25, 0x00
.mul_end:
    pop r29
    pop r28
    pop r27
    pop r26
    pop r21
    pop r20
    pop r19
    pop r18
    ret

; --------------------------------------------------
; f16_div
; espera A em r18:r19, B em r20:r21; retorna em r24:r25
; --------------------------------------------------
f16_div:
    push r18
    push r19
    push r20
    push r21
    push r26
    push r27
    push r28
    push r29

    ; copiar entradas
    mov r22, r18
    mov r23, r19
    mov r24, r20
    mov r25, r21

    mov r30, r22
    mov r31, r23
    rcall f16_extract
    mov r16, r26
    mov r17, r27
    mov r18, r28
    mov r19, r29
    mov r22, r24
    mov r23, r25
    rcall f16_extract
    mov r20, r26
    mov r21, r27
    mov r22, r28
    mov r23, r29
    or r22, r23
    breq .div_by_zero
    eor r16, r20
    mov r26, r17
    sub r26, r21
    add r26, 15
    mov r24, r18
    mov r25, r19
    mov r28, r22
    mov r29, r23
    ldi r30, 0x00
    ldi r31, 0x00
    ldi r27, 16
.div_loop:
    lsl r24
    rol r25
    lsl r30
    rol r31
    mov r26, r25
    cp r26, r29
    brlo .div_no_sub
    sub r25, r29
    sbc r24, r28
    ori r31, 0x01
.div_no_sub:
    dec r27
    brne .div_loop
    mov r22, r30
    mov r23, r31
    mov r26, r16
    mov r27, r26
    mov r28, r22
    mov r29, r23
    rcall f16_pack
    mov r24, r22
    mov r25, r23
    jmp .div_end
.div_by_zero:
    ldi r24, 0x00
    ldi r25, 0x7C
    jmp .div_end
.div_end:
    pop r29
    pop r28
    pop r27
    pop r26
    pop r21
    pop r20
    pop r19
    pop r18
    ret

; --------------------------------------------------
; print_hex16 - imprime r24:r25 (agora) em hex (placeholder)
; --------------------------------------------------
print_hex16:
    ; conv hex nibble by nibble e rcall usart_transmit
    ret
"""

def float_to_ieee754_half(value):
    """
    Converte um float Python para formato IEEE 754 half-precision (16 bits)
    Formato: 1 bit sinal | 5 bits expoente | 10 bits mantissa
    """
    import struct
    
    # Casos especiais
    if value == 0.0:
        return 0x0000
    if value != value:  # NaN
        return 0x7E00
    
    # Extrai sinal
    sign = 0 if value >= 0 else 1
    value = abs(value)
    
    # Infinito
    if value == float('inf'):
        return (sign << 15) | 0x7C00
    
    # Converte para float32 primeiro para facilitar
    bits32 = struct.unpack('>I', struct.pack('>f', value))[0]
    
    # Extrai componentes do float32
    sign32 = (bits32 >> 31) & 0x1
    exp32 = (bits32 >> 23) & 0xFF
    mant32 = bits32 & 0x7FFFFF
    
    # Ajusta expoente (bias 127 -> bias 15)
    exp16 = exp32 - 127 + 15
    
    # Overflow -> infinito
    if exp16 >= 31:
        return (sign << 15) | 0x7C00
    
    # Underflow -> zero
    if exp16 <= 0:
        return sign << 15
    
    # Trunca mantissa de 23 para 10 bits
    mant16 = mant32 >> 13
    
    # Monta o half-precision
    result = (sign << 15) | (exp16 << 10) | mant16
    return result & 0xFFFF

def int_to_ieee754_half(value_int):
    """Converte inteiro para IEEE 754 half-precision"""
    return float_to_ieee754_half(float(value_int))

# Tradução de instrução TAC para assembly
def traduzirInstrucaoTAC(inst):
    op = inst.get("op")
    if op in ["+", "-", "*", "/", "%", "|", "^"]:
        return traduzirOperacaoAritmetica(inst)
    elif op == "=":
        return traduzirAtribuicao(inst)
    elif op in ["<", ">", "<=", ">=", "==", "!="]:
        return traduzirComparacao(inst)
    elif op == "label":
        return f"{inst['dest']}:\n"
    elif op == "goto":
        return f"\trjmp {inst['dest']}\n"
    elif op == "ifgoto":
        return traduzirIfGoto(inst)
    elif op == "print":
        return traduzirPrint(inst)
    elif op == "ifFalse":
        return traduzirIfFalse(inst)
    else:
        return f"; [ERRO] operação TAC não reconhecida: {op}\n"
    
def traduzirOperacaoAritmetica(inst):
    """Traduz operação aritmética para Assembly"""
    A = inst.get("a")
    B = inst.get("b")
    D = inst.get("dest")
    op = inst.get("op")
    tipo = inst.get("tipo", "int")

    codigo = f"\n; TAC: {D} = {A} {op} {B}\n"
    
    # Carrega operandos
    codigo += carregar_operando(A, "r18", "r19")
    codigo += carregar_operando(B, "r20", "r21")
    
    if tipo == "float":
        if op == "+": codigo += "    rcall f16_add\n"
        elif op == "-": codigo += "    rcall f16_sub\n"
        elif op == "*": codigo += "    rcall f16_mul\n"
        elif op == "/": codigo += "    rcall f16_div\n"
    else:  # int
        if op == "+":
            codigo += "    movw r24, r18\n"
            codigo += "    add  r24, r20\n"
            codigo += "    adc  r25, r21\n"
        elif op == "-":
            codigo += "    movw r24, r18\n"
            codigo += "    sub  r24, r20\n"
            codigo += "    sbc  r25, r21\n"
        elif op == "*":
            codigo += gerar_mul16("r18", "r19", "r20", "r21", "r22", "r23")
            codigo += "    movw r24, r22\n"
        elif op == "/":
            codigo += gerar_div16("r18", "r19", "r20", "r21", "r22", "r23")
    
    # Salva resultado
    codigo += f"    sts {D}, r24\n"
    codigo += f"    sts {D}+1, r25\n"
    
    return codigo

def traduzirAtribuicao(inst):
    A = inst.get("a")
    D = inst.get("dest")
    tipo_a = inst.get("tipo_a", "int")
    
    codigo = f"\n; {D} = {A}\n"
    
    # Carrega valor em r20:r21
    if isinstance(A, int):
        lo = A & 0xFF
        hi = (A >> 8) & 0xFF
        codigo += f"    ldi r20, 0x{lo:02X}\n"
        codigo += f"    ldi r21, 0x{hi:02X}\n"
    elif isinstance(A, float) and tipo_a == 'float':
        ieee_value = float_to_ieee754_half(A)
        lo = ieee_value & 0xFF
        hi = (ieee_value >> 8) & 0xFF
        codigo += f"    ldi r20, 0x{lo:02X}\n"
        codigo += f"    ldi r21, 0x{hi:02X}\n"
    else:
        # Carrega de outra variável
        codigo += f"    lds r20, {A}\n"
        codigo += f"    lds r21, {A}+1\n"
    
    # Armazena no destino
    codigo += f"    sts {D}, r20\n"
    codigo += f"    sts {D}+1, r21\n"
    
    return codigo

def traduzirIfGoto(inst):
    cond = inst.get("a")
    destino = inst.get("dest")
    return f"\n    lds r16, {cond}\n    cpi r16, 0\n    brne {destino}\n"

def traduzirIfFalse(inst):
    cond = inst.get("a")
    destino = inst.get("dest")

    codigo = f"\n; ifFalse {cond} goto {destino}\n"
    
    # Caso 1: condição é comparação (dict)
    if isinstance(cond, dict) and cond.get("op") in ["<=", "<", ">", ">=", "==", "!="]:
        op = cond["op"]
        a = cond["a"]
        b = cond["b"]

        codigo += f"    lds r16, {a}\n"
        codigo += f"    lds r17, {a}+1\n"
        codigo += f"    lds r18, {b}\n"
        codigo += f"    lds r19, {b}+1\n"

        codigo += "    cp r16, r18\n"
        codigo += "    cpc r17, r19\n"

        if op == "<=": codigo += f"    brgt {destino}\n"
        elif op == "<": codigo += f"    brge {destino}\n"
        elif op == ">=": codigo += f"    brlt {destino}\n"
        elif op == ">": codigo += f"    brle {destino}\n"
        elif op == "==": codigo += f"    brne {destino}\n"
        elif op == "!=": codigo += f"    breq {destino}\n"

        return codigo

    # Caso 2: condição é número ou variável (como INDICE)
    else:
        if isinstance(cond, int):
            lo = cond & 0xFF
            hi = (cond >> 8) & 0xFF
            codigo += f"    ldi r16, 0x{lo:02X}\n"
            codigo += f"    ldi r17, 0x{hi:02X}\n"
        else:
            codigo += f"    lds r16, {cond}\n"
            codigo += f"    lds r17, {cond}+1\n"
        
        codigo += "    or r16, r17\n"
        codigo += f"    breq {destino}\n"

        return codigo

def traduzirComparacao(inst):
    """Gera código para comparação entre valores"""
    A = inst.get("a")
    B = inst.get("b")
    D = inst.get("dest")
    op = inst.get("op")

    # Gera labels únicos usando contador global ao invés do nome do destino
    label_id = novo_label().replace('L', '')  # Remove 'L' para ficar só o número
    label_true = f"_cmp_true_{label_id}"
    label_end  = f"_cmp_end_{label_id}"
    
    codigo = f"\n; {D} = {A} {op} {B}\n"
    
    codigo += carregar_operando(A, "r18", "r19")
    codigo += carregar_operando(B, "r20", "r21")

    codigo += "    cp  r18, r20\n"
    codigo += "    cpc r19, r21\n"

    # zera false (resultado padrão)
    codigo += "    ldi r24, 0\n"
    codigo += "    ldi r25, 0\n"
    
    # Define resultado baseado no operador
    if op == "<":
        codigo += f"    brlo {label_true}\n"
    elif op == "<=":
        codigo += f"    brlo {label_true}\n"
        codigo += f"    breq {label_true}\n"
    elif op == ">":
        codigo += f"    brsh {label_end}\n"
        codigo += f"    rjmp {label_true}\n"
    elif op == ">=":
        codigo += f"    brlo {label_end}\n"
        codigo += f"    rjmp {label_true}\n"
    elif op == "==":
        codigo += f"    breq {label_true}\n"
    elif op == "!=":
        codigo += f"    brne {label_true}\n"

    codigo += f"    rjmp {label_end}\n"
    codigo += f"{label_true}:\n"
    codigo += "    ldi r24, 1\n"
    codigo += f"{label_end}:\n"

    codigo += f"    sts {D}, r24\n"
    codigo += f"    sts {D}+1, r25\n"
    return codigo

def traduzirPrint(inst):
    """Imprime valor com formatação correta"""
    A = inst.get("a")
    tipo = inst.get("tipo_a", inst.get("tipo", "int"))
    
    codigo = f"\n; PRINT {A} (tipo: {tipo})\n"
    
    if isinstance(A, int):
        lo = A & 0xFF
        hi = (A >> 8) & 0xFF
        codigo += f"    ldi r24, 0x{lo:02X}\n    ldi r25, 0x{hi:02X}\n"
    else:
        codigo += f"    lds r24, {A}\n    lds r25, {A}+1\n"
    
    if tipo == 'float':
        codigo += "    rcall UART_printIEEE754\n"
    else:
        codigo += "    rcall UART_printHex16\n"
    
    # Adiciona newline SEMPRE
    codigo += "    ldi r24, 0x0D\n    rcall UART_sendByte\n"  # CR
    codigo += "    ldi r24, 0x0A\n    rcall UART_sendByte\n"  # LF
    
    return codigo

def gerarAssembly(tacOtimizado, tabela_simbolos):
    assembly = []
    assembly.append(".equ RAMEND, 0x08FF")
    assembly.append(".equ SPL, 0x3D")
    assembly.append(".equ SPH, 0x3E")
    assembly.append(".equ TXEN0, 0x03")
    assembly.append(".equ UBRR0H, 0xC5")
    assembly.append(".equ UBRR0L, 0xC4")
    assembly.append(".equ UCSR0A, 0xC0")
    assembly.append(".equ UCSR0B, 0xC1")
    assembly.append(".equ UCSR0C, 0xC2")
    assembly.append(".equ UCSZ00, 0x01")
    assembly.append(".equ UCSZ01, 0x02")
    assembly.append(".equ UDR0, 0xC6")

    variaveis = mapear_variaveis(tacOtimizado, tabela_simbolos)
    assembly.append(gerar_secao_dados(variaveis))

    assembly.append("\n.global main")
    assembly.append(ROTINAS_UART)
    assembly.append(ROTINA_PRINT_IEEE754)
    assembly.append(OPERACOES_IEEE754)

    assembly.append("\n\nmain:\n    ; inicializa pilha\n    ldi r16, hi8(RAMEND)\n    out SPH, r16\n    ldi r16, lo8(RAMEND)\n    out SPL, r16\n")
    assembly.append("    rcall UART_init\n")

    # Teste inicial - imprime caractere de teste
    assembly.append("\n    ; Teste inicial UART\n")
    assembly.append("    ldi r24, 'O'\n")
    assembly.append("    rcall UART_sendByte\n")
    assembly.append("    ldi r24, 'K'\n")
    assembly.append("    rcall UART_sendByte\n")
    assembly.append("    ldi r24, 0x0D\n")
    assembly.append("    rcall UART_sendByte\n")
    assembly.append("    ldi r24, 0x0A\n")
    assembly.append("    rcall UART_sendByte\n\n")

    for inst in tacOtimizado:
        codigo = traduzirInstrucaoTAC(inst)
        assembly.append(codigo)

    # Epílogo
    assembly.append("\n; Fim do programa")
    assembly.append("fim:")
    assembly.append("    rjmp fim  ; Loop infinito\n")

    texto = "\n".join(assembly)
    linhas = texto.split("\n")
    nova = []
    vistos = set()

    for linha in linhas:
        stripped = linha.strip()
        if stripped.endswith(":"):
            if stripped in vistos:
                continue
            vistos.add(stripped)
        nova.append(linha)

    texto = "\n".join(nova)

    with open("./src/saida.s", "w", encoding="utf-8") as f:
        f.write(texto)

    print("\n✓ Arquivo Assembly gerado: saida.s")
    return assembly

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

    if historico_resultados:
        # Pega o último resultado da tabela de símbolos ou última variável
        ultima_linha = historico_resultados[-1]

        # Procura por variáveis na última linha que foram modificadas
        ultima_var = None
        for nome, info in tabela_simbolos.items():
            if info.get('linha_declaracao') == len(linhas):
                ultima_var = nome
                break

        # Se não encontrou, usa a primeira variável declarada (FATORIAL no caso)
        if not ultima_var and tabela_simbolos:
            # Procura por FATORIAL ou a última variável declarada
            for nome in ['FATORIAL', 'resultado', 'RES']:
                if nome in tabela_simbolos:
                    ultima_var = nome
                    break

            if not ultima_var:
                # Usa qualquer variável
                ultima_var = list(tabela_simbolos.keys())[-1]

        if ultima_var:
            tipo_var = tabela_simbolos[ultima_var].get('tipo', 'int')

            print(f"Adicionando PRINT para variável: {ultima_var} (tipo: {tipo_var})")

            # Adiciona instrução TAC para print
            tac_completo.append({
                'op': 'print',
                'a': ultima_var,
                'tipo': tipo_var,
                'tipo_a': tipo_var,
                'comment': f'print resultado final: {ultima_var}'
            })

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

    gerarAssembly(tac_otimizado, tabela_simbolos)

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