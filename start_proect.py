import subprocess
import sys
from typing import Callable, Dict

MIN_ARGS = 2
COMMAND_INDEX = 1
DB_COMMAND = "db_fill"
STATIC_SRC_DIR = "/app/collected_static/"
STATIC_DEST_DIR = "/backend_static/static/"


class CommandExecutionError(Exception):
    """Пользовательское исключение для ошибок выполнения команд."""

    pass


def run_command(command: str) -> None:
    """Функция для выполнения команды в терминале."""
    try:
        result = subprocess.run(
            command,
            check=True,
            shell=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        print(f"Команда выполнена успешно: {command}")
        if result.stdout:
            print(f"Вывод: {result.stdout}")
    except subprocess.CalledProcessError as e:
        error_msg = (
            f"Ошибка при выполнении команды: {command}\n"
            f"Код ошибки: {e.returncode}\n"
            f"Вывод ошибки: {e.stderr}"
        )
        print(error_msg)
        raise CommandExecutionError(error_msg)


def prepare_database() -> None:
    """Подготавливает базу данных, выполняя миграции."""
    print("Подготовка БД...")
    run_command("python manage.py makemigrations")
    run_command("python manage.py migrate")


def fill_database() -> None:
    """Наполняет базу данных данными из фикстур."""
    print("Наполнение БД данными...")
    run_command("python manage.py fill_db")


def collect_static() -> None:
    """Собирает статические файлы и копирует их в нужную директорию."""
    print("Собираем статику в контейнере backend...")
    run_command("python manage.py collectstatic")
    print(f"Копируем статику из {STATIC_SRC_DIR} в {STATIC_DEST_DIR}")
    run_command(f"cp -r {STATIC_SRC_DIR}. {STATIC_DEST_DIR}")


def create_superuser() -> None:
    """
    Создает суперпользователя для админки
    с использованием переменных окружения.
    """
    print("Создание админа...")
    import os

    os.environ.setdefault("DJANGO_SUPERUSER_USERNAME", "admin")
    os.environ.setdefault("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
    os.environ.setdefault("DJANGO_SUPERUSER_PASSWORD", "password")
    try:
        run_command("python manage.py createsuperuser --noinput")
    except CommandExecutionError as e:
        print(
            f"Ошибка создания суперпользователя "
            f"(возможно, уже существует): {e}"
        )


def filling_db():
    """
    Выполняет полный процесс подготовки базы данных:
    миграции, наполнение данными, сбор статики и создание суперпользователя.
    """
    try:
        prepare_database()
        fill_database()
        collect_static()
        create_superuser()
    except CommandExecutionError as e:
        print(f"Процесс подготовки БД прерван: {e}")
        sys.exit(1)


def get_commands() -> Dict[str, Callable[[], None]]:
    """Возвращает словарь доступных команд."""
    return {
        DB_COMMAND: filling_db,
    }


if __name__ == "__main__":
    if len(sys.argv) < MIN_ARGS:
        print("Пример команды: python start_proect.py [db_fill]")
        sys.exit(COMMAND_INDEX)

    command = sys.argv[COMMAND_INDEX]
    commands = get_commands()
    if command in commands:
        commands[command]()
    else:
        print("Некорректный аргумент. Введите 'db_fill'" "для подготовки БД.")
        sys.exit(COMMAND_INDEX)
