@echo off
chcp 65001 >nul
echo ========================================
echo 部署到 GitHub 和 Render
echo ========================================
echo.

REM 检查是否已初始化Git
if not exist .git (
    echo [1/5] 初始化 Git 仓库...
    git init
    git branch -M main
) else (
    echo [1/5] Git 仓库已存在，跳过初始化
)

echo.
echo [2/5] 添加所有文件...
git add .

echo.
echo [3/5] 创建提交...
set /p commit_msg="请输入提交信息 (直接回车使用默认): "
if "%commit_msg%"=="" set commit_msg=Update images and code

git commit -m "%commit_msg%"

echo.
echo [4/5] 推送到 GitHub...
echo.
echo 请输入你的 GitHub 仓库地址
echo 格式: https://github.com/YOUR_USERNAME/REPO_NAME.git
echo.
set /p repo_url="GitHub 仓库地址: "

if "%repo_url%"=="" (
    echo ❌ 错误: 未输入仓库地址
    pause
    exit /b 1
)

REM 检查是否已添加remote
git remote | findstr origin >nul
if %errorlevel% equ 0 (
    echo Remote origin 已存在，更新地址...
    git remote set-url origin %repo_url%
) else (
    echo 添加 Remote origin...
    git remote add origin %repo_url%
)

git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo ✓ 推送成功！
    echo ========================================
    echo.
    echo [5/5] 下一步：部署到 Render
    echo.
    echo 1. 访问: https://render.com
    echo 2. 使用 GitHub 账号登录
    echo 3. 点击 "New +" - "Web Service"
    echo 4. 选择你的仓库
    echo 5. 配置:
    echo    - Name: tos-image-viewer
    echo    - Region: Singapore
    echo    - Build Command: pip install -r requirements.txt
    echo    - Start Command: gunicorn api_v2:app
    echo    - Instance Type: Free
    echo 6. 点击 "Create Web Service"
    echo 7. 等待部署完成（约3-5分钟）
    echo.
    echo 部署完成后，Render 会提供一个公开URL
    echo.
) else (
    echo.
    echo ❌ 推送失败！
    echo.
    echo 可能的原因:
    echo 1. 仓库地址错误
    echo 2. 没有权限（需要先在 GitHub 创建仓库）
    echo 3. 网络问题
    echo.
    echo 请检查后重新运行此脚本
)

echo.
pause
