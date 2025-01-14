import sys
import os
import requests
import argparse
import time
from dotenv import load_dotenv
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
import base64
import sqlite3
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
load_dotenv()
firefox_options = Options()


rutaDB = "RUTA A LA BASE DE DATOS" #CAMBIAR 
urlNotification = "http://IP_GOTIFY:PUERTO_GOTIFY/RUTA?token=" #CAMBIAR

firefox_options.add_argument('--headless') # EN CASO DE QUERER VER LA EJECUCIÓN DEL NAVEGADOR EN TIEMPO REAL DE LA API COMENTAR ESTA LINEA

browser = webdriver.Firefox(options=firefox_options)
#browser = webdriver.Firefox()

class account():
    def __init__(self,accountName,browser):

        self.name = accountName
        self.followers = 0
        self.followersAccounts = []
        self.following = 0
        self.followingAccounts = []
        self.comprobation = True
        self.getDataAccount(accountName,browser )

    #AL CREAR EL OBJETO SACA LOS DATOS DEL USUARIO Y LOS GUARDA EN EL OBJETO
    def getDataAccount(self,accountName,browser):

        try:
            url="https://www.instagram.com/"+self.name
            browser.get(url)
            time.sleep(15)
            insta_href="/"+accountName+"/followers/"
            print(insta_href)
            followerButton=browser.find_element("css selector",f"a.x1i10hfl[href='{insta_href}']")
            followerButton.click()
            time.sleep(15)

            ventana = browser.find_element("css selector",'div.x1ccrb07') 
            time.sleep(15)
            scroll(browser,ventana)

            names, quantity = informationParser()
            self.followersAccounts = names
            self.followers = quantity
            self.comptobation = True

        except:
            print("HA OCURRIDO UN ERROR EN FOLLOWERS")
            sendNotification("Ha ocurrido un error en followers")
            self.comprobation = False
            return


        try:
            url="https://www.instagram.com/"+self.name
            browser.get(url)
            time.sleep(15)
            insta_href="/"+accountName+"/following/"
            print(insta_href)
            followerButton=browser.find_element("css selector",f"a.x1i10hfl[href='{insta_href}']")
            followerButton.click()
            time.sleep(15)

            ventana = browser.find_element("css selector",'div.x1ccrb07')
            time.sleep(15)
            scroll(browser,ventana)

            names, quantity = informationParser()
            self.followingAccounts = names
            self.following = quantity
            self.comprobation = True

        except:
            print("HA OCURRIDO UN ERROR EN FOLLOWING")
            sendNotification("Ha ocurrido un error en following")
            self.comprobation = False
            return

        print("Objeto creado")
        pass


    def introduceData(self,number):
        conn = sqlite3.connect(rutaDB)
        cursor = conn.cursor()

        cursor.execute("select USERNAME from CUENTAS")
        resultados_CUENTAS=cursor.fetchall()


        #lo devuelve en tuplas, y necesitamos compararlo con un array, y para ello lo pasamos a array
        registros_CUENTAS = []
        for i in resultados_CUENTAS:
            registros_CUENTAS.append(i[0])


        if number == 1:
            ImIn="seguidores"
            cursor.execute("select SEGUIDOR from FOLLOWS WHERE SEGUIDO = ? " , (self.name,))
            resultados_FOLLOWS=cursor.fetchall()

            registros_FOLLOWS = []
            for i in resultados_FOLLOWS:
                registros_FOLLOWS.append(i[0])

            persons = self.followersAccounts
            contador_CUENTAS=0
            contador_FOLLOWS=0

            personas_messages = []

            for i in persons:

                if i not in registros_CUENTAS:
                    cursor.execute("insert into CUENTAS (USERNAME,PASSWORD) values (?, ?)",(i, ''))
                    #print("Se ha insertado a", i, "en cuentas correctamente.")
                    #print("________________________________")
                    contador_CUENTAS=contador_CUENTAS+1

                if i not in registros_FOLLOWS:
                    cursor.execute('SELECT * FROM UNFOLLOWS WHERE SEGUIDOR = ? AND SEGUIDO = ?;', (i,self.name))
                    unfollower=cursor.fetchall()
                    cursor.execute('INSERT INTO FOLLOWS (SEGUIDOR, SEGUIDO) VALUES (?,?);',(i,self.name))

                    if len(unfollower) != 0:
                        cursor.execute('DELETE FROM UNFOLLOWS WHERE SEGUIDOR = ? AND SEGUIDO = ?;', (i, self.name))
                        #print(i,"Era una persona que te había dejado de seguir. Y te ha vuelto a seguir.")


                    #print("Se ha insertado como que", i, "sigue a", self.name, "en FOLLOWS correctamente.")
                    #print("________________________________")
                    contador_FOLLOWS=contador_FOLLOWS+1
                    personas_messages.append('@'+i)

            message=f"Hoy {contador_FOLLOWS} personas te han seguido, que son los siguientes: \n{', '.join(map(str, personas_messages))}"


        else:
            ImIn="seguidos"
            cursor.execute("select SEGUIDO from FOLLOWS WHERE SEGUIDOR = ? " , (self.name,))
            resultados_FOLLOWS=cursor.fetchall()

            registros_FOLLOWS = []
            for i in resultados_FOLLOWS:
                registros_FOLLOWS.append(i[0])

            persons = self.followingAccounts
            contador_CUENTAS=0
            contador_FOLLOWS=0
            personas_messages = []

            for i in persons:
                if i not in registros_CUENTAS:

                    cursor.execute("insert into CUENTAS (USERNAME,PASSWORD) values (?, ?)",(i, ''))
                    #print("Se ha insertado a", i, "en cuentas correctamente.")
                    #print("________________________________")
                    contador_CUENTAS=contador_CUENTAS+1

                if i not in registros_FOLLOWS:
                    cursor.execute('SELECT * FROM UNFOLLOWS WHERE SEGUIDOR = ? AND SEGUIDO = ?;', (self.name, i))
                    unfollower=cursor.fetchall()


                    if len(unfollower) != 0:
                        cursor.execute('DELETE FROM UNFOLLOWS WHERE SEGUIDOR = ? AND SEGUIDO = ?;', (self.name, i))
                        #print(i,"Era una persona que te había dejado de seguir. Y te ha vuelto a seguir.")

                    cursor.execute('INSERT INTO FOLLOWS (SEGUIDOR, SEGUIDO) VALUES (?,?);',(self.name, i))
                    #print("Se ha insertado como que", self.name, "sigue a", i, "en FOLLOWS correctamente.")
                    #print("________________________________")
                    contador_FOLLOWS=contador_FOLLOWS+1
                    personas_messages.append('@'+i)

            message=f"Has empezado a seguir a {contador_FOLLOWS} personas, que son los siguientes: \n{', '.join(map(str, personas_messages))}"

        conn.commit()
        conn.close()

        if contador_FOLLOWS == 0:
            return False
        else:
            sendNotification(message)
            return True



    def unfollows(self):
        conn = sqlite3.connect(rutaDB)
        cursor = conn.cursor()
        cursor.execute('select count(*) from FOLLOWS where SEGUIDO = ?;',(self.name,))

        tupla_cantidad_SEGUIDORES_db=cursor.fetchone()
        cantidad_SEGUIDORES_db = int(tupla_cantidad_SEGUIDORES_db[0])

        cursor.execute('select count(*) from FOLLOWS where SEGUIDOR = ?;',(self.name,))
        tupla_cantidad_SEGUIDOS_db=cursor.fetchone()
        cantidad_SEGUIDOS_db = int(tupla_cantidad_SEGUIDOS_db[0])

        contador_TONTOS = 0
        contador_SAPOS = 0

        if self.followers < cantidad_SEGUIDORES_db:
            cursor.execute('SELECT SEGUIDOR FROM FOLLOWS WHERE SEGUIDO = ?;',(self.name,))
            SEGUIDORES_db=cursor.fetchall()
            registro_SEGUIDORES = []
            for i in SEGUIDORES_db:
                registro_SEGUIDORES.append(i[0])

            registro_SAPOS = []

            for i in registro_SEGUIDORES:
                if i not in self.followersAccounts:
                    registro_SAPOS.append('@'+i)
                    cursor.execute('INSERT INTO UNFOLLOWS (SEGUIDOR, SEGUIDO) VALUES (?,?);', (i,self.name))
                    cursor.execute('DELETE FROM FOLLOWS WHERE SEGUIDOR = ? AND SEGUIDO = ?;', (i,self.name))
                    print(i, "HA SIDO UN PUTO SAPO QUE TE HA DEJADO DE SEGUIR")
                    contador_SAPOS = contador_SAPOS + 1


            Message=f"Te han dejado de seguir {contador_SAPOS} personas, que son: \n{', '.join(map(str, registro_SAPOS))}"
            sendNotification(Message)

        if self.following <  cantidad_SEGUIDOS_db:
            cursor.execute('SELECT SEGUIDO FROM FOLLOWS WHERE SEGUIDOR = ?;',(self.name,))
            SEGUIDOS_db=cursor.fetchall()
            registro_SEGUIDOS = []
            for i in SEGUIDOS_db:
                registro_SEGUIDOS.append(i[0])

            registro_TONTOS = []


            for i in registro_SEGUIDOS:
                if i not in self.followingAccounts:
                    registro_TONTOS.append('@'+i)
                    cursor.execute('INSERT INTO UNFOLLOWS (SEGUIDOR, SEGUIDO) VALUES (?,?);', (self.name, i))
                    cursor.execute('DELETE FROM FOLLOWS WHERE SEGUIDOR = ? AND SEGUIDO = ?;', (self.name, i))
                    print(i, "ERA UN TONTO SEGURO QUE HAS DEJADO DE SEGUIR")
                    contador_TONTOS = contador_TONTOS + 1

            Message=f"Has dejado de seguir a {contador_TONTOS} personas, que son: \n{', '.join(map(str, registro_TONTOS))}"
            sendNotification(Message)


        conn.commit()
        conn.close()

        if contador_TONTOS > 0 or contador_SAPOS > 0:
            return True

        else:
            return False


