import sys


class Command:

    NAME = ""
    HELP = ""

    def define(self, parser):
        pass

    def run(self, args):
        print(args)

    def __call__(self, args=sys.argv[1:] if len(sys.argv) > 1 else []):
        parser = argparse.ArgumentParser(prog=self.NAME, help=self.HELP)
        self.define(parser)
        options, args = parser.parse_known_args(args)
        return self.run(options)

# EOF
