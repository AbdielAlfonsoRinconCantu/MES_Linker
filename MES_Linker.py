# MES Linker

# ------------------------------------------------------------------------ Libraries ------------------------------------------------------------------------ #

print("Initializing MES Linker...")
print("Importing libraries...")

from tkinter import ttk, font, filedialog
import json
import sv_ttk
import tkinter as tk
import queue
import threading
import socket
import datetime
import shutil
import os
import pywinstyles


print("Importing libraries SUCCESS \n")

# ------------------------------------ Global variables ------------------------------------------------------------------------------------------------------------ #

# Station settings
MES_Linker_Settings = "MES_Linker_Settings.json"

# Queues
UI_terminal_Queue = queue.Queue()
Device_1_Queue = queue.Queue()
MES_Queue = queue.Queue()

# Lists
Active_Sockets = []

# ------------------------------------------------ Global functions ------------------------------------------------------------------------------------------------------------------------ #


def MES_Linker_Settings_Load():
    defaults = {"Station_Name": "Station_Name", "Station_Line": "Station_Line",
                "Station_Type": "Station_Type", "Station_OPID": "Station_OPID", "MES_folder_Path": f"{os.getcwd()}", "Device_1_Socket_Host": "127.0.0.2", "Device_1_Socket_Port": 65431, "MES_Socket_Host": "127.0.0.2", "MES_Socket_Port": 65432}
    try:
        with open(MES_Linker_Settings, "r") as f:
            return {**defaults, **json.load(f)}
    except:
        return defaults


Station_Name = MES_Linker_Settings_Load()["Station_Name"]
Station_Line = MES_Linker_Settings_Load()["Station_Line"]
Station_Type = MES_Linker_Settings_Load()["Station_Type"]
Station_OPID = MES_Linker_Settings_Load()["Station_OPID"]
MES_folder_Path = MES_Linker_Settings_Load()["MES_folder_Path"]
Device_1_Socket_Host = MES_Linker_Settings_Load()["Device_1_Socket_Host"]
Device_1_Socket_Port = MES_Linker_Settings_Load()["Device_1_Socket_Port"]
MES_Socket_Host = MES_Linker_Settings_Load()["MES_Socket_Host"]
MES_Socket_Port = MES_Linker_Settings_Load()["MES_Socket_Port"]

# ------------------------------------------------ Main ------------------------------------------------------------------------------------------------------------------------ #


def main():

    UI_terminal_Queue.put("Starting MES Linker...")

    log_txt_file = f"{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f')}_{Station_Name}_Log.txt"

    root = tk.Tk()
    root.title("MES Linker")
    root.protocol("WM_DELETE_WINDOW", lambda: (
        Close_all_sockets(), root.destroy(), os._exit(0)))

    root.iconbitmap("icon.ico")

    Body_font = font.Font(family="Segoe UI", size=16)
    Terminal_font = font.Font(family="Cascadia Mono", size=11)
    sv_ttk.set_theme("dark")

    style = ttk.Style()
    style.configure("Red.TButton", foreground="#FF5555", font=Body_font)
    style.configure("Green.TButton", foreground="#55FF55", font=Body_font)

    def Print_to_terminal():
        while True:
            print_to_terminal_message = f"\n{datetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S.%f]')}: {UI_terminal_Queue.get()}"
            print(print_to_terminal_message)

            with open(log_txt_file, "a") as f:
                f.write(print_to_terminal_message)

            os.makedirs(
                f"{MES_folder_Path}\\log", exist_ok=True)
            shutil.copy2(
                log_txt_file, f"{MES_folder_Path}\\log\\{log_txt_file}")

            try:
                UI_terminal.configure(state="normal")
                UI_terminal.insert(tk.END, print_to_terminal_message)
                UI_terminal.see(tk.END)
                UI_terminal.update_idletasks()
                UI_terminal.configure(state="disabled")
            except:
                pass

    def Close_all_sockets():
        UI_terminal_Queue.put("Closing all active sockets...")
        while Active_Sockets:
            try:
                Active_Sockets.pop().close()
            except Exception as e:
                UI_terminal_Queue.put(f"{e}")

    def Start_socket_threads():

        UI_terminal_Queue.put(
            f"Station: {Station_Name}, Line: {Station_Line}, Type: {Station_Type}, OPID: {Station_OPID}")

        UI_terminal_Queue.put("Opening all sockets")

        threading.Thread(target=build_a_socket, args=(Device_1_Socket_button,
                         "Device 1", Device_1_Socket_Host, Device_1_Socket_Port, Device_1_Queue)).start()

        threading.Thread(target=build_a_socket, args=(MES_Socket_button,
                         "MES", MES_Socket_Host, MES_Socket_Port, MES_Queue)).start()

