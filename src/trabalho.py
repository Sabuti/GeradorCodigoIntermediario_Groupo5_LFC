# Integrantes do grupo:
# Ana Maria Midori Rocha Hinoshita - anamariamidori
# Lucas Antonio Linhares - Sabuti
#
# Nome do grupo no Canvas: RA4 5

import sys
import math

EPS = 'E'

# -------------------------
# Função para ler arquivo linha por linha
def lerArquivo(nomeArquivo):
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

# -------------------------
# Função para separar tokens em uma linha
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

# -------------------------
# Funções de estado para o analisador léxico
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

def RESorMEM(token):
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

# -------------------------
# Analisador léxico
def analisadorLexico(tokens_originais):
    tokens_convertidos = []
    tokens_valores = []
    
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

# -------------------------
# Analisador sintático
def analisadorSintatico(tokens, tabelaLL1):
    stack = ['$', 'LINHA']
    derivation = []
    index = 0
    nonterminals = {A for (A, _) in tabelaLL1.keys()}

    def is_nonterminal(sym):
        return sym in nonterminals

    while stack:
        top = stack.pop()
        if index < len(tokens):
            current_token = tokens[index]
        else:
            current_token = '$'
        
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
                production = tabelaLL1[key]
                derivation.append((top, production))
                for sym in reversed(production):
                    if sym != EPS:
                        stack.append(sym)
            else:
                raise ValueError(f"Erro Sintático: não há produção para {top}, '{current_token}'")
    
    raise ValueError("Erro Sintático: pilha vazia antes do fim dos tokens")

## FASE 3: ANÁLISE SEMÂNTICA

# -------------------------
# Funções auxiliares para Tabela de Símbolos
def inicializarTabelaSimbolos():
    return {}

def adicionarSimbolo(tabela, nome, tipo='desconhecido', inicializada=False, valor=None, linha=0, escopo='global'):
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
            'linhas_uso': [] # Lista para rastrear linhas onde o símbolo é usado
        }
    return tabela

def buscarSimbolo(tabela, nome):
    return tabela.get(nome, None)

def marcarSimboloUsado(tabela, nome, linha):
    if nome in tabela:
        tabela[nome]['usada'] = True
        if 'linhas_uso' not in tabela[nome]:
            tabela[nome]['linhas_uso'] = []
        if linha not in tabela[nome]['linhas_uso']:
            tabela[nome]['linhas_uso'].append(linha)

