import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
from PIL import Image, ImageTk


# Global variables
ser = None
root = None
com_port_menu = None
output_label = None
received_frame_label = None
received_checksum_entry = None

# Function to calculate checksum
def calculate_checksum(start_byte, dev_id, cmd_id, prm_id, error_byte, data_bytes):
    return (start_byte + dev_id + cmd_id + prm_id + error_byte + sum(data_bytes)) & 0xFF

# Function to open the COM port
def open_com_port():
    global ser
    port = com_port_var.get()
    baud_rate = 9600
    try:
        ser = serial.Serial(port, baud_rate, timeout=1)
        status_label.config(text="Connected", foreground="green")
    except serial.SerialException:
        status_label.config(text="Failed to connect", foreground="red")

# Function to close the COM port
def close_com_port():
    global ser
    if ser:
        ser.close()
        ser = None
    status_label.config(text="Disconnected", foreground="red")

# Function to send the frame
def send_frame():
    if ser:
        start_byte = int(sync_field_entry.get(), 16)
        dev_id = int(dev_id_entry.get(), 16)
        cmd_id = int(cmd_id_entry.get(), 16)
        prm_id = int(param_id_entry.get(), 16)
        error_byte = int(error_byte_entry.get(), 16)
        data_bytes = [
            int(data_byte_3_entry.get(), 16),
            int(data_byte_2_entry.get(), 16),
            int(data_byte_1_entry.get(), 16),
            int(data_byte_0_entry.get(), 16)
        ]
        
        checksum = calculate_checksum(start_byte, dev_id, cmd_id, prm_id, error_byte, data_bytes)
        checksum_entry.config(state="normal")
        checksum_entry.delete(0, tk.END)
        checksum_entry.insert(0, f"{checksum:02X}")
        checksum_entry.config(state="readonly")
        
        frame = [start_byte, dev_id, cmd_id, prm_id, error_byte] + data_bytes + [checksum]
        ser.write(bytes(frame))
        
        output_label.config(text=f"Frame Sent: {start_byte:02X} {dev_id:02X} {cmd_id:02X} {prm_id:02X} "
                                 f"{error_byte:02X} {' '.join(f'{byte:02X}' for byte in data_bytes)} {checksum:02X}")
        
        # Wait and read the response frame
        receive_frame()

# Function to receive the frame
def receive_frame():
    if ser:
        response = ser.read(10)  # Assuming the frame length is 10 bytes
        if len(response) == 10:
            start_byte, dev_id, cmd_id, prm_id, error_byte, data_byte_3, data_byte_2, data_byte_1, data_byte_0, checksum = response
            
            # Display the received frame
            received_frame_label.config(text=f"Frame Received: {start_byte:02X} {dev_id:02X} {cmd_id:02X} "
                                             f"{prm_id:02X} {error_byte:02X} {data_byte_3:02X} {data_byte_2:02X} "
                                             f"{data_byte_1:02X} {data_byte_0:02X} {checksum:02X}")
            
            # Calculate the expected checksum
            calculated_checksum = calculate_checksum(start_byte, dev_id, cmd_id, prm_id, error_byte, [data_byte_3, data_byte_2, data_byte_1, data_byte_0])
            
            # Display the calculated checksum in the GUI
            received_checksum_entry.config(state="normal")
            received_checksum_entry.delete(0, tk.END)
            received_checksum_entry.insert(0, f"{calculated_checksum:02X}")
            received_checksum_entry.config(state="readonly")

# Function to update available COM ports in the dropdown menu
def update_com_ports():
    ports = serial.tools.list_ports.comports()
    com_port_var.set('')
    com_port_menu["values"] = [port.device for port in ports]

