#Progetto di Programmazione di Reti
#Fabio Pedrini (matricola: 0000916427)
#Parte Server

import tkinter as tk
import socket
import threading
import numpy as np # mi serve per non fare domande già fatte


window = tk.Tk()
window.title("Server")

# Cornice superiore composta da due pulsanti (btnStart, btnStop)
topFrame = tk.Frame(window)
btnStart = tk.Button(topFrame, text="Start", command=lambda : start_server())
btnStart.pack(side=tk.LEFT)
btnStop = tk.Button(topFrame, text="Stop", command=lambda : stop_server(), state=tk.DISABLED)
btnStop.pack(side=tk.LEFT, padx=(10, 0))
topFrame.pack(side=tk.TOP, pady=(5, 0))

# Cornice centrale composta da due etichette per la visualizzazione delle informazioni sull'host e sulla porta
middleFrame = tk.Frame(window)
lblHost = tk.Label(middleFrame, text = "Address: X.X.X.X")
lblHost.pack(side=tk.LEFT)
lblPort = tk.Label(middleFrame, text = "Port:XXXX")
lblPort.pack(side=tk.LEFT)
middleFrame.pack(side=tk.TOP, pady=(5, 0))

# Il frame client mostra l'area dove sono elencati i clients che partecipano al gioco
clientFrame = tk.Frame(window)
lblLine = tk.Label(clientFrame, text="Client List:").pack()
scrollBar = tk.Scrollbar(clientFrame)
scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
tkDisplay = tk.Text(clientFrame, height=10, width=30)
tkDisplay.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
scrollBar.config(command=tkDisplay.yview)
tkDisplay.config(yscrollcommand=scrollBar.set, background="#F4F6F7", highlightbackground="grey", state="disabled")
clientFrame.pack(side=tk.BOTTOM, pady=(5, 10))


server = None
HOST_ADDR = '127.0.0.1'
HOST_PORT = 8080
client_name = " "
clients = []
clients_names = []

questions_made = {}
scores = {}
numQuestions = 12


# Avvia la funzione server
def start_server():
    global server, HOST_ADDR, HOST_PORT, acc_clients
    btnStart.config(state=tk.DISABLED)
    btnStop.config(state=tk.NORMAL)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print (socket.AF_INET)
    print (socket.SOCK_STREAM)

    server.bind((HOST_ADDR, HOST_PORT))
    server.listen(5)  # il server è in ascolto per la connessione del client

    threading._start_new_thread(accept_clients, (server, " "))

    lblHost["text"] = "Address: " + HOST_ADDR
    lblPort["text"] = "Port: " + str(HOST_PORT)


# Arresta la funzione server
def stop_server():
    global server, acc_clients
    btnStart.config(state=tk.NORMAL)
    btnStop.config(state=tk.DISABLED)
    print("\nRESULTS: ", scores)


def accept_clients(the_server, y):
    # mi metto in continua attesa di client che vogliono iniziare a giocare
    while True:
        client, addr = the_server.accept()
        clients.append(client)

        # utilizza un thread in modo da non intasare il thread della gui
        threading._start_new_thread(send_receive_client_message, (client, addr))
        

# Funzione per ricevere e inviare messaggi al client corrente
def send_receive_client_message(client_connection, client_ip_addr):
    global server, client_name, clients, questions_made, numQuestions

    # invia un messaggio di benvenuto al client
    client_name = client_connection.recv(4096)
    client_connection.send("welcome".encode())

    clients_names.append(client_name)
    questions_made[client_name] = 0
    
    # creo gli indici delle domande da inviare al client
    question_indexes = np.arange(1, numQuestions+1, 1)
    # permuto gli indici delle domande in modo che siano inviati in modo casuale
    np.random.shuffle(question_indexes)  
    
    scores[client_name] = []
    update_client_names_display(clients_names)  # aggiornare la visualizzazione dei nomi dei client

    while True:
        data = client_connection.recv(4096)
        if not data: break
        
        if data.startswith("Question".encode()):
            # Controllo che non siano finite le domande
            if questions_made[client_name] < numQuestions:
                question_index = question_indexes[questions_made[client_name]]
                questions_made[client_name] += 1
                client_connection.send(("$question_index" + str(question_index)).encode())
            else:
                client_connection.send("$endgame".encode())
            
        elif data.startswith("TimeOrTrick".encode()):
            # il client ha preso il trabocchetto ho ha finito il tempo, quindi la partita è finita
            client_connection.send("$endgame".encode())
        
        elif data.startswith("Score".encode()):
            # ricevo il punteggio dal client e lo salvo
            score = data.replace("Score".encode(), "".encode()).decode()
            scores[client_name].append(score)

    # trova l'indice del client, quindi lo rimuove da entrambi gli elenchi (elenco dei nomi dei client e elenco delle connessioni)
    idx = get_client_index(clients, client_connection)
    del clients_names[idx]
    del clients[idx]
    client_connection.close()

    update_client_names_display(clients_names)  # aggiorna la visualizzazione dei nomi dei client


# Restituisce l'indice del client corrente nell'elenco dei client
def get_client_index(client_list, curr_client):
    idx = 0
    for conn in client_list:
        if conn == curr_client:
            break
        idx = idx + 1

    return idx


# Aggiorna la visualizzazione del nome del client quando un nuovo client si connette
# o quando un client connesso si disconnette
def update_client_names_display(name_list):
    tkDisplay.config(state=tk.NORMAL)
    tkDisplay.delete('1.0', tk.END)

    for c in name_list:
        tkDisplay.insert(tk.END, c.decode()+"\n")
    tkDisplay.config(state=tk.DISABLED)


window.mainloop()