# -------------------------
# Definição da Gramática de Atributos
def definirGramaticaAtributos():
    regras_semanticas = {
        'operadores_aritmeticos': {
            '+': {'aceita': ['int', 'float'], 'retorna': 'promover'},
            '-': {'aceita': ['int', 'float'], 'retorna': 'promover'},
            '*': {'aceita': ['int', 'float'], 'retorna': 'promover'},
            '|': {'aceita': ['int', 'float'], 'retorna': 'float'},
            '/': {'aceita': ['int'], 'retorna': 'int'},
            '%': {'aceita': ['int'], 'retorna': 'int'},
            '^': {'aceita_base': ['int', 'float'], 'aceita_exp': ['int'], 'retorna': 'promover'}
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

def promoverTipo(tipo1, tipo2):
    if tipo1 == 'float' or tipo2 == 'float':
        return 'float'
    if tipo1 == 'int' and tipo2 == 'int':
        return 'int'
    if tipo1 == 'booleano' or tipo2 == 'booleano':
        return 'booleano'
    return 'desconhecido'

# -------------------------
# Construção da gramática LL(1)
def construirGramatica():
    def is_nonterminal(sym, G):
        return sym in G

    def calcularFirst(G):
        FIRST = {A: set() for A in G}
        changed = True
        while changed:
            changed = False
            for A in G:
                for prod in G[A]:
                    if len(prod) == 0:
                        if EPS not in FIRST[A]:
                            FIRST[A].add(EPS)
                            changed = True
                        continue
                    add_epsilon = True
                    for sym in prod:
                        if sym == EPS:
                            if EPS not in FIRST[A]:
                                FIRST[A].add(EPS)
                                changed = True
                            add_epsilon = False
                            break
                        if not is_nonterminal(sym, G):
                            if sym not in FIRST[A]:
                                FIRST[A].add(sym)
                                changed = True
                            add_epsilon = False
                            break
                        else:
                            before = len(FIRST[A])
                            FIRST[A].update(x for x in FIRST[sym] if x != EPS)
                            if len(FIRST[A]) != before:
                                changed = True
                            if EPS in FIRST[sym]:
                                add_epsilon = True
                            else:
                                add_epsilon = False
                                break
                    if add_epsilon:
                        if EPS not in FIRST[A]:
                            FIRST[A].add(EPS)
                            changed = True
        return FIRST

    def first_of_sequence(seq, FIRST, G):
        result = set()
        if len(seq) == 0:
            result.add(EPS)
            return result
        add_epsilon = True
        for sym in seq:
            if sym == EPS:
                result.add(EPS)
                add_epsilon = False
                break
            if not is_nonterminal(sym, G):
                result.add(sym)
                add_epsilon = False
                break
            else:
                result.update(x for x in FIRST[sym] if x != EPS)
                if EPS in FIRST[sym]:
                    add_epsilon = True
                else:
                    add_epsilon = False
                    break
        if add_epsilon:
            result.add(EPS)
        return result

    def calcularFollow(G, FIRST, start='LINHA'):
        FOLLOW = {A: set() for A in G}
        FOLLOW[start].add('$')
        changed = True
        while changed:
            changed = False
            for A in G:
                for prod in G[A]:
                    for i, B in enumerate(prod):
                        if not is_nonterminal(B, G):
                            continue
                        beta = prod[i+1:]
                        first_beta = first_of_sequence(beta, FIRST, G)
                        before = len(FOLLOW[B])
                        FOLLOW[B].update(x for x in first_beta if x != EPS)
                        if EPS in first_beta or len(beta) == 0:
                            FOLLOW[B].update(FOLLOW[A])
                        if len(FOLLOW[B]) != before:
                            changed = True
        return FOLLOW

    def construirTabelaLL1(G, FIRST, FOLLOW):
        table = {}
        conflicts = []
        for A in G:
            for prod in G[A]:
                first_prod = first_of_sequence(prod, FIRST, G)
                for a in (first_prod - {EPS}):
                    key = (A, a)
                    if key in table and table[key] != prod:
                        conflicts.append((key, table[key], prod))
                    else:
                        table[key] = prod
                if EPS in first_prod:
                    for b in FOLLOW[A]:
                        key = (A, b)
                        if key in table and table[key] != prod:
                            conflicts.append((key, table[key], prod))
                        else:
                            table[key] = prod
        return table, conflicts

    G = {}
    G['LINHA'] = [['EXPR']]
    G['EXPR'] = [['(', 'ITEMS', ')']]
    G['ITEMS'] = [['ITEM', 'ITEMS'], [EPS]]
    G['ITEM'] = [['NUMERO'], ['IDENT'], ['OPERADOR'], ['IFKW'], ['WHILEKW'], ['EXPR']]
    G['NUMERO'] = [['float'], ['int']]
    G['IDENT'] = [['ident'], ['res']]
    G['OPERADOR'] = [['+'], ['-'], ['*'], ['/'], ['%'], ['^'], ['|'], 
                     ['>'], ['<'], ['>='], ['<='], ['=='], ['!=']]
    G['IFKW'] = [['if']]
    G['WHILEKW'] = [['while']]

    FIRST = calcularFirst(G)
    FOLLOW = calcularFollow(G, FIRST, start='LINHA')
    tabelaLL1, conflitos = construirTabelaLL1(G, FIRST, FOLLOW)

    if conflitos:
        print("Conflitos encontrados na tabela LL(1):")
        for (A, a), prod1, prod2 in conflitos:
            print(f"  Não determinismo para ({A}, {a}): {prod1} e {prod2}")
        raise ValueError("Gramática não é LL(1) devido a conflitos na tabela.")
    
    return G, FIRST, FOLLOW, tabelaLL1

# -------------------------
# Analisador Semântico - Verificação de Tipos
def analisarSemantica(derivacao, tokens_valores, tabela_simbolos, regras_semanticas, historico_resultados, numero_linha):
    erros = []
    arvore_anotada = []
    pilha_tipos = []
    pilha_valores = []
    elementos_expr = []
    idx_valor = 0
    profundidade = 0

    atribuicoes_nomes = set()

    for i, token in enumerate(tokens_valores):
        if token == '(':
            if profundidade == 0:
                elementos_expr = []
            elif profundidade == 1:
                sub_prof = 1
                i += 1
                while i < len(tokens_valores) and sub_prof > 0:
                    if tokens_valores[i] == '(':
                        sub_prof += 1
                    elif tokens_valores[i] == ')':
                        sub_prof -= 1
                    i += 1
                elementos_expr.append(('subexpr', None))
            profundidade += 1

        elif token == ')':
            profundidade -= 1
            if profundidade == 0:
                if len(elementos_expr) == 2: #verificar se é atribuição (len==2 e segundo é ident)
                    tipo1, val1 = elementos_expr[0]
                    tipo2, val2 = elementos_expr[1]
                    if tipo2 == 'ident' and val2 is not None:
                        if tipo1 in ['int', 'float', 'subexpr', 'ident', 'res']:
                            atribuicoes_nomes.add(val2)
                elementos_expr = []

        elif profundidade == 1 and token not in ['(', ')']:
            if isinstance(token, int):
                elementos_expr.append(('int', None))
            elif isinstance(token, float):
                elementos_expr.append(('float', None))
            elif token in ['+', '-', '*', '/', '%', '^', '|', '<', '>', '<=', '>=', '==', '!=']:
                elementos_expr.append(('op', token))
            elif token in ['RES', 'res']:
                elementos_expr.append(('res', None))
            elif token in ['IF', 'if']:
                elementos_expr.append(('if', None))
            elif token in ['WHILE', 'while']:
                elementos_expr.append(('while', None))
            elif isinstance(token, str):
                elementos_expr.append(('ident', token))
        i += 1

    tokens_processaveis = [v for v in tokens_valores if v not in ['(', ')']]
    memorias_declaradas_nesta_linha = set()
    
    for nao_terminal, producao in derivacao:
        if not producao or producao == [EPS]:
            continue
        
        for simbolo in producao:

            if simbolo in ['(', ')']:
                continue

            if simbolo == 'int':
                if idx_valor >= len(tokens_processaveis):
                    erros.append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: Token inesperado")
                    continue

                tipo = 'int'
                valor = tokens_processaveis[idx_valor]
                idx_valor += 1

                pilha_tipos.append(tipo)
                pilha_valores.append(valor)
                arvore_anotada.append({
                    'tipo_no': 'LITERAL',
                    'tipo_inferido': tipo,
                    'valor': valor,
                    'linha': numero_linha
                })
            
            elif simbolo == 'float':
                if idx_valor >= len(tokens_processaveis):
                    erros.append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: Token inesperado")
                    continue

                tipo = 'float'
                valor = tokens_processaveis[idx_valor]
                idx_valor += 1

                pilha_tipos.append(tipo)
                pilha_valores.append(valor)
                arvore_anotada.append({
                    'tipo_no': 'LITERAL',
                    'tipo_inferido': tipo,
                    'valor': valor,
                    'linha': numero_linha
                })
            
            elif simbolo == 'ident':
                if idx_valor >= len(tokens_processaveis):
                    erros.append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: Token inesperado")
                    continue

                nome = tokens_processaveis[idx_valor]
                idx_valor += 1

                if nome in ['(', ')', '+', '-', '*', '/', '%', '^', '|',
                            '<', '>', '<=', '>=', '==', '!=', 'IF', 'WHILE', 'RES', 'res']:
                    erros.append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: "
                                f"Token sintático '{nome}' tratado como identificador inválido")
                    continue

                eh_atribuicao = nome in atribuicoes_nomes

                if eh_atribuicao:
                    if len(pilha_tipos) < 1:
                        erros.append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: Atribuição requer valor")
                        continue
                    tipo_valor = pilha_tipos.pop()
                    valor = pilha_valores.pop() if pilha_valores else None
                    tabela_simbolos = adicionarSimbolo(
                        tabela_simbolos, nome, tipo_valor, True, valor, numero_linha
                    )

                    memorias_declaradas_nesta_linha.add(nome)
                    pilha_tipos.append(tipo_valor)
                    pilha_valores.append(valor)

                    arvore_anotada.append({
                        'tipo_no': 'ATRIBUICAO',
                        'tipo_inferido': 'desconhecido',
                        'nome': nome,
                        'valor': None,
                        'linha': numero_linha
                    })

                else: # Leitura. Exemplo: (MEM)
                    info = buscarSimbolo(tabela_simbolos, nome)
                    if info is None:
                        erros.append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: Variável '{nome}' usada sem declaração prévia\nContexto: ({nome})")
                        tipo = 'desconhecido'
                        valor = "X"
                        tipo_valor = 'desconhecido'

                        tabela_simbolos = adicionarSimbolo(
                        tabela_simbolos, nome, tipo_valor, False, valor, numero_linha
                    )
                    elif not info['inicializada']:
                        erros.append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: Memória '{nome}' utilizada sem inicialização\nContexto: ({nome})")
                        tipo = info['tipo']
                        valor = "X"
                        tipo_valor = 'desconhecido'

                        tabela_simbolos = adicionarSimbolo(
                        tabela_simbolos, nome, tipo_valor, False, valor, numero_linha
                    )
                    else:
                        tipo = info['tipo']
                        valor = info['valor']
                        marcarSimboloUsado(tabela_simbolos, nome, numero_linha) # Marca o símbolo como usado
                    
                    pilha_tipos.append(tipo)
                    pilha_valores.append(valor)

                    arvore_anotada.append({
                        'tipo_no': 'LEITURA_VARIAVEL',
                        'tipo_inferido': tipo,
                        'nome': nome,
                        'linha': numero_linha
                    })
            
            elif simbolo == 'res':
                if idx_valor >= len(tokens_processaveis):
                    erros.append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: Token inesperado")
                    continue

                if tokens_processaveis[idx_valor] not in ['RES', 'res']:
                    erros.append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: Esperado 'RES', encontrado '{tokens_processaveis[idx_valor]}'")
                    idx_valor += 1
                    continue
                    
                idx_valor += 1  # Consome o 'RES'

                if len(pilha_tipos) < 1:
                    erros.append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: RES requer um parâmetro")
                    pilha_tipos.append('desconhecido')
                    pilha_valores.append(None)

                    arvore_anotada.append({
                        'tipo_no': 'RES',
                        'tipo_inferido': 'desconhecido',
                        'parametro': None,
                        'linha': numero_linha
                    })
                    continue

                tipo_param = pilha_tipos.pop()
                n_valor = pilha_valores.pop() if pilha_valores else None

                # Validação de tipo
                if tipo_param != 'int':
                    erros.append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: RES requer parâmetro inteiro, recebeu '{tipo_param}'")
                    pilha_tipos.append('desconhecido')
                    pilha_valores.append(None)

                    arvore_anotada.append({
                        'tipo_no': 'RES',
                        'tipo_inferido': 'desconhecido',
                        'parametro': 0,
                        'linha': numero_linha
                    })
                    continue

                # Verificação de valor
                if not isinstance(n_valor, int):
                    erros.append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: RES com valor inválido: {n_valor}")
                    pilha_tipos.append('desconhecido')
                    pilha_valores.append(None)

                    arvore_anotada.append({
                        'tipo_no': 'RES',
                        'tipo_inferido': 'desconhecido',
                        'parametro': 0,
                        'linha': numero_linha
                    })
                    continue

                n = int(n_valor)
                if n < 0:
                    erros.append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: RES requer N não negativo")
                    tipo_resultado = 'desconhecido'
                elif n >= len(historico_resultados):
                    erros.append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: RES({n}) referencia linha inexistente")
                    tipo_resultado = 'desconhecido'
                else:
                    idx_resultado = len(historico_resultados) - 1 - n
                    tipo_resultado = historico_resultados[idx_resultado]['tipo']

                pilha_tipos.append(tipo_resultado)
                pilha_valores.append(None)

                arvore_anotada.append({
                    'tipo_no': 'RES',
                    'tipo_inferido': tipo_resultado,
                    'parametro': n,
                    'linha': numero_linha
                })

            elif simbolo in ['+', '-', '*', '/', '%', '^', '|']:
                if idx_valor >= len(tokens_processaveis):
                    erros.append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: Token inesperado")
                    continue

                idx_valor += 1  # Avança o operador em tokens_valores

                if len(pilha_tipos) < 2:
                    erros.append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: "
                                f"Operador '{simbolo}' requer dois operandos\nContexto: operação incompleta")
                    continue
                
                tipo2 = pilha_tipos.pop()
                tipo1 = pilha_tipos.pop()
                pilha_valores.pop()
                pilha_valores.pop()
                
                regra = regras_semanticas['operadores_aritmeticos'][simbolo]
                
                if simbolo == '^':
                    if tipo1 not in regra['aceita_base']:
                        erros.append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: Potência requer base int ou float\nContexto: ({tipo1} {tipo2} ^)")
                    if tipo2 != 'int':
                        erros.append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: Potência requer expoente inteiro\nContexto: ({tipo1} {tipo2} ^)")
                    tipo_resultado = promoverTipo(tipo1, 'int')
                
                elif simbolo in ['/', '%']:
                    if tipo1 != 'int' or tipo2 != 'int':
                        erros.append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: Operador '{simbolo}' requer operandos inteiros\nContexto: ({tipo1} {tipo2} {simbolo})")
                    tipo_resultado = 'int' # retorna int para não causar cascata de erros
                
                elif simbolo == '|':
                    if tipo1 not in regra['aceita'] or tipo2 not in regra['aceita']:
                        erros.append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: Divisão float requer operandos numéricos\nContexto: ({tipo1} {tipo2} |)")
                    tipo_resultado = 'float'
                
                else:
                    if tipo1 not in regra['aceita'] or tipo2 not in regra['aceita']:
                        erros.append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: Operador '{simbolo}' com tipos incompatíveis\nContexto: ({tipo1} {tipo2} {simbolo})")
                    tipo_resultado = promoverTipo(tipo1, tipo2)
                
                if tipo_resultado == 'desconhecido':
                    pilha_tipos.append('desconhecido')
                    pilha_valores.append(None)
                    continue

                pilha_tipos.append(tipo_resultado)
                pilha_valores.append(None)
                
                arvore_anotada.append({
                    'tipo_no': 'OPERACAO',
                    'operador': simbolo,
                    'tipo_inferido': tipo_resultado,
                    'operandos': [tipo1, tipo2],
                    'linha': numero_linha
                })
            
            elif simbolo in ['<', '>', '<=', '>=', '==', '!=']:
                if idx_valor >= len(tokens_processaveis):
                    erros.append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: Token inesperado")
                    continue

                idx_valor += 1  # Avança o operador em tokens_valores

                if len(pilha_tipos) < 2:
                    erros.append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: Operador '{simbolo}' requer dois operandos\nContexto: comparação incompleta")
                    continue
                
                tipo2 = pilha_tipos.pop()
                tipo1 = pilha_tipos.pop()
                pilha_valores.pop()
                pilha_valores.pop()
                
                regra = regras_semanticas['operadores_relacionais'][simbolo]
                
                if tipo1 not in regra['aceita'] or tipo2 not in regra['aceita']:
                    erros.append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: Comparação '{simbolo}' com tipos incompatíveis\nContexto: ({tipo1} {tipo2} {simbolo})")
                
                tipo_resultado = 'booleano'
                pilha_tipos.append(tipo_resultado)
                pilha_valores.append(None)
                
                arvore_anotada.append({
                    'tipo_no': 'COMPARACAO',
                    'operador': simbolo,
                    'tipo_inferido': tipo_resultado,
                    'operandos': [tipo1, tipo2],
                    'linha': numero_linha
                })
            
            elif simbolo == 'if':
                if idx_valor >= len(tokens_processaveis):
                    erros.append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: Token inesperado")
                    continue

                idx_valor += 1  # Avança o operador em tokens_valores

                if len(pilha_tipos) < 3:
                    erros.append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: IF requer condição e dois ramos\nContexto: estrutura IF incompleta")
                    continue
                
                tipo_else = pilha_tipos.pop()
                tipo_then = pilha_tipos.pop()
                tipo_cond = pilha_tipos.pop()
                pilha_valores.pop()
                pilha_valores.pop()
                pilha_valores.pop()
                
                if tipo_cond != 'booleano':
                    erros.append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: IF sem condição de comparação válida\nContexto: condição tipo '{tipo_cond}'")
                
                tipo_resultado = promoverTipo(tipo_then, tipo_else)
                pilha_tipos.append(tipo_resultado)
                pilha_valores.append(None)
                
                arvore_anotada.append({
                    'tipo_no': 'CONDICIONAL_IF',
                    'tipo_inferido': tipo_resultado,
                    'tipo_condicao': tipo_cond,
                    'tipos_ramos': [tipo_then, tipo_else],
                    'linha': numero_linha
                })
            
            elif simbolo == 'while':
                if idx_valor >= len(tokens_processaveis):
                    erros.append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: Token inesperado")
                    continue
                
                idx_valor += 1  # Avança o operador em tokens_valores

                if len(pilha_tipos) < 2:
                    erros.append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: WHILE requer condição e corpo\nContexto: estrutura WHILE incompleta")
                    continue
                
                tipo_corpo = pilha_tipos.pop()
                tipo_cond = pilha_tipos.pop()
                pilha_valores.pop()
                pilha_valores.pop()
                
                if tipo_cond != 'booleano':
                    erros.append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: WHILE sem condição de comparação válida\nContexto: condição tipo '{tipo_cond}'")
                
                tipo_resultado = tipo_corpo
                pilha_tipos.append(tipo_resultado)
                pilha_valores.append(None)
                
                arvore_anotada.append({
                    'tipo_no': 'LOOP_WHILE',
                    'tipo_inferido': tipo_resultado,
                    'tipo_condicao': tipo_cond,
                    'tipo_corpo': tipo_corpo,
                    'linha': numero_linha
                })

    tipo_final = pilha_tipos[-1] if pilha_tipos else 'desconhecido'
    
    return tabela_simbolos, erros, arvore_anotada, tipo_final, memorias_declaradas_nesta_linha

