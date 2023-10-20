import getpass
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import time
import textwrap
import PySimpleGUI as sg
import winsound

def run():
    print("Executando o robô INPI...")

s = requests.session()
#sg.theme_previewer()
sg.theme('DarkBlue14')
layout = [
    #obrigatoriedades
    #pass
    #pular o defender
    [sg.Text(" ")],
    #[sg.Text("   "), sg.Image('logo.png'), sg.Text(" Pesquisa de patentes em massa!")],
    #[sg.Image('logo.png')],
    #[sg.Text("                     Robô de buscas Site INPI")],
    [sg.Text(" ")],
    [sg.Text("⌨ Digite patentes uma abaixo da outra:")],
    #[sg.InputText(key="patentes")],
    [sg.Multiline(key="patentes", size=(43, 10))],
    [sg.Text(" ")],
    [sg.Text("▪ Usuário e senha https://busca.inpi.gov.br:")],
    [sg.Text('Usuário', size=(7, 0)), sg.InputText('', key='usu', size=(36, 0))],
    #[sg.InputText(key="usu")],
    [sg.Text('Senha', size=(7, 0)), sg.InputText('', key='senha', size=(36, 0), password_char='*')],
    #[sg.InputText(key="senha")],    
    [sg.Text(" ")],
    [sg.Button("Avançar")],
    [sg.Text("", key="Avançar")],
]
  
janela = sg.Window("Robô de buscas Site INPI", layout)

while True:
    evento, valores = janela.read()
    if evento == sg.WIN_CLOSED or evento == "Sair":
        break
    if  evento == "Avançar":
        patentes = valores["patentes"]
        usuario = valores["usu"]
        senha = valores["senha"]
        janela.close()
        
if len(patentes)==0:
    print("⚠ Erro: Patentes não inclusas!")

if len(usuario)==0:
    print("⚠ Erro: Usuário não informado!")

if len(senha)==0:
    print("⚠ Erro: Senha não informada!")

lpat = list(patentes.splitlines())
pat = 'x'
print(" ")
lpat = [s.strip().replace(" ","") for s in lpat]
print ("⌨ Lista de processos com ",len(lpat)," patente(s): ", lpat)
username = usuario
password = senha
   
login = {'T_Login': 'username', 'T_senha': 'password', 'action': 'login'}

headers = {
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
"Accept-Encoding": "gzip, deflate, br",
"Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
"Cache-Control": "max-age=0",
"Connection": "keep-alive",
"Content-Length": "169",
"Content-Type": "application/x-www-form-urlencoded",
"Host": "busca.inpi.gov.br",
"Origin": "https://busca.inpi.gov.br",
"Referer": "https://busca.inpi.gov.br/pePI/jsp/patentes/PatenteSearchBasico.jsp",
"Sec-Fetch-Dest": "document",
"Sec-Fetch-Mode": "navigate",
"Sec-Fetch-Site": "same-origin",
"Sec-Fetch-User": "?1",
"Upgrade-Insecure-Requests": "1",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
"sec-ch-ua": 'Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
"sec-ch-ua-mobile": "?0",
"sec-ch-ua-platform": "Windows"

}

