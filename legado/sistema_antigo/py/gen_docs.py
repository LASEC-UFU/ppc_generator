# source ./ppc/bin/activate
from typing import TypeVar, Type
from unidecode import unidecode
import csv, shutil, os, re


PER_ACC = 5
PER_NOBR = 2

def read_news(curr_path: str):
    """
    Lê o arquivo 'old.csv' (hardcoded) e compara com 'curr.csv' (passado em curr_path).
    
    Se 'old.csv' não existir:
      - Lemos todo o 'curr.csv' e consideramos todas as linhas como "novas",
      - Gravamos 'curr.csv' em 'old.csv',
      - Retornamos todas as linhas (cabeçalho + dados) lidas de 'curr.csv'.
    
    Se 'old.csv' existir:
      - Comparação normal: retorna apenas o cabeçalho e as linhas novas/diferentes
        em relação a 'old.csv'.
      - Ao final, sobrescreve 'old.csv' com o conteúdo de 'curr.csv'.
    
    Retorna uma lista de listas, onde o primeiro item é o cabeçalho,
    e os demais são as linhas consideradas "novas ou diferentes".
    """
    old_path = "old.csv"  # Hardcoded

    # 1) Verifica se old.csv existe
    if not os.path.exists(old_path):
        # Se NÃO existe, vamos ler todo o 'curr.csv' (header + dados)
        with open(curr_path, mode='r', encoding='utf-8', newline='') as f_curr:
            reader_curr = list(csv.reader(f_curr))

        # Copia 'curr.csv' para 'old.csv'
        shutil.copyfile(curr_path, old_path)

        # Aqui, retornamos todo o 'curr.csv' (primeira linha = cabeçalho, demais = linhas)
        return reader_curr

    # 2) Se old.csv existe, faz a comparação
    linhas_diferentes_ou_novas = []

    # Lê o arquivo old.csv
    with open(old_path, mode='r', encoding='utf-8', newline='') as f_old:
        reader_old = csv.reader(f_old, delimiter=";")
        header_old = next(reader_old)  # cabeçalho de old (caso queira usar)
        old_rows = set(tuple(row) for row in reader_old)

    # Lê o arquivo curr.csv
    with open(curr_path, mode='r', encoding='utf-8', newline='') as f_curr:
        reader_curr = csv.reader(f_curr, delimiter=";")
        header_curr = next(reader_curr, None)  # cabeçalho de curr

        for row in reader_curr:
            # Se a linha de curr não está em old, é nova/diferente
            if tuple(row) not in old_rows:
                linhas_diferentes_ou_novas.append(row)

    # Monta o resultado final (cabeçalho + linhas novas/diferentes)
    resultado = []
    if header_curr:
        resultado.append(header_curr)
    resultado.extend(linhas_diferentes_ou_novas)

    # 3) Sobrescreve old.csv com o conteúdo de curr.csv
    shutil.copyfile(curr_path, old_path)

    return resultado

T = TypeVar('T', bound='Certificado')


with open("py/PPC_disciplinas_final.csv") as f:
    reader = csv.reader(f, delimiter=";")
    header = next(reader)  # cabeçalho de old (caso queira usar)
    disciplinas_csv = list(dict(zip(header,r)) for r in reader)
    
print(disciplinas_csv)

    # lines = list(l.strip().replace("s, O", "s\, O") for l in f.readlines())

optativas_equivalentes_csv  = list()
# retirar disciplinas que não são obrigatórias
to_delete = [] 
for i, d in enumerate(disciplinas_csv):
    print(d)
    if d['FLX'] == 'False':
        print(d)
        to_delete.append(i)

for i in reversed(to_delete):
    optativas_equivalentes_csv.append(disciplinas_csv[i])
    del disciplinas_csv[i]
# ===========================================

def nome_alt(nome:str, traz_pra_inicio:str=", Experimental de") -> str:
    if nome.endswith(traz_pra_inicio):
        return traz_pra_inicio.replace(",", "").strip() + " " + nome.replace(traz_pra_inicio, "")
    return nome
    
disciplinas_csv.sort(key=lambda x: (x['PER'], unidecode(x['Nome'])))

print("***\n", disciplinas_csv)

# exit()

class Certificado:
    @classmethod
    def new(cls: Type[T], info:str) -> T:
        assert(info.startswith("CERT_") and info.count(":") == 1)
        cert, fn = info.split(":")
        sigla = cert.split("_")[-1]
        nome = fn.split("/")[-1].split(".")[0].replace("_", " ")
        return cls(nome, sigla, fn)
    def __init__(self, certificado, sigla, arquivo) -> None:
        self.certificado = certificado
        self.sigla = sigla
        self.arquivo = arquivo
    def __repr__(self) -> str:
        return f"{self.certificado} ({self.sigla}): {self.arquivo}"
    def isThis(self, info):
        return self.certificado == info or \
            self.sigla == info or \
            self.arquivo == info

certificados = dict()
for disc in list(col for col in header if col.startswith("CERT_") and col.count(":") == 1):
    certificados[disc.split(":")[0]] = Certificado.new(disc)
print(certificados)

class Carga_Horária:
    __symbol__ = r"--"
    def __init__(self, horas:int):
        self.horas:int = int(horas)
    def __repr__(self):
        return f"{self.horas}" if self.horas >= 0 else Carga_Horária.__symbol__
    def get(self):
        return max(self.horas, 0)
    def set(self, horas:int):
        self.horas = int(horas)


class Disciplina:
    def __init__(self,
                Nome:str= "",
                Codigo:str= "",
                PER:str= "",
                CHT:Carga_Horária = Carga_Horária(-1),
                CHP:Carga_Horária = Carga_Horária(-1),
                CHD:Carga_Horária = Carga_Horária(-1),
                CHE:Carga_Horária = Carga_Horária(-1),
                TOT:int= 0,
                FLX:bool= False,
                OBR:bool= False,
                OPT:bool= False,
                AB:str= "",
                EXT:bool= False,
                FORM_BAS:bool= False,
                FORM_HUM:bool= False,
                FORM_TEC:bool= False,
                FORM_CMP:bool= False,
                CC_UO1:bool= False,
                CC_SM2:bool= False,
                CC_SAI3:bool= False,
                CC_SD4:bool= False,
                CC_SF5:bool= False,
                CC_HW6:bool= False,
                PREQ:list= [],
                CREQ:list= [],
                QEXTR:list= [],
                DCN_base:list= [],
                DCN_tec:list= [],
                Ementa:str= "",
                CERT:list[Certificado]= [],
                 ) -> None:
        self.enum = 0
        self.Nome:str = Nome.replace('"','')
        self.Codigo:str = Codigo
        self.PER:str = PER
        self.CHT:Carga_Horária = Carga_Horária(CHT)
        self.CHP:Carga_Horária = Carga_Horária(CHP)
        self.CHD:Carga_Horária = Carga_Horária(CHD)
        self.CHE:Carga_Horária = Carga_Horária(CHE)
        self.TOT:int = TOT
        self.FLX:bool = FLX
        self.OBR:bool = OBR
        self.OPT:bool = OPT
        self.AB:str = AB
        self.EXT:bool = EXT
        self.FORM_BAS:bool = FORM_BAS
        self.FORM_HUM:bool = FORM_HUM
        self.FORM_TEC:bool = FORM_TEC
        self.FORM_CMP:bool = FORM_CMP
        self.CC_UO1:bool = CC_UO1
        self.CC_SM2:bool = CC_SM2
        self.CC_SAI3:bool = CC_SAI3
        self.CC_SD4:bool = CC_SD4
        self.CC_SF5:bool = CC_SF5
        self.CC_HW6:bool = CC_HW6
        self.PREQ:list = PREQ
        self.CREQ:list = CREQ
        self.QEXTR:list = QEXTR
        self.DCN_base:list = DCN_base
        self.DCN_tec:list = DCN_tec
        self.Ementa:str = Ementa
        self.CERT:list[Certificado] = CERT

def keysort(x):
    return (x.Codigo.startswith("FEELT"), "Extensão" in x.Nome, unidecode(x.Nome))


def upd_codigo(nome, cod):
    nome = unidecode(nome).replace("-", " ").replace(".", " ")
    if "?" in cod:
        romans = {"I":"1", "II":"2", "III":"3", "IV":"4", "V":"5", "VI":"6", "VII":"7", "VIII":"8", "IX":"9"}
        words = list(n[0].upper() for n in nome.split(" ") if len(n) > 2 or (not n in romans.keys() and n.isupper()))
        if any(nome.endswith(n) for n in romans.keys()):
            words.append(romans[nome.split(' ')[-1]])
        sigla = "".join(words)
        if len(sigla) == 2:
            sigla = sigla[0] + nome.split(" ")[-1][:2].upper()
        elif len(sigla) < 2:
            sigla = nome[:3].upper()
        return cod + sigla
    return cod

def isint(number):
    try:
        int(number)
        return True
    except:
        return False

disciplinas:list[Disciplina] = list()
for disc in disciplinas_csv:
    # disc = disc.replace("\,", "!@#").split(",")
    Nome:str = disc[header[0]].replace("!@#", ",")
    Codigo:str = upd_codigo(Nome, disc[header[1]])
    print(Nome, Codigo)
    PER:str = disc[header[2]]
    CHT:Carga_Horária = Carga_Horária((disc[header[3]]) if isint(disc[header[3]]) else 0)
    CHP:Carga_Horária = Carga_Horária((disc[header[4]]) if isint(disc[header[4]]) else 0)
    CHD:Carga_Horária = Carga_Horária((disc[header[5]]) if isint(disc[header[5]]) else 0)
    CHE:Carga_Horária = Carga_Horária((disc[header[6]]) if isint(disc[header[6]]) else 0)
    TOT:int = int(disc[header[7]]) if disc[header[7]].isnumeric() else 0
    FLX:bool = disc[header[8]].upper() == "TRUE"
    OBR:bool = disc[header[9]].upper() == "TRUE"
    OPT:bool = disc[header[10]].upper() == "TRUE"
    AB:str = disc[header[11]]
    EXT:bool = disc[header[12]].upper() == "TRUE"
    FORM_BAS:bool = disc[header[13]].upper() == "TRUE"
    FORM_HUM:bool = disc[header[14]].upper() == "TRUE"
    FORM_TEC:bool = disc[header[15]].upper() == "TRUE"
    FORM_CMP:bool = disc[header[16]].upper() == "TRUE"
    CC_UO1:bool = disc[header[17]].upper() == "TRUE"
    CC_SM2:bool = disc[header[18]].upper() == "TRUE"
    CC_SAI3:bool = disc[header[19]].upper() == "TRUE"
    CC_SD4:bool = disc[header[20]].upper() == "TRUE"
    CC_SF5:bool = disc[header[21]].upper() == "TRUE"
    CC_HW6:bool = disc[header[22]].upper() == "TRUE"
    PREQ:list[str] = disc[header[23]].split("/") if disc[header[23]] else []
    CREQ:list[str] = disc[header[24]].split("/") if disc[header[24]] else []
    QEXTR:list[int] = [int(x) for x in (disc[header[header.index("QEXTR")]].split("/") if disc[header[header.index("QEXTR")]] else []) if int(x) > 0]
    DCN_BASE:list[int] = [int(x) for x in (disc[header[header.index("DCN_base")]].split("/") if disc[header[header.index("DCN_base")]] else []) if int(x) >= 0]
    DCN_TEC:list[int] = [int(x) for x in (disc[header[header.index("DCN_ecp")]].split("/") if disc[header[header.index("DCN_ecp")]] else []) if int(x) >= 0]
    CERT:list[Certificado] = list()
    # for i, z in enumerate(zip(certificados.keys(), disc[header[24]:])):
    #     k, b = z
    #     if b.upper() == "TRUE":
    #         CERT.append(certificados[k])
    disciplinas.append(
        Disciplina(
            Nome, Codigo, PER, CHT.horas, CHP.horas, CHD.horas, CHE.horas, TOT, FLX, OBR, OPT, AB, EXT, FORM_BAS, FORM_HUM, FORM_TEC, FORM_CMP, CC_UO1, CC_SM2, CC_SAI3, CC_SD4, CC_SF5, CC_HW6, PREQ, CREQ, QEXTR, DCN_BASE, DCN_TEC
        )
    )

