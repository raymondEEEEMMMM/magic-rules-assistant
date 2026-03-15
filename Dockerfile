FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY functions/mtgAsk/backend/ ./backend/
COPY functions/mtgAsk/backend/data/ ./data/

# 复制卡牌数据库（如果存在）
COPY functions/mtgAsk/backend/data/*.db* ./data/ 2>/dev/null || true

EXPOSE 3000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "3000"]
