import os
import logging
from typing import Dict, Optional, Any
from app.services.directus import make_directus_request


logger = logging.getLogger(__name__)

def check_checkin_status(user_id: int) -> str:

    try:

        user_response = make_directus_request(
            endpoint="/items/telegram_user_links",
            params={
                "filter": {
                    "telegram_id": {"_eq": user_id}
                },
                "fields": ["user_id"]
            }
        )


        if not user_response or "data" not in user_response or not user_response["data"]:
            return "❌ Ваш Telegram аккаунт не привязан к системе. Пожалуйста, привяжите аккаунт."


        system_user_id = user_response["data"][0]["user_id"]


        occupation_response = make_directus_request(
            endpoint="/items/student_accommodation_room_occupations",
            params={
                "filter": {
                    "user_id": {"_eq": system_user_id}
                },
                "fields": ["room_id"]
            }
        )


        if not occupation_response or "data" not in occupation_response or not occupation_response["data"]:
            return "❌ Вы не заселены. Пожалуйста, обратитесь в администрацию общежития."


        room_id = occupation_response["data"][0]["room_id"]


        room_response = make_directus_request(
            endpoint=f"/items/student_accommodation_rooms/{room_id}",
            params={
                "fields": ["room_number", "max_capacity", "apartments_blocks_id", "floor_id"]
            }
        )

        if not room_response or "data" not in room_response:
            return "⚠️ Не удалось получить информацию о комнате. Пожалуйста, попробуйте позже."

        room_data = room_response["data"]
        room_number = room_data.get("room_number", "Неизвестно")
        max_capacity = room_data.get("max_capacity", "Неизвестно")
        apartments_blocks_id = room_data.get("apartments_blocks_id")
        floor_id = room_data.get("floor_id")


        floor_number = "Неизвестно"
        accommodation_id = None
        accommodation_address_id = None
        apartment_number = None


        if apartments_blocks_id:
            apartment_response = make_directus_request(
                endpoint=f"/items/student_accommodation_apartments_blocks/{apartments_blocks_id}",
                params={
                    "fields": ["number", "floor_id"]
                }
            )

            if apartment_response and "data" in apartment_response:
                apartment_data = apartment_response["data"]
                apartment_number = apartment_data.get("number", "Неизвестно")
                floor_id = apartment_data.get("floor_id")


        if floor_id:
            floor_response = make_directus_request(
                endpoint=f"/items/student_accommodation_floors/{floor_id}",
                params={
                    "fields": ["floor_number", "accommodation_id","accommodation_address"]
                }
            )

            if floor_response and "data" in floor_response:
                floor_data = floor_response["data"]
                floor_number = floor_data.get("floor_number", "Неизвестно")
                accommodation_id = floor_data.get("accommodation_id")
                accommodation_address_id = floor_data.get("accommodation_address")


        accommodation_name = "Неизвестно"
        accommodation_type = "Неизвестно"

        if accommodation_id:
            accommodation_response = make_directus_request(
                endpoint=f"/items/student_accommodation/{accommodation_id}",
                params={
                    "fields": ["name", "type"]
                }
            )

            if accommodation_response and "data" in accommodation_response:
                accommodation_data = accommodation_response["data"]
                accommodation_name = accommodation_data.get("name", "Неизвестно")
                accommodation_type_id = accommodation_data.get("type")


                if accommodation_type_id:
                    type_response = make_directus_request(
                        endpoint=f"/items/student_accommodation_type/{accommodation_type_id}",
                        params={
                            "fields": ["name"]
                        }
                    )

                    if type_response and "data" in type_response:
                        accommodation_type = type_response["data"].get("name", "Неизвестно")


        address = "Неизвестно"

        if accommodation_address_id:
            address_response = make_directus_request(
                endpoint=f"/items/student_accommodation_addresses/{accommodation_address_id}",
                params={
                    "fields": ["city", "street", "building_number", "house_structure", "corpus"]
                }
            )

            if address_response and "data" in address_response:
                address_data = address_response["data"]
                city = address_data.get("city", "")
                street = address_data.get("street", "")
                building_number = address_data.get("building_number", "")
                house_structure = address_data.get("house_structure", "")
                corpus = address_data.get("corpus", "")


                address_parts = []
                if city:
                    address_parts.append(city)
                if street:
                    address_parts.append(street)
                if building_number:
                    address_parts.append(f"д. {building_number}")
                if house_structure:
                    address_parts.append(f"стр. {house_structure}")
                if corpus:
                    address_parts.append(f"корп. {corpus}")

                address = ", ".join(address_parts) if address_parts else "Неизвестно"


        message = f"✅ Вы заселены!\n\n"
        message += f"Общежитие: {accommodation_name}\n"
        message += f"Тип: {accommodation_type}\n"
        message += f"Адрес: {address}\n"
        message += f"Этаж: {floor_number}\n"

        if apartment_number:
            message += f"Квартира/Блок: {apartment_number}\n"

        message += f"Комната: {room_number}\n"
        message += f"Вместимость комнаты: {max_capacity} чел."

        return message

    except Exception as e:
        logger.error(f"Error checking check-in status for user {user_id}: {e}")
        return "⚠️ Не удалось получить информацию о заселении. Пожалуйста, попробуйте позже."

