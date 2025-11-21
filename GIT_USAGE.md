# Git Repository Location

## ⚠️ Important: Repository is in subdirectory

The git repository is located in:
```
D:\deepseek-ai-web-crawler-main\deepseek-ai-web-crawler-main
```

**NOT** in:
```
D:\deepseek-ai-web-crawler-main
```

## How to Use Git Commands

### Always navigate to the correct folder first:

```powershell
cd D:\deepseek-ai-web-crawler-main\deepseek-ai-web-crawler-main
```

Then run git commands:
```powershell
git status
git pull
git push
git add .
git commit -m "message"
```

---

## Quick Reference

### Navigate to repository:
```powershell
cd D:\deepseek-ai-web-crawler-main\deepseek-ai-web-crawler-main
```

### Check status:
```powershell
git status
```

### Pull latest changes:
```powershell
git pull origin main
```

### Push changes:
```powershell
git add .
git commit -m "Your message"
git push origin main
```

### Check remote:
```powershell
git remote -v
```

Should show:
```
origin  https://github.com/playershyan/Web-scraper.git (fetch)
origin  https://github.com/playershyan/Web-scraper.git (push)
```

---

## Why This Happens

The project structure is:
```
D:\deepseek-ai-web-crawler-main\          ← Parent folder (no git)
└── deepseek-ai-web-crawler-main\         ← Project folder (has git)
    ├── .git                              ← Git repository here
    ├── output\
    ├── sessions\
    └── ... (all project files)
```

The `.git` folder is in the **inner** folder, so you must be in that folder to run git commands.

---

## Alternative: Move Git to Parent Folder

If you want git in the parent folder instead, I can help reorganize. Just let me know!

