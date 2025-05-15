import requests
import json
from pathlib import Path
import time

# Wait for application to start and create tables
print("Waiting for application to initialize database...")
time.sleep(5)  # Give the app time to create tables


BASE_URL = "http://127.0.0.1:8000"
AUTH = ("rr", "dina")
headers = {"Content-Type": "application/json; charset=utf-8"}

# Load JSON data
current_dir = Path(__file__).resolve().parent
json_file_path = current_dir / "site_data.json"

with open(json_file_path, "r", encoding="utf-8") as file:
    data = json.load(file)

# Loop through each site in the JSON list
for entry in data:
    site_name = entry["site"]["name"]
    robots = entry["site"].get("robots", [])
    site_payload = {"name": site_name}

    # Step 1: Try to create the site
    site_response = requests.post(f"{BASE_URL}/site/", json=site_payload, auth=AUTH)
    try:
        site_data = site_response.json()
    except requests.exceptions.JSONDecodeError:
        print(f"❌ Error decoding JSON from /site/ POST for {site_name}")
        print("Status code:", site_response.status_code)
        print("Response:", site_response.text)
        continue

    if "site_id" in site_data:
        site_id = site_data["site_id"]
        print(f"✅ Created Site: {site_name} (ID: {site_id})")
    elif site_data.get("detail") == "Site already exists":
        print(f"⚠️ Site '{site_name}' already exists!")
        # Get site by name to find its ID
        site_lookup_response = requests.get(f"{BASE_URL}/site/{site_name}", auth=AUTH)
        if site_lookup_response.status_code != 200:
            print(f"❌ Cannot find existing site '{site_name}'")
            continue
            
        # Since site endpoint returns HTML, we need to use a different approach
        # Get all robots and find those belonging to this site
        robots_response = requests.get(f"{BASE_URL}/robots", auth=AUTH)
        try:
            all_robots = robots_response.json()
            # Find any robot belonging to this site to get the site_id
            for robot in all_robots:
                # Check if robot name matches any in our site_data
                for our_robot in robots:
                    if robot["name"] == our_robot["name"]:
                        site_id = robot["site_id"]
                        print(f"✅ Found existing Site ID: {site_id}")
                        break
                if 'site_id' in locals():
                    break
        except:
            print("❌ Could not retrieve robots to find site ID")
            continue
            
        if 'site_id' not in locals():
            print("❌ Could not determine site ID, skipping")
            continue
    else:
        print(f"❌ Unexpected API response for site '{site_name}':", site_data)
        continue

    # Step 2: Add robots and hardware
    if robots:
        for robot in robots:
            robot_payload = {"name": robot["name"], "site_id": site_id}
            robot_response = requests.post(f"{BASE_URL}/robot/", json=robot_payload, auth=AUTH)

            try:
                robot_data = robot_response.json()
            except requests.exceptions.JSONDecodeError:
                print(f"❌ Failed to create Robot '{robot['name']}':", robot_response.status_code, robot_response.text)
                continue

            robot_id = robot_data.get("robot_id")
            if not robot_id:
                print(f"❌ Robot creation failed: {robot_data}")
                continue

            print(f"✅ Added Robot: {robot['name']} (ID: {robot_id})")

            for hw in robot.get("hardware", []):
                # Only send fields that the API accepts
                hardware_payload = {
                    "name": hw["name"],
                    "type": hw["type"],
                    "robot_id": robot_id,
                    "status": hw.get("status", "Active"),
                    "replacement_count": hw.get("replacement_count", 0),
                    "repair_count": hw.get("repair_count", 0),
                    "comments": hw.get("comments", "")
                }
                hardware_response = requests.post(f"{BASE_URL}/hardware/", json=hardware_payload, auth=AUTH, headers=headers)
                try:
                    hardware_data = hardware_response.json()
                    print(f"    ✅ Added Hardware: {hw['name']}")
                    
                    # If hardware has additional fields, update them separately
                    if "hardware_id" in hardware_data:
                        hardware_id = hardware_data["hardware_id"]
                        update_payload = {
                            "hardware_id": hardware_id,
                            "status": hw.get("status", "Active"),
                            "replacement_count": hw.get("replacement_count", 0),
                            "repair_count": hw.get("repair_count", 0),
                            "comments": hw.get("comments", "")
                        }
                        update_response = requests.post(f"{BASE_URL}/update_hardware", json=update_payload, auth=AUTH)
                        if update_response.status_code == 200:
                            print(f"    ✅ Updated Hardware details for {hw['name']}")
                        else:
                            print(f"    ⚠️ Could not update hardware details: {update_response.text}")
                except requests.exceptions.JSONDecodeError:
                    print(f"    ❌ Failed to add hardware '{hw['name']}':", hardware_response.status_code, hardware_response.text)
    else:
        print(f"⚠️ No robots found for site '{site_name}'.")

print("✅ Database population completed!")

