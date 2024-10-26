import os
import random
import csv
import calendar
import sys

class Doctor:
    def __init__(self, doctor_id, specialty_name, specialty_id):
        self.id = doctor_id
        self.specialty_name = specialty_name
        self.specialty_id = specialty_id

class Room:
    def __init__(self, room_id, room_type, specialty_id):
        self.id = room_id
        self.type = room_type
        self.specialty_id = specialty_id

class TimeSlot:
    def __init__(self, slot_id):
        self.id = slot_id

class Schedule:
    def __init__(self, doctor_id, room_id, time_slot, day, month, year):
        self.doctor_id = doctor_id
        self.room_id = room_id
        self.time_slot = time_slot
        self.day = day
        self.month = month
        self.year = year

    def __repr__(self):
        return f"(Doctor: {self.doctor_id}, Room: {self.room_id}, TimeSlot: {self.time_slot.id}, Day: {self.day}, Month: {self.month}, Year: {self.year})"

class CSVReader:
    @staticmethod
    def read_doctors(file_path):
        doctors = []
        with open(file_path, mode='r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                doctor_id = int(row['doctor_id'])
                specialty_name = row['specialty_name']
                specialty_id = int(row['specialty_id'])
                doctors.append(Doctor(doctor_id, specialty_name, specialty_id))
        return doctors

    @staticmethod
    def read_rooms(file_path):
        rooms = []
        with open(file_path, mode='r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                room_id = int(row['room_id'])
                room_type = row['room_type']
                specialty_id = int(row['specialty_id'])
                rooms.append(Room(room_id, room_type, specialty_id))
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

#def get_month_year():
#    while True:
#        try:
#            year = int(input("Nhập năm (ví dụ: 2024): "))
#            month = int(input("Nhập tháng (1-12): "))
#            if 1 <= month <= 12:
#                return year, month
#            else:
#                print("Tháng không hợp lệ! Vui lòng nhập lại.")
#        except ValueError:
#            print("Vui lòng nhập năm và tháng hợp lệ.")

def get_valid_days(year, month):
    num_days = calendar.monthrange(year, month)[1]
    valid_days = [day for day in range(1, num_days + 1) if calendar.weekday(year, month, day) != 6]  # 6 là Chủ Nhật
    return valid_days

doctor_file = os.path.join(os.path.dirname(__file__), '../Models/doctors.csv')
room_file = os.path.join(os.path.dirname(__file__), '../Models/rooms.csv')
time_slot_file = os.path.join(os.path.dirname(__file__), '../Models/time_slots.csv')
schedule_file = os.path.join(os.path.dirname(__file__), '../Models/schedule.csv')

doctors = CSVReader.read_doctors(doctor_file)
rooms = CSVReader.read_rooms(room_file)
time_slots = CSVReader.read_time_slots(time_slot_file)

class GeneticAlgorithm:
    def __init__(self, doctors, rooms, time_slots, valid_days, month, year, population_size=200, generations=500, cxpb=0.7, mutpb=0.2):
        self.doctors = doctors
        self.rooms = rooms
        self.time_slots = time_slots
        self.valid_days = valid_days
        self.month = month
        self.year = year
        self.population_size = population_size
        self.generations = generations
        self.cxpb = cxpb
        self.mutpb = mutpb

    def create_individual(self):
        individual = []
        for doctor in self.doctors:
            num_days_working = random.randint(2, 6)  # Số ngày làm việc ngẫu nhiên cho mỗi bác sĩ
            for _ in range(num_days_working):
                room = random.choice([room for room in self.rooms if room.specialty_id == doctor.specialty_id]).id
                time_slot = random.choice(self.time_slots)
                day = random.choice(self.valid_days)
                individual.append(Schedule(doctor.id, room, time_slot, day, self.month, self.year))
        return individual

    def create_population(self):
        return [self.create_individual() for _ in range(self.population_size)]

    def fitness(self, individual):
        violations = 0
        room_timeslot = {}
        doctor_day_slots = {}

        for schedule in individual:
            room_id = schedule.room_id
            timeslot_id = schedule.time_slot.id
            doctor_id = schedule.doctor_id
            day = schedule.day

            room_info = next((room for room in self.rooms if room.id == room_id), None)
            doctor_info = next((doctor for doctor in self.doctors if doctor.id == doctor_id), None)

            if not room_info or not doctor_info:
                violations += 5000
                continue

            # Kiểm tra trùng lặp lịch trình
            if (doctor_id, room_id, timeslot_id, day) in room_timeslot:
                print(f"Trùng lặp phát hiện: Bác sĩ {doctor_id}, Phòng {room_id}, Thời gian {timeslot_id} vào ngày {day}/{self.month}/{self.year}")
                violations += 1500
            room_timeslot[(doctor_id, room_id, timeslot_id, day)] = doctor_id

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
            doctor_id = individual[idx].doctor_id
            specialty_id = next((doctor.specialty_id for doctor in self.doctors if doctor.id == doctor_id), None)
            valid_rooms = [room for room in self.rooms if room.specialty_id == specialty_id]

            if valid_rooms:
                room = random.choice(valid_rooms).id
                time_slot = random.choice(self.time_slots)
                day = random.choice(self.valid_days)
                individual[idx] = Schedule(doctor_id, room, time_slot, day, self.month, self.year)
            else:
                print(f"No valid rooms found for doctor ID {doctor_id} with specialty ID {specialty_id}.")
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

def write_schedule_to_csv(schedule, file_path):
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['doctor_id', 'room_id', 'time_slot_id', 'day', 'month', 'year'])
        for entry in schedule:
            writer.writerow([entry.doctor_id, entry.room_id, entry.time_slot.id, entry.day, entry.month, entry.year])


if __name__ == "__main__":
    year = int(sys.argv[1])  # Nhận giá trị từ tham số command line
    month = int(sys.argv[2])  # Nhận giá trị từ tham số command line
    valid_days = get_valid_days(year, month)

    ga = GeneticAlgorithm(doctors, rooms, time_slots, valid_days, month, year)
    best_schedule = ga.run()

    write_schedule_to_csv(best_schedule, schedule_file)
    print("Lịch đã được ghi vào tệp schedule.csv.")
