import asyncio
from octoprint_rest_api import OctoPrint


async def main():
    OP = OctoPrint("192.168.1.212", 5000)
    await OP.get_api_key("test")
    print("Got: %s", OP.api_key)
    print(OP.get_printer_status())


if __name__ == "__main__":
    asyncio.run(main())
