#!/bin/bash
# 配网通 - 创建UOS桌面快捷方式

APP_NAME="配网通"
APP_PATH="$(cd "$(dirname "$0")/dist" && pwd)/配网通"
ICON_PATH="$(cd "$(dirname "$0")" && pwd)/ico.ico"
DESKTOP_FILE="$HOME/Desktop/${APP_NAME}.desktop"

cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=${APP_NAME}
Comment=企业级交换路由自动配置系统
Exec=${APP_PATH}
Icon=${ICON_PATH}
Terminal=false
Categories=Network;Utility;
EOF

chmod +x "$DESKTOP_FILE"
echo "桌面快捷方式已创建: $DESKTOP_FILE"
