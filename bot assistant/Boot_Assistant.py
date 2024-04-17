from collections import defaultdict
from datetime import datetime, timedelta
import json


class AddressBook:
    def __init__(self):
        self.contacts = {}
        self.modified = False


    def input_error(func):
        def inner(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            
            except ValueError:
                return "Please provide both a name and a phone number!"
            except KeyError:
                return "Contact not found or not existing!"
            except IndexError:
                return "Please enter more details!"
            except TypeError:
                return "Phone number must consist of 10 digits!"
            except Exception:
                return "Error"

        return inner


    @input_error
    def parse_input(self, user_input):
        cmd, *args = user_input.split()
        cmd = cmd.strip().lower()
        return cmd, args
    

    @input_error
    def add_contact(self, args):
        if len(args) != 2:
            raise ValueError("Please provide both a name and a phone number!")
        
        name, phone = args
        if len(phone) != 10 or not phone.isdigit():
            raise TypeError("Phone number must consist of 10 digits!")
        
        if name in self.contacts:
            return f'Contact "{name}", already exists!'
        else:
            self.contacts[name] = {"phone": phone, "birthday": None}
            self.sort_contacts()
            self.modified = True
            return f'Contact "{name}", added successfully!'


    @input_error
    def update_contact(self, args):
        if len(args) != 2:
            raise ValueError("Please provide both a name and a phone number!")
        name, phone = args
        if len(phone) != 10 or not phone.isdigit():
            raise TypeError("Phone number must consist of 10 digits!")
        
        if name not in self.contacts:
            raise KeyError("Contact not found or not existing!")
        else:
            self.contacts[name]["phone"] = phone
            self.modified = True
            return f'Contact "{name}", successfully updated!'
        
        
    @input_error
    def update_contact_name(self, args):
        if len(args) != 2:
            raise ValueError("Please provide both the old and new names!")
        
        old_name, new_name = args
        if old_name not in self.contacts:
            raise KeyError("Contact not found, or not existing!")
        
        self.contacts[new_name] = self.contacts.pop(old_name)
        self.sort_contacts()
        self.modified = True
        return f'Contact name updated from "{old_name}" to "{new_name}" successfully!'


    @input_error
    def show_phone(self, args):
        name = args[0]
        if name not in self.contacts:
            raise KeyError("Contact not found!")
        return f'Phone number for: "{name}": {self.contacts[name]["phone"]}'


    @input_error
    def show_all(self):
        contacts_list = []
        for name, info in self.contacts.items():
            contact_info = f'{name}: {info["phone"]}'
            if info["birthday"]:
                contact_info += f', Birthday: {info["birthday"]}'
            contacts_list.append(contact_info)
        return '\n'.join(contacts_list)
    

    @input_error
    def delete_contact(self, args):
        name = args[0]
        if name in self.contacts:
            del self.contacts[name]
            self.sort_contacts()
            self.modified = True
            return f'Contact "{name}" deleted successfully!'
        else:
            return f'Contact "{name}" does not exist!'
        

    @input_error
    def clear_all_contacts(self):
        confirmation = input("Are you sure you want to delete all contacts? (yes/no): ")
        if confirmation.lower() == "yes":
            self.contacts.clear()
            self.modified = True
            return 'All contacts deleted successfully!'
        else:
            return 'No contacts were deleted.'
    

    def add_birthday(self, name, birth_day):
        if name in self.contacts:
            self.contacts[name]["birthday"] = birth_day
            self.modified = True
            return f'Birthday successfully added for contact "{name}"!'
        else:
            return f'Contact "{name}", does not exist!'


    def show_birthday(self, name):
        if name in self.contacts and self.contacts[name]["birthday"]:
            return f'Birthday for contact "{name}": {self.contacts[name]["birthday"]}'
        elif name not in self.contacts:
            return f'Contact "{name}", does not exists!'
        else:
            f'No birthday found for contact "{name}"!'


    def get_birthdays_per_week(self):                                             
        birthdays_per_week = defaultdict(list)
        today = datetime.today().date()
        next_week = today + timedelta(days=7)

        for name, info in self.contacts.items():
            if info["birthday"]:
                birth_day = datetime.strptime(info["birthday"], '%d/%m/%Y').date() 
                birthday_current_year = birth_day.replace(year=today.year)

                if birthday_current_year < today:
                    birthday_current_year = birthday_current_year.replace(year=today.year + 1)

                delta_days = (birthday_current_year - today).days

                if 0 <= delta_days < 7:
                    birthday_week = birthday_current_year.strftime("%A")
                    if birthday_week in ["Saturday", "Sunday"]:
                        birthday_week = "Monday"
                    birthdays_per_week[birthday_week].append(name)

        return birthdays_per_week
    

    @staticmethod
    def validate_birthday(birthday_str):
        try:
            datetime.strptime(birthday_str, '%d/%m/%Y')
            return True
        except ValueError:
            return False
    

    def save_to_file(self, filename):
        with open(filename, 'w') as file:
            json.dump(self.contacts, file)

    def load_from_file(self, filename):
        try:
            with open(filename, 'r') as file:
                self.contacts = json.load(file)
        except FileNotFoundError:
            print("No previous data found. Starting with an empty address book.")


    def sort_contacts(self):
        self.contacts = dict(sorted(self.contacts.items()))

    
   


def main():
    address_book = AddressBook()
    filename = "address_book.json"
    address_book.load_from_file(filename)
    

    print('\nWelcome to your assistant bot!\nIf you need help with the commands, please type "help".')

    save_choice = None

    while True:
        user_input = input("\nEnter a command: ")
        parts = user_input.split()
        command = parts[0].strip().lower()
        args = parts[1:]

        if command in ["close", "exit"]:
            if address_book.modified:
                save_choice = input("Do you want to save changes to the address book, before exiting? (yes/no): ")
                if save_choice.lower() == "yes":
                    address_book.save_to_file(filename)
            print("Goodbye!")
            break

        elif command == "hello":
            print("Hi, how can I help you today?")

        elif command == "help":
            print('\nPlease use one of the commands bellow:')
            print('"add ___" - To add a new contact,','\n"update ___" - To update an existing contact\'s number,','\n"update-name ___" - To update the name of an existing contact,')
            print('"show ___" - To display a specific contact,\n"all" - To display all contacts,')
            print('"add-birthday ___" - To add birthday to an existing contact,\n"delete ___" - To delete a contact,\n"clear_all" - To delete all contacts.')
            print('"show-birthday ___" - To display the birthday of a contact,\n"birthdays" - To display the birthdays of contacts occurring in the next week,')
            print('And "exit" or "close"')

        elif command == "add":
            print(address_book.add_contact(args))

        elif command == "update":
            print(address_book.update_contact(args))

        elif command == "update-name":
            print(address_book.update_contact_name(args))

        elif command == "show":
            print(address_book.show_phone(args))

        elif command == "all":
            print(address_book.show_all())

        elif command == "delete":
            print(address_book.delete_contact(args))

        elif command == "clear_all":
            print(address_book.clear_all_contacts())       #        ******  This command shall be used carefully :)) ******* 

        elif command == "add-birthday":
            if len(args) != 2:
                print("Please provide both name and birthday in DD.MM.YYYY format.")
            else:
                name, birth_date = args
                print(address_book.add_birthday(name, birth_date))

        elif command == "show-birthday":
            if len(args) != 1:
                print("Please provide the name of the contact.")
            else:
                name = args[0]
                print(address_book.show_birthday(name))

        elif command == "birthdays":
            birthdays = address_book.get_birthdays_per_week()
            if birthdays:
                for day, contacts in birthdays.items():
                    print(f"{day}: {', '.join(contacts)}")
            else:
                print("No birthdays in the next week.")

        else:
            print("\nInvalid command.\nPlease try again!\n")


if __name__ == "__main__":
    main()
