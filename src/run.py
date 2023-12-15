from serv_SIMPLE import *

hostName = "0.0.0.0"
serverPort = 8080


if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    log_message(f"Server started at port {serverPort} at {datetime.now()}")

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    except e:
        print(e)

    finally:
        webServer.server_close()
        log_message(f"Server stopped at {datetime.now()}")
