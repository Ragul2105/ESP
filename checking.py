import tkinter as tk
import serial
import serial.tools.list_ports
import threading
import time

class SerialReaderApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Serial Reader")

        self.label = tk.Label(master, text="Select Serial Port:")
        self.label.pack()

        self.port_listbox = tk.Listbox(master, selectmode=tk.SINGLE)
        self.port_listbox.pack()

        self.refresh_button = tk.Button(master, text="Refresh Ports", command=self.refresh_ports)
        self.refresh_button.pack()

        self.connect_button = tk.Button(master, text="Connect", command=self.connect_serial)
        self.connect_button.pack()

        self.disconnect_button = tk.Button(master, text="Disconnect", command=self.disconnect_serial, state=tk.DISABLED)
        self.disconnect_button.pack()

        self.output_label = tk.Label(master, text="Serial Output:")
        self.output_label.pack()

        self.output_text = tk.Text(master, height=10, width=50)
        self.output_text.pack()

        self.thread = None
        self.running = False
        self.update_ports_interval = 1  # Update ports every 5 seconds
        self.last_ports = self.get_serial_ports()
        self.latest_output = ""

        self.update_ports_thread = threading.Thread(target=self.update_ports_periodically)
        self.update_ports_thread.daemon = True
        self.update_ports_thread.start()

    def update_ports_periodically(self):
        while True:
            current_ports = self.get_serial_ports()
            if current_ports != self.last_ports:
                self.refresh_ports()
                self.last_ports = current_ports
            time.sleep(1)  # Check every second

    def refresh_ports(self):
        ports = self.get_serial_ports()
        self.port_listbox.delete(0, tk.END)
        for port in ports:
            self.port_listbox.insert(tk.END, port)

    def get_serial_ports(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        return ports

    def connect_serial(self):
        selected_port_index = self.port_listbox.curselection()
        if selected_port_index:
            selected_port = self.port_listbox.get(selected_port_index)
            try:
                self.ser = serial.Serial(selected_port, 115200, timeout=0.1)
                self.connect_button.config(state=tk.DISABLED)
                self.disconnect_button.config(state=tk.NORMAL)
                self.port_listbox.config(state=tk.DISABLED)

                self.running = True
                self.thread = threading.Thread(target=self.read_serial)
                self.thread.start()
            except Exception as e:
                self.output_text.insert(tk.END, f"Error connecting to serial port: {e}\n")

    def disconnect_serial(self):
        try:
            self.running = False  # Stop the thread
            if self.thread is not None:
                self.thread.join(timeout=0.1)  # Decreased timeout value
            if self.ser is not None:
                self.ser.close()  # Close the serial port
            self.connect_button.config(state=tk.NORMAL)
            self.disconnect_button.config(state=tk.DISABLED)
            self.port_listbox.config(state=tk.NORMAL)
            self.refresh_ports()  # Refresh the list of ports
            self.output_text.delete(1.0, tk.END)  # Clear the output text
        except Exception as e:
            self.output_text.insert(tk.END, f"Error disconnecting from serial port: {e}\n")

    def read_serial(self):
        while self.running:
            try:
                line = self.ser.readline().decode().strip()
                self.latest_output = line  # Store the latest output
                self.master.after(100, self.update_output_text)  # Update the text box with the latest output
            except Exception as e:
                self.output_text.insert(tk.END, f"Error reading from serial port: {e}\n")
                break

    def update_output_text(self):
        self.output_text.insert(tk.END, f"{self.latest_output}\n")  # Append latest output

def main():
    root = tk.Tk()
    app = SerialReaderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
