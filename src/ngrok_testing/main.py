from ngrok_tunnel import NgrokTunnel

tunnel = NgrokTunnel(port=9999)
public_url = tunnel.start()

if public_url:
    print("Tunnel is active. Share this address with client.")
    input("Press Enter to stop the tunnel...")
    tunnel.stop()
