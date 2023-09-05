import multiprocessing


def when_ready(server):
    """Called just after the server is started."""
    open("/tmp/app-initialized", "w").close()


bind = "unix:///tmp/nginx.socket"
workers = multiprocessing.cpu_count() * 2 + 1
