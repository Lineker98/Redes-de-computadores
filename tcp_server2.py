import socket
from threading import Thread
import numpy as np


class TCPServer:
    def __init__(self) -> None:
        self.__HOST = "127.0.0.1"
        self.__PORT = 55554
        self.__BUFFER_SIZE = 1024
        self.clients = []
        self.nick_names = []
        self.winners = []
        self.number = None
        self.client_chooser_number = None
        self.client_shooter = None

    def __start_server(self) -> None:
        """Método para iniciar o servidor e deixa-lo escutando"""
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.__HOST, self.__PORT))
        self.server.listen()

    def __get_other_client(self, client: socket.socket) -> socket.socket:
        """Método para a partir de um cliente, encontrar seu par jogador

        Args:
            client (socket.socket): Cliente base para encontar seu jogador par

        Returns:
            client (socket.socket): O outro cliente logado
        """
        other_client = list(
            filter(lambda other_client: other_client != client, self.clients)
        )[0]
        return other_client

    def __send_message(self, message: str, client: socket.socket) -> None:
        """Método para mandar mensagem de um cliente para o outro

        Args:
            message (str): _Mensagem a ser enviada
            client (socket.socket): Cliente que enviará a mensagem
        """
        if len(self.clients) == 2:
            client = self.__get_other_client(client=client)
        client.send(message)

    def _get_nick_name(self, client: socket.socket) -> str:
        """Método para encontrar o nickname de um client a partir
        de index na lista de clientes

        Args:
            client (socket.socket): Cliente para ser encontrado seu nickname

        Returns:
            str: O nick name do cliente
        """
        index__client = self.clients.index(client)
        nick_name = self.nick_names[index__client]
        return nick_name

    def __choose_the_players_roles(self) -> socket.socket:
        """Método para escolher o jogador que escolherá o número

        Returns:
            socket.socket: socketo do jogador que escolheu o número
        """

        if len(self.winners) == 0:
            client_chooser_number = np.random.choice(self.clients, p=[0.5, 0.5])
            client_chooser_number.send("Escolha um numero: ".encode("utf-8"))
            client_chooser_number.send("\nNumero: ".encode("utf-8"))
            nick_name = self._get_nick_name(client=client_chooser_number)
            self.number = client_chooser_number.recv(self.__BUFFER_SIZE).decode("utf-8")
            self.__send_message(
                f"O jogador {nick_name} ja escolheu seu numero".encode("utf-8"),
                client_chooser_number,
            )
            return client_chooser_number

    def multi_player(self, client: socket.socket):
        """Método principal para lidar com dinâmica do jogo

        Args:
            client (socket.socket): _description_
        """

        if len(self.clients) == 2:
            self.client_chooser_number = self.__choose_the_players_roles()

        if len(self.clients) < 2:
            client.send("\nEsperando por um novo jogador...".encode("utf-8"))
            while len(self.clients) < 2 or self.client_chooser_number == None:
                pass

        self.client_shooter = self.__get_other_client(client=self.client_chooser_number)
        nick_name_shooter = self._get_nick_name(client=self.client_shooter)

        while True:
            try:

                self.client_shooter.send("\nDigite sua tentativa:".encode())
                attempt = self.client_shooter.recv(self.__BUFFER_SIZE).decode("utf-8")

                self.client_chooser_number.send(
                    f"\nO jogador {nick_name_shooter} chutou {attempt} \nDe seu feedback:".encode(
                        "utf-8"
                    )
                )
                feedback = self.client_chooser_number.recv(self.__BUFFER_SIZE).decode(
                    "utf-8"
                )
                self.client_shooter.send(feedback.encode("utf-8"))
                if feedback.lower() == "3m0t":
                    self.client_shooter.send("Parabes, voce venceu!".encode("utf-8"))
                    break

            except:

                # Remove and closing clients
                index = self.clients.index(client)
                self.clients.remove(client)
                client.close()

                # removing nickname
                nick_name = self.nick_names[index]
                self.__send_message(f"{nick_name} desistiu do jogo", client)
                self.nick_names.remove(nick_name)
                break

    def __choose_game_mode(self, client: socket.socket) -> str:
        """Método para escolha do método do jogo

        Args:
            client (socket.socket): socket do cliente para escolher o modo de jogo que deseja

        Returns:
            str: Modo de jogo escolhido
        """
        game_mode = ""
        # Ask the game mode
        while game_mode != "s" and game_mode != "m":
            client.send(
                "Selecione o modo de jogo \nM - Multiplayer | S - Single Player:".encode(
                    "utf-8"
                ).strip()
            )
            game_mode = client.recv(self.__BUFFER_SIZE).decode("utf-8").lower()
        return game_mode

    def __call__(self):

        self.__start_server()
        while True:

            # Accept connection
            client, address = self.server.accept()
            print(f"Concetado ao cliente no endereço: {address}")

            game_mode = self.__choose_game_mode(client)

            # Request and store nick name
            client.send("NICK".encode("utf-8"))
            nick_name = client.recv(self.__BUFFER_SIZE).decode("utf-8")
            self.nick_names.append(nick_name)
            self.clients.append(client)

            # Print and broadcast the nikename
            print(f"Nickname is {nick_name}")
            self.__send_message(
                f"{nick_name} se juntou ao jogo".encode("utf-8"), client
            )
            client.send("\nConectado ao servidor".encode("utf-8"))

            thread = Thread(target=self.multi_player, args=(client,))
            thread.start()


if __name__ == "__main__":
    server = TCPServer()
    server()