def informationParser(): # Parsea los nombres de usuarios todo el contenido de la página
    html=browser.page_source
    soup = BeautifulSoup(html,"html.parser")
    spans = soup.select('span._ap3a._aaco._aacw._aacx._aad7._aade')

    names = []
    for name in spans:
        names.append(name.text)

    quantity=len(names)
    return names,quantity


def scroll(browser,ventana): #Realiza el scroll dentro de la ventana emergente
    boolean = True
    lastHeight = 0
    while boolean:
        browser.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight)",ventana)
        time.sleep(10)
        newHeight = browser.execute_script("return arguments[0].scrollHeight", ventana)
        #print(newHeight)
        #print(lastHeight)

        if newHeight == lastHeight:
            html=browser.page_source
            boolean = False
            soupNumber = BeautifulSoup(html,"html.parser")
            print("ya no puedo bajar mas")
            return soupNumber

        else:
            lastHeight = newHeight




def comprobationNameExists(URL,browser): #MEDIANTE LA URL COMPRUEBA SI EXISTE LA CUENTA O SI ES PRIVADA O PUBLICA Y LO DEVUELVE
#Actualmente es una función obsoleta pero posiblemente útil en futuras implementaciones del proyecto
    browser.get(URL)
    time.sleep(5)

    try:
        cookie=browser.find_element("css selector",'button._a9--')
        cookie.click()
    except:
        print("No existían cookies")


    #saca el html y lo parsea con beautifulsoup(creando una sopa y usando el parser html.parser) buscando si existe el nombre de la cuenta
    html=browser.page_source
    soup = BeautifulSoup(html,"html.parser")

    accountName = soup.find('h2', class_=["x1lliihq", "x1plvlek", "xryxfnj"])

    #si existe el nombre busca si es privada
    if accountName != None:

        accountType= soup.find('h2', class_="_aa_u")

        if accountType == None:
            finalReturn={'accountName':accountName.text,'exists':True,'public':True}
        else:
            finalReturn={'accountName':accountName.text,'exists':True,'public':False}


    elif accountName == None:
        parserExists = soup.find('span', class_=["x1lliihq", "x1plvlek", "xryxfnj"])
        finalReturn={'exists':False,'priv':False}

    return finalReturn



