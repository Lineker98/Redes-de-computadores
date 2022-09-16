import socket
from threading import Thread
from typing import Tuple


class TCPServer:
    def __init__(self) -> None:
        self.__host = "127.0.0.1"
        self.__port = 20000
        self.__buffer_size = 1024

    def on_new_client(self, client_socket: socket.socket, addr: Tuple) -> None:
        """_summary_

        Args:
            client_socket (socket.socket): _description_
            addr (Tuple): _description_
        """
        while True:
            try:
                dado = client_socket.recv(self.__buffer_size)
                if not dado:
                    break

                dado_recebido = dado.decode("utf-8")
                print(
                    f"Recebido do cliente {addr[0]} na porta {addr[1]}: {dado_recebido}"
                )

                # Envia o mesmo texto ao cliente
                client_socket.send(dado)
                if dado_recebido == "bye":
                    print(f"vai encerrar o socket do cliente {addr[0]} !")
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
