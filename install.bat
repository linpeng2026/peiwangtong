@echo off
echo ========================================
echo 企业级交换路由自动配置系统 - 依赖安装
echo ========================================
echo.

echo [1/2] 升级pip...
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
echo.

echo [2/2] 安装依赖包...
python -m pip install paramiko requests -i https://pypi.tuna.tsinghua.edu.cn/simple
echo.

echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 现在可以运行 python main.py 启动程序
echo.
pause