for npat in lpat:
    while True:
        try:
	    #r = s.get('https://busca.inpi.gov.br/pePI/servlet/LoginController?T_Login=x&T_Senha=x&action=login')
            r = s.get('https://busca.inpi.gov.br/pePI/servlet/LoginController?T_Login=' + username + '&T_Senha=' + password + '&action=login&Usuario=',headers=headers,data=login)
            n_pdf = 0
            print(" ")
            print("⏱⏱⏱ Procurando patente " + npat + " ⏱️⏱️⏱️")
            r = s.get("https://busca.inpi.gov.br/pePI/jsp/patentes/PatenteSearchBasico.jsp")
            payload = {'NumPedido': npat, 'Action': 'SearchBasico'}
            r =s.post('https://busca.inpi.gov.br/pePI/servlet/PatenteServletController', data=payload)
            Soup = BeautifulSoup(r.text, 'html.parser')
            n_link = 0
            for link in Soup.find_all('a', href=True):
                if npat in link['href']:
                    n_link = n_link+1
                    l = 'https://busca.inpi.gov.br' + link['href'].split("&SearchParameter")[0]
                    CodPedido = l.split("CodPedido=")[1]
                    r = s.get(l)
                    Soup = BeautifulSoup(r.text, 'html.parser')
                    ################################################
                    #Ajuste para a Listagem de Usuários Interessados
                    if Soup.find('font',{"class":"link-sol-amplo-acesso"}):
                        l2 = 'https://busca.inpi.gov.br/pePI/servlet/AmploAcessoServletController'
                        payload2 = {'codigoHipotese': '1', 'aceite': 'on', 'CodPedido': CodPedido, 'Action': 'LiberarAmploAcessoPatentes'}
                        r2 = s.post(l2,data=payload2)
                        print("Usuário cadastrado na Listagem Terceiros Interessados Habilitados")
                        r = s.get(l)
                        r2 = s.get('https://busca.inpi.gov.br/pePI/servlet/AmploAcessoServletController?Action=DesativarAmploAcessoPatentes&CodPedido='+CodPedido)
                        print("Usuário descadastrado na Listagem Terceiros Interessados Habilitados")
                        Soup = BeautifulSoup(r.text, 'html.parser')
                    #Fim do ajuste
                    ################################################    
                    print("Salvando Site")
                    print(npat)
                    Path(npat).mkdir(exist_ok=True)
                    filename = Path(npat + "\\_"+npat+".htm")
                    filename.write_bytes(r.content)
                    print("Salvando PDFs")
                    pdf_list = []
                    n_pdf = 0
                    for tr in Soup.find_all('tr',{"class":"normal"}):
                        for td in tr.find_all('td'):
                            for i in td.find_all('img',{"class":"salvaDocumento cursor"}):
                                pdf_id = i['id']
                                pdf_t1 = tr.find_all('td')[0].text.strip().replace(" ","")[:4].strip()
                                if tr.find_all('td')[2].text.strip().replace(" ","")[:4].strip() != "Desc":
                                    pdf_t1 = pdf_t1 + "_" + tr.find_all('td')[2].text.strip().replace(" ","")[:4].strip()

                                try:
                                    pdf_t2 = ' - ' + tr.find_all('td')[10].text.replace(" ","").replace("\n", "")
                                except:
                                    pdf_t2 = ''

                                pdf_path = "https://busca.inpi.gov.br/pePI/servlet/ImagemDocumentoPdfController?CodDiretoria=200&NumeroID=" + i['id'] + "&certificado=undefined&numeroProcesso=&ipasDoc=undefined&action=DocumentoPatente&codPedido=" + CodPedido
                                if not pdf_path in pdf_list:
                                    pdf_list.append(pdf_path)
                                    print("Salvando PDF "+str(n_pdf+1)+": "+pdf_t1 + pdf_t2)
                                    pdf = s.get(pdf_path)
                                    filename = Path(npat + "\\" + str(n_pdf) + " - " + pdf_t1 + pdf_t2 + '.pdf')
                                    filename.write_bytes(pdf.content)
                                    n_pdf = n_pdf+1
                    break
            if n_link == 0: print("Não foi encontrado nenhum item com este código")
            if n_pdf == 0:
                print("Não foi encontrado nenhum PDF para baixar")
            else:
                print(str(n_pdf) + " baixado(s) para " + npat)
            break
        except Exception as e:
            print("Erro, tentando em 15s...")
            print(e)
            time.sleep(15)            
winsound.Beep(1000, 150)            
print(" ")
print ("Finalizado(s) ", len(lpat)," processo(s) de ",len(lpat))

USE_FADE_IN = True
WIN_MARGIN = 70
WIN_COLOR = "#282828"
TEXT_COLOR = "#ffffff"
DEFAULT_DISPLAY_DURATION_IN_MILLISECONDS = 5000
img_error = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAMAAABEpIrGAAAAA3NCSVQICAjb4U/gAAAACXBIWXMAAADlAAAA5QGP5Zs8AAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAAAIpQTFRF////20lt30Bg30pg4FJc409g4FBe4E9f4U9f4U9g4U9f4E9g31Bf4E9f4E9f4E9f4E9f4E9f4FFh4Vdm4lhn42Bv5GNx5W575nJ/6HqH6HyI6YCM6YGM6YGN6oaR8Kev9MPI9cbM9snO9s3R+Nfb+dzg+d/i++vt/O7v/fb3/vj5//z8//7+////KofnuQAAABF0Uk5TAAcIGBktSYSXmMHI2uPy8/XVqDFbAAAA8UlEQVQ4y4VT15LCMBBTQkgPYem9d9D//x4P2I7vILN68kj2WtsAhyDO8rKuyzyLA3wjSnvi0Eujf3KY9OUP+kno651CvlB0Gr1byQ9UXff+py5SmRhhIS0oPj4SaUUCAJHxP9+tLb/ezU0uEYDUsCc+l5/T8smTIVMgsPXZkvepiMj0Tm5txQLENu7gSF7HIuMreRxYNkbmHI0u5Hk4PJOXkSMz5I3nyY08HMjbpOFylF5WswdJPmYeVaL28968yNfGZ2r9gvqFalJNUy2UWmq1Wa7di/3Kxl3tF1671YHRR04dWn3s9cXRV09f3vb1fwPD7z9j1WgeRgAAAABJRU5ErkJggg=='
img_success = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAMAAABEpIrGAAAAA3NCSVQICAjb4U/gAAAACXBIWXMAAAEKAAABCgEWpLzLAAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAAAHJQTFRF////ZsxmbbZJYL9gZrtVar9VZsJcbMRYaMZVasFYaL9XbMFbasRZaMFZacRXa8NYasFaasJaasFZasJaasNZasNYasJYasJZasJZasJZasJZasJZasJYasJZasJZasJZasJZasJaasJZasJZasJZasJZ2IAizQAAACV0Uk5TAAUHCA8YGRobHSwtPEJJUVtghJeYrbDByNjZ2tvj6vLz9fb3/CyrN0oAAADnSURBVDjLjZPbWoUgFIQnbNPBIgNKiwwo5v1fsQvMvUXI5oqPf4DFOgCrhLKjC8GNVgnsJY3nKm9kgTsduVHU3SU/TdxpOp15P7OiuV/PVzk5L3d0ExuachyaTWkAkLFtiBKAqZHPh/yuAYSv8R7XE0l6AVXnwBNJUsE2+GMOzWL8k3OEW7a/q5wOIS9e7t5qnGExvF5Bvlc4w/LEM4Abt+d0S5BpAHD7seMcf7+ZHfclp10TlYZc2y2nOqc6OwruxUWx0rDjNJtyp6HkUW4bJn0VWdf/a7nDpj1u++PBOR694+Ftj/8PKNdnDLn/V8YAAAAASUVORK5CYII='

