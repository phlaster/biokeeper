from serv_SIMPLE import *

hostName = "0.0.0.0"
serverPort = 8080


if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    logger = Logger("logs.log")

    try:
        logger.log(f"{datetime.now()} server started at port {serverPort}")
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)
    finally:
        logger.log(f"{datetime.now()} server stopped")
        webServer.server_close()
