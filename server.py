import os
import socket
import threading
import shutil
import configHelper
from fileinuse_functions import is_file_in_use

#IP = socket.gethostbyname(socket.gethostname())
IP = "0.0.0.0"
PORT = 4456
IPANDPORT = (IP, PORT)
SIZE = 1024
config_file = "fileupload.ini"
lockfile = "ord.lock"
path = configHelper.read_config(config_file, "fileupload", "path", default_value="C:\\Users\\Administrator\\Documents\\ord_receiver")
def handle_client(client, addr):
    print(f"Client {addr} has Connected")
    if os.path.isfile(os.path.join(path, lockfile)):
        if not is_file_in_use:
            os.remove(os.path.join(path, lockfile))
        else:
            client.shutdown(socket.SHUT_RDWR)
    filename = str(client.recv(SIZE).decode())
    filename = filename.rstrip('\r\n')
    client.send("SENT".encode())
    print(filename)
    filesize = int(client.recv(SIZE).decode())
    client.send("SENT".encode())
    print(filesize)

    file = open(filename, 'wb')

    filebytes = bytearray()

    done = False
    print("Getting Data...\n")
    number = 0
    while not done:
        data = client.recv(filesize)
        client.send("SENT".encode())
        number = number + 1
        print(number, end='\r')
        if filebytes[-5:] == b"<END>":
            done = True
            print("\n")
            filebytes = filebytes.replace(b'<END>', b'')
        else:
            filebytes += data
            filebytes = filebytes.rstrip(b'\r\n')
    print("Got Data..")
    file.write(filebytes)
    file.close()
    client.close()
    print(f"Done : Saved {filename}...")
    filepath = os.path.join(path, filename)
    if os.path.isfile(filepath) == True:
        os.remove(filepath)
    shutil.move(filename, filepath)
    print(f"Moved {filename} to {filepath} ")
    if os.path.isfile("start.cmd"):
        os.system("start cmd /c send.cmd")

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(IPANDPORT)
    server.listen()
    print(f"Start Server {IP}:{PORT}")

    while True:
        client, addr = server.accept()
        print(addr)
        thread = threading.Thread(target=handle_client, args=(client, addr))
        thread.start()

if __name__ == "__main__":
    main()
