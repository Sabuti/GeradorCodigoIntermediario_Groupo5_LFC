# Relatório de Otimizações

## Estatísticas Gerais

- **Instruções TAC original**: 8
- **Instruções TAC otimizado**: 6
- **Instruções removidas**: 2 (25.0%)

- **Temporários no TAC original**: 3
- **Temporários no TAC otimizado**: 1
- **Temporários eliminados**: 2

## Técnicas de Otimização Implementadas

### 1. Constant Folding
Avalia expressões constantes em tempo de compilação.

**Exemplo:**
```
Antes:  t1 = 2 + 3
Depois: t1 = 5
```

### 2. Constant Propagation
Propaga valores constantes através do código.

**Exemplo:**
```
Antes:  t1 = 5
        t2 = t1 + 3
Depois: t1 = 5
        t2 = 5 + 3  →  t2 = 8
```

### 3. Dead Code Elimination
Remove código que não afeta o resultado do programa.

**Exemplo:**
```
Antes:  t1 = 5
        t2 = 3      ; t2 nunca é usado
        t3 = t1 + 2
Depois: t1 = 5
        t3 = t1 + 2
```

### 4. Eliminação de Saltos Redundantes
Remove saltos desnecessários e labels não utilizados.

**Exemplo:**
```
Antes:  goto L1
        L1:
Depois: L1:
```

## Comparação TAC Original vs Otimizado

### TAC Original
```
  t1 = I <= 5
  t2 = FATORIAL * I
L1:
  t3 = I <= 5
  ifFalse t3 goto L2
  goto L1
L2:
  {'op': 'print', 'a': 'FATORIAL', 'tipo': 'int', 'tipo_a': 'int', 'comment': 'print resultado final: FATORIAL'}
```

### TAC Otimizado
```
L1:
  t3 = I <= 5
  ifFalse t3 goto L2
  goto L1
L2:
  {'op': 'print', 'a': 'FATORIAL', 'tipo': 'int', 'tipo_a': 'int', 'comment': 'print resultado final: FATORIAL'}
```

