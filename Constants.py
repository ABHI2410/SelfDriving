import os

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Define constants for scenario_runner and leaderboard paths
SCENARIO_RUNNER_PATH = os.path.join(current_dir, "..", "Carla", "scenario_runner")
LEADERBOARD_PATH = os.path.join(current_dir, "..", "Carla", "leaderboard")

# You can access these constants from other files by importing constant.py