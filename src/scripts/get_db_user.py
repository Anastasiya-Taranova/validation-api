from framework.utils.db import get_db_username


def main():
    name = get_db_username()
    print(name)


if __name__ == "__main__":
    main()
