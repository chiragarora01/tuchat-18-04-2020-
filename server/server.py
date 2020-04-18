from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import time
from person import Person

HOST = "localhost"
PORT = 5500
ADDR = (HOST, PORT)
MAX_CONNECTION = 1
BUFFSIZ = 1024

persons = []
SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)


def broadcast(msg, name):
    for person in persons:
        client = person.client
        client.send(bytes(name, "utf8" + msg))


def client_communication(person):
    '''handle all messages from client'''
    client = person.client

    name = client.recv(BUFFSIZ).decode("utf8")
    person.set_name(name)
    msg = bytes(f"{name} has joined the chat", "utf8")
    broadcast(msg, name)

    while True:
        try:
            msg = client.recv(BUFFSIZ)
            print(f"{name}:", msg.decode("utf8"))
            if msg == bytes("{quit}", "utf8"):
                broadcast(f"{name} has left the chat ...", "")
                client.send(bytes("{quit}", "utf8"))
                client.close()
                persons.remove(person)
                break
            else:
                broadcast(msg, name+": ")
        except Exception as e:
            print("[EXCEPTION]", e)
            break


def wait_for_connection():
    '''wait for connection from new clients ,start new thread'''
    run = True
    while run:
        try:
            client, addr = SERVER.accept()
            person = Person(addr, client)
            persons.append(person)
            print(f"[CONNECTION] {addr} connected to server at {time.time()} ")
            Thread(target=client_communication, args=(person,)).start()
        except Exception as e:
            print("[EXCEPTION]", e)
            run = False

    print("server crash")


SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

if __name__ == "__main__":
    SERVER.listen(MAX_CONNECTION)
    print("waiting for connection")
    ACCEPT_THREAD = Thread(target=wait_for_connection)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()
