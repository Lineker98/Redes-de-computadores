import socket
import pickle


class TCPClient:
    def __init__(self) -> None:
        """_summary_"""
        self.__host = "127.0.0.1"
        self.__port = 20000
        self.__buffer_size = 1024
        self.attempts = []

    def __call__(self) -> None:
        """_summary_"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((self.__host, self.__port))
                print("Servidor executando!")
                while True:

                    client_entry = input("Digite sua tentativa!: ")
                    client_socket.send(
                        client_entry.encode()
                    )  # texto.encode - converte a string para bytes

                    server_response = client_socket.recv(self.__buffer_size)
                    server_response = (
                        server_response.decode()
                    )  # converte de bytes para um formato "printável"

                    # Store the history attempts
                    self.attempts.append(server_response)
                    print("Histórico de tentativas:")
                    print(*self.attempts, sep="\n")

                    if server_response == "bye":
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
