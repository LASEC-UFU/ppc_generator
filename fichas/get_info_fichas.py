import csv
import re
from PyPDF2 import PdfReader
import os, easygui
from unidecode import unidecode

def get_pdfs_from_folder():
    """
    Permite ao usuário selecionar uma pasta usando easygui
    e retorna uma lista com todos os arquivos PDF encontrados na pasta selecionada.
    
    Retorno:
        list: Lista de caminhos completos para os arquivos PDF na pasta selecionada.
    """
    # Selecionar a pasta com o easygui
    folder = easygui.diropenbox(msg="Selecione uma pasta com arquivos PDF", title="Seleção de Pasta")
    
    if not folder:
        print("Nenhuma pasta foi selecionada.")
        return []
    
    # Procurar por arquivos PDF na pasta
    pdf_files = [os.path.join(folder, file) for file in os.listdir(folder) if file.lower().endswith('.pdf')]
    
    return pdf_files

ACM_TAB_4_1 = {
    "Usuários e Organizações": [
        "Questões Sociais e Prática Profissional",
        "Política e Gestão de Segurança",
        "Gestão e Liderança de Sistemas de Informação (SI)",
        "Arquitetura Empresarial",
        "Gestão de Projetos",
        "Design de Experiência do Usuário (UX)",
    ],
    "Modelagem de Sistemas": [
        "Questões e Princípios de Segurança",
        "Análise e Design de Sistemas",
        "Análise de Requisitos e Especificações",
        "Gestão de Dados e Informação",
    ],
    "Arquitetura e Infraestrutura de Sistemas": [
        "Sistemas e Serviços Virtuais",
        "Sistemas Inteligentes (IA)",
        "Internet das Coisas (IoT)",
        "Computação Paralela e Distribuída",
        "Redes de Computadores",
        "Sistemas Embarcados",
        "Tecnologia de Sistemas Integrados",
        "Tecnologias de Plataforma",
        "Tecnologia e Implementação de Segurança",
    ],
    "Desenvolvimento de Software": [
        "Qualidade de Software, Verificação e Validação",
        "Processos de Software",
        "Modelagem e Análise de Software",
        "Design de Software",
        "Desenvolvimento Baseado em Plataformas",
    ],
    "Fundamentos de Software": [
        "Gráficos e Visualização",
        "Sistemas Operacionais",
        "Estruturas de Dados, Algoritmos e Complexidade",
        "Linguagens de Programação",
        "Fundamentos de Programação",
        "Fundamentos de Sistemas Computacionais",
    ],
    "Hardware": [
        "Arquitetura e Organização de Computadores",
        "Design Digital",
        "Circuitos e Eletrônica",
        "Processamento de Sinais",
    ],
}

ACM_CSV = {
    "Usuários e Organizações": "CC_UO1",
    "Modelagem de Sistemas": "CC_SM2",
    "Arquitetura e Infraestrutura de Sistemas": "CC_SAI3",
    "Desenvolvimento de Software": "CC_SD4",
    "Fundamentos de Software": "CC_SF5",
    "Hardware": "CC_HW6",
}

ACM_TAB_4_2 = [
    "Pensamento Analítico e Crítico", #  Processo mental de simplificar informações complexas e tomar decisões
    "Colaboração e Trabalho em Equipe", #  Dividir tarefas complexas e trabalhar em conjunto para completá-las
    "Perspectivas Éticas e Interculturais", #  Visões éticas de diferentes pontos de vista em contextos humanos
    "Matemática e Estatística", #  Uso abstrato de números e teorias, especialmente na análise de dados
    "Priorização e Gestão de Múltiplas Tarefas", #  Organizar e priorizar múltiplas tarefas simultaneamente
    "Comunicação Oral e Apresentação", #  Transmitir mensagens com eficácia usando recursos visuais e orais
    "Resolução de Problemas e Solução de Erros", #  Buscar e resolver problemas de maneira lógica e organizada
    "Organização e Planejamento de Projetos e Tarefas", #  Planejar e organizar projetos para atingir resultados
    "Controle e Garantia de Qualidade", #  Usar métodos para identificar e prevenir defeitos
    "Gestão de Relacionamentos", #  Manter o engajamento com clientes e parceiros
    "Pesquisa e Aprendizagem Independente", #  Iniciar e conduzir projetos sem necessidade de direção
    "Gestão de Tempo", #  Utilizar o tempo de maneira produtiva e eficiente
    "Comunicação Escrita", #  Uso eficaz da escrita para comunicação entre pessoas e organizações
]

