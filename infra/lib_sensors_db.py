import os
import sqlite3
import repackage
import sys
from instance.config import Config
def get_sensors_type():
    conn = sqlite3.connect(os.path.join(Config.DB_DIR, 'vilatec.db'))
    cursor = conn.cursor()

    sensors_db = list(cursor.execute("SELECT tipo FROM tipo_sensor"))

    cursor.close()
    conn.close()

    list_sensors = []
    for sensor in sensors_db:
        list_sensors.append(sensor[0])
    return list_sensors

def get_sensors_id():
    conn = sqlite3.connect(os.path.join(Config.DB_DIR, 'vilatec.db'))
    cursor = conn.cursor()

    sensors_db = list(cursor.execute("SELECT * FROM tipo_sensor"))

    cursor.close()
    conn.close()

    list_sensors = []
    for sensor in sensors_db:
        list_sensors.append((sensor[0], sensor[1]))
    return list_sensors

def get_sensors_info():
    conn = sqlite3.connect(os.path.join(Config.DB_DIR, 'vilatec.db'))
    cursor = conn.cursor()

    intervalo_db = list(cursor.execute("SELECT * FROM sensor"))

    cursor.close()
    conn.close()

    list_intervalo = []
    for sensor in intervalo_db:
        list_intervalo.append((sensor[1], sensor[2], sensor[3]))
    return list_intervalo
