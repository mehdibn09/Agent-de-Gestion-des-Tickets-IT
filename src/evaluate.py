"""Raccourci de la commande ticket evaluate."""
import sys

from ticket_agent.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["evaluate", *sys.argv[1:]]))
