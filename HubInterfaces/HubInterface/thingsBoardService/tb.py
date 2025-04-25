import logging
import threading
import subprocess
import requests
import time

logger = logging.getLogger(__name__)

class TB:
    _instance = None
    url = "thingsboard.cloud"
    tb_gateway_started = False
    thread = None
    stop_event = None
    
    def __new__(cls):
        if cls._instance is None:
            try:
                logger.info("Creating TB instance.")
                cls._instance = super(TB, cls).__new__(cls)
                
                cls._instance._stop_service()
            except Exception as error:
                logger.error(f"Error creating TB instance: {error}")
                raise Exception("TB not created.")
        return cls._instance
    
    def __del__(self): 
        self.stop()
    
    def _start_service(self):
        count = 0
        while not self.stop_event.is_set():
            self.tb_gatway_service_loop(count)
            count += 1
            if count >= 60:
                count = 0
            time.sleep(1)
        
    def _stop_service(self):
        command = ["systemctl", "stop", "thingsboard-gateway"]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            logger.debug("thingsboard-gateway stopped.")
        else:
            logger.error(f"Failed to stop thingsboard-gateway, {result.stderr}")
            # raise Exception("Failed to stop thingsboard-gateway.")
            
    def start(self):
        logger.debug("Starting TB service.")
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._start_service)
        self.thread.start()
        
    def stop(self):
        logger.debug("Stopping TB service.")
        if self.stop_event:
            self.stop_event.set()
        if self.thread:
            self.thread.join()
        self._stop_service()
        logger.debug("TB service stopped.")
        
    def tb_gatway_service_loop(self, count: int):
        if count == 0:
            try:
                result = requests.get(f"http://{self.url}/", verify=False, timeout=5)
                if result.status_code == 200:
                    if not self.tb_gateway_started:
                        self.tb_gateway_started = True
                        command = ["systemctl", "start", "thingsboard-gateway"]
                        result = subprocess.run(command, capture_output=True, text=True)
                        if result.returncode == 0:
                            logger.debug("thingsboard-gateway started.")
                        else:
                            logger.error(f"Failed to start thingsboard-gateway, {result.stderr}")
                else:
                    logger.error(f"Failed to connect to thingsboard at {self.url}, {result.status_code}")
                    if self.tb_gateway_started:
                        self.tb_gateway_started = False
                        self._stop_service()
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except Exception as e:
                logger.error(f"Error checking TB service: {e}")