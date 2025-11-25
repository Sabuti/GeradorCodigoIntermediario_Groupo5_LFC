# GeradorCodigoIntermediario_Groupo5_LFC  

## Descrição do Projeto
Este projeto foca no desenvolvimento de um programa em Python para praticar todo o conceito de compiladores, desde o analisador léxico até a criação do código de máquina, como aprendido em aula.  
Ele processa e executa expressões em Notação Polonesa Reversa (RPN) e para essa fase do projeto tem 3 arquivos de teste (cálculo de Fatorial até 8, de Fibonacci até 24 números e séries de Taylor para cosseno). Para isso, utilizamos meia precisão (16 bits, IEEE 754) para números de ponto flutuante (float).  
Além disso, o código pega a árvore sintática abstrata, transforma em Three Address Code (TAC), otimiza, e só depois traduz para Assembly.  
Ao rodar o programa, ele cria 7 arquivos mostrando o resultado da conversão do arquivo, mostrando cada parte do processo.  
Utiliza-se o PlatformIO, integrado ao VS Code, para facilitar na criação do .hex e não precisar se aprofundar em ferramentas AVR.

## Objetivo
Conforme dito pelo professor no site dele: "Pesquisar e praticar os conceitos de geração de código intermediário, otimização e geração de código Assembly desenvolvendo um programa em Python."  
Para mais informações, acessar: [site do professor](https://frankalcantara.com/lf/fase4.html)

## Informações dos Autores e da Matéria
**Integrantes do grupo:**

- Ana Maria Midori Rocha Hinoshita - anamariamidori  
- Lucas Antonio Linhares - Sabuti  

**Nome do grupo no Canvas:** RA4_5  
**Professor:** Frank Coelho de Alcantara  
**Disciplina:** Linguagens Formais e Compiladores (LFC)  
**Intituição:** PUC-PR (Câmpus: Curitiba)  
**Ano:** 2025  

## Divisão de Tarefas

**Aluno 1 -** Ana Maria;  
**Aluno 2 -** Ana Maria;  
**Aluno 3 -** Lucas;  
**Aluno 4 -** Lucas;

** Combinado entre os alunos que ajuda com suas funções são permitidas **

## Documentação das Funções Criadas
**IF**  
A contrução do IF foi definida como:

- (Comparação Resultado_seVerdade Resultado_seFalso IF)

Comparação: booleano  
Resultado_seVerdade: int ou float  
Resultado_seFalso: int ou float  

**WHILE**  
A construção do WHILE foi definida como:

- (Comparação Enquanto_Verdade WHILE)

Comparação: booleano  
Enquanto_Verdade: int ou float

## Decisões Tomadas
-- Seguimos a convenção sugeria pelo professor:  
R16-R23: Variáveis temporárias  
R24-R25: Parâmetros e valores de retorno  
R26-R27 (X): Ponteiro de endereço  
R28-R29 (Y): Frame pointer  
R30-R31 (Z): Ponteiro de pilha  

-- Para operações de ponto flutuante, escolhemos fazer operações com inteiros escalados.

-- Para validação no Arduino, foi escolhido a comunicação serial

## Pré-requisitos
1 - Instalar o Visual Studio Code (VS Code)  
2 - Adicionar a extensão do PlatformIO dentro do VS Code  

## Execução do Código
```bash
1 - Clonar este reposítorio para o ambiente do VS Code
2 - Rodar "python src/trabalho.py fatorial.txt" (ou fibonacci.txt, ou taylor.txt)
3 - Acessar os arquivos de relatórios gerados
4 - Dar upload do código em Assembly (.s) via Ctrl+Alt+U*
5 - Após sucesso, abrir o monitor serial apertando no símbolo de tomada na parte inferior da tela

* O PlatformIO vai cuidar de transformar o .s em .o, para linkar o .elf para converter para .hex e enviar para o Arduino