# -------------------------
# Analisador Semântico - Validação de Memória
def analisarSemanticaMemoria(tabela_simbolos, numero_linha, memorias_declaradas_nesta_linha):
    erros = []
    for nome in memorias_declaradas_nesta_linha:
        if nome in ['(', ')', '+', '-', '*', '/', '%', '^', '|', '<', '>', '<=', '>=', '==', '!=']:
            continue

        info = tabela_simbolos.get(nome)
        if not info:
            continue

        # 🔹 Se foi uma atribuição (linha de declaração == linha atual), ignora
        if info['linha_declaracao'] == numero_linha:
            continue

    return erros

# -------------------------
# Analisador Semântico - Validação de Estruturas de Controle
def analisarSemanticaControle(arvore_anotada, numero_linha):
    erros = []
    for no in arvore_anotada:
        if no['tipo_no'] == 'CONDICIONAL_IF':
            if no['tipo_condicao'] != 'booleano':
                erros.append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: IF com condição não booleana")
        elif no['tipo_no'] == 'LOOP_WHILE':
            if no['tipo_condicao'] != 'booleano':
                erros.append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: WHILE com condição não booleana")
    return erros

# -------------------------
# Geração da Árvore Atribuída
def gerarArvoreAtribuida(arvore_anotada, tipo_final, numero_linha):
    arvore_atribuida = {
        'tipo_no': 'PROGRAMA',
        'tipo_inferido': tipo_final,
        'linha': numero_linha,
        'filhos': arvore_anotada
    }
    return arvore_atribuida

