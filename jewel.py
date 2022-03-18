##!/usr/bin/env python3

import socket
import sys
import select
from file_reader import FileReader
import queue
import os

class Jewel:

    # Note, this starter example of using the socket is very simple and
    # insufficient for implementing the project. You will have to modify this
    # code.
    def __init__(self, port, file_path, file_reader):
        self.file_path = file_path
        self.file_reader = file_reader
        #ip = socket.gethostbyname(socket.gethostname())
        ip = '0.0.0.0'
        #print('0.0.0.0', port)
        #192.168.56.1 80
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((ip, port))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #s.setblocking(False)
        s.listen(5)
        
        inputs = [s]
        outputs = []
        message_queues = {}
        
        #print(address)
        while inputs:

            readable, writable, exceptional = select.select(inputs, outputs, inputs)
            for server in readable:
                if server is s:
                    (client, address) = server.accept()
                    sys.stdout.write('[CONN] Connection from {} on port {}\n'.format(address[0], address[1]))
                    client.setblocking(0)
                    inputs.append(client)
                    message_queues[client] = queue.Queue()
                else:
                    data = server.recv(2**18).decode()
                    if data:
                        message_queues[server].put(data)
                        if server not in outputs:
                            outputs.append(server)
                    else:
                        if server in outputs:
                            outputs.remove(server)
                        inputs.remove(server)
                        server.close()
                        print("closed")
                        del message_queues[server]

            for server in writable:
                try: 
                    data = message_queues[server].get_nowait()
                    header_end = data.find('\r\n\r\n')
                    if header_end > -1:
                        header_string = data[:header_end]
                        lines = header_string.split('\r\n')
                        #print(lines)
                        request_fields = lines[0].split()
                        real_path = file_path + request_fields[1]
                        print(real_path)
                        if len(request_fields) != 3:
                            sys.stdout.write('[ERRO] 400 Bad Request')
                            server.sendall(b"HTTP/1.1 400 Bad Request\r\n")
                        if request_fields[0] == 'GET':        
                            body = file_reader.get(real_path, "")
                            header = file_reader.head(real_path, "")
                            #print("header", header, type(header))
                            if body:
                                sys.stdout.write('[REQU] [{}:{}] GET request for {}\n'.format(server.getpeername()[0], server.getpeername()[1], real_path))
                                server.sendall(b"HTTP/1.1 200 OK\r\n")
                                server.sendall(("Server: tg2vpw\r\nContent-Length: {:}\r\n\r\n".format(header)).encode())
                                #server.sendall(("Content-Length: {:}\r\n\r\n".format(header)).encode())
                                server.sendall(body)
                            else:
                                #404 error, none
                                sys.stdout.write('[ERRO] [{}:{}] GET request returned error 404\n'.format(server.getpeername()[0], server.getpeername()[1]))
                                #rint("404, error")
                                server.sendall(b"HTTP/1.1 404 NOT FOUND\r\n")
                                server.sendall(("Server: tg2vpw\r\nContent-Length: {:}\r\n\r\n".format(1)).encode())
                                #server.sendall(("Content-Length: {:}\r\n\r\n".format(1)).encode())
                        elif request_fields[0] == 'HEAD': 
                            #header = file_reader.head(path, "")
                            #response = file_reader.get(path, "")
                            header = file_reader.head(real_path, "")
                            if header:
                                #print("200, no error")
                                sys.stdout.write('[REQU] [{}:{}] HEAD request for {}\n'.format(server.getpeername()[0], server.getpeername()[1], real_path))
                                server.sendall(b"HTTP/1.1 200 OK\r\n")
                                server.sendall(("Server: tg2vpw\r\nContent-Length: {:}\r\n\r\n".format(header)).encode())
                                #server.sendall(("Content-Length: {:}\r\n\r\n".format(header)).encode())
                                
                            else:
                                #404 error, none
                               # print("404, error")
                                sys.stdout.write('[ERRO] [{}:{}] HEAD request returned error 404\n'.format(server.getpeername()[0], server.getpeername()[1]))
                                server.sendall(b"HTTP/1.1 404 NOT FOUND\r\n")
                                server.sendall(("Server: tg2vpw\r\nContent-Length: {:}\r\n\r\n".format(1)).encode())
                                #server.sendall(("Content-Length: {:}\r\n\r\n".format(1)).encode())

                        else:
                            #header = file_reader.head(path, "")
                            #print("501, not implemented")
                            sys.stdout.write('[ERRO] [{}:{}] {} request returned error 501\n'.format(server.getpeername()[0], server.getpeername()[1], request_fields[0]))
                            server.sendall(b"HTTP/1.1 501 Not Implemented\r\n")
                            server.sendall(("Server: tg2vpw\r\nContent-Length: {:}\r\n\r\n".format(header)).encode())
                            #server.sendall(("Content-Length: {:}\r\n\r\n".format(1)).encode())
                        # client.close()
                    else:
                        sys.stdout.write('[ERRO] 400 Bad Request')
                        server.sendall(b"HTTP/1.1 400 Bad Request\r\n")
                except queue.Empty:
                    outputs.remove(server)


                
                    

            for server in exceptional:
                inputs.remove(server)
                if server in outputs:
                    outputs.remove(server)
                server.close()



            #parsing
            
        s.close()
    

if __name__ == "__main__":
    port = os.environ.get('PORT', 5000)
    file_path = './pic'

    FR = FileReader()

    J = Jewel(port, file_path, FR)
    
    