# encoding: utf-8
# Revisión 2019 (a Python 3 y base64): Pablo Ventura
# Copyright 2014 Carlos Bederián
# $Id: connection.py 455 2011-05-01 00:32:09Z carlos $

from os import listdir
from os.path import getsize, exists, isdir
import socket
from constants import *
from base64 import b64encode


class Connection(object):
    """
    Conexión punto a punto entre el servidor y un cliente.
    Se encarga de satisfacer los pedidos del cliente hasta
    que termina la conexión.
    """

    def __init__(self, socket, directory):
        self.clientsocket = socket
        self.directory = directory
        self.status = CODE_OK
        self.closed = False

    def check_num_args(self, tokens):
        '''
        Comprueba si el comando ingresado tiene la correcta
        cantidad de argumentos.
        '''
        if tokens[0] == 'get_file_listing':
            self.status = CODE_OK if len(tokens) == 1 else INVALID_ARGUMENTS
        elif tokens[0] == 'get_metadata':
            self.status = CODE_OK if len(tokens) == 2 else INVALID_ARGUMENTS
        elif tokens[0] == 'get_slice':
            self.status = CODE_OK if len(tokens) == 4 else INVALID_ARGUMENTS
        elif tokens[0] == 'quit':
            self.status = CODE_OK if len(tokens) == 1 else INVALID_ARGUMENTS

    def check_valid_file(self, filename):
        '''
        Comprueba si un archivo existe en el directorio y que su
        nombre sea valido.
        '''
        if len(filename) < 80:
            path = self.directory + '/' + filename
            if isdir(self.directory):
                set_chars = set(filename)
                self.status = CODE_OK if exists(path) else FILE_NOT_FOUND
                if self.status == CODE_OK:
                    set_chars = set_chars.difference(VALID_CHARS)
                    self.status = CODE_OK if len(set_chars) == 0 else FILE_NOT_FOUND
        else:
            self.status = FILE_NOT_FOUND

    def check_type_args(self, tokens):
        '''
        Comprueba que el tipo de los argumentos de 
        la funcion get_slice sean validos.
        '''
        if tokens[0] == 'get_slice':
            self.status = CODE_OK if tokens[2].isnumeric(
            ) and tokens[3].isnumeric() else INVALID_ARGUMENTS

    def check_valid_values(self, tokens):
        '''
        Comprueba que los valores de los argumentos de 
        la funcion get_slice sean validos.
        '''
        if tokens[0] == 'get_slice':
            filename = tokens[1]
            offset = int(tokens[2])
            size = int(tokens[3])
            path = self.directory + '/' + filename
            file_size = getsize(path)
            valid_position = offset >= 0 and size >= 0 and offset+size <= file_size
            self.status = CODE_OK if valid_position else BAD_OFFSET

    def get_response_message(self, message=''):
        '''
        Arma un mensaje de respuesta en bytes concatenando
        el header y la respuesta del comando.
        '''
        response = str(self.status) + ' ' + error_messages[self.status] + EOL
        if self.status == CODE_OK:
            response += message + EOL
        return response.encode()

    def execute_command(self, tokens):
        '''
        Ejecuta un comando simple.
        '''
        response = ''
        if tokens[0] == 'get_file_listing':
            self.check_num_args(tokens)
            if self.status == CODE_OK:
                if isdir(self.directory):
                    response = self.get_file_listing()
                else:
                    self.status = FILE_NOT_FOUND

        elif tokens[0] == 'get_metadata':
            self.check_num_args(tokens)
            if self.status == CODE_OK:
                self.check_valid_file(tokens[1])
                if self.status == CODE_OK:
                    response = self.get_metadata(tokens[1])

        elif tokens[0] == 'get_slice':
            self.check_num_args(tokens)
            if self.status == CODE_OK:
                filename = tokens[1]
                offset = tokens[2]
                size = tokens[3]
                self.check_valid_file(filename)
                if self.status == CODE_OK:
                    self.check_type_args(tokens)
                    if self.status == CODE_OK:
                        self.check_valid_values(tokens)
                        if self.status == CODE_OK:
                            response = self.get_slice(filename, offset, size)

        elif tokens[0] == 'quit':
            self.check_num_args(tokens)
            if self.status == CODE_OK:
                self.closed = True

        else:  # Comando inexistente
            self.status = INVALID_COMMAND

        return self.get_response_message(response)

    def get_metadata(self, filename):
        '''
        Obtiene el tamaño en bytes de un archivo.
        '''
        path = self.directory + '/' + filename
        size = getsize(path)
        response = str(size)
        return response

    def get_file_listing(self):
        '''
        Obtiene una lista con los archivos del directorio.
        '''
        files = listdir(self.directory)
        response = ''
        for file in files:
            response += file + EOL
        return response

    def get_slice(self, filename, offset, size):
        '''
        Obtiene trozos de un archivo.
        '''
        path = self.directory + '/' + filename
        file = open(path, 'rb')
        file.seek(int(offset))
        content = file.read(int(size))
        file.close()
        cont_decode = b64encode(content).decode()
        return cont_decode

    def handle(self):
        """
        Atiende eventos de la conexión hasta que termina.
        """
        try:
            # Inicializamos la queue de eventos:
            events_queue = ''
            while not self.closed:

                message = self.clientsocket.recv(1024).decode()
                
                # Si no se reciben mensajes cerramos la conexión:
                if len(message) < 1:
                    self.closed = True

                #Agregamos el mensaje a la cola de eventos:
                events_queue += message

                # Una vez que se recibieron comandos completos, tomamos el primer
                # comando de la cola y lo desencolamos.
                # Y tambien ejecutamos todos los comandos que estan el la cola de procesos.
                # Si EOL no esta en la cola de eventos significa que no
                # se ha terminado de recibir el comando.
                # Entonces esperamos a que se termine de formar el comando.
                while events_queue.count(EOL) != 0:

                    simple_command, events_queue = events_queue.split(EOL, 1)

                    # Comprobamos que el comando este bien formado. Caso contrario
                    # enviamos mensaje de error y cerramos conexión:
                    if '\n' in simple_command:
                        self.status = BAD_EOL
                        response = self.get_response_message()
                        self.clientsocket.send(response)
                        break

                    # Obtenemos los argumentos del comando y lo ejecutamos:
                    tokens = simple_command.split()
                    response = self.execute_command(tokens)

                    # Mandamos la respuesta obtenida al cliente:
                    self.clientsocket.send(response)

            # Si la conexión esta cerrada, cerramos el socket.
            self.clientsocket.close()

        # Si ocurre un error con el socket, cerramos la conexion con el cliente.
        except socket.error:
            self.status = INTERNAL_ERROR
            response = self.get_response_message()
            self.clientsocket.send(response)
            self.clientsocket.close()