from framework.utils.db import get_db_host


def main():
    host = get_db_host()
    print(host)


if __name__ == "__main__":
    main()