# -------------------------------------------- Message interpreter -------------------------------------------------------------------------------------------------------------------- #

    def received_message_interpreter(data, s, server_name):
        global Station_Name, Station_Line, Station_Type, Station_OPID

        match server_name:
            case "Device 1":
                MES_Queue.put(data)
                pass

# -------------------------------------------- Socket -------------------------------------------------------------------------------------------------------------------- #

    def build_a_socket(button, server_name, host, port, socket_queue):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                Active_Sockets.append(s)
                s.bind((host, port))
                UI_terminal_Queue.put(
                    f"{server_name} Socket on {host}:{port}...")
                s.listen()

                while True:
                    try:
                        conn, addr = s.accept()
                    except Exception as e:
                        UI_terminal_Queue.put(f"{server_name} Socket: {e}")
                        break

                    Active_Sockets.append(conn)
                    button.configure(style="Green.TButton")
                    UI_terminal_Queue.put(
                        f"{server_name} Socket connected by: {addr}")

                    conn.settimeout(0.05)

                    with conn:
                        while True:
                            try:
                                data = conn.recv(1024)
                                UI_terminal_Queue.put(
                                    f"{addr} {server_name} Socket received: {data.decode('utf-8')}")

                                received_message_interpreter(
                                    data, s, server_name)

                                if not data:
                                    break
                            except socket.timeout:
                                pass

                                try:

                                    # UI_terminal_Queue.put(f"Entered message sender, server_name: {server_name}, queue: {socket_queue}")

                                    message = socket_queue.get_nowait()

                                    # UI_terminal_Queue.put(f"message: {message}")

                                    conn.sendall(message)

                                    UI_terminal_Queue.put(
                                        f"{addr} {server_name} Socket sent: {message}")

                                except queue.Empty:
                                    pass

                                except Exception as e:
                                    UI_terminal_Queue.put(
                                        f"{server_name} Socket error catch: {e}")

                            except Exception as e:
                                UI_terminal_Queue.put(
                                    f"{server_name} Socket:{e}")
                                break

                        button.configure(style="Red.TButton")
                        UI_terminal_Queue.put(
                            f"{server_name} Socket disconnected by: {addr}")

        except Exception as e:
            UI_terminal_Queue.put(f"{server_name} Socket: {e}")

# -------------------------------------------- Change addresses function -------------------------------------------------------------------------------------------------------------------- #

    def Change_addresses_button_Function():
        def Change_addresses_Accept_button_Function():
            Close_all_sockets()

            targets = [
                ('Device_1_Socket', Device_1_Socket_text_box),
                ('MES_Socket', MES_Socket_text_box),
            ]

            for name, widget in targets:
                host, port = widget.get().strip().split(':')
                globals()[f"{name}_Host"] = host
                globals()[f"{name}_Port"] = int(port)

            MES_Linker_Settings_Save()

            Change_addresses_button_window.destroy()
            Start_socket_threads()

        Change_addresses_button_window = tk.Toplevel(root)
        Change_addresses_button_window.title("Change addresses")
        Change_addresses_button_window.iconbitmap("icon.ico")

        pywinstyles.apply_style(Change_addresses_button_window, "mica")

        Change_addresses_button_window_Row_2 = ttk.Frame(
            Change_addresses_button_window)
        Change_addresses_button_window_Row_2.pack(side=tk.BOTTOM)

        Change_addresses_button_window_frame = ttk.Frame(Change_addresses_button_window)
        Change_addresses_button_window_frame.pack(side=tk.TOP, padx=10, pady=10)

        Device_1_Socket_Label = ttk.Label(Change_addresses_button_window_frame, text=f"Device 1 Socket: ", font=Body_font)
        Device_1_Socket_Label.grid(row=0, column=0, sticky=tk.W, padx=10, pady=8)

        Device_1_Socket_text_box = ttk.Entry(Change_addresses_button_window_frame, font=Body_font, width=30)
        Device_1_Socket_text_box.grid(row=0, column=1, padx=10, pady=8)
        Device_1_Socket_text_box.insert(tk.END, f"{Device_1_Socket_Host}:{Device_1_Socket_Port}")

        MES_Socket_Label = ttk.Label(Change_addresses_button_window_frame, text=f"MES Socket: ", font=Body_font)
        MES_Socket_Label.grid(row=1, column=0, sticky=tk.W, padx=10, pady=8)

        MES_Socket_text_box = ttk.Entry(Change_addresses_button_window_frame, font=Body_font, width=30)
        MES_Socket_text_box.grid(row=1, column=1, padx=10, pady=8)
        MES_Socket_text_box.insert(tk.END, f"{MES_Socket_Host}:{MES_Socket_Port}")

        Change_addresses_Accept_button = ttk.Button(
            Change_addresses_button_window_Row_2, text="Accept", command=Change_addresses_Accept_button_Function)
        Change_addresses_Accept_button.pack(side=tk.LEFT, padx=10, pady=10)

        Change_addresses_Cancel_button = ttk.Button(
            Change_addresses_button_window_Row_2, text="Cancel", command=Change_addresses_button_window.destroy)
        Change_addresses_Cancel_button.pack(side=tk.LEFT, padx=10, pady=10)

