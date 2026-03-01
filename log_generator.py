# log_generator.py - Módulo para gerar logs simulados

import json
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker("pt_BR")

NORMAL_USERS = [f"user_{i:03d}" for i in range(1, 21)]
ADMIN_USERS = ["admin_001", "admin_002"]
ALL_USERS = NORMAL_USERS + ADMIN_USERS

NORMAL_IPS = [fake.ipv4() for _ in range(30)]

EVENT_TYPES = ["login_success", "login_failed", "transaction", "access_resource", "logout", "profile_update"]


def _random_timestamp(days_back: int = 7) -> str:
    now = datetime.now()
    delta = timedelta(
        days=random.randint(0, days_back),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59),
    )
    return (now - delta).isoformat()


def generate_normal_event() -> dict:
    event_type = random.choice(["login_success", "transaction", "access_resource", "logout", "profile_update"])
    user_id = random.choice(ALL_USERS)
    base = {
        "timestamp": _random_timestamp(),
        "user_id": user_id,
        "event_type": event_type,
        "source_ip": random.choice(NORMAL_IPS),
        "status": "success",
        "details": {},
    }

    if event_type == "transaction":
        base["amount"] = round(random.uniform(10, 5000), 2)
        base["details"] = {"description": fake.bs(), "recipient": fake.name()}
    elif event_type == "access_resource":
        base["details"] = {"resource": random.choice(["/dashboard", "/profile", "/reports", "/settings"])}
    elif event_type == "login_success":
        base["details"] = {"device": random.choice(["mobile", "desktop", "tablet"])}

    return base


def generate_suspicious_event(kind: str = None) -> dict:
    """Gera um evento suspeito de um tipo específico ou aleatório."""
    kinds = ["brute_force", "high_value_transaction", "suspicious_hour_transaction", "unauthorized_access"]
    if kind is None:
        kind = random.choice(kinds)

    user_id = random.choice(NORMAL_USERS)
    ts = _random_timestamp()

    if kind == "brute_force":
        return {
            "timestamp": ts,
            "user_id": user_id,
            "event_type": "login_failed",
            "source_ip": fake.ipv4(),  # IP diferente a cada tentativa
            "status": "failed",
            "details": {
                "failed_attempts": random.randint(5, 20),
                "countries": [fake.country_code() for _ in range(random.randint(3, 6))],
            },
        }

    elif kind == "high_value_transaction":
        return {
            "timestamp": ts,
            "user_id": user_id,
            "event_type": "transaction",
            "source_ip": random.choice(NORMAL_IPS),
            "status": "success",
            "amount": round(random.uniform(15000, 100000), 2),
            "details": {
                "description": "Transferência internacional",
                "recipient": fake.name(),
                "recipient_country": fake.country(),
                "user_avg_transaction": round(random.uniform(50, 500), 2),
            },
        }

    elif kind == "suspicious_hour_transaction":
        # Transação entre 0h e 5h
        hour = random.randint(0, 4)
        base_dt = datetime.now().replace(hour=hour, minute=random.randint(0, 59))
        return {
            "timestamp": base_dt.isoformat(),
            "user_id": user_id,
            "event_type": "transaction",
            "source_ip": fake.ipv4(),
            "status": "success",
            "amount": round(random.uniform(5000, 30000), 2),
            "details": {
                "description": "Pagamento noturno",
                "recipient": fake.name(),
                "note": "Horário fora do padrão",
            },
        }

    elif kind == "unauthorized_access":
        return {
            "timestamp": ts,
            "user_id": user_id,  # Usuário comum tentando acessar admin
            "event_type": "access_resource",
            "source_ip": fake.ipv4(),
            "status": "denied",
            "details": {
                "resource": random.choice(["/admin", "/config", "/users/all", "/export/data"]),
                "reason": "Insufficient privileges",
                "attempts": random.randint(2, 10),
            },
        }

    return generate_normal_event()


def generate_logs(count: int = 50, suspicious_ratio: float = 0.25) -> list[dict]:
    """Gera uma lista de logs misturados (normais e suspeitos)."""
    logs = []
    n_suspicious = int(count * suspicious_ratio)
    n_normal = count - n_suspicious

    for _ in range(n_normal):
        logs.append(generate_normal_event())

    for _ in range(n_suspicious):
        logs.append(generate_suspicious_event())

    random.shuffle(logs)
    return logs


def save_logs(logs: list[dict], filepath: str) -> None:
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2, default=str)
    print(f"✅ {len(logs)} logs salvos em '{filepath}'")


def load_logs(filepath: str) -> list[dict]:
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)
