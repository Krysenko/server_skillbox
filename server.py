#
# Серверное приложение для соединений
#
import asyncio
from asyncio import transports



class ServerProtocol(asyncio.Protocol):
    login: str = None
    server: 'Server'
    transport: transports.Transport
    ten_messeges: list

    def __init__(self, server: 'Server'):
        self.server = server
        self.ten_messeges = []

    def data_received(self, data: bytes):
        print(data)

        decoded = data.decode()

        if self.login is not None:
            self.send_message(decoded)
        else:
            if decoded.startswith("login:"):
                login = decoded.replace("login:", "").replace("\r\n", "")
                if login in self.server.logins:
                    self.transport.write(
                        f"Логин {login} занят, попробуйте другой\n".encode()
                    )
                else:
                    self.server.logins.append(login)
                    self.login = login
                    self.transport.write(
                       f"Привет, {self.login}!\n".encode()
                    )
                    for i in range(len(ten_messeges)):
                        self.transport.write(ten_messeges[i].encode())

            else:
                self.transport.write("Неправильный логин\n".encode())

    def connection_made(self, transport: transports.Transport):
        self.server.clients.append(self)
        self.transport = transport
        print("Пришел новый клиент")

    def connection_lost(self, exception):
        self.server.clients.remove(self)
        print("Клиент вышел")

    def add_ten_messeges(self, inf: str):
        if len(ten_messeges) < 10:
            ten_messeges.append(inf)
        else:
            for i in range(9):
                ten_messeges[i] = ten_messeges[i + 1]
            ten_messeges[9] = inf

    def send_message(self, content: str):
        message = f"{self.login}: {content}\n"
        self.add_ten_messeges(message)
        for user in self.server.clients:
            user.transport.write(message.encode())


class Server:
    clients: list
    logins: list


    def __init__(self):
        self.clients = []
        self.logins = []


    def build_protocol(self):
        return ServerProtocol(self)

    async def start(self):
        loop = asyncio.get_running_loop()

        coroutine = await loop.create_server(
            self.build_protocol,
            '127.0.0.1',
            9999
        )

        print("Сервер запущен ...")

        await coroutine.serve_forever()


process = Server()

try:
    asyncio.run(process.start())
except KeyboardInterrupt:
    print("Сервер остановлен вручную")