# Function to create the GUI
def create_gui():
    global root, com_port_menu, output_label, received_frame_label, received_checksum_entry

    root = tk.Tk()
    root.title("JE-Dresden WSA BLE")
    # Load image with Pillow
    image = Image.open("D:\Documents and Settings\Muthukumar Murugesan\Downloads\JE_lOGO.png")
    image = image.resize((32, 32), Image.LANCZOS)
    photo = ImageTk.PhotoImage(image)

    # Set the icon
    root.iconphoto(True, photo)



    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    # COM Port Selection
    ttk.Label(frame, text="Select COM Port:").grid(row=0, column=0, sticky=tk.W)
    global com_port_var
    com_port_var = tk.StringVar()
    com_port_menu = ttk.Combobox(frame, textvariable=com_port_var)
    com_port_menu.grid(row=0, column=1, sticky=(tk.W, tk.E))
    update_com_ports()

    ttk.Button(frame, text="Refresh Ports", command=update_com_ports).grid(row=0, column=2, sticky=tk.W)
    ttk.Button(frame, text="Open Port", command=open_com_port).grid(row=0, column=3, sticky=tk.W)
    ttk.Button(frame, text="Close Port", command=close_com_port).grid(row=0, column=4, sticky=tk.W)

    global status_label
    status_label = ttk.Label(frame, text="Disconnected", foreground="red")
    status_label.grid(row=0, column=5, sticky=tk.W)
 
    # Sending Frame Section
    ttk.Label(frame, text="Sync Field:").grid(row=1, column=0, sticky=tk.W)
    global sync_field_entry
    sync_field_entry = ttk.Entry(frame, width=5)
    sync_field_entry.grid(row=1, column=1, sticky=(tk.W, tk.E))

    ttk.Label(frame, text="DEV_ID:").grid(row=1, column=2, sticky=tk.W)
    global dev_id_entry
    dev_id_entry = ttk.Entry(frame, width=5)
    dev_id_entry.grid(row=1, column=3, sticky=(tk.W, tk.E))

    ttk.Label(frame, text="CMD_ID:").grid(row=1, column=4, sticky=tk.W)
    global cmd_id_entry
    cmd_id_entry = ttk.Entry(frame, width=5)
    cmd_id_entry.grid(row=1, column=5, sticky=(tk.W, tk.E))

    ttk.Label(frame, text="Parameter ID:").grid(row=1, column=6, sticky=tk.W)
    global param_id_entry
    param_id_entry = ttk.Entry(frame, width=5)
    param_id_entry.grid(row=1, column=7, sticky=(tk.W, tk.E))

    ttk.Label(frame, text="Error Byte:").grid(row=1, column=8, sticky=tk.W)
    global error_byte_entry
    error_byte_entry = ttk.Entry(frame, width=5)
    error_byte_entry.grid(row=1, column=9, sticky=(tk.W, tk.E)) 

    ttk.Label(frame, text="Data Byte 3:").grid(row=2, column=0, sticky=tk.W)
    global data_byte_3_entry
    data_byte_3_entry = ttk.Entry(frame, width=5)
    data_byte_3_entry.grid(row=2, column=1, sticky=(tk.W, tk.E))

    ttk.Label(frame, text="Data Byte 2:").grid(row=2, column=2, sticky=tk.W)
    global data_byte_2_entry
    data_byte_2_entry = ttk.Entry(frame, width=5)
    data_byte_2_entry.grid(row=2, column=3, sticky=(tk.W, tk.E))

    ttk.Label(frame, text="Data Byte 1:").grid(row=2, column=4, sticky=tk.W)
    global data_byte_1_entry
    data_byte_1_entry = ttk.Entry(frame, width=5)
    data_byte_1_entry.grid(row=2, column=5, sticky=(tk.W, tk.E))

    ttk.Label(frame, text="Data Byte 0:").grid(row=2, column=6, sticky=tk.W)
    global data_byte_0_entry
    data_byte_0_entry = ttk.Entry(frame, width=5)
    data_byte_0_entry.grid(row=2, column=7, sticky=(tk.W, tk.E))

    ttk.Label(frame, text="Checksum:").grid(row=2, column=8, sticky=tk.W)
    global checksum_entry
    checksum_entry = ttk.Entry(frame, width=5, state="readonly")
    checksum_entry.grid(row=2, column=9, sticky=(tk.W, tk.E))
  
    send_button = ttk.Button(frame, text="Send Frame", command=send_frame)
    send_button.grid(row=3, column=0, columnspan=15, sticky=(tk.W, tk.E))

    output_label = ttk.Label(frame, text="")
    output_label.grid(row=4, column=0, columnspan=10, sticky=(tk.W, tk.E))

    # Receiving Frame Section
    ttk.Label(frame, text="Received Frame:").grid(row=5, column=0, columnspan=10, sticky=tk.W)
    
    received_frame_label = ttk.Label(frame, text="")
    received_frame_label.grid(row=6, column=0, columnspan=10, sticky=(tk.W, tk.E))

    ttk.Label(frame, text="Received Checksum:").grid(row=9, column=0, sticky=tk.W)
    received_checksum_entry = ttk.Entry(frame, width=5, state="readonly")
    received_checksum_entry.grid(row=9, column=1, sticky=(tk.W, tk.E))

    root.mainloop()

if __name__ == "__main__":
    create_gui()
