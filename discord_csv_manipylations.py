# Function to get classes from filenames (New function)
import csv
import os

header_row = []
points_possible_row = []

def read_csv_headers(class_csv):
    global header_row, points_possible_row
    with open(class_csv, 'r', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        header_row = next(csvreader)  # Read the header
        points_possible_row = next(csvreader)  # R
        
def get_classes_from_filenames(directory):
    classes = []
    index = 0
    print("direcoty: ", directory)
    for filename in os.listdir(directory):
        print("filename: ", filename)
        if filename.endswith('.csv'):
            index += 1
            parts = filename.replace(".csv", "").split("_")
            teacher = parts[0].replace("_", " ")
            teacher_lastname = parts[1]
            course = parts[2]
            section = parts[3]
            classes.append(f"{index}. {teacher} {teacher_lastname} {course} section {section}")
    return classes

# Function to list students in a class (Updated function)
def list_students_in_class(class_csv):
    students = []
    with open(class_csv, 'r', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  # Skip the header
        next(csvreader)  # Skip the "Points Possible" row
        for row in csvreader:
            students.append(f"{row[0]} ({row[1]})")  # Student name and section
    return students

# Function to update student in CSV (Updated function)
def update_student_in_csv(class_csv, student_name, section, discord_name, discord_username):
    updated_rows = []
    with open(class_csv, 'r', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  # Skip the header
        next(csvreader)  # Skip the "Points Possible" row
        for row in csvreader:
            if row[0] == student_name and row[1] == section:
                # Let's assume the Discord username and ID will be added in the last two columns
                while len(row) < len(header_row):  # Fill in any missing columns
                    row.append("")
                row[-2] = discord_name
                row[-1] = discord_username
            updated_rows.append(row)
    
    with open(class_csv, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(header_row)  # Write the header back
        csvwriter.writerow(points_possible_row)  # Write the "Points Possible" row back
        csvwriter.writerows(updated_rows)  # Write updated rows
# Function to get available homework for a student
def list_homeworks(class_csv, student_name):
    homeworks = []
    with open(class_csv, 'r', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        header = next(csvreader)  # Read the header
        next(csvreader)  # Skip the "Points Possible" row
        for row in csvreader:
            if row[0] == student_name:
                for i, cell in enumerate(row[2:], 2):  # Skip first two columns (Name and Section)
                    if cell == "":  # Assuming empty cell means homework is not submitted
                        homeworks.append(header[i])
    return homeworks
# Function to update homework status in CSV
def update_homework_status_in_csv(class_csv, student_name, homework, status):
    updated_rows = []
    with open(class_csv, 'r', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        header = next(csvreader)
        next(csvreader)  # Skip "Points Possible" row
        for row in csvreader:
            if row[0] == student_name:
                homework_index = header.index(homework)
                row[homework_index] = status  # Mark as submitted
            updated_rows.append(row)

    with open(class_csv, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(header)
        csvwriter.writerow(points_possible_row)
        csvwriter.writerows(updated_rows)
# Function to find the class associated with a Discord username
def get_class_by_discord_username(directory, discord_username):
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            with open(os.path.join(directory, filename), 'r', newline='') as csvfile:
                csvreader = csv.reader(csvfile)
                next(csvreader)  # Skip the header
                next(csvreader)  # Skip the "Points Possible" row
                for row in csvreader:
                    if discord_username in row:
                        parts = filename.replace(".csv", "").split("_")
                        teacher = parts[0].replace("_", " ")
                        course = parts[1]
                        section = parts[2]
                        return f"{teacher} {course} section {section}"
    return None
