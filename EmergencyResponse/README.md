# Emergency Response Multi-Agent System

A sophisticated multi-agent system for emergency response and public safety. The system consists of three autonomous agents working together to provide real-time emergency response capabilities.

## Agents

1. **Weather Monitoring Agent**
   - Monitors weather conditions in real-time
   - Detects severe weather events (tornadoes, storms)
   - Triggers alerts based on weather conditions

2. **Emergency Notification Agent**
   - Handles communication with affected individuals
   - Sends SMS alerts to people within 25km radius
   - Makes emergency calls to people within 10km radius
   - Tracks last known locations of unreachable individuals

3. **Crime Detection Agent**
   - Monitors live CCTV feeds
   - Detects suspicious activities and potential crimes
   - Alerts law enforcement with video evidence
   - Provides real-time crime scene information

## Features

- Real-time weather monitoring and alerts
- Automated emergency notifications via SMS and phone calls
- Live crime detection and reporting
- Web dashboard for monitoring agent activities
- Location tracking for emergency response
- Real-time communication between agents

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env`:
```
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=your_twilio_number
OPENWEATHER_API_KEY=your_api_key
```

3. Run the application:
```bash
python app.py
```

## Web Dashboard

The web dashboard provides real-time monitoring of:
- Agent status and activities
- Emergency alerts and notifications
- Crime detection reports
- Weather monitoring data
- System logs and communication

## License

MIT License 