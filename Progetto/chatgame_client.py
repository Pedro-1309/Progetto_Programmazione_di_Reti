#Progetto di Programmazione di Reti
#Fabio Pedrini (matricola: 0000916427)
#Parte Client

import tkinter as tk
from tkinter import PhotoImage
import socket
from time import sleep
import threading
import random

# FINESTRA DI GIOCO PRINCIPALE
window_main = tk.Tk()
window_main.title("Game Client")

your_name = ""
game_timer = 30
start_game = 5
#Qui verrà scritta la risposta data dall'utente
your_answer = tk.StringVar()
your_choice = 0
your_score = 0
questions = {
    '1': ["7 x 8 ?", "56"],
    '2': ["Quante sono le regioni d'Italia?", "20"],
    '3': ["Qual è il capoluogo della Lombardia?", "Milano"],
    '4': ["Quanti gol ha fatto l'Italia contro la Turchia?", "3"],
    '5': ["Da quale città provengono i Beatles?", "Liverpool"],
    '6': ["Quante sono le stelle sulla bandiera americana?", "50"],
    '7': ["Qual è il fiume più lungo del mondo?", "Nilo"],
    '8': ["Quale terra si trova tra il Tigri e l'Eufrate?", "Mesopotamia"],
    '9': ["Quanti giorni ha il mese di giugno?", "30"],
    '10': ["Quante sono le corde di una chitarra classica?", "6"],
    '11': ["Quanti giocatori compongono una squadra di basket?", "5"],
    '12': ["Quanti anni ha la Regina Elisabetta?", "95"]
}
numQuestions = len(questions)
question_index = 1

# client di rete
client = None
HOST_ADDR = '127.0.0.1'
HOST_PORT = 8080
sck_closed = False


top_welcome_frame= tk.Frame(window_main)
lbl_name = tk.Label(top_welcome_frame, text = "Name:")
lbl_name.pack(side=tk.LEFT)
ent_name = tk.Entry(top_welcome_frame)
ent_name.pack(side=tk.LEFT)
btn_connect = tk.Button(top_welcome_frame, text="Connect", command=lambda : connect())
btn_connect.pack(side=tk.LEFT)
top_welcome_frame.pack(side=tk.TOP)

top_message_frame = tk.Frame(window_main)
lbl_line = tk.Label(top_message_frame, text="***********************************************************").pack()
lbl_welcome = tk.Label(top_message_frame, text="")
lbl_welcome.pack()
lbl_line_server = tk.Label(top_message_frame, text="***********************************************************")
lbl_line_server.pack_forget()
top_message_frame.pack(side=tk.TOP)


top_frame = tk.Frame(window_main)
top_left_frame = tk.Frame(top_frame, highlightbackground="green", highlightcolor="green", highlightthickness=1)
lbl_your_name = tk.Label(top_left_frame, text="Name: " + your_name, font = "Helvetica 13 bold")
lbl_your_score = tk.Label(top_left_frame, text="Score: " + str(your_score), font = "Helvetica 13 bold")
lbl_your_name.grid(row=0, column=0, padx=5, pady=8)
lbl_your_score.grid(row=1, column=0, padx=5, pady=8)
top_left_frame.pack(side=tk.LEFT, padx=(10, 10))


top_right_frame = tk.Frame(top_frame, highlightbackground="green", highlightcolor="green", highlightthickness=1)
lbl_time_left = tk.Label(top_right_frame, text="     Time left:     ", foreground="blue", font = "Helvetica 14 bold")
lbl_timer = tk.Label(top_right_frame, text=" ", font = "Helvetica 24 bold", foreground="blue")
lbl_time_left.grid(row=0, column=0, padx=5, pady=5)
lbl_timer.grid(row=1, column=0, padx=5, pady=5)
top_right_frame.pack(side=tk.RIGHT, padx=(10, 10))

top_frame.pack_forget()

middle_frame = tk.Frame(window_main)

