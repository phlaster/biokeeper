from serv_SIMPLE import *

hostName = "0.0.0.0"
serverPort = 8080


if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (real_host, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    except e:
        print(e)
        
    finally:
        webServer.server_close()
        print("Server stopped.")