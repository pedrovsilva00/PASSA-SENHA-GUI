import flet as ft
from flet_route import Routing,path, Params, Basket
from banco import Banquinho,Log_pass
from main import App,Nacha
from happy_money import Money

def route(page: ft.Page,):
    page.theme_mode='light'
    page.scroll = 'auto'
    app_routes = [
        path(
            url="/", # Here you have to give that url which will call your view on mach
            clear=False, # If you want to clear all the routes you have passed so far, then pass True otherwise False.
            view=App().main # Here you have to pass a function or method which will take page,params and basket and return ft.View (If you are using class based view then you have to pass method name like IndexView().view .)
            ),
        path(url='/login',clear=True,view=Log_pass().view),
        path(url="/banco", clear=False, view=Banquinho().main_banco),
        ]

    icon_home =ft.IconButton(ft.icons.HOME, on_click=lambda _:page.go('/'))
    appbar = ft.AppBar(
            leading=icon_home,
            leading_width=40,
            title=ft.Text("Meu App"),
            center_title=False,
            bgcolor=ft.colors.SURFACE_VARIANT,
            actions=[
                #ft.Text(my_id),
                
                ft.PopupMenuButton(
                    items=[
                        ft.PopupMenuItem(text="Conta",on_click=lambda _:page.go("/")),
                        ft.PopupMenuItem(text="Configurações"),
                        ft.PopupMenuItem(text='Estatisticas'), 
                        ft.PopupMenuItem(text='Sair')
                ])
        ])
    Routing(
            page=page, # Here you have to pass the page. Which will be found as a parameter in all your views
            app_routes=app_routes, # Here a list has to be passed in which we have defined app routing like app_routes
            appbar=appbar,
            not_found_view=Nacha().build

        )
    page.go(page.route)

ft.app(target=route)#view=ft.AppView.WEB_BROWSER modo web
