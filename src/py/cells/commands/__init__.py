import sys


class Command:

    NAME = ""
    HELP = ""

    def define(self, parser):
        pass

    def out(self, message: str):
        sys.stdout.write(message)
        sys.stdout.write("\n")

    def info(self, message: str):
        sys.stderr.write(message)
        sys.stderr.write("\n")
        return False

    def err(self, message: str):
        sys.stderr.write(message)
        sys.stderr.write("\n")
        return False

    def run(self, args):
        sys.stdout.write(repr(args))

    def __call__(self, args=sys.argv[1:] if len(sys.argv) > 1 else []):
        parser = argparse.ArgumentParser(prog=self.NAME, help=self.HELP)
        self.define(parser)
        options, args = parser.parse_known_args(args)
        return self.run(options)

# EOF