def inicioSesion(URL, browser, user):
    booleano=True
    while booleano:
        try:
            #Saco la contraseña de la base de datos
            conn = sqlite3.connect(rutaDB)
            cursor = conn.cursor()
            cursor.execute("select PASSWORD from CUENTAS where USERNAME = ?",(user.lower(),))
            password=cursor.fetchone()
            password_decrypted = descifrar_contrasena(password[0])

            #Abro el navegador en el login de instagram y acepto cookies
            browser.get("https://www.instagram.com/accounts/login/")
            time.sleep(2)
            cookie=browser.find_element("css selector",'button._a9--')
            cookie.click()


            #Meto los credenciales que me ha proporcionado el usuario
            boxUser= browser.find_element("css selector", "input._aa4b[name='username']") #._add6
            boxPassword= browser.find_element("css selector", "input._aa4b[name='password']") #._add6
            time.sleep(1)

            boxUser.send_keys(user)
            boxPassword.send_keys(password_decrypted)
            time.sleep(2)

            submitButton=browser.find_element("css selector", 'button[type="submit"]')
            submitButton.click()
            time.sleep(5)
            conn.close()
            return True

        except:
            conn.close()
            return False


def cifrar_contrasena(password): # Se debe tener en el archivo .env un registro llamado KEY con la key que se debe generar de 32 bytes para poder cifrar y descifrar la contraseña de forma segura
    # Convertir la contraseña en bytes
    password_bytes = password.encode('utf-8')

    # Generar un nonce único de 16 bytes
    nonce = os.urandom(16)
    # print("LOS DATOS PARA CIFRAR")
    # print("EL NONCE ES:", nonce)

    #Sacar la key
    key_based = os.getenv("KEY")
    key = base64.b64decode(key_based)

    # Crear el cifrador ChaCha20
    cipher = Cipher(algorithms.ChaCha20(key, nonce), mode=None)
    encryptor = cipher.encryptor()

    # Cifrar la contraseña
    encrypted_password = encryptor.update(password_bytes)
    encrypted_password_nonce=base64.b64encode(encrypted_password + nonce).decode('utf-8')

    return encrypted_password_nonce



