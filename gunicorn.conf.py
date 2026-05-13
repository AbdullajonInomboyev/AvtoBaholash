# gunicorn sozlamalari
bind             = "0.0.0.0:8000"
workers          = 3          # CPU*2 + 1
worker_class     = "sync"
timeout          = 120
keepalive        = 5
max_requests     = 1000
max_requests_jitter = 100
loglevel         = "info"
accesslog        = "logs/access.log"
errorlog         = "logs/error.log"
