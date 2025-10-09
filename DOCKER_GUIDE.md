# 🐳 Docker Setup Guide for Wellness Bot

## What is Docker? (Beginner Friendly)

**Docker = A magic box that runs your app anywhere!**

Imagine you have a laptop with Windows. Your friend has Mac. The server uses Linux. Normally, you'd need to install Python, libraries, and configure everything on each machine differently.

**With Docker:** You create ONE "box" (called a container) that has everything inside. This box works the same on Windows, Mac, Linux, or any cloud server!

### Key Terms:
- **Dockerfile** = Recipe to build your box (what to include)
- **Image** = The actual box (built from Dockerfile)
- **Container** = Running box (your app is running inside)
- **docker-compose.yml** = Manages multiple boxes at once (backend, frontend, admin)

---

## 📋 Prerequisites

### 1. Install Docker Desktop

**For Windows:**
1. Download: https://www.docker.com/products/docker-desktop/
2. Run installer
3. Restart computer
4. Open Docker Desktop
5. Wait for "Docker Desktop is running" ✅

**Verify Installation:**
```powershell
docker --version
# Should show: Docker version 24.x.x or similar

docker-compose --version
# Should show: Docker Compose version 2.x.x or similar
```

---

## 🚀 How to Use Docker with Your Project

### Option 1: Quick Start (Easiest)

**1. Start all services with one command:**
```powershell
docker-compose up
```

That's it! Docker will:
- Build the containers
- Start backend (port 5000)
- Start frontend (port 8501)
- Start admin (port 8502)

**Access your app:**
- Frontend: http://localhost:8501
- Backend API: http://localhost:5000
- Admin Dashboard: http://localhost:8502

**2. Stop all services:**
```powershell
# Press Ctrl+C in terminal
# OR
docker-compose down
```

### Option 2: Build First, Then Run

**1. Build the Docker image:**
```powershell
docker build -t wellness-bot .
```
This creates a "box" with all your code and dependencies.

**2. Run individual services:**
```powershell
# Backend
docker run -p 5000:5000 wellness-bot python backend.py

# Frontend
docker run -p 8501:8501 wellness-bot streamlit run frontend.py --server.port=8501 --server.address=0.0.0.0

# Admin
docker run -p 8502:8502 wellness-bot streamlit run admin_dashboard.py --server.port=8502 --server.address=0.0.0.0
```

### Option 3: Development Mode (Best for Testing)

**Run with live code updates:**
```powershell
docker-compose up --build
```

This rebuilds containers if you changed code.

---

## 📁 Files I Created for You

### 1. `Dockerfile`
**What it does:** Recipe to build your Docker container
**Contains:**
- Python 3.11
- All your requirements
- Your application code
- Pre-trained models
- Database initialization

### 2. `docker-compose.yml`
**What it does:** Manages all 3 services (backend, frontend, admin)
**Contains:**
- Backend service on port 5000
- Frontend service on port 8501
- Admin service on port 8502
- Network configuration
- Database volume mounts

### 3. `.dockerignore`
**What it does:** Tells Docker what NOT to copy
**Ignores:**
- Virtual environments (.venv)
- Python cache (__pycache__)
- Git files
- Test files

---

## 🔧 Common Docker Commands

### Managing Containers

```powershell
# Start all services (in background)
docker-compose up -d

# Stop all services
docker-compose down

# View running containers
docker ps

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Remove everything (clean slate)
docker-compose down -v
```

### Building and Rebuilding

```powershell
# Build image
docker build -t wellness-bot .

# Rebuild (after code changes)
docker-compose up --build

# Force rebuild (ignore cache)
docker-compose build --no-cache
```

### Debugging

```powershell
# Enter a running container (like SSH into it)
docker exec -it wellness_backend bash

# View logs from specific service
docker-compose logs backend
docker-compose logs frontend
docker-compose logs admin

# Check if containers are healthy
docker-compose ps
```

---

## 🐛 Troubleshooting

### Problem: "Port already in use"

**Solution:**
```powershell
# Stop other apps using ports 5000, 8501, 8502
# OR change ports in docker-compose.yml:
ports:
  - "5001:5000"  # Use port 5001 instead of 5000
```

### Problem: "docker command not found"