## FASE 4: TAC, ASSEMBLY E OTIMIZAÇÕES

# A convenção usada:
# - temporários gerados: t1, t2, t3, ...
# - variáveis globais são escritas como rótulos .word
# - floats são convertidos para Q8.8 e armazenados como inteiros (16 bits)

TEMP_COUNTER = 0
def novo_temp():
    global TEMP_COUNTER
    TEMP_COUNTER += 1
    return f"t{TEMP_COUNTER}"

def int_to_q8_8_integer(value_float):
    # converte float -> Q8.8 int (arredonda)
    return int(round(value_float * 256.0))

def gerarTAC(arvore_atribuida):
    pass

def otimizarTAC(tac):
    pass

# -------------------------
# Gerador de Assembly (contém rotinas UART e print hex)
PROLOGO = """
    .include "m328pdef.inc"
    .cseg
    .org 0x0000
    rjmp main
"""

EPILOGO = """
; fim do programa - trava
fim:
    rjmp fim
"""

# seção dados e helpers
def mapear_variaveis(tac, tabela_simbolos):
    """Mapeia variáveis com seus tipos (int ou float/Q8.8)"""
    vars_map = {}
    for inst in tac:
        for campo in ["a", "b", "dest"]:
            if campo in inst:
                val = inst[campo]
                if isinstance(val, str) and not val.startswith('label_'):
                    if val not in vars_map:
                        # Busca tipo na tabela de símbolos
                        info = tabela_simbolos.get(val)
                        tipo = info['tipo'] if info else inst.get('tipo', 'int')
                        vars_map[val] = {'tipo': tipo, 'storage': '.word 0'}
    return vars_map

