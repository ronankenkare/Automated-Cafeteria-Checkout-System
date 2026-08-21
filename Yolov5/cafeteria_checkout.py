from utils.general import LOGGER
from picamera2 import Picamera2
from datetime import datetime
from time import sleep
import datetime
import csv
import socket
import subprocess
import shutil
import os

def detection():
	# LOGGER.info("Cafeteria Checkout")
	subprocess.run(["python3", "detect.py"], check=True)
	# LOGGER.info("Program ended")

def start_server(host='192.168.88.191', port=12345):
    LOGGER.info("Scan your ID")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)  
    
    # print(f"Server listening on {host}:{port}")
    conn, addr = server_socket.accept()  
    # print(f"Connection from {addr}")
    
    data = conn.recv(1024) 
    try:
        data = data.decode('utf-8')
        print(f"User ID: {data}")
    except UnicodeDecodeError:
        LOGGER.error("Failed to decode data")
        data = "unknown_data"
		
    conn.close()  # Close the connection
    server_socket.close()
	
    return data

def take_picture(data):
    print("")
    print("Place your tray in view of the camera")
    print("")
    print("Capturing image in...")
    sleep(1)
    print("3...")
    sleep(1)
    print("2...")
    sleep(1)
    print("1...")
    sleep(1)
    picam2 = Picamera2()
    try:
        preview_config = picam2.create_preview_configuration()
        picam2.configure(preview_config)
        picam2.start_preview()
        picam2.start()
        sleep(3)
        time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_data = "".join([c if c.isalnum() else "_" for c in data]).replace(" ", "")
        output_dir = "data/images"
        os.makedirs(output_dir, exist_ok=True)
        img_name = os.path.join(output_dir, f"transaction_{time}_{safe_data}.jpg")
        picam2.capture_file(img_name)
    finally:
        picam2.stop()
    return img_name

def remove_img(img_name):
    if os.path.exists(img_name):
        os.remove(img_name)
        # print("File has been deleted")
    else:
        print("File does not exist")
    if os.path.exists("exp"):
        shutil.rmtree("exp")
        # print("Folder has been deleted")
    else:
        print("Folder does not exist")
	
def get_items_to_search():
    # print("Get_items_search started")
    file_path = "detected_foods.csv"
    with open(file_path, mode='r') as file:
        # print("Checkpoint 1")
        csv_reader = csv.reader(file)
        items = [row[1] for row in csv_reader]
    # print("Get_items_search done")
    return items

def get_item_prices(items_to_search):
    # print("Get_prices started")
    file_path = "admin_data/food_items.csv"
    item_prices = {}
    with open(file_path, mode='r') as file:
        # print("Checkpoint 2")
        csv_reader = csv.reader(file)
        next(csv_reader)  
        for row in csv_reader:
            # print("Checkpoint 3")
            item_name = row[1]  
            price = row[2]  
            if item_name in items_to_search:
                # print("Checkpoint 4")
                item_prices[item_name] = price
    # print("Get_prices search")
    return item_prices


def write_transactions(employee_id, item_prices):
    print("")
    print("--------------------------")
    print("Items purchased:")
    print("--------------------------")
    # print("transactions start")
    file_path = "admin_data/transactions.csv"
    with open(file_path, mode='w', newline='') as file:
        # print("Checkpoint 5")
        csv_writer = csv.writer(file)
        csv_writer.writerow(["Time", "Employee ID", "Item Name", "Price"]) 
        for item, price in item_prices.items():
            print(f"{item} {price}")
            # print("Checkpoint 6")
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            csv_writer.writerow([current_time, employee_id, item, price])
    # print("transactions ended")
    print("")

def clear_detected_items() :
	with open("detected_foods.csv", mode='w', newline='') as file:
		pass

def get_employee_info(employee_id):
    # print("get emp data")
    with open("admin_data/employee_data.csv", mode='r') as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)
        # print("another check")
        for row in csv_reader:
            # print("Checkpoint 0")
            if row[0] == employee_id:
                print(f"ID: {row[0]}")
                print(f"Name: {row[1]}")
                print(f"Department: {row[2]}")
                print(f"Email: {row[3]}")

def clear_terminal():
    os.system('clear')

if __name__ == "__main__":
    clear_terminal()
    print("Welcome to the Cafeteria Checkout System")
    print(" ")
    print("System initializing...")
    sleep(3)
    clear_terminal()
    while True:
        data = start_server()
        get_employee_info(data)
        img_name = take_picture(data)
        detection()
        
        clear_terminal()
        get_employee_info(data)
        
        items_to_search = get_items_to_search()
        item_prices = get_item_prices(items_to_search)
        print(items_to_search)
        write_transactions(data, item_prices)
    
        clear_detected_items()
        remove_img(img_name)
        print("Thank you for your purchase")
        print("")
        print("Resetting system...")
        sleep(10)
        clear_terminal()
