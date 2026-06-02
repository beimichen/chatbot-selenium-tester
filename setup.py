import csv

def output():
    with open('output.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['job', 'last_response', 'status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()


def chat_db(job_in):
    base = r"./chats/"
    fname = str(job_in) + '_chat.csv'
    full = base + fname
    with open(full, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['user_type', 'message']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
    return full

# output()


