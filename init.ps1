# 部署后初始化脚本

Write-Host "电商价格监控系统 - 初始化" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

# 1. 初始化数据库
Write-Host "`n步骤 1: 初始化数据库..." -ForegroundColor Yellow
docker exec -it price_monitor_backend python init_db.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "数据库初始化成功！" -ForegroundColor Green
} else {
    Write-Host "数据库初始化失败！" -ForegroundColor Red
    exit 1
}

# 2. 测试后端API
Write-Host "`n步骤 2: 测试后端API..." -ForegroundColor Yellow
docker exec -it price_monitor_backend python test_api.py

# 3. 显示服务信息
Write-Host "`n================================" -ForegroundColor Green
Write-Host "初始化完成！" -ForegroundColor Green
Write-Host "`n服务访问地址:" -ForegroundColor Cyan
Write-Host "  前端: http://localhost" -ForegroundColor White
Write-Host "  后端API: http://localhost:8000" -ForegroundColor White
Write-Host "  API文档: http://localhost:8000/docs" -ForegroundColor White
Write-Host "`n下一步:" -ForegroundColor Cyan
Write-Host "  1. 访问前端页面注册账号" -ForegroundColor White
Write-Host "  2. 配置电商平台API凭证" -ForegroundColor White
Write-Host "  3. 添加商品开始监控" -ForegroundColor White
Write-Host "`n查看日志:" -ForegroundColor Cyan
Write-Host "  docker-compose logs -f backend" -ForegroundColor White
Write-Host "  docker-compose logs -f frontend" -ForegroundColor White
