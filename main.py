from flet import *
import flet as ft
import sqlite3
from datetime import datetime
from flet_route import Routing,path, Params, Basket


class App():
    def __init__(self):
        # variaveis do banco
        self.conn=sqlite3.connect('database.db', check_same_thread=False) #
        self.cur = self.conn.cursor()
            
    def main(self, page: ft.Page, params: Params, basket: Basket):
        self.page = page
        print(params,basket, ' para e bask do main')
        return ft.View(
            route='/',
            adaptive=True,
            controls=[Column([
                Row([]),
                Row([ElevatedButton('Banquinho', on_click=lambda _:page.go('/login'))]),#Banquinho
                ]),
                Column([
                Row([]),#saude financeira
                Row([]),#anotação segura
                Row([])
                ])]
            )
class Nacha:
    def build(self,page: ft.Page, params: Params, basket: Basket):
        return ft.View(
            route='/erro404',
            controls=[
                ft.Text("Pagina não encontrada")

            ]
        )