# -------------------------------------------- Change Station function ------------------------------------------------------------------------------------------------------------ #

    def MES_Linker_Settings_Save():
        data = {
            "Station_Name": Station_Name,
            "Station_Line": Station_Line,
            "Station_Type": Station_Type,
            "Station_OPID": Station_OPID,
            "MES_folder_Path": MES_folder_Path,
            "Device_1_Socket_Host": Device_1_Socket_Host,
            "Device_1_Socket_Port": Device_1_Socket_Port,
            "MES_Socket_Host": MES_Socket_Host,
            "MES_Socket_Port": MES_Socket_Port
        }
        with open(MES_Linker_Settings, "w") as f:
            json.dump(data, f, indent=4, sort_keys=True)

    def Change_station_button_Function():
        def Change_station_Accept_button_Function():
            global Station_Name, Station_Line, Station_Type, Station_OPID

            Close_all_sockets()

            Station_Name = Station_Label_text_box.get().strip()
            Station_Line = Line_Label_text_box.get().strip()
            Station_Type = Type_Label_text_box.get().strip()
            Station_OPID = OPID_Label_text_box.get().strip()

            MES_Linker_Settings_Save()

            Change_station_button_window.destroy()
            Start_socket_threads()

        Change_station_button_window = tk.Toplevel(root)
        Change_station_button_window.title("Change station")
        Change_station_button_window.iconbitmap("icon.ico")

        pywinstyles.apply_style(Change_station_button_window, "mica")

        Change_station_button_window_Row_2 = ttk.Frame(
            Change_station_button_window)
        Change_station_button_window_Row_2.pack(side=tk.BOTTOM)

        Change_station_button_window_frame = ttk.Frame(Change_station_button_window)
        Change_station_button_window_frame.pack(side=tk.TOP, padx=10, pady=10)

        Station_Label = ttk.Label(Change_station_button_window_frame, text=f"Station: ", font=Body_font)
        Station_Label.grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        Station_Label_text_box = ttk.Entry(Change_station_button_window_frame, font=Body_font, width=30)
        Station_Label_text_box.grid(row=0, column=1, padx=10, pady=8)
        Station_Label_text_box.insert(tk.END, f"{Station_Name}")

        Line_Label = ttk.Label(Change_station_button_window_frame, text=f"Line: ", font=Body_font)
        Line_Label.grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
        Line_Label_text_box = ttk.Entry(Change_station_button_window_frame, font=Body_font, width=30)
        Line_Label_text_box.grid(row=1, column=1, padx=10, pady=8)
        Line_Label_text_box.insert(tk.END, f"{Station_Line}")

        Type_Label = ttk.Label(Change_station_button_window_frame, text=f"Type: ", font=Body_font)
        Type_Label.grid(row=2, column=0, sticky=tk.W, padx=10, pady=10)
        Type_Label_text_box = ttk.Entry(Change_station_button_window_frame, font=Body_font, width=30)
        Type_Label_text_box.grid(row=2, column=1, padx=10, pady=8)
        Type_Label_text_box.insert(tk.END, f"{Station_Type}")
        
        OPID_Label = ttk.Label(Change_station_button_window_frame, text=f"OPID: ", font=Body_font)
        OPID_Label.grid(row=3, column=0, sticky=tk.W, padx=10, pady=10)
        OPID_Label_text_box = ttk.Entry(Change_station_button_window_frame, font=Body_font, width=30)
        OPID_Label_text_box.grid(row=3, column=1, padx=10, pady=8)
        OPID_Label_text_box.insert(tk.END, f"{Station_OPID}")

        Change_station_Accept_button = ttk.Button(
            Change_station_button_window_Row_2, text="Accept", command=Change_station_Accept_button_Function)
        Change_station_Accept_button.pack(side=tk.LEFT, padx=10, pady=10)

        Change_station_Cancel_button = ttk.Button(
            Change_station_button_window_Row_2, text="Cancel", command=Change_station_button_window.destroy)
        Change_station_Cancel_button.pack(side=tk.LEFT, padx=10, pady=10)

