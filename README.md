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

1. **Using Docker Compose (Recommended):**
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