# Integrantes do grupo:
# Ana Maria Midori Rocha Hinoshita - anamariamidori
# Lucas Antonio Linhares - Sabuti
#
# Nome do grupo no Canvas: RA4 5

import sys
import math

EPS = 'E'

# CONTADORES GLOBAIS PARA TAC

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

def lerArquivo(nomeArquivo):
    """
    Lê um arquivo linha por linha, removendo espaços extras e ignorando linhas vazias.
    Retorna uma lista de strings ou None em caso de erro.
    """
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

        # Separação por espaço
        if char.isspace():
            if token:
                _tokens_.append(token)
                token = ""

        # Parênteses são tokens individuais
        elif char in "()":
            if token:
                _tokens_.append(token)
                token = ""
            _tokens_.append(char)

            # Atualiza contagem de parênteses para verificação posterior
            if char == "(":
                parenteses += 1
            else:
                parenteses -= 1
                if parenteses < 0:
                    # Fecha mais do que abre → erro
                    raise ValueError("Erro Sintático: parêntese fechado sem correspondente.")

        # Operadores aritméticos simples
        elif char in "+-*/%^":
            if token:
                _tokens_.append(token)
                token = ""
            _tokens_.append(char)

        # Operador especial "|" (divisão float)
        elif char == '|':
            if token:
                _tokens_.append(token)
                token = ""
            _tokens_.append(char)

        # Operadores relacionais (<, <=, >, >=, ==, !=)
        elif char in "><=!":
            if token:
                _tokens_.append(token)
                token = ""

            # Verifica se operador é composto (ex.: >=)
            if i + 1 < len(linha) and linha[i + 1] == '=':
                _tokens_.append(char + '=')
                i += 1
            else:
                _tokens_.append(char)

        # Acumula caracteres de identificadores ou números
        else:
            token += char

        i += 1

    # Último token pendente
    if token:
        _tokens_.append(token)

    # Checa se parênteses estão balanceados
    if parenteses != 0:
        raise ValueError("Erro Sintático: parêntese aberto sem correspondente.")

    return True

def estadoNumero(token):
    """
    Determina se um token representa um número inteiro ou real válido.
    Aceita inteiros ou floats com apenas um ponto.
    """
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
    """Retorna True se o token é um operador aritmético simples."""
    return token in ["+", "-", "*", "|", "/", "%", "^"]

def estadoParenteses(token):
    """Verifica se o token é '(' ou ')'."""
    return token in ["(", ")"]

def estadoComparador(token):
    """Verifica se o token é um operador relacional válido."""
    return token in ["<", ">", "<=", ">=", "==", "!="]


def RESorMEM(token: str) -> bool:
    """
    Verifica se o token representa um identificador válido no padrão da linguagem.
    A regra implementada é:
      - Primeiro caractere: letra maiúscula
      - Demais caracteres: letras maiúsculas ou dígitos

    Essa função simula um autômato finito:
      Q0  → espera primeira letra
      QID → aceita sequência de letras maiúsculas e dígitos
    """
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
            # Só permite letras maiúsculas ou dígitos
            if not (ch.isalpha() and ch.isupper()) and not ch.isdigit():
                return False

    return estado == "QID"

def analisadorLexico(tokens_originais: list[str]) -> tuple[list[str], list]:
    """
    Converte uma lista de tokens brutos (strings extraídas do código)
    para:

        - tokens_convertidos: tipos ou classes de tokens 
            ('int', 'float', 'if', 'ident', '+', '(', ...)

        - tokens_valores: valores concretos
            (ex: número convertido para int/float, identificadores mantidos)

    Essa função identifica:
        - Parênteses
        - Operadores aritméticos
        - Operadores relacionais
        - Tipos numéricos
        - Palavras reservadas (RES, IF, WHILE)
        - Identificadores válidos definidos por RESorMEM()
    """

    tokens_convertidos: list[str] = []
    tokens_valores: list = []

    for token in tokens_originais:

        # Parênteses
        if estadoParenteses(token):
            tokens_convertidos.append(token)
            tokens_valores.append(token)
            continue

        # Operadores aritméticos
        if estadoOperador(token):
            tokens_convertidos.append(token)
            tokens_valores.append(token)
            continue

        # Operadores relacionais
        if estadoComparador(token):
            tokens_convertidos.append(token)
            tokens_valores.append(token)
            continue

        # Números (inteiros ou reais)
        if estadoNumero(token):
            if token.count(".") == 1:
                tokens_convertidos.append("float")
                tokens_valores.append(float(token))
            else:
                tokens_convertidos.append("int")
                tokens_valores.append(int(token))
            continue

        # Palavras-chave e identificadores
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
                # Identificador válido
                tokens_convertidos.append("ident")
                tokens_valores.append(token)

            continue

        # Se nada corresponde → erro léxico
        raise ValueError(f"Erro Léxico: token inválido -> {token}")

    return tokens_convertidos, tokens_valores

