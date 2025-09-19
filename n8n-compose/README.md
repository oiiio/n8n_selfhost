# n8n Local Development Setup

This directory contains everything you need to run n8n locally on your MacBook for testing and development.

## Quick Start

1. **Start n8n:**
   ```bash
   ./start.sh up
   ```

2. **Access n8n:**
   - Open your browser and go to: http://localhost:5678
   - Default credentials: `admin` / `password`

3. **Stop n8n:**
   ```bash
   ./start.sh down
   ```

## Available Commands

The `start.sh` script provides several commands:

- `./start.sh up` or `./start.sh start` - Start n8n
- `./start.sh down` or `./start.sh stop` - Stop n8n
- `./start.sh restart` - Restart n8n
- `./start.sh logs` - View live logs
- `./start.sh status` - Check container status

## Configuration

### Environment Variables (.env)

Key settings in your `.env` file:

- **N8N_BASIC_AUTH_USER**: Username for basic authentication (default: admin)
- **N8N_BASIC_AUTH_PASSWORD**: Password for basic authentication (default: password)
- **N8N_PORT**: Port where n8n will be accessible (default: 5678)
- **GENERIC_TIMEZONE**: Your timezone (default: America/New_York)

### Security Note

⚠️ **Important**: The default setup uses basic authentication with simple credentials. This is fine for local development but should be changed for any production use.

## Data Persistence

Your n8n data (workflows, credentials, etc.) is stored in a Docker volume named `n8n_data`. This means your data will persist even if you stop and restart the container.

## Customization

### Custom Nodes

To add custom nodes:
1. Create a `custom` directory in this folder
2. Uncomment the volume mount line in `docker-compose.yml`
3. Place your custom nodes in the `custom` directory

### Different Database

By default, this setup uses SQLite for simplicity. For production or more demanding use cases, you might want to switch to PostgreSQL:

1. Update the `.env` file with PostgreSQL settings
2. Add a PostgreSQL service to the `docker-compose.yml`
3. Update the database environment variables

## Troubleshooting

### Port Already in Use

If port 5678 is already in use, change `N8N_PORT` in your `.env` file to another port.

### Docker Issues

Make sure Docker Desktop is running before starting n8n:
```bash
docker info
```

### View Logs

To see what's happening:
```bash
./start.sh logs
```

### Reset Everything

To completely reset (⚠️ **This will delete all your workflows and data**):
```bash
./start.sh down
docker volume rm n8n-compose_n8n_data
./start.sh up
```

## Files in This Directory

- `.env` - Environment configuration
- `docker-compose.yml` - Docker Compose configuration
- `start.sh` - Management script
- `README.md` - This file

## Next Steps

1. Change the default password in your `.env` file
2. Explore n8n by creating your first workflow
3. Check out the [n8n documentation](https://docs.n8n.io/) for more advanced features

Happy automating! 🚀