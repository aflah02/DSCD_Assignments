import socket

def tcp_ping(host, port):
    try:
        # Create a TCP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # Timeout for the connection attempt

        # Connect to the server
        sock.connect((host, port))
        print(f"Successfully connected to {host}:{port}")
        return True

    except socket.error as e:
        print(f"Failed to connect to {host}:{port} - {e}")
        return False

    finally:
        # Close the socket
        sock.close()

if __name__ == "__main__":
    host = 'localhost'
    port = 5556
    tcp_ping(host, port)
