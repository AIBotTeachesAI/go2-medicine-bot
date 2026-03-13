# go2_controller.py
import os, time
from dotenv import load_dotenv

load_dotenv()

MOCK_MODE = True  # flip to False when on robot

cw = None
robot = None

POSITIONS = {
    "claritin": [1.5, 0.0, 0.0],
    "dayquil":  [-1.5, 0.0, 0.0]
}

def init_robot():
    global cw, robot
    if MOCK_MODE:
        print("[MOCK] Robot init skipped"); return
    from cyberwave import Cyberwave
    cw = Cyberwave(api_key=os.getenv("CYBERWAVE_API_KEY"), source_type="tele")
    robot = cw.twin("unitree/go2")  # confirm registry_id with organizers
    print("Robot connected ✅")

def navigate_to(medicine: str):
    if MOCK_MODE:
        print(f"[MOCK] Walking to {medicine} station"); time.sleep(1); return
    robot.edit_position(POSITIONS[medicine])
    time.sleep(4)  # wait for robot to arrive

def navigate_home():
    if MOCK_MODE:
        print("[MOCK] Returning home"); time.sleep(1); return
    robot.edit_position([0.0, 0.0, 0.0])
    time.sleep(4)
    
def navigate_to(medicine: str):
    if MOCK_MODE:
        print(f"[MOCK] Walking to {medicine} station"); time.sleep(1); return
    pos = POSITIONS[medicine]
    robot.navigation.goto(pos)
    time.sleep(4)

def navigate_home():
    if MOCK_MODE:
        print("[MOCK] Returning home"); time.sleep(1); return
    robot.navigation.goto([0.0, 0.0, 0.0])
    time.sleep(4)
    

def capture_image(medicine: str) -> str:
    if MOCK_MODE:
        return f"test_images/{medicine}.jpg"
    import cv2
    frame = robot.capture_frame("numpy")
    path = f"/tmp/{medicine}_live.jpg"
    cv2.imwrite(path, frame)
    return path

def celebrate():
    if MOCK_MODE:
        print("[MOCK] Robot doing celebration dance"); time.sleep(2); return
    try:
        robot.motion.asset.pose("say hello")
        robot._connect_to_mqtt_if_not_connected()
        cw.mqtt.publish(f"twins/{robot.uuid}/commands/sport", {"action": "dance"})
    except Exception as e:
        print(f"[celebrate] {e}")
