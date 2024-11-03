from collections import UserDict
from datetime import datetime
import pickle 

# Функція для збереження адресної книги у файл
def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

# Функція для завантаження адресної книги з файлу
def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except (FileNotFoundError, EOFError):
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено

# Базовий клас для всіх полів контакту
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

# Клас для імені контакту
class Name(Field):
    def __init__(self, name: str):
        super().__init__(name)
        self.name = name  # Виклик сетера для перевірки

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value: str):
        if value:  # Перевірка, що ім'я не порожнє
            self._name = value
        else:
            raise ValueError("The name cannot be empty")

# Клас для телефону контакту
class Phone(Field):
    def __init__(self, phone_number: str):
        self._phone_number = None  # Тимчасове значення для першої перевірки
        self.phone_number = phone_number  # Виклик сетера для перевірки номера

    @property
    def phone_number(self):
        return self._phone_number

    @phone_number.setter
    def phone_number(self, value: str):
        if value.isdigit() and len(value) == 10:  # Перевірка, що номер складається з 10 цифр
            self._phone_number = value
        else:
            raise ValueError("The phone number must contain only 10 digits")

# Клас для зберігання дати народження
class Birthday(Field):
    def __init__(self, value):
        try:
           self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")   

# Клас для зберігання запису про контакт
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []  # Список для зберігання об'єктів Phone
        self.birthday = None  # За замовчуванням день народження відсутній
    
    def add_birthday(self, birthday: str):
        self.birthday = Birthday(birthday)  # Створення об'єкта Birthday з перевіркою формату
    
    def add_phone(self, phone_number: str):
        phone = Phone(phone_number)  # Використання класу Phone для створення об'єкта
        self.phones.append(phone)  # Додавання створеного об'єкта до списку

    def remove_phone(self, phone_number: str):
        for phone in self.phones:
            if phone.phone_number == phone_number:  # Порівняння номерів
                self.phones.remove(phone)  # Видалення об'єкта Phone зі списку
                return
        raise ValueError("Phone not found")  # Якщо телефон не знайдено

    def edit_phone(self, old_phone_number: str, new_phone_number: str):
        for phone in self.phones:
            if phone.phone_number == old_phone_number:  # Порівняння старого номера
                phone.phone_number = new_phone_number  # Зміна номера на новий
                return
        raise ValueError("Old phone not found")  # Якщо старий номер не знайдено

    def find_phone(self, phone_number: str):
        for phone in self.phones:
            if phone.phone_number == phone_number:  # Порівняння номеру
                return phone  # Повернення знайденого об'єкта Phone
        raise ValueError("Phone not found")  # Якщо номер не знайдено

    def __str__(self):
        phones = '; '.join(p.phone_number for p in self.phones)
        birthday_str = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name.name}, phones: {phones}{birthday_str}"

# Клас для адресної книги, що зберігає записи
class AddressBook(UserDict):
    def __init__(self):
        super().__init__()

    def add_record(self, record: Record):
        self.data[record.name.name] = record  # Використання імені контакту як ключа

    def find(self, name: str):
        for record in self.data.values():  # Перебір всіх записів
            if record.name.name.lower() == name.lower():  
                return record  # Повернення знайденого запису
        raise ValueError("Contact not found")  

    def delete(self, name: str):
        if name in self.data:
            del self.data[name]

    def upcoming_birthdays(self, days=7):
        # Показує контакти, у яких день народження в найближчі дні
        today = datetime.now().date()
        upcoming_contacts = []

        for record in self.data.values():
            if record.birthday:
                birthday_this_year = record.birthday.value.replace(year=today.year).date()
                delta = (birthday_this_year - today).days
                if 0 <= delta <= days:
                    upcoming_contacts.append(record)
                elif delta < 0 and abs(delta) <= days:
                    upcoming_contacts.append(record)
        if upcoming_contacts:
            return upcoming_contacts
        return "No upcoming birthdays."
    
    def input_error(func):
        # Декоратор для обробки помилок вводу
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ValueError as e:
                return str(e)
            except IndexError:
                return "Not enough arguments."
        return wrapper

    @input_error
    def add_birthday(self, args):
        # Додає дату народження до контакту
        name = args[0]
        birthday_date = args[1]
        record = self.find(name)
        if not record:
            return f"Contact {name} not found."
        record.add_birthday(birthday_date)
        return f"Birthday for {name} added."

    @input_error
    def show_birthday(self, args):
        # Відображає день народження контакту
        name = args[0]
        record = self.find(name)  # Знаходить контакт
        if record and record.birthday:
            return f"Birthday for {name} - {record.birthday.value.strftime('%d.%m.%Y')}."
        return f"No birthday for {name}."

    @input_error
    def birthdays(self):
        # Показує всі дні народження, що наближаються
        upcoming = self.upcoming_birthdays()
        if not upcoming:
            return "No birthdays in the coming week."
        return "\n".join(f"{record.name.name} - {record.birthday.value.strftime('%d.%m.%Y')}" for record in upcoming) 
    
    def add_contact(self, name: str, phone_number: str):
        # Додає новий контакт з номером телефону
        if name in self.data:
            raise ValueError("Contact already exists")
        record = Record(name)
        record.add_phone(phone_number)
        self.add_record(record)
        return f"Contact {name} with phone {phone_number} added."

    def edit_phone(self, name: str, old_phone: str, new_phone: str):
        # Змінює номер телефону контакту
        record = self.find(name)
        if record:
            record.edit_phone(old_phone, new_phone)
            return f"Phone for {name} changed from {old_phone} to {new_phone}."
        else:
            raise ValueError("Contact not found")

    def find_phone(self, phone_number: str):
        # Шукає контакт за номером телефону
        for record in self.data.values():
            if any(phone.phone_number == phone_number for phone in record.phones):
                return record
        raise ValueError("Phone number not found")

    def all_contacts(self):
        # Відображає всі контакти в адресній книзі
        return "\n".join(str(record) for record in self.data.values())

def main():
    # Основна функція для запуску бота
    book = load_data()
    
    def parse_input(user_input):
        return user_input.strip().split()
    
    print("Welcome to the assistant bot!")
    while True:
        save_data(book)  # Зберігає адресну книгу
        user_input = input("Enter a command: ").strip()
        if not user_input:
            print("Please enter a command.")
            continue
        
        command, *args = parse_input(user_input)
        
        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(book.add_contact(args[0], args[1]))

        elif command == "change":
            print(book.edit_phone(args[0], args[1], args[2]))

        elif command == "phone":
            print(book.find_phone(args[0]))

        elif command == "all":
            print(book.all_contacts())

        elif command == "add-birthday":
            print(book.add_birthday(args))

        elif command == "show-birthday":
            print(book.show_birthday(args))

        elif command == "birthdays":
            print(book.birthdays())

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
