from air_pong_controller import PongController


def main():
    """begins and runs the game"""
    controller = PongController()
    while True:
        # print("running while")
        controller.get_hand()
        print(f"latest controller key is {controller.latest_key}")


if __name__ == "__main__":
    main()
