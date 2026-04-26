from time import time

from database.meteo_dao import MeteoDao
import copy

class Model:
    def __init__(self):
        self._situazioni = {}
        self.get_all_situazioni()
        self._n_soluzioni = 0
        self._chiamate = 0
        self._soluzioni = []

    def get_all_situazioni(self):
        situazioni = MeteoDao.get_all_situazioni()

        for s in situazioni:
            self._situazioni[(s.localita, s.data)] = s

    def calcolo_umidita_media(self, mese: int):
        localita = ["Genova", "Torino", "Milano"]
        medie = []

        for loc in localita:
            somma_um = 0
            cont = 0
            for s in self._situazioni.values():
                if s.data.month == mese and loc == s.localita:
                    somma_um += s.umidita
                    cont += 1
            medie.append(somma_um / cont)
        return {"Genova": medie[0],
                "Torino": medie[1],
                "Milano": medie[2]}

    @staticmethod
    def get_first_days(mese: int, giorni: int):
        situazioni = MeteoDao.get_all_situazioni()

        situazioni_sorted = sorted(situazioni, key=lambda x: x.data)
        situazioni_filtered = []

        giorni_list = list(range(1, giorni+1))

        for i in range(len(situazioni_sorted)):
            if situazioni_sorted[i].data.month == mese and situazioni_sorted[i].data.day in giorni_list:
                situazioni_filtered.append(situazioni_sorted[i])

        return situazioni_filtered

    def get_best_solution(self, mese, giorni):
        situazioni_x_giorni = self.get_first_days(mese, giorni)

        situazioni_sorted = sorted(situazioni_x_giorni, key=lambda x: x.data)
        giorni_rimanenti = set(s.data for s in situazioni_sorted)
        giorni_rim_sorted = sorted(list(giorni_rimanenti), key=lambda x: x)
        self._n_soluzioni = 0
        self._chiamate = 0
        self._soluzioni = []
        start_time = time()
        self._ricorsione([], giorni_rim_sorted, giorni)
        end_time = time()
        print(f"Chiamate effettuate: {self._chiamate}")
        print(f"Soluzioni trovate: {self._n_soluzioni}")
        print(f"Elapsed time: {end_time- start_time}")
        best_solution = self._compute_best()
        return best_solution

    def _ricorsione(self, parziale, rimanenti, giorni):
        self._chiamate += 1
        # Caso terminale
        if len(parziale) == giorni:
            if self._is_parziale_valid(parziale) and self._step_is_valid(parziale):
                self._n_soluzioni += 1
                self._soluzioni.append(copy.deepcopy(parziale))
                print(parziale)
        # Caso ricorsivo
        else:
            for c in ["Genova", "Milano", "Torino"]:
                if len(parziale) == 0 or self._citta_is_valid(soluzione_potenziale=parziale, citta=c):
                    parziale.append((c, rimanenti[0]))
                    if not self._is_parziale_valid(parziale):
                        parziale.pop()
                        continue
                    nuovi_rimanenti = rimanenti[1:]
                    self._ricorsione(parziale, nuovi_rimanenti, giorni)
                    parziale.pop()

    @staticmethod
    def _is_parziale_valid(possibile_soluzione):
        # In nessuna città si possono trascorre più di 6 giornate
        for c in ["Genova", "Torino", "Milano"]:
            counter = 0
            for (citta, data) in possibile_soluzione:
                if citta == c:
                    counter += 1
            if counter > 6:
                return False
        return True

    @staticmethod
    def _step_is_valid(soluzione_parziale):
        # In una città bisogna stare almeno 3 giorni consecutivi
        # Prendo l'ultimo indice della soluzione_parziale,
        # ciclo su tutti gli ultimi elementi. Conto quanti elementi sono uguali,
        # se sono meno di 3 return False, altrimenti resetto il contatore e
        # conto il prossimo gruppo.
        # altrimenti return True
        count_uguali = 0
        elemento_da_paragonare = soluzione_parziale[0][0]
        for i, (element, data) in enumerate(soluzione_parziale[0 : len(soluzione_parziale)]):
            if element == elemento_da_paragonare:
                count_uguali += 1
            else:
                if count_uguali < 3:
                    return False
                else:
                    count_uguali = 1
                    elemento_da_paragonare = element
        if count_uguali < 3:
            return False
        return True

    @staticmethod
    def _citta_is_valid(soluzione_potenziale, citta):
        # Questa funzione controlla che la città che voglio inserire
        # sia valida. Se ho inserito ad esempio due Genova e ora sto per
        # inserire Milano, evito di farlo e taglio un branch di esplorazione
        if len(soluzione_potenziale) < 3:
            if citta != soluzione_potenziale[0][0]:
                return False
        elif len(soluzione_potenziale) >= 3:
            ultimi_elementi = soluzione_potenziale[-3:]
            count_uguali = 0
            for (elem, data) in ultimi_elementi:
                if elem == citta:
                    count_uguali += 1
            # Conto quanti degli ultimi 3 elementi sono uguali alla citta.
            # Se ho meno di tre elementi uguali, quindi 1 o 2 o 0, devo
            # controllare che se è uno solo, che sia in ultima posizione,
            # se sono due devo controllare che siano nelle ultime due posizioni,
            # se sono 0 devo controllare che gli ultimi 3 siano uguali per
            # poter inserire la citta
            if count_uguali == 0:
                cont = 0
                for (elem, data) in ultimi_elementi:
                    if elem == ultimi_elementi[-3][0]:
                        cont += 1
                if cont < 3:
                    return False
            elif count_uguali == 1:
                if citta != ultimi_elementi[-1][0]:
                    return False
            elif count_uguali == 2:
                if citta != ultimi_elementi[-1][0] or citta != ultimi_elementi[-2][0]:
                    return False
        return True

    def _compute_best(self):
        costi_soluzioni = []
        for soluzione in self._soluzioni:
            costo_soluzione = 0
            situazioni = []
            for i, (citta, data) in enumerate(soluzione):
                situazione = self._situazioni.get((citta, data))
                if i != 0:
                    if citta != soluzione[i-1][0]:
                        costo_soluzione += 100
                costo_soluzione += situazione.umidita
                situazioni.append(situazione)
            costi_soluzioni.append((costo_soluzione, situazioni))
        costi_sorted = sorted(costi_soluzioni, key=lambda x: x[0])
        best = costi_sorted[0]
        return best[0], best[1]     # Ritorno il costo minimo e la rispettiva soluzione