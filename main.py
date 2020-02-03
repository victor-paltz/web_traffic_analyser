
import argparse
import os
import time

from ConsoleApp import ConsoleApp


# Set a parser for CLI interface
parser = argparse.ArgumentParser(
    description="HTTP log monitoring console program")

parser.add_argument("--src_path", type=str, default="sample_csv.txt",
                    help="path to the CSV-encoded HTTP access log")

parser.add_argument("--avg_trafic_threshold", type=float, default=10,
                    help="average traffic threshold to trigger alerts (in requests per second)")

args = parser.parse_args()


# Instanciate the app and the simulation
app = ConsoleApp(args.src_path, args.avg_trafic_threshold)


# Print project name in ASCII
os.system("clear")
print(r"""   __                               _ __           _                          
  / /  ___  ___ _  __ _  ___  ___  (_) /____  ____(_)__  ___ _  ___ ____  ___ 
 / /__/ _ \/ _ `/ /  ' \/ _ \/ _ \/ / __/ _ \/ __/ / _ \/ _ `/ / _ `/ _ \/ _ \
/____/\___/\_, / /_/_/_/\___/_//_/_/\__/\___/_/ /_/_//_/\_, /  \_,_/ .__/ .__/
          /___/                                        /___/      /_/  /_/    """)
print("\n\n\n")


# Wait for a key pressed to start the simulation
input("Press Enter to continue...")
app.start()
