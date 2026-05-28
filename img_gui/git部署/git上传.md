## 生成公私钥

```
ssh-keygen -t rsa -C "ssh"
```

### 上传

```
#git init
git add .
git commit -m "assets"
#git branch -m master main
#git clone https://github.com:fantasycat6/repo.git
#git remote add origin https://github.com:fantasycat6/repo.git
git push origin main
```

## bat

```
@echo off
git add .
git commit -m "assets"
git push origin main
pause
```

## url替换

```
../.*?/repo/assets/
https://image.201068.xyz/assets
```
