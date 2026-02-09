import os
import csv
from dataclasses import dataclass, astuple

@dataclass
class Task:
    task_number: int
    planned_action: str
    planned_outcome: str
    time_estimate: str
    target_completion_date: str
    criterion: str


#table headers
TASK_DETAILS = [
    "Task number",
    "Planned action",
    "Planned outcome",
    "Time estimate",
    "Target completion date",
    "Criterion"
]

def create_record(path: str) -> None:
    """
    if the path exists:
        Does nothing
    else:
        Creates an empty record-of-tasks csv file (with table headers)
    
    :param path: csv path
    :type path: str
    """

    if not os.path.isfile(path):
        #file doesn't exist
        with open(path, mode='w', newline='', encoding='utf-8') as f:
            csv_w = csv.writer(f)
            csv_w.writerow(TASK_DETAILS)


def log_task(task: Task, path: str) -> None:
    """
    Appends a task to csv
    
    :param task: task data
    :type task: Task
    :param path: csv path
    :type path: str
    """

    #convert data to list
    data = list(astuple(task))

    #write data
    with open(path, mode='a', newline='', encoding='utf-8') as f:
        csv_w = csv.writer(f)
        csv_w.writerow(data)
    

def count_tasks(path: str) -> int:
    """
    Counts number of tasks in csv
    
    :param path: csv path
    :type path: str
    :return: number of tasks
    :rtype: int
    """

    with open(path, mode='r', encoding='utf-8') as f:
        csv_r = csv.reader(f)
        return len(list(csv_r))

def get_task(path: str) -> Task:
    """
    Queries user for task details

    :param path: csv path
    :type path: str
    """

    #auto task number
    task_number = count_tasks(path)

    #get task data from user
    planned_action = input("Planned action: ")
    planned_outcome = input("Planned outcome: ")
    time_estimate = input("Time estimate: ")
    target_completion_date = input("Target completion date: ")
    criterion = input("Criterion: ")

    return Task(task_number, 
                planned_action, 
                planned_outcome,
                time_estimate,
                target_completion_date,
                criterion)

def main() -> None:
    """
    Task loop
    """
    path = "./output/record_of_tasks.csv"
    create_record(path)

    while True:
        task = get_task(path)
        log_task(task, path)

        repeat = input("Input another task [Y/n]?")
        if repeat != "Y":
            break

main()







