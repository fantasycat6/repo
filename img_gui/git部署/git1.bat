@echo off
::git init
git add .
git commit -m "assets"
git remote add origin https://github.com:fantasycat6/repo.git
git branch -m master main
::git pull
git push origin main
::git push git@github.com:fantasycat6/repo.git main
pause