def gerar_secao_dados(vars_map):
    saida = [".dseg", ".org 0x0100"]  # coloca dados na SRAM? OBS: .dseg+labels: Para .s puro com .data, isso é simplista.
    # Para compatibilidade com avr-gcc, geraremos .data no formato simples:
    # Porém .s e .include podem aceitar .data/.text; usamos versão simples:
    data_lines = [".data"]
    for nome, tipo in vars_map.items():
        data_lines.append(f"{nome}:\t{tipo}")
    data_lines.append(".text")
    return "\n".join(data_lines)

# gerar carregamento de operando
def load_operand(op, regL, regH):
    """Gera código para mover variável/imediato → registradores (little-endian: low em regL)"""
    if isinstance(op, int):
        lo = op & 0xFF
        hi = (op >> 8) & 0xFF
        return f"\n    ldi {regL}, {lo}\n    ldi {regH}, {hi}\n"
    else:
        # assume label word (little endian)
        return f"\n    lds {regL}, {op}\n    lds {regH}, {op}+1\n"

# rotinas aritméticas já previstas (simplificadas)
def gerar_mul16():
    return """
    ; --- MUL16: A=r22:r23, B=r24:r25 => Ret=r20:r21 ---
    clr  r20
    clr  r21

    mul  r23, r25
    mov  r20, r0
    mov  r21, r1

    mul  r22, r25
    add  r21, r0

    mul  r23, r24
    add  r21, r0

    clr  r1
"""

def gerar_div16():
    return """
    ; --- DIV16 por subtrações sucessivas ---
    clr  r20
    clr  r21

div_loop:
    cp   r22, r24
    cpc  r23, r25
    brlo div_done

    sub  r23, r25
    sbc  r22, r24

    inc  r21
    brne div_loop
    inc  r20
    rjmp div_loop

div_done:
    ; resto em r22:r23, quociente em r20:r21
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
; ----------------------------
; UART routines (9600 @ 16MHz)
; ----------------------------

UART_init:
    ; Set baud 9600 @16MHz: UBRR0 = 103
    ldi r16, 0
    sts UBRR0H, r16
    ldi r16, 103
    sts UBRR0L, r16
    ; enable TX
    ldi r16, (1<<TXEN0)
    sts UCSR0B, r16
    ; frame: 8-bit
    ldi r16, (1<<UCSZ01)|(1<<UCSZ00)
    sts UCSR0C, r16
    ret

; send byte in r24
UART_sendByte:
WaitTX:
    lds r18, UCSR0A
    sbrc r18, UDRE0
    rjmp UART_send_send
    rjmp WaitTX
UART_send_send:
    sts UDR0, r24
    ret

; print string pointed by Z (flash) - uses lpm
UART_printString:
    ; Z must point to string in flash (with terminating 0)
PrintLoop:
    lpm r24, Z+
    tst r24
    breq PrintEnd
    rcall UART_sendByte
    rjmp PrintLoop
PrintEnd:
    ret

; print one hex nibble in r24 (lower 4 bits)
UART_printHexNibble:
    andi r24, 0x0F
    cpi r24, 10
    brlo HexIsDigit
    ; A-F
    subi r24, 10
    ldi r25, ord_A  ; ord_A é preenchido por tabela de dados
    add r24, r25
    rcall UART_sendByte
    ret
HexIsDigit:
    ldi r25, ord_0
    add r24, r25
    rcall UART_sendByte
    ret

; print byte in r24 as two hex chars
UART_printHex8:
    push r18
    push r19
    mov r19, r24
    ; high nibble: swap -> low nibble contains high nibble
    swap r24
    andi r24, 0x0F
    rcall UART_printHexNibble
    ; low nibble: original low nibble
    mov r24, r19
    andi r24, 0x0F
    rcall UART_printHexNibble
    pop r19
    pop r18
    ret

; print 16-bit value in r24:r25 (r25 high)
UART_printHex16:
    ; print high byte then low byte
    push r18
    push r19
    mov r24, r25
    rcall UART_printHex8
    mov r24, r24 ; no-op to ensure sequencing
    mov r24, r24
    mov r24, r24
    mov r24, r24
    mov r24, r24
    mov r24, r24
    mov r24, r24
    ; now low byte
    mov r24, r24 ; placeholder
    mov r24, r24
    mov r24, r24
    ; actually use r24 = low byte
    mov r24, r24
    mov r24, r24
    pop r19
    pop r18
    ; simpler approach: caller must place low byte into r24 and call UART_printHex8
    ret

; Data constants for ASCII offsets
; We'll create labels for '0' and 'A' values used by UART_printHexNibble:
"""

