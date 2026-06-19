# Deployment Guide

This guide covers various deployment options for the Developer Portfolio API.

## Local Development

### Prerequisites
- Python 3.9+
- pip or poetry
- OpenAI API key (optional, for AI features)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd developer-portfolio-backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

5. Run the application:
```bash
python run.py
# or
uvicorn app.main:app --reload
```

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - SMTP_USER=${SMTP_USER}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
```

### Build and Run

```bash
docker-compose up --build
```

## Cloud Deployment

### Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set environment variables:
   - `OPENAI_API_KEY`
   - `SMTP_USER`
   - `SMTP_PASSWORD`
   - `EMAIL_FROM`
   - `EMAIL_TO`
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Railway

1. Create a new project on Railway
2. Connect your GitHub repository
3. Add environment variables in the dashboard
4. Railway will automatically detect and deploy your Python app

### Heroku

1. Create a `Procfile`:
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

2. Create `runtime.txt`:
```
python-3.11.0
```

3. Deploy:
```bash
git push heroku main
```

### AWS (EC2)

1. Launch an EC2 instance with Ubuntu
2. Install Python and dependencies
3. Use systemd to run the service:

```ini
# /etc/systemd/system/portfolio-api.service
[Unit]
Description=Portfolio API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/app
ExecStart=/home/ubuntu/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

4. Enable and start:
```bash
sudo systemctl enable portfolio-api
sudo systemctl start portfolio-api
```

## Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Monitoring

### Health Check Endpoint

```bash
curl https://your-domain.com/api/health
```

### Logs

```bash
# View application logs
tail -f logs/app.log

# View error logs
tail -f logs/errors.log

# View request logs
tail -f logs/requests.log
```

## Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| `APP_NAME` | Application name | No |
| `APP_VERSION` | Application version | No |
| `DEBUG` | Debug mode | No |
| `HOST` | Server host | No |
| `PORT` | Server port | No |
| `ALLOWED_ORIGINS` | CORS origins | No |
| `SMTP_HOST` | SMTP server host | For email |
| `SMTP_PORT` | SMTP server port | For email |
| `SMTP_USER` | SMTP username | For email |
| `SMTP_PASSWORD` | SMTP password | For email |
| `EMAIL_FROM` | Sender email | For email |
| `EMAIL_TO` | Recipient email | For email |
| `AI_PROVIDER` | AI provider | No |
| `OPENAI_API_KEY` | OpenAI API key | For AI |
| `OPENAI_MODEL` | OpenAI model | No |
| `RATE_LIMIT_REQUESTS` | Rate limit count | No |
| `RATE_LIMIT_WINDOW` | Rate limit window | No |
| `DATA_DIR` | Data directory | No |
| `LOGS_DIR` | Logs directory | No |

## Troubleshooting

### Common Issues

1. **Port already in use**:
```bash
lsof -i :8000
kill -9 <PID>
```

2. **Permission denied**:
```bash
chmod +x run.py
```

3. **Module not found**:
```bash
pip install -r requirements.txt
```

4. **Environment variables not loading**:
```bash
# Check if .env file exists
ls -la .env

# Verify variables are set
echo $OPENAI_API_KEY
```

### Performance Tuning

For production, consider:

1. Using Gunicorn with Uvicorn workers:
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

2. Enabling gzip compression
3. Setting up a reverse proxy (Nginx)
4. Using a CDN for static files
5. Implementing caching (Redis)