# ACM_TAB_4_3 = [ # Taxonomia de Bloom
#     "Lembrar", #	Relembrar materiais previamente aprendidos
#     "Compreender", #	Demonstrar entendimento por meio de organização e comparação
#     "Aplicar", #	Resolver problemas novos aplicando o conhecimento
#     "Analisar", #	Examinar e decompor informações em partes
#     "Avaliar", #	Fazer julgamentos sobre a validade e qualidade das informações
#     "Criar", #	Compilar informações em padrões novos ou propor alternativas
# ]

ACM_TAB_4_3 = [ # Taxonomia de Bloom
    "Recordação", # "Rememoração", #"Lembrança",   # Ato de relembrar materiais previamente aprendidos
    "Compreensão", # Capacidade de demonstrar entendimento (por meio de organização e comparação)
    "Aplicação",   # Utilização do conhecimento para resolver problemas novos
    "Análise",     # Exame e decomposição das informações em partes
    "Avaliação",   # Julgamento sobre a validade e qualidade das informações
    "Criação",     # Compilação das informações em padrões novos ou proposição de alternativas
]

ACM_TAB_4_4 = [ # Elemento |	Elaboração
    "Adaptável", #	Flexível; ágil, ajusta-se em resposta à mudança
    "Colaborativo", #	Colabora em equipe, demonstra disposição para trabalhar em conjunto
    "Inventivo", #	Exploratório; busca soluções além do óbvio
    "Meticuloso", #	Atento aos detalhes; minucioso, preciso
    "Apaixonado", #	Convicção; forte comprometimento; envolvimento cativante
    "Proativo", #	Atua com iniciativa; empreendedor; independente
    "Profissional", #	Demonstra profissionalismo, discrição, comportamento ético e perspicácia
    "Orientado por Propósito", #	Focado em metas; busca atingir objetivos; apresenta discernimento em termos de resultados e negócios
    "Responsável", #	Exerce bom julgamento, usa discrição; age de maneira apropriada
    "Solícito", #	Respeitoso; reage de forma rápida e positiva
    "Autodirigido", #	Autônomo, motivado internamente, determinado, independente
]


