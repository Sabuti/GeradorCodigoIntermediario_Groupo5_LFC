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
    pilha_resultados = [] 
    # Processa a árvore atribuída
    processar_no_tac(arvore_atribuida, tac, pilha_resultados)
    return tac
    
    

def processar_no_tac(no: dict, tac: list, pilha: list) -> dict:
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
            resultado = processar_no_tac(filho, tac, pilha)
        return resultado if resultado else {'temp': None, 'tipo': 'desconhecido', 'kind': 'temp'}
    
    elif tipo_no == 'LITERAL':
        valor = no.get('valor')
        tipo = no.get('tipo_inferido', 'int')
        resultado = {
            'temp': valor,
            'tipo': tipo,
            'kind': 'imm'
        }
        pilha.append(resultado)  #EMPILHA
        return resultado
    
    elif tipo_no == 'LEITURA_VARIAVEL':
        nome = no.get('nome')
        tipo = no.get('tipo_inferido', 'int')
        resultado = {
            'temp': nome,
            'tipo': tipo,
            'kind': 'var'
        }
        pilha.append(resultado)  #EMPILHA
        return resultado
    
    elif tipo_no == 'ATRIBUICAO':
        if not pilha:
            return {'temp': None, 'tipo': 'desconhecido', 'kind': 'temp'}
    
        valor_info = pilha.pop()  #DESEMPILHA
        nome = no.get('nome')
        tipo = no.get('tipo_inferido', 'int')
    
        #GERA TAC DE ATRIBUIÇÃO
        tac.append({
            'op': '=',
            'a': valor_info['temp'],
            'dest': nome,
            'tipo': tipo,
            'tipo_a': valor_info['tipo'],
            'comment': f'assignment to {nome}'
        })
    
        resultado = {
            'temp': nome,
            'tipo': tipo,
            'kind': 'var'
        }
        pilha.append(resultado)  #REEMPILHA RESULTADO
        return resultado
    
    elif tipo_no == 'OPERACAO':
        if len(pilha) < 2:
            return {'temp': None, 'tipo': 'desconhecido', 'kind': 'temp'}
    
        b_info = pilha.pop()  #DESEMPILHA OPERANDOS
        a_info = pilha.pop()
    
        operador = no.get('operador')
        tipo_resultado = no.get('tipo_inferido', 'int')
        temp_resultado = novo_temp()
    
         #USA OS OPERANDOS REAIS
        tac.append({
            'op': operador,
            'a': a_info['temp'],  #OPERANDO A
            'b': b_info['temp'],  #OPERANDO B
            'dest': temp_resultado,
            'tipo': tipo_resultado,
            'tipo_a': a_info['tipo'],
            'tipo_b': b_info['tipo'],
            'comment': f'{operador} operation'
        })
    
        resultado = {
            'temp': temp_resultado,
            'tipo': tipo_resultado,
            'kind': 'temp'
        }
        pilha.append(resultado)  #EMPILHA RESULTADO
        return resultado
    
    elif tipo_no == 'COMPARACAO':
        # Operação relacional
        if len(pilha) < 2:
            return {'temp': None, 'tipo': 'desconhecido', 'kind': 'temp'}
        b_info = pilha.pop()
        a_info = pilha.pop()
        operador = no.get('operador')
        tipo_resultado = no.get('tipo_inferido', 'booleano')
        temp_resultado = novo_temp()
        tac.append({
            'op': operador,
            'a': a_info['temp'],
            'b': b_info['temp'],
            'dest': temp_resultado,
            'tipo': tipo_resultado,
            'tipo_a': a_info['tipo'],
            'tipo_b': b_info['tipo'],
            'comment': f'{operador} comparison'
        })
        resultado = {
            'temp': temp_resultado,
            'tipo': tipo_resultado,
            'kind': 'temp'
        }
        pilha.append(resultado)
        return resultado
    
    elif tipo_no == 'CONDICIONAL_IF':
        # Estrutura condicional IF
        if len(pilha) < 3:
            return {'temp': None, 'tipo': 'desconhecido', 'kind': 'temp'}
        a_info = pilha.pop()  # condição
        b_info = pilha.pop()  # then
        c_info = pilha.pop()  # else
        tipo_resultado = no.get('tipo_inferido', 'desconhecido')
        temp_resultado = novo_temp()
        label_then = novo_label()
        label_else = novo_label()
        label_end = novo_label()
        # GERA TAC PARA IF
        tac.append({
            'op': 'ifFalse',
            'a': a_info['temp'],
            'dest': label_else,
            'tipo': 'booleano',
            'tipo_a': a_info['tipo'],
            'comment': 'if condition'
        })
        # THEN
        tac.append({
            'op': '=',
            'a': b_info['temp'],
            'dest': temp_resultado,
            'tipo': tipo_resultado,
            'tipo_a': b_info['tipo'],
            'comment': 'then branch'
        })
        tac.append({
            'op': 'goto',
            'dest': label_end,
            'comment': 'jump to end'
        })
        # ELSE
        tac.append({
            'op': 'label',
            'dest': label_else
        })
        tac.append({
            'op': '=',
            'a': c_info['temp'],
            'dest': temp_resultado,
            'tipo': tipo_resultado,
            'tipo_a': c_info['tipo'],
            'comment': 'else branch'
        })
        # END
        tac.append({
            'op': 'label',
            'dest': label_end
        })
        resultado = {
            'temp': temp_resultado,
            'tipo': tipo_resultado,
            'kind': 'temp'
        }
        pilha.append(resultado)
        return resultado
        
    
    elif tipo_no == 'LOOP_WHILE':
        # Estrutura de repetição WHILE
        if len(pilha) < 2:
            return {'temp': None, 'tipo': 'desconhecido', 'kind': 'temp'}
        a_info = pilha.pop()  # condição
        b_info = pilha.pop()  # corpo
        tipo_resultado = no.get('tipo_inferido', 'desconhecido')
        temp_resultado = novo_temp()
        label_start = novo_label()
        label_end = novo_label()
        # GERA TAC PARA WHILE
        tac.append({
            'op': 'label',
            'dest': label_start
        })
        tac.append({
            'op': 'ifFalse',
            'a': a_info['temp'],
            'dest': label_end,
            'tipo': 'booleano',
            'tipo_a': a_info['tipo'],
            'comment': 'while condition'
        })
        tac.append({
            'op': '=',
            'a': b_info['temp'],
            'dest': temp_resultado,
            'tipo': tipo_resultado,
            'tipo_a': b_info['tipo'],
            'comment': 'while body'
        })
        tac.append({
            'op': 'goto',
            'dest': label_start,
            'comment': 'jump to start'
        })
        tac.append({
            'op': 'label',
            'dest': label_end
        })
        resultado = {
            'temp': temp_resultado,
            'tipo': tipo_resultado,
            'kind': 'temp'
        }
        pilha.append(resultado)
        return resultado
    
    elif tipo_no == 'RES':
        # Comando especial 
        if len(pilha) < 1:
            return {'temp': None, 'tipo': 'desconhecido', 'kind': 'temp'}
        a_info = pilha.pop()
        tipo_resultado = no.get('tipo_inferido', 'desconhecido')
        temp_resultado = novo_temp()
        tac.append({
            'op': 'res',
            'a': a_info['temp'],
            'dest': temp_resultado,
            'tipo': tipo_resultado,
            'tipo_a': a_info['tipo'],
            'comment': 'RES operation'
        })
        resultado = {
            'temp': temp_resultado,
            'tipo': tipo_resultado,
            'kind': 'temp'
        }
        pilha.append(resultado)
        return resultado
        
    else:
        # Nó desconhecido
        return {'temp': None, 'tipo': 'desconhecido', 'kind': 'temp'}


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
                    not val.startswith('t') and
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
; Operações IEEE 754 half-precision (stubs - implementação simplificada)

