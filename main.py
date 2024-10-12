import matplotlib
matplotlib.use('Qt5Agg')  # Set the backend to Qt5Agg for interactive plotting

import serial
import binascii
import struct
import time
import argparse
from datetime import datetime
import sys
import matplotlib.pyplot as plt

plt.ion()  # Enable interactive mode for dynamic updating

# Global flag to track if the window is closed
program_running = True

# Function to handle the window close event
def on_close(event):
    global program_running
    print(f"{get_timestamp()} - Plot window closed. Exiting program.")
    program_running = False

# Function to get the current timestamp with milliseconds
def get_timestamp():
    now = datetime.now()
    return now.strftime('%H:%M:%S') + f'.{now.microsecond // 1000:03d}'

# Function to decode the RX message
def decode_vibration_data(data):
    if len(data) != 29:
        print(f"Invalid data length: {len(data)}. Expected 29 bytes.")
        return None

    AXH, AXL, AYH, AYL, AZH, AZL = data[3:9]

    AX = (AXH << 8) | AXL
    AY = (AYH << 8) | AYL
    AZ = (AZH << 8) | AZL

    AX = struct.unpack('h', struct.pack('H', AX))[0]
    AY = struct.unpack('h', struct.pack('H', AY))[0]
    AZ = struct.unpack('h', struct.pack('H', AZ))[0]

    AX_corrected = AX / 32768 * 16
    AY_corrected = AY / 32768 * 16
    AZ_corrected = AZ / 32768 * 16

    CRCH, CRCL = data[-2], data[-1]
    CRC = (CRCH << 8) | CRCL

    return AX_corrected, AY_corrected, AZ_corrected, CRC

# Function to parse command-line arguments and set default values
def parse_arguments():
    parser = argparse.ArgumentParser(description="3-Axis Vibrometer Data Reader")

    # Set default values for arguments
    parser.add_argument('--port', type=str, default='/dev/ttyUSB0', help="Serial port location (e.g., /dev/ttyUSB0 or COM3)")
    parser.add_argument('--baudrate', type=int, default=230400, help="Baud rate for the serial port (default: 230400)")
    parser.add_argument('--max', type=int, default=500, help="Number of messages to show min/max after processing (default: 500)")
    parser.add_argument('--live', action='store_true', help="Show live decoded AX, AY, AZ, and CRC data")
    parser.add_argument('--plot', action='store_true', help="Plot min/max AX, AY, AZ values after processing max messages")
    parser.add_argument('--debug', action='store_true', help="Enable debug mode")
    parser.add_argument('--line', type=float, default=None, help="Draw a horizontal line at this value and its negative (e.g., --line 6.1)")

    args = parser.parse_args()

    # Handle exceptions related to invalid arguments
    if args.baudrate <= 0:
        print("Error: Baud rate must be a positive integer.")
        parser.print_help()
        sys.exit(1)

    if args.max <= 0:
        print("Error: Max messages must be a positive integer.")
        parser.print_help()
        sys.exit(1)

    # Print all arguments received
    print(f"Arguments: port={args.port}, baudrate={args.baudrate}, max={args.max}, live={args.live}, plot={args.plot}, debug={args.debug}, line={args.line}")
    
    return args

# Function to read exactly 29 bytes from the serial port (with timeout)
def read_exact_message(ser, expected_length=29, timeout=0.1):
    buffer = b''
    start_time = time.time()

    while len(buffer) < expected_length:
        byte = ser.read(1)
        if byte:
            buffer += byte
            start_time = time.time()
        else:
            if time.time() - start_time > timeout:
                break

    return buffer

# Function to track and maintain min/max values of AX, AY, AZ and timestamps
def track_min_max(ax_list, ay_list, az_list, timestamp_list, ax, ay, az):
    current_timestamp = get_timestamp()
    
    ax_list.append(ax)
    ay_list.append(ay)
    az_list.append(az)
    timestamp_list.append(current_timestamp)

    ax_min = min(ax_list)
    ax_max = max(ax_list)
    ax_min_time = timestamp_list[ax_list.index(ax_min)]
    ax_max_time = timestamp_list[ax_list.index(ax_max)]

    ay_min = min(ay_list)
    ay_max = max(ay_list)
    ay_min_time = timestamp_list[ay_list.index(ay_min)]
    ay_max_time = timestamp_list[ay_list.index(ay_max)]

    az_min = min(az_list)
    az_max = max(az_list)
    az_min_time = timestamp_list[az_list.index(az_min)]
    az_max_time = timestamp_list[az_list.index(az_max)]

    return (ax_min, ax_max, ax_min_time, ax_max_time,
            ay_min, ay_max, ay_min_time, ay_max_time,
            az_min, az_max, az_min_time, az_max_time)

