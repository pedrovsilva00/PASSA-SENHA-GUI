from flet import *
import flet as ft
import sqlite3
import random,string
from flet_route import Params,Basket
import hashlib
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

#Aqui sera toda a pagina do banquinho
class Banquinho():
    def __init__(self):
        self.conn=sqlite3.connect('database.db', check_same_thread=False) #
        self.cur = self.conn.cursor()
        #variaveis ambiente
        self.conta = ''
        self.email = ''
        self.senha = ''
        self.grupo = ''
        self.pesq = ''
        #variavies card input conta
        in_conta = TextField(label='Conta',on_change=self.set_value)
        in_email = TextField(label='Email',on_change=self.set_value)
        self.in_senha = TextField(label='Senha',on_change=self.set_value)
        in_grupo = TextField(label='Grupo',on_change=self.set_value)
        self.inputcon = Card(
            offset=transform.Offset(2,0),
            animate_offset=animation.Animation(600,curve='easyIn'),
            elevation=30,
            content=Container(
                bgcolor='green200',
                content=Column([
                    Row([
                        Text('Nova Conta',size=20,weight='bold'),
                        IconButton(icon='close',icon_size=30, on_click=self.hidecon),
                    ]),
                    in_conta,
                    in_email, 
                    Row([self.in_senha,IconButton(icon=icons.REFRESH, on_click=self.gera_pass)]),
                    in_grupo, 
                    FilledButton('Salvar dados', on_click=self.db_add)
                ])
            )
        )

        #Pesquisa variaveis
        self.op = ''
        self.in_search = TextField(label='Pesquisa',on_change=self.set_value)
        self.drop = ft.Dropdown(
            width=200,
            on_change=self.set_value,
            options=[
                ft.dropdown.Option("conta",data=0),
                ft.dropdown.Option("grupo",data=1),
            ],
        )
        self.b_search = FilledButton('Pesquisar', on_click=self.search)
        #variaveis de edição
        self.id_edit = Text()
        self.conta_edit = TextField(label='Conta')
        self.email_edit = TextField(label='Email')
        self.senha_edit = TextField(label='Senha')
        self.grupo_edit = TextField(label='Grupo')
        self.dlg = Container(
            visible=False,
            bgcolor='green200',
            padding=10,
            content=Column([
                Row([
                    Text(
                        'Editar dados ',
                        size=20,
                        weight='bold'
                    ),
                    IconButton(
                        icon='close', 
                        on_click=self.hidedlg
                    )], alignment='spaceBetween'),
                self.conta_edit,
                self.email_edit,
                Row([self.senha_edit,IconButton(icon=icons.REFRESH, on_click=self.gera_pass)]),
                self.grupo_edit,
                ElevatedButton(
                    'Atualizar',
                    on_click=self.updateandsave
                ),
            ])
        )
        self.tb=DataTable(
            columns=[
                ft.DataColumn(ft.Text('Ações')),
                ft.DataColumn(ft.Text('Conta')),
                ft.DataColumn(ft.Text('Email',tooltip='Usuario')),
                ft.DataColumn(ft.Text('Senha')),
                ft.DataColumn(ft.Text('Grupo')),
                ],
            rows=[]
        )
        self.mytable = Column([
            self.dlg,
            Row([self.tb],scroll='always')
            ])

    def generate_key(password):
        return hashlib.sha256(password.encode()).digest()

    def encry(d,p):
        key = Banquinho.generate_key(p)
        iv = b'\xdf\x9e>\r\xfc\x82y\x14&\xd4pc0 \xa6\x8c'  # IV fixo (16 bytes para AES)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        while len(d) % 16 != 0:  # Prepara os dados (padding se necessário)
            d += ' '
        encrypted = encryptor.update(d.encode()) + encryptor.finalize()
        return base64.b64encode(encrypted).decode()

    def decry(encrypted_data,p):
        key = Banquinho.generate_key(p)
        iv = b'\xdf\x9e>\r\xfc\x82y\x14&\xd4pc0 \xa6\x8c'  # IV fixo
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted = decryptor.update(base64.b64decode(encrypted_data)) + decryptor.finalize()
        return decrypted.decode().rstrip()  # Remove padding

    def search(self,e):
        try:
            if not self.pesq:
                self.page.snack_bar  = SnackBar(
                    ft.Text(f'Sem dado de pesquisa'),
                    bgcolor='red')
                self.page.snack_bar.open=True
                self.page.update()
            elif not self.op:
                self.page.snack_bar  = SnackBar(
                    ft.Text(f'Falta escolher o tipo de pesquisa'),
                    bgcolor='red')
                self.page.snack_bar.open=True
                self.page.update()
            elif self.pesq == 'all':
                self.cur.execute(f'SELECT * FROM passbank ')
                m = self.cur.fetchall()
                self.tb.rows.clear()
                self.calldb(m)
                self.tb.update()
                self.pesq = ''
                self.in_search.value = ''
                self.page.update()
            elif self.op == 'conta':
                cc = Banquinho.encry(self.pesq,key)
                print('cry pesq conta: ',cc)
                self.cur.execute(f"SELECT * FROM passbank WHERE conta=(?)",(cc,))
                m = self.cur.fetchall()
                self.tb.rows.clear()
                self.calldb(m)
                self.tb.update()
                self.pesq = ''
                self.in_search.value = ''
                #self.page.update()
            elif self.op == 'grupo':
                cc = Banquinho.encry(self.pesq,key)
                print('cry pesq grupo: ',cc)
                self.cur.execute(f"SELECT * FROM passbank WHERE grupo=(?)",(cc,))
                m = self.cur.fetchall()
                self.tb.rows.clear()
                self.calldb(m)
                self.tb.update()
                self.pesq = ''
                self.in_search.value = ''
                #self.page.update()
            else: 
                self.page.snack_bar  = SnackBar(
                    ft.Text(f'Dados nao encontrados'),
                    bgcolor='green')
                self.page.snack_bar.open=True
                self.page.update()
        except Exception as err: 
            self.page.snack_bar  = SnackBar(
                    ft.Text(f'Deu um erro na pesquisa: ', err),
                    bgcolor='red')
            self.page.snack_bar.open=True
            self.page.update()

    def set_value(self,e): # setar valor do input pras variaveis globais
        if e.control.label == "Conta":
            self.conta = e.control.value
            e.control.value =''
        elif e.control.label == "Email":
            self.email = e.control.value
            e.control.value =''
        elif e.control.label == "Senha":
            self.senha = e.control.value
            e.control.value =''
        elif e.control.label == "Grupo":
            self.grupo = e.control.value
            e.control.value =''
        elif e.control.label == "Pesquisa":
            self.pesq = e.control.value      
        else: 
            self.op = e.control.value
    
    def showdelete(self,e):
        try:
            myid = int(e.control.data)
            self.cur.execute(f"DELETE FROM passbank WHERE id={myid}")
            self.conn.commit()
            self.tb.rows.clear()
            self.tb.update()
            self.page.snack_bar  = SnackBar(
                    ft.Text(f'Conta deletada com sucesso'),
                    bgcolor='green')
            self.page.snack_bar.open=True
            self.page.update()
        except Exception as erro:
            self.page.snack_bar  = SnackBar(
                    ft.Text(f'Deu erro em deletar a conta: ', erro),
                    bgcolor='red')
            self.page.snack_bar.open=True
            self.page.update()

    def gera_pass(self,e): # Gerador de senha 15 caracters
            xxx = 0
            senha = ''
            for xxx in range(15):
                senha += random.choice((string.ascii_letters) + (string.digits) + "#$%&*^?@_!-ç=]}{[")
            self.senha =senha
            self.in_senha.value = str(senha)
            self.in_senha.update()  
            self.senha_edit.value = str(senha)
            self.senha_edit.update()    

    def hidedlg(self,e):
        self.dlg.visible=False
        self.dlg.update()

    def db_add(self,e): 
        try:
            if not self.conta:
                self.page.snack_bar  = SnackBar(
                    ft.Text(f'Falta conta'),
                    bgcolor='red')
                self.page.snack_bar.open=True
                self.page.update()
            elif not self.email:
                self.page.snack_bar  = SnackBar(
                    ft.Text(f'Falta email'),
                    bgcolor='red')
                self.page.snack_bar.open=True
                self.page.update()
            elif not self.senha:
                self.page.snack_bar  = SnackBar(
                    ft.Text(f'Falta senha'),
                    bgcolor='red')
                self.page.snack_bar.open=True
                self.page.update()
            elif not self.grupo:
                self.page.snack_bar  = SnackBar(
                    ft.Text(f'Falta grupo'),
                    bgcolor='red')
                self.page.snack_bar.open=True
                self.page.update()
            else:
                cc = Banquinho.encry(self.conta,key)
                ce = Banquinho.encry(self.email,key)
                cs = Banquinho.encry(self.senha,key)
                cg = Banquinho.encry(self.grupo,key)
                self.cur.execute(f'INSERT INTO passbank (conta,email,senha,grupo) VALUES {cc,ce,cs,cg}')
                self.conn.commit()
                self.tb.rows.clear()
                self.cur.execute(f'SELECT * FROM passbank ORDER BY id DESC')
                m = self.cur.fetchall()
                self.calldb(m)
                self.tb.update()
                self.page.snack_bar  = SnackBar(
                    ft.Text(f'Cadastrado com sucesso a Conta: {self.conta} '),
                    bgcolor='green')
                self.page.snack_bar.open=True
                self.inputcon.offset=transform.Offset(2,0)
                self.page.update()
                cc,ce,cs,cg = '','','',''
        except Exception as err: 
            self.page.snack_bar  = SnackBar(
                    ft.Text(f'Cadastro não realizado devido ao erro: ',err),
                    bgcolor='red')
            self.page.snack_bar.open=True
            self.page.update()

    def updateandsave(self,e):
        try:
            myid = self.id_edit.value
            cc = Banquinho.encry(self.conta_edit.value,key)
            ce = Banquinho.encry(self.email_edit.value,key)
            cs = Banquinho.encry(self.senha_edit.value,key)
            cg = Banquinho.encry(self.grupo_edit.value,key)
            self.cur.execute(
                """UPDATE passbank SET conta=?, email=?,
                senha=?, grupo=?
                WHERE id=?""", (cc,ce,cs,cg, myid)
            )
            self.conn.commit()
            self.tb.rows.clear()
            self.cur.execute('SELECT * FROM passbank ')
            m = self.cur.fetchall()
            self.calldb(m)
            self.dlg.visible=False
            self.dlg.update()
            self.tb.update()
            cc,ce,cs,cg = '','','',''
            self.page.snack_bar  = SnackBar(
                    ft.Text(f'A conta ', {self.conta_edit.value}, ' foi editada com sucesso'),
                    bgcolor='green')
            self.page.snack_bar.open=True
            self.page.update()
        except Exception as erro:
            self.page.snack_bar  = SnackBar(
                    ft.Text(f'Não foi possivel editar os dados devido: ', erro),
                    bgcolor='red')
            self.page.snack_bar.open=True
            self.page.update()

    def showedit(self,e):
        cc,ce,cs,cg = '','','',''
        data_edit = e.control.data
        self.id_edit.value = data_edit['id']
        cc  = Banquinho.decry(data_edit['conta'],key) 
        ce = Banquinho.decry(data_edit['email'],key) 
        cs = Banquinho.decry(data_edit['senha'],key) 
        cg = Banquinho.decry(data_edit['grupo'],key) 
        self.conta_edit.value = cc
        self.email_edit.value = ce
        self.senha_edit.value = cs
        self.grupo_edit.value = cg
        self.dlg.visible=True
        self.dlg.update()

    def calldb(self,b=[]):
        bank = b
        keys= ['id', 'conta', 'email', 'senha', 'grupo']
        result = [dict(zip(keys, values)) for values in bank]
        for x in result:
            cc  = Banquinho.decry(x['conta'],key) 
            ce = Banquinho.decry(x['email'],key) 
            cs = Banquinho.decry(x['senha'],key) 
            cg = Banquinho.decry(x['grupo'],key) 
            self.tb.rows.append(
                DataRow(
                    cells=[
                        DataCell(
                            Row([
                                IconButton(
                                    icon='create',
                                    icon_color='blue',
                                    data=x,
                                    on_click=self.showedit
                                ),
                                IconButton(
                                    icon='delete',
                                    icon_color='red',
                                    data=x['id'],
                                    on_click=self.showdelete
                                ),
                            ])
                        ),
                        DataCell(Text(cc)),
                        DataCell(Text(ce)),
                        DataCell(Text(cs)),
                        DataCell(Text(cg)),
                    ],
                ),
            )
            cc,ce,cs,cg = '','','',''

    def showinput(self,e):
        self.inputcon.offset=transform.Offset(0,0)
        self.page.update()
    def hidecon(self,e):
        self.inputcon.offset=transform.Offset(1,0)
        self.page.update()

    def haxi(t):
        thaxi = hashlib.sha512(t.encode())
        h = thaxi.hexdigest() # transformação do senha fornecido em hash sha512
        return h

    def main_banco(self,page:ft.page,params:Params,basket:Basket): # view banco
        params.my_id = user
        params.crip = key
        self.page = page
        return ft.View(
            route='/banco',
            adaptive=True,
            controls=[
                Column(
                    scroll=ft.ScrollMode.ALWAYS,
                    controls=[
                    ft.Container(content=ft.Row([
                    ft.Container(content=ft.Column([
                        ElevatedButton('Adicionar Nova Conta', on_click=self.showinput),])),
                    ft.Container(content=ft.Row([self.in_search,self.drop,self.b_search])),
                ])),
                self.mytable,
                self.inputcon
                ])
                ]
            )