def descifrar_contrasena(passwdNonceBased): 

    #Separar el once del hash
    passwdNonce = base64.b64decode(passwdNonceBased)
    nonce = passwdNonce[-16:]
    encrypted_password = passwdNonce[:-16]

    #Sacar la key
    key_based = os.getenv("KEY")
    key = base64.b64decode(key_based)

    # Crear el descifrador ChaCha20
    cipher = Cipher(algorithms.ChaCha20(key, nonce), mode=None)
    decryptor = cipher.decryptor()

    # Descifrar la contraseña
    decrypted_password = decryptor.update(encrypted_password)

    return decrypted_password.decode('utf-8')

def sendNotification(message, who=""): #Manda notificaciones a través de gotify, si se le pasa un segundo parámetro a la función se le enviará al admin la notificación.

    # Configuración
    if who != "":
        name = "ADMIN"
        token = os.getenv("ADMIN")
    else:
        name=args.destinatario.upper()
        token = os.getenv(name)

    urlNotification = urlNotification + token
    title="OYE "+ name +" UNA COSITA..."
    data = {
        "title": title,
        "message": message,
        "priority": 5
    }

# Enviar el mensaje
    response = requests.post(urlNotification, data=data)

# Comprobar la respuesta
    if response.status_code == 200:
        print("Mensaje enviado correctamente.")
    else:
        print(f"Error al enviar el mensaje: {response.status_code}")
        print(response.text)




