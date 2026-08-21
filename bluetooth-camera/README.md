# README

MicroPython project to send caemera data over Bluetooth Low Energy (BLE) using a Raspberry Pi Pico. The project includes a BLE sensor that can be used to advertise camera data to connected devices.

## Source files
- `bluetooth_camera.py`: Main application file that initializes the BLE sensor and updates its value
- `bluetooth_sensor.py`: Contains the `BLESensor` class that handles BLE advertising and connections
- `bluetooth_advertising.py`: Contains the `advertising_payload` function to create BLE advertising payloads

## Micropython libraries
Common and hardware specific:
https://docs.micropython.org/en/latest/library/index.html#

## Bluetooth
Micropython BLE implementation suggests using aioble package as high level micropython API for bluetooth.  
https://github.com/micropython/micropython-lib/tree/master/micropython/bluetooth/aioble

Micropython code exaamples, including BLE can be found here:
https://github.com/raspberrypi/pico-micropython-examples

There are more examples on micropython git - bonding example shows security pairing:
https://github.com/micropython/micropython/tree/master/examples/bluetooth

Example of pairing/bnonding:
https://github.com/micropython/micropython/issues/8837

Pairinig or bonding is not supported on Pico in firmware v 1.28.0 yet
https://github.com/orgs/micropython/discussions/11793
https://github.com/orgs/micropython/discussions/13612

Sample for push notifications (not Pico though):
https://hubble.com/community/guides/how-to-use-esp32-bluetooth-le-with-micropython-for-rapid-prototyping/

General info about bluetooth security:
https://www.allaboutcircuits.com/technical-articles/understanding-bluetooth-le-pairingstep-by-step/
https://www.allaboutcircuits.com/technical-articles/understanding-security-keys-in-bluetooth-low-energy/

### MTU
MTU (Maximum Transmission Unit) is the largest size (in bytes) of a single data packet that can be exchanged in one BLE ATT (Attribute Protocol) transaction.  
Default BLE MTU is 23 bytes, of which 3 bytes are ATT protocol overhead, leaving 20 bytes usable for characteristic data per packet.  
BLE 4.2+ and 5 support MTU negotiation up to 517 bytes, giving more usable payload per packet (negotiated MTU − 3 bytes overhead).  
It directly limits how much of your image row you can send in a single characteristic write/notify — hence why chunking is needed

### Attribute data
The `_CAMERA_ROW_CHAR` characteristic value is a custom, application-defined byte layout — BLE itself treats a characteristic value as an opaque blob and imposes no header or structure on it. Predefined BLE characteristics (like heart rate, battery level, etc.) have their own defined formats, but for custom data like camera rows, you define your own.

In BLE code using Python/MicroPython's `struct` module, the "header string" is just a `struct` format string. The general symbols you can use:

**Byte order/alignment prefix** (first character, optional):
| Symbol | Meaning |
|---|---|
| `<` | little-endian, no padding |
| `>` | big-endian, no padding |
| `!` | network (big-endian), no padding |
| `=` | native byte order, no padding |
| `@` | native byte order, native alignment/padding (default if omitted) |

BLE is little-endian by convention, so `<` is standard (as used in `_CAMERA_ROW_HEADER_FORMAT`).

**Field type codes** (each maps to a fixed byte width):
| Symbol | C type | Size | Python type |
|---|---|---|---|
| `x` | pad byte | 1 | none |
| `c` | char | 1 | bytes (len 1) |
| `b` / `B` | signed/unsigned char | 1 | int |
| `?` | bool | 1 | bool |
| `h` / `H` | signed/unsigned short | 2 | int |
| `i` / `I` | signed/unsigned int | 4 | int |
| `l` / `L` | signed/unsigned long | 4 | int |
| `q` / `Q` | signed/unsigned long long | 8 | int |
| `e` | half-precision float | 2 | float |
| `f` | float | 4 | float |
| `d` | double | 8 | float |
| `s` | char array (fixed length, prefix with count e.g. `4s`) | N | bytes |
| `p` | Pascal string | N | bytes |

For BLE characteristic headers you'll typically only use `<` plus `B`, `H`, `I` (and occasionally `b`/`h`/`i` for signed values) since GATT fields are almost always small unsigned integers.
https://docs.micropython.org/en/latest/library/struct.html

Attribute value is sized to fit the negotiated MTU. Only the packed header bytes are transmitted — the format string itself is
never sent, so both peripheral and central must know it independently to parse the value. The rest of the attribute value is the actual data, which is a sequence of bytes representing pixel values.

### Default Service
In addition to your custom service, the BLE stack automatically adds a default GATT service "Generic Attribute Profile" with a Service Changed characteristic.

That's the standard GATT service (UUID 0x1801), and it's automatically added by the Bluetooth stack itself (MicroPython's bluetooth module / the underlying BLE controller), not by your Python code.

Every BLE peripheral is required by the Bluetooth spec to expose a GATT service (0x1801) containing the Service Changed characteristic (0x2A05). Its purpose is to let a central device (like your phone) know when the GATT table (services/characteristics) has changed since the last connection, so the central knows it needs to re-discover services instead of using cached ones.

You'll see this automatically whenever you call bluetooth.BLE() and register services with gatts_register_services() — the stack silently inserts this service alongside yours. There's nothing to add in your code, and generally nothing you need to configure for it either (it's mostly relevant for centrals that cache GATT tables, which is common on iOS).

### Notify vs indicate
Notify and Indicate are two BLE GATT mechanisms for a peripheral to push a characteristic value to a central without the central polling/reading it:

Notify — fire-and-forget. The peripheral sends the value; there's no acknowledgment at the ATT protocol level. Lower overhead, faster, but the peripheral doesn't know if the central actually received it (could be lost if disconnected/busy).

Indicate — sends the value and waits for an acknowledgment (a confirmation) from the central before considering it delivered. This is why _IRQ_GATTS_INDICATE_DONE exists in your code (line with elif event == _IRQ_GATTS_INDICATE_DONE:) — it fires once that ack is confirmed. More reliable, but higher latency/overhead since each indication is a full round trip.

For streaming camera-row use case, notify is the better fit — you're pushing continuous chunks at high rate, and occasional drops are tolerable/recoverable via total_row_bytes framing, whereas indicate's per-chunk round-trip would throttle throughput significantly.