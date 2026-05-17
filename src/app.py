from flask import Flask, render_template, Blueprint
from flask_socketio import SocketIO

app = Flask(__name__,)
# IMPORTANT: cors_allowed_origins="*" for OBS compatibility
# async_mode='threading' avoids eventlet monkey-patching, which breaks asyncio
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Create a blueprint specifically for your assets
assets_bp = Blueprint('assets', __name__, 
                      static_url_path='/assets', 
                      static_folder='assets')

app.register_blueprint(assets_bp)


@app.route('/overlay')
def overlay():
    return render_template('overlay.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

# We only listen on the admin endpoint
@socketio.on('admin_update')
def handle_admin_data(data):
    # When data comes from the admin panel, we BROADCAST it to all clients (overlay)
    # This acts as the push mechanism.
    print(f"Server received data to push: {data}")
    
    # Pre-process your Helios model data here if needed before broadcast
    data_to_broadcast = {
        "status": data.get("status", "Standby"),
        "telemetry": data.get("telemetry", {}),
        "system": data.get("system", {})
    }
    socketio.emit('push_data', data_to_broadcast)

if __name__ == '__main__':
    # Map port 8080 inside Docker
    socketio.run(app, host='0.0.0.0', port=8080)