def newClient(username=None,password=None): #Función que solo se utiliza si aparece la opción --register a la hora de lanzar la aplicación. Añade un nuevo usuario que tendrá contraseña a la base de datos.
    if username == None and password == None:
        boolean = True
        while boolean:
            username=input("Cual es tu nombre de usuario de instagram? (sin el arroba por favorrrr) ")
            # time.sleep(2)
            answer = input(f"\nseguro que '{username}' es tu nombre de usuario? y/N ")

            if answer.lower() == "y" or answer.lower() == "yes":
                boolean = False

        boolean = True
        while boolean:
            password=input("Cual es tu contraseña? ")
            passwordRepeat =input("Escribe tu contraseña de nuevo ")

            if password != passwordRepeat:
                answer = input("\nLas contraseñas no coinciden, quieres salir del programa? y/N ")
                if answer.lower() == "y" or answer.lower() == "yes":
                    boolean = False
                    print("\nHasta luego")
                    return
            else:
                boolean = False

    try:
        conn = sqlite3.connect(rutaDB)
        cursor = conn.cursor()
        cursor.execute("select USERNAME,PASSWORD from CUENTAS where USERNAME = ?",(username.lower(),))
        resultado=cursor.fetchone()

    except:
        print("Ha ocurrido un error a la hora de conectarse a la base de datos.")

    if resultado == None:
        print("el usuario no existe, por lo que voy a introducirlo en la base de datos")
        try:
            password_ecrypted = cifrar_contrasena(password)
            cursor.execute("INSERT INTO CUENTAS (USERNAME, PASSWORD) VALUES (?, ?)", (username, password_ecrypted))
        except:
            print("No se ha podido crear el nuevo usuario, una pena :/")

    elif resultado[1] == '':
        try:
            password_ecrypted = cifrar_contrasena(password)
            cursor = conn.cursor()
            cursor.execute("UPDATE CUENTAS SET PASSWORD = ? WHERE USERNAME = ?",(password_ecrypted,username.lower()))
            print("LA CONTRASEÑA DE LA CUENTA HA SIDO ACTUALIZADA POR PRIMERA VEZ CON ÉXITO")

        except:
            print("Ha ocurrido un error a la hora de actualizar la contraseña por primera vez")

    elif resultado[1] != '':
        answer = input(f"Quieres actualizar la contraseña? y/N ")

        if answer.lower() == "y" or answer.lower() == "yes":
            password_decrypted = descifrar_contrasena(resultado[1])
            if password_decrypted == password:
                print("Eres un grande, quieres actualizar la contraseña con la misma. PUTO GENIO")
            else:
                try:
                    password_ecrypted = cifrar_contrasena(password)
                    cursor.execute("UPDATE CUENTAS SET PASSWORD = ? WHERE USERNAME = ?",(password_ecrypted,username.lower()))
                    print("CUENTA ACTUALIZADA CON ÉXITO")

                except:
                    print("Ha ocurrido un error a la hora de actualizar la contraseña.")

        else:
            print("Pues ya está actualizao master, no se pa que me pides que la actualice.")
    try:
        conn.commit()
        conn.close()
    except:
        print("Ha ocurrido un error a la hora de actualizar la base de datos y cerrarla, revisalo anda.")