ieee754_add:
    ; TODO: Implementar adição IEEE 754 completa
    ; Por ora, retorna primeiro operando
    movw r20, r22
    ret

ieee754_sub:
    ; TODO: Implementar subtração IEEE 754
    movw r20, r22
    ret

ieee754_mul:
    ; TODO: Implementar multiplicação IEEE 754
    movw r20, r22
    ret

ieee754_div:
    ; TODO: Implementar divisão IEEE 754
    movw r20, r22
    ret

ieee754_pow:
    ; TODO: Implementar potência IEEE 754
    movw r20, r22
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
    """Traduz operação com suporte a IEEE 754 half-precision"""
    A = inst.get("a")
    B = inst.get("b")
    D = inst.get("dest")
    op = inst.get("op")
    tipo = inst.get("tipo", "int")
    tipo_a = inst.get("tipo_a", "int")
    tipo_b = inst.get("tipo_b", "int")

    codigo = f"\n; TAC: {D} = {A} {op} {B} (tipo: {tipo})\n"
    
    # Carrega operandos
    codigo += load_operand(A, "r23", "r22")  # A em r22:r23 (LO:HI)
    codigo += load_operand(B, "r25", "r24")  # B em r24:r25
    
    # Converte int para IEEE 754 se necessário
    if tipo == 'float' and tipo_a == 'int':
        codigo += "    rcall int_to_ieee754  ; converte A para IEEE 754\n"
        codigo += "    movw r22, r20\n"
    
    if tipo == 'float' and tipo_b == 'int':
        codigo += "    movw r22, r24  ; salva A\n"
        codigo += "    rcall int_to_ieee754  ; converte B\n"
        codigo += "    movw r24, r20\n"
        codigo += "    movw r20, r22  ; restaura A\n"
    
    if op == "+":
        if tipo == 'float':
            codigo += "    rcall ieee754_add\n"
        else:
            codigo += "    add r23, r25\n    adc r22, r24\n    movw r20, r22\n"
        
    elif op == "-":
        if tipo == 'float':
            codigo += "    rcall ieee754_sub\n"
        else:
            codigo += "    sub r23, r25\n    sbc r22, r24\n    movw r20, r22\n"
        
    elif op == "*":
        if tipo == 'float':
            codigo += "    rcall ieee754_mul\n"
        else:
            codigo += gerar_mul16()
            
    elif op == "/":
        if tipo == 'int':
            codigo += gerar_div16()
        else:
            codigo += "    rcall ieee754_div\n"
            
    elif op == "|":
        # Divisão float
        codigo += "    rcall ieee754_div\n"
        
    elif op == "^":
        if tipo == 'float':
            codigo += "    rcall ieee754_pow\n"
        else:
            codigo += gerar_pow16()
    
    elif op == "int_to_ieee":
        codigo += "    rcall int_to_ieee754\n"
    
    # Salva resultado
    codigo += f"    sts {D}, r20\n    sts {D}+1, r21\n"
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
        codigo += f"    ldi r20, {lo}\n"
        codigo += f"    ldi r21, {hi}\n"
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
    
    # Carrega a condição
    if isinstance(cond, int):
        lo = cond & 0xFF
        hi = (cond >> 8) & 0xFF
        codigo += f"    ldi r16, {lo}\n"
        codigo += f"    ldi r17, {hi}\n"
    else:
        codigo += f"    lds r16, {cond}\n"
        codigo += f"    lds r17, {cond}+1\n"
    
    # Testa se é zero (falso)
    codigo += f"    or r16, r17\n"      # OR dos dois bytes
    codigo += f"    breq {destino}\n"   # Se zero, pula
    
    return codigo

