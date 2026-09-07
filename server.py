import ctypes
import http.server
import json
import os
import platform
import threading
import time
import webbrowser

ROOT = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(ROOT, 'settings.json')
PORT = 8877

def load_settings():
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as settings_file:
            value = json.load(settings_file)
            return value if isinstance(value, dict) else {}
    except (OSError, ValueError, TypeError):
        return {}

STATE = {'keyboard_seq': 0, 'mouse_seq': 0, 'mouse_down': False, 'mouse_move': 0,
         'mouse_dx': 0, 'mouse_dy': 0, 'voice_level': 0, 'settings': load_settings(),
         'input_backend': 'starting', 'input_heartbeat': 0, 'voice_updated': 0,
         'voice_seq': 0}

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()
    def do_GET(self):
        if self.path.startswith('/state'):
            snapshot = dict(STATE)
            now = time.time()
            # A closed mouth and released mouse are the safe state if a sender stops.
            if now - snapshot.get('voice_updated', 0) > 0.65:
                snapshot['voice_level'] = 0
            if now - snapshot.get('input_heartbeat', 0) > 1.0:
                snapshot['mouse_down'] = False
                snapshot['mouse_dx'] = 0
                snapshot['mouse_dy'] = 0
            data = json.dumps(snapshot).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        super().do_GET()
    def do_POST(self):
        try:
            length = min(int(self.headers.get('Content-Length', '0')), 4096)
            payload = json.loads(self.rfile.read(length) or b'{}')
            if self.path == '/voice':
                STATE['voice_level'] = max(0, min(100, float(payload.get('level', 0))))
                STATE['voice_updated'] = time.time()
                STATE['voice_seq'] += 1
            elif self.path == '/settings' and isinstance(payload, dict):
                STATE['settings'] = payload
                with open(SETTINGS_FILE, 'w', encoding='utf-8') as settings_file:
                    json.dump(payload, settings_file, indent=2)
            else:
                self.send_error(404)
                return
            self.send_response(204)
            self.end_headers()
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            self.send_error(400)
    def log_message(self, fmt, *args):
        if not str(args[0]).startswith(('GET /state', 'POST /voice', 'POST /settings')):
            super().log_message(fmt, *args)

def windows_input_loop():
    user32 = ctypes.windll.user32
    class Point(ctypes.Structure):
        _fields_ = [('x', ctypes.c_long), ('y', ctypes.c_long)]
    keyboard_keys = [key for key in range(8, 255) if key not in (1, 2, 4, 5, 6)]
    mouse_keys = (1, 2, 4)
    keys_down, mouse_was_down, last_pointer = set(), False, None
    STATE['input_backend'] = 'Windows direct input active'
    while True:
        current_keys = {key for key in keyboard_keys if user32.GetAsyncKeyState(key) & 0x8000}
        new_keys = current_keys - keys_down
        if new_keys:
            STATE['keyboard_seq'] += len(new_keys)
        keys_down = current_keys
        mouse_is_down = any(user32.GetAsyncKeyState(key) & 0x8000 for key in mouse_keys)
        if mouse_is_down and not mouse_was_down:
            STATE['mouse_seq'] += 1
        STATE['mouse_down'] = bool(mouse_is_down)
        mouse_was_down = mouse_is_down
        point = Point()
        if user32.GetCursorPos(ctypes.byref(point)):
            pointer = (point.x, point.y)
            if last_pointer is not None:
                dx, dy = pointer[0] - last_pointer[0], pointer[1] - last_pointer[1]
                if dx or dy:
                    STATE['mouse_move'] = time.time()
                    STATE['mouse_dx'] = max(-1, min(1, dx / 24))
                    STATE['mouse_dy'] = max(-1, min(1, dy / 24))
            last_pointer = pointer
        STATE['input_heartbeat'] = time.time()
        time.sleep(0.008)

def fallback_input_loop():
    from pynput import keyboard, mouse
    last_pointer = [None]
    def key_pressed(key):
        STATE['keyboard_seq'] += 1
    def mouse_clicked(x, y, button, pressed):
        STATE['mouse_down'] = bool(pressed)
        if pressed:
            STATE['mouse_seq'] += 1
    def mouse_moved(x, y):
        if last_pointer[0] is not None:
            dx, dy = x - last_pointer[0][0], y - last_pointer[0][1]
            if dx or dy:
                STATE['mouse_move'] = time.time()
                STATE['mouse_dx'] = max(-1, min(1, dx / 24))
                STATE['mouse_dy'] = max(-1, min(1, dy / 24))
        last_pointer[0] = (x, y)
    STATE['input_backend'] = 'Compatibility input active'
    key_listener = keyboard.Listener(on_press=key_pressed)
    mouse_listener = mouse.Listener(on_click=mouse_clicked, on_move=mouse_moved)
    key_listener.start()
    mouse_listener.start()
    while key_listener.is_alive() and mouse_listener.is_alive():
        STATE['input_heartbeat'] = time.time()
        time.sleep(0.1)

def start_input_capture():
    target = windows_input_loop if platform.system() == 'Windows' else fallback_input_loop
    threading.Thread(target=target, daemon=True, name='kevin-input-capture').start()

if __name__ == '__main__':
    start_input_capture()
    print(f'Kevin Production Rig controls: http://localhost:{PORT}')
    print(f'OBS source: http://localhost:{PORT}/?obs=1')
    print('Input capture: starting... Press Ctrl+C to stop.')
    threading.Timer(1, lambda: webbrowser.open(f'http://localhost:{PORT}/?production=1')).start()
    try:
        http.server.ThreadingHTTPServer(('127.0.0.1', PORT), Handler).serve_forever()
    except OSError as error:
        print(f'Could not start Kevin Production Rig on port {PORT}: {error}')
        input('Press Enter to close...')
