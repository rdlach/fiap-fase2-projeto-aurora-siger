"""MGPEB - Modulo de Gerenciamento de Pouso e Estabilizacao de Base."""

import random

# Este arquivo continua a historia da Fase 1.
# Antes a Aurora Siger decidia se podia decolar; agora ela ja esta em Marte
# e precisa organizar a chegada dos modulos que formam a base inicial.

# Variaveis principais da simulacao
# Por isso, as configuracoes gerais, os limites e as colecoes principais aparecem
# logo no comeco do arquivo.
nomeSistema = "AURORA SIGER - MGPEB"
versaoSistema = "V3"
opcaoMenu = "-1"
opcaoModo = "-1"
modoDados = "BASE"
respManual = ""
filaProcessadaCheck = False
condAtm = "ESTAVEL"
areaPouso = "LIVRE"
ventoMs = 12
visibKm = 8
semPoeiraCheck = True

limCombMin = 35
limVentoMax = 18
limVisibMin = 4
limMassaMax = 12000

# A funcao da descida usa um modelo quadratico simples.
# Ela nao tenta simular Marte com precisao real; serve para mostrar como uma
# funcao matematica pode apoiar uma decisao de engenharia no MGPEB.
altInicialM = 1200
tempoDescidaS = 80
coefDescida = altInicialM / (tempoDescidaS * tempoDescidaS)
altRetroM = 550

# Estruturas lineares usadas na simulacao.
# filaPouso funciona como fila FIFO: o primeiro modulo da fila e processado antes.
# modsPousados, modsEspera e modsAlerta sao listas auxiliares de classificacao.
# pilhaAlertas funciona como pilha LIFO: o ultimo alerta registrado sai primeiro.
filaPouso = []
modsPousados = []
modsEspera = []
modsAlerta = []
pilhaAlertas = []

# Cada modulo foi descrito como um dicionario para deixar os atributos visiveis.
# A prioridade menor representa maior urgencia de pouso.
modHab = {
    "id": "M01",
    "nome": "Habitat Orion",
    "tipo": "HAB",
    "prio": 1,
    "comb": 62,
    "massa": 9200,
    "crit": 5,
    "horaOrb": "08:10",
    "carga": "HABITACAO",
    "sens": "FUNCIONAIS",
    "status": "CADASTRADO",
}

modEnergia = {
    "id": "M02",
    "nome": "Gerador Helios",
    "tipo": "ENE",
    "prio": 1,
    "comb": 54,
    "massa": 8700,
    "crit": 5,
    "horaOrb": "08:18",
    "carga": "ENERGIA",
    "sens": "FUNCIONAIS",
    "status": "CADASTRADO",
}

modLab = {
    "id": "M03",
    "nome": "Lab Ares",
    "tipo": "LAB",
    "prio": 3,
    "comb": 33,
    "massa": 7600,
    "crit": 3,
    "horaOrb": "08:24",
    "carga": "CIENCIA",
    "sens": "FUNCIONAIS",
    "status": "CADASTRADO",
}

modLog = {
    "id": "M04",
    "nome": "Carga Atlas",
    "tipo": "LOG",
    "prio": 4,
    "comb": 28,
    "massa": 10800,
    "crit": 2,
    "horaOrb": "08:32",
    "carga": "LOGISTICA",
    "sens": "FUNCIONAIS",
    "status": "CADASTRADO",
}

modMed = {
    "id": "M05",
    "nome": "Suporte Vita",
    "tipo": "MED",
    "prio": 2,
    "comb": 47,
    "massa": 6900,
    "crit": 4,
    "horaOrb": "08:40",
    "carga": "MEDICA",
    "sens": "FALHA PARCIAL",
    "status": "CADASTRADO",
}

todosMods = [modHab, modEnergia, modLab, modLog, modMed]


def mostrarTitulo(titulo):
    # Padroniza os blocos de saida no terminal.
    print("\n" + "=" * 68)
    print(titulo)
    print("=" * 68)


def mostrarLinha():
    # Separador visual simples para nao misturar trechos da simulacao.
    print("-" * 68)


