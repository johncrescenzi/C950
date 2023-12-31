# Author: John Crescenzi
# Student ID: 010429467
# Title: NHP3 — NHP3 TASK 1: WGUPS ROUTING PROGRAM PLANNING 

# Import necessary modules and classes
import csv
import datetime
import Truck
from builtins import ValueError

from CreateHashTable import CreateHashMap
from Package import Package

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Read the distance information file and store it in a list
with open("CSV/Distance_File.csv") as csvfile:
    CSV_Distance = csv.reader(csvfile)
    CSV_Distance = list(CSV_Distance)

# Read the address information file and store it in a list
with open("CSV/Address_File.csv") as csvfile1:
    CSV_Address = csv.reader(csvfile1)
    CSV_Address = list(CSV_Address)

# Read the package information file and store it in a list
with open("CSV/Package_File.csv") as csvfile2:
    CSV_Package = csv.reader(csvfile2)
    CSV_Package = list(CSV_Package)

# Create package objects from the CSV package file
# Load package objects into the hash table: package_hash_table
def load_package_data(filename, package_hash_table):
    with open(filename) as package_info:
        package_data = csv.reader(package_info)
        for package in package_data:
            pID = int(package[0])
            pAddress = package[1]
            pCity = package[2]
            pState = package[3]
            pZipcode = package[4]
            pDeadline_time = package[5]
            pWeight = package[6]
            pStatus = "At Hub"

            # Create Package object
            p = Package(pID, pAddress, pCity, pState, pZipcode, pDeadline_time,
                        pWeight, pStatus)

            # Insert data into hash table
            package_hash_table.insert(pID, p)

# Method for finding distance between two addresses
def distance_in_between(x_value, y_value):
    distance = CSV_Distance[x_value][y_value]
    if distance == '':
        distance = CSV_Distance[y_value][x_value]

    return float(distance)

# Method to get address number from string literal of address
def extract_address(address):
    for row in CSV_Address:
        if address in row[2]:
            return int(row[0])

# Create truck objects
truck1 = Truck.Truck(16, 18, None,
                     [1, 13, 14, 15, 16, 20, 29, 30, 31, 34, 37, 40], 0.0,
                     "4001 South 700 East", datetime.timedelta(hours=8))

truck2 = Truck.Truck(
    16, 18, None,
    [3, 6, 9, 12, 17, 18, 19, 21, 22, 23, 24, 27, 35, 36, 38, 39], 0.0,
    "4001 South 700 East", datetime.timedelta(hours=10, minutes=20))

truck3 = Truck.Truck(16, 18, None,
                     [2, 4, 5, 6, 7, 8, 10, 11, 25, 26, 28, 32, 33], 0.0,
                     "4001 South 700 East",
                     datetime.timedelta(hours=9, minutes=5))

# Create hash table
package_hash_table = CreateHashMap()

# Load packages into hash table
load_package_data("CSV/Package_File.csv", package_hash_table)

# Method for ordering packages on a given truck using the nearest neighbor algorithm
# This method also calculates the distance a given truck drives once the packages are sorted
def delivering_packages(truck):
    # Place all packages into an array of not delivered
    not_delivered = []
    for packageID in truck.packages:
        package = package_hash_table.lookup(packageID)
        not_delivered.append(package)

    # Clear the package list of a given truck so the packages can be placed back into the truck in the order
    # of the nearest neighbor
    truck.packages.clear()

    # Cycle through the list of not_delivered until none remain in the list
    # Adds the nearest package into the truck.packages list one by one
    while len(not_delivered) > 0:
        next_address = 2000
        next_package = None
        for package in not_delivered:
            if distance_in_between(extract_address(truck.address),
                                   extract_address(package.address)) <= next_address:
                next_address = distance_in_between(extract_address(truck.address),
                                                   extract_address(package.address))
                next_package = package

        # Adds next closest package to the truck package list
        truck.packages.append(next_package.ID)
        # Removes the same package from the not_delivered list
        not_delivered.remove(next_package)
        # Takes the mileage driven to this packaged into the truck.mileage attribute
        truck.mileage += next_address
        # Updates truck's current address attribute to the package it drove to
        truck.address = next_package.address
        # Updates the time it took for the truck to drive to the nearest package
        truck.time += datetime.timedelta(hours=next_address / 18)
        next_package.delivery_time = truck.time
        next_package.departure_time = truck.depart_time

# Put the trucks through the loading process
delivering_packages(truck1)
delivering_packages(truck2)
# Ensure that truck 3 does not leave until either of the first two trucks is finished delivering their packages
truck3.depart_time = min(truck1.time, truck2.time)
delivering_packages(truck3)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_status', methods=['POST'])
def get_status():
    try:
        user_time = request.form['userTime']
        (h, m, s) = user_time.split(":")
        convert_timedelta = datetime.timedelta(hours=int(h),
                                               minutes=int(m),
                                               seconds=int(s))

        second_input = request.form['type']

        if second_input == "solo":
            solo_input = request.form['packageID']
            try:
                package = package_hash_table.lookup(int(solo_input))
                package.update_status(convert_timedelta)
                total_distance = truck1.mileage + truck2.mileage + truck3.mileage
                return jsonify(result=[{
                    "ID": package.ID,
                    "address": package.address,
                    "departureTime": str(package.departure_time),
                    "deliveryTime": str(package.delivery_time),
                    "status": package.status
                }],
                               totalDistance=total_distance)
            except ValueError:
                return jsonify(error="Entry invalid. Closing program.")
        elif second_input == "all":
            try:
                result = []
                for packageID in range(1, 41):
                    package = package_hash_table.lookup(packageID)
                    package.update_status(convert_timedelta)
                    # Append package information to the result list
                    result.append({
                        "ID": package.ID,
                        "address": package.address,
                        "departureTime": str(package.departure_time),
                        "deliveryTime": str(package.delivery_time),
                        "status": package.status
                    })
                # Calculate and return the total distance
                total_distance = truck1.mileage + truck2.mileage + truck3.mileage
                return jsonify(result=result, totalDistance=total_distance)
            except ValueError:
                return jsonify(error="Entry invalid. Closing program.")
        else:
            return jsonify(error="Invalid type. Closing program.")
    except ValueError:
        return jsonify(error="Entry invalid. Closing program.")

app.run(host='0.0.0.0', port=81)