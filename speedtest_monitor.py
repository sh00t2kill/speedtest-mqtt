#!/usr/bin/env python3
import os
import time
import json
import subprocess
import logging
from datetime import datetime
import paho.mqtt.client as mqtt

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SpeedtestMQTTMonitor:
    def __init__(self):
        # MQTT Configuration from environment variables
        self.mqtt_host = os.getenv('MQTT_HOST', 'localhost')
        self.mqtt_port = int(os.getenv('MQTT_PORT', '1883'))
        self.mqtt_username = os.getenv('MQTT_USERNAME', 'client')
        self.mqtt_password = os.getenv('MQTT_PASSWORD', 'client')
        self.base_topic = os.getenv('MQTT_BASE_TOPIC', 'internet/')
        
        # Monitoring Configuration
        self.sleep_interval = int(os.getenv('SLEEP_INTERVAL', '21600'))  # 12 hours default
        
        # Initialize MQTT client
        self.mqtt_client = mqtt.Client(client_id="python-speedtest-monitor")
        self.mqtt_client.username_pw_set(self.mqtt_username, self.mqtt_password)
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_disconnect = self.on_disconnect
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("Connected to MQTT broker successfully")
        else:
            logger.error(f"Failed to connect to MQTT broker with code {rc}")
    
    def on_disconnect(self, client, userdata, rc):
        logger.info("Disconnected from MQTT broker")
    
    def run_speedtest(self):
        """Run speedtest and parse results"""
        try:
            # Run speedtest command
            result = subprocess.run(['speedtest', '--format=json'], 
                                  capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                logger.error(f"Speedtest failed: {result.stderr}")
                return None
            
            # Parse JSON output
            data = json.loads(result.stdout)
            
            # Extract the values we need
            parsed_data = {
                'start': datetime.now().strftime('%d%m%Y%H%M%S'),
                'ping': round(data.get('ping', {}).get('latency', 0), 2),
                'down': round(data.get('download', {}).get('bandwidth', 0) * 8 / 1000000, 2),  # Convert to Mbps
                'up': round(data.get('upload', {}).get('bandwidth', 0) * 8 / 1000000, 2),     # Convert to Mbps
                'jitter': round(data.get('ping', {}).get('jitter', 0), 2),
                'server_name': data.get('server', {}).get('name', 'Unknown'),
                'server_location': data.get('server', {}).get('location', 'Unknown'),
                'isp': data.get('isp', 'Unknown')
            }
            
            return parsed_data
            
        except subprocess.TimeoutExpired:
            logger.error("Speedtest command timed out")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse speedtest JSON output: {e}")
            return None
        except Exception as e:
            logger.error(f"Error running speedtest: {e}")
            return None
    
    def publish_to_mqtt(self, data):
        """Publish speedtest results to MQTT"""
        try:
            # Connect to MQTT broker
            self.mqtt_client.connect(self.mqtt_host, self.mqtt_port, 60)
            
            # Publish each metric
            for key, value in data.items():
                topic = f"{self.base_topic}{key}"
                self.mqtt_client.publish(topic, str(value), qos=0, retain=True)
                logger.info(f"Published {key}: {value} to {topic}")
            
            # Disconnect
            self.mqtt_client.disconnect()
            
        except Exception as e:
            logger.error(f"Error publishing to MQTT: {e}")
    
    def run(self):
        """Main monitoring loop"""
        logger.info("Starting speedtest monitor...")
        logger.info(f"MQTT Host: {self.mqtt_host}:{self.mqtt_port}")
        logger.info(f"Base Topic: {self.base_topic}")
        logger.info(f"Sleep Interval: {self.sleep_interval} seconds")
        
        while True:
            try:
                logger.info("Running speedtest...")
                data = self.run_speedtest()
                
                if data:
                    logger.info(f"Speedtest results: Down={data['down']}Mbps, Up={data['up']}Mbps, Ping={data['ping']}ms")
                    self.publish_to_mqtt(data)
                    logger.info("Results published to MQTT")
                else:
                    logger.error("Failed to get speedtest results")
                
                logger.info(f"Sleeping for {self.sleep_interval} seconds...")
                time.sleep(self.sleep_interval)
                
            except KeyboardInterrupt:
                logger.info("Received interrupt signal, stopping...")
                break
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}")
                logger.info("Retrying in 60 seconds...")
                time.sleep(60)

if __name__ == "__main__":
    monitor = SpeedtestMQTTMonitor()
    monitor.run()