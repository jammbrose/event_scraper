# Waltham Event Scraper Service Configuration

## Option 1: Systemd Service (Linux)

Create `/etc/systemd/system/waltham-events.service`:

```ini
[Unit]
Description=Waltham Event Scraper Service
After=network.target

[Service]
Type=simple
User=jared
WorkingDirectory=/home/jared/Documents/coding_projects/event_scraper
ExecStart=/home/jared/Documents/coding_projects/event_scraper/.venv/bin/python scheduler.py
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
```

### Enable and start the service:
```bash
sudo systemctl enable waltham-events.service
sudo systemctl start waltham-events.service
sudo systemctl status waltham-events.service
```

## Option 2: Cron Job (Alternative)

Add to crontab (`crontab -e`):

```bash
# Run event scraper daily at 6:00 AM
0 6 * * * cd /home/jared/Documents/coding_projects/event_scraper && /home/jared/Documents/coding_projects/event_scraper/.venv/bin/python scraper.py

# Run event scraper daily at 6:00 PM
0 18 * * * cd /home/jared/Documents/coding_projects/event_scraper && /home/jared/Documents/coding_projects/event_scraper/.venv/bin/python scraper.py
```

## Option 3: Docker with Cron (Production)

Create `Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Install cron
RUN apt-get update && apt-get install -y cron

# Add cron job
RUN echo "0 6,18 * * * cd /app && python scraper.py" | crontab -

CMD ["cron", "-f"]
```

## Option 4: PM2 Process Manager

```bash
npm install -g pm2
pm2 start scheduler.py --interpreter python3 --name waltham-events
pm2 startup
pm2 save
```

## Monitoring and Logging

The scheduler now includes:
- **Detailed logging** to `scraper.log`
- **Error handling** with retries
- **Multiple daily updates** (6 AM and 6 PM)
- **Weekly deep cleaning** (Sundays at 3 AM)

### Log monitoring:
```bash
tail -f scraper.log
```

### Service status:
```bash
sudo systemctl status waltham-events.service
```

## Recommended Setup

1. **Development**: Use the Python scheduler directly
2. **Production**: Use systemd service for reliability
3. **Cloud**: Use cron jobs or scheduled functions
4. **Docker**: Use containerized cron for portability
