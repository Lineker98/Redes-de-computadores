import socket
from threading import Thread
from typing import Tuple, List
import numpy as np
import pickle


class TCPServer:
    def __init__(self) -> None:
        self.__host = "127.0.0.1"
        self.__port = 20000
        self.__buffer_size = 1024

    def __convert_number_in_list(self, number: int) -> List[str]:
        """Method to  convert n digits number into a list of n elements

        Args:
            number (int): The number to be converted

        Returns:
            List[str]: The list which the number mapped to a element
        """
        number = [x for x in str(number)]
        return number

    def __analize_shot(self, true_number: List[str], number_guess: List[str]) -> str:
        """Method to analise how many numbers of the current attempt match with the true number

        Args:
            true_number (List[str]): The number which the user is trying to guess
            user_guess (List[str]): The user shot

        Returns:
            str: How many numbers match wth the right index (nM) and
            match but with the wrong index (nT), eg., nMnT being n from 0 to 3
        """
        tiro = mosca = 0
        for index, number in enumerate(number_guess):
            if number in true_number:
                real_indexes = np.where(np.array(true_number) == number)[0]
                if index in real_indexes:
                    mosca += 1
                else:
                    tiro += len(real_indexes)
        output = str(mosca) + "M" + str(tiro) + "T"
        return output

    def __creat_random_number(self):
        """Method to generate a random number avoiding repeat the ddigits"""
        list_digits = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
        number = np.random.choice(list_digits, 3, replace=False)
        number = map(str, number)
        number = "".join(number)
        return int(number)

    def on_new_client(self, client_socket: socket.socket, addr: Tuple) -> None:
        """Method to connect a new client and get its data sent

        Args:
            client_socket (socket.socket): The client socket object to manage the connection
            addr (Tuple): Tuple with the port and client address
        """

        number = self.__creat_random_number()
        number = self.__convert_number_in_list(number=number)
        counter_attempts = 0
        print(number)
        while True:
            try:
                dado = client_socket.recv(self.__buffer_size)
                if not dado:
                    break
                counter_attempts += 1
                client_entry = dado.decode("utf-8")
                print(
                    f"Tentativa do cliente {addr[0]} na porta {addr[1]}: {client_entry}"
                )
                attempt_treated = self.__convert_number_in_list(client_entry)

                result = self.__analize_shot(
                    true_number=number, number_guess=attempt_treated
                )

                feed_back = client_entry + " - " + result
                client_socket.send(feed_back.encode())
                if result == "3M0T":
                    win_message = "win"
                    client_socket.send(win_message.encode())
                    print(f"Vai encerrar o socket do cliente {addr[0]} !")
                    client_socket.close()
                    return
            except Exception as error:
                print("Erro na conexão com o cliente")
                return

    def __call__(self) -> None:
        try:
            # AF_INET: indica o protocolo IPv4. SOCK_STREAM: tipo de socket para TCP
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                server_socket.bind((self.__host, self.__port))
                while True:
                    server_socket.listen()
                    client_socket, addr = server_socket.accept()
                    print(f"Concetado ao cliente no endereço: {addr}")
                    thread = Thread(
                        target=self.on_new_client, args=(client_socket, addr)
                    )
                    thread.start()
        except Exception as error:
            print("Erro na execução do servidor")
            print(error)
            return


if __name__ == "__main__":
    server = TCPServer()
    server()