def lerInt(msg, menor, maior):
    # Entrada numerica com repeticao ate o usuario digitar algo aceitavel.
    while True:
        try:
            valor = int(input(msg))

            if menor <= valor <= maior:
                return valor

            print(f"Digite um valor entre {menor} e {maior}.")
        except ValueError:
            print("Entrada invalida. Digite um numero inteiro.")


def lerTexto(msg):
    # Entrada de texto padronizada para comparacoes simples.
    texto = input(msg).strip().upper()
    return texto


def clonarMod(mod):
    # Criamos copias dos modulos para preservar o cadastro original.
    # Assim, a fila pode mudar status sem estragar os dados base do projeto.
    return {
        "id": mod["id"],
        "nome": mod["nome"],
        "tipo": mod["tipo"],
        "prio": mod["prio"],
        "comb": mod["comb"],
        "massa": mod["massa"],
        "crit": mod["crit"],
        "horaOrb": mod["horaOrb"],
        "carga": mod["carga"],
        "sens": mod["sens"],
        "status": mod["status"],
    }


def ajustarMod(mod, prio, comb, massa, crit, sens):
    # Ajusta apenas os campos que variam entre modo base, manual e randomico.
    mod["prio"] = prio
    mod["comb"] = comb
    mod["massa"] = massa
    mod["crit"] = crit
    mod["sens"] = sens
    mod["status"] = "CADASTRADO"


def aplicarModoBase():
    global modoDados, condAtm, areaPouso, ventoMs, visibKm, semPoeiraCheck

    # Volta para o cenario fixo da entrega, bom para demonstrar sem depender de sorte.
    modoDados = "BASE"
    condAtm = "ESTAVEL"
    areaPouso = "LIVRE"
    ventoMs = 12
    visibKm = 8
    semPoeiraCheck = True

    ajustarMod(modHab, 1, 62, 9200, 5, "FUNCIONAIS")
    ajustarMod(modEnergia, 1, 54, 8700, 5, "FUNCIONAIS")
    ajustarMod(modLab, 3, 33, 7600, 3, "FUNCIONAIS")
    ajustarMod(modLog, 4, 28, 10800, 2, "FUNCIONAIS")
    ajustarMod(modMed, 2, 47, 6900, 4, "FALHA PARCIAL")


def aplicarModoRandomico():
    global modoDados, condAtm, areaPouso, ventoMs, visibKm, semPoeiraCheck

    # Gera um cenario novo para testar se a logica reage a entradas diferentes.
    modoDados = "RANDOMICO"
    condAtm = random.choice(["ESTAVEL", "ESTAVEL", "INSTAVEL"])
    areaPouso = random.choice(["LIVRE", "LIVRE", "OCUPADA"])
    ventoMs = random.randint(6, 26)
    visibKm = random.randint(2, 10)
    semPoeiraCheck = random.choice([True, True, False])

    for mod in todosMods:
        mod["prio"] = random.randint(1, 5)
        mod["comb"] = random.randint(20, 75)
        mod["massa"] = random.randint(6200, 12600)
        mod["crit"] = random.randint(1, 5)
        mod["sens"] = random.choice(["FUNCIONAIS", "FUNCIONAIS", "FALHA PARCIAL"])
        mod["status"] = "CADASTRADO"


