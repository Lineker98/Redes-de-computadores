import socket
from threading import Thread
import numpy as np
from typing import Tuple, List


class TCPServer:
    def __init__(self) -> None:
        self.__HOST = "127.0.0.1"
        self.__PORT = 55555
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

    def single_player(self, client: socket.socket, addr: Tuple) -> None:
        """Method to connect a new client and get its data sent

        Args:
            client (socket.socket): The client socket object to manage the connection
            addr (Tuple): Tuple with the port and client address
        """

        number = self.__creat_random_number()
        number = self.__convert_number_in_list(number=number)
        counter_attempts = 0
        print(number)
        while True:
            try:

                client.send(
                    f"\n{self.nick_names[0]}, informe sua tentaiva:".encode("utf-8")
                )
                dado = client.recv(self.__BUFFER_SIZE)
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
                client.send(feed_back.encode())
                if result == "3M0T":
                    win_message = "win"
                    client.send(win_message.encode())
                    print(f"Vai encerrar o socket do cliente {addr[0]} !")
                    client.close()
                    return
            except Exception as error:
                print("Erro na conexão com o cliente")
                return

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

            if game_mode == "m":
                print("m")
                thread = Thread(target=self.multi_player, args=(client,))
                thread.start()
            elif game_mode == "s":
                print("HERE")
                thread = Thread(target=self.single_player, args=(client, address))
                thread.start()


if __name__ == "__main__":
    server = TCPServer()
    server()
