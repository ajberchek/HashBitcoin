import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("stratum.slushpool.com", 3333))

sock.send("""{"id": 1, "method": "mining.subscribe", "params": []}\n""".encode('utf-8'))
data = sock.recv(4000)
print(data.decode('utf-8'))

sock.send("""{"params": ["btcminer4242.worker1", "Nything"], "id": 2, "method": "mining.authorize"}\n""".encode('utf-8'))
print(sock.recv(4000))

