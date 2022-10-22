import socket
from threading import Thread, ThreadError


class TCPCLient:
    def __init__(self) -> None:
        self.__HOST = "127.0.0.1"
        self.__PORT = 55554
        self.__BUFFER_SIZE = 1024
        self.attempts = []
        self.counter_attemps = 0

    def __start_client(self) -> None:
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.__HOST, self.__PORT))

    def receive(self):
        while True:
            try:

                # receive Message from server
                # If nick, senf nickname
                message = self.client.recv(self.__BUFFER_SIZE).decode("ascii")
                if message == "NICK":
                    self.client.send(self.nickname.encode("ascii"))
                else:
                    print(message)
            except:
                # close connection when error
                print("An error occured!")
                self.client.close()
                break

    def send_message(self):
        while True:
            message = f"{input('')}"
            self.client.send(message.encode("ascii"))

    def __call__(self) -> None:
        self.__start_client()
        self.nickname = input("Choose your nickname: ")
        self.receive_thread = Thread(target=self.receive)
        self.receive_thread.start()

        self.send_message = Thread(target=self.send_message)
        self.send_message.start()


if __name__ == "__main__":
    client = TCPCLient()
    client()