def aplicarModoManual():
    global modoDados, respManual, condAtm, areaPouso, ventoMs, visibKm, semPoeiraCheck

    # Aqui o grupo pode forcar cenarios e observar se o pouso passa ou trava.
    modoDados = "MANUAL"
    mostrarTitulo("MODO MANUAL DE DADOS")

    condAtm = lerTexto("Condicao atmosferica ESTAVEL ou INSTAVEL: ")
    if condAtm != "ESTAVEL":
        condAtm = "INSTAVEL"

    areaPouso = lerTexto("Area de pouso LIVRE ou OCUPADA: ")
    if areaPouso != "LIVRE":
        areaPouso = "OCUPADA"

    ventoMs = lerInt("Vento em m/s de 0 a 80: ", 0, 80)
    visibKm = lerInt("Visibilidade em km de 0 a 50: ", 0, 50)
    respManual = lerTexto("Sem tempestade de poeira? S ou N: ")
    semPoeiraCheck = respManual == "S"

    for mod in todosMods:
        mostrarTitulo(f"DADOS DO MODULO {mod['id']} - {mod['nome']}")
        mod["prio"] = lerInt("Prioridade de pouso 1 a 5: ", 1, 5)
        mod["crit"] = lerInt("Criticidade da carga 1 a 5: ", 1, 5)
        mod["comb"] = lerInt("Combustivel percentual 0 a 100: ", 0, 100)
        mod["massa"] = lerInt("Massa em kg 1000 a 20000: ", 1000, 20000)

        respManual = lerTexto("Sensores FUNCIONAIS? S ou N: ")
        if respManual == "S":
            mod["sens"] = "FUNCIONAIS"
        else:
            mod["sens"] = "FALHA PARCIAL"

        mod["status"] = "CADASTRADO"


def mostrarAmbiente():
    # Mostra o cenario que esta alimentando a regra booleana.
    mostrarTitulo("DADOS DO CENARIO")
    print(f"Modo de dados: {modoDados}")
    print(f"Condicao atmosferica: {condAtm}")
    print(f"Area de pouso: {areaPouso}")
    print(f"Vento: {ventoMs} m/s")
    print(f"Visibilidade: {visibKm} km")

    if semPoeiraCheck:
        print("Poeira: sem tempestade ativa")
    else:
        print("Poeira: tempestade ativa")


def escolherModoDados():
    global opcaoModo

    # O usuario escolhe se quer um cenario fixo, sorteado ou preenchido na mao.
    mostrarTitulo("ESCOLHA DO MODO DE DADOS")
    print("1 - Modo base da entrega")
    print("2 - Modo randomico")
    print("3 - Modo manual")
    opcaoModo = input("Modo escolhido: ").strip()

    if opcaoModo == "1":
        aplicarModoBase()
    elif opcaoModo == "2":
        aplicarModoRandomico()
    elif opcaoModo == "3":
        aplicarModoManual()
    else:
        print("Modo invalido. Mantendo o modo base.")
        aplicarModoBase()

    prepararFilaOrdenada()
    mostrarAmbiente()
    mostrarLista("FILA DE POUSO ORDENADA", filaPouso)


def carregarFila():
    global filaProcessadaCheck

    # Reinicia a simulacao e coloca todos os modulos na fila principal.
    # Isso permite rodar o programa de novo sem carregar sujeira da execucao anterior.
    filaPouso.clear()
    modsPousados.clear()
    modsEspera.clear()
    modsAlerta.clear()
    pilhaAlertas.clear()

    for mod in todosMods:
        novoMod = clonarMod(mod)
        novoMod["status"] = "EM FILA"
        filaPouso.append(novoMod)

    filaProcessadaCheck = False


def prepararFilaOrdenada():
    # Junta duas etapas que sempre caminham juntas na demonstracao:
    # carregar a fila e aplicar a ordenacao por prioridade.
    carregarFila()
    filaOrd = ordenarFilaPorPrio(filaPouso)
    filaPouso.clear()

    for mod in filaOrd:
        filaPouso.append(mod)


def mostrarModulo(mod):
    # Mostra um modulo em uma linha compacta, como um registro operacional.
    print(
        f"{mod['id']} | {mod['nome']} | tipo {mod['tipo']} | "
        f"prio {mod['prio']} | comb {mod['comb']}% | "
        f"massa {mod['massa']} kg | crit {mod['crit']} | "
        f"orb {mod['horaOrb']} | {mod['status']}"
    )


def mostrarLista(titulo, listaMods):
    # Exibe qualquer lista de modulos com o mesmo formato.
    mostrarTitulo(titulo)

    if len(listaMods) == 0:
        print("Nenhum modulo nesta lista.")
        return

    for mod in listaMods:
        mostrarModulo(mod)