optativas_equivalentes:list[Disciplina] = list()
for disc in optativas_equivalentes_csv:
    # disc = disc.replace("\,", "!@#").split(",")
    Nome:str = disc[header[0]].replace("!@#", ",")
    Codigo:str = upd_codigo(Nome, disc[header[1]])
    print(Nome, Codigo)
    PER:str = disc[header[2]]
    CHT:Carga_Horária = Carga_Horária((disc[header[3]]) if isint(disc[header[3]]) else 0)
    CHP:Carga_Horária = Carga_Horária((disc[header[4]]) if isint(disc[header[4]]) else 0)
    CHD:Carga_Horária = Carga_Horária((disc[header[5]]) if isint(disc[header[5]]) else 0)
    CHE:Carga_Horária = Carga_Horária((disc[header[6]]) if isint(disc[header[6]]) else 0)
    TOT:int = int(disc[header[7]]) if disc[header[7]].isnumeric() else 0
    FLX:bool = disc[header[8]].upper() == "TRUE"
    OBR:bool = disc[header[9]].upper() == "TRUE"
    OPT:bool = disc[header[10]].upper() == "TRUE"
    AB:str = disc[header[11]]
    EXT:bool = disc[header[12]].upper() == "TRUE"
    FORM_BAS:bool = disc[header[13]].upper() == "TRUE"
    FORM_HUM:bool = disc[header[14]].upper() == "TRUE"
    FORM_TEC:bool = disc[header[15]].upper() == "TRUE"
    FORM_CMP:bool = disc[header[16]].upper() == "TRUE"
    CC_UO1:bool = disc[header[17]].upper() == "TRUE"
    CC_SM2:bool = disc[header[18]].upper() == "TRUE"
    CC_SAI3:bool = disc[header[19]].upper() == "TRUE"
    CC_SD4:bool = disc[header[20]].upper() == "TRUE"
    CC_SF5:bool = disc[header[21]].upper() == "TRUE"
    CC_HW6:bool = disc[header[22]].upper() == "TRUE"
    PREQ:list[str] = disc[header[23]].split("/") if disc[header[23]] else []
    CREQ:list[str] = disc[header[24]].split("/") if disc[header[24]] else []
    QEXTR:list[int] = [int(x) for x in (disc[header[header.index("QEXTR")]].split("/") if disc[header[header.index("QEXTR")]] else []) if int(x) > 0]
    DCN_BASE:list[int] = [int(x) for x in (disc[header[header.index("DCN_base")]].split("/") if disc[header[header.index("DCN_base")]] else []) if int(x) >= 0]
    DCN_TEC:list[int] = [int(x) for x in (disc[header[header.index("DCN_ecp")]].split("/") if disc[header[header.index("DCN_ecp")]] else []) if int(x) >= 0]
    # for i, z in enumerate(zip(certificados.keys(), disc[header[24]:])):
    #     k, b = z
    #     if b.upper() == "TRUE":
    #         CERT.append(certificados[k])
    EMENTA:str = disc["Ementa"].split("/") if disc["Ementa"] else []
    CERT:list[Certificado] = list()
    optativas_equivalentes.append(
        Disciplina(
            Nome, Codigo, PER, CHT.horas, CHP.horas, CHD.horas, CHE.horas, TOT, FLX, OBR, OPT, AB, EXT, FORM_BAS, FORM_HUM, FORM_TEC, FORM_CMP, CC_UO1, CC_SM2, CC_SAI3, CC_SD4, CC_SF5, CC_HW6, PREQ, CREQ, QEXTR, DCN_BASE, DCN_TEC, EMENTA
        )
    )


# print(disciplinas)
# exit()

def buildFluxoDisciplinasORIG(name:str, domain:dict, tblrnotes:dict, ch_req_acc:int=0):
    target = unidecode(name.replace(" e ", " ").replace(" de ", " ").replace(" ", "_").lower())
    fn = "include/auto/tab_" + target + ".tex"
    
    notes = dict(zip(tblrnotes.keys(),[str(i+1) for i in range(len(tblrnotes))]))
    tblrnotes_blk = ""
    for k, v in tblrnotes.items():
        tblrnotes_blk += r"note{$" + notes[k] + r"$} = {\scriptsize " + v + r"}," + "\n"
    
    header_txt = r"""\begin{longtblr}[
        theme = ecp,
        caption = {Fluxo Curricular (Guia de Orientações)},%\protect\footnotemark[\value{footnote}]},
        label = {tab:fluxo_curricular_wrt_guia},
    """
    header_txt += tblrnotes_blk
    header_txt += r"""]{
    colspec = {|Q[c,m,wd=3mm]|Q[l,m,wd=20mm]|Q[c,m,wd=13mm]|Q[c,m,wd=5mm]|Q[c,m,wd=5mm]|Q[c,m,wd=5mm]|Q[c,m,wd=19mm]|Q[c,m,wd=19mm]|Q[c,m,wd=8mm]|}, %140mm
    %lastfoot = {\hline},
    rowsep = 1pt,
    rowhead = 2,
    hlines = {fg=AzulEscuro},
    vlines = {fg=AzulEscuro},
    row{odd} = {bg=CinzaClaro},
    row{1} = {bg=AzulEscuro, fg=white},
    row{2} = {bg=AzulEscuro, fg=white},
    row{Z} = {ht=1mm},
    cells  = {font = \fontsize{8pt}{8pt}\selectfont}
    } 
    
    % Cabeçalho Principal
    \SetCell[r=2]{m}\textbf{PER} & 
    \SetCell[r=2]{c,m}\textbf{Componente Curricular} & 
    \SetCell[r=2]{m}\textbf{Natureza}  & 
    \SetCell[c=3]{c,m}\textbf{Carga Horária} & & & 
    \SetCell[c=2]{m}\textbf{Requisitos} & & 
    \SetCell[r=2]{m}\textbf{UA Oferta}\\ \hline[AzulEscuro]
        
    % Segunda linha do cabeçalho (divisão das cargas horárias)
     &  &  & \textbf{CHT} & \textbf{CHP} & \textbf{TOT} & \textbf{PREQ} & \textbf{CREQ} & \\
    """
    body_txt = ""

    to_delete = []
    to_include = dict()
    for k, val in domain.items():
        for d in val:
            # if d["Nome"].startswith("Opt") or d["Nome"] == "ENADE":
            if d["Nome"] == "ENADE": #mudei aqui
                to_delete.append((k, d))
                if not k in to_include:
                    to_include[k] = list()
                to_include[k].append(d)
    print("to_delete:", to_delete)
    for v in to_delete:
        k, d = v
        domain[k].remove(d)
    print("to_include:", to_include)
    for k, val in to_include.items():
        if not k in domain:
            domain[k] = list()
        # aux = None
        # for d in val:
        #     if d["Nome"] != "ENADE":
        #         if aux is None:
        #             aux = d.copy()
        #             aux["Nome"] = "Optativas"
        #         else:
        #             aux["TOT"] += d["TOT"]
        # domain[k].append(aux) #mudei aqui
        for d in val:
            if d["Nome"] == "ENADE":
                domain[k].append(d)
        
    done = []
    for k, val in domain.items():
        nval = len(val)
        nopt = sum([1 for v in val if 1 in v["QEXTR"]])
        for v in val:
            v_nome = nome_alt(v["Nome"]) + (" (EaD)" if v["CHD"].get()>0 else "")
            v_CHP = v["CHP"].get()+ v["CHD"].get()+ v["CHE"].get()
            v_TOT = v["TOT"]
            if v_CHP == 0 and str(v["CHT"]) == Carga_Horária.__symbol__:
                v_CHP = Carga_Horária.__symbol__
            if v_TOT == 0 and str(v["CHT"]) == Carga_Horária.__symbol__ and v_CHP == Carga_Horária.__symbol__:
                v_TOT = Carga_Horária.__symbol__
            if v["TblrNote"]:
                v_nome += r"\TblrNote{$" + notes[v["TblrNote"]] + r"$}"
            if k == "optativas" and k in done and 1 in v["QEXTR"]:
                v_UA = "FACED" if v["UA"] == "LIBRAS" else v["UA"]
                body_txt += " & " + " & ".join([str(n) for n in [v_nome, "Obrigatória" if not v["OPT"] else "Optativa", v["CHT"], v_CHP, v_TOT, r"; ".join(v["PREQ"]), r"; ".join(nome_alt(n) for n in v["CREQ"]), v_UA]])
            elif k == "optativas" and 1 not in v["QEXTR"]:
                continue
            elif nval == 1:
                # print("%%%%%%%%%%%%%%%%%%%%%%%%", v["PREQ"])
                body_txt += r"""\hline[AzulEscuro]
                \SetCell[c=2]{l}{""" + v_nome + r"} & & " + " & ".join([str(n) for n in ["Obrigatória" if not v["OPT"] else "Optativa", v["CHT"], v_CHP, v_TOT, r"; ".join([r'\textit{' + f'{ch_req_acc} horas' + r'}'] if v["PREQ"][0].startswith("*") else v["PREQ"]), r"; ".join(nome_alt(n) for n in v["CREQ"]), v["UA"]]])
            elif not k in done:
                done.append(k)
                if k == "optativas":
                    body_txt += r"""\hline[AzulEscuro]
                \SetCell[r=""" + str(nopt) + r"]{h,bg=white} " + r"\rotatebox[origin=r]{90}{Seleção de Optativas (ver Seção~\ref{sec:optativas} para mais)} & " + " & ".join([str(n) for n in [v_nome, "Obrigatória" if not v["OPT"] else "Optativa", v["CHT"], v_CHP, v_TOT, r"; ".join(v["PREQ"]), r"; ".join(nome_alt(n) for n in v["CREQ"]), v["UA"]]])
                else:
                    body_txt += r"""\hline[AzulEscuro]
                \SetCell[r=""" + str(nval) + r"]{h,bg=white} " + k + r"\textordmasculine & " + " & ".join([str(n) for n in [v_nome, "Obrigatória" if not v["OPT"] else "Optativa", v["CHT"], v_CHP, v_TOT, r"; ".join(v["PREQ"]), r"; ".join(nome_alt(n) for n in v["CREQ"]), v["UA"]]])
            else:
                body_txt += " & " + " & ".join([str(n) for n in [v_nome, "Obrigatória" if not v["OPT"] else "Optativa", v["CHT"], v_CHP, v_TOT, r"; ".join(v["PREQ"]), r"; ".join(nome_alt(n) for n in v["CREQ"]), v["UA"]]])
            body_txt += r"\\" + "\n"
    # for opt in domain["optativas"]:
    #     print("####################################################################")
    #     print(opt)
    #     print("####################################################################")
    footer_txt = r"""%\SetRow{bg=AzulEscuro} & & & & & & & & \\
    \end{longtblr}"""
    with open(fn, "w") as f:
        f.write(header_txt)
        f.write(body_txt)
        f.write(footer_txt)


