# main.py
from voice_listener import listen, speak
from go2_controller import init_robot, navigate_to, navigate_home, capture_image
from vlm_verifier import verify_medicine

def run():
    print("🏥 Hospital Medicine Bot starting...")
    init_robot()
    speak("Hello, I am your medicine assistant. Please tell me what medicine you need.")

    medicine = None
    while not medicine:
        medicine = listen()
        if not medicine:
            speak("Sorry, I didn't catch that. Please say Claritin or DayQuil.")

    speak(f"Got it. Fetching {medicine} for you now.")
    print(f"🎯 Target medicine: {medicine}")

    navigate_to(medicine)

    image_path = capture_image(medicine)
    print(f"📸 Image captured: {image_path}")

    verified = verify_medicine(image_path, medicine)

    if verified:
        navigate_home()
        speak(f"I have verified and retrieved your {medicine}. Here you go!")
        print("✅ Demo complete!")
    else:
        speak(f"Warning: I could not verify the medicine label. Please check manually.")
        navigate_home()
        print("⚠️ Verification failed.")

if __name__ == "__main__":
    run()