def vemDepois(modA, modB):
    # Define a regra de comparacao usada na ordenacao da fila.
    # Primeiro vem a prioridade, depois a criticidade e, por fim, o combustivel.
    if modA["prio"] > modB["prio"]:
        return True

    if modA["prio"] == modB["prio"] and modA["crit"] < modB["crit"]:
        return True

    if (
        modA["prio"] == modB["prio"]
        and modA["crit"] == modB["crit"]
        and modA["comb"] > modB["comb"]
    ):
        return True

    return False


def ordenarFilaPorPrio(listaMods):
    # Insertion sort foi escolhido por ser simples, didatico e adequado
    # para uma fila pequena como a desta simulacao.
    listaOrd = []

    for mod in listaMods:
        listaOrd.append(clonarMod(mod))

    for pos in range(1, len(listaOrd)):
        modChave = listaOrd[pos]
        posAnt = pos - 1

        # Enquanto o item anterior deve vir depois, abrimos espaco para a chave.
        while posAnt >= 0 and vemDepois(listaOrd[posAnt], modChave):
            listaOrd[posAnt + 1] = listaOrd[posAnt]
            posAnt = posAnt - 1

        listaOrd[posAnt + 1] = modChave

    return listaOrd


def buscarMenorComb(listaMods):
    # Busca linear: percorre tudo porque a lista nao precisa estar ordenada.
    if len(listaMods) == 0:
        return None

    menorMod = listaMods[0]

    for mod in listaMods:
        if mod["comb"] < menorMod["comb"]:
            menorMod = mod

    return menorMod


def buscarMaiorPrio(listaMods):
    # Como prioridade 1 e mais urgente que prioridade 4, o menor numero vence.
    # Em empate, a carga mais critica fica na frente.
    if len(listaMods) == 0:
        return None

    maiorPrioMod = listaMods[0]

    for mod in listaMods:
        if mod["prio"] < maiorPrioMod["prio"]:
            maiorPrioMod = mod
        elif mod["prio"] == maiorPrioMod["prio"] and mod["crit"] > maiorPrioMod["crit"]:
            maiorPrioMod = mod

    return maiorPrioMod


def buscarPorTipo(listaMods, tipoBusca):
    # Busca todos os modulos de um tipo especifico, nao apenas o primeiro.
    achados = []

    for mod in listaMods:
        if mod["tipo"] == tipoBusca:
            achados.append(mod)

    return achados


def calcularChecks(mod):
    # Cada check vira uma entrada booleana para a regra de autorizacao.
    # Essa parte conversa diretamente com o diagrama de portas logicas do relatorio.
    combCheck = mod["comb"] >= limCombMin
    atmCheck = (
        condAtm == "ESTAVEL"
        and ventoMs <= limVentoMax
        and visibKm >= limVisibMin
        and semPoeiraCheck
    )
    areaCheck = areaPouso == "LIVRE"
    sensCheck = mod["sens"] == "FUNCIONAIS"
    massaCheck = mod["massa"] <= limMassaMax

    return {
        "combCheck": combCheck,
        "atmCheck": atmCheck,
        "areaCheck": areaCheck,
        "sensCheck": sensCheck,
        "massaCheck": massaCheck,
    }


def avaliarPouso(mod):
    # AUTORIZAR = combCheck AND atmCheck AND areaCheck AND sensCheck AND massaCheck.
    # Em outras palavras: uma unica condicao falsa ja segura o pouso.
    checks = calcularChecks(mod)
    autPouso = (
        checks["combCheck"]
        and checks["atmCheck"]
        and checks["areaCheck"]
        and checks["sensCheck"]
        and checks["massaCheck"]
    )

    falhaCritica = (not checks["combCheck"] and mod["comb"] < 30) or not checks["sensCheck"]

    # O if, elif e else deixam a decisao parecida com a funcao booleana modelada.
    if autPouso:
        return "AUTORIZADO", "Todas as condicoes de pouso foram atendidas.", checks
    elif falhaCritica:
        return "ALERTA", "Modulo exige revisao antes de nova tentativa de pouso.", checks
    else:
        return "ESPERA", "Pouso adiado ate normalizacao das condicoes.", checks


