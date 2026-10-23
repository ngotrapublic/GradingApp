"""Serve api/index.py's `handler` like Vercel does (test only)."""
import http.server, os, sys
APP = '/Users/mac/Tra/SE9_ElecCircuitLab/HCM/GradingApp'
sys.path.insert(0, APP); sys.path.insert(0, APP + '/api')
import index
srv = http.server.ThreadingHTTPServer(('127.0.0.1', int(os.environ['PORT'])), index.handler)
print('vercel sim on', os.environ['PORT'], flush=True)
srv.serve_forever()
