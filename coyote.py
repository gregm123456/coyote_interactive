import config

def main():
    print(f"Button to listen to person is set to: {config.BUTTON_LISTEN_TO_PERSON}")
    print(f"Button to listen to television is set to: {config.BUTTON_LISTEN_TO_TELEVISION}")
    print(f"Switch to wake/sleep is set to: {config.SWITCH_WAKE_SLEEP}")
    
    print(f"API Key for local development is set to: {config.API_KEY}")

if __name__ == "__main__":
    main()
