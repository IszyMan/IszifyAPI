from flask import Blueprint, request
import cloudinary.uploader
import cloudinary.api
import cloudinary_config
from utils import convert_binary, generate_signature, return_response
from http_status import HttpStatus
from status_res import StatusRes
import time
import os
from logger import logger

cloudnary = Blueprint("cloudnary", __name__)

ACCOUNT_PREFIX = "cloudinary"


@cloudnary.route(f"/{ACCOUNT_PREFIX}/manage-file", methods=["POST"])
def manage_file():
    try:
        data = request.get_json()
        file = data.get("file", None)
        public_id = data.get("public_id", None)
        action = data.get("action", None)
        folder = data.get("folder", None)

        logger.info(f"data: {data}")

        cloud_name = (os.environ.get("CLOUD_NAME"),)
        api_key = (os.environ.get("API_KEY"),)
        api_secret = (os.environ.get("API_SECRET"),)

        cloud_name = str(cloud_name[0]) if isinstance(cloud_name, tuple) else cloud_name
        api_key = str(api_key[0]) if isinstance(api_key, tuple) else api_key
        api_secret = str(api_secret[0]) if isinstance(api_secret, tuple) else api_secret

        if not action:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Action is required",
            )

        if action == "upload" and not file:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="File is required",
            )

        if not public_id:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Public ID is required",
            )

        file = convert_binary(file) if action == "upload" else None

        params_to_sign = {
            "public_id": public_id,
            "timestamp": int(time.time()),
        }
        signature = generate_signature(params_to_sign, api_secret)

        params_to_sign["signature"] = signature

        params_to_sign["folder"] = folder if folder else None

        if action == "upload":
            result = cloudinary.uploader.upload(file, **params_to_sign)
            logger.info(f"result: {result}")
            file_url = result["secure_url"]

            return return_response(
                HttpStatus.OK,
                status=StatusRes.SUCCESS,
                message="File uploaded successfully",
                data={
                    "file_url": file_url,
                    "public_id": public_id,
                    "signature": signature,
                },
            )
        elif action == "destroy":
            params_to_sign["public_id"] = (
                f"{folder}/{public_id}" if folder else public_id
            )
            result = cloudinary.uploader.destroy(**params_to_sign)
            logger.info(f"result: {result}")

            return (
                return_response(
                    HttpStatus.OK,
                    status=StatusRes.SUCCESS,
                    message="File deleted successfully",
                )
                if result["result"] == "ok"
                else return_response(
                    HttpStatus.BAD_REQUEST,
                    status=StatusRes.FAILED,
                    message="File not found",
                )
            )
        else:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Invalid action",
            )

    except KeyError as e:
        logger.error(f"{e}: error@cloudnary/manage_file")
        return return_response(
            HttpStatus.BAD_REQUEST,
            status=StatusRes.FAILED,
            message="All fields are required",
        )
    except Exception as e:
        logger.exception("traceback@cloudnary/manage_file")
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network error",
        )
