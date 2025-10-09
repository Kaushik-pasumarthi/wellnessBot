# 🐳 Docker Quick Reference Card

## What You Need to Know

### 1️⃣ Install Docker Desktop
👉 Download from: https://www.docker.com/products/docker-desktop/
✅ Install and start Docker Desktop
✅ Wait for "Docker Desktop is running"

### 2️⃣ One Command to Run Everything
```powershell
docker-compose up
```
**That's it!** This starts:
- ✅ Backend (http://localhost:5000)
- ✅ Frontend (http://localhost:8501)
- ✅ Admin (http://localhost:8502)

### 3️⃣ Stop Everything
```powershell
Ctrl + C
# OR
docker-compose down
```

---

## 🎯 Visual: How Docker Works

```
YOUR CODE (Python files, CSV, models)
         ↓
    Dockerfile (Recipe: "How to build the box")
         ↓
   Docker Image (The box with everything inside)
         ↓
Docker Container (Running box with your app)
         ↓
    Access via Browser!
```

---

## 📦 What's Inside the Docker Container?

```
Docker Container 📦
├─ Python 3.11 ✅
├─ Your code (all .py files) ✅
├─ CSV files (dataset, descriptions, precautions) ✅
├─ Models (trained ML models) ✅
├─ Dependencies (from requirements.txt) ✅
├─ Databases (admin.db, users.db) ✅
└─ Everything ready to run! ✅
```

---

## 🚀 3 Ways to Use Docker

### Option 1: Docker Compose (Recommended)
```powershell
# Start everything
docker-compose up

# Stop everything
docker-compose down
```
**Best for:** Running all services together

### Option 2: Individual Docker Commands
```powershell
# Build
docker build -t wellness-bot .

# Run backend only
docker run -p 5000:5000 wellness-bot
```
**Best for:** Testing one service

### Option 3: Background Mode
```powershell
# Start in background
docker-compose up -d

# Check status
docker ps

# View logs
docker-compose logs -f

# Stop
docker-compose down
```
**Best for:** Long-running services

---

## 🔥 Most Common Commands

```powershell
# 1. Start all services (first time)
docker-compose up --build

# 2. Start all services (subsequent times)
docker-compose up

# 3. Start in background
docker-compose up -d

# 4. Stop all services
docker-compose down

# 5. View logs
docker-compose logs -f

# 6. Rebuild after code changes
docker-compose up --build

# 7. See running containers
docker ps

# 8. Clean restart
docker-compose down && docker-compose up --build
```

---

## ❓ Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Port already in use | Change ports in docker-compose.yml |
| "docker not found" | Start Docker Desktop, restart terminal |
| Changes not showing | Run `docker-compose up --build` |
| Container keeps restarting | Check logs: `docker-compose logs` |
| Can't access services | Make sure ports 5000, 8501, 8502 are free |

---

## 📝 Before Pushing to Git

### ✅ Test Docker Locally

```powershell
# 1. Start services
docker-compose up

# 2. Test in browser:
#    - http://localhost:8501 (Frontend)
#    - http://localhost:5000/health (Backend API)
#    - http://localhost:8502 (Admin)

# 3. Test bot: report "fever" and check response

# 4. Stop
docker-compose down
```

### ✅ Add Docker Files to Git

```powershell
git add Dockerfile
git add docker-compose.yml
git add .dockerignore
git add DOCKER_GUIDE.md
git commit -m "Add Docker containerization"
```

---

## 🎓 Key Concepts (Super Simple)

**Dockerfile** = Recipe 📝
- Lists ingredients: Python, libraries, code
- Steps: Copy files, install dependencies, run setup

**docker-compose.yml** = Menu 📋
- Describes services: backend, frontend, admin
- Each service uses the same recipe (Dockerfile)
- Assigns ports and configurations

**Container** = Running App 🏃
- Like running multiple instances of your app
- Each service runs in its own container
- All containers talk to each other

---

## 💡 Why Docker is Awesome

### Without Docker 😓
```
Developer: Works on my machine!
Server: Doesn't work here...
Developer: Let me check your Python version...
Server: Which libraries do I need?
Developer: Did you install dependencies?
Server: What's the right configuration?
(Hours wasted debugging...)
```

### With Docker 🎉
```
Developer: Here's the Docker image
Server: *runs image*
Server: It works! ✅
(Takes 5 minutes!)
```

---

## 🚀 Deployment Advantage

**Traditional:**
1. Set up server
2. Install Python
3. Install dependencies
4. Configure database
5. Set up environment
6. Deploy code
7. Debug issues
8. Repeat for each server

**With Docker:**
1. `docker-compose up`
2. Done! ✅

---

## 📊 Your Project Structure with Docker

```
wellness-bot/
├── Dockerfile              ← Build recipe
├── docker-compose.yml      ← Service orchestration
├── .dockerignore          ← What to ignore
├── requirements.txt        ← Dependencies
├── backend.py             ← Backend service
├── frontend.py            ← Frontend service
├── admin_dashboard.py     ← Admin service
├── models/                ← ML models
├── dataset.csv            ← Medical data
└── [all other files]
```

**Docker reads:** Dockerfile → Builds image → Runs containers

---

## ✨ Final Steps

1. **Install Docker Desktop** ✅
2. **Test locally:** `docker-compose up` ✅
3. **Verify all services work** ✅
4. **Add to Git:** `git add Dockerfile docker-compose.yml .dockerignore` ✅
5. **Commit:** `git commit -m "Add Docker support"` ✅
6. **Push to GitHub:** `git push` ✅
7. **Deploy anywhere!** 🚀

---

## 🎉 You Did It!

Your wellness bot is now:
- ✅ Containerized (portable)
- ✅ Easy to deploy (one command)
- ✅ Works everywhere (same environment)
- ✅ Professional setup (production-ready)
- ✅ Ready for the cloud! ☁️

**Questions?** Check DOCKER_GUIDE.md for detailed explanations!

**Ready to deploy?** Your project is Docker-ready! 🐳✨