def display_notification(title, message, icon, display_duration_in_ms=DEFAULT_DISPLAY_DURATION_IN_MILLISECONDS, use_fade_in=True, alpha=0.9, location=None):
    """
    Function that will create, fade in and out, a small window that displays a message with an icon
    The graphic design is similar to other system/program notification windows seen in Windows / Linux
    :param title: (str) Title displayed at top of notification
    :param message: (str) Main body of the noficiation
    :param icon: (str) Base64 icon to use. 2 are supplied by default
    :param display_duration_in_ms: (int) duration for the window to be shown
    :param use_fade_in: (bool) if True, the window will fade in and fade out
    :param alpha: (float) Amount of Alpha Channel to use.  0 = invisible, 1 = fully visible
    :param location: Tuple[int, int] location of the upper left corner of window. Default is lower right corner of screen
    """
    
    message = textwrap.fill(message, 50)
    win_msg_lines = message.count("\n") + 1

    screen_res_x, screen_res_y = sg.Window.get_screen_size()
    win_margin = WIN_MARGIN  # distance from screen edges
    win_width, win_height = 364, 66 + (14.8 * win_msg_lines)
    win_location = location if location is not None else (screen_res_x - win_width - win_margin, screen_res_y - win_height - win_margin)

    layout = [[sg.Graph(canvas_size=(win_width, win_height), graph_bottom_left=(0, win_height), graph_top_right=(win_width, 0), key="-GRAPH-",
                        background_color=WIN_COLOR, enable_events=True)]]

    window = sg.Window(title, layout, background_color=WIN_COLOR, no_titlebar=True,
                       location=win_location, keep_on_top=True, alpha_channel=0, margins=(0, 0), element_padding=(0, 0),
                       finalize=True)

    window["-GRAPH-"].draw_rectangle((win_width, win_height), (-win_width, -win_height), fill_color=WIN_COLOR, line_color=WIN_COLOR)
    window["-GRAPH-"].draw_image(data=icon, location=(20, 20))
    window["-GRAPH-"].draw_text(title, location=(64, 20), color=TEXT_COLOR, font=("Arial", 12, "bold"), text_location=sg.TEXT_LOCATION_TOP_LEFT)
    window["-GRAPH-"].draw_text(message, location=(64, 44), color=TEXT_COLOR, font=("Arial", 9), text_location=sg.TEXT_LOCATION_TOP_LEFT)
    window['-GRAPH-'].set_cursor('hand2')

    if use_fade_in == True:
        for i in range(1,int(alpha*100)):               # fade in
            window.set_alpha(i/100)
            event, values = window.read(timeout=20)
            if event != sg.TIMEOUT_KEY:
                window.set_alpha(1)
                break
        event, values = window(timeout=display_duration_in_ms)
        if event == sg.TIMEOUT_KEY:
            for i in range(int(alpha*100),1,-1):       # fade out
                window.set_alpha(i/100)
                event, values = window.read(timeout=20)
                if event != sg.TIMEOUT_KEY:
                    break
    else:
        window.set_alpha(alpha)
        event, values = window(timeout=display_duration_in_ms)

    window.close()


title = "Robô finalizado"
message = "Busca de patentes finalizada. Se você inseriu as patentes, os downloads foram efetuados!"
display_notification(title, message, img_success, 5000, use_fade_in=True)
sg.popup_ok("Processo finalizado. Clique em OK para sair.")