def buildFluxoDisciplinas(name:str, domain:dict, tblrnotes:dict, ch_req_acc:int=0):
    target = unidecode(name.replace(" e ", " ").replace(" de ", " ").replace(" ", "_").lower())
    fn = "include/auto/tab_" + target + ".tex"
    
    notes = dict(zip(tblrnotes.keys(),[str(i+1) for i in range(len(tblrnotes))]))
    tblrnotes_blk = ""
    for k, v in tblrnotes.items():
        tblrnotes_blk += r"note{$" + notes[k] + r"$} = {\scriptsize " + v + r"}," + "\n"
    
    header_txt = r"""\begin{longtblr}[
        theme = ecp,
        caption = {Fluxo Curricular},%\protect\footnotemark[\value{footnote}]},
        label = {tab:fluxo_curricular},
    """
    header_txt += tblrnotes_blk
    header_txt += r"""]{
    colspec = {|Q[c,m,wd=3mm]|Q[l,m,wd=18mm]|Q[c,m,wd=10mm]|Q[c,m,wd=5mm]|Q[c,m,wd=5mm]|Q[c,m,wd=5mm]|Q[c,m,wd=5mm]|Q[c,m,wd=5mm]|Q[c,m,wd=12mm]|Q[c,m,wd=12mm]|Q[c,m,wd=6mm]|}, %140mm
    %lastfoot = {\hline},
    rowsep = 1pt,
    rowhead = 2,
    hlines = {fg=AzulEscuro},
    vlines = {fg=AzulEscuro},
    row{odd} = {bg=CinzaClaro},
    row{1} = {bg=AzulEscuro, fg=white},
    row{2} = {bg=AzulEscuro, fg=white},
    row{Z} = {ht=1mm},
    cells  = {font = \fontsize{6.5pt}{6.5pt}\selectfont}
    } 
    
    % Cabeçalho Principal
    \SetCell[r=2]{m}\textbf{PER} & 
    \SetCell[r=2]{c,m}\textbf{Componente Curricular} & 
    \SetCell[r=2]{m}\textbf{Natureza}  & 
    \SetCell[c=5]{c,m}\textbf{Carga Horária} & & & & &
    \SetCell[r=2]{m}\textbf{PREQ} & 
    \SetCell[r=2]{m}\textbf{CREQ} & 
    \SetCell[r=2]{m}\textbf{UA Oferta}\\ \hline[AzulEscuro]
        
    % Segunda linha do cabeçalho (divisão das cargas horárias)
     &  &  & \textbf{CHT} & \textbf{CHP} & \textbf{CHD} & \textbf{CHE} & \textbf{TOT} & & & \\
    """
    body_txt = ""

    to_delete = []
    to_include = dict()
    for k, val in domain.items():
        for d in val:
            # if d["Nome"].startswith("Opt") or d["Nome"] == "ENADE":
            if d["Nome"] == "ENADE": #mudei aqui
                to_delete.append((k, d))
                if not k in to_include:
                    to_include[k] = list()
                to_include[k].append(d)
    print("to_delete:", to_delete)
    for v in to_delete:
        k, d = v
        domain[k].remove(d)
    print("to_include:", to_include)
    for k, val in to_include.items():
        if not k in domain:
            domain[k] = list()
        # aux = None
        # for d in val:
        #     if d["Nome"] != "ENADE":
        #         if aux is None:
        #             aux = d.copy()
        #             aux["Nome"] = "Optativas"
        #         else:
        #             aux["TOT"] += d["TOT"]
        # domain[k].append(aux) #mudei aqui
        for d in val:
            if d["Nome"] == "ENADE":
                domain[k].append(d)
        
    done = []
    for k, val in domain.items():
        nval = len(val)
        nopt = sum([1 for v in val if 1 in v["QEXTR"]])
        for v in val:
            v_nome = nome_alt(v["Nome"])
            if v["TblrNote"]:
                v_nome += r"\TblrNote{$" + notes[v["TblrNote"]] + r"$}"
            if k == "optativas" and k in done and 1 in v["QEXTR"]:
                v_UA = "FACED" if v["UA"] == "LIBRAS" else v["UA"]
                body_txt += " & " + " & ".join([str(n) for n in [v_nome, "Obrigatória" if not v["OPT"] else "Optativa", v["CHT"], v["CHP"], v["CHD"], v["CHE"], v["TOT"], r"; ".join(v["PREQ"]), r"; ".join(nome_alt(n) for n in v["CREQ"]), v_UA]])
            elif k == "optativas" and 1 not in v["QEXTR"]:
                continue
            elif nval == 1:
                # print("%%%%%%%%%%%%%%%%%%%%%%%%", v["PREQ"])
                body_txt += r"""\hline[AzulEscuro]
                \SetCell[c=2]{l}{""" + v_nome + r"} & & " + " & ".join([str(n) for n in ["Obrigatória" if not v["OPT"] else "Optativa", v["CHT"], v["CHP"], v["CHD"], v["CHE"], v["TOT"], r"; ".join([r'\textit{' + f'{ch_req_acc} horas' + r'}'] if v["PREQ"][0].startswith("*") else v["PREQ"]), r"; ".join(nome_alt(n) for n in v["CREQ"]), v["UA"]]])
            elif not k in done:
                done.append(k)
                if k == "optativas":
                    body_txt += r"""\hline[AzulEscuro]
                \SetCell[r=""" + str(nopt) + r"]{h,bg=white} " + r"\rotatebox[origin=r]{90}{Seleção de Optativas (ver Seção~\ref{sec:optativas} para mais)} & " + " & ".join([str(n) for n in [v_nome, "Obrigatória" if not v["OPT"] else "Optativa", v["CHT"], v["CHP"], v["CHD"], v["CHE"], v["TOT"], r"; ".join(v["PREQ"]), r"; ".join(nome_alt(n) for n in v["CREQ"]), v["UA"]]])
                else:
                    body_txt += r"""\hline[AzulEscuro]
                \SetCell[r=""" + str(nval) + r"]{h,bg=white} " + k + r"\textordmasculine & " + " & ".join([str(n) for n in [v_nome, "Obrigatória" if not v["OPT"] else "Optativa", v["CHT"], v["CHP"], v["CHD"], v["CHE"], v["TOT"], r"; ".join(v["PREQ"]), r"; ".join(nome_alt(n) for n in v["CREQ"]), v["UA"]]])
            else:
                body_txt += " & " + " & ".join([str(n) for n in [v_nome, "Obrigatória" if not v["OPT"] else "Optativa", v["CHT"], v["CHP"], v["CHD"], v["CHE"], v["TOT"], r"; ".join(v["PREQ"]), r"; ".join(nome_alt(n) for n in v["CREQ"]), v["UA"]]])
            body_txt += r"\\" + "\n"
    # for opt in domain["optativas"]:
    #     print("####################################################################")
    #     print(opt)
    #     print("####################################################################")
    footer_txt = r"""%\SetRow{bg=AzulEscuro} & & & & & & & & & & \\
    \end{longtblr}"""
    with open(fn, "w") as f:
        f.write(header_txt)
        f.write(body_txt)
        f.write(footer_txt)

aux_fluxo = dict()
fluxo_disciplinas = dict()
ch_req_acc = 0
ch_acc = 0
ch_aac = 0
ch_opt = 0
ch_ext = 0
for d in disciplinas:
    aux_fluxo[d.Codigo] = d.Nome  
    fluxo_disciplinas[d.PER] = list()
    if d.PER.isnumeric() and int(d.PER) <= PER_ACC and d.OBR:
        ch_req_acc += d.TOT
    # if d.Codigo.startswith("OPT"):
    if d.Codigo == "OPT": #mudei aqui
        ch_opt += d.TOT
    if d.Codigo == "AAC":
        ch_aac += d.TOT
    if d.Codigo == "ACC":
        ch_acc += d.TOT
    if d.Codigo.startswith("ACE") or d.Codigo.endswith("ACE"):
        ch_ext += d.TOT
tblrnotes = {
    "ACE": r"Os discentes deverão integralizar \textbf{" + str(ch_ext) + r" horas} de atividades extensionistas (ACE) ao longo do curso, incluindo defesa de memorial em disciplina específica, com distribuição sugerida neste fluxo como \textit{Atividades Curriculares de Extensão}.",
    "ENADE": r"O Exame Nacional de Desempenho dos Estudantes (ENADE) integra o Sistema Nacional de Avaliação da Educação Superior (Sinaes) e é componente curricular obrigatório, conforme Lei n\textordmasculine{} 10.861, de 14 de abril de 2004.",
    "AAC": r"Para integralização curricular, o discente deverá cursar \textbf{" + str(ch_aac) + r" horas} horas de atividades acadêmicas complementares (AAC) ao longo do curso.",
    # "ACC": r"Para iniciar a realização do mínimo de " + str(ch_acc) + r" horas na Atividade de Conclusão do Curso - ACC (Estágio Supervisionado ou Trabalho de Conclusão de Curso), o discente deverá ter integralizado, no mínimo, \textbf{" + str(ch_req_acc) + r" horas} em disciplinas obrigatórias, o equivalente a todas do 1\textordmasculine{} ao " + str(PER_ACC) + r"\textordmasculine{} períodos.",
    "ACC": r"Para a realização do mínimo de " + str(ch_acc) + r" horas na Atividade de Conclusão do Curso (Estágio Supervisionado ou do Trabalho de Conclusão de Curso, opção possibilitada pela Resolução CNE/CES nº 5/2016 em seus artigos 7º e 8º), o discente deverá ter integralizado, no mínimo, \textbf{" + str(ch_req_acc) + r" horas} em disciplinas obrigatórias, o equivalente a todas do 1\textordmasculine{} ao " + str(PER_ACC) + r"\textordmasculine{} períodos.",
    "OPT": r"O discente deverá cursar, no mínimo, \textbf{" + str(ch_opt) + r" horas} em disciplinas optativas (ver relação na \autoref{sec:optativas}) para integralização curricular.",
}
for d in disciplinas:
    print(d.PREQ, type(d.PREQ))
    fluxo_disciplinas[d.PER].append({
        "Nome": d.Nome,
        "OPT": d.OPT,
        "CHT": d.CHT,
        "CHP": d.CHP,
        "CHD": d.CHD,
        "CHE": d.CHE,
        "TOT": d.TOT,
        "PREQ": [(x if x.startswith("*") else aux_fluxo[x]) for x in d.PREQ if x] if d.PREQ else ["Livre"],
        "CREQ": [aux_fluxo[x] for x in d.CREQ if x] if d.CREQ else ["Livre"],
        "UA": (r"--" if "ACE" not in d.Codigo else "FEELT") if d.Codigo[:3] in tblrnotes else re.match(r'^[A-Z]+', d.Codigo).group(),
        "TblrNote": d.Codigo[:3] if d.Codigo[:3] in tblrnotes else ("ACE" if d.Codigo.endswith("MACE") else ""),
        # "Last": True if d.Codigo[:3] in tblrnotes and not d.Codigo[:3].startswith("OPT") else (True if d.Codigo.endswith("MACE") else False),
        "Last": True if d.Codigo[:3] in tblrnotes else (True if d.Codigo.endswith("MACE") else False), #mudei aqui
        "QEXTR": [x for x in d.QEXTR],
    })
fluxo_disciplinas["1"].append({
    "Nome": "ENADE (Ingressante)",
    "OPT": False,
    "CHT": Carga_Horária(-1),
    "CHP": Carga_Horária(-1),
    "CHD": Carga_Horária(-1),
    "CHE": Carga_Horária(-1),
    "TOT": 0,
    "PREQ": ["Livre"],
    "CREQ": ["Livre"],
    "UA": r"--",
    "TblrNote": "ENADE",
    "Last": True,
    "QEXTR": [],
})
fluxo_disciplinas["8"].append({
    "Nome": "ENADE (Concluinte)",
    "OPT": False,
    "CHT": Carga_Horária(-1),
    "CHP": Carga_Horária(-1),
    "CHD": Carga_Horária(-1),
    "CHE": Carga_Horária(-1),
    "TOT": 0,
    "PREQ": ["Livre"],
    "CREQ": ["Livre"],
    "UA": r"--",
    "TblrNote": "ENADE",
    "Last": True,
    "QEXTR": [],
})
for k in fluxo_disciplinas.keys():
    fluxo_disciplinas[k].sort(key=lambda x: (x["Last"], x["TblrNote"], unidecode(x["Nome"])))
auxflux = fluxo_disciplinas.copy()
del fluxo_disciplinas["opt"]
del fluxo_disciplinas["aac"]
del fluxo_disciplinas["acc"]
fluxo_disciplinas["aac"] = auxflux["aac"]
fluxo_disciplinas["acc"] = auxflux["acc"]
fluxo_disciplinas["opt"] = auxflux["opt"]

fluxo_disciplinas["optativas"] = list()

aux_fluxo2 = aux_fluxo.copy()
for d in optativas_equivalentes:
    aux_fluxo2[d.Codigo] = d.Nome 

