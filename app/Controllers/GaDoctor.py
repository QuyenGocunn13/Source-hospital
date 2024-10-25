import os
import random
import csv
import calendar

# Định nghĩa các lớp trước khi sử dụng
class Doctor:
    def __init__(self, doctor_id, specialty_name):
        self.id = doctor_id
        self.specialty_name = specialty_name

class Room:
    def __init__(self, room_id, room_type):
        self.id = room_id
        self.type = room_type

class TimeSlot:
    def __init__(self, slot_id):
        self.id = slot_id

class Schedule:
    def __init__(self, doctor_id, room_id, time_slot, day):
        self.doctor_id = doctor_id
        self.room_id = room_id
        self.time_slot = time_slot  # Đối tượng TimeSlot
        self.day = day  # Ngày cụ thể

    def __repr__(self):
        return f"(Doctor: {self.doctor_id}, Room: {self.room_id}, TimeSlot: {self.time_slot.id}, Day: {self.day})"

# Lớp đọc tệp CSV cho Doctor, Room, và TimeSlot
class CSVReader:
    @staticmethod
    def read_doctors(file_path):
        doctors = []
        with open(file_path, mode='r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                doctor_id = int(row['doctor_id'])
                specialty_name = row['specialty_name']
                doctors.append(Doctor(doctor_id, specialty_name))
        return doctors

    @staticmethod
    def read_rooms(file_path):
        rooms = []
        with open(file_path, mode='r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                room_id = int(row['room_id'])
                room_type = row['room_type']
                rooms.append(Room(room_id, room_type))
        return rooms

    @staticmethod
    def read_time_slots(file_path):
        time_slots = []
        with open(file_path, mode='r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                slot_id = int(row['slot_id'])
                time_slots.append(TimeSlot(slot_id))
        return time_slots

# Hàm để nhập tháng và năm
def get_month_year():
    year = int(input("Nhập năm (ví dụ: 2024): "))
    month = int(input("Nhập tháng (1-12): "))
    return year, month

# Hàm để lấy danh sách các ngày hợp lệ trong tháng
def get_valid_days(year, month):
    num_days = calendar.monthrange(year, month)[1]
    valid_days = [day for day in range(1, num_days + 1) if calendar.weekday(year, month, day) != 6]  # 6 là Chủ Nhật
    return valid_days

# Đường dẫn tệp
doctor_file = os.path.join(os.path.dirname(__file__), '../Models/doctors.csv')
room_file = os.path.join(os.path.dirname(__file__), '../Models/rooms.csv')
time_slot_file = os.path.join(os.path.dirname(__file__), '../Models/time_slots.csv')
schedule_file = os.path.join(os.path.dirname(__file__), '../Models/schedule.csv')  # Đường dẫn đến tệp schedule.csv

# Đọc dữ liệu từ tệp CSV
doctors = CSVReader.read_doctors(doctor_file)
rooms = CSVReader.read_rooms(room_file)
time_slots = CSVReader.read_time_slots(time_slot_file)

class GeneticAlgorithm:
    def __init__(self, doctors, rooms, time_slots, valid_days, population_size=100, generations=50, cxpb=0.7, mutpb=0.2):
        self.doctors = doctors
        self.rooms = rooms
        self.time_slots = time_slots
        self.valid_days = valid_days
        self.population_size = population_size
        self.generations = generations
        self.cxpb = cxpb
        self.mutpb = mutpb

    def create_individual(self):
        individual = []
        for doctor in self.doctors:
            room = random.choice(self.rooms).id
            time_slot = random.choice(self.time_slots)  # Lấy đối tượng TimeSlot
            day = random.choice(self.valid_days)  # Chọn ngày hợp lệ
            individual.append(Schedule(doctor.id, room, time_slot, day))
        return individual

    def create_population(self):
        return [self.create_individual() for _ in range(self.population_size)]

    def fitness(self, individual):
        violations = 0
        room_timeslot = {}
        doctor_day_slots = {}

        for schedule in individual:
            room_id = schedule.room_id
            timeslot_id = schedule.time_slot.id  # Lấy id của timeslot từ đối tượng
            doctor_id = schedule.doctor_id
            day = schedule.day

            room_info = next((room for room in self.rooms if room.id == room_id), None)
            doctor_info = next((doctor for doctor in self.doctors if doctor.id == doctor_id), None)

            if not room_info or not doctor_info:
                violations += 5000
                continue

            if (doctor_id, room_id, timeslot_id) in room_timeslot:
                violations += 1500
            room_timeslot[(doctor_id, room_id, timeslot_id)] = doctor_id

            if room_info.type != doctor_info.specialty_name:
                violations += 1000

            if (doctor_id, day) not in doctor_day_slots:
                doctor_day_slots[(doctor_id, day)] = 0
            doctor_day_slots[(doctor_id, day)] += 1

            if doctor_day_slots[(doctor_id, day)] > 2:
                violations += 2000

        return violations

    def selection(self, population):
        population.sort(key=self.fitness)
        return population[:self.population_size // 2]

    def crossover(self, parent1, parent2):
        cut_point = random.randint(1, len(parent1) - 1)
        child1 = parent1[:cut_point] + parent2[cut_point:]
        child2 = parent2[:cut_point] + parent1[cut_point:]
        return child1, child2

    def mutate(self, individual):
        if random.random() < self.mutpb:
            idx = random.randint(0, len(individual) - 1)
            room = random.choice(self.rooms).id
            time_slot = random.choice(self.time_slots)  # Lấy đối tượng TimeSlot
            day = random.choice(self.valid_days)  # Chọn ngày hợp lệ
            individual[idx] = Schedule(individual[idx].doctor_id, room, time_slot, day)
        return individual

    def run(self):
        population = self.create_population()

        for generation in range(self.generations):
            fitness_values = [self.fitness(ind) for ind in population]
            print(f"Generation {generation + 1}: Best Fitness = {min(fitness_values)}")

            if min(fitness_values) == 0:
                print("Optimal solution found!")
                break

            population = self.selection(population)
            offspring = []

            while len(offspring) < self.population_size:
                parent1, parent2 = random.sample(population, 2)
                child1, child2 = self.crossover(parent1, parent2)
                offspring.append(self.mutate(child1))
                offspring.append(self.mutate(child2))

            population = offspring

        best_schedule = min(population, key=self.fitness)
        return best_schedule

# Hàm ghi lịch vào tệp CSV
def write_schedule_to_csv(schedule, file_path):
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['doctor_id', 'room_id', 'time_slot_id', 'day'])  # Tiêu đề cột
        for entry in schedule:
            writer.writerow([entry.doctor_id, entry.room_id, entry.time_slot.id, entry.day])

# Nhập tháng và năm
year, month = get_month_year()
valid_days = get_valid_days(year, month)

# Chạy thuật toán GA
ga = GeneticAlgorithm(doctors, rooms, time_slots, valid_days, population_size=150, generations=500)
best_schedule = ga.run()

# In kết quả
print("Best Schedule Found:")
for s in best_schedule:
    print(s)

# Ghi lịch vào tệp CSV
write_schedule_to_csv(best_schedule, schedule_file)
print(f"Lịch đã được ghi vào tệp {schedule_file}.")
