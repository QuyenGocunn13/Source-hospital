import csv
import os

# Hàm chung để đọc CSV
def read_csv(file_path):
    data = []
    try:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data.append(row)
    except FileNotFoundError:
        print(f"File {file_path} không tồn tại.")
    return data

def read_rooms_from_csv(file_path):
    rooms = read_csv(file_path)
    return [
        {'room_id': row['room_id'], 'room_type': row['room_type'], 'specialty_id': row['specialty_id']}
        for row in rooms
    ]

def read_doctors_from_csv(file_path):
    doctors = read_csv(file_path)
    return [
        {'doctor_id': row['doctor_id'], 'name': row['name'], 'specialty_name': row['specialty_name'], 'user_id': row['user_id']}
        for row in doctors
    ]

def read_time_slots_from_csv(file_path):
    return read_csv(file_path)

def read_specialties_from_csv(file_path):
    specialties = read_csv(file_path)
    return {row['specialty_id']: row['specialty_name'] for row in specialties}

def read_schedule_from_csv(file_path):
    schedule_data = read_csv(file_path)
    # Chuyển đổi year và month thành int
    for row in schedule_data:
        row['year'] = int(row['year'])  
        row['month'] = int(row['month'])  
        row['day'] = int(row['day'])  
    return schedule_data
