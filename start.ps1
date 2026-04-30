# 快速启动脚本（Windows PowerShell）

Write-Host "电商价格监控系统 - 快速启动" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

# 检查Docker是否运行
Write-Host "`n检查Docker状态..." -ForegroundColor Yellow
docker info > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: Docker未运行，请先启动Docker Desktop" -ForegroundColor Red
    exit 1
}

# 检查环境变量文件
if (-not (Test-Path "backend\.env")) {
    Write-Host "`n创建环境变量文件..." -ForegroundColor Yellow
    Copy-Item "backend\.env.example" "backend\.env"
    Write-Host "已创建 backend\.env，请根据需要修改配置" -ForegroundColor Green
}

# 启动服务
Write-Host "`n启动Docker服务..." -ForegroundColor Yellow
docker-compose up -d

# 等待服务启动
Write-Host "`n等待服务启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# 检查服务状态
Write-Host "`n服务状态:" -ForegroundColor Yellow
docker-compose ps

Write-Host "`n================================" -ForegroundColor Green
Write-Host "启动完成！" -ForegroundColor Green
Write-Host "`n访问地址:" -ForegroundColor Cyan
Write-Host "  前端: http://localhost" -ForegroundColor White
Write-Host "  后端API文档: http://localhost:8000/docs" -ForegroundColor White
Write-Host "`n常用命令:" -ForegroundColor Cyan
Write-Host "  查看日志: docker-compose logs -f" -ForegroundColor White
Write-Host "  停止服务: docker-compose down" -ForegroundColor White
Write-Host "  重启服务: docker-compose restart" -ForegroundColor White
