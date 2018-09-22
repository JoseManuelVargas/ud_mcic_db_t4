import json
import itertools
import threading
import time
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename
import os

class RelationModel:
    '''
    Esta clase modela una relarion de la forma:
    R = (T,L)
    Donde R: es la relacion
    T: es el conjunto de atributos
    L: es el conjunto de dependencias funcionales
    '''
    def __init__(self):
        self.t_set = set()
        self.l_set = set()

    def saveAsJson(self, json_path: str):
        self.l_set = list(self.l_set)
        self.t_set = list(self.t_set)
        json_string = json.dumps(self.__dict__)
        with open(json_path, "w") as file:
            file.write(json_string)
        self.__convertListToSets()

    def loadSetsFromJson(self, data: dict):
        if "t_set" in data.keys():
            self.t_set = data["t_set"]
        else:
            raise Exception('No se encontró conjunto T en el archivo Json. "t_set"')
        if "l_set" in data.keys():
            self.l_set = data["l_set"]
        else:
            raise Exception('No se encontró conjunto L en el archivo Json. "l_set"')
        self.__convertListToSets()

    def __convertListToSets(self):
        self.t_set = set(self.t_set)
        self.l_set = set(tuple(element) for element in self.l_set)


def calculateAttributeClosure(attr: str, L: set):
    '''
    Este método calcula el cierre de un atributo para el
    conjunto de dependencias funcionales L por medio del algoritmo
    de cierre técnico
    l_set: conjunto de dependencias funcionales
    attr: atributo

    Retorna un conjunto con todos los atributos del cierre de attr
    '''
    l_set = L.copy()
    last_closure = set()
    current_closure = set(attr)
    while len(last_closure) < len(current_closure):
        last_closure = current_closure.copy()
        for element in l_set.copy():
            if last_closure.issuperset(element[0]):
                for character in element[1]:
                    current_closure.add(character)
                l_set.discard(element)
    return current_closure

def calculateAttributeClosure2(attr: str, L: set):
    '''
    Este método calcula el cierre de un atributo para el
    conjunto de dependencias funcionales L por medio del algoritmo
    de cierre técnico
    l_set: conjunto de dependencias funcionales
    attr: atributo

    Retorna un conjunto con todos los atributos del cierre de attr
    '''
    l_set = L.copy()
    is_closure_changed = True
    current_closure = set(attr)
    while is_closure_changed:
        is_closure_changed = False
        for element in l_set.copy():
            if current_closure.issuperset(element[0]):
                is_closure_changed = True
                for character in element[1]:
                    current_closure.add(character)
                l_set.discard(element)
    return current_closure


