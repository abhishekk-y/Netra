# Installation Guide

## Prerequisites
- Docker Engine 24.0+
- Docker Compose v2.0+
- Linux (Ubuntu 22.04 recommended) or Windows (WSL2 recommended)

## Steps
1. Clone the repository.
2. Ensure you have the required ports free: 8000 (Backend), 3000 (Frontend), 5432 (PostgreSQL), 6379 (Valkey).
3. Run the startup script:
   - On Linux: `./start.sh`
   - On Windows: `.\start.ps1`
4. The script will create necessary evidence folders, initialize `.env`, and start all containers.
5. Access the application at `http://localhost:3000`.
