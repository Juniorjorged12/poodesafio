import textwrap
from abc import ABC, abstractclassmethod, abstractproperty


class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self,conta,transacao):
        transacao.registrar(conta)


    def adicionar_conta(self, conta):
        self.contas.append(conta)


class Pessoa_fisica(Cliente):
    def __init__(self, nome, nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.nascimento = nascimento
        self.cpf = cpf


class Conta:
    def __init__(self,numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = '0001'
        self._cliente = cliente
        self._historico = Historico()


    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero,cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico


    def sacar(self, valor):
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            print('Você não tem saldo suficiente !!!!')
        elif valor > 0 :
            self._saldo -= valor
            print('Saque realizado com sucesso')
            return True
        else:
            print('O valor informado é inválido')

        return False


    def depositar(self, valor):
        if valor >0:
            self._saldo += valor
            print('Depósito realizado com sucesso')
        else:
            print('Digite um valor valido para deposito!!!')
            return False

        return True


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite = 500, limite_saques = 3):
        super().__init__(numero,cliente)
        self.limite = limite
        self.limite_saques = limite_saques

    def sacar(self,valor):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao['tipo'] == Saque.__name__]

        )

        excedeu_limite = valor > self.limite
        excedeu_saques = numero_saques >= self.limite_saques

        if excedeu_limite:
            print('O valor a ser sacado excedeu o limite diário!')
        elif excedeu_saques:
            print('Voce atingiu o limite de saques diário')
        else:
            return super().sacar(valor)
        return False

    def __str__(self):
        return  f'''
            Agencia: {self.agencia}
            C/C : {self.numero}
            Titular: {self.cliente.nome}
        '''


class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                'tipo': transacao.__class__.__name__,
                'valor': transacao.valor,

            }
        )


class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractclassmethod
    def registrar(cls, conta):
        pass



class Saque(Transacao):
    def __init__(self,valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self,conta):
        sucesso_transacao = conta.sacar(self.valor)
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):

    def __init__(self,valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self,conta):
        sucesso_transacao = conta.depositar(self.valor)
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


def menu ():
    menu = '''
    ======= MENU ======
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    [nc]\tNova Conta
    [lc]\tLista Contas
    [nu]\tNovo Usuario 
    [q]\tSair
    =>> '''
    return input(textwrap.dedent(menu))

def filtrar_cliente(cpf,clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None

def recuperar_conta(cliente):
    if not cliente.contas:
        print('Cliente nao possui conta')
        return
    # FIXME: Não permite o cliente escolher a conta
    return cliente.contas[0]

def depositar(clientes):
    cpf = input('Digite o CPF do cliente: ')
    cliente = filtrar_cliente(cpf,clientes)
    if not cliente:
        print('Cliente nao registrado em nosso sistema')
        return
    valor = float(input('INforme o valor do deposito: '))
    transacao = Deposito(valor)

    conta = recuperar_conta(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta,transacao)

def sacar(clientes):
    cpf = input('Digite o CPF do cliente: ')
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print('Cliente nao registrado em nosso sistema')
        return
    valor = float(input('INforme o valor do saque: '))
    transacao = Saque(valor)

    conta = recuperar_conta(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


def extrato(clientes):
    cpf = input('Digite o CPF do cliente: ')
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print('Cliente nao registrado em nosso sistema')
        return
    conta = recuperar_conta(cliente)
    if not conta:
        return

    print('====== EXTRATO ======')
    transacoes = conta.historico.transacoes
    extrato = ''
    if not transacoes:
        extrato = 'Nao foram realizadas movimentações na sua conta'
    else:
        for transacao in transacoes:
            extrato += f'{transacao["tipo"]}:\n\tR${transacao["valor"]:.2f} '

    print(extrato)
    print(f'\nSaldo:\n\tR$ {conta.saldo:.2f}')
    print('='*20)

def criar_cliente(clientes):
    cpf = input('Digite o CPF do cliente: ')
    cliente = filtrar_cliente(cpf, clientes)
    if  cliente:
        print('Cliente ja registrado em nosso sistema')
        return

    nome = input('Nome completo do cliente: ')
    data_nascimento = input('Data d enascimento (dd-mm-aaaa): ')
    endereco = input('Endereço completo (Logradouro, nro - bairro - cidade/UF: ')
    cliente = Pessoa_fisica(nome=nome, nascimento=data_nascimento,cpf=cpf,endereco = endereco)
    clientes.append(cliente)
    print('Cliente criado com sucesso!!!!')

def criar_conta(numero_conta,clientes,contas):
    cpf = input('Digite o CPF do cliente: ')
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print('Cliente nao registrado em nosso sistema')
        return
    conta = ContaCorrente.nova_conta(cliente=cliente, numero = numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)
    print('Conta criada com sucesso!!!')

def listar_contas(contas):
    for conta in contas:
        print('='*100)
        print(textwrap.dedent(str(conta)))


def main():
    clientes = []
    contas = []
    while True:
        opcao = menu()

        if opcao == 's':
            sacar(clientes)

        elif opcao == 'd':
            depositar(clientes)

        elif opcao == 'e':
            extrato(clientes)

        elif opcao == 'nu':
            criar_cliente(clientes)

        elif opcao == 'nc':
            numero_conta = len(contas)+1
            criar_conta(numero_conta,clientes,contas)

        elif opcao == 'lc':
            listar_contas(contas)

        elif opcao == 'q':
            break



main()
