import uvicorn
from Logger import Logger

if __name__ == "__main__":
    logger = Logger("logs.log")
    hostName = "0.0.0.0"
    serverPort = 8080
    
    try:
        logger.log_message(f"server_started_at_port {serverPort}")
        uvicorn.run("serv_fastAPI:app", host=hostName, port=serverPort, reload=True)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)
    finally:
        logger.log_message(f"server_stopped_at_port {serverPort}")