def registrarAlerta(mod, motivo):
    # A pilha guarda alertas para revisao operacional.
    # O ultimo problema detectado fica no topo, simulando uma triagem imediata.
    alerta = {
        "id": mod["id"],
        "nome": mod["nome"],
        "motivo": motivo,
        "comb": mod["comb"],
        "horaOrb": mod["horaOrb"],
    }
    pilhaAlertas.append(alerta)


def processarFila():
    global filaProcessadaCheck

    # Esta e a rotina central do MGPEB.
    # A cada volta, um modulo sai da frente da fila e recebe uma decisao.
    mostrarTitulo("PROCESSAMENTO DA FILA DE POUSO")

    if filaProcessadaCheck:
        print("A fila ja foi processada. Recarregue a fila antes de rodar de novo.")
        return

    if len(filaPouso) == 0:
        print("Fila vazia. Carregue e ordene a fila antes do processamento.")
        return

    while len(filaPouso) > 0:
        # pop(0) simula o dequeue da fila: sai quem estava na frente.
        modAtual = filaPouso.pop(0)
        status, motivo, checks = avaliarPouso(modAtual)
        modAtual["status"] = status

        print(f"\nAnalisando {modAtual['id']} - {modAtual['nome']}")
        print(
            "checks:",
            f"comb={checks['combCheck']}",
            f"atm={checks['atmCheck']}",
            f"area={checks['areaCheck']}",
            f"sens={checks['sensCheck']}",
            f"massa={checks['massaCheck']}",
        )

        # Cada resultado leva o modulo para uma lista auxiliar diferente.
        if status == "AUTORIZADO":
            modAtual["status"] = "POUSADO"
            modsPousados.append(modAtual)
            print("Decisao: POUSO AUTORIZADO")
        elif status == "ALERTA":
            modsAlerta.append(modAtual)
            registrarAlerta(modAtual, motivo)
            print("Decisao: ALERTA OPERACIONAL")
        else:
            modsEspera.append(modAtual)
            print("Decisao: MODULO EM ESPERA")

        print(f"Motivo: {motivo}")

    filaProcessadaCheck = True


def mostrarBuscas():
    # Demonstra os algoritmos de busca pedidos pela atividade.
    mostrarTitulo("BUSCAS LINEARES")
    menorComb = buscarMenorComb(todosMods)
    maiorPrio = buscarMaiorPrio(todosMods)
    modsEnergia = buscarPorTipo(todosMods, "ENE")

    if menorComb is not None:
        print("Modulo com menor combustivel:")
        mostrarModulo(menorComb)

    if maiorPrio is not None:
        print("\nModulo com maior prioridade:")
        mostrarModulo(maiorPrio)

    print("\nBusca por tipo ENE:")
    for mod in modsEnergia:
        mostrarModulo(mod)


def mostrarPilhaAlertas():
    # Mostra a pilha sem destruir a pilha real da simulacao.
    mostrarTitulo("PILHA DE ALERTAS")

    if len(pilhaAlertas) == 0:
        print("Nenhum alerta empilhado.")
        return

    print("Topo da pilha aparece primeiro na retirada simulada.")
    pilhaTemp = []

    # Copia simples para retirar itens da pilha temporaria sem perder o historico.
    for alerta in pilhaAlertas:
        pilhaTemp.append(alerta)

    while len(pilhaTemp) > 0:
        alerta = pilhaTemp.pop()
        print(f"{alerta['id']} | {alerta['nome']} | {alerta['motivo']}")


def alturaDescida(tempoS):
    # Modelo: h(t) = h0 - a.t².
    # Quando o valor passa de zero, travamos em zero para representar contato.
    alturaM = altInicialM - coefDescida * (tempoS * tempoS)

    if alturaM < 0:
        return 0

    return alturaM


