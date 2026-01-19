# Speedtest MQTT Monitor

A Docker container that runs periodic internet speed tests and publishes the results to MQTT topics for Home Assistant integration.

## Features

- Uses official Ookla Speedtest CLI for accurate measurements
- Publishes results to MQTT with retain flag for Home Assistant
- Configurable via environment variables
- Automatic retry on failures
- Comprehensive logging
- Runs as non-root user for security

## Quick Start

### Using Pre-built Docker Image (Recommended)

**Docker Run:**
```bash
docker run -d \
  --name speedtest-mqtt-monitor \
  --restart unless-stopped \
  -e MQTT_HOST=192.168.1.47 \
  -e MQTT_USERNAME=client \
  -e MQTT_PASSWORD=client \
  -e SLEEP_INTERVAL=7200 \
  sh00t2kill/speedtest-mqtt:latest
```

**Docker Compose:**
```yaml
version: '3.8'
services:
  speedtest-monitor:
    image: sh00t2kill/speedtest-mqtt:latest
    container_name: speedtest-mqtt-monitor
    restart: unless-stopped
    environment:
      MQTT_HOST: "192.168.1.47"
      MQTT_USERNAME: "client"
      MQTT_PASSWORD: "client"
      SLEEP_INTERVAL: "7200"  # 2 hours
```

### Building from Source

1. **Using Docker Compose:**
   ```bash
   docker-compose up -d
   ```

2. **Using Docker directly:**
   ```bash
   docker build -t speedtest-monitor .
   docker run -d \
     --name speedtest-mqtt \
     -e MQTT_HOST=192.168.1.47 \
     -e MQTT_USERNAME=client \
     -e MQTT_PASSWORD=client \
     speedtest-monitor
   ```

## Configuration

Configure the container using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `MQTT_HOST` | `192.168.1.47` | MQTT broker hostname/IP |
| `MQTT_PORT` | `1883` | MQTT broker port |
| `MQTT_USERNAME` | `client` | MQTT username |
| `MQTT_PASSWORD` | `client` | MQTT password |
| `MQTT_BASE_TOPIC` | `internet/` | Base topic for publishing |
| `SLEEP_INTERVAL` | `21600` | Seconds between tests (12 hours) |

## MQTT Topics

The following topics are published with retain flag:

- `internet/start` - Test start timestamp (ddMMYYYYHHmmss)
- `internet/ping` - Latency in milliseconds
- `internet/down` - Download speed in Mbps
- `internet/up` - Upload speed in Mbps  
- `internet/jitter` - Jitter in milliseconds
- `internet/server_name` - Test server name
- `internet/server_location` - Test server location
- `internet/isp` - Internet service provider

## Home Assistant Integration

Add these sensors to your `configuration.yaml`:

```yaml
mqtt:
  sensor:
    - name: "Internet Download Speed"
      state_topic: "internet/down"
      unit_of_measurement: "Mbps"
      icon: mdi:download
      
    - name: "Internet Upload Speed"  
      state_topic: "internet/up"
      unit_of_measurement: "Mbps"
      icon: mdi:upload
      
    - name: "Internet Ping"
      state_topic: "internet/ping" 
      unit_of_measurement: "ms"
      icon: mdi:timer
      
    - name: "Internet Jitter"
      state_topic: "internet/jitter"
      unit_of_measurement: "ms" 
      icon: mdi:sine-wave
```

## Development

To run locally for testing:

```bash
pip install -r requirements.txt
export MQTT_HOST=your-mqtt-broker
export MQTT_USERNAME=your-username
export MQTT_PASSWORD=your-password
python speedtest_monitor.py
```

## Logs

View container logs:
```bash
docker-compose logs -f speedtest-monitor
```

## Troubleshooting

- **Speedtest fails**: Check internet connectivity and firewall settings
- **MQTT connection fails**: Verify MQTT broker settings and credentials  
- **Container exits**: Check logs for specific error messages