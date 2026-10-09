FROM python:3.11-slim
WORKDIR /app
ENV APP_ENV=production
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN addgroup --system rulelock && adduser --system --ingroup rulelock rulelock
COPY --chown=rulelock:rulelock . .
RUN python train_model.py
USER rulelock
EXPOSE 5001
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT:-5001} --workers ${WEB_CONCURRENCY:-2} --preload app:app"]
