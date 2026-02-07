import os
from datetime import datetime

import requests
from fastapi import Depends
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from config.logger import log
from config.settings import settings
from db.session import get_db
from domains.auth.models import User


class IntruderDetectionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, db: Session = Depends(get_db)):
        super().__init__(app)
        self.db = db

    @staticmethod
    def intruder_info(request: Request):
        # intruder_list = []
        client_ip = request.client.host
        headers = request.headers
        user_agent = headers.get("User-Agent")
        mac_address = headers.get("X-MAC-Address")  # Custom header for MAC Address
        location = requests.get(f"https://ipinfo.io/{client_ip}/geo").json()

        intruder_info = {
            "ip_address": client_ip,
            "mac_address": mac_address,
            "user_agent": user_agent,
            "location": location,
        }
        log.info("intruder info dict: ", intruder_info)
        settings.intruder_list.append(intruder_info)
        log.info(f"Intruder detected: {intruder_info}")

        return intruder_info

    @staticmethod
    def log_intruder_info(ip_addr: str, mac_addr: str, user_agent: str, location: str):
        # Get current date to create or append to the log file
        current_date = datetime.now().strftime('%Y-%m-%d')
        log_file_name = f"intruder_log_{current_date}.txt"
        log_directory = "security/logs/"

        os.makedirs(log_directory, exist_ok=True)

        # Check if the log file exists
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)

        log_filepath = os.path.join(log_directory, log_file_name)

        # Create log entry
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"{ip_addr} | {mac_addr} | {user_agent} | {location} | {timestamp}"

        # Check if the log file already exists
        if os.path.exists(log_filepath):
            with open(log_filepath, 'a') as file:
                file.write("================================================================================\n")
                file.write(log_entry + "\n")
        else:
            with open(log_file_name, 'w') as file:
                file.write("IP Addr | Mac Addr | User Agent | location | Timestamp\n")
                file.write(log_entry + "\n")

        return log_filepath

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)  # Await the async function
        if response.status_code == 429:
            username = request.headers.get("X-Username")
            log.info("\nusername in middleware: ", username)
            if username:
                user = self.db.query(User).filter(User.username == username).first()
                if user:
                    log.info("user in middleware: ", user)
                    user.lock_account(lock_time_minutes=10)
                    self.db.commit()

        return response

