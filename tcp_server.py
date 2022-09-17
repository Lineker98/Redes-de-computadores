import socket
from threading import Thread
from typing import Tuple, List
import numpy as np


class TCPServer:
    def __init__(self) -> None:
        self.__host = "127.0.0.1"
        self.__port = 20000
        self.__buffer_size = 1024

    def __convert_number_in_list(self, number: int) -> List[str]:
        """_summary_

        Args:
            number (int): _description_

        Returns:
            List[str]: _description_
        """
        number = [x for x in str(number)]
        return number

    def __analize_shot(self, true_number: List[str], number_guess: List[str]) -> str:
        """_summary_

        Args:
            true_number (List[str]): _description_
            user_guess (List[str]): _description_

        Returns:
            str: _description_
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

    def on_new_client(self, client_socket: socket.socket, addr: Tuple) -> None:
        """_summary_

        Args:
            client_socket (socket.socket): _description_
            addr (Tuple): _description_
        """

        number = np.random.randint(low=100, high=1000)
        number = self.__convert_number_in_list(number=number)
        print(number)
        while True:
            try:
                dado = client_socket.recv(self.__buffer_size)
                if not dado:
                    break

                dado_recebido = dado.decode("utf-8")
                print(
                    f"Tentativa do cliente {addr[0]} na porta {addr[1]}: {dado_recebido}"
                )
                dado_recebido = self.__convert_number_in_list(dado_recebido)
                result = self.__analize_shot(
                    true_number=number, number_guess=dado_recebido
                )
                print(result)
                # Envia o mesmo texto ao cliente
                client_socket.send(dado)
                if result == "0T3M":
                    print("Parabéns, você venceu!")
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