def commonFollow(): # Si la opción --commonfollows es utilizada a la hora de lanzar el comando, comprueba qué personas TÚ sigues, que NO te siguen de vuelta.
    try:
        conn = sqlite3.connect(rutaDB)
        cursor = conn.cursor()
        cursor.execute('SELECT SEGUIDO FROM FOLLOWS WHERE SEGUIDOR = ?;',(args.usuario,))
        SEGUIDOS_db=cursor.fetchall()
        registro_SEGUIDOS = []
        for i in SEGUIDOS_db:
            registro_SEGUIDOS.append(i[0])

        cursor.execute('SELECT SEGUIDOR FROM FOLLOWS WHERE SEGUIDO = ?;',(args.usuario,))
        SEGUIDORES_db=cursor.fetchall()
        registro_SEGUIDORES = []
        for i in SEGUIDORES_db:
            registro_SEGUIDORES.append(i[0])

        ijosdeputa = []
        contador_CUENTAS = 0
        for i in registro_SEGUIDOS:
                if i not in registro_SEGUIDORES:
                    ijosdeputa.append('@'+i)
                    contador_CUENTAS=contador_CUENTAS+1
        message=f"Hay {contador_CUENTAS} personas que no te siguen de vuelta, que son los siguientes: \n{', '.join(map(str, ijosdeputa))}"
        sendNotification(message)

    except:
        print("Ha ocurrido un error a la hora de conectarse a la base de datos.")

    conn.close()

def main(user):
    print("Bienvenido a ValBot-Instagram")
    url="https://www.instagram.com/" + user
    print(url)
    response = inicioSesion(url ,browser, user)
    if response:
        persona1 = account(user,browser)
        comprobation = getattr(persona1,"comprobation")
        if comprobation == False:
            sendNotification("Ha ocurrido un error en el programa que hace que no se muestren los seguidores correctamente.")
            sys.exit("Ha ocurrido un error en el programa que hace que no se muestren los seguidores correctamente.")

    else:
        sendNotification("Ha ocurrido un error en el programa ya que la cuenta no se encuentra disponible")
        sys.exit("Ha ocurrido un error en el programa ya que la cuenta no se encuentra disponible")


    print("Comprobación del objeto creado")
    print("*********************************")
    print("El usuario", getattr(persona1,"name"), "tiene", getattr(persona1,"followers"),"seguidores, y sigue a",getattr(persona1,"following"), "personas")

    browser.quit()

    responseFunction1 = persona1.introduceData(1)
    responseFunction2 = persona1.introduceData(2)
    responseFunctionUnfollows = persona1.unfollows()

    if responseFunction1 == False and responseFunction2 == False and responseFunctionUnfollows == False:
        sendNotification("No hay actualizaciones de seguidores.")

    print("\nprograma terminado")



#************************************************************************************************************************
#****************************************************** IMPORTANTE ******************************************************
#************************************************************************************************************************
#
# Reglas de uso para cuando lancemos el programa
# Los parámetros --usuario y --destinatario NO pueden ir vacío en ningún momento.
# El parámetro de --usuario corresponde a qué usuario (que debe tener el mismo nombre que la cuenta de instagram y la contraseña, además el registro debe estar en la base de datos) vamos a consultar sus seguidores. (En caso de no estar en la base de datos utilizar la opción --register)
# El parámetro de --destinatario debe corresponderse a el nombre que de usuario de GOTIFY que vaya a recibir la notificación. Que debe ser el mismo nombre con el que almacenes su Nombre e id de gotify en el .env. EJEMPLO: PAQUITO=Ab4JKnouyL_DwFF
# El parámetro --commonfollows solo va a enviar quien no te sigue pero tu sigues. No se va a actualizar en la base de datos, simplemente lo saca de los datos que ya tiene.


# Crear el parser de argumentos
parser = argparse.ArgumentParser(description="Procesar argumentos para el script.")

# Definir los argumentos esperados
parser.add_argument("--usuario", required=True, help="El nombre del usuario de instagram (Nunca puede estar vacío el parámetro)")
parser.add_argument("--destinatario", required=True, help="Quien va a recibir al notificación (Nunca puede estar vacío el parámetro)")
parser.add_argument("--register", action="store_true",help="Quieres registrar un usuario?")
parser.add_argument("--commonfollows", action="store_true",help="Saber quien sigues que no te sigue de vuelta?")


# Parsear los argumentos
args = parser.parse_args()

if args.register:
    newClient()

elif args.commonfollows:
    commonFollow()

else:
    main(args.usuario)