lbl_line = tk.Label(middle_frame, text="***********************************************************").pack()
lbl_line = tk.Label(middle_frame, text="**** GAME LOG ****", font = "Helvetica 13 bold", foreground="blue").pack()
lbl_line = tk.Label(middle_frame, text="***********************************************************").pack()

round_frame = tk.Frame(middle_frame)
lbl_desc = tk.Label(round_frame, text="Choose a letter and answer the question you get!")
lbl_desc.pack()
lbl_your_choice = tk.Label(round_frame, text="Your choice: " + "None", font = "Helvetica 12 bold")
lbl_your_choice.pack()
lbl_question = tk.Label(round_frame, text="Question: " + "None", font = "Helvetica 12 bold")
lbl_question.pack()
lbl_result = tk.Label(round_frame, text=" ", foreground="blue", font = "Helvetica 14 bold")
lbl_result.pack()
round_frame.pack(side=tk.TOP)

final_frame = tk.Frame(middle_frame)
lbl_line = tk.Label(final_frame, text="***********************************************************").pack()
lbl_final_result = tk.Label(final_frame, text=" ", font = "Helvetica 15 bold", foreground="blue")
lbl_final_result.pack()
lbl_line = tk.Label(final_frame, text="***********************************************************").pack()
final_frame.pack(side=tk.TOP)

middle_frame.pack_forget()

#Creo il campo di input e lo associo alla variabile your_answer
textbox_frame = tk.Frame(middle_frame)
lbl_answer = tk.Label(textbox_frame, text = "Answer:")
lbl_answer.pack(side=tk.LEFT)
entry_field = tk.Entry(textbox_frame, textvariable=your_answer, state=tk.DISABLED)
entry_field.pack(side=tk.LEFT)

send_button = tk.Button(textbox_frame, text="Send", command=lambda : game_logic(question_index), state=tk.DISABLED)
send_button.pack(side=tk.LEFT)
textbox_frame.pack(side=tk.TOP)

button_frame = tk.Frame(window_main)
photo_a = PhotoImage(file = r"a.gif")
photo_b = PhotoImage(file = r"b.gif")
photo_c = PhotoImage(file = r"c.gif")
btn_a = tk.Button(button_frame, text="A", command=lambda : choice(0), state=tk.DISABLED, image=photo_a)
btn_b = tk.Button(button_frame, text="B", command=lambda : choice(1), state=tk.DISABLED, image=photo_b)
btn_c = tk.Button(button_frame, text="C", command=lambda : choice(2), state=tk.DISABLED, image=photo_c)
btn_a.grid(row=0, column=0)
btn_b.grid(row=0, column=1)
btn_c.grid(row=0, column=2)
button_frame.pack(side=tk.BOTTOM)

def enable_disable_buttons(todo):
    if todo == "disable":
        btn_a.config(state=tk.DISABLED)
        btn_b.config(state=tk.DISABLED)
        btn_c.config(state=tk.DISABLED)
    else:
        btn_a.config(state=tk.NORMAL)
        btn_b.config(state=tk.NORMAL)
        btn_c.config(state=tk.NORMAL)
        
def enable_disable_textbox(todo):
    if todo == "disable":
        send_button.config(state=tk.DISABLED)
        entry_field.config(state=tk.DISABLED)
    else:
        send_button.config(state=tk.NORMAL)
        entry_field.config(state=tk.NORMAL)


def game_logic(index):
    global your_score, questions, your_answer
    guess = your_answer.get()
    your_answer.set("")   #libero la zona di input della risposta
    question, answer = questions[index]
    if guess == answer:
        your_score += 1
        lbl_result["text"] = "CORRECT!"
    else:
        your_score -= 1
        lbl_result["text"] = "WRONG!"
    lbl_your_score["text"] = "Score: " + str(your_score)
    enable_disable_buttons("enable")
    enable_disable_textbox("disable")
    

def connect():
    global name
    if len(ent_name.get()) < 1:
        tk.messagebox.showerror(title="ERROR!!!", message="You MUST enter your first name <e.g. John>")
    else:
        name = ent_name.get()
        lbl_your_name["text"] = "Your name: " + name
        connect_to_server(name)


