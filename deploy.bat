@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: 简化版Docker部署脚本
echo.
echo ==========================================
echo     Data Processor Tool - Docker部署
echo ==========================================
echo.

:: 获取命令参数
set "COMMAND=%1"
set "PROJECT_NAME=data-processor-tool"
set "CONTAINER_NAME=data-processor-container"
set "HOST_PORT=5000"

if "%COMMAND%"=="" (
    echo 使用方法: %~n0 [命令]
    echo.
    echo 可用命令:
    echo   status  - 查看状态
    echo   deploy  - 完整部署
    echo   logs    - 查看日志
    echo   help    - 显示帮助
    echo.
    goto :end
)

if "%COMMAND%"=="status" (
    echo [检查] Docker环境...
    docker --version >nul 2>&1
    if %errorLevel% neq 0 (
        echo [错误] Docker未安装或未运行
        goto :end
    )
    echo [OK] Docker环境正常
    
    echo.
    echo [检查] 容器状态...
    docker ps -a --format "{{.Names}}" | findstr /x "%CONTAINER_NAME%" >nul 2>&1
    if %errorLevel% equ 0 (
        echo [OK] 找到容器: %CONTAINER_NAME%
        echo.
        echo === 容器信息 ===
        docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | findstr /v "NAMES"
    ) else (
        echo [提示] 容器不存在，请先运行部署
    )
    
) else if "%COMMAND%"=="deploy" (
    echo [步骤] 开始部署...
    
    :: 检查文件
    if not exist "Dockerfile" (
        echo [错误] 缺少 Dockerfile
        goto :end
    )
    if not exist "app.py" (
        echo [错误] 缺少 app.py
        goto :end
    )
    
    :: 构建镜像
    echo [步骤] 构建 Docker镜像...
    docker build -t "%PROJECT_NAME%" .
    if %errorLevel% neq 0 (
        echo [错误] 镜像构建失败
        goto :end
    )
    
    :: 停止现有容器
    docker stop "%CONTAINER_NAME%" >nul 2>&1
    docker rm "%CONTAINER_NAME%" >nul 2>&1
    
    :: 启动新容器
    echo [步骤] 启动容器...
    if not exist "uploads" mkdir uploads
    docker run -d --name "%CONTAINER_NAME%" -p "%HOST_PORT%:5000" -v "%cd%\uploads:/app/uploads" "%PROJECT_NAME%"
    
    if %errorLevel% equ 0 (
        echo [成功] 部署完成！
        echo.
        echo 访问地址: http://localhost:%HOST_PORT%
        echo 查看日志: %~n0 logs
    ) else (
        echo [错误] 容器启动失败
    )
    
) else if "%COMMAND%"=="logs" (
    echo [步骤] 查看容器日志...
    docker logs "%CONTAINER_NAME%" --tail 50
    
) else (
    echo [错误] 未知命令: %COMMAND%
    echo 运行 '%~n0 help' 查看帮助
)

:end
echo.
pause