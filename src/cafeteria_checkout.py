"""Automated cafeteria checkout -- main entry point.

Runs the full checkout loop on the Raspberry Pi: wait for an RFID scan over the
network, photograph the tray, run food_detector.py over the photo, price the
detected items against data/admin/food_items.csv, and append the sale to
data/admin/transactions.csv.

    python3 src/cafeteria_checkout.py
"""

import csv
import datetime
import os
import shutil
import socket
import subprocess
import sys
from pathlib import Path
from time import sleep

# Make sibling modules importable when this file is run directly as a script.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import config  # noqa: E402  -- also puts vendor/yolov5 on sys.path for the import below

from picamera2 import Picamera2  # noqa: E402  -- Raspberry Pi only
from utils.general import LOGGER  # noqa: E402  -- from vendor/yolov5


def detection(img_name):
    # LOGGER.info("Cafeteria Checkout")
    # Scope the detector to this one photo. Pointed at the whole capture
    # directory it would re-bill any image left behind by an earlier tray.
    subprocess.run(
        [sys.executable, str(config.SRC_DIR / "food_detector.py"), "--source", str(img_name)],
        check=True,
    )
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
        img_name = os.path.join(config.CAPTURE_DIR, f"transaction_{time}_{safe_data}.jpg")
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
    # YOLOv5 increments its output directory every run (exp, exp2, exp3, ...),
    # so clear the whole tree instead of guessing the name this run landed on.
    if os.path.exists(config.RUNS_DIR):
        shutil.rmtree(config.RUNS_DIR)
        # print("Folder has been deleted")
    else:
        print("Folder does not exist")


def get_items_to_search():
    # print("Get_items_search started")
    with open(config.DETECTED_FOODS_CSV, mode='r') as file:
        # print("Checkpoint 1")
        csv_reader = csv.reader(file)
        items = [row[1] for row in csv_reader]
    # print("Get_items_search done")
    return items


def get_item_prices(items_to_search):
    # print("Get_prices started")
    item_prices = {}
    with open(config.FOOD_ITEMS_CSV, mode='r') as file:
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
    # Append -- the ledger has to outlive the transaction. The header is only
    # written when the file is new or empty.
    needs_header = not os.path.exists(config.TRANSACTIONS_CSV) or os.path.getsize(config.TRANSACTIONS_CSV) == 0
    with open(config.TRANSACTIONS_CSV, mode='a', newline='') as file:
        # print("Checkpoint 5")
        csv_writer = csv.writer(file)
        if needs_header:
            csv_writer.writerow(["Time", "Employee ID", "Item Name", "Price"])
        for item, price in item_prices.items():
            print(f"{item} {price}")
            # print("Checkpoint 6")
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            csv_writer.writerow([current_time, employee_id, item, price])
    # print("transactions ended")
    print("")


def clear_detected_items():
    with open(config.DETECTED_FOODS_CSV, mode='w', newline='') as file:
        pass


def get_employee_info(employee_id):
    # print("get emp data")
    with open(config.EMPLOYEE_DATA_CSV, mode='r') as file:
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
        detection(img_name)

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
