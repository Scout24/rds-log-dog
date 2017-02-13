import os

def unset_http_proxy():
    os.environ['http_proxy'] = ''
    os.environ['http_proxy'] = ''
    os.environ['HTTPS_PROXY'] = ''
    os.environ['HTTP_PROXY'] = ''