for d in optativas_equivalentes:
    if d.OPT:
        print(d.QEXTR, "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
        fluxo_disciplinas["optativas"].append({
        "Nome": d.Nome,
        "OPT": d.OPT,
        "CHT": d.CHT,
        "CHP": d.CHP,
        "CHD": d.CHD,
        "CHE": d.CHE,
        "TOT": d.TOT,
        "PREQ": [(x if x.startswith("*") else aux_fluxo2[x]) for x in d.PREQ if x] if d.PREQ else ["Livre"],
        "CREQ": [aux_fluxo2[x] for x in d.CREQ if x] if d.CREQ else ["Livre"],
        "UA": r"--" if d.Codigo[:3] in tblrnotes else re.match(r'^[A-Z]+', d.Codigo).group(),
        "TblrNote": d.Codigo[:3] if d.Codigo[:3] in tblrnotes else ("ACE" if d.Codigo.endswith("MACE") else ""),
        # "Last": True if d.Codigo[:3] in tblrnotes and not d.Codigo[:3].startswith("OPT") else (True if d.Codigo.endswith("MACE") else False),
        "Last": True if d.Codigo[:3] in tblrnotes else (True if d.Codigo.endswith("MACE") else False), #mudei aqui
        "QEXTR": [x for x in d.QEXTR],
    })
fluxo_disciplinas["optativas"].sort(key=lambda x: (x["Last"], x["TblrNote"], unidecode(x["Nome"])))
print("#*&$", [k for k,v in fluxo_disciplinas.items()])
print("****************************************************************\n", fluxo_disciplinas.keys(), "\n********************************)")
print(fluxo_disciplinas["optativas"])
buildFluxoDisciplinas("Fluxo Curricular", fluxo_disciplinas, tblrnotes, ch_req_acc)
buildFluxoDisciplinasORIG("Fluxo Curricular conforme Guia", fluxo_disciplinas, tblrnotes, ch_req_acc)


def buildTabDisciplinas(name:str, domain:list[Disciplina], optativas=False, filename=None, total=True):
    hasacc = False
    chacc = 0
    for d in domain:
        if d.Codigo == "ACC":
            hasacc = True
            chacc = d.TOT
    if filename is None:
        target = unidecode(name.replace(":", "").replace(".", "").replace(" e ", " ").replace(" de ", " ").replace(" ", "_").lower())
    else:
        target = unidecode(filename.replace(":", "").replace(".", "").replace(" e ", " ").replace(" de ", " ").replace(" ", "_").lower())
    fn = "include/auto/tab_" + target + ".tex"
    header_txt = r"""\begin{longtblr}[
        theme = ecp,
        caption = {""" + name + r"""},
        label = {tab:""" + target + r"""},"""
    if optativas:
        header_txt += r"""
        remark{\scriptsize \textbf{Nota}} = {\scriptsize As disciplinas optativas pré-aprovadas são apresentadas na \autoref{sec:optativas}.}"""
    elif hasacc:
        header_txt += r"""
        note{$\ast$} = {\scriptsize Contando com as """ + str(chacc) + r""" horas da Atividade de Conclusão de Curso.}"""
    header_txt += r"""]{
    colspec = {Q[l,m,wd=63mm]Q[l,m,wd=23mm]Q[c,m,wd=7mm]Q[c,m,wd=7mm]Q[c,m,wd=7mm]Q[c,m,wd=7mm]Q[c,m,wd=9mm]},
    rowhead = 1,
    row{odd} = {bg=CinzaClaro},
    row{1} = {bg=AzulEscuro, fg=white},
    row{""" + f"{len(domain) + 2}" + r"""} = {bg=AzulClaro, fg=white},
    cells  = {font=\fontsize{10pt}{12pt}\selectfont},
    }
        \textbf{Componente} & \textbf{Código}  & \textbf{CH Teór.} & \textbf{CH Prát.}  & \textbf{CH EaD} & \textbf{CH Ext.} & \textbf{CH Total} \\
    """
    scht = Carga_Horária.__symbol__ if all(list(d.CHT.horas < 0 for d in domain)) else f"{sum(list(d.CHT.get() for d in domain))}"
    schp = Carga_Horária.__symbol__ if all(list(d.CHP.horas < 0 for d in domain)) else f"{sum(list(d.CHP.get() for d in domain))}"
    schd = Carga_Horária.__symbol__ if all(list(d.CHD.horas < 0 for d in domain)) else f"{sum(list(d.CHD.get() for d in domain))}"
    sche = Carga_Horária.__symbol__ if all(list(d.CHE.horas < 0 for d in domain)) else f"{sum(list(d.CHE.get() for d in domain))}"
    stot = f"{sum(list(d.TOT for d in domain))}"
    footer_txt = r"""    \textbf{TOTAL} &  & \textbf{""" + scht + r"""} & \textbf{""" + schp + r"""} & \textbf{""" + schd + r"""} & \textbf{""" + sche + r"""} & \textbf{""" + stot + (r"$^\ast$" if hasacc else "") + r"""} \\""" if total else ""
    footer_txt += r"""
    \end{longtblr}
    """
    body_txt = ""
    for d in domain:
        body_txt += rf"    {nome_alt(d.Nome)} & {d.Codigo} & {d.CHT} & {d.CHP} & {d.CHD} & {d.CHE} & {d.TOT}" + (r"\TblrNote{$\ast$}" if hasacc and d.Codigo == "ACC" else "") + r" \\" + '\n'
    body_txt = body_txt[:-1] + r"*" + '\n'  # remove the last \\
    with open(fn, "w") as f:
        f.write(header_txt)
        f.write(body_txt)
        f.write(footer_txt)

def buildTabDisciplinasEQUIV(name:str, domain:list[Disciplina], optativas=False, filename=None, total=True):
    if filename is None:
        target = unidecode(name.replace(":", "").replace(".", "").replace(" e ", " ").replace(" de ", " ").replace(" ", "_").lower())
    else:
        target = unidecode(filename.replace(":", "").replace(".", "").replace(" e ", " ").replace(" de ", " ").replace(" ", "_").lower())
    fn = "include/auto/tab_" + target + ".tex"
    header_txt = r"""\begin{longtblr}[
        theme = ecp,
        caption = {""" + name + r"""},
        label = {tab:""" + target + r"""},"""
    if optativas:
        header_txt += r"""
        remark{\scriptsize \textbf{Nota}} = {\scriptsize As disciplinas optativas pré-aprovadas são apresentadas na \autoref{sec:optativas}.}
        """
    header_txt += r"""]{
    colspec = {Q[l,m,wd=31mm]Q[l,m,wd=19mm]Q[c,m,wd=7mm]Q[c,m,wd=7mm]Q[c,m,wd=7mm]Q[c,m,wd=7mm]Q[c,m,wd=9mm]Q[l,m,wd=31mm]},
    rowhead = 1,
    row{odd} = {bg=CinzaClaro},
    row{1} = {bg=AzulEscuro, fg=white},
    row{""" + f"{len(domain) + 2}" + r"""} = {bg=AzulClaro, fg=white},
    cells  = {font=\fontsize{9pt}{9pt}\selectfont},
    }
        \textbf{Componente} & \textbf{Código}  & \textbf{CH Teór.} & \textbf{CH Prát.}  & \textbf{CH EaD} & \textbf{CH Ext.} & \textbf{CH Total}  & \textbf{Equivale a} \\
    """
    scht = f"{sum(list(d.CHT.get() for d in domain))}" + (Carga_Horária.__symbol__ if any(list(d.CHT.horas < 0 for d in domain)) else "")
    schp = f"{sum(list(d.CHP.get() for d in domain))}" + (Carga_Horária.__symbol__ if any(list(d.CHP.horas < 0 for d in domain)) else "")
    schd = f"{sum(list(d.CHD.get() for d in domain))}" + (Carga_Horária.__symbol__ if any(list(d.CHD.horas < 0 for d in domain)) else "")
    sche = f"{sum(list(d.CHE.get() for d in domain))}" + (Carga_Horária.__symbol__ if any(list(d.CHE.horas < 0 for d in domain)) else "")
    stot = f"{sum(list(d.TOT for d in domain))}"
    footer_txt = r"""    \textbf{TOTAL} &  & \textbf{""" + scht + r"""} & \textbf{""" + schp + r"""} & \textbf{""" + schd + r"""} & \textbf{""" + sche + r"""} & \textbf{""" + stot + r"""} & \\""" if total else ""
    footer_txt += r"""
    \end{longtblr}
    """
    body_txt = ""
    for d in domain:
        print("@@@ Ementa de", d.Nome, ":", d.Ementa)
        body_txt += rf"    {nome_alt(d.Nome)} & {d.Codigo} & {d.CHT} & {d.CHP} & {d.CHD} & {d.CHE} & {d.TOT} & {d.Ementa[0] if d.Ementa else '[por tipo]'} \\" + '\n'
    body_txt = body_txt[:-1] + r"*" + '\n'  # remove the last \\
    with open(fn, "w") as f:
        f.write(header_txt)
        f.write(body_txt)
        f.write(footer_txt)


def buildTabDistr(name:str, domain:dict, nota=False):
    
    tot_che = 0
    tot = 0
    for k, v in domain.items():
        che = sum([d.CHE.get() for d in v])
        tot += sum(list(d.TOT for d in v))
        tot_che += che
        
    ch20 = 0
    if "Atividades Acadêmicas Complementares" in domain:
        ch20 += sum(list(d.TOT for d in domain["Atividades Acadêmicas Complementares"]))
        ch20 += sum(list(d.TOT for d in domain["Atividade de Conclusão de Curso"]))
    
    target = unidecode(name.replace(" e ", " ").replace(" de ", " ").replace(" ", "_").lower())
    fn = "include/auto/tab_" + target + ".tex"
    header_txt = r"""\begin{longtblr}[
        theme = ecp,
        caption = {""" + name + r"""},""" + ( r"""   remark{\scriptsize \textbf{Sobre Estágio e Atividades Complementares}} = {\scriptsize """ + f"A somatória de {ch20} horas dos componentes Atividade de Conclusão de Curso (possível Estágio Supervisionado" + r""", ver Seção~\ref{sec:acc_conclusao}) e Atividades Acadêmicas Complementares totalizam \textbf{""" + f"{100*(ch20/tot):0.1f}".replace(".",",") + r"""\%} da carga horária total do curso, respeitando o limite legal de 20\% para estágios e atividades complementares estabelecido pela legislação vigente~\cite{MEC:CNE:CES:2:2007}.}, """ if nota else r"""""" ) + r"""
        label = {tab:""" + target + r"""}
    ]{
    colspec = {Q[l,m,wd=100mm]Q[c,m,wd=20mm]Q[c,m,wd=20mm]},
    rowhead = 1,
    row{odd} = {bg=CinzaClaro},
    row{1} = {bg=AzulEscuro, fg=white},
    row{""" + f"{len(domain.keys()) + 2}" + r"""} = {bg=AzulClaro, fg=white},
    cells  = {font = \fontsize{10pt}{12pt}\selectfont}
    }
        \textbf{Componentes Curriculares} & \textbf{CH Total} & \textbf{Percentual} \\
    """
    body_txt = ""
    tot_chk = 0
    for k, v in domain.items():
        aux = sum(list(d.TOT for d in v))
        tot_chk += aux
        body_txt += rf"    {k} & {aux} & " + f"{100*(aux/tot):0.1f}".replace(".",",") + rf"\% \\" + '\n'
    body_txt = body_txt[:-1] + r"*" + '\n'  # remove the last \\
    footer_txt = r"""   \textbf{TOTAL} &  \textbf{""" + f"{tot_chk}" + r"""} & \textbf{""" + f"{100*(tot_chk/tot):0.1f}".replace(".",",") + r"""\%} \\
    \end{longtblr}
    """
    with open(fn, "w") as f:
        f.write(header_txt)
        f.write(body_txt)
        f.write(footer_txt)
        
        
    
def buildTabDistrEAD(name:str, domain:dict, percEAD:float):
    target = unidecode(name.replace(" e ", " ").replace(" de ", " ").replace(" ", "_").lower())
    fn = "include/auto/tab_" + target + ".tex"
    
    # Disciplinas Obrigatórias	0*	489	0	2445
    # Disciplinas Optativas	0	270	0	270
    # Atividades Curriculares de Extensão	0	0	345	345
    # Atividade de Conclusão de Curso	0	0	0	300
    # Atividades Acadêmicas Complementares	0	0	0	90
    # scht = f"{sum(list(d.CHT.get() for d in domain))}" + (Carga_Horária.__symbol__ if any(list(d.CHT.horas < 0 for d in domain)) else "")
    # schp = f"{sum(list(d.CHP.get() for d in domain))}" + (Carga_Horária.__symbol__ if any(list(d.CHP.horas < 0 for d in domain)) else "")
    # schd = f"{sum(list(d.CHD.get() for d in domain))}" + (Carga_Horária.__symbol__ if any(list(d.CHD.horas < 0 for d in domain)) else "")
    # sche = f"{sum(list(d.CHE.get() for d in domain))}" + (Carga_Horária.__symbol__ if any(list(d.CHE.horas < 0 for d in domain)) else "")
    # stot = f"{sum(list(d.TOT for d in domain))}"
    tot = 0
    for k, v in domain.items():
        tot += sum(list(d.TOT for d in v))
    body_txt = ""
    tot_chdmin = 0
    tot_chdmax = 0
    tot_che = 0
    tot_chtotal = 0
    for k, v in domain.items():
        chdmin = 0
        chdmax = 0
        che = sum([d.CHE.get() for d in v])
        chtotal = sum([d.TOT for d in v])
        if "OBRIGA" in k.upper():
            chdmin = sum([d.CHD.get() for d in v])
            chdmax = round(chdmin + sum([d.CHT.get() + d.CHP.get() for d in v])*percEAD)
        elif "OPTATIVAS" in k.upper():
            chdmin = 0
            chdmax = sum([d.TOT for d in v])
        tot_chdmin += chdmin
        tot_chdmax += chdmax
        tot_che += che
        tot_chtotal += chtotal
        body_txt += rf"    {k}  & {chdmin}  & {chdmax}  & {che} & {chtotal} \\" + '\n'
    body_txt = body_txt[:-1] + r"*" + '\n'  # remove the last \\
    footer_txt = r"""   \textbf{TOTAL} &  \textbf{""" + f"{tot_chdmin}" + r"""} &  \textbf{""" + f"{tot_chdmax}" + r"""} &  \textbf{""" + f"{tot_che}" + r"""} &  \textbf{""" + f"{tot_chtotal}" + r"""} \\*
        \textbf{Percentual} & \textbf{""" + f"{100*(tot_chdmin/tot):0.1f}".replace(".",",") + r"""\%} & \textbf{""" + f"{100*(tot_chdmax/tot):0.1f}".replace(".",",") + r"""\%} & \textbf{""" + f"{100*(tot_che/tot):0.1f}".replace(".",",") + r"""\%} & \textbf{""" + f"{100*(tot_chtotal/tot):0.1f}".replace(".",",") + r"""\%} \\
    \end{longtblr}
    """
    header_txt = r"""\begin{longtblr}[
        theme = ecp,
        caption = {""" + name + r"""},
        label = {tab:""" + target + r"""},
        remark{\scriptsize \textbf{Sobre EaD}} = {\scriptsize A carga horária em formato EaD mínima (CHD\textsubscript{min}) e máxima (CHD\textsubscript{max}) foi calculada considerando-se um percentual flexível de até """ + f"{100*percEAD:0.1f}".replace(".",",") + r"""\% sobre a carga horária presencial (CHT+CHP) das disciplinas obrigatórias, conforme Seção~\ref{sec:planejamento_ead}. Com isso, comprova-se que a flexibilidade de \textbf{""" + f"{100*(tot_chdmin/tot):0.1f}".replace(".",",") + r"""\%} a \textbf{""" + f"{100*(tot_chdmax/tot):0.1f}".replace(".",",") + r"""\%} de sua carga horária em formato EaD mantém-se, no melhor e no pior caso, em conformidade com o limite legal de 30\% estabelecido pela legislação vigente~\cite{Decreto:12456:2025}.},
        remark{\scriptsize \textbf{Sobre Extensão}} = {\scriptsize O curso possui \textbf{""" + f"{100*(tot_che/tot):0.1f}".replace(".",",") + r"""\%} de sua carga horária total dedicada à Extensão (CHE), em conformidade com as diretrizes e normativas vigentes~\cite{MEC:CNE:CES:7:2018,UFU:CONSUN:25:2019}.}
    ]{
    colspec = {Q[l,m,wd=72mm]Q[c,m,wd=15mm]Q[c,m,wd=15mm]Q[c,m,wd=15mm]Q[c,m,wd=15mm]},
    rowhead = 1,
    row{odd} = {bg=CinzaClaro},
    row{1} = {bg=AzulEscuro, fg=white},
    row{""" + f"{len(domain.keys()) + 2}" + r"""} = {bg=AzulClaro, fg=white},
    row{""" + f"{len(domain.keys()) + 3}" + r"""} = {bg=AzulClaro, fg=white},
    cells  = {font = \fontsize{10pt}{12pt}\selectfont},
    }
        \textbf{Componentes Curriculares} & \textbf{CHD$_{\min}$} & \textbf{CHD$_{\max}$} & \textbf{CHE} & \textbf{CH Total} \\
    """
    with open(fn, "w") as f:
        f.write(header_txt)
        f.write(body_txt)
        f.write(footer_txt)
    with open("include/auto/par_carga_horaria_total_do_curso.tex", "w") as f:
        f.write(f"{tot_chtotal}" + r"\xspace")
        

def buildTabPerPeriodo(name:str, domain:dict):
    target = unidecode(name.replace(" e ", " ").replace(" de ", " ").replace(" ", "_").lower())
    fn = "include/auto/tab_" + target + ".tex"
    
    tot = 0
    for k, v in domain.items():
        if k != "MACE":
            tot += sum(list(d.TOT for d in v))
    body_txt = ""
    tot_chk = 0
    aux = dict()
    for k, v in domain.items():
        if k != "MACE":
            aux[k] = sum(list(d.TOT for d in v))
            tot_chk += aux[k]
            # if k == "ACE":
            #     body_txt += "    " + k + r"\TblrNote{$\dagger$}" + rf" & {aux[k]//15 if not k in ['AAC', 'ACE', 'ACC'] else 'distribuída'} & {aux[k]} & " + f"{100*(aux[k]/tot):0.1f}".replace(".",",") + rf"\% \\" + '\n'
            # else:
            body_txt += rf"    {k} & {aux[k]//15 if not k in ['Optativas', 'AAC', 'ACE', 'ACC'] else 'variada'} & {aux[k]} & " + f"{100*(aux[k]/tot):0.1f}".replace(".",",") + rf"\% \\" + '\n' #mudei aqui
    
    newch = sum(d.TOT for d in domain[r"8\textordmasculine{}"]) + domain["MACE"]
    
    #   ,
        # note{$\dagger$} = {\scriptsize Se as """ + str(domain["MACE"]) + r""" horas teóricas da disciplina \textit{Memorial de Atividades Curriculares de Extensão} incluída em ACE fossem adicionadas ao 8º Período, teríamos para o mesmo um total de """ + str(newch//15) + r""" horas semanais e """ + str(newch) + r""" horas no semestre.},
    
    header_txt = r"""\begin{longtblr}[
        theme = ecp,
        caption = {Carga Horária Semanal por Período},%\protect\footnotemark[\value{footnote}]},
        label = {tab:ch_semanal_por_periodo}
    ]{
    colspec = {Q[c,m,wd=30mm]Q[c,m,wd=30mm]Q[c,m,wd=30mm]Q[c,m,wd=30mm]},
    rowhead = 1,
    row{odd} = {bg=CinzaClaro},
    row{1} = {bg=AzulEscuro, fg=white},
    row{""" + f"{len(domain.keys()) + 1}" + r"""} = {bg=AzulClaro, fg=white},
    cells  = {font = \fontsize{10pt}{12pt}\selectfont},
    } 
        \textbf{Período} & \textbf{CH Semanal (horas)} & \textbf{Total (horas)} & \textbf{Percentual} \\
    """
    
    footer_txt = r"""   \textbf{TOTAL} &  & \textbf{""" + f"{tot_chk}" + r"""} & \textbf{""" + f"{100*(tot_chk/tot):0.1f}".replace(".",",") + r"""\%} \\
    \end{longtblr}"""
    with open(fn, "w") as f:
        f.write(header_txt)
        f.write(body_txt)
        f.write(footer_txt)

def buildTabPerACM(name:str, domain:dict):
    target = unidecode(name.replace(" e ", " ").replace(" de ", " ").replace(" ", "_").lower())
    fn = "include/auto/tab_" + target + ".tex"
    header_txt = r"""\begin{longtblr}[
        theme = ecp,
        caption = {Carga Horária por Elemento de Conhecimento},%\protect\footnotemark[\value{footnote}]},
        label = {tab:ch_acm_semanal},
        note{$\ast$} = {\scriptsize A carga horária total de disciplinas de IA é de """ + f"{sum(list(d.TOT for v in domain.values() for d in v if d.PER.isnumeric() and ("inteligência" in d.Nome.lower() or "aprendiz" in d.Nome.lower() or "IA" in d.Nome.split())))}" + r""" horas.}
    ]{
    colspec = {Q[l,m,wd=80mm]Q[c,m,wd=30mm]Q[c,m,wd=30mm]},
    rowhead = 1,
    row{odd} = {bg=CinzaClaro},
    row{1} = {bg=AzulEscuro, fg=white},
    row{""" + f"{8}" + r"""} = {bg=gray, fg=white},
    row{""" + f"{len(domain.keys()) + 2 + 1}" + r"""} = {bg=gray, fg=white},
    row{""" + f"{len(domain.keys()) + 2 + 2}" + r"""} = {bg=AzulClaro, fg=white},
    cells  = {font = \fontsize{10pt}{12pt}\selectfont},
    } 
        \textbf{Conhecimento} & \textbf{Total (horas)} & \textbf{Percentual} \\
    """
    tot = 0
    for k, v in domain.items():
        tot += sum(list(d.TOT for d in v))
    body_txt = ""
    # great_tot = 0
    # for k, v in domain.items():
    #     aux = sum(list(d.TOT for d in v))
    #     great_tot += aux
    tot_chk = 0
    aux_tot = 0
    chk = False
    for k, v in domain.items():
        if k.startswith("Formação") and not chk:
            body_txt += r"""   \textbf{Subtotal} &  \textbf{""" + f"{tot_chk}" + r"""} & \textbf{""" + f"{100*(tot_chk/tot):0.1f}".replace(".",",") + r"""\%} \\"""
            aux_tot = tot_chk
            tot_chk = 0
            chk = True
        aux = sum(list(d.TOT for d in v))
        tot_chk += aux
        body_txt += rf"    {k}" + (r"\TblrNote{$\ast$}" if "Arquitetura" in k else "") + rf" & {aux} & " + f"{100*(aux/tot):0.1f}".replace(".",",") + rf"\% \\" + '\n'
        if k.startswith("Atividade de Conclusão de Curso"):
            body_txt += r"""   \textbf{Subtotal} &  \textbf{""" + f"{tot_chk}" + r"""} & \textbf{""" + f"{100*(tot_chk/tot):0.1f}".replace(".",",") + r"""\%} \\"""
            tot_chk += aux_tot
    # body_txt = body_txt[:-1] + r"*" + '\n'  # remove the last \\
    footer_txt = r"""   \textbf{TOTAL} &  \textbf{""" + f"{tot_chk}" + r"""} & \textbf{""" + f"{100*(tot_chk/tot):0.1f}".replace(".",",") + r"""\%} \\
    \end{longtblr}"""
    with open(fn, "w") as f:
        f.write(header_txt)
        f.write(body_txt)
        f.write(footer_txt)


# def buildTabCC2020(name:str, domain:dict):
#     target = unidecode(name.replace(" e ", " ").replace(" de ", " ").replace(" ", "_").lower())
#     fn = "include/auto/tab_" + target + ".tex"
#     header_txt = r"""  \begin{longtblr}[
#         theme = ecp,
#         caption = {Carga Horária Semanal por Período},%\protect\footnotemark[\value{footnote}]},
#         label = {tab:ch_semanal},
#     ]{
#     colspec = {Q[c,m,wd=30mm]Q[c,m,wd=30mm]Q[c,m,wd=30mm]Q[c,m,wd=30mm]},
#     rowhead = 1,
#     row{odd} = {bg=CinzaClaro},
#     row{1} = {bg=AzulEscuro, fg=white},"""
#     row{""" + f"{len(domain.keys()) + 2}" + r"""} = {bg=AzulClaro, fg=white},
#     header_txt += r"""cells  = {font = \fontsize{10pt}{12pt}\selectfont},
#     } 
#         \textbf{Período} & \textbf{CH Semanal (horas)} & \textbf{Total (horas)} & \textbf{Percentual} \\
#     """
    

buildTabDisciplinas(
    "Núcleo de Formação Básica", 
    sorted(list(d for d in disciplinas if d.FORM_BAS), key=lambda x:keysort(x))
)

buildTabDisciplinas(
    "Núcleo de Formação Humanística e de Extensão", 
    sorted(list(d for d in disciplinas if d.FORM_HUM), key=lambda x:keysort(x))
)

buildTabDisciplinas(
    "Núcleo de Formação Tecnológica e Profissional", 
    sorted(list(d for d in disciplinas if d.FORM_TEC), key=lambda x:keysort(x))
)

optss = sorted(list(d for d in disciplinas if d.FORM_CMP), key=lambda x:keysort(x))
optsss = [o for o in optss if o.Nome != "Optativa"]
nmb = len([o for o in optss if o.Nome == "Optativa"])
# newopt = Disciplina("Optativas", f"OPT1-{nmb}", "opt", -1, -1, -1, -1, sum([o.TOT for o in optss if o.Nome == "Optativa"]), True, False, True, "A", False, False, False, False, True, False, False, False, False, False, False, [], [])
# # Nome Codigo PER CHT CHP CHD CHE TOT FLX OBR OPT AB EXT FORM_BAS FORM_HUM FORM_TEC FORM_CMP CC_UO1 CC_SM2 CC_SAI3 CC_SD4 CC_SF5 CC_HW6 PREQ CREQ CERT
# optsss.append(newopt)

buildTabDisciplinas(
    "Núcleo de Formação Optativa e Complementar", optsss, True
)

tab_ch = dict()
tab_ch["Núcleo de Formação Básica"] = list(d for d in disciplinas if d.FORM_BAS)
tab_ch["Núcleo de Formação Tecnológica e Profissional"] = list(d for d in disciplinas if d.FORM_TEC)
tab_ch["Núcleo de Formação Humanística e de Extensão"] = list(d for d in disciplinas if d.FORM_HUM)
tab_ch["Núcleo de Formação Optativa e Complementar"] = list(d for d in disciplinas if d.FORM_CMP or (d.FLX and d.OPT))
       
buildTabDistr("Carga Horária por Núcleo de Formação", tab_ch)



tab_ch = dict()
tab_ch["Disciplinas Obrigatórias"] = list(d for d in disciplinas if d.FLX and d.OBR and not d.EXT and d.PER.isnumeric())
tab_ch["Disciplinas Optativas"] = list(d for d in disciplinas if d.FLX and d.OPT)
tab_ch["Atividades Curriculares de Extensão"] = list(d for d in disciplinas if d.FLX and d.EXT)
tab_ch["Atividade de Conclusão de Curso"] = list(d for d in disciplinas if d.PER == "acc")
tab_ch["Atividades Acadêmicas Complementares"] = list(d for d in disciplinas if d.PER == "aac")
for d in disciplinas:
    print(d.Nome, end="  ::  ")
    if d.OBR:
        print("OBR*", d.FLX, "*", d.OBR, "*", not d.EXT, "*", d.PER.isnumeric())
    if d.OPT:
        print("OPT*", d.FLX, "*", d.OPT)
    if d.EXT:
        print("EXT*", d.FLX, "*", d.EXT)
print(tab_ch)
buildTabDistr("Carga Horária por Componente Curricular", tab_ch, nota=True)

buildTabDistrEAD("EaD e Extensão por Componente Curricular", tab_ch, 0.2)

tab_ch = dict()
for i in range(1,9):
    tab_ch[f"{i}" + r"\textordmasculine{}"] = list(d for d in disciplinas if d.PER == f"{i}" and not d.EXT)
tab_ch["Optativas"] = list(d for d in disciplinas if d.PER == "opt") #mudei aqui
tab_ch["ACE"] = list(d for d in disciplinas if d.FLX and d.EXT)
tab_ch["ACC"] = list(d for d in disciplinas if d.PER == "acc")
tab_ch["AAC"] = list(d for d in disciplinas if d.PER == "aac")
tab_ch["MACE"] = sum(d.TOT for d in disciplinas if d.Codigo.endswith("MACE"))
buildTabPerPeriodo("Carga Horária Semanal por Período", tab_ch)


tab_acm = {
    "Hardware": list(d for d in disciplinas if d.CC_HW6),
    "Arquitetura e Infraestrutura de Sistemas": list(d for d in disciplinas if d.CC_SAI3),
    "Fundamentos de Software": list(d for d in disciplinas if d.CC_SF5),
    "Usuários e Organizações": list(d for d in disciplinas if d.CC_UO1),
    "Modelagem de Sistemas": list(d for d in disciplinas if d.CC_SM2),
    "Desenvolvimento de Software": list(d for d in disciplinas if d.CC_SD4),
    "Formação Matemática e Física Aplicadas à Engenharia": list(d for d in disciplinas if not(d.CC_UO1 or d.CC_SM2 or d.CC_SAI3 or d.CC_SD4 or d.CC_SF5 or d.CC_HW6) and d.FORM_BAS),
    "Formação Optativa e Complementar": list(d for d in disciplinas if not(d.CC_UO1 or d.CC_SM2 or d.CC_SAI3 or d.CC_SD4 or d.CC_SF5 or d.CC_HW6) and d.FORM_CMP),
    "Atividades Curriculares de Extensão": list(d for d in disciplinas if not(d.CC_UO1 or d.CC_SM2 or d.CC_SAI3 or d.CC_SD4 or d.CC_SF5 or d.CC_HW6) and d.FORM_HUM),
    "Atividade de Conclusão de Curso": list(d for d in disciplinas if not(d.CC_UO1 or d.CC_SM2 or d.CC_SAI3 or d.CC_SD4 or d.CC_SF5 or d.CC_HW6) and not (d.FORM_HUM or d.FORM_CMP or d.FORM_BAS)),
}
# print("*********************")
# print([w.Nome for w in tab_acm["Formação Básica (extra)"]])
# print("*********************")
buildTabPerACM("Carga Horária por Elemento de Conhecimento", tab_acm)


for c in certificados.values():
    buildTabDisciplinas(
        c.certificado, 
        sorted(list(d for d in disciplinas if c in d.CERT), key=lambda x:keysort(x))
    )
    
buildTabDisciplinas(
    "CC2020: Usuários e Organizações", 
    sorted(list(d for d in disciplinas if d.CC_UO1 and d.OBR), key=lambda x:keysort(x))
)

buildTabDisciplinas(
    "CC2020: Modelagem de Sistemas", 
    sorted(list(d for d in disciplinas if d.CC_SM2 and d.OBR), key=lambda x:keysort(x))
)

buildTabDisciplinas(
    "CC2020: Arquitetura e Infraestrutura de Sistemas", 
    sorted(list(d for d in disciplinas if d.CC_SAI3 and d.OBR and "integrador" not in d.Nome.lower()), key=lambda x:keysort(x))
)

buildTabDisciplinas(
    "CC2020: Desenvolvimento de Software", 
    sorted(list(d for d in disciplinas if d.CC_SD4 and d.OBR), key=lambda x:keysort(x))
)

buildTabDisciplinas(
    "CC2020: Fundamentos de Software", 
    sorted(list(d for d in disciplinas if d.CC_SF5 and d.OBR), key=lambda x:keysort(x))
)

buildTabDisciplinas(
    "CC2020: Hardware", 
    sorted(list(d for d in disciplinas if d.CC_HW6 and d.OBR), key=lambda x:keysort(x))
)

def representacaoGrafica(domain:dict, ch_req_acc:int):
    def getDiscEnum(codigo):
        for iv in domain.values():
            for i in iv:
                if i.Codigo == codigo:
                    aux = str(i.enum)
                    return "0" + aux if len(aux) == 1 else aux
        return ""
    def getDiscEnumExt(codigo):
        for iv in extensoes.values():
            for i in iv:
                if i.Codigo == codigo:
                    aux = str(i.enum)
                    return "0" + aux if len(aux) == 1 else aux
        return ""
    
    target = "representacao_grafica"
    fn = "include/auto/" + target + ".tex"
    
    sCHT = list(sum(i.CHT.get() for i in iv) for iv in domain.values())
    sCHP = list(sum(i.CHP.get() for i in iv) for iv in domain.values())
    sCHD = list(sum(i.CHD.get() for i in iv) for iv in domain.values())
    sCHE = list(sum(i.CHE.get() for i in iv) for iv in domain.values())
    # sTOT = list(sum(i.TOT for i in iv if not ("Extensão" in i.Nome and not "Memorial" in i.Nome)) for iv in domain.values())
    sTOT = list(sum(i.TOT for i in iv) for iv in domain.values())
    
    # extrass = {
    #     'sCHT': -1,
    #     'sCHP': -1,
    #     'sCHD': -1,
    #     'sCHE': -1,
    #     'sTOT': domain["extra"],
    # }
    
    extensoes = dict()
    for k, v in domain.items():
        aux = list()
        for i in v:
            if "Extensão" in i.Nome:
                aux.append(i)
                domain[k].remove(i)
        extensoes[i.PER] = aux
    extensoes["extra"] = []
    
    sEXT = list(sum(i.TOT for i in iv) for iv in extensoes.values())

    
    header_txt = r"""\newcommand{\ccheader}[6]{
    \begin{tikzpicture}
        \draw (-0.2,1.5) node[font=\itshape\sffamily\scriptsize, yshift=-7pt, anchor=center, align=right, text width=2ex]{};
        \draw (0,0.5) rectangle node[font=\bfseries\sffamily\scriptsize, text width=3cm, align=center]{#1Período} (3,1);
        
        \draw (0,0) rectangle node[font=\bfseries\sffamily\tiny, text width=0.75cm, align=center]{CHT} (0.6,0.5);
        \draw (0.6,0) rectangle node[font=\bfseries\sffamily\tiny, text width=0.6cm, align=center]{CHP} (1.2,0.5);
        \draw (1.2,0) rectangle node[font=\bfseries\sffamily\tiny, text width=0.6cm, align=center]{CHD} (1.8,0.5);
        \draw (1.8,0) rectangle node[font=\bfseries\sffamily\tiny, text width=0.6cm, align=center]{CHE} (2.4,0.5);
        \draw (2.4,0) rectangle node[font=\bfseries\sffamily\tiny, text width=0.6cm, align=center]{TOT} (3,0.5);
        
        \draw (0,-0.5) rectangle node[font=\bfseries\sffamily\scriptsize, text width=0.6cm, align=center]{#2} (0.6,0);
        \draw (0.6,-0.5) rectangle node[font=\bfseries\sffamily\scriptsize, text width=0.6cm, align=center]{#3} (1.2,0);
        \draw (1.2,-0.5) rectangle node[font=\bfseries\sffamily\scriptsize, text width=0.6cm, align=center]{#4} (1.8,0);
        \draw (1.8,-0.5) rectangle node[font=\bfseries\sffamily\scriptsize, text width=0.6cm, align=center]{#5} (2.4,0);
        \draw (2.4,-0.5) rectangle node[font=\bfseries\sffamily\scriptsize, text width=0.6cm, align=center]{#6} (3,0);
        
    \end{tikzpicture}
    }
    
    %\newcounter{contbloco}
    %\setcounter{contbloco}{0}

    \newcommand{\ccbloco}[9]{
    %\addtocounter{contbloco}{1}
    \begin{tikzpicture}
        \draw (0,0.5) rectangle node[font=\sffamily\scriptsize, yshift=-2pt, text width=2.8cm, align=center]{#2} (3,2.5);
        \draw (1.5,2.5) node[font=\bfseries\sffamily\scriptsize, yshift=-7pt, anchor=mid]{#1};
        \draw (0,0) rectangle node[font=\sffamily\scriptsize, text width=1cm, align=center]{#3} (0.6,0.5);
        \draw (0.6,0) rectangle node[font=\sffamily\scriptsize, text width=1cm, align=center]{#4} (1.2,0.5);
        \draw (1.2,0) rectangle node[font=\sffamily\scriptsize, text width=1cm, align=center]{#5} (1.8,0.5);
        \draw (1.8,0) rectangle node[font=\sffamily\scriptsize, text width=1cm, align=center]{#6} (2.4,0.5);
        \draw (2.4,0) rectangle node[font=\sffamily\scriptsize, text width=1cm, align=center]{#7} (3,0.5);
        \ifthenelse{\isempty{#8}}
        {
        \draw (-0.475,1.75) node[font=\sffamily\scriptsize, yshift=-7pt, anchor=center, align=right, text width=2ex]{};
        }
        {
        \draw (-0.475,1.75) node[font=\sffamily\scriptsize, yshift=-7pt, anchor=center, align=right, text width=2ex]{\textbf{#8}};
        \draw (-0.10,1.75) node[font=\sffamily\footnotesize, yshift=-7pt, anchor=mid, rotate=90]{$\boldsymbol{\blacktriangledown}$};
        }
        \ifthenelse{\isempty{#9}}
        {
        \draw (-0.475,0.5) node[font=\sffamily\scriptsize, yshift=-7pt, anchor=center, align=right, text width=2ex]{};
        }
        {
        \draw (-0.475,0.5) node[font=\sffamily\scriptsize, yshift=-7pt, anchor=center, align=right, text width=2ex]{\textbf{#9}};
        \draw (-0.30,0.5) node[font=\sffamily\footnotesize, yshift=-7pt, anchor=mid, rotate=90]{\rotatebox{180}{$\boldsymbol{\bigstar}$}};
        }
    \end{tikzpicture}
    }

    
    """
    N = max(list(int(d) for d in domain.keys() if d.isnumeric())) + 1 #extra
    up_txt = r"""
    \begin{table}
    \refstepcounter{section}
    \addcontentsline{toc}{section}{\protect\numberline{\thesection}Representação Gráfica do Fluxo Curricular}
    \centering
    \rotatebox{90}{\resizebox{0.85\pdfpageheight}{!}{
    \nohyph{}
    \begin{tabular}{||""" + "c"*(N-1) + "|c" + r"""||}
    \hline\hline
    \multicolumn{"""+ str(N) +r"""}{l}{{\fontfamily{phv}\selectfont{\scriptsize \framebox[1.1\width]{Seção~\thesection} PPC \ppcversao - Representação Gráfica:} \textbf{\nomecursonovo} / FEELT / UFU}}\\\hline
    """
        
    aux = list()
    for per in range(1, N):
        aux.append(r"\hspace*{0pt}\ccheader{" + str(per) + r"º }{" + str(sCHT[per-1]) + r"}{" + str(sCHP[per-1]) + r"}{" + str(sCHD[per-1]) + r"}{" + str(sCHE[per-1]) + r"}{" + str(sTOT[per-1]) + r"}" )
    aux.append(r"\hspace*{-4pt}\ccheader{" + "Multi-" + r"}{" + str(sCHT[-1]) + r"}{" + str(sCHP[-1]) + r"}{" + str(sCHD[-1]) + r"}{" + str(sCHE[-1]) + r"}{" + str(sTOT[-1]) + r"}" )
    tableitself = " & ".join(aux)
    tableitself += r"""\\
    """
    ##### DISCIPLINAS
    M = max(list(len(d) for d in domain.values()))
    print(M)
    for idx in range(M):
        aux = list()
        for per_ in list(range(1, N)) + ["extra"]:
            per = f"{per_}"
            if len(domain[per]) > idx:
                dscpl:Disciplina = domain[per][idx]
                preq = sorted([getDiscEnum(pr) for pr in dscpl.PREQ]) ## pré-requisito
                creq = sorted([getDiscEnum(pr) for pr in dscpl.CREQ]) ## correquisito
                enumdisc = "0" + str(dscpl.enum) if dscpl.enum < 10 else str(dscpl.enum)
                # if dscpl.Nome == "Atividade de Conclusão de Curso":
                #     # dscpl_Nome = dscpl.Nome + r"\qquad\qquad \rotatebox[origin=c]{90}{$\boldsymbol{\blacktriangledown}$} \rotatebox[origin=c]{90}{\vspace{-25mm}\textit{" + f"{ch_req_acc}" + r" horas}}"
                #     dscpl_Nome = dscpl.Nome + r"\qquad\qquad \rotatebox[origin=c]{90}{$\boldsymbol{\blacktriangledown}$} \rotatebox[origin=c]{90}{\vspace{-25mm}\textit{" + f"{ch_req_acc}" + r" horas}}"
                # else:
                dscpl_Nome = dscpl.Nome
                if preq and preq[0] == "":
                    preq = [r"\rotatebox[origin=c]{90}{\tiny " + f"{ch_req_acc} horas" + r"}"]
                aux.append(r"\ccbloco{(" + enumdisc + r")}{" + dscpl_Nome + r"}{" + str(dscpl.CHT) + r"}{" + str(dscpl.CHP) + r"}{" + str(dscpl.CHD) + r"}{" + str(dscpl.CHE) + r"}{" + str(dscpl.TOT) + r"}{" + " ".join(preq) + r"}{" + " ".join(creq) + r"}")
            else:
                aux.append(" ")
        tableitself += " & ".join(aux)
        tableitself += r""" \\
        """
    tableitself = tableitself[:-11]  # remove last \\
    sTOTAL = sum(sum(i.TOT for i in iv) for iv in domain.values()) + sum(sum(i.TOT for i in iv) for iv in extensoes.values())
    tableitself += r"""{\fontfamily{phv}\selectfont\footnotesize\textbf{CH Extensão:} """ + f"{sum(sEXT)}" + r""" horas} \\
    """
    tableitself += r"""\hline
    """
    ##### EXTENSÕES
    M = max(list(len(d) for d in extensoes.values()))
    print(M)
    for idx in range(M):
        aux = list()
        for per_ in list(range(1, N)) + ["extra"]:
            per = f"{per_}"
            if len(extensoes[per]) > idx:
                dscpl:Disciplina = extensoes[per][idx]
                preq = sorted(getDiscEnumExt(pr) for pr in dscpl.PREQ) ## pré-requisito
                creq = sorted(getDiscEnumExt(pr) for pr in dscpl.CREQ) ## correquisito
                enumdisc = "0" + str(dscpl.enum) if dscpl.enum < 10 else str(dscpl.enum)
                aux.append(r"\ccbloco{(" + enumdisc + r")}{" + dscpl.Nome + r"}{" + str(dscpl.CHT) + r"}{" + str(dscpl.CHP) + r"}{" + str(dscpl.CHD) + r"}{" + str(dscpl.CHE) + r"}{" + str(dscpl.TOT) + r"}{" + " ".join(preq) + r"}{" + " ".join(creq) + r"}")
            elif per_ == "extra":
                # aux.append(r"{\fontfamily{phv}\selectfont\footnotesize\makecell[bc]{\textbf{CH Extensão:}\\ " + f"{sum(sEXT)}" + r" horas\\ \hline\\ \textbf{CH Total:}\\ " + f"{sTOTAL}" + r" horas\\}}")
                aux.append(r"\framebox[1.1\width]{\textbf{CH Total:} " + f"{sTOTAL}" + r" horas}")
            else:
                aux.append(" ")
        tableitself += " & ".join(aux)
        tableitself += r"""\\
        """
    
    
        # aux = list()
        # for d in domain[per]:
        #     aux += [r"""
        #     \ccbloco{Computação Gráfica e Realidade Virtual e Aumentada}{30}{30}{0}{60}
        #     """]
        # tableitself += " & ".join(aux) + r" \\"
    if dscpl.PREQ or dscpl.CREQ:
        footer_txt = r"""
        \hline
        \multicolumn{""" + str(N)+ r"""}{l}{{\fontfamily{phv}\selectfont\footnotesize\textbf{Legenda:}"""
        # if dscpl.PREQ:
        footer_txt += r"""\quad \rotatebox[origin=c]{90}{$\boldsymbol{\blacktriangledown}$} Pré-requisito """
        # if dscpl.CREQ:
        footer_txt += r"""\quad \rotatebox[origin=c]{-90}{$\boldsymbol{\bigstar}$} Correquisito """
        footer_txt += rf"""\quad {Carga_Horária.__symbol__} CHT/CHP/CHD/CHE indefinidas ou definidas conforme o componente curricular escolhido""" + r"""}}\\"""
        footer_txt += r"""
            \hline\hline
        \end{tabular}
        """
    else:
        footer_txt = r"""
        \end{tabular}
        """
    footer_txt += r"""   
        }
     }
     \end{table}
     
    """
    with open(fn, "w") as f:
        # f.write(r"{\scriptsize Representação Gráfica:} \textbf{Engenharia de Computação}\\" + "\n\n")
        f.write(header_txt)
        f.write(up_txt)
        f.write(tableitself)
        f.write(footer_txt)

tabrepgraph = dict()    
to_del = list()
for per_ in range(1,11):
    per = f"{per_}"
    tabrepgraph[per] = sorted(list(d for d in disciplinas if d.PER == str(per) and (d.OBR or not (d.Nome.startswith("Opt") and d.OPT)) and not d.EXT), key=lambda x:keysort(x))
    tabrepgraph[per] += sorted(list(d for d in disciplinas if d.PER == str(per) and (not d.OBR or (d.Nome.startswith("Opt") and d.OPT)) and not d.EXT), key=lambda x:keysort(x))
    tabrepgraph[per] += sorted(list(d for d in disciplinas if d.PER == str(per) and (d.OBR or (d.Nome.startswith("Opt") and d.OPT)) and d.EXT), key=lambda x:keysort(x))
    tabrepgraph[per] += sorted(list(d for d in disciplinas if d.PER == str(per) and d.EXT), key=lambda x:keysort(x))
    if len(tabrepgraph[per]) == 0:
        to_del.append(per)
for d in to_del:
    del tabrepgraph[d]
tabrepgraph["extra"] = sorted(list(d for d in disciplinas if not d.PER.isnumeric()), key=lambda x:keysort(x))
print("*(&*(&*¨**))", [(k,v) for k,v in tabrepgraph.items()])


k = 1
for per in list(range(1,11)) + ["extra"]:
    if str(per) in tabrepgraph:
        for t in tabrepgraph[str(per)]:
            t.enum = k
            k += 1

print(tabrepgraph)
tabrepgraph["extra"] = [tabrepgraph["extra"][-1]] + tabrepgraph["extra"][:-1]
representacaoGrafica(tabrepgraph, sum([d.TOT for d in disciplinas if d.PER.isnumeric() and int(d.PER) <= PER_ACC and d.OBR]))


def buildCHInfo(name:str, text:str):
    target = unidecode(name.replace(" e ", " ").replace(" de ", " ").replace(" ", "_").lower())
    fn = "include/auto/par_" + target + ".tex"
    with open(fn, "w") as f:
        # f.write(r"{\scriptsize Representação Gráfica:} \textbf{Engenharia de Computação}\\" + "\n\n")
        f.write(text + "\n")

ch_curso = sum([d.TOT for d in disciplinas])
partxt = r"""\textbf{""" + str(ch_curso) + r""" horas}"""
buildCHInfo("Carga Horária Total", r"""\textbf{""" + str(ch_curso) + r""" horas}""")

# ch_opt = sum([d.TOT for d in disciplinas if d.OPT and d.Nome.startswith("Optativa")])
ch_opt = sum([d.TOT for d in disciplinas if d.PER == "opt"]) #mudei aqui
ch_aac = sum([d.TOT for d in disciplinas if d.PER == "aac"])
ch_acc = sum([d.TOT for d in disciplinas if d.PER == "acc"])
ch_req_acc = sum([d.TOT for d in disciplinas if d.PER.isnumeric() and int(d.PER) <= PER_ACC and d.OBR])
ch_ace = sum([d.TOT for d in disciplinas if "Extensão" in d.Nome])
partxt = r"""Note que o quadro do núcleo de formação optativa (Quadro~\ref{tab:nucleo_formacao_optativa_complementar}) elenca disciplinas que podem ser escolhidas pelo discente, sendo necessária a integralização de pelo menos \textbf{""" + str(ch_opt) + r""" horas} entre elas, além das \textbf{""" + str(ch_aac) + r""" horas} de ``Atividades Acadêmicas Complementares''."""
buildCHInfo("Estrutura Optativas e AAC", partxt)
buildCHInfo("Estrutura AAC", r"\textbf{" + f"{ch_aac} " + r"horas}, sem necessidade de pré-requisito.")

buildCHInfo("Carga Horária OPT", r"""\textbf{""" + str(ch_opt) + r""" horas}""")
buildCHInfo("Carga Horária AAC", r"""\textbf{""" + str(ch_aac) + r""" horas}""")
buildCHInfo("Carga Horária ACE", r"""\textbf{""" + str(ch_ace) + r""" horas}""")
buildCHInfo("Carga Horária ACC", r"""\textbf{""" + str(ch_acc) + r""" horas}""")
buildCHInfo("Carga Horária min ACC", r"""\textbf{""" + str(ch_req_acc) + r""" horas}""")
buildCHInfo("Equivale min ACC", str(PER_ACC+1))
ch_req_nobr = sum([d.TOT for d in disciplinas if d.PER.isnumeric() and int(d.PER) <= PER_NOBR and d.OBR])
buildCHInfo("Carga Horária min NOBR", r"""\textbf{""" + str(ch_req_nobr) + r""" horas}""")
buildCHInfo("Equivale min NOBR", f"{'º, '.join([str(x) for x in range(1, PER_NOBR)])}º e {PER_NOBR}º")




# buildTabDisciplinas(
#     "Disciplinas Optativas Pré-Aprovadas", 
#     sorted(list(d for d in optativas_equivalentes if d.OPT), key=lambda x:("".join(c for c in x.Codigo.split("!")[0] if not c.isnumeric()), *keysort(x))),
#     False, "disciplinas_optativas", total=False
# )

# buildTabDisciplinasEQUIV(
#     "Disciplinas Equivalentes Pré-Aprovadas", 
#     sorted(list(d for d in optativas_equivalentes if d.OBR), key=lambda x:("".join(c for c in x.Codigo.split("!")[0] if not c.isnumeric()), *keysort(x))),
#     False, "disciplinas_equivalentes", total=False
# )

buildTabDisciplinas(
    "Disciplinas Optativas Pré-Aprovadas", 
    sorted(list(d for d in optativas_equivalentes if d.OPT), key=lambda x:unidecode(x.Nome)),
    False, "disciplinas_optativas", total=False
)

buildTabDisciplinasEQUIV(
    "Disciplinas Equivalentes Pré-Aprovadas", 
    sorted(list(d for d in optativas_equivalentes if d.OBR), key=lambda x:unidecode(x.Nome)),
    False, "disciplinas_equivalentes", total=False
)

# DISTRIBUIÇÃO DOS CONTEÚDOS CURRICULARES COM REFERÊNCIA À EDUCAÇÃO EM RELAÇÕES ÉTNICO-RACIAIS (RESOLUÇÃO CNE/CP Nº 1/2004 E PARECER CNE/CP Nº 3/2004)

# DISTRIBUIÇÃO DOS CONTEÚDOS CURRICULARES COM REFERÊNCIA AO ENSINO DE LIBRAS (DECRETO Nº 5.626/2005)

# DISTRIBUIÇÃO DOS CONTEÚDOS CURRICULARES COM REFERÊNCIA À EDUCAÇÃO EM DIREITOS HUMANOS (RESOLUÇÃO CNE Nº 1/2012)

# DISTRIBUIÇÃO DOS CONTEÚDOS CURRICULARES COM REFERÊNCIA À EDUCAÇÃO AMBIENTAL (RESOLUÇÃO CNE Nº 2/2012)

# DISTRIBUIÇÃO DOS CONTEÚDOS CURRICULARES COM REFERÊNCIA À EDUCAÇÃO EM PREVENÇÃO A DESASTRES PARA ENGENHARIAS (LEI Nº 13.425/2017)


def buildTabDisciplinasREF(name:str, domain:list[Disciplina], referencia:str, filename=None):
    if filename is None:
        target = unidecode(name.replace(":", "").replace(".", "").replace(" e ", " ").replace(" de ", " ").replace(" ", "_").lower())
    else:
        target = unidecode(filename.replace(":", "").replace(".", "").replace(" e ", " ").replace(" de ", " ").replace(" ", "_").lower())
    fn = "include/auto/tab_" + target + ".tex"
    header_txt = r"""\begin{longtblr}[
        theme = ecp,
        caption = {""" + name + r"""},
        label = {tab:""" + target + r"""},
        remark{\small \textbf{Referência}} = {\small """ + referencia + r""".}"""
    header_txt += r"""]{
    colspec = {Q[c,m,wd=20mm]Q[l,m,wd=90mm]Q[l,m,wd=25mm]},
    rowhead = 1,
    row{odd} = {bg=CinzaClaro},
    row{1} = {bg=AzulEscuro, fg=white},
    row{""" + f"{len(domain) + 2}" + r"""} = {bg=AzulClaro, fg=white},
    cells  = {font=\fontsize{10pt}{12pt}\selectfont},
    }
        \textbf{Período} & \textbf{Componente} & \textbf{Código} \\
    """
    footer_txt = r"""
    \end{longtblr}
    """
    body_txt = ""
    for d in domain:
        d_PER = d.PER + r"\textordmasculine" if d.PER.isnumeric() else "Optativa"
        body_txt += rf"    {d_PER} & {nome_alt(d.Nome)} & {d.Codigo} \\" + '\n'
    body_txt = body_txt[:-1] + r"*" + '\n'  # remove the last \\
    with open(fn, "w") as f:
        f.write(header_txt)
        f.write(body_txt)
        f.write(footer_txt)


referencias = {
    2: ("Educação em Relações Étnico-Raciais", "etnico_raciais", "Resolução CNE/CP nº 1/2004 e Parecer CNE/CP nº 3/2004"),
    3: ("Ensino de Libras", "libras", "Decreto nº 5.626/2005"),
    4: ("Educação em Direitos Humanos", "humano", "Resolução CNE nº 1/2012"),
    5: ("Educação Ambiental", "ambiental", "Resolução CNE nº 2/2012"),
    6: ("Educação em Prevenção a Desastres para Engenharias", "desastre", "Lei nº 13.425/2017"),
}

todas = disciplinas.copy()
todas += optativas_equivalentes

for k, v in referencias.items():
    buildTabDisciplinasREF(
        "Distribuição dos Conteúdos Curriculares Referentes a " + v[0], 
        sorted(list(d for d in todas if k in d.QEXTR), key=lambda x:(int(x.PER) if x.PER.isnumeric() and int(x.PER) > 0 else 100, unidecode(x.Nome))),
        v[2], "disciplinas_ref_" + v[1]
    )
    
buildTabDisciplinasREF(
    "Distribuição dos Conteúdos Curriculares Referentes à Área de Inteligência Artificial", 
    sorted(list(d for d in todas if d.PER.isnumeric() and ("inteligência" in d.Nome.lower() or "aprendiz" in d.Nome.lower() or "IA" in d.Nome.split())), key=lambda x:(int(x.PER) if x.PER.isnumeric() and int(x.PER) > 0 else 100, unidecode(x.Nome))),
    "Disciplinas obrigatórias, existem opções entre as optativas", "disciplinas_ref_ia"
)

def buildTabDisciplinasDCN(name:str, domain:list[Disciplina], referencia:list, legal:str, base=True, filename=None):
    if filename is None:
        target = unidecode(name.replace(":", "").replace(".", "").replace(" e ", " ").replace(" de ", " ").replace(" ", "_").lower())
    else:
        target = unidecode(filename.replace(":", "").replace(".", "").replace(" e ", " ").replace(" de ", " ").replace(" ", "_").lower())
    fn = "include/auto/tab_" + target + ".tex"
    header_txt = r"""\begin{longtblr}[
        theme = ecp,
        caption = {""" + name + r"""},
        label = {tab:""" + target + r"""},
        remark{\small \textbf{Referência}} = {\small """ + legal + r""".}"""
    header_txt += r"""]{
    colspec = {Q[c,m,wd=20mm]Q[l,m,wd=50mm]Q[l,m,wd=25mm]Q[l,m,wd=40mm]},
    rowhead = 1,
    row{odd} = {bg=CinzaClaro},
    row{1} = {bg=AzulEscuro, fg=white},
    row{""" + f"{len(domain) + 2}" + r"""} = {bg=AzulClaro, fg=white},
    cells  = {font=\fontsize{10pt}{12pt}\selectfont},
    }
        \textbf{Período} & \textbf{Componente} & \textbf{Código} & \textbf{Conteúdos}\\
    """
    footer_txt = r"""
    \end{longtblr}
    """
    body_txt = ""
    for d in domain:
        dcn = d.DCN_base if base else d.DCN_tec
        d_PER = d.PER + r"\textordmasculine" if d.PER.isnumeric() else "Optativa"
        body_txt += rf"    {d_PER} & {nome_alt(d.Nome)} & {d.Codigo} & {r"{\scriptsize " + "; ".join(sorted([referencia[i] for i in dcn])) + r"}"} \\" + '\n'
    body_txt = body_txt[:-1] + r"*" + '\n'  # remove the last \\
    with open(fn, "w") as f:
        f.write(header_txt)
        f.write(body_txt)
        f.write(footer_txt)

conteudos_curriculares = "sistemas operacionais; compiladores; engenharia de software; interação humano-computador; redes de computadores; sistemas de tempo real; inteligência artificial e computacional; processamento de imagens; computação gráfica; banco de dados; dependabilidade; segurança; multimídia; sistemas embarcados; processamento paralelo; processamento distribuído; robótica; realidade virtual; automação; novos paradigmas de computação; matemática discreta; estruturas algébricas; matemática do contínuo; teoria dos grafos; análise combinatória; probabilidade e estatística; pesquisa operacional e otimização; teoria da computação; lógica; algoritmos e complexidade; linguagens formais e autômatos; abstração e estruturas de dados; fundamentos de linguagens; programação; modelagem computacional; métodos formais; análise, especificação, verificação e testes de sistemas; circuitos digitais; arquitetura e organização de computadores; avaliação de desempenho; ética e legislação; empreendedorismo; computação e sociedade; filosofia; metodologia cientifica; meio ambiente; fundamentos de administração; fundamentos de economia".split("; ") # fundamentos de linguagens = sintaxe, semântica e modelos

matematica_continuo = "cálculo, álgebra linear, equações diferenciais, geometria analítica, matemática aplicada, cálculo numérico".split(", ") # matemática aplicada = séries, transformadas

conteudos_basicos_tecnologicos = "projeto de sistemas digitais; projeto de circuitos integrados; microeletrônica e nanoeletrônica; processamento digital de sinais; comunicação de dados; sistemas de controle; automação de projeto; transdutores; teoria dos semicondutores; teoria eletromagnética; eletrônica digital; eletrônica analógica; circuitos elétricos; eletricidade; física".split("; ")

base_data = sorted([d for d in todas if d.DCN_base != []], key=lambda x:(int(x.PER) if x.PER.isnumeric() and int(x.PER) > 0 else 100, unidecode(x.Nome)))

aux_dcn = sorted(list(set(sum([d.DCN_base for d in base_data], start=[]))))
print("MISSING (BASE):", sorted(list(set(list(range(len(conteudos_curriculares)))) - set(aux_dcn))))
print("MISSING (BASE):", ";".join([conteudos_curriculares[i] for i in sorted(list(set(list(range(len(conteudos_curriculares)))) - set(aux_dcn)))]))

buildTabDisciplinasDCN(
    "Distribuição dos Conteúdos Curriculares Referentes à Formação Tecnológica e Básica para todos os Cursos de Bacharelado e de Licenciatura (DCN Computação)", 
    sorted([d for d in todas if d.DCN_base != []], key=lambda x:(int(x.PER) if x.PER.isnumeric() and int(x.PER) > 0 else 100, unidecode(x.Nome))),
    conteudos_curriculares, "Parecer CNE/CES Nº 136/2012, item 3.1",
    base=True, filename="disciplinas_ref_dcn_base"
)

tec_data = sorted([d for d in todas if d.DCN_tec != []], key=lambda x:(int(x.PER) if x.PER.isnumeric() and int(x.PER) > 0 else 100, unidecode(x.Nome)))

aux_dcn = sorted(list(set(sum([d.DCN_tec for d in tec_data], start=[]))))
print("MISSING (TECN):", sorted(list(set(list(range(len(conteudos_basicos_tecnologicos)))) - set(aux_dcn))))
print("MISSING (TECN):", ";".join([conteudos_basicos_tecnologicos[i] for i in sorted(list(set(list(range(len(conteudos_basicos_tecnologicos)))) - set(aux_dcn)))]))

buildTabDisciplinasDCN(
    "Distribuição dos Conteúdos Curriculares Referentes à Formação Tecnológica e Básica dos Cursos de Bacharelado em Engenharia de Computação (DCN Computação)", 
    sorted([d for d in todas if d.DCN_tec != []], key=lambda x:(int(x.PER) if x.PER.isnumeric() and int(x.PER) > 0 else 100, unidecode(x.Nome))),
    conteudos_basicos_tecnologicos, "Parecer CNE/CES Nº 136/2012, item 3.3",
    base=False, filename="disciplinas_ref_dcn_ecp"
)