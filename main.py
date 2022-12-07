import time

import requests
import mysql.connector
from os import getenv
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = getenv("API_TOKEN")
TEAM_ID = getenv("TEAM_ID")
PROJECT_ID = getenv("PROJECT_ID")
DATABASE = {
    "database": getenv("DATABASE_DB"),
    "user": getenv("DATABASE_USER"),
    "host": getenv("DATABASE_HOST"),
    "password": getenv("DATABASE_PASSWORD")
}


def get_current_time():
    return time.strftime("%Y-%m-%d %H:%M:%S")

def log(message: str):
    print(f"{get_current_time()} {message}")

def request_insights() -> dict:
    response = requests.get(f'https://vercel.com/api/web/insights/realtime?teamId={TEAM_ID}&projectId={PROJECT_ID}',
                            headers={
                                "Authorization": f"Bearer {API_TOKEN}"
                            })
    if response.status_code == 200:
        return response.json()
    log(f"Failed to get insights: {response.status_code} {response.text}")
    return {}


def get_current_devices() -> int:
    data = request_insights()
    if 'devices' in data:
        return data['devices']
    return 0


def connect_to_db():
    return mysql.connector.connect(
        host=f"{DATABASE['host']}",
        user=DATABASE['user'],
        password=DATABASE['password'],
        database=DATABASE['database']
    )


def create_tables():
    db = connect_to_db()
    cursor = db.cursor()
    cursor.execute(
        "CREATE TABLE `website` (`id` INT NOT NULL AUTO_INCREMENT, `devices` INT NOT NULL, `timestamp` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (`id`));")
    db.commit()
    db.close()


def main():
    log("Starting script")
    while True:
        devices = get_current_devices()

        db = connect_to_db()
        cursor = db.cursor()
        cursor.execute(f"INSERT INTO `website` (`devices`) VALUES ('{devices}')")
        db.commit()
        log(f"Inserted {devices} devices into database")

        db.close()

        # sleep for 30 seconds
        time.sleep(30)


if __name__ == '__main__':
    main()
