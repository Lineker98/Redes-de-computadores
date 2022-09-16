import socket, sys


class TCPClient:
    def __init__(self) -> None:
        """_summary_"""
        self.__host = "127.0.0.1"
        self.__port = 20000
        self.__buffer_size = 1024

    def __call__(self) -> None:
        """_summary_"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((self.__host, self.__port))
                print("Servidor executando!")
                while True:

                    dado = input("Digite o texto a ser enviado ao servidor:\n")
                    client_socket.send(
                        dado.encode()
                    )  # texto.encode - converte a string para bytes
                    dado = client_socket.recv(self.__buffer_size)
                    dado_recebido = repr(
                        dado
                    )  # converte de bytes para um formato "printável"
                    print("Recebido do servidor", dado_recebido)
                    if dado_recebido == "bye":
                        print("vai encerrar o socket cliente!")
                        client_socket.close()
                        break
        except Exception as error:
            print("Exceção - Programa será encerrado!")
            print(error)
            return


if __name__ == "__main__":
    client = TCPClient()
    client()