class IrreducibleFD:
    '''
    Esta clase calcula el conjunto de cobertura minima de las dependencias funcionales
    '''
    def __init__(self, json_path: str):
        data = dict()
        try:
            with open(json_path) as file:
                data = json.load(file)
        except Exception as ex:
            print("Error leyendo archivo . Error: " + str(ex))
            return
        self.relation = RelationModel()
        self.relation.loadSetsFromJson(data)
        if not self.__validateDependencies(self.relation.t_set, self.relation.l_set):
            raise Exception("El conjunto de dependencias L contiene atributos que no están en T")
        self.irreducible_rel = RelationModel()
        self.__calculateCanonicalCover()

    def checkEquivalenceJson(self, json_path: str):
        data = dict()
        try:
            with open(json_path) as file:
                data = json.load(file)
        except Exception as ex:
            print("Error leyendo archivo . Error: " + str(ex))
            return
        new_relation = RelationModel()
        new_relation.loadSetsFromJson(data)
        self.checkEquivalence(new_relation.l_set)

    def checkEquivalence(self, L: set):
        l_set = L.copy()
        if not self.__validateDependencies(self.relation.t_set, l_set):
            print("El conjunto L contiene atributos que no están en T")
            return False
        l_set = self.__setOneAttributeRight(l_set)
        l_set = self.__setIrreducibleAttributeLeft(l_set)
        l_set = self.__deleteRedundantFD(l_set)
        if not l_set == L:
            print("El conjunto L no es una covertura mínima")
            return False
        if not self.__generateFDfromFD(l_set, self.irreducible_rel.l_set):
            print("El conjunto L ingresado no genera al conjunto L de nuestra solución")
            return False
        if not self.__generateFDfromFD(self.irreducible_rel.l_set, l_set):
            print("El conjunto L de nuestra solución no genera al conjunto L ingresado")
            return  False
        print("Si son dependencias funcionales equivalentes")
        return True

    def __generateFDfromFD(self, L_generated: set, L_used: set):
        '''se genera el conjunto de dependencias funcionales
        L_generated usando las dependencias funcionales del conjunto
        L_used'''
        for item in L_generated:
            closure = calculateAttributeClosure2(item[0], L_used)
            if not set(item[1]).issubset(closure):
                return False
        return True


    def saveIrreducibleFD(self, json_path: str):
        self.irreducible_rel.saveAsJson(json_path)


    def __calculateCanonicalCover(self):
        self.irreducible_rel.t_set = self.relation.t_set.copy()
        self.irreducible_rel.l_set = self.__setOneAttributeRight(self.relation.l_set)
        self.irreducible_rel.l_set = self.__setIrreducibleAttributeLeft(self.irreducible_rel.l_set)
        self.irreducible_rel.l_set = self.__deleteRedundantFD(self.irreducible_rel.l_set)

    def __validateDependencies(self, T: set, L: set):
        for item in L:
            if len(item) == 2:
                for character in item[0]:
                    if character not in T:
                        return False
                for character in item[1]:
                    if character not in T:
                        return False
            else:
                return False
        return True


    def __setOneAttributeRight(self, L: set):
        """
            ("fd[0]", "fd[1]")
        """
        func_dep = L.copy()
        for fd in func_dep.copy():
            if fd:
                if len(fd[1]) < 1:
                    func_dep.discard(fd)
                else:
                    if set(fd[1]).issubset(set(fd[0])):
                        func_dep.discard(fd)
                    else:
                        func_dep.discard(fd)
                        for character in fd[1]:
                            if not set(character).issubset(set(fd[0])):
                                func_dep.add((fd[0], character))
            else:
                func_dep.discard(df)
        return func_dep


    def __setIrreducibleAttributeLeft(self, L: set):
        func_dep = L.copy()
        l_set = set()
        self.closure_dict = {}
        for element in func_dep:
            if len(element[0]) == 1:
                l_set.add(element)
            elif len(element[0]) > 1:
                new_fd = self.__deleteExtraneousAttributes(L, element)
                if new_fd:
                    l_set.add(new_fd)
        return  l_set


    def __deleteExtraneousAttributes(self, L: set, func_dep: tuple):
        is_irreducible = False
        while not is_irreducible:
            func_dep_copy = func_dep
            is_irreducible = True
            for character in func_dep_copy[0]:
                new_implicating = str(func_dep_copy[0]).replace(character, '')
                if new_implicating not in self.closure_dict:
                    self.closure_dict[new_implicating] = calculateAttributeClosure2(new_implicating, L)
                if func_dep_copy[1] in self.closure_dict[new_implicating]:
                    func_dep = (func_dep[0].replace(character, ''), func_dep[1])
                    if len(func_dep[0]) == 1:
                        break
                    is_irreducible = False
        return func_dep

    def __deleteRedundantFD(self, L: set):
        l_copy = L.copy()
        for element in L:
            l_copy.discard(element)
            closure = calculateAttributeClosure2(element[0], l_copy)
            if element[1] not in closure:
                l_copy.add(element)
        return l_copy

