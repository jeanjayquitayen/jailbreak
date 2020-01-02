#!/usr/bin/python3

import csv
import consolemenu
import inquirer
from inquirer.themes import GreenPassion
import re

questions = [
  inquirer.Text('name', message="Enter Name"),
  inquirer.Text('phone', message="Enter Mobile Number",
                validate=lambda _, x: re.match('^09\d{9}', x),
                )
]

#print(answers["phone"])
contacts = dict()

def inq():
    answers = inquirer.prompt(questions, theme=GreenPassion())
    try:
        if not con_prompt.confirm_answer("name:{}, number:{}".format(answers['name'],answers['phone'])):
            inq()
    except:
        menu.show()

    try:
        csvWriter(answers['name'], answers['phone'])
    except:
        pass

def csvWriter(name,phonenumber):
    with open("contact.csv", 'a+', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow([name, phonenumber])

def readCSV():
    with open("contact.csv",'r') as csvfile:
        for line in csvfile:
            line = line.strip()
            line_split = line.split(',')
            contacts[line_split[0]] = contacts.get(line_split[0], line_split[1])
    return contacts

def showContacts():
    receivers = readCSV()
    if not receivers.keys():
        return None
    contacts_list = [
        inquirer.Checkbox('contact_name', 'Select contact(s) to delete.', receivers.keys())
    ]
    answer = inquirer.prompt(contacts_list, theme=GreenPassion())
    return answer['contact_name']

def delContacts():
    contact_key = showContacts()
    if not contact_key:
        menu.show()
    else:
        for i in contact_key:
            _ = contacts.pop(i)
        print(contacts)
        with open("contact.csv",'w',newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            for i in contacts.items():
                csv_writer.writerow(i)
        con_prompt.enter_to_continue()



if __name__ == "__main__":
    new_screen = consolemenu.screen.Screen()
    con_prompt = consolemenu.prompt_utils.PromptUtils(new_screen)
    menu = consolemenu.ConsoleMenu("Select an Option.")
    add_contact = consolemenu.items.FunctionItem("Add contact", inq, None)
    delete_contact = consolemenu.items.FunctionItem("Delete contact",delContacts, None)


    menu.append_item(add_contact)
    menu.append_item(delete_contact)
    menu.show()