**Solution:**
1. Make sure Docker Desktop is running
2. Restart terminal/PowerShell
3. Re-install Docker Desktop if needed

### Problem: Container keeps restarting

**Solution:**
```powershell
# Check logs to see error
docker-compose logs backend

# Common issues:
# - Database not initialized → Run setup_db.py manually
# - Models not trained → Run train_bot.py manually
# - Port conflict → Change ports
```

### Problem: Changes not reflected

**Solution:**
```powershell
# Rebuild containers after code changes
docker-compose down
docker-compose up --build
```

---

## 🎯 Before Pushing to Git

### Step 1: Test Docker Locally

```powershell
# 1. Build and run
docker-compose up --build

# 2. Open browser and test:
#    - http://localhost:8501 (Frontend)
#    - http://localhost:5000/health (Backend)
#    - http://localhost:8502 (Admin)

# 3. Test bot conversation
#    - Report symptoms
#    - Check disease predictions
#    - Verify CSV data is used

# 4. Stop containers
docker-compose down
```

### Step 2: Update .gitignore

Your `.gitignore` already includes Docker files, but verify:
```gitignore
# Docker (already in .gitignore - just verify)
*.db
.venv/
__pycache__/
```

### Step 3: Add Docker Files to Git

```powershell
# Add Docker files
git add Dockerfile
git add docker-compose.yml
git add .dockerignore

# Commit
git commit -m "Add Docker support for containerization"
```

### Step 4: Update README.md

Add Docker section to your README:
```markdown
## 🐳 Docker Deployment

### Quick Start
```bash
docker-compose up
```

### Access Services
- Frontend: http://localhost:8501
- Backend API: http://localhost:5000
- Admin Dashboard: http://localhost:8502

### Stop Services
```bash
docker-compose down
```
```

---

## 🚀 Deployment with Docker

### Deploy to Any Cloud Platform

Once on Git, you can deploy to:

**1. Railway** (Easiest)
- Connect GitHub repo
- Railway detects Dockerfile automatically
- Deploy with one click!

**2. Render**
- Connect GitHub repo
- Select "Docker" as environment
- Deploy!

**3. AWS/Azure/Google Cloud**
- Push Docker image to container registry
- Deploy to container service
- Scale as needed

**4. Your Own Server**
```bash
# On server:
git clone your-repo
cd your-repo
docker-compose up -d
```

---

## 📊 Docker vs Regular Deployment

| Feature | Without Docker | With Docker |
|---------|---------------|-------------|
| Setup | Install Python, dependencies, configure | Just `docker-compose up` |
| Works everywhere | Need to configure each machine | Same everywhere |
| Dependencies | Can conflict | Isolated in container |
| Deployment | Complex | Simple |
| Scaling | Manual | Easy with orchestration |

---

## 🎓 Learning Resources

**Docker Basics:**
- Official Tutorial: https://docs.docker.com/get-started/
- Docker Desktop: https://www.docker.com/products/docker-desktop/

**Your Project Specific:**
- All Docker files created ✅
- Ready to use immediately ✅
- No Docker knowledge required to use ✅

---

## ✅ Quick Checklist

Before pushing to Git:

- [ ] Docker Desktop installed and running
- [ ] Tested `docker-compose up` locally
- [ ] All 3 services work (backend, frontend, admin)
- [ ] Bot responses include CSV data
- [ ] Committed Dockerfile to Git
- [ ] Committed docker-compose.yml to Git
- [ ] Committed .dockerignore to Git
- [ ] Updated README.md with Docker instructions

---

## 🎉 You're Ready!

**What you have now:**
1. ✅ Clean project structure
2. ✅ CSV integration working
3. ✅ Docker containerization
4. ✅ Easy deployment anywhere
5. ✅ Professional setup

**Next steps:**
1. Test Docker locally (`docker-compose up`)
2. Push to GitHub
3. Deploy to cloud platform
4. Share with users! 🚀

---

## 💡 Pro Tips

1. **Always use docker-compose** - It's easier than individual docker commands
2. **Check logs when debugging** - `docker-compose logs -f`
3. **Rebuild after code changes** - `docker-compose up --build`
4. **Databases persist** - Even after stopping containers, your data is safe
5. **One command deployment** - That's the Docker magic! ✨

**Need help?** All Docker commands are in this guide! 📚