def traduzirComparacao(inst):
    """Gera código para comparação entre valores"""
    A = inst.get("a")
    B = inst.get("b")
    D = inst.get("dest")
    op = inst.get("op")
    
    codigo = f"\n; {D} = {A} {op} {B}\n"
    
    # Carrega A em r22:r23
    if isinstance(A, int):
        codigo += f"    ldi r22, {A & 0xFF}\n"
        codigo += f"    ldi r23, {(A >> 8) & 0xFF}\n"
    else:
        codigo += f"    lds r22, {A}\n"
        codigo += f"    lds r23, {A}+1\n"
    
    # Carrega B em r24:r25
    if isinstance(B, int):
        codigo += f"    ldi r24, {B & 0xFF}\n"
        codigo += f"    ldi r25, {(B >> 8) & 0xFF}\n"
    else:
        codigo += f"    lds r24, {B}\n"
        codigo += f"    lds r25, {B}+1\n"
    
    # Realiza comparação
    codigo += f"    cp r22, r24\n"      # Compara low bytes
    codigo += f"    cpc r23, r25\n"     # Compara high bytes com carry
    
    # Define resultado baseado no operador
    if op == "<":
        # Se A < B, carry será setado
        codigo += "    ldi r20, 0\n"
        codigo += "    ldi r21, 0\n"
        codigo += "    brlo cmp_true\n"  # Branch if lower (unsigned)
        codigo += "    rjmp cmp_end\n"
        codigo += "cmp_true:\n"
        codigo += "    ldi r20, 1\n"
        codigo += "cmp_end:\n"
    
    elif op == "<=":
        codigo += "    ldi r20, 0\n"
        codigo += "    ldi r21, 0\n"
        codigo += "    brlo cmp_true\n"
        codigo += "    breq cmp_true\n"
        codigo += "    rjmp cmp_end\n"
        codigo += "cmp_true:\n"
        codigo += "    ldi r20, 1\n"
        codigo += "cmp_end:\n"
    
    elif op == ">":
        codigo += "    ldi r20, 0\n"
        codigo += "    ldi r21, 0\n"
        codigo += "    brsh cmp_false\n"  # Branch if same or higher
        codigo += "    ldi r20, 1\n"
        codigo += "cmp_false:\n"
    
    elif op == ">=":
        codigo += "    ldi r20, 0\n"
        codigo += "    ldi r21, 0\n"
        codigo += "    brlo cmp_end\n"
        codigo += "    ldi r20, 1\n"
        codigo += "cmp_end:\n"
    
    elif op == "==":
        codigo += "    ldi r20, 0\n"
        codigo += "    ldi r21, 0\n"
        codigo += "    brne cmp_end\n"
        codigo += "    ldi r20, 1\n"
        codigo += "cmp_end:\n"
    
    elif op == "!=":
        codigo += "    ldi r20, 0\n"
        codigo += "    ldi r21, 0\n"
        codigo += "    breq cmp_end\n"
        codigo += "    ldi r20, 1\n"
        codigo += "cmp_end:\n"
    
    # Salva resultado
    codigo += f"    sts {D}, r20\n"
    codigo += f"    sts {D}+1, r21\n"
    
    return codigo

