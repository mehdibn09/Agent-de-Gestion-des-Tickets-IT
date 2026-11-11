"""Raccourci de la commande ticket train."""
import sys

from ticket_agent.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["train", *sys.argv[1:]]))
