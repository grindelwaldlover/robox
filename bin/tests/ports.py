import serial.tools.list_ports

with open("ports_log.txt", "w", encoding="utf-8") as file:
    for port in serial.tools.list_ports.comports():
        line = f"{port.device}, VID: {port.vid}, PID: {port.pid}, Description: {port.description}"
        print(line)
        file.write(line + "\n")

print("Информация о портах сохранена в ports_log.txt")