class CandidatesKeys:
    '''
    Esta clase calcula las llaves candidatas
    dado un conjunto de relaciones. R (T,L).
    Para ello hace uso de la clase IrreducibleFD, para
    obtener el conjunto de cobertura mínima.

    Se recomienda la siguiente página para realizar pruebas:
        http://raymondcho.net/RelationalDatabaseTools/RelationalDatabaseTools
    '''
    def __init__(self, json_path: str):
        self.minimal_cover = IrreducibleFD(json_path)
        self.setAttributeSets()
        if self.checkPrimaryKey():
            print("Se encontró una llave primaria: {0}".format(self.necessary_attr_set))
            self.candidate_keys = set()
            self.candidate_keys.add(''.join(self.necessary_attr_set))
            return
        self.calculateCandidateKeys()


    def setAttributeSets(self):
        self.left_attr_set = set()
        self.right_attr_set = set()
        for item in self.minimal_cover.irreducible_rel.l_set:
            for character in item[0]:
                self.left_attr_set.add(character)
            for character in item[1]:
                self.right_attr_set.add(character)
        self.necessary_attr_set = self.minimal_cover.relation.t_set.difference(self.right_attr_set)
        self.useless_attr_set = self.minimal_cover.relation.t_set.difference(self.left_attr_set)
        self.useless_attr_set = self.useless_attr_set.difference(self.necessary_attr_set)
        aux_set = self.useless_attr_set.union(calculateAttributeClosure2("".join(self.necessary_attr_set), self.minimal_cover.irreducible_rel.l_set))
        self.middle_attr_set = self.minimal_cover.relation.t_set.difference(aux_set)

    def checkPrimaryKey(self):
        necessary_closure = calculateAttributeClosure2("".join(self.necessary_attr_set), self.minimal_cover.irreducible_rel.l_set)
        if necessary_closure == self.minimal_cover.relation.t_set:
            return True
        return  False

    def calculateCandidateKeys(self):
        self.middle_attr_list = list(self.middle_attr_set)
        level_num = len(self.middle_attr_set)
        self.candidate_keys = set()
        self.necessary_attr_str = ''.join(self.necessary_attr_set)
        thread_list = []
        max_thread_len = 4
        for i in range(level_num):
            for j in range(len(self.middle_attr_list)):
                if len(thread_list) >= max_thread_len:
                    is_any_thread_finished = False
                    while not is_any_thread_finished:
                        for ck_thread in thread_list:
                            if not ck_thread[0].is_alive():
                                thread_list.pop(ck_thread[1])
                                is_any_thread_finished = True
                                break
                        time.sleep(0.001)
                new_thread = threading.Thread(target=self.getKeysAtLevel, kwargs={"level_num": i, "attr_index": j})
                thread_list.append((new_thread, len(thread_list)))
                new_thread.start()
        for ck_thread in thread_list:
            ck_thread[0].join()
                #self.getKeysAtLevel(level_num=i, attr_index=j)

    def getKeysAtLevel(self, level_num: int, attr_index: int):
        middle_attr_copy = self.middle_attr_list[:]
        attr = middle_attr_copy.pop(attr_index)
        base_attr = self.necessary_attr_str + attr
        if self.checkIsSupperKey(set(base_attr)):
            return
        attr_list = [base_attr]
        for char in middle_attr_copy:
            attr_list.append(char)
        for combination in itertools.combinations(attr_list, level_num + 1):
            if base_attr in combination:
                if not self.checkIsSupperKey(set(combination)):
                    combination_str = ''.join(combination)
                    attr_closure = calculateAttributeClosure2(combination_str, self.minimal_cover.irreducible_rel.l_set)
                    if attr_closure == self.minimal_cover.relation.t_set:
                        self.candidate_keys.add(combination_str)

    def checkIsSupperKey(self, key: set):
        for item in self.candidate_keys:
            if key.issubset(item):
                return True
        return False