def traduzirPrint(inst):
    """Imprime valor com formatação correta"""
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
        codigo += "    rcall UART_printIEEE754\n"
    else:
        codigo += "    rcall UART_printHex16\n"
    
    # Adiciona newline SEMPRE
    codigo += "    ldi r24, 0x0D\n    rcall UART_sendByte\n"  # CR
    codigo += "    ldi r24, 0x0A\n    rcall UART_sendByte\n"  # LF
    
    return codigo

# -------------------------
# Geração de Código Assembly completo
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

    variaveis = mapear_variaveis(tacOtimizado, tabela_simbolos)
    assembly.append(gerar_secao_dados(variaveis))

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
        print("V Gramática LL(1) construída com sucesso.")
    except Exception as e:
        print(f"X Erro ao construir a gramática: {e}")
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
            
            print(f"  V Léxico: {len(tokens)} tokens")

            # Fase 2: Análise Sintática
            derivacao = analisadorSintatico(tokens, tabelaLL1)
            
            todas_derivacoes.append({
                'linha': numero_linha,
                'derivacao': derivacao
            })
            
            print(f"  V Sintático: {len(derivacao)} produções")

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
                print(f"  X Semântico: {len(erros)} erro(s)")
                for e in erros:
                    todos_erros.append(e)
            else:
                print(f"  V Semântico: OK (tipo: {tipo_final})")

            # Fase 4: Geração de TAC
            resetar_contadores_tac()
            tac_linha = gerarTAC(arvore_atribuida)
            tac_completo.extend(tac_linha)
            print(f"  V TAC: {len(tac_linha)} instruções")

        except ValueError as e:
            msg = str(e)
            todos_erros.append(msg)
            print(f"  X {msg}")

    # ========================================
    # GERAÇÃO DE RELATÓRIOS E ARQUIVOS
    # ========================================
    
    print("\n" + "="*60)
    print("GERANDO RELATÓRIOS")
    print("="*60)
    
    # 1. Relatório Léxico
    gerar_relatorio_lexico(todos_tokens, f'{nome_base}_tokens.txt')
    print(f"V Relatório léxico: {nome_base}_tokens.txt")
    
    # 2. Relatório Sintático
    gerar_relatorio_sintatico(todas_derivacoes, f'{nome_base}_derivacoes.txt')
    print(f"V Relatório sintático: {nome_base}_derivacoes.txt")
    
    # 3. Relatório Semântico (Árvore Atribuída)
    gerar_relatorio_semantico(todas_arvores, tabela_simbolos, f'{nome_base}_arvore.txt')
    print(f"V Relatório semântico: {nome_base}_arvore.txt")
    
    # 4. TAC Original
    salvar_tac(tac_completo, f'{nome_base}_tac.txt')
    print(f"V TAC original: {nome_base}_tac.txt")

    # 5. Otimização de TAC
    tac_otimizado = otimizarTAC(tac_completo)
    salvar_tac_otimizado(tac_otimizado, f'{nome_base}_tac_otimizado.txt')
    print(f"V TAC otimizado: {nome_base}_tac_otimizado.txt")
    
    # 6. Relatório de Otimizações
    gerar_relatorio_otimizacoes(tac_completo, tac_otimizado, f'{nome_base}_otimizacoes.md')
    print(f"V Relatório otimizações: {nome_base}_otimizacoes.md")
    
    # 7. Tabela de Símbolos
    gerar_relatorio_tabela_simbolos(tabela_simbolos, f'{nome_base}_simbolos.txt')
    print(f"V Tabela de símbolos: {nome_base}_simbolos.txt")

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
        print("\nXXX Compilação concluída COM ERROS")
        return 1
    else:
        print("\nV Compilação concluída COM SUCESSO")
        print("Todos os relatórios foram gerados.")
        return 0

if __name__ == "__main__":
    main()