# Because inline assembly macros like ldi r25, ord_A are not defined,
# we'll append ASCII constants in .data and modify UART_printHexNibble to load from those addresses.
ROTINAS_UART_DATA = """
    .data
ord_0: .byte 48
ord_A: .byte 65
    .text
"""

# A safer implementation: implement UART_printHexNibble using immediate compares and adds,
# without referencing ord_0/ord_A memory (to avoid complications). We'll rewrite a clean version here:

ROTINAS_UART_CLEAN = r"""
; Clean versions (no data table)

UART_printHexNibble_clean:
    andi r24, 0x0F
    cpi r24, 10
    brlo HexDigit_clean
    ; A-F: add 'A' - 10 => 65 - 10 = 55
    subi r24, 10
    ldi r18, 55
    add r24, r18
    rcall UART_sendByte
    ret
HexDigit_clean:
    ldi r18, 48
    add r24, r18
    rcall UART_sendByte
    ret

UART_printHex8_clean:
    push r18
    push r19
    mov r19, r24
    swap r24
    andi r24, 0x0F
    rcall UART_printHexNibble_clean
    mov r24, r19
    andi r24, 0x0F
    rcall UART_printHexNibble_clean
    pop r19
    pop r18
    ret

UART_printHex16_clean:
    ; caller puts low byte in r24 and high byte in r25
    push r18
    push r19
    mov r24, r25
    rcall UART_printHex8_clean
    mov r24, r24 ; nop
    mov r24, r24
    mov r24, r24
    mov r24, r24
    ; now print low byte
    mov r24, r24
    mov r24, r24
    ; real low byte must be loaded by caller into r24 before call to UART_printHex8_clean
    ; So we instead expect caller to call UART_printHex8_clean twice:
    pop r19
    pop r18
    ret
"""

# Given complexity of mixing, we'll keep a minimal usable set:
ROTINAS_UART_FINAL = r"""
UART_init:
    ldi r16, 0
    sts UBRR0H, r16
    ldi r16, 103
    sts UBRR0L, r16
    ldi r16, (1<<TXEN0)
    sts UCSR0B, r16
    ldi r16, (1<<UCSZ01)|(1<<UCSZ00)
    sts UCSR0C, r16
    ret

UART_sendByte:
WaitTX2:
    lds r18, UCSR0A
    sbrc r18, UDRE0
    rjmp UART_send_send2
    rjmp WaitTX2
UART_send_send2:
    sts UDR0, r24
    ret

;print nibble (r24 low 4 bits)
UART_printHexNibble2:
    andi r24, 0x0F
    cpi r24, 10
    brlo H2_digit
    subi r24, 10
    ldi r18, 55   ; 'A' - 10 = 65 - 10 = 55
    add r24, r18
    rcall UART_sendByte
    ret
H2_digit:
    ldi r18, 48
    add r24, r18
    rcall UART_sendByte
    ret

UART_printHex8:
    push r18
    push r19
    mov r19, r24
    swap r24
    andi r24, 0x0F
    rcall UART_printHexNibble2
    mov r24, r19
    andi r24, 0x0F
    rcall UART_printHexNibble2
    pop r19
    pop r18
    ret

UART_printHex16:
    ; input: r24 = low byte, r25 = high byte
    push r18
    push r19
    mov r24, r25
    rcall UART_printHex8
    ldi r24, 0x20  ; space separator
    rcall UART_sendByte
    mov r24, r24    ; nop
    mov r24, r24
    mov r24, r24
    ; low byte
    mov r24, r24
    ; actual low byte is in r24 already? Not reliable, so caller should:
    ; Caller will move low byte into r24 and call UART_printHex8 directly.
    pop r19
    pop r18
    ret
"""

ROTINA_PRINT_Q8_8 = r"""
; ============================================================================
; Print Q8.8 como decimal (valor/256.0)
; Input: r24:r25 = valor Q8.8 (little endian)
; ============================================================================
UART_printQ8_8:
    push r18
    push r19
    push r20
    push r21
    push r22
    push r23
    
    ; Separa parte inteira (bits 15-8) e fracionária (bits 7-0)
    mov r22, r25        ; parte inteira em r22
    mov r23, r24        ; parte fracionária em r23
    
    ; Imprime parte inteira (8 bits)
    mov r24, r22
    rcall UART_printDec8
    
    ; Imprime ponto decimal
    ldi r24, '.'
    rcall UART_sendByte
    
    ; Converte fração: (frac * 100) >> 8
    mov r24, r23
    ldi r25, 100
    mul r24, r25        ; r1:r0 = frac * 100
    mov r24, r1         ; pega byte alto (>> 8)
    rcall UART_printDec8
    
    pop r23
    pop r22
    pop r21
    pop r20
    pop r19
    pop r18
    ret

; Imprime byte como decimal (0-255)
UART_printDec8:
    push r18
    push r19
    push r20
    
    ; Divide por 100
    ldi r18, 100
    clr r19
    clr r20
dec_100:
    cp r24, r18
    brlo dec_10
    sub r24, r18
    inc r19
    rjmp dec_100
    
dec_10:
    ; r19 = centenas, r24 = resto
    ; Divide resto por 10
    ldi r18, 10
dec_10_loop:
    cp r24, r18
    brlo dec_1
    sub r24, r18
    inc r20
    rjmp dec_10_loop
    
dec_1:
    ; r19=centenas, r20=dezenas, r24=unidades
    ; Imprime (suprime zeros à esquerda)
    tst r19
    breq skip_cent
    mov r18, r19
    ldi r24, '0'
    add r24, r18
    rcall UART_sendByte
    ldi r21, 1          ; flag: já imprimiu algo
    rjmp print_dez
    
skip_cent:
    clr r21
    
print_dez:
    tst r21
    brne print_dez_force
    tst r20
    breq print_uni
print_dez_force:
    mov r18, r20
    ldi r24, '0'
    add r24, r18
    rcall UART_sendByte
    
print_uni:
    ldi r18, '0'
    add r24, r18
    rcall UART_sendByte
    
    pop r20
    pop r19
    pop r18
    ret
"""

