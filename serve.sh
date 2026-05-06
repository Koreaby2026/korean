#!/usr/bin/env bash
# Запускает локальный сервер на порту 8765.
# Открой index.html на компе: http://localhost:8765/
# С телефона (в той же Wi-Fi сети): http://<IP-компа>:8765/
# IP компа покажется в выводе ниже.

cd "$(dirname "$0")"
IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "—")
echo ""
echo "  📱 С телефона (та же Wi-Fi):  http://$IP:8765/"
echo "  💻 С компа:                   http://localhost:8765/"
echo ""
echo "  Ctrl+C чтобы остановить."
echo ""
python3 -m http.server 8765