class NormalFormsChecker:
    def __init__(self, json_path: str):
        self.candidates_keys = CandidatesKeys(json_path)
        #self.l_set = self.candidates_keys.minimal_cover.irreducible_rel.l_set.copy()
        self.l_set = self.candidates_keys.minimal_cover.relation.l_set.copy()
        self.is_2nf = self.check2NF()
        if not self.is_2nf:
            print("La relación no cumple 2 FN. Por lo tanto tampoco 3 FN ni FNBC")
            self.is_3nf = False
            self.is_bc_nf = False
            return
        print("La relación cumple 2 FN")
        self.is_3nf = self.check3NF()
        if not self.is_3nf:
            print("La relación no cumple 3 FN. Por lo tanto tampoco FNBC")
            self.is_bc_nf = False
            return
        print("La relación cumple 3 FN")
        self.is_bc_nf = self.checkBCNF()
        if not self.is_bc_nf:
            print("La relación no cumple FNBC")
        else:
            print("La relación cumple FNBC")

    def check2NF(self):
        for element in self.l_set:
            for character in element[0]:
                new_element = element[0].replace(character, "")
                closure = calculateAttributeClosure2(new_element, self.l_set)
                if set(element[1]).issubset(closure):
                    return False
        return True

    def check3NF(self):
        for candidate_key in self.candidates_keys.candidate_keys:
            no_keys_set = self.candidates_keys.minimal_cover.relation.t_set.difference(set(candidate_key))
            for attr in no_keys_set:
                closure = calculateAttributeClosure2(attr, self.l_set)
                if closure.intersection(no_keys_set.difference(set(attr))):
                    return False
        return True

    def checkBCNF(self):
        for candidate_key in self.candidates_keys.candidate_keys:
            for element in self.l_set:
                if not set(candidate_key).issubset(set(element[0])):
                    return False
        return True

