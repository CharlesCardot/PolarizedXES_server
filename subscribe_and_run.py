import json
import subprocess
import re
import os

def extract_all(message):
    # Match tag
    tag_match = re.search(r"🔖 Tag: (\w+)", message)
    tag = tag_match.group(1) if tag_match else None

    # Match oxidation state info
    oxidation_match = re.search(r"⚙️ Oxidation states: (.+)", message)
    oxidation = oxidation_match.group(1).strip() if oxidation_match else "guess"

    # Match filename (optional, in case you want to save it)
    filename_match = re.search(r"📦 File received: (.+)", message)
    filename = filename_match.group(1) if filename_match else "received.cif"

    # Find start of CIF content
    cif_start = message.find("\n\n") + 2
    cif_content = message[cif_start:]

    return tag, oxidation, filename, cif_content


def handle_message(json_line):
    try:
        data = json.loads(json_line)
        message = data.get("message", "")
        tag, oxidation, filename, cif_content = extract_all(message)

        if not tag or not cif_content:
            print("❌ Could not extract tag or CIF data.")
            return

        print(f"✅ Received tag: {tag}")

        # Create folder name using base name and tag
        base_filename = os.path.splitext(filename)[0]
        folder_name = f"{base_filename}_{tag}"
        os.makedirs(folder_name, exist_ok=True)

        # Write CIF file into that folder
        full_path = os.path.join(folder_name, filename)
        print(f"📄 Writing to: {full_path}")
        with open(full_path, "w") as f:
            f.write(cif_content)

        # Parse oxidation string into dictionary
        if oxidation != "guess":
            oxidation_dict = {}
            for pair in oxidation.split(","):
                element, value = pair.strip().split(":")
                oxidation_dict[element.strip()] = int(value)
            
            # Save to JSON
            full_path = os.path.join(folder_name, "oxidation_states.json")
            with open(full_path, "w") as f:
                json.dump(oxidation_dict, f, indent=2)

        # Save full ntfy object
        with open(os.path.join(folder_name, "ntfy_object.json"), "w") as f:
            json.dump(data, f, indent=2)    

        # 🔁 Submit job to task spooler with full path and tag
        job_command = f"./run_prediction.sh {full_path} {tag}"
        print(f"🚀 Submitting job to Task Spooler: {job_command}")
        subprocess.run(["tsp", "bash", "-c", job_command], check=True)

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("📡 Listening for messages...")
    process = subprocess.Popen(
        ["ntfy", "subscribe", "polarized-xes-upload"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    try:
        for line in process.stdout:
            if line.strip():
                handle_message(line.strip())
    except KeyboardInterrupt:
        print("👋 Exiting.")
    finally:
        process.terminate()

