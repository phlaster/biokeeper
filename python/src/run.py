from serv_SIMPLE import *
from Logger import Logger

hostName = "0.0.0.0"
serverPort = 8080


if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    logger = Logger("logs.log")

    try:
        logger.log_message(f"server_started_at_port {serverPort}")
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)
    finally:
        logger.log_message(f"server_stopped_at_port {serverPort}")
        webServer.server_close()