class Log_pass:
    def __init__(self):
        self.conn=sqlite3.connect('database.db', check_same_thread=False) #
        self.cur = self.conn.cursor()
        self.centro = ft.MainAxisAlignment.CENTER      
        self.u = ft.TextField(label='Usuario',on_change=self.validate)
        self.p = ft.TextField(label='Senha',password=True,on_change=self.validate)
        self.b_sub = ft.ElevatedButton(text='SUBMIT',disabled=True,on_click=self.submit)

    def validate(self,e) -> None:
        if all([self.u.value,self.p.value]):
            self.b_sub.disabled = False
        else: self.b_sub.disable =True
        self.page.update()

    def submit(self,e) -> None:
        self.cur.execute('SELECT user,pass from users ')
        ver_u,ver_p = self.cur.fetchone()
        in_u_hash = Banquinho.haxi(self.u.value)
        in_p_hash = Banquinho.haxi(self.p.value)
        if in_u_hash == ver_u and in_p_hash == ver_p:
            global user,key
            user = str(self.u.value)
            key = user+self.p.value+'6969'
            print(key,'-> cripto')
            self.page.go('/banco')
        else: 
            self.page.snack_bar = ft.SnackBar(bgcolor=ft.colors.RED,content=(ft.Text('Not Authorized')))
            self.page.snack_bar.open = True
            self.page.update()
    def create():
        u = 'c7ad44cbad762a5da0a452f9e854fdc1e0e7a52a38015f23f3eab1d80b931dd472634dfac71cd34ebc35d16ab7fb8a90c81f975113d6c7538dc69dd8de9077ec #user padrao admin
        p = 'd404559f602eab6fd602ac7680dacbfaadd13630335e951f097af3900e9de176b6db28512f2e000b9d04fba5133e8b1c6e8df59db3a8ab9d60be4b97cc9e81db' #senha padrao 1234
        conn=sqlite3.connect('database.db', check_same_thread=False)
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS users(user,pass)")
        cur.execute(f'INSERT INTO users (user,pass) VALUES {u,p}')
        cur.execute("CREATE TABLE IF NOT EXISTS passbank(id INTEGER PRIMARY KEY AUTOINCREMENT, conta,email,senha,grupo)")
        conn.commit()
    def view(self,page:ft.page,params:Params,basket:Basket):
        Log_pass.create()
        self.page = page
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        return ft.View(
            route="/login",
            horizontal_alignment = ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text("Pagina Login"),
                ft.Container(
                    expand=True,
                    margin=10,
                    padding=10,
                    alignment=ft.alignment.center,
                    width=250,
                    height=200,
                    content=(ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[self.u,self.p,self.b_sub])
                ))
            ]
        )

    ''''''
