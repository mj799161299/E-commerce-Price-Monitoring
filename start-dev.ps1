# 前端本地开发模式启动脚本

Write-Host "启动前端开发服务器..." -ForegroundColor Green

# 检查是否在frontend目录
if (-not (Test-Path "package.json")) {
    Write-Host "错误: 请在frontend目录下运行此脚本" -ForegroundColor Red
    Write-Host "使用方法: cd frontend; ..\start-dev.ps1" -ForegroundColor Yellow
    exit 1
}

# 检查node_modules
if (-not (Test-Path "node_modules")) {
    Write-Host "首次运行，正在安装依赖..." -ForegroundColor Yellow
    npm install
}

Write-Host "`n前端开发服务器配置:" -ForegroundColor Cyan
Write-Host "  本地地址: http://localhost:3000" -ForegroundColor White
Write-Host "  后端代理: http://localhost:8000" -ForegroundColor White
Write-Host "`n提示: 修改代码会自动热更新" -ForegroundColor Yellow
Write-Host "按 Ctrl+C 停止服务器`n" -ForegroundColor Yellow

# 启动开发服务器
npm run dev