def check_relocation_status(user_id: int) -> str:

    try:

        user_response = make_directus_request(
            endpoint="/items/telegram_user_links",
            params={
                "filter": {
                    "telegram_id": {"_eq": user_id}
                },
                "fields": ["user_id"]
            }
        )


        if not user_response or "data" not in user_response or not user_response["data"]:
            return "❌ Ваш Telegram аккаунт не привязан к системе. Пожалуйста, привяжите аккаунт."


        system_user_id = user_response["data"][0]["user_id"]


        application_response = make_directus_request(
            endpoint="/items/student_relocation_applications",
            params={
                "filter": {
                    "user_created": {"_eq": system_user_id}
                },
                "fields": [
                    "id", 
                    "status", 
                    "student_relocation_id", 
                    "student_accommodation_id_from", 
                    "student_accommodation_from_address_id", 
                    "room_number", 
                    "apartment_number", 
                    "floor"
                ],
                "sort": ["-date_created"],
            }
        )


        if not application_response or "data" not in application_response or not application_response["data"]:
            return "ℹ️ У вас нет активных заявок на переселение. Вы можете создать заявку в личном кабинете."


        application = application_response["data"][0]
        application_id = application.get("id")
        application_status = application.get("status", "В обработке")


        status_map = {
            "created": "Создана заявка на переселение",
            "rejected": "Отклонена заявка",
            "ended": "Заявка на переселение закончена",
            "canceled": "Заявка отменена пользователем"
        }

        status_text = status_map.get(application_status, application_status)


        relocation_name = "Неизвестно"
        if application.get("student_relocation_id"):
            relocation_response = make_directus_request(
                endpoint=f"/items/student_relocation/{application['student_relocation_id']}",
                params={
                    "fields": ["name"]
                }
            )

            if relocation_response and "data" in relocation_response:
                relocation_name = relocation_response["data"].get("name", "Неизвестно")


        matches_response = make_directus_request(
            endpoint="/items/student_relocation_applications_match",
            params={
                "filter": {
                    "relocation_applications_id_to": {"_eq": application_id}
                },
                "fields": ["id", "status"]
            }
        )

        matches_count = 0
        if matches_response and "data" in matches_response:
            matches_count = len(matches_response["data"])


        approved_match = None
        if matches_response and "data" in matches_response:
            for match in matches_response["data"]:
                if match.get("status") == "approved":
                    approved_match = match
                    break


        message = f"✅ У вас есть заявка на переселение\n\n"
        message += f"Переселение: {relocation_name}\n"
        message += f"Статус: {status_text}\n"
        message += f"Количество заявок на вашу комнату: {matches_count}\n"


        if application_status == "ended" and approved_match:

            match_id = approved_match.get("id")
            match_response = make_directus_request(
                endpoint=f"/items/student_relocation_applications_match/{match_id}",
                params={
                    "fields": ["relocation_applications_id_from"]
                }
            )

            if match_response and "data" in match_response:
                from_application_id = match_response["data"].get("relocation_applications_id_from")


                from_application_response = make_directus_request(
                    endpoint=f"/items/student_relocation_applications/{from_application_id}",
                    params={
                        "fields": [
                            "student_accommodation_id_from", 
                            "student_accommodation_from_address_id",
                            "user_created"
                        ]
                    }
                )

                if from_application_response and "data" in from_application_response:
                    from_application = from_application_response["data"]


                    from_accommodation_id = from_application.get("student_accommodation_id_from")
                    from_accommodation_name = "Неизвестно"

                    if from_accommodation_id:
                        from_accommodation_response = make_directus_request(
                            endpoint=f"/items/student_accommodation/{from_accommodation_id}",
                            params={
                                "fields": ["name"]
                            }
                        )

                        if from_accommodation_response and "data" in from_accommodation_response:
                            from_accommodation_name = from_accommodation_response["data"].get("name", "Неизвестно")

                    to_accommodation_id = application.get("student_accommodation_id_from")
                    to_accommodation_name = "Неизвестно"

                    if to_accommodation_id:
                        to_accommodation_response = make_directus_request(
                            endpoint=f"/items/student_accommodation/{to_accommodation_id}",
                            params={
                                "fields": ["name"]
                            }
                        )

                        if to_accommodation_response and "data" in to_accommodation_response:
                            to_accommodation_name = to_accommodation_response["data"].get("name", "Неизвестно")

                    match_user_id = from_application.get("user_created")
                    match_user_name = "Неизвестный пользователь"

                    if match_user_id:
                        user_response = make_directus_request(
                            endpoint=f"/users/{match_user_id}",
                            params={
                                "fields": ["first_name", "last_name"]
                            }
                        )

                        if user_response and "data" in user_response:
                            user_data = user_response["data"]
                            first_name = user_data.get("first_name", "")
                            last_name = user_data.get("last_name", "")
                            match_user_name = f"{first_name} {last_name}".strip() or "Неизвестный пользователь"

                    message += f"\nВы переселяетесь из {from_accommodation_name} в {to_accommodation_name}"
                    message += f"\nВместе с: {match_user_name}"

        return message

    except Exception as e:
        logger.error(f"Error checking relocation status for user {user_id}: {e}")
        return "⚠️ Не удалось получить информацию о переселении. Пожалуйста, попробуйте позже."