# Function to plot and update the min/max values in the same window
def plot_min_max(ax_min, ax_max, ay_min, ay_max, az_min, az_max, line_value=None):
    labels = ['AX', 'AY', 'AZ']
    min_values = [ax_min, ay_min, az_min]
    max_values = [ax_max, ay_max, az_max]

    # Clear the previous plot and create a new one
    plt.clf()

    # Set background color based on the min/max values in relation to the line range
    if line_value is not None:
        if (ax_min >= -line_value and ax_max <= line_value and
            ay_min >= -line_value and ay_max <= line_value and
            az_min >= -line_value and az_max <= line_value):
            # All values are within the range, set background to green
            plt.gcf().patch.set_facecolor('green')
        else:
            # Any value is outside the range, set background to red
            plt.gcf().patch.set_facecolor('red')
    else:
        # Default background color when no line is specified
        plt.gcf().patch.set_facecolor('white')

    plt.bar(labels, min_values, label='Min', color='blue', width=0.4, align='center')
    plt.bar(labels, max_values, label='Max', color='red', width=0.4, align='edge')
    
    plt.xlabel('Axis')
    plt.ylabel('Values')
    plt.title('Min/Max Values of AX, AY, AZ')

    # Set the y-axis scale from -16 to +16
    plt.ylim(-16, 16)

    # If line_value is provided, draw the lines
    if line_value is not None:
        plt.axhline(y=line_value, color='green', linestyle='--', label=f'+{line_value}')
        plt.axhline(y=-line_value, color='green', linestyle='--', label=f'-{line_value}')

    plt.legend()

    # Draw the updated plot without opening a new window
    plt.pause(0.001)  # Small pause to allow the plot to update

# Main function
def main():
    global program_running
    try:
        args = parse_arguments()

        debug = args.debug
        port = args.port
        baudrate = args.baudrate
        max_messages = args.max  # Number of messages to process before showing min/max
        show_live = args.live  # Show live decoded data if --live is used
        plot_data = args.plot  # Plot data if --plot is used

        # Lists to store the values of AX, AY, AZ, and timestamps
        ax_list, ay_list, az_list, timestamp_list = [], [], [], []
        message_count = 0  # Counter to track the number of messages processed

        # Set up the close event handler to detect when the plot window is closed
        fig = plt.figure()
        fig.canvas.mpl_connect('close_event', on_close)

        try:
            ser = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=0.05  # Reduced timeout for faster operation
            )

            if ser.is_open:
                print(f"{get_timestamp()} - Serial port {ser.name} is open.")

            hex_string = '50030034000C0980'  # Example command to request data
            data_to_send = binascii.unhexlify(hex_string)

            try:
                print(f"{get_timestamp()} - Running. Use Ctrl+C to stop the program.")

                while program_running:  # Keep running until the window is closed
                    ser.write(data_to_send)

                    if debug:
                        print(f"{get_timestamp()} - TX: {hex_string}")

                    response = read_exact_message(ser, expected_length=29)
                    response_len = len(response)

                    if response_len == 29:
                        if debug:
                            response_hex = binascii.hexlify(response).decode('utf-8')
                            print(f"{get_timestamp()} - RX: {response_len} - {response_hex}")

                        # Decode the vibration data
                        AX_corrected, AY_corrected, AZ_corrected, CRC = decode_vibration_data(response)

                        # Show live decoded data if --live is used
                        if show_live:
                            print(f"{get_timestamp()} - AX: {AX_corrected:.3f}, AY: {AY_corrected:.3f}, AZ: {AZ_corrected:.3f}, CRC: {CRC}")

                        # Add the values and timestamp to the lists, and increment the message counter
                        (ax_min, ax_max, ax_min_time, ax_max_time,
                         ay_min, ay_max, ay_min_time, ay_max_time,
                         az_min, az_max, az_min_time, az_max_time) = track_min_max(ax_list, ay_list, az_list, timestamp_list, AX_corrected, AY_corrected, AZ_corrected)

                        message_count += 1

                        # Show min/max values after processing `max_messages` number of messages
                        if message_count == max_messages:
                            print(f"{get_timestamp()} - Min/Max AX: {ax_min:.3f} / {ax_max:.3f}  |  AY: {ay_min:.3f} / {ay_max:.3f}  |  AZ: {az_min:.3f} / {az_max:.3f}")
                            message_count = 0  # Reset the counter
                            
                            # Plot the data if --plot is used
                            if plot_data:
                                plot_min_max(ax_min, ax_max, ay_min, ay_max, az_min, az_max, line_value=args.line)
                            # Reset the lists to clear previous values for the next batch
                            ax_list.clear()
                            ay_list.clear()
                            az_list.clear()
                            timestamp_list.clear()

                    else:
                        print(f"{get_timestamp()} - Invalid response length: {response_len}. Expected 29 bytes.")

            except KeyboardInterrupt:
                print(f"{get_timestamp()} - Program interrupted with Ctrl+C, exiting...")

            finally:
                if ser.is_open:
                    ser.close()
                    print(f"{get_timestamp()} - Serial port {ser.name} is closed.")

        except serial.SerialException as e:
            print(f"{get_timestamp()} - Error: Could not open serial port: {str(e)}")
            sys.exit(1)

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

# Entry point for the script
if __name__ == '__main__':
    main()