def count_down(my_timer, nothing):
    global client
    flag = my_timer > start_game
    while my_timer > 0:
        my_timer = my_timer - 1
        print("game timer is: " + str(my_timer))
        if sck_closed:  #se il socket è stato chiuso, la partita è finita, il countdown non serve
            my_timer = 0
        lbl_timer["text"] = my_timer
        sleep(1)
        
    #se ho fatto il countdown di tutto il round e il socket non è stato chiuso, invio il segnale al server
    if flag and not sck_closed:   
        client.send(("TimeOrTrick"+str(your_score)).encode())
        

def choice(arg):
    global your_choice, client, questions
    trick = random.randint(0, 3)
    your_choice = arg
    
    if your_choice == trick:     #trabocchetto
        lbl_your_choice["text"] = "Your choice: TRICK!!"
        if not sck_closed:
            client.send(("TimeOrTrick"+str(your_score)).encode())
            
    else:           #domanda
        lbl_your_choice["text"] = "Your choice: Question"
        if client:
            enable_disable_buttons("disable")
            enable_disable_textbox("enable")
            client.send(("Question"+str(your_choice)).encode()) #invio la stringa "Question1" per esempio
            
    lbl_result["text"] = ""
    lbl_question["text"] = "Question: None"
    

def connect_to_server(name):
    global client, HOST_PORT, HOST_ADDR
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST_ADDR, HOST_PORT))
        client.send(name.encode()) # Invia il nome al server dopo la connessione

        # disable widgets
        btn_connect.config(state=tk.DISABLED)
        ent_name.config(state=tk.DISABLED)
        lbl_name.config(state=tk.DISABLED)
        enable_disable_buttons("disable")

        # avvia un thread per continuare a ricevere messaggi dal server
        # non bloccare il thread principale
        threading._start_new_thread(receive_message_from_server, (client, "m"))
    except Exception as e:
        tk.messagebox.showerror(title="ERROR!!!", message="Cannot connect to host: " + HOST_ADDR + " on port: " + str(HOST_PORT) + " Server may be Unavailable. Try again later")



    
def receive_message_from_server(sck, m):
    global your_name, question_index, sck_closed, your_choice, your_score

    while True:
        from_server = sck.recv(4096)

        if not from_server: break

        if from_server.startswith("welcome".encode()):
            lbl_welcome["text"] = "Master says: Welcome " + name + "! Game will start soon"
            lbl_line_server.pack()

            lbl_your_score["text"] = "Score: " + str(your_score)
            top_frame.pack()
            middle_frame.pack()

            # il gioco è pronto per iniziare
            lbl_time_left["text"] = "   Game starts in:  "
            threading._start_new_thread(count_down, (start_game, ""))
            enable_disable_buttons("disable")
            lbl_result["text"] = ""
            sleep(start_game)
            lbl_welcome.config(state=tk.DISABLED)
            lbl_line_server.config(state=tk.DISABLED)
            
            enable_disable_buttons("enable")
            lbl_time_left["text"] = "      Time left:    "
            threading._start_new_thread(count_down, (game_timer, ""))

        elif from_server.startswith("$question_index".encode()):
            # ottieni l'indice della domanda dal server
            question_index = from_server.replace("$question_index".encode(), "".encode()).decode()
            
            # Aggiorno la GUI
            question, answer = questions.get(question_index)
            lbl_question["text"] = "Question: " + question
            #questions_made.append(question_index)
            enable_disable_textbox("enable")
            enable_disable_buttons("disable")
                
                
        elif from_server.startswith("$endgame".encode()):
            #la partita è finita, mando i risultati al server
            client.send(("Score"+str(your_score)).encode())
            lbl_final_result["text"] = "FINAL RESULT: " + str(your_score)
            enable_disable_buttons("disable")
            enable_disable_textbox("disable")
            break
    
    #controllo che il socket non sia già stato chiuso
    if not sck_closed:
        sck_closed = True
        sck.close()
        
window_main.mainloop()

