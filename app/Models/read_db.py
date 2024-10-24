import csv

def read_rooms_from_csv(file_path):
    rooms = []
    with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            rooms.append({
                'room_id': row['room_id'],
                'room_type': row['room_type']
            })
    return rooms

if __name__ == "__main__":
    # Kiểm tra độc lập
    file_path = '/Models/rooms.csv'  # Đường dẫn đến file CSV
    rooms = read_rooms_from_csv(file_path)
    for room in rooms:
        print(room)