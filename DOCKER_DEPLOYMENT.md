# Birthday Wisher - Docker Deployment Guide

## Quick Start

### 1. Build the Docker image:
```bash
./deploy.sh build
```

### 2. Start the application:
```bash
./deploy.sh start
```

### 3. Access the application:
Open your browser and go to: **http://localhost:8501**

## Deployment Commands

| Command | Description |
|---------|-------------|
| `./deploy.sh build` | Build the Docker image |
| `./deploy.sh start` | Start the application |
| `./deploy.sh stop` | Stop the application |
| `./deploy.sh restart` | Restart the application |
| `./deploy.sh logs` | View application logs |
| `./deploy.sh status` | Show container status |
| `./deploy.sh clean` | Remove containers and volumes |
| `./deploy.sh rebuild` | Rebuild from scratch (no cache) |
| `./deploy.sh shell` | Open a shell in the container |

## Manual Docker Commands

### Build the image:
```bash
docker build -t birthday-wisher .
```

### Run the container:
```bash
docker run -d \
  --name birthday-wisher-app \
  -p 8501:8501 \
  -v $(pwd)/templates:/app/templates:ro \
  -v $(pwd)/output:/app/output \
  birthday-wisher
```

### Using Docker Compose:
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f

# Rebuild
docker-compose up -d --build
```

## Production Deployment

### Environment Variables

You can customize the deployment by setting environment variables in `docker-compose.yml`:

```yaml
environment:
  - STREAMLIT_SERVER_PORT=8501
  - STREAMLIT_SERVER_HEADLESS=true
  - STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

### Port Configuration

To change the port, edit `docker-compose.yml`:

```yaml
ports:
  - "8080:8501"  # Change 8080 to your desired port
```

### Volume Mounts

The application uses these volumes:
- `./templates:/app/templates:ro` - Read-only template files
- `./output:/app/output` - Rendered video outputs
- `./uploads:/app/uploads` - Temporary uploaded images

## Cloud Deployment

### Deploy to AWS ECS/Fargate:

1. Push image to ECR:
```bash
aws ecr create-repository --repository-name birthday-wisher
docker tag birthday-wisher:latest <account-id>.dkr.ecr.<region>.amazonaws.com/birthday-wisher:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/birthday-wisher:latest
```

2. Create ECS task definition and service

### Deploy to Google Cloud Run:

```bash
# Build and push
gcloud builds submit --tag gcr.io/<project-id>/birthday-wisher

# Deploy
gcloud run deploy birthday-wisher \
  --image gcr.io/<project-id>/birthday-wisher \
  --platform managed \
  --port 8501 \
  --allow-unauthenticated
```

### Deploy to Azure Container Instances:

```bash
az container create \
  --resource-group myResourceGroup \
  --name birthday-wisher \
  --image birthday-wisher:latest \
  --dns-name-label birthday-wisher \
  --ports 8501
```

### Deploy to DigitalOcean App Platform:

1. Push to Docker Hub or DigitalOcean Container Registry
2. Create new app from container image
3. Set port to 8501

## Troubleshooting

### View logs:
```bash
./deploy.sh logs
```

### Container not starting:
```bash
docker ps -a
docker logs birthday-wisher-app
```

### Permission issues with volumes:
```bash
sudo chown -R 1000:1000 output/ uploads/
```

### Check FFmpeg inside container:
```bash
./deploy.sh shell
ffmpeg -version
```

## Resource Requirements

**Minimum:**
- CPU: 1 core
- RAM: 1GB
- Storage: 2GB

**Recommended:**
- CPU: 2 cores
- RAM: 2GB
- Storage: 10GB (for output videos)

## Security Notes

- The container runs as a non-root user
- Templates are mounted as read-only
- No sensitive data is stored in the image
- Health checks are enabled for monitoring
