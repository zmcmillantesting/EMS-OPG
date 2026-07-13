import sys

from src.ems_opg.core.application  import Application


def main():

    app = Application()

    sys.exit(app.run())


if __name__ == "__main__":
    main()