import os
import random
import csv

# Lớp đọc tệp CSV cho Doctor, Room, và TimeSlot
class CSVReader:
    @staticmethod
    def read_doctors(file_path):
        doctors = []
        with open(file_path, mode='r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                doctor_id = int(row['doctor_id'])
                specialty = row['specialty']
                doctors.append(Doctor(doctor_id, specialty))
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

# Đường dẫn tệp
doctor_file = os.path.join(os.path.dirname(__file__), '../Models/doctors.csv')
room_file = os.path.join(os.path.dirname(__file__), '../Models/rooms.csv')
time_slot_file = os.path.join(os.path.dirname(__file__), '../Models/time_slots.csv')

# Đọc dữ liệu từ tệp CSV
doctors = CSVReader.read_doctors(doctor_file)
rooms = CSVReader.read_rooms(room_file)
time_slots = CSVReader.read_time_slots(time_slot_file)

class Doctor:
    def __init__(self, doctor_id, specialty):
        self.id = doctor_id
        self.specialty = specialty

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
        self.day = day  # Sử dụng số nguyên (0 cho Monday, 1 cho Tuesday, ..., 4 cho Friday)

    def __repr__(self):
        return f"(Doctor: {self.doctor_id}, Room: {self.room_id}, TimeSlot: {self.time_slot.id}, Day: {self.day})"

class GeneticAlgorithm:
    def __init__(self, doctors, rooms, time_slots, population_size=100, generations=50, cxpb=0.7, mutpb=0.2):
        self.doctors = doctors
        self.rooms = rooms
        self.time_slots = time_slots
        self.population_size = population_size
        self.generations = generations
        self.cxpb = cxpb
        self.mutpb = mutpb

    def create_individual(self):
        individual = []
        for doctor in self.doctors:
            room = random.choice(self.rooms).id
            time_slot = random.choice(self.time_slots).id
            individual.append(Schedule(doctor.id, room, time_slot))
        return individual

    def create_population(self):
        return [self.create_individual() for _ in range(self.population_size)]

    def fitness(self, individual):
        violations = 0
        room_timeslot = {}
        doctor_day_slots = {}  # Dictionary để lưu số ca mỗi bác sĩ theo ngày

        for schedule in individual:
            room_id = schedule.room_id
            timeslot_id = schedule.time_slot.id  # Lấy id của timeslot từ đối tượng
            doctor_id = schedule.doctor_id
            day = schedule.day  # Lấy ngày trong tuần

            # Tìm room_info và doctor_info với error handling
            room_info = next((room for room in self.rooms if room.id == room_id), None)
            doctor_info = next((doctor for doctor in self.doctors if doctor.id == doctor_id), None)

            if not room_info or not doctor_info:
                violations += 5000
                continue

            # Kiểm tra xung đột về phòng và thời gian
            if (doctor_id, room_id, timeslot_id) in room_timeslot:
                violations += 1500
            room_timeslot[(doctor_id, room_id, timeslot_id)] = doctor_id

            # Kiểm tra xung đột về loại phòng và loại chuyên môn
            if room_info.type != doctor_info.specialty:
                violations += 1000

            # Đếm số ca mỗi bác sĩ theo ngày
            if (doctor_id, day) not in doctor_day_slots:
                doctor_day_slots[(doctor_id, day)] = 0
            doctor_day_slots[(doctor_id, day)] += 1

            # Nếu bác sĩ làm quá 2 ca trong cùng một ngày
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
            time_slot = random.choice(self.time_slots).id
            individual[idx] = Schedule(individual[idx].doctor_id, room, time_slot)
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


# Hàm tổng hợp để tạo dữ liệu ngẫu nhiên cho bác sĩ, phòng, và khung thời gian
def generate_data(num_doctors, num_rooms, num_time_slots, specialties, room_types):
    # Tạo danh sách bác sĩ
    doctors = []
    for i in range(1, num_doctors + 1):
        specialty = random.choice(specialties)
        doctors.append(Doctor(i, specialty))

    # Tạo danh sách phòng
    rooms = []
    for i in range(1, num_rooms + 1):
        room_type = random.choice(room_types)
        rooms.append(Room(i, room_type))

    # Tạo danh sách khung thời gian (chỉ gồm ID)
    time_slots = [TimeSlot(i) for i in range(1, num_time_slots + 1)]

    return doctors, rooms, time_slots

# Sử dụng hàm tổng hợp để tạo dữ liệu
specialties = ["Cardiology", "Neurology", "Orthopedics", "Pediatrics", "Dermatology"]
room_types = ["Cardiology", "Neurology", "Orthopedics", "Pediatrics", "Dermatology"]

# Số lượng bác sĩ, phòng, và khung thời gian người dùng nhập vào
num_doctors = 30
num_rooms = 10
num_time_slots = 10

# Gọi hàm generate_data để tạo dữ liệu
doctors, rooms, time_slots = generate_data(num_doctors, num_rooms, num_time_slots, specialties, room_types)

# In kết quả
print("Generated Doctors:")
for doctor in doctors:
    print(f"Doctor ID: {doctor.id}, Specialty: {doctor.specialty}")

print("\nGenerated Rooms:")
for room in rooms:
    print(f"Room ID: {room.id}, Type: {room.type}")

print("\nGenerated Time Slots:")
for time_slot in time_slots:
    print(f"TimeSlot ID: {time_slot.id}")

# Chạy thuật toán GA
ga = GeneticAlgorithm(doctors, rooms, time_slots, population_size=150, generations=10)
best_schedule = ga.run()

# In kết quả
print("Best Schedule Found:")
for s in best_schedule:
    print(s)