# Função para extrair informações de um único PDF
def extract_info_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = "\n".join(page.extract_text() for page in reader.pages).replace("\nComplexidade"," Complexidade")
    
    # if not "IGOR SOUSA" in text:
    #     print(re.search(r"COMPONENTE CURRICULAR:\s*(.*)", text).group(1).strip())
    #     exit()
    

    

    alt_cod = "!".join(pdf_path.split("_")[-2:])
    if "Curricular" in alt_cod:
        alt_cod = "?"
    
    # # Regex para capturar qualquer texto que termine com " [4.1]" ou " [4.2]"
    # elementos_4_1 = re.findall(r"(.*?)\s*\[4\.1\]", text)
    # elementos_4_1_3 = re.findall(r"\s*\[4\.1\]\n(.*?)\s*", text)
    # elementos_4_2 = re.findall(r"(.*?)\s*\[4\.2\]", text)
    # elementos_4_2_3 = re.findall(r"\s*\[4\.2\]\n(.*?)\s*", text)

    # Regex para capturar elementos que terminam com "[4.1]" e seus níveis
    elementos_e_niveis_41 = re.findall(r"(.*?)\s*\[4\.1\]\s*([\wÀ-ÿ]+)", text)

    # Separar os elementos e níveis em listas
    elementos_41 = [elem.strip() for elem, _ in elementos_e_niveis_41]
    niveis_41 = [nivel.strip() for _, nivel in elementos_e_niveis_41]
    
    # Regex para capturar elementos que terminam com "[4.1]" e seus níveis
    elementos_e_niveis_42 = re.findall(r"(.*?)\s*\[4\.2\]\s*([\wÀ-ÿ]+)", text)

    # Separar os elementos e níveis em listas
    elementos_42 = [elem.strip() for elem, _ in elementos_e_niveis_42]
    niveis_42 = [nivel.strip() for _, nivel in elementos_e_niveis_42]
    
    # Regex para capturar as disposições na seção "DISPOSIÇÕES"
    disposicoes_ = re.findall(r"DISPOSIÇÕES\n+([A-ZA-zÀ-ÿ ]+)\n([A-ZA-zÀ-ÿ ]+)\n([A-ZA-zÀ-ÿ ]+)\n", text)[0]
    disposicoes = [disp.strip() for disp in disposicoes_]
    
    # Regex para capturar a ementa
    ementa_match = re.search(r"EMENTA\s*([\s\S]*?)\nPROGRAMA", text)
    ementa = " ".join(ementa_match.group(1).strip().split("\n")[:-2]) if ementa_match else "Ementa não encontrada"

    
    # Nome,Código,PER,CHT,CHP,CHD,TOT,FLX,OBR,OPT,A|B,EXT,FORM_BAS,FORM_HUM,FORM_TEC,FORM_CMP,CC_UO1,CC_SM2,CC_SAI3,CC_SD4,CC_SF5,CC_HW6,PREQ,CERT_CG:include/certificado/Computação_Gráfica_e_Realidade_Virtual_e_Aumentada.tex,CERT_AL:include/certificado/Engenharia_de_Algoritmos.tex,CERT_HW:include/certificado/Engenharia_de_Hardware.tex,CERT_RC:include/certificado/Engenharia_de_Redes_de_Computadores.tex

    
    
    # Regex para capturar informações específicas
    # Nome,Código,PER,CHT,CHP,CHD,TOT,FLX,OBR,OPT,A|B,EXT,FORM_BAS,FORM_HUM,FORM_TEC,FORM_CMP,CC_UO1,CC_SM2,CC_SAI3,CC_SD4,CC_SF5,CC_HW6,PREQ,CREQ,
    data = {
        "Nome": re.search(r"COMPONENTE CURRICULAR:\s*(.*)", text).group(1).strip().replace("-"," ").title().replace(" E ", " e ").replace(" De ", " de ").replace(" Da ", " da ").replace(" Do ", " do ").replace(" A ", " a ").replace(" À ", " à ").replace(" Para ", " para ").replace(" Iot", " IOT").replace(" Ii", " II").replace(" IIi", " III"),
        "Código": re.search(r"CÓDIGO:\s*(.*)", text).group(1).strip() if alt_cod == "?" else alt_cod.replace(".pdf",""), #re.search(r"informe o código", text) else "?",
        "PER": None,
        # "UAO": re.search(r"SIGLA:\s*(.*)", text).group(1).strip(),
        "CHT": re.search(r"TEÓRICA:\s*(\d+)", text).group(1).strip(),
        "CHP": re.search(r"PRÁTICA:\s*(\d+)", text).group(1).strip(),
        "CHD": re.search(r"DISTÂNCIA:\s*(\d+)", text).group(1).strip(),
        "TOT": re.search(r"CH TOTAL:\s*(\d+)", text).group(1).strip(),
        "FLX": True, # rever
        "OBR": False,
        "OPT": False,
        "A|B": "A", # rever
        "EXT": False,
        "FORM_BAS": False,
        "FORM_HUM": False,
        "FORM_TEC": False,
        "FORM_CMP": False,
        "CC_UO1": False,
        "CC_SM2": False,
        "CC_SAI3": False,
        "CC_SD4": False,
        "CC_SF5": False,
        "CC_HW6": False,
        "PREQ": [],
        "CREQ": [],
        "Elementos41": "|".join(elementos_41) if elementos_41 else "",
        "Níveis41": "|".join(niveis_41) if niveis_41 else "",
        "Elementos42": "|".join(elementos_42) if elementos_42 else "",
        "Níveis42": "|".join(niveis_42) if niveis_42 else "",
        "Disposições": "|".join(disposicoes) if disposicoes else "",
        "Ementa": ementa,
    }
    
    if data["Nome"].startswith("Experimental de "):
        data["Nome"] = data["Nome"].replace("Experimental de ", "") + ", Experimental de"
    
    if False: # pular essas linhas ####################################################################################
        periodo = input(f"Qual período de {data["Nome"]}? ")
        data["PER"] = int(periodo) if periodo.isnumeric() else "?"
        while True:
            ask = input("0:OBR / 1:OPT / 2:EXT ? ")
            if ask.isnumeric() or int(ask) in [0,1,2]:
                ask = int(ask)
                break
        data[["OBR","OPT","EXT"][ask]] = True
        while True:
            ask = input("0:FORM_BAS / 1:FORM_HUM / 2:FORM_TEC / 3:FORM_CMP ? ")
            if ask.isnumeric() or int(ask) in [0,1,2,3]:
                ask = int(ask)
                break
        data[["FORM_BAS","FORM_HUM","FORM_TEC","FORM_CMP"][ask]] = True
        while (preq := input("Pré-requisito? [coloque '?'+sigla se não tiver código e for FEELT]: ")):
            if preq.startswith("?"):
                data["PREQ"].append("FEELT"+preq)
            else:
                data["PREQ"].append(preq)
        data["PREQ"] = "/".join(data["PREQ"])
        while (creq := input("Correquisito? [coloque '?'+sigla se não tiver código e for FEELT]: ")):
            if creq.startswith("?"):
                data["CREQ"].append("FEELT|"+creq[1:])
            else:
                data["CREQ"].append(creq)
        data["CREQ"] = "/".join(data["CREQ"])
    else:
        with open("fichas/perinfo.csv", mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["Código"] == data["Código"]:
                    data["OBR"] = True
                    data["PER"] = row["PER"]
                    data["FORM_BAS"] = row["FORM"] == "B"
                    data["FORM_HUM"] = row["FORM"] == "H"
                    data["FORM_TEC"] = row["FORM"] == "T"
                    data["FORM_CMP"] = row["FORM"] == "C"
                    data["PREQ"] = row["PREQ"]
                    data["CREQ"] = row["CREQ"]
                    break

    
    return data

# Função principal para processar vários PDFs
def process_pdfs(pdf_files, output_csv):
    # Lista para armazenar os dados de cada PDF
    all_data = []

    # OPTATIVAS
    for i in range(8):
        all_data.append(
            {
                "Nome": "Optativa",
                "Código": f"OPT{i+1}",
                "PER": f"{[7,7,7,7,8,8,8,8][i]}",
                # "UAO": "?",
                "CHT": -1,
                "CHP": -1,
                "CHD": -1,
                "TOT": 45,
                "FLX": True, # rever
                "OBR": False,
                "OPT": True,
                "A|B": "A", # rever
                "EXT": False,
                "FORM_BAS": False,
                "FORM_HUM": False,
                "FORM_TEC": False,
                "FORM_CMP": True,
                "CC_UO1": False,
                "CC_SM2": False,
                "CC_SAI3": False,
                "CC_SD4": False,
                "CC_SF5": False,
                "CC_HW6": False,
                "PREQ": "",
                "CREQ": "",
                "Elementos41": "",
                "Níveis41": "",
                "Elementos42": "",
                "Níveis42": "",
                "Disposições": "",
                "Ementa": "",
            }
        )
    
    # EXTENSÃO
    for i in range(5):
        all_data.append(
            {
                "Nome": ("Memorial de " if i == 0 else "") + "Atividades Curriculares de Extensão" + [""," I"," II"," III"," IV"][i],
                "Código": "FEELT!MACE" if i == 0 else f"ACE{i}",
                "PER": f"{[8,4,5,6,7][i]}",
                # "UAO": "FEELT" if i == 0 else "?",
                "CHT": -1 if i > 0 else 30,#[30,0,0,0,0][i],
                "CHP": -1 if i > 0 else 0,#[0,90,90,75,60][i],
                "CHD": -1 if i > 0 else 0,#0,
                "TOT": [30,60,75,90,90][i],
                "FLX": True, # rever
                "OBR": False,
                "OPT": False,
                "A|B": "A", # rever
                "EXT": True,
                "FORM_BAS": False,
                "FORM_HUM": True,
                "FORM_TEC": False,
                "FORM_CMP": False,
                "CC_UO1": False,
                "CC_SM2": False,
                "CC_SAI3": False,
                "CC_SD4": False,
                "CC_SF5": False,
                "CC_HW6": False,
                "PREQ": "ACE4" if i == 0 else (f"ACE{i-1}" if i > 1 else ""),
                "CREQ": "",
                "Elementos41": "",
                "Níveis41": "",
                "Elementos42": "",
                "Níveis42": "",
                "Disposições": "",
                "Ementa": "",
            }
        )
    
    all_data.append(
        {
            "Nome": "Atividade de Conclusão de Curso",
            "Código": "ACC",
            "PER": "acc",
            # "UAO": "",
            "CHT": 0,
            "CHP": 300,
            "CHD": 0,
            "TOT": 300,
            "FLX": True, # rever
            "OBR": True,
            "OPT": False,
            "A|B": "A", # rever
            "EXT": False,
            "FORM_BAS": False,
            "FORM_HUM": False,
            "FORM_TEC": True,
            "FORM_CMP": False,
            "CC_UO1": False,
            "CC_SM2": False,
            "CC_SAI3": False,
            "CC_SD4": False,
            "CC_SF5": False,
            "CC_HW6": False,
            "PREQ": "",
            "CREQ": "",
            "Elementos41": "",
            "Níveis41": "",
            "Elementos42": "",
            "Níveis42": "",
            "Disposições": "",
            "Ementa": "",
        }
    )
    
    all_data.append(
        {
            "Nome": "Atividade Acadêmicas Complementares",
            "Código": "AAC",
            "PER": "aac",
            # "UAO": "",
            "CHT": -1,
            "CHP": -1,
            "CHD": -1,
            "TOT": 90,
            "FLX": True, # rever
            "OBR": True,
            "OPT": False,
            "A|B": "A", # rever
            "EXT": False,
            "FORM_BAS": False,
            "FORM_HUM": False,
            "FORM_TEC": False,
            "FORM_CMP": True,
            "CC_UO1": False,
            "CC_SM2": False,
            "CC_SAI3": False,
            "CC_SD4": False,
            "CC_SF5": False,
            "CC_HW6": False,
            "PREQ": "",
            "CREQ": "",
            "Elementos41": "",
            "Níveis41": "",
            "Elementos42": "",
            "Níveis42": "",
            "Disposições": "",
            "Ementa": "",
        }
    )

    for pdf in pdf_files:
        data = extract_info_from_pdf(pdf)
        all_data.append(data)
        
    all_data.sort(key=lambda x:(x["PER"], unidecode(x["Nome"].upper())))
    
    temas = dict([(k, 0) for k in ACM_TAB_4_1.keys()])
    temas["Ciclo básico engenharia"] = 0
    total_temas = 0

    msg = ""
    for i, data in enumerate(all_data):
        print()
        print(i+1, data["Nome"], "="*(60 - len(data["Nome"])))
        msg += f"{i+1} {data['Nome']} {'='*(60 - len(data['Nome']))}\n"
        # print(data["Ementa"])
        msg += data["Ementa"] + '\n'*2
        cc_ = set()
        for elem, nivel in zip(data["Elementos41"].split("|"), data["Níveis41"].split("|")):
            if not elem in sum(ACM_TAB_4_1.values(), start=[]):
                print("X", end=" ")
            else:
                for k, v in ACM_TAB_4_1.items():
                    if elem in v:
                        cc_.add(k)
                print("-", end=" ")
            print(f":{elem}:", end="\t")
            if not nivel in ACM_TAB_4_3:
                print("X", end=" ")
            else:
                print("-", end=" ")
            print(f":{nivel}:")
            msg += f"{elem}: {nivel}\n"
        print("---")
        msg += f"- < {'; '.join(cc_) if cc_ else 'ND'} >\n"
        # importante!!!
        for aux in cc_:
            all_data[i][ACM_CSV[aux]] = True
        #
        total_temas += int(data["TOT"])
        for k in cc_:
            temas[k] += int(data["TOT"])
        if not cc_:
            temas["Ciclo básico engenharia"] += int(data["TOT"])
        print(cc_)
        print("---")
        for elem, nivel in zip(data["Elementos42"].split("|"), data["Níveis42"].split("|")):
            if not elem in ACM_TAB_4_2:
                print("X", end=" ")
            else:
                print("-", end=" ")
            print(f":{elem}:", end="\t")
            if not nivel in ACM_TAB_4_3:
                print("X", end=" ")
            else:
                print("-", end=" ")
            print(f":{nivel}:")
            msg += f"{elem}: {nivel}\n"
        msg += f"\nDisposições: {data["Disposições"]}\n"
        msg += "\n"*2
            
    with open("ementas.txt", "w") as f:
        f.write(msg)
    
    print()
    print("*"*42)
    print()
    for k, v in temas.items():
        print(k, ":", v, "=", f"{100*v/total_temas:.2f}%")
    
    if True: # pular essas linhas ####################################################################################
        for d in all_data:
            print(d["Código"],"\t",d["Nome"])
    
        # exit()
        
    
    # Escrever os dados no arquivo CSV
    with open(output_csv, mode="w", newline="", encoding="utf-8") as file:
        fields = list(data.keys())
        # fields.remove("Ementa")
        # fields.remove("UAO")
        writer = csv.DictWriter(file, fieldnames=data.keys(), delimiter=";")#["Código", "Nome", "UAO", "CHT", "CHP", "CHD", "TOT", "CC2020 Tab.4.1", "CC2020 Tab.4.2"])
        writer.writeheader()
        all_data_copy = all_data.copy()
        for i in range(len(all_data_copy)):
            # del all_data_copy[i]["UAO"]
            del all_data_copy[i]["Ementa"]
        writer.writerows(all_data)

# Lista de arquivos PDF e arquivo de saída
pdf_files = get_pdfs_from_folder()  # Substitua pelos caminhos dos PDFs
print(f"Foram encontrados {len(pdf_files)} arquivos PDF.")
output_csv = "py/PPC_disciplinas.csv"

process_pdfs(pdf_files, output_csv)
print(f"Informações extraídas e salvas em {output_csv}")