# For clarity, we'll implement in gerarAssembly a simple call sequence:
# - to print 16-bit value v: load low into r24, high into r25, call UART_printHex8 (with r24=low) then move r24=r25 and call UART_printHex8
# Simpler: we'll implement the sequence in Python emitted assembly directly (no reliance on UART_printHex16).

# Tradução de instrução TAC para assembly
def traduzirInstrucaoTAC(inst):
    op = inst.get("op")
    if op in ["+", "-", "*", "/", "%", "|", "^"]:
        return traduzirOperacaoAritmetica(inst)
    elif op == "=":
        return traduzirAtribuicao(inst)
    elif op == "label":
        return f"{inst['dest']}:\n"
    elif op == "goto":
        return f"\trjmp {inst['dest']}\n"
    elif op == "ifgoto":
        return traduzirIfGoto(inst)
    elif op == "print":
        return traduzirPrint(inst)
    else:
        return f"; [ERRO] operação TAC não reconhecida: {op}\n"
    
def converter_operandos_q8_8(left, right, op, tipo_resultado, tac):
    """
    Gera código TAC para converter operandos int->Q8.8 quando necessário
    Retorna: (left_operand, right_operand, tipo_operacao)
    """
    left_name = left['value'] if left['kind']=='imm' else left['name']
    right_name = right['value'] if right['kind']=='imm' else right['name']
    
    # Se resultado é float, promove operandos int para Q8.8
    if tipo_resultado == 'float':
        if left['tipo'] == 'int':
            temp_left = novo_temp()
            if left['kind'] == 'imm':
                # Converte literal int para Q8.8
                val_q8 = int_to_q8_8_integer(left['value'])
                tac.append({
                    'op': '=',
                    'a': val_q8,
                    'dest': temp_left,
                    'tipo': 'float',
                    'tipo_a': 'float'
                })
            else:
                # int_to_q8_8: shift left 8
                tac.append({
                    'op': 'int_to_q8',
                    'a': left_name,
                    'dest': temp_left,
                    'tipo': 'float'
                })
            left_name = temp_left
            
        if right['tipo'] == 'int':
            temp_right = novo_temp()
            if right['kind'] == 'imm':
                val_q8 = int_to_q8_8_integer(right['value'])
                tac.append({
                    'op': '=',
                    'a': val_q8,
                    'dest': temp_right,
                    'tipo': 'float',
                    'tipo_a': 'float'
                })
            else:
                tac.append({
                    'op': 'int_to_q8',
                    'a': right_name,
                    'dest': temp_right,
                    'tipo': 'float'
                })
            right_name = temp_right
    
    return left_name, right_name, tipo_resultado

def traduzirOperacaoAritmetica(inst):
    """Traduz operação com suporte correto a Q8.8"""
    A = inst.get("a")
    B = inst.get("b")
    D = inst.get("dest")
    op = inst.get("op")
    tipo = inst.get("tipo", "int")
    tipo_a = inst.get("tipo_a", "int")
    tipo_b = inst.get("tipo_b", "int")

    codigo = f"\n; TAC: {D} = {A} {op} {B} (tipo: {tipo})\n"
    
    # Carrega operandos
    codigo += load_operand(A, "r23", "r22")  # A em r22:r23 (HI:LO)
    codigo += load_operand(B, "r25", "r24")  # B em r24:r25
    
    if op == "+":
        codigo += "    add r23, r25\n    adc r22, r24\n    movw r20, r22\n"
        
    elif op == "-":
        codigo += "    sub r23, r25\n    sbc r22, r24\n    movw r20, r22\n"
        
    elif op == "*":
        if tipo == 'float':
            # Multiplicação Q8.8: resultado em Q16.16, precisa shift right 8
            codigo += gerar_mul16()
            codigo += "; Shift right 8 bits (Q16.16 -> Q8.8)\n"
            codigo += "    mov r20, r21\n"
            codigo += "    ldi r21, 0\n"
        else:
            codigo += gerar_mul16()
            
    elif op == "/":
        if tipo == 'int':
            codigo += gerar_div16()
        else:
            # Já não deveria chegar aqui - use '|' para divisão float
            codigo += "; ERRO: use | para divisao float\n"
            
    elif op == "|":
        # Divisão float: A<<8 / B
        codigo += "; Divisao Q8.8: shift left A 8 bits\n"
        for _ in range(8):
            codigo += "    lsl r23\n    rol r22\n"
        codigo += gerar_div16()
        
    elif op == "^":
        codigo += gerar_pow16()
        if tipo == 'float':
            # Se operandos eram Q8.8, resultado está em Q8.8^n
            # Precisa normalizar (complexo) - simplificação: aviso
            codigo += "; AVISO: potencia Q8.8 pode overflow\n"
    
    elif op == "int_to_q8":
        # Conversão int -> Q8.8: shift left 8
        codigo += "; Converte int para Q8.8\n"
        for _ in range(8):
            codigo += "    lsl r23\n    rol r22\n"
        codigo += "    movw r20, r22\n"
    
    # Salva resultado
    codigo += f"    sts {D}, r20\n    sts {D}+1, r21\n"
    return codigo

def traduzirAtribuicao(inst):
    A = inst.get("a")
    D = inst.get("dest")
    codigo = f"\n; TAC: {D} = {A}\n"
    codigo += load_operand(A, "r20", "r21")
    codigo += f"    sts {D}, r20\n    sts {D}+1, r21\n"
    return codigo

def traduzirIfGoto(inst):
    cond = inst.get("a")
    destino = inst.get("dest")
    return f"\n    lds r16, {cond}\n    cpi r16, 0\n    brne {destino}\n"