def mostrarModeloDescida():
    # Apresenta a funcao matematica em formato que possa ir para o relatorio.
    mostrarTitulo("MODELO MATEMATICO DA DESCIDA")
    print(f"h(t) = {altInicialM} - {coefDescida:.4f} * t^2")
    print("t representa o tempo em segundos e h(t) representa a altura em metros.")
    print("A funcao quadratica simula a reducao de altura durante a aproximacao.")
    mostrarLinha()

    for tempoS in range(0, tempoDescidaS + 1, 20):
        alturaM = alturaDescida(tempoS)
        print(f"t={tempoS:02d}s -> h={alturaM:.2f} m")

    # O primeiro instante abaixo do limite vira sugestao de acionamento.
    for tempoS in range(0, tempoDescidaS + 1):
        if alturaDescida(tempoS) <= altRetroM:
            print(f"\nRetropropulsores sugeridos a partir de t={tempoS}s.")
            print(f"Altura aproximada neste instante: {alturaDescida(tempoS):.2f} m.")
            break


def mostrarRegrasLogicas():
    # Texto curto para ligar o codigo ao diagrama de portas logicas.
    mostrarTitulo("REGRAS LOGICAS DO MGPEB")
    print("A = combCheck")
    print("B = atmCheck")
    print("C = areaCheck")
    print("D = sensCheck")
    print("E = massaCheck")
    print("K = combustivel abaixo de 30%")
    print("\nAUTORIZAR = A . B . C . D . E")
    print("ALERTA = (NOT A . K) + NOT D")
    print("ESPERA = NOT (AUTORIZAR + ALERTA)")
    print("\nLeitura: o pouso so e autorizado quando todas as entradas sao verdadeiras.")
    print("Alerta: combustivel critico ou sensores com falha. Espera: qualquer outra falha.")


def mostrarResumoFinal():
    # Fecha a simulacao separando o que pousou, o que aguardou e o que virou alerta.
    mostrarLista("MODULOS POUSADOS", modsPousados)
    mostrarLista("MODULOS EM ESPERA", modsEspera)
    mostrarLista("MODULOS EM ALERTA", modsAlerta)
    mostrarPilhaAlertas()


def mostrarMenu():
    # Menu simples para demonstrar repeticao com while e escolha com if encadeado.
    print("\nEscolha uma opcao do MGPEB:")
    print("1 - Mostrar regras logicas")
    print("2 - Executar buscas lineares")
    print("3 - Carregar fila ordenada")
    print("4 - Processar fila de pouso")
    print("5 - Mostrar resumo final")
    print("6 - Mostrar modelo matematico")
    print("7 - Executar demonstracao completa")
    print("8 - Escolher modo de dados")
    print("0 - Sair")


def executarDemoCompleta():
    # Caminho rapido para apresentar tudo sem ficar escolhendo opcao por opcao.
    mostrarAmbiente()
    mostrarRegrasLogicas()
    mostrarBuscas()
    prepararFilaOrdenada()
    mostrarLista("FILA DE POUSO ORDENADA", filaPouso)
    processarFila()
    mostrarResumoFinal()
    mostrarModeloDescida()


def main():
    global opcaoMenu

    # O menu fica ativo ate o usuario escolher sair.
    # Isso mostra a aplicacao direta do while estudado na Fase 2.
    mostrarTitulo(f"{nomeSistema} - {versaoSistema}")

    while opcaoMenu != "0":
        mostrarMenu()
        opcaoMenu = input("Opcao escolhida: ").strip()

        if opcaoMenu == "8":
            escolherModoDados()
        elif opcaoMenu == "1":
            mostrarRegrasLogicas()
        elif opcaoMenu == "2":
            mostrarBuscas()
        elif opcaoMenu == "3":
            prepararFilaOrdenada()
            mostrarLista("FILA DE POUSO ORDENADA", filaPouso)
        elif opcaoMenu == "4":
            if len(filaPouso) == 0 and not filaProcessadaCheck:
                prepararFilaOrdenada()
            processarFila()
        elif opcaoMenu == "5":
            mostrarResumoFinal()
        elif opcaoMenu == "6":
            mostrarModeloDescida()
        elif opcaoMenu == "7":
            executarDemoCompleta()
        elif opcaoMenu == "0":
            print("Encerrando o MGPEB.")
        else:
            print("Opcao invalida. Tente novamente.")


main()
