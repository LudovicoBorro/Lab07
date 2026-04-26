import flet as ft
from UI.view import View
from model.model import Model

class Controller:
    def __init__(self, view: View, model: Model):
        # the view, with the graphical elements of the UI
        self._view = view
        # the model, which implements the logic of the program and holds the data
        self._model = model
        # other attributes
        self._mese = 0
        self._n_soluzioni = 0
        self._chiamate = 0
        self._soluzioni = []

    def handle_umidita_media(self, e):
        self._view.lst_result.controls.clear()

        if self._view.dd_mese.value is None:
            self._view.create_alert("Inserire un mese!")
            return

        medie = self._model.calcolo_umidita_media(int(self._view.dd_mese.value))

        self._view.lst_result.controls.append(
            ft.Text("L'umidità media nel mese selezionato è:")
        )
        for citta, m in medie.items():
            self._view.lst_result.controls.append(
                ft.Text(f"{citta}: {m:.4f}")
            )
        self._view.update_page()

    def handle_sequenza(self, e):
        self._view.lst_result.controls.clear()

        if self._view.dd_mese.value is None:
            self._view.create_alert("Inserire un mese!")
            return

        best_cost, best_sol = self._model.get_best_solution(int(self._view.dd_mese.value), 15)

        self._view.lst_result.controls.append(
            ft.Text(f"La sequenza ottima ha costo {best_cost} ed è:")
        )
        for sit in best_sol:
            self._view.lst_result.controls.append(
                ft.Text(sit)
            )
        self._view.update_page()

    def read_mese(self, e):
        self._mese = int(e.control.value)