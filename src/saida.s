.equ RAMEND, 0x08FF
.equ SPL, 0x3D
.equ SPH, 0x3E
.equ TXEN0, 0x03
.equ UBRR0H, 0xC5
.equ UBRR0L, 0xC4
.equ UCSR0A, 0xC0
.equ UCSR0B, 0xC1
.equ UCSR0C, 0xC2
.equ UCSZ00, 0x01
.equ UCSZ01, 0x02
.equ UDR0, 0xC6


.data
TTRES: .word 0  ; variável TTRES
XVAL: .word 0  ; variável XVAL
XDOIS: .word 0  ; variável XDOIS
XQUATRO: .word 0  ; variável XQUATRO
XSEIS: .word 0  ; variável XSEIS
COS: .word 0  ; variável COS
TUM: .word 0  ; variável TUM
TDOIS: .word 0  ; variável TDOIS

; === SEÇÃO DE CÓDIGO ===
.text

.global main

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



main:
    ; inicializa pilha
    ldi r16, hi8(RAMEND)
    out SPH, r16
    ldi r16, lo8(RAMEND)
    out SPL, r16

    rcall UART_init


    ; Teste inicial UART

    ldi r24, 'O'

    rcall UART_sendByte

    ldi r24, 'K'

    rcall UART_sendByte

    ldi r24, 0x0D

    rcall UART_sendByte

    ldi r24, 0x0A

    rcall UART_sendByte



; PRINT TTRES (tipo: int)
    lds r24, TTRES
    lds r25, TTRES+1
    rcall UART_printHex16
    ldi r24, 0x0D
    rcall UART_sendByte
    ldi r24, 0x0A
    rcall UART_sendByte


; Fim do programa
fim:
    rjmp fim  ; Loop infinito