## FASE 2: ANÁLISE SINTÁTICA

def analisadorSintatico(tokens: list[str], tabelaLL1: dict) -> list[tuple[str, list[str]]]:
    """
    Implementa um analisador sintático LL(1) clássico usando pilha.

    Parâmetros:
        tokens      - lista de tokens já classificados pelo léxico (strings)
        tabelaLL1   - dicionário {(nao-terminal, terminal): produção}

    Retorna:
        derivation - lista de produções aplicadas durante a análise, no formato (A, produção)

    Lógica geral:
        - A pilha inicia com o símbolo inicial 'LINHA' e o símbolo de fim '$'
        - A cada passo, compara topo da pilha com o token atual
        - Se for terminal, deve casar exatamente
        - Se for não-terminal, consulta a tabela LL(1)
        - Substitui produção na pilha (em ordem reversa)
        - Caso não haja produção compatível → erro sintático
    """

    stack: list[str] = ['$', 'LINHA']
    derivation: list[tuple[str, list[str]]] = []
    index = 0

    # Conjunto de não-terminais (chaves da tabela)
    nonterminals = {A for (A, _) in tabelaLL1.keys()}

    def is_nonterminal(sym: str) -> bool:
        return sym in nonterminals

    while stack:
        top = stack.pop()

        # Token atual ou símbolo de fim
        current_token = tokens[index] if index < len(tokens) else '$'

        # Caso aceitação total
        if top == current_token == '$':
            return derivation

        # Caso seja terminal
        if not is_nonterminal(top):
            if top == current_token:
                index += 1
            else:
                raise ValueError(f"Erro Sintático: esperado '{top}', encontrado '{current_token}'")

        # Caso seja não-terminal
        else:
            key = (top, current_token)

            if key in tabelaLL1:
                production: list[str] = tabelaLL1[key]

                derivation.append((top, production))

                # Empilha a produção em ordem reversa
                for sym in reversed(production):
                    if sym != EPS:
                        stack.append(sym)
            else:
                raise ValueError(f"Erro Sintático: não há produção para {top}, '{current_token}'")

    raise ValueError("Erro Sintático: pilha vazia antes do fim dos tokens")

## FASE 3: ANÁLISE SEMÂNTICA

def inicializarTabelaSimbolos() -> dict:
    """
    Cria e retorna uma nova tabela de símbolos vazia.
    A tabela é representada como um dicionário cuja chave é o nome do símbolo
    e o valor é outro dicionário contendo atributos (tipo, valor, escopo etc.).
    """
    return {}

def adicionarSimbolo(tabela: dict, nome: str, tipo: str = 'desconhecido', inicializada: bool = False,
    valor=None, linha: int = 0, escopo: str = 'global' ) -> dict:
    """
    Insere ou atualiza um símbolo na tabela de símbolos.

    - Se o símbolo já existe, atualiza seus campos quando apropriado.
    - Se não existe, cria uma nova entrada completa.

    Parâmetros:
        tabela        - tabela de símbolos onde o símbolo será inserido
        nome          - nome do identificador
      tipo          – tipo do símbolo (int, float, booleano, ...)
        inicializada  - se já recebeu valor
        valor         - valor literal (se conhecido)
        linha         - linha onde foi declarado
        escopo        - escopo atual (global ou algum bloco interno)
    """
    if nome in tabela:
        tabela[nome]['tipo'] = tipo
        tabela[nome]['inicializada'] = inicializada
        tabela[nome]['valor'] = valor

        # Insere linha de declaração apenas se ainda não existir
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
            'linhas_uso': []  # Registra todas as linhas em que o símbolo foi referenciado
        }

    return tabela

