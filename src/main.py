import asyncio
import logging
import threading

from helios import HeliosClient
from generated import TelemetryPacket, FlightState
from app import socketio, app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def flight_state_name(state: int) -> str:
    """Convert FlightState enum to string."""
    state_names = {
        FlightState.STANDBY: "STANDBY",
        FlightState.ASCENT: "ASCENT",
        FlightState.MACH_LOCK: "MACH_LOCK",
        FlightState.DROGUE_DESCENT: "DROGUE_DESCENT",
        FlightState.MAIN_DESCENT: "MAIN_DESCENT",
        FlightState.LANDED: "LANDED",
    }
    return state_names.get(state, f"UNKNOWN_{state}")


def broadcast_telemetry(telemetry: TelemetryPacket, error_count: int = 0, last_error: bool = False) -> None:
    """Broadcast telemetry data to all connected overlay clients via Socket.IO."""
    data_to_broadcast = {
        "status": flight_state_name(telemetry.state),
        "telemetry": {
            "counter": telemetry.counter,
            "timestamp_ms": telemetry.timestamp_ms,
            "state": int(telemetry.state),
            "accel_x": telemetry.accel_x,
            "accel_y": telemetry.accel_y,
            "accel_z": telemetry.accel_z,
            "gyro_x": telemetry.gyro_x,
            "gyro_y": telemetry.gyro_y,
            "gyro_z": telemetry.gyro_z,
            "kf_altitude": telemetry.kf_altitude,
            "kf_velocity": telemetry.kf_velocity,
            "kf_alt_variance": telemetry.kf_alt_variance,
            "kf_vel_variance": telemetry.kf_vel_variance,
            "baro0_healthy": telemetry.baro0_healthy,
            "baro0_pressure": telemetry.baro0_pressure,
            "baro1_healthy": telemetry.baro1_healthy,
            "baro1_pressure": telemetry.baro1_pressure,
            "gps_latitude": telemetry.gps_latitude,
            "gps_longitude": telemetry.gps_longitude,
            "gps_altitude": telemetry.gps_altitude,
            "gps_speed": telemetry.gps_speed,
            "gps_sats": telemetry.gps_sats,
            "gps_fix": telemetry.gps_fix,
            "packet_count": telemetry.counter,
            "error_count": error_count,
            "last_error": last_error,
        },
        "system": {}
    }
    socketio.emit('push_data', data_to_broadcast)


async def main() -> None:
    """Main coroutine - connect to Helios and stream telemetry to overlay."""
    # Start Flask server in background thread
    flask_thread = threading.Thread(
        target=lambda: socketio.run(app, host='0.0.0.0', port=8080, debug=False),
        daemon=True
    )
    flask_thread.start()
    logger.info("Flask server started on http://0.0.0.0:8080")

    # Initialize Helios client
    helios_client = HeliosClient(
        core_address="Helios",
        core_port=5000,
        node_uri="Helios.FALCON.Livestream",
    )

    try:
        await helios_client.connect()
        logger.info("Connected to Helios core")

        error_count = 0
        last_telemetry = None
        async with helios_client.subscribe_event(
            address="Helios.FALCON.Telemetry",
            event_name="telemetry",
        ) as events:
            logger.info("Subscribed to telemetry stream")
            async for event in events:
                if not event.data or len(event.data) < 15:
                    error_count += 1
                    if last_telemetry:
                        broadcast_telemetry(last_telemetry, error_count, last_error=True)
                    continue

                try:
                    # Parse incoming data as TelemetryPacket from protobuf schema
                    telemetry = TelemetryPacket().parse(event.data)
                    last_telemetry = telemetry

                    # Broadcast to all connected overlay clients with good packet status
                    broadcast_telemetry(telemetry, error_count, last_error=False)

                    logger.debug(
                        f"[Telemetry] Broadcasted: state={flight_state_name(telemetry.state)}, "
                        f"alt={telemetry.kf_altitude:.1f}m, vel={telemetry.kf_velocity:.1f}m/s"
                    )

                except Exception as e:
                    error_count += 1
                    if last_telemetry:
                        broadcast_telemetry(last_telemetry, error_count, last_error=True)
                    logger.error(f"Error parsing packet: {e}")
                    continue

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        await helios_client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())