# -------------------------------------------- Change MES folder function ------------------------------------------------------------------------------------------------------------ #

    def Change_MES_folder_button_Function():
        global MES_folder_Path
        MES_folder_Path = filedialog.askdirectory()
        UI_terminal_Queue.put(f"MES folder: {MES_folder_Path}")
        MES_Linker_Settings_Save()

# -------------------------------------------- GUI -------------------------------------------------------------------------------------------------------------------- #

    Main_screen_Header_frame = ttk.Frame(root)
    Main_screen_Header_frame.pack(side=tk.TOP, fill=tk.X)

    pywinstyles.apply_style(root, "mica")

    Header_frame_Row_1 = ttk.Frame(Main_screen_Header_frame)
    Header_frame_Row_1.pack(side=tk.TOP)

    Header_frame_Row_2 = ttk.Frame(Main_screen_Header_frame)
    Header_frame_Row_2.pack(side=tk.TOP)

    Header_frame_Row_3 = ttk.Frame(Main_screen_Header_frame)
    Header_frame_Row_3.pack(side=tk.TOP)

    Header_frame_Row_4 = ttk.Frame(Main_screen_Header_frame)
    Header_frame_Row_4.pack(side=tk.TOP)

    Device_1_Socket_button = ttk.Button(
        Header_frame_Row_1, text="Device 1 Socket", style="Red.TButton")
    Device_1_Socket_button.pack(
        side=tk.LEFT, padx=10, pady=10, anchor=tk.CENTER)

    MES_Socket_button = ttk.Button(
        Header_frame_Row_1, text="MES Socket", style="Red.TButton")
    MES_Socket_button.pack(
        side=tk.LEFT, padx=10, pady=10, anchor=tk.CENTER)

    UI_terminal = tk.Text(Header_frame_Row_3, state="disabled",
                          font=Terminal_font, width=200)
    UI_terminal.pack(side=tk.BOTTOM, fill=tk.BOTH,
                     expand=True, padx=10, pady=0)
    UI_terminal.configure(state="normal")

    Change_addresses_button = ttk.Button(
        Header_frame_Row_4, text="Change Addresses", command=Change_addresses_button_Function)
    Change_addresses_button.pack(
        side=tk.LEFT, padx=10, pady=10, anchor=tk.CENTER)

    Change_Station_button = ttk.Button(
        Header_frame_Row_4, text="Change Station", command=Change_station_button_Function)
    Change_Station_button.pack(
        side=tk.LEFT, padx=10, pady=10, anchor=tk.CENTER)

    Change_MES_folder_button = ttk.Button(
        Header_frame_Row_4, text="Change MES folder", command=Change_MES_folder_button_Function)
    Change_MES_folder_button.pack(
        side=tk.LEFT, padx=10, pady=10, anchor=tk.CENTER)

# -------------------------------------------- Threads -------------------------------------------------------------------------------------------------------------------- #

    threading.Thread(target=Print_to_terminal).start()

    Start_socket_threads()

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #

    root.mainloop()


if __name__ == '__main__':
    main()