def buscarSimbolo(tabela: dict, nome: str):
    """
    Retorna o símbolo correspondente ao nome, ou None caso não exista.
    """
    return tabela.get(nome, None)

def marcarSimboloUsado(tabela: dict, nome: str, linha: int) -> None:
    """
    Marca que um símbolo foi utilizado em uma linha específica.
    Isso é útil para avisar quando variáveis são declaradas mas nunca usadas.
    """
    if nome in tabela:
        tabela[nome]['usada'] = True

        if 'linhas_uso' not in tabela[nome]:
            tabela[nome]['linhas_uso'] = []

        if linha not in tabela[nome]['linhas_uso']:
            tabela[nome]['linhas_uso'].append(linha)

def definirGramaticaAtributos() -> dict:
    """
    Define todas as regras semânticas da linguagem.
    As regras são divididas em categorias semânticas:
        - operadores aritméticos
      - operadores relacionais
      - estruturas de controle
      - comandos especiais (RES, MEM, etc.)

    Cada operador contém:
      - quais tipos aceita
      - qual tipo retorna
      - regras especiais (ex.: promoção de tipo)

    Retorna um dicionário contendo todas as regras.
    """
    regras_semanticas = {
        'operadores_aritmeticos': {
            '+': {'aceita': ['int', 'float'], 'retorna': 'promover'},
            '-': {'aceita': ['int', 'float'], 'retorna': 'promover'},
            '*': {'aceita': ['int', 'float'], 'retorna': 'promover'},
            '|': {'aceita': ['int', 'float'], 'retorna': 'float'},  # divisão float
            '/': {'aceita': ['int'], 'retorna': 'int'},             # divisão inteira
            '%': {'aceita': ['int'], 'retorna': 'int'},
            '^': {  # exponenciação
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
    """
    Aplica a regra de promoção de tipos.
    A promoção ocorre quando a operação precisa elevar o tipo do resultado,
    por exemplo: int + float → float.

    Regras:
        - Se qualquer operando é float → resultado é float
        - Se ambos são int → resultado é int
        - Se qualquer é booleano → resultado é booleano
        - Caso contrário → desconhecido
    """
    if tipo1 == 'float' or tipo2 == 'float':
        return 'float'

    if tipo1 == 'int' and tipo2 == 'int':
        return 'int'

    if tipo1 == 'booleano' or tipo2 == 'booleano':
        return 'booleano'

    return 'desconhecido'

def construirGramatica() -> tuple:
    """
    Constrói a gramática LL(1), seus conjuntos FIRST, FOLLOW e a tabela LL(1).
    Também realiza detecção de conflitos que invalidam a gramática.

    Retorna:
        (G, FIRST, FOLLOW, tabelaLL1):
            G (dict): gramática no formato {NaoTerminal: [produções]}
            FIRST (dict): conjunto FIRST para cada não terminal
            FOLLOW (dict): conjunto FOLLOW para cada não terminal
            tabelaLL1 (dict): tabela LL(1) no formato {(A, a): produção}
    """

    # --------------------------------------------------------
    # Funções internas
    # --------------------------------------------------------

    def is_nonterminal(simbolo: str, G: dict) -> bool:
        """Retorna True se um símbolo é não-terminal da gramática."""
        return simbolo in G

    def calcularFirst(G: dict) -> dict:
        """
        Calcula FIRST para cada não terminal da gramática.
        Implementação clássica iterativa.

        Retorna:
            dict: FIRST[A] = conjunto de símbolos terminais ou ε
        """
        FIRST = {A: set() for A in G}
        alterou = True

        while alterou:
            alterou = False
            for A in G:
                for producao in G[A]:

                    # Produção vazia
                    if len(producao) == 0:
                        if EPS not in FIRST[A]:
                            FIRST[A].add(EPS)
                            alterou = True
                        continue

                    pode_gerar_epsilon = True

                    for simbolo in producao:

                        # Símbolo é ε
                        if simbolo == EPS:
                            if EPS not in FIRST[A]:
                                FIRST[A].add(EPS)
                                alterou = True
                            pode_gerar_epsilon = False
                            break

                        # Terminal
                        if not is_nonterminal(simbolo, G):
                            if simbolo not in FIRST[A]:
                                FIRST[A].add(simbolo)
                                alterou = True
                            pode_gerar_epsilon = False
                            break

                        # Não-terminal
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
        """
        Calcula FIRST de uma sequência de símbolos.

        Retorna:
            set: conjunto FIRST( seq )
        """
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
        """
        Calcula FOLLOW de cada não terminal da gramática.

        Args:
            G: gramática
            FIRST: conjuntos FIRST
            start: símbolo inicial

        Retorna:
            dict: FOLLOW[A]
        """
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
        """
        Constrói a tabela LL(1) no formato:
            tabela[(NaoTerminal, Terminal)] = produção

        Detecta conflitos de entrada múltipla.

        Retorna:
            (tabela, conflitos)
        """
        tabela = {}
        conflitos = []

        for A in G:
            for producao in G[A]:

                first_prod = first_of_sequence(producao, FIRST, G)

                # FIRST sem ε
                for a in (first_prod - {EPS}):
                    chave = (A, a)

                    if chave in tabela and tabela[chave] != producao:
                        conflitos.append((chave, tabela[chave], producao))
                    else:
                        tabela[chave] = producao

                # Caso tenha ε, propaga para FOLLOW
                if EPS in first_prod:
                    for b in FOLLOW[A]:
                        chave = (A, b)

                        if chave in tabela and tabela[chave] != producao:
                            conflitos.append((chave, tabela[chave], producao))
                        else:
                            tabela[chave] = producao

        return tabela, conflitos

    # --------------------------------------------------------
    # Definição formal da gramática
    # --------------------------------------------------------

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

    # FIRST, FOLLOW e tabela LL(1)
    FIRST = calcularFirst(G)
    FOLLOW = calcularFollow(G, FIRST)
    tabelaLL1, conflitos = construirTabelaLL1(G, FIRST, FOLLOW)

    if conflitos:
        for (A, a), p1, p2 in conflitos:
            print(f"Conflito LL(1) em ({A}, {a}): {p1} / {p2}")
        raise ValueError("Gramática não é LL(1).")

    return G, FIRST, FOLLOW, tabelaLL1

def coletar_atribuicoes(tokens_valores: list) -> set:
    """
    Vasculha tokens estruturados para detectar se ocorre padrão de
    atribuição no formato:

        ( <expressão> <identificador> )

    Considerando profundidade:
        - Coleta elementos apenas no nível 1
        - Quando fecha parêntese e volta ao nível 0, checa se há padrão
          de dois elementos, sendo o segundo obrigatoriamente um
          identificador válido.

    Retorna:
        set: nomes de identificadores que aparecem como alvo de atribuição.
    """
    atribuicoes = set()
    profundidade = 0
    elementos_expr = []

    for token in tokens_valores:

        # Abertura de parêntese
        if token == '(':
            if profundidade == 0:
                elementos_expr = []
            profundidade += 1
            continue

        # Fechamento de parêntese
        if token == ')':
            profundidade -= 1

            # Somente fecha atribuições completas ao retomar profundidade 0
            if profundidade == 0 and len(elementos_expr) == 2:
                tipo1, _ = elementos_expr[0]
                tipo2, nome2 = elementos_expr[1]

                if tipo2 == 'ident' and nome2 is not None:
                    if tipo1 in ['int', 'float', 'ident', 'res', 'subexpr']:
                        atribuicoes.add(nome2)

            elementos_expr = []
            continue

        # Coleta apenas no nível 1
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
    """
    Cria estrutura usada durante a análise semântica, contendo
    pilhas, árvore anotada, erros e estado da linha.

    Retorna:
        dict: contexto totalmente inicializado.
    """
    return {
        'erros': [],
        'arvore_anotada': [],
        'pilha_tipos': [],
        'pilha_valores': [],
        'idx_valor': 0,
        'memorias_decl_nesta_linha': set()
    }

def tokens_processaveis_de(tokens_valores: list) -> list:
    """
    Remove parênteses dos tokens e retorna apenas valores úteis.

    Args:
        tokens_valores: lista de tokens brutos.

    Retorna:
        list: tokens sem '(' e ')'.
    """
    return [v for v in tokens_valores if v not in ('(', ')')]

def consumir_literal(ctx: dict, tokens_proc: list, tipo: str, linha: int) -> None:
    """
    Consome um literal numérico (int ou float).

    Atualiza:
        - ctx['idx_valor']
        - ctx['pilha_tipos']
        - ctx['pilha_valores']
        - ctx['arvore_anotada']

    Em caso de falha, registra erro sem lançar exceção.
    """
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
    """
    Processa um identificador, que pode representar:

    1) Atribuição:
        nome pertence ao conjunto de 'atribuicoes'.
        Consome topo da pilha de tipos/valores.

    2) Leitura:
        Busca na tabela. Se inexistente → erro; se não inicializada → erro.

    Após processar:
        empilha tipo e valor resultante e adiciona nó à árvore anotada.

    Retorna:
        tabela_simbolos atualizada.
    """

    # Falha: tokens acabaram
    if ctx['idx_valor'] >= len(tokens_proc):
        ctx['erros'].append(
            f"ERRO SEMÂNTICO [Linha {linha}]: Token inesperado ao processar identificador."
        )
        return tabela_simbolos

    nome = tokens_proc[ctx['idx_valor']]
    ctx['idx_valor'] += 1

    # Token sintático inválido
    if nome in ['(', ')', '+', '-', '*', '/', '%', '^', '|',
                '<', '>', '<=', '>=', '==', '!=', 'IF', 'WHILE', 'RES', 'res']:
        ctx['erros'].append(
            f"ERRO SEMÂNTICO [Linha {linha}]: Token '{nome}' não é identificador válido."
        )
        return tabela_simbolos

    # ------------------------------------------
    # Caso 1: ATRIBUIÇÃO
    # ------------------------------------------
    if nome in atribuicoes:

        # Requer valor no topo da pilha
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

        # Resultado da atribuição volta para pilha
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

    # ------------------------------------------
    # Caso 2: LEITURA
    # ------------------------------------------
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
    """
    Processa uma operação RES, que consulta resultados passados.
    A operação exige 1 parâmetro inteiro na pilha de tipos.

    Funcionamento:
        - Verifica se o token atual é 'RES'
        - Consome o parâmetro da pilha
        - Valida se é inteiro
        - Usa o número para indexar o histórico de resultados
        - Empilha o tipo recuperado

    Parâmetros:
        ctx: dicionário com o estado da análise (pilhas, erros, árvore)
        tokens_processaveis: tokens da linha após filtragem
        historico_resultados: lista com tipos de resultados anteriores
        numero_linha: número da linha original do código
    """

    # Verificação de limites do índice do token
    if ctx['idx_valor'] >= len(tokens_processaveis):
        ctx['erros'].append(
            f"ERRO SEMÂNTICO [Linha {numero_linha}]: Token inesperado (fim da linha)"
        )
        return

    token = tokens_processaveis[ctx['idx_valor']]

    # O comando RES deve aparecer explicitamente
    if token not in ['RES', 'res']:
        ctx['erros'].append(
            f"ERRO SEMÂNTICO [Linha {numero_linha}]: Esperado 'RES', encontrado '{token}'"
        )
        ctx['idx_valor'] += 1
        return

    # Consome o token RES
    ctx['idx_valor'] += 1

    # RES exige um parâmetro na pilha
    if len(ctx['pilha_tipos']) < 1:
        ctx['erros'].append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: RES requer um parâmetro na pilha")
        # Registra nó inconsistente e segue
        ctx['pilha_tipos'].append('desconhecido')
        ctx['pilha_valores'].append(None)
        ctx['arvore_anotada'].append({
            'tipo_no': 'RES',
            'tipo_inferido': 'desconhecido',
            'parametro': None,
            'linha': numero_linha
        })
        return

    # Desempilha o tipo e valor concretos
    tipo_param = ctx['pilha_tipos'].pop()
    n_valor = ctx['pilha_valores'].pop() if ctx['pilha_valores'] else None

    # O parâmetro precisa ser inteiro
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

    # O valor concreto deve ser inteiro
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

    # Índice deve ser não negativo
    if n < 0:
        ctx['erros'].append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: RES requer N >= 0")
        tipo_resultado = 'desconhecido'

    # N não pode ultrapassar histórico
    elif n >= len(historico_resultados):
        ctx['erros'].append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: RES({n}) fora do alcance do histórico")
        tipo_resultado = 'desconhecido'

    else:
        # Consulta resultado anterior
        idx_resultado = len(historico_resultados) - 1 - n
        tipo_resultado = historico_resultados[idx_resultado].get('tipo', 'desconhecido')

    # Resultado final da operação
    ctx['pilha_tipos'].append(tipo_resultado)
    ctx['pilha_valores'].append(None)

    # Adiciona nó na árvore anotada
    ctx['arvore_anotada'].append({
        'tipo_no': 'RES',
        'tipo_inferido': tipo_resultado,
        'parametro': n,
        'linha': numero_linha
    })

def processar_operador_aritmetico(ctx: dict, simbolo: str, regras_semanticas: dict, numero_linha: int) -> None:
    """
    Processa operadores aritméticos de dois operandos.

    Operadores:
        +, -, *, /, %, ^, |

    A validação baseia-se em regras_semanticas['operadores_aritmeticos'].

    Fluxo:
        - Consome token do operador
        - Verifica se há dois operandos na pilha
        - Desempilha operandos
        - Valida tipos conforme regras
        - Reempilha o tipo resultante
    """

    regra = regras_semanticas.get('operadores_aritmeticos', {}).get(simbolo, {'aceita': [], 'aceita_base': []})

    # Consome símbolo do fluxo
    ctx['idx_valor'] += 1

    # Operadores aritméticos exigem 2 operandos
    if len(ctx['pilha_tipos']) < 2:
        ctx['erros'].append(
            f"ERRO SEMÂNTICO [Linha {numero_linha}]: "
            f"Operador '{simbolo}' requer dois operandos (insuficientes)"
        )
        return

    # Desempilha operandos
    tipo2 = ctx['pilha_tipos'].pop()
    tipo1 = ctx['pilha_tipos'].pop()

    # Descarta valores concretos
    if ctx['pilha_valores']:
        ctx['pilha_valores'].pop()
    if ctx['pilha_valores']:
        ctx['pilha_valores'].pop()

    # Tratamento específico para potência
    if simbolo == '^':
        base_valida = tipo1 in regra.get('aceita_base', [])
        exp_valido = tipo2 == 'int'

        if not base_valida:
            ctx['erros'].append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: Base inválida para '^' ({tipo1})")
        if not exp_valido:
            ctx['erros'].append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: Expoente deve ser int (recebido '{tipo2}')")

        tipo_resultado = promoverTipo(tipo1, 'int')

    # Divisão inteira e módulo
    elif simbolo in ['/', '%']:
        if tipo1 != 'int' or tipo2 != 'int':
            ctx['erros'].append(
                f"ERRO SEMÂNTICO [Linha {numero_linha}]: "
                f"Operador '{simbolo}' exige inteiros ({tipo1}, {tipo2})"
            )
        tipo_resultado = 'int'

    # Divisão float customizada '|'
    elif simbolo == '|':
        if tipo1 not in regra['aceita'] or tipo2 not in regra['aceita']:
            ctx['erros'].append(
                f"ERRO SEMÂNTICO [Linha {numero_linha}]: "
                f"Operador '|' exige operandos numéricos"
            )
        tipo_resultado = 'float'

    else:
        # Operadores binários + - *
        if tipo1 not in regra['aceita'] or tipo2 not in regra['aceita']:
            ctx['erros'].append(
                f"ERRO SEMÂNTICO [Linha {numero_linha}]: "
                f"Tipos incompatíveis para '{simbolo}' ({tipo1}, {tipo2})"
            )
        tipo_resultado = promoverTipo(tipo1, tipo2)

    # Empilha resultado
    ctx['pilha_tipos'].append(tipo_resultado)
    ctx['pilha_valores'].append(None)

    # Nó da árvore
    ctx['arvore_anotada'].append({
        'tipo_no': 'OPERACAO',
        'operador': simbolo,
        'tipo_inferido': tipo_resultado,
        'operandos': [tipo1, tipo2],
        'linha': numero_linha
    })

def processar_comparacao(ctx: dict, simbolo: str, regras_semanticas: dict, numero_linha: int) -> None:
    """
    Processa operadores relacionais (<, >, <=, >=, ==, !=).

    Sempre retorna booleano.

    Fluxo:
        - Consome token
        - Verifica dois operandos
        - Desempilha operandos
        - Valida tipos com regras_semanticas
        - Empilha 'booleano'
    """

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

    # descarta valores concretos
    if ctx['pilha_valores']:
        ctx['pilha_valores'].pop()
    if ctx['pilha_valores']:
        ctx['pilha_valores'].pop()

    # Verificação de tipos
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
    """
    Processa estruturas de controle: IF e WHILE.

    Regras:
        IF    - condição (booleano), then, else
        WHILE - condição (booleano), corpo

    Ambos desempilham seus componentes e empilham o tipo do bloco.
    O tipo final de IF é promover(then, else).
    O tipo final de WHILE é o tipo do corpo.
    """

    ctx['idx_valor'] += 1

    # Tratamento da estrutura IF
    if simbolo == 'if':
        if len(ctx['pilha_tipos']) < 3:
            ctx['erros'].append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: IF incompleto")
            return

        tipo_else = ctx['pilha_tipos'].pop()
        tipo_then = ctx['pilha_tipos'].pop()
        tipo_cond = ctx['pilha_tipos'].pop()

        # Descarta valores
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

    # Tratamento da estrutura WHILE
    if simbolo == 'while':
        if len(ctx['pilha_tipos']) < 2:
            ctx['erros'].append(f"ERRO SEMÂNTICO [Linha {numero_linha}]: WHILE incompleto")
            return

        tipo_corpo = ctx['pilha_tipos'].pop()
        tipo_cond = ctx['pilha_tipos'].pop()

        # Descarta valores concretos
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
    """
    Realiza a análise semântica de uma linha inteira.

    Divide o processo em múltiplas funções especializadas:
        - Literais
        - Identificadores
        - Operadores aritméticos
        - Comparações
        - Estruturas de controle
        - RES

    Retorna:
        (tabela_simbolos, erros, arvore_anotada, tipo_final, mems_declaradas)
    """

    # Cria o contexto interno da análise
    ctx = criar_contexto()

    # Identifica identificadores com atribuição
    atribuicoes_nomes = coletar_atribuicoes(tokens_valores)

    # Converte tokens brutos para tokens processáveis
    tokens_processaveis = tokens_processaveis_de(tokens_valores)

    # Para retorno final
    memorias_declaradas_nesta_linha = ctx['memorias_decl_nesta_linha']

    # Suporte opcional para EPS
    eps = globals().get('EPS', None)

    # Caminha por cada produção derivada
    for nao_terminal, producao in derivacao:

        if not producao:
            continue

        # Ignora produções EPS
        if eps is not None and producao == [eps]:
            continue

        # Analisa cada símbolo individualmente
        for simbolo in producao:

            # Ignora tokens sintáticos
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

    # O tipo final é o topo da pilha
    tipo_final = ctx['pilha_tipos'][-1] if ctx['pilha_tipos'] else 'desconhecido'

    memorias_declaradas_nesta_linha = ctx['memorias_decl_nesta_linha']

    return ( tabela_simbolos, ctx['erros'], ctx['arvore_anotada'], tipo_final, memorias_declaradas_nesta_linha)

def analisarSemanticaMemoria(tabela_simbolos: dict, numero_linha: int, memorias_declaradas_nesta_linha: list[str]) -> list[str]:
    """
    Verifica regras semânticas relacionadas ao uso de MEM/identificadores
    declarados ou atribuídos na linha atual.

    Parâmetros
    ----------
    tabela_simbolos : dict
        Tabela contendo informações de todos os identificadores e memórias.
    numero_linha : int
        Linha do código sendo analisada.
    memorias_declaradas_nesta_linha : list[str]
        Lista de tokens identificados como memória ou variáveis referenciadas
        nesta linha específica.

    Retorna
    -------
    list[str]
        Lista de mensagens de erro semântico encontradas.
    """

    erros = []

    # Percorre todos os nomes detectados como possíveis memórias/variáveis
    for nome in memorias_declaradas_nesta_linha:

        # Ignorar operadores e símbolos que não podem ser nomes
        if nome in [
            '(', ')', '+', '-', '*', '/', '%', '^', '|',
            '<', '>', '<=', '>=', '==', '!='
        ]:
            continue

        # Buscar na tabela de símbolos
        info = tabela_simbolos.get(nome)
        if not info:
            # Identificador não declarado — em algumas linguagens seria erro,
            # mas aqui pode ser permitido dependendo da gramática.
            # Mantemos comportamento atual: ignorar.
            continue

        # Se a memória foi declarada/atribuída nesta mesma linha,
        # não geramos erro (regra definida pelo modelo atual).
        if info.get('linha_declaracao') == numero_linha:
            continue

    return erros

def analisarSemanticaControle(arvore_anotada: list[dict], numero_linha: int) -> list[str]:
    """
    Valida regras semânticas de estruturas de controle como IF e WHILE.

    Parâmetros
    ----------
    arvore_anotada : list[dict]
        Lista de nós anotados da análise sintática contendo os tipos inferidos.
    numero_linha : int
        Linha do código sendo analisada.

    Retorna
    -------
    list[str]
        Lista de erros semânticos detectados.
    """

    erros = []

    # Percorre todos os nós produzidos pela análise sintática
    for no in arvore_anotada:

        tipo_no = no.get('tipo_no')
        tipo_cond = no.get('tipo_condicao')

        # Validação de IF
        if tipo_no == 'CONDICIONAL_IF':
            # A condição deve ser obrigatoriamente booleana
            if tipo_cond != 'booleano':
                erros.append(
                    f"ERRO SEMÂNTICO [Linha {numero_linha}]: "
                    "IF com condição não booleana."
                )

        # Validação de WHILE
        elif tipo_no == 'LOOP_WHILE':
            # A condição também deve ser booleano
            if tipo_cond != 'booleano':
                erros.append(
                    f"ERRO SEMÂNTICO [Linha {numero_linha}]: "
                    "WHILE com condição não booleana."
                )

    return erros

def gerarArvoreAtribuida(arvore_anotada: list[dict], tipo_final: str, numero_linha: int) -> dict:
    """
    Gera a árvore final de atributos após a validação semântica.

    Parâmetros
    ----------
    arvore_anotada : list[dict]
        Lista de nós anotados com informações sintáticas e semânticas.
    tipo_final : str
        Tipo inferido da expressão ou comando.
    numero_linha : int
        Linha correspondente à construção analisada.

    Retorna
    -------
    dict
        Estrutura hierárquica representando o nó raiz da árvore atribuída.
    """

    # Cria o nó raiz da árvore com as informações principais
    arvore_atribuida = {
        'tipo_no': 'PROGRAMA',         # Tipo do nó raiz
        'tipo_inferido': tipo_final,   # Tipo deduzido pela análise semântica
        'linha': numero_linha,         # Linha do código original
        'filhos': arvore_anotada       # Nós internos já analisados
    }

    return arvore_atribuida

## FASE 4: TAC, ASSEMBLY E OTIMIZAÇÕES
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
            tac = gerarTAC(arvore_atribuida)

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