class NormalFormsGUI:
    def __init__(self):
        self.root = Tk()
        self.root.title("Normal Forms")
        self.mainframe = ttk.Frame(self.root, padding="3 3 12 12")
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.rowconfigure(0, weight=1)
        self.last_init_dir = "C:/Users/Estudiantes/Documents"

        self.file_name = StringVar()
        self.nf_list = ["2 FN", "3 FN", "BC NF"]
        self.nf_choice = StringVar()
        self.message = StringVar()
        self.input_option = IntVar()
        self.manual_lset = StringVar()
        self.manual_tset = StringVar()

        ttk.Label(self.mainframe, text="Choose input option:").grid(column=1, row=1, sticky=W)

        radiobtn_file = ttk.Radiobutton(self.mainframe, text="From File", variable=self.input_option, value=1, command=self.onRadioBtnClic)
        radiobtn_file.grid(column=1, row=2, columnspan=1, sticky=(W, E))

        radiobtn_manual = ttk.Radiobutton(self.mainframe, text="Manuel Input", variable=self.input_option, value=2, command=self.onRadioBtnClic)
        radiobtn_manual.grid(column=2, row=2, columnspan=1, sticky=(W, E))

        self.input_option.set(1)

        ttk.Label(self.mainframe, text="From file input:").grid(column=2, row=3, sticky=W)

        file_entry = ttk.Entry(self.mainframe, width=7, textvariable=self.file_name, state="readonly")
        file_entry.grid(column=2, row=4, columnspan=2, sticky=(W, E))
        ttk.Label(self.mainframe, text="File name:").grid(column=1, row=4, sticky=W)

        ttk.Label(self.mainframe, text="Manual input:").grid(column=2, row=5, sticky=W)

        ttk.Label(self.mainframe, text="Write L set in this way: ABC->D,BE->F,AB->E. Here we have \nthree functional dependencies.").grid(column=1, row=6, columnspan=2, sticky=W)
        self.manual_entry_lset = ttk.Entry(self.mainframe, width=10, textvariable=self.manual_lset)
        self.manual_entry_lset.grid(column=1, row=7, columnspan=2, sticky=(W, E))

        ttk.Label(self.mainframe,text="Write T set in this way: ABCDEF. Here we have six attributes.").grid(column=1, row=8, columnspan=2, sticky=W)
        self.manual_entry_tset = ttk.Entry(self.mainframe, width=10, textvariable=self.manual_tset)
        self.manual_entry_tset.grid(column=1, row=9, columnspan=2, sticky=(W, E))

        fn_entry = OptionMenu(self.mainframe, self.nf_choice, *self.nf_list, command=self.resetMessage)
        fn_entry.grid(column=2, row=10, columnspan=2, sticky=(W, E))
        ttk.Label(self.mainframe, text="Choose Normal Form:").grid(column=1, row=10, sticky=W)
        self.nf_choice.set(self.nf_list[0])

        ttk.Button(self.mainframe, text="Check", command=self.onCheckClic).grid(column=1, row=11, sticky=W)
        self.examine_btn = ttk.Button(self.mainframe, text="Examine", command=self.onExamineClic)
        self.examine_btn.grid(column=3, row=11, sticky=E)

        self.onRadioBtnClic()

        ttk.Label(self.mainframe, textvariable=self.message).grid(column=1, row=12, columnspan=3, sticky=(W, E))

        for child in self.mainframe.winfo_children():
            child.grid_configure(padx=15, pady=15)

        file_entry.focus()
        self.root.bind('<Return>', self.onCheckClic)

        self.root.mainloop()

    def onRadioBtnClic(self):
        if self.input_option.get() == 1:
            self.manual_entry_lset.configure(state=DISABLED)
            self.manual_entry_tset.configure(state=DISABLED)
        elif self.input_option.get() == 2:
            self.manual_entry_lset.configure(state=NORMAL)
            self.manual_entry_tset.configure(state=NORMAL)
        else:
            self.input_option.set(1)

    def onCheckClic(self):
        if self.input_option.get() == 1:
            file_name = self.file_name.get()
        elif self.input_option.get() == 2:
            if not self.manual_lset.get():
                self.message.set("Debe ingresar información válida en la caja de L set.")
                return
            if not self.manual_tset.get():
                self.message.set("Debe ingresar información válida en la caja de T set.")
                return
            l_set = set()
            t_set = set()
            try:
                for char in self.manual_tset.get():
                    if char.isalpha():
                        t_set.add(char.upper())
                str_split_comma = self.manual_lset.get().split(",")
                for word in str_split_comma:
                    fd = ["", ""]
                    str_split_arrow = word.split("->")
                    if len(str_split_arrow) != 2:
                        self.message.set("Debe ingresar información válida en la caja de L set. Error en la DF " + word)
                        return
                    for i in range(2):
                        for char in str_split_arrow[i]:
                            if char.isalpha():
                                fd[i] += char.upper()
                    l_set.add(tuple(fd))
            except Exception:
                self.message.set("Debe ingresar información válida en la caja de L set y T set.")
                return
            relation = RelationModel()
            relation.l_set = l_set
            relation.t_set = t_set
            file_name = "json/temp.json"
            relation.saveAsJson(file_name)
        else:
            self.input_option.set(1)
            self.onRadioBtnClic()
            return
        if file_name:
            try:
                normal_forms = NormalFormsChecker(file_name)
                if self.nf_choice.get() == self.nf_list[0]:
                    if normal_forms.is_2nf:
                        self.message.set("Está en 2 Forma Normal")
                    else:
                        self.message.set("NO Está en 2 Forma Normal")
                elif self.nf_choice.get() == self.nf_list[1]:
                    if normal_forms.is_3nf:
                        self.message.set("Está en 3 Forma Normal")
                    else:
                        self.message.set("NO Está en 3 Forma Normal")
                elif self.nf_choice.get() == self.nf_list[2]:
                    if normal_forms.is_bc_nf:
                        self.message.set("Está en Boyce-Codd Forma Normal")
                    else:
                        self.message.set("NO Está en Boyce-Codd Forma Normal")
                else:
                    self.message.set("Not a valid normal form")
            except Exception as ex:
                self.message.set("It was not possible to open the file " + str(ex))
        else:
            self.message.set("Not file found")

    def onExamineClic(self):
        file_name = askopenfilename(initialdir=self.last_init_dir,
                           filetypes =(("JSONFile", "*.json"),("All Files","*.*")),
                           title = "Choose a file.")
        self.last_init_dir = os.path.split(file_name)[0]
        if self.input_option.get() == 1:
            self.file_name.set(file_name)
        elif self.input_option.get() == 2:
            relation = RelationModel()
            try:
                data = dict()
                with open(file_name) as file:
                    data = json.load(file)
                relation.loadSetsFromJson(data)
                self.manual_lset.set("")
                self.manual_tset.set(''.join(relation.t_set))
                l_set = ""
                for fd in relation.l_set:
                    l_set += "," + fd[0] + "->" + fd[1]
                self.manual_lset.set(l_set[1:])
            except Exception as ex:
                self.message.set("El archivo no continue información válida")
        else:
            self.input_option.set(1)
            self.onRadioBtnClic()



    def resetMessage(self, value):
        self.message.set("")

if __name__ == "__main__":
    wgui = NormalFormsGUI()


