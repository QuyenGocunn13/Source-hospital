import csv
import random
import sys

# Hàm để tạo dữ liệu và ghi vào tệp CSV
def create_csv_files():
    # Hàm tổng hợp để tạo dữ liệu ngẫu nhiên cho bác sĩ, phòng và khung thời gian
    def generate_data(num_doctors, num_rooms, specialties, room_types):
        # Tạo danh sách bác sĩ
        doctors = []
        for i in range(1, num_doctors + 1):
            name = f"Doctor {i}"
            specialty = random.choice(specialties)
            doctors.append((i, name, specialty))

        # Tạo danh sách phòng
        rooms = []
        for i in range(1, num_rooms + 1):
            room_type = random.choice(room_types)
            rooms.append((i, room_type))

        # Tạo danh sách khung thời gian với các giá trị mặc định
        time_slots = [
            (1, "Sáng"),
            (2, "Chiều"),
            (3, "Tối")
        ]

        return doctors, rooms, time_slots

    # Sử dụng hàm tổng hợp để tạo dữ liệu
    specialties = ["Cardiology", "Neurology", "Orthopedics", "Pediatrics", "Dermatology"]
    room_types = ["Cardiology", "Neurology", "Orthopedics", "Pediatrics", "Dermatology"]

    # Số lượng bác sĩ và phòng người dùng nhập vào
    num_doctors = 30
    num_rooms = 10

    # Tạo dữ liệu
    doctors, rooms, time_slots = generate_data(num_doctors, num_rooms, specialties, room_types)

    # Ghi dữ liệu vào các tệp CSV với mã hóa utf-8
    with open('doctors.csv', 'w', newline='', encoding='utf-8') as doc_file:
        writer = csv.writer(doc_file)
        writer.writerow(['doctor_id', 'name', 'specialty'])  # Header
        writer.writerows(doctors)

    with open('rooms.csv', 'w', newline='', encoding='utf-8') as room_file:
        writer = csv.writer(room_file)
        writer.writerow(['room_id', 'room_type'])  # Header
        writer.writerows(rooms)

    with open('time_slots.csv', 'w', newline='', encoding='utf-8') as time_slot_file:
        writer = csv.writer(time_slot_file)
        writer.writerow(['slot_id', 'time_slot'])  # Header
        writer.writerows(time_slots)

    print("CSV files created successfully.")

def run():
    print("Running the CSV creation...")
    create_csv_files()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        run()
    else:
        print("Please use 'run' argument to execute the script.")
