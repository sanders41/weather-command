from dotenv import load_dotenv

from weather_command._builder import show_current_weather_by_city

load_dotenv()


def main() -> None:
    show_current_weather_by_city("Greensboro", units="imperial")


if __name__ == "__main__":
    main()
