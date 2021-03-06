
import socket


from threading import Thread


import sys


import time


import webbrowser as wb


import signal


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


IP = "127.0.0.1"
PORT = 42069


HEADER_LENGTH = 10


server_socket.bind((IP, PORT))


server_socket.listen(100)


clients = {}


clientList = []

clientToDoctor = []


threads = []

url = "https://www2.hse.ie/conditions/coronavirus/coronavirus.html"




def sigint_handler(signum, frame):
    print('\n Server Shutting down')
    server_socket.close()
    sys.exit()


signal.signal(signal.SIGINT, sigint_handler)




def getNewUser(client_socket):
    try:

        message_header = client_socket.recv(HEADER_LENGTH)


        if not len(message_header):
            return False


        message_length = int(message_header.decode('utf-8').strip())


        dataReceived = client_socket.recv(message_length)
        dataReceived = dataReceived.decode('utf-8')
        return {'header': message_header, 'data': dataReceived}

    except:
        return False


# ---------------------client == patient functions ---------------------

def greetUser(client_socket, username):

    client_socket.send(
        f"Welcome to this helpline {username}!\n".encode('utf-8'))
    client_socket.send(
        f"We have collected your location data\n".encode('utf-8'))
    client_socket.send(
        f"Press Y to begin the survey".encode('utf-8'))




possibleAnswers = ['y\n', 'yes\n', 'Y\n',
                   'Yes\n', 'n\n', 'no\n', 'N\n', 'No\n']



def sendSurvey(client_socket, question):

    surveyList = [
        "Do you have a fever? Y/N",
        "Do you have a dry cough? Y/N",
        "Are you coughing up phlegm or mucous? Y/N",
        "Do you have shortness of breath? Y/N",
        "Can you hold your breath for 10 seconds? Y/N",
        "Are you feeling fatigued or exhausted? Y/N",
        "Have you got a sore throat? Y/N",
        "Are you experiencing headaches? Y/N",
        "Are you experiencing muscle aches? Y/N",
        "Are you experiencing chills? Y/N",
        "Have you got nausea/ have you been vomiting? Y/N",
        "Have you had diarrhoea? Y/N",
        "Do you have a stuffy nose? Y/N",
        "Do you have a runny nose? Y/N",
        "Have you been to an affected area in the past two weeks e.g. Spain, Italy, Wuhan? Y/N",
        "Have you been in contact with any people who have tested positive for the virus? Y/N",
        "Have you been to a hospital in the past two weeks? Y/N"]

    client_socket.send(surveyList[question].encode('utf-8'))



def checkForVirus(answerlist):
    weights = [0.88, 0.38, 0.33, 0.18, 0.33, 0.38, 0.14,
               0.14, 0.14, 0.11, 0.05, 0.05, 0.04, -1, 0.3, 0.5, 0.3]

    
    answerlist = answerlist[1:]
    virusSum = 0
    affirmitiveAnswers = ['y\n', 'yes\n', 'Y\n',
                          'Yes\n']

    for i in range(len(answerlist)):
        if answerlist[i] in affirmitiveAnswers:
            virusSum = virusSum + weights[i]

    if virusSum >= 1.58:
        return "positive"
    else:
        return "negative"


def sendMessageToDoctor(client_socket, messageDoctor):
  

    message = (str(clients[client_socket]) +
               " > " + messageDoctor).encode('utf-8')

    for client in clientToDoctor:
        if client != client_socket:
            try:
                client.send(message)
            except:
                print(f"{clients[client_socket]} has left the application")


def askForDoctor(client_socket):
    while True:
        try:

            ans = client_socket.recv(2048)
            ans = ans.decode('utf-8')

            if ans in possibleAnswers:
                if ans not in ['y\n', 'yes\n', 'Y\n',
                               'Yes\n']:
                    client_socket.send(
                        "We are redirecting you to the HSE website for more information as to how to arrange your test".encode('utf-8'))
                    wb.open(url, new=2)
                    client_socket.close()
                else:
                    connectToDoctor(client_socket)
                    client_socket.close()
        except:
            continue


def connectToDoctor(client_socket):


    doctorFound = False

    while not doctorFound:
        for socket in clientToDoctor:
            if clients[socket] == "Doctor":
                doctorFound = True

        if doctorFound == False:
            client_socket.send("Waiting for a doctor... \n".encode('utf-8'))
            time.sleep(5)


    session = False
    while not session:
        if len(clientToDoctor) < 2:
            session = True
        else:
            client_socket.send(
                "Doctor is busy... trying again in 5 seconds\n".encode('utf-8'))
            time.sleep(5)

    client_socket.send("You are now connected to a doctor\n".encode('utf-8'))
    client_socket.send("Type 'close' to end this session".encode('utf-8'))

    clientToDoctor.append(client_socket)

    while True:
        try:
            messageDoctor = client_socket.recv(2048)
            messageDoctor = messageDoctor.decode('utf-8')
            if messageDoctor:
                if messageDoctor == 'close\n':
                    print(f"{clients[client_socket]} has left the server")

                    clientToDoctor.remove(client_socket)
                    clientList.remove(client_socket)
                    del clients[client_socket]
                    client_socket.close()
                else:
                    sendMessageToDoctor(client_socket, messageDoctor)
        except:
            continue


# --------------------End of client functions ------------------------------


# ---------------------Start of doctor functions -----------------------------

def sendToClient(message_to_send, client_socket):
    for client in clientToDoctor:

        if client != client_socket:
            try:
                client.send(message_to_send)
            except:
                print(f"{clients[client]} has left the application")


def doctorThread(client_socket):
    client_socket.send(
        "Welcome to the server Doctor. Thank you for your service".encode('utf-8'))
    while True:
        try:
            message = client_socket.recv(2048)
            message = message.decode('utf-8')
            if message == "doctor exiting":
                print("Doctor has left the server")
                clientToDoctor.remove(client_socket)
                clientList.remove(client_socket)
                del clients[client_socket]
                client_socket.close()
            else:
                message_to_send = ("Doctor" + " > " + message).encode('utf-8')
                sendToClient(message_to_send, client_socket)
        except:
            continue

#------------------End of doctor functions ------------------------------------


def clientThread(client_socket, client_address):

    new_user = getNewUser(client_socket)

    username = new_user['data']

    clients[client_socket] = username

    print(f"{username} has connected to the server")

    #-----------code separates here for doctor and patient -------------------
    if username == "Doctor":
        clientToDoctor.append(client_socket)
        doctorThread(client_socket)

    greetUser(client_socket, username)

    question = 0

    answerlist = []


    while True:
        try:
            message = client_socket.recv(2048)
            message = message.decode('utf-8')
            if message in possibleAnswers:
                answerlist.append(message)
                print(answerlist)
                if question > 16:

                    client_socket.send("End of Survey\n".encode('utf-8'))
                    client_socket.send(
                        "We are now checking if you need to be tested\n".encode('utf-8'))

                    confirmation = checkForVirus(answerlist)

                    if confirmation == "positive":
                        client_socket.send(
                            "You will need a test\n Would you like to speak to a doctor?".encode('utf-8'))
                        askForDoctor(client_socket)

                    elif confirmation == "negative":
                        client_socket.send(
                            "You don't need a test\n".encode('utf-8'))
                        print(f"{username} has left the server")
                        client_socket.close()

                sendSurvey(client_socket, question)
                question = question + 1

        except:
            continue



print("Server is now running")

while True:

    client_socket, client_address = server_socket.accept()


    clientList.append(client_socket)


    process = Thread(target=clientThread, args=[
        client_socket, client_address])


    process.daemon = True

    process.start()

    threads.append(process)
