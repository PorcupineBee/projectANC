import subprocess
import requests
import time
import os
import signal

class NgrokTunnel:
    def __init__(self, port=9999):
        self.local_port = port
        self.ngrok_process = None
        self.public_url = None

    def start(self):
        self.ngrok_process = subprocess.Popen(
            ["ngrok", "tcp", str(self.local_port)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT
        )
        print("Starting ngrok tunnel...")
        time.sleep(2)

        try:
            tunnels = requests.get("http://localhost:4040/api/tunnels").json()
            self.public_url = tunnels['tunnels'][0]['public_url']
            print(f"Ngrok tunnel: {self.public_url}")
            return self.public_url
        except Exception as e:
            print("Failed to get ngrok URL:", e)
            return None

    def stop(self):
        if self.ngrok_process:
            print("Stopping ngrok tunnel...")
            if os.name == 'nt':
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(self.ngrok_process.pid)])
            else:
                os.killpg(os.getpgid(self.ngrok_process.pid), signal.SIGTERM)
            self.ngrok_process = None


# Example usage:
if __name__ == "__main__":
    tunnel = NgrokTunnel(port=5000)
    public_url = tunnel.start()

    if public_url:
        input("Tunnel active. Press Enter to stop it...")

    tunnel.stop()
