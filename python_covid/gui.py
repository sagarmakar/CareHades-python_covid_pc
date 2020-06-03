import tkinter as tk    
from PIL import Image, ImageTk  
import socket   
import select  
import sys  
import os
import webbrowser
import cv2

# Size of GUI
HEIGHT = 714
WIDTH = 1000
new = 1

root = tk.Tk()  

def sigint_handler(signum, frame):
    print('\n Disconnecting from server')
    sys.exit()


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

IP = "127.0.0.1"
PORT = 42069

client_socket.connect((IP, PORT))


import signal


signal.signal(signal.SIGINT, sigint_handler)


HEADER_LENGTH = 10

def sendUsernameToServer(username_entry):
    username = username_entry.encode('utf-8')
    username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
    client_socket.send(username_header + username)
    checkIO()

def checkIO():
  
    sockets_list = [sys.stdin, client_socket]

  
    read_sockets, write_socket, error_socket = select.select(sockets_list, [], [])

    for socket in read_sockets:

        if socket == client_socket:
            message = socket.recv(2048)
            if not len(message):
                text_label['text'] = "Connection closed by server"
                print("Connection closed by server")
                sys.exit()
                
            text_label['text'] = message.decode('utf-8')
            print(message.decode('utf-8'))

def sendY():

    message = 'y'
    message = message.encode('utf-8')
    client_socket.send(message)
    sys.stdout.flush()
    checkIO()
    client_socket.close()
    
def sendN():

    message = 'n'
    message = message.encode('utf-8')
    client_socket.send(message)
    sys.stdout.flush()
    checkIO()

    client_socket.close()
    
def runheatmap():
	os.system('python3 heatmap.py')
	
def openweb():
	webbrowser.open('https://www.mohfw.gov.in/',new=new)

#-----------------------------------------------------
#-------------GUI-LAYOUT------------------------------
#-----------------------------------------------------

canvas = tk.Canvas(root, height=HEIGHT, width=WIDTH)
canvas.pack()

background_image = tk.PhotoImage(file='background.gif')
background_label = tk.Label(root, image=background_image)
background_label.place(relwidth=1, relheight=1)

covid_label = tk.Label(root, text="COVID-19 Helper", bg="grey")
covid_label.config(font=("Arial", 40))
covid_label.place(relx=0.12, rely=0.1, relwidth=0.76, relheight=0.1)

main_frame = tk.Frame(root, bg="khaki3")
main_frame.place(relx=0.12, rely=0.2, relwidth=0.76, relheight=0.7)

#----------------------------------------------------------

right_frame = tk.Frame(main_frame, bg="grey")
right_frame.place(relx=0.74, rely=0.05, relwidth=0.23, relheight=0.9)

heat_button = tk.Button(right_frame, text="View HeatMap",  bg="green3", activebackground="DarkOlivegreen3", command= runheatmap)
heat_button.place(relx=0.05, rely=0.04, relwidth=0.9, relheight=0.2)

info_button = tk.Button(right_frame, text="Covid-19 HSE Info",  bg="green3", activebackground="DarkOlivegreen3", command=openweb)
info_button.place(relx=0.05, rely=0.28, relwidth=0.9, relheight=0.2)

contact_button = tk.Button(right_frame, text="Heathcare Contacts",  bg="green3", activebackground="DarkOlivegreen3")
contact_button.place(relx=0.05, rely=0.52, relwidth=0.9, relheight=0.2)

doctor_button = tk.Button(right_frame, text="Speak with a doctor",  bg="orange2", activebackground="DarkOrange1")
doctor_button.place(relx=0.05, rely=0.76, relwidth=0.9, relheight=0.2)

#----------------------------------------------------------

left_frame = tk.Frame(main_frame, bg="grey")
left_frame.place(relx=0.03, rely=0.05, relwidth=0.69, relheight=0.9)

text_frame = tk.Frame(left_frame, bg="ghost white")
text_frame.place(relx=0.05, rely=0.05, relwidth= 0.9, relheight=0.6)

text_label = tk.Label(text_frame, bg="ghost white", font=('Courier', 10))
text_label['text'] = "Please enter your username and click\n'Connect to testing server'"
text_label.place(relwidth=1, relheight=1)

server_button = tk.Button(left_frame, text="Connect to testing server",  bg="green3", activebackground="DarkOlivegreen3", command=lambda:sendUsernameToServer(username_entry.get()))
server_button.place(relx=0.05, rely=0.7, relwidth=0.9, relheight=0.05)

username_label = tk.Label(left_frame, text="Username:", bg="DarkSeaGreen1")
username_label.place(relx=0.05, rely=0.77, relwidth=0.2, relheight=0.05)

username_entry = tk.Entry(left_frame, bg="PaleGreen1")
username_entry.place(relx=0.3, rely=0.77, relwidth=0.65, relheight=0.05)

yes_button = tk.Button(left_frame, text="Yes",  bg="green3", activebackground="DarkOlivegreen3", command=sendY)
yes_button.place(relx=0.05, rely=0.84, relwidth=0.44, relheight=0.12)

no_button = tk.Button(left_frame, text="No",  bg="green3", activebackground="DarkOlivegreen3", command=sendN)
no_button.place(relx=0.51, rely=0.84, relwidth=0.44, relheight=0.12)

#----------------------------------------------------------

root.mainloop()
