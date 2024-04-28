import tkinter as tk
from tkinter import filedialog
import serial

class FileUploaderApp:
    def __init__(self, master):
        self.master = master
        self.master.title("File Uploader")

        self.file_path = None
        self.serial_port = 'COM10'  # Adjust the serial port as needed
        self.baud_rate = 115200  # Adjust the baud rate as needed
        self.ser = None

        self.label = tk.Label(master, text="Select a file:")
        self.label.pack()

        self.select_button = tk.Button(master, text="Select File", command=self.select_file)
        self.select_button.pack()

        self.connect_button = tk.Button(master, text="Connect", command=self.connect_serial)
        self.connect_button.pack()

        self.disconnect_button = tk.Button(master, text="Disconnect", command=self.disconnect_serial, state=tk.DISABLED)
        self.disconnect_button.pack()

        self.upload_button = tk.Button(master, text="Upload File", command=self.upload_file)
        self.upload_button.pack()

        self.status_label = tk.Label(master, text="")
        self.status_label.pack()

    def select_file(self):
        self.file_path = filedialog.askopenfilename()

    def connect_serial(self):
        try:
            self.ser = serial.Serial(self.serial_port, self.baud_rate, timeout=5)
            self.status_label.config(text="Connected to serial port.")
            self.connect_button.config(state=tk.DISABLED)
            self.disconnect_button.config(state=tk.NORMAL)
        except Exception as e:
            self.status_label.config(text=f"Error connecting to serial port: {e}")

    def disconnect_serial(self):
        try:
            if self.ser is not None:
                self.ser.close()
                self.status_label.config(text="Disconnected from serial port.")
                self.connect_button.config(state=tk.NORMAL)
                self.disconnect_button.config(state=tk.DISABLED)
        except Exception as e:
            self.status_label.config(text=f"Error disconnecting from serial port: {e}")

    def upload_file(self):
        if self.ser is None or not self.ser.is_open:
            self.status_label.config(text="Serial port not connected.")
            return

        if self.file_path is None:
            self.status_label.config(text="Please select a file.")
            return

        try:
            self.ser.write(b"UPLOAD_START\n")
            with open(self.file_path, 'rb') as f:
                file_data = f.read()
                self.ser.write(file_data)
            self.ser.write(b"UPLOAD_END\n")
            self.status_label.config(text="File uploaded successfully.")
        except Exception as e:
            self.status_label.config(text=f"Error uploading file: {e}")

def main():
    root = tk.Tk()
    app = FileUploaderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