def traduzirPrint(inst):
    """Imprime valor com formatação correta (hex para int, decimal para float)"""
    A = inst.get("a")
    tipo = inst.get("tipo_a", inst.get("tipo", "int"))
    
    codigo = f"\n; PRINT {A} (tipo: {tipo})\n"
    
    if isinstance(A, int):
        lo = A & 0xFF
        hi = (A >> 8) & 0xFF
        codigo += f"    ldi r24, {lo}\n    ldi r25, {hi}\n"
    else:
        codigo += f"    lds r24, {A}\n    lds r25, {A}+1\n"
    
    if tipo == 'float':
        # Imprime como decimal Q8.8
        codigo += "    rcall UART_printQ8_8\n"
    else:
        # Imprime como hex
        codigo += "    mov r18, r25\n    mov r24, r18\n"
        codigo += "    rcall UART_printHex8\n"
        codigo += f"    lds r24, {A}\n" if not isinstance(A, int) else f"    ldi r24, {lo}\n"
        codigo += "    rcall UART_printHex8\n"
    
    codigo += "    ldi r24, 0x0A\n    rcall UART_sendByte\n"
    return codigo

# -------------------------
# Geração de Código Assembly completo
def gerarAssembly(tacOtimizado, tabela_simbolos):
    assembly = []
    assembly.append(PROLOGO)
    # inicialização de pilha (prologue runtime)
    assembly.append("main:\n    ; inicializa pilha\n    ldi r16, HIGH(RAMEND)\n    out SPH, r16\n    ldi r16, LOW(RAMEND)\n    out SPL, r16\n    rcall UART_init\n")

    # Criar mapa de variáveis para memória estática
    variaveis = mapear_variaveis(tacOtimizado, tabela_simbolos)

    assembly.append(gerar_secao_dados(variaveis))

    # Converter cada instrução TAC → AVR
    for inst in tacOtimizado:
        codigo = traduzirInstrucaoTAC(inst)
        assembly.append(codigo)

    # epílogo e trava
    assembly.append(EPILOGO)

    # acrescenta rotinas UART (clean final)
    assembly.append(ROTINAS_UART_FINAL)
    # e rotina print8/printNibble
    assembly.append("""
; UART_printHex8 expects byte in r24
; We'll provide an implementation used above: it uses r24 for byte and outputs two hex chars.
""")
    # salvar em arquivo
    texto = "\n".join(assembly)
    with open("saida.s", "w", encoding="utf-8") as f:
        f.write(texto)
    print("Arquivo Assembly gerado: saida.s")
    return assembly

def main():
    if len(sys.argv) < 2:
        print("Uso correto: python trabalho.py <arquivo_de_entrada>")
        print("Exemplo: python trabalho.py teste1.txt")
        return

    caminho = sys.argv[1]

    # Lê o arquivo de entrada
    linhas = lerArquivo(caminho)
    if linhas is None:
        return

    # Estruturas principais
    tabela_simbolos = inicializarTabelaSimbolos()
    historico_resultados = []
    todos_erros = []
    todas_arvores = []

    # Define as regras semânticas
    regras_semanticas = definirGramaticaAtributos()

    # Constrói a gramática LL(1)
    try:
        G, FIRST, FOLLOW, tabelaLL1 = construirGramatica()
        print("Gramática LL(1) construída com sucesso.")
    except Exception as e:
        print(f"Erro ao construir a gramática: {e}")
        return

    # Processa cada linha do arquivo
    for numero_linha, linha in enumerate(linhas, start=1):

        try:
            # Etapa 1: Análise Léxica
            tokens_originais = []
            parseExpressao(linha, tokens_originais)
            tokens, tokens_valores = analisadorLexico(tokens_originais)
            print(f"  - Análise léxica concluída ({len(tokens)} tokens).")

            # Etapa 2: Análise Sintática
            derivacao = analisadorSintatico(tokens, tabelaLL1)
            print(f"  - Análise sintática concluída ({len(derivacao)} produções).")

            # Etapa 3: Análise Semântica
            tabela_simbolos, erros, arvore_anotada, tipo_final, memorias_declaradas_nesta_linha = analisarSemantica(
                derivacao, tokens_valores, tabela_simbolos,
                regras_semanticas, historico_resultados, numero_linha
            )

            # Validações adicionais
            erros.extend(analisarSemanticaMemoria(tabela_simbolos, numero_linha, memorias_declaradas_nesta_linha))
            erros.extend(analisarSemanticaControle(arvore_anotada, numero_linha))

            # Gera árvore atribuída consolidada
            arvore_atribuida = gerarArvoreAtribuida(arvore_anotada, tipo_final, numero_linha)
            todas_arvores.append(arvore_atribuida)

            # Atualiza histórico (para comandos RES)
            historico_resultados.append({
                'linha': numero_linha,
                'tipo': tipo_final,
                'arvore': arvore_atribuida
            })

            # Etapa 4: Geração de Código Intermediário (TAC)
            tac = gerarTAC(arvore_atribuida, tabela_simbolos)

            tacOt = otimizarTAC(tac)
            print(f"  - TAC gerado ({len(tacOt)} instruções).")
            # Gera Assembly (salva em saida.s)
            gerarAssembly(tacOt, tabela_simbolos)

            # Resultados da linha
            if erros:
                print(f"Erros encontrados ({len(erros)}):\n")
                for e in erros:
                    print(f"- {e}\n")
                    todos_erros.append(e)
                print(f"  - {len(erros)} erro(s) encontrado(s).")
            else:
                print(f"Semântico: OK (tipo final: {tipo_final})\n")
                print("  - Análise semântica concluída sem erros.")

        except ValueError as e:
            msg = str(e)
            todos_erros.append(msg)
            print(f"  - {msg}")

    if todos_erros:
        print("A análise foi concluída com erros. Verifique os relatórios para mais detalhes.")
    else:
        print("A análise foi concluída com sucesso, sem erros encontrados.")

if __name__ == "__main__":
    main()