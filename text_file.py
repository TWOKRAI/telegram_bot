def write_in_file(file: str, message: str):
    with open('messages.txt', 'a', encoding='utf-8') as file:
        file.write(message)


def read_all_file(file_path: str) -> str:
    """
    Функция для чтения всего текста из файла и возврата его в виде строки.

    :param file_path: Путь к файлу.
    :return: Содержимое файла в виде строки.
    """

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        return f"Файл {file_path} не найден."
    except Exception as e:
        return f"Произошла ошибка при чтении файла: {e}"


def delete_message_data(self):
    with open('messages.txt', 'w', encoding='utf-8') as file:
        pass