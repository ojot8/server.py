import socket
import json

# Define the host and port for the server to listen on, the maximum amount of data to receive at once, the maximum number of queued connections, and a list of fun runs
host = '127.0.0.1'
port = 9900
data_payload = 2048
backlog = 5

fun_runs = [
    {"Area": "Covuni", "Run Name": "Engineering Marathon", "Distance": "7 KM", "Time": "Fast", "Price Per Runner": 10, "Run Number": "001", "Available Spaces": 50},
    {"Area": "Coventry", "Run Name": "Uni Fun Run", "Distance": "10 KM", "Time": "Slow", "Price Per Runner": 5, "Run Number": "002", "Available Spaces": 50},
    {"Area": "WestMidlands", "Run Name": "Combe Abbey Swan Challenge", "Distance": "10 KM", "Time": "Medium", "Price Per Runner": 20, "Run Number": "003", "Available Spaces": 50},
    {"Area": "NorthEast", "Run Name": "Pier to Pier", "Distance": "22 KM", "Time": "Fast", "Price Per Runner": 25, "Run Number": "004", "Available Spaces": 50},
    {"Area": "York", "Run Name": "York 10KM", "Distance": "5 KM", "Time": "Very Fast", "Price Per Runner": 30, "Run Number": "005", "Available Spaces": 50},

]

waiting_list = []

# This function recommends runs based on multiple sets of criteria
def recommend_runs(*args):
    recommended_runs = []
    for i in range(0, len(args), 4):
        area, min_length, max_length, time = args[i:i+4]
        min_length = int(min_length)
        max_length = int(max_length)

        runs = [run for run in fun_runs if run["Area"] == area and min_length <= int(run["Distance"].split(" ")[0]) <= max_length and run["Time"] == time]
        recommended_runs.extend(runs)

    return recommended_runs


# This function registers runners for a run and handles errors, waiting list, discounts, and restrictions on the number of runners
def register_runners(secretary_name, run_number, quantity):
    max_runner = 25

    if quantity > max_runner:
        return "Cannot register more than {} runners at once.".format(max_runner)

    run = next((run for run in fun_runs if run["Run Number"] == run_number), None)

    if run is None:
        return "Run not found."

    if run["Available Spaces"] >= quantity:
        run["Available Spaces"] -= quantity
        total_fee = quantity * run["Price Per Runner"]
        if total_fee > 50:
            total_fee *= 0.9 
        return "{} runners registered for {} by {}. Total fee: GBP{:.2f}".format(quantity, run['Run Name'], secretary_name, total_fee)
    else:
        registered = run["Available Spaces"]
        run["Available Spaces"] = 0
        waiting = quantity - registered
        waiting_list.append({"Secretary Name": secretary_name, "Run Number": run_number, "Quantity": waiting})
        return "{} runners registered for {} by {}. {} runners added to the waiting list.".format(registered, run['Run Name'], secretary_name, waiting)

# This function handles the server-side operations
def echo_server(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('127.0.0.1', 9900))
    sock.listen(backlog)

    while True:
        print("Waiting to receive message from client")
        client, address = sock.accept()
        data = client.recv(data_payload)
        print("Message Received from client: ",data)

        if data:
            data = data.decode("utf-8").split(" ")
            command = data[0]

            if command == "recommend":
                recommended_runs = recommend_runs(*data[1:])
                response = json.dumps(recommended_runs)
            elif command == "register":
                secretary_name, run_number, quantity = data[1:]
                response = register_runners(secretary_name, run_number, int(quantity))
            else:
                response = "Invalid command."

            client.send(response.encode("utf-8"))
            print("sent {} bytes back to {}".format(response, address))

        client.close()

# If this script is run directly, start the server
if __name__ == '__main__':
    echo_server(9900)
