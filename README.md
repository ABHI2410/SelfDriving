# CARLA Autonomous Driving Simulation

This project is a simulation of an autonomous vehicle using the CARLA simulator. The vehicle is equipped with various sensors to perceive its environment and make driving decisions based on sensor data.

## Getting Started

### Prerequisites

- Python 3.7 or higher
- CARLA Simulator (version 0.9.12 or higher)
- Required Python packages:
  - carla
  - numpy
  - opencv-python (cv2)
  - open3d
  - matplotlib

### Installation

1. Install CARLA Simulator by following the instructions on the [official website](https://carla.org/).
2. Clone this repository to your local machine.
3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt

Running the Simulation
Start the CARLA server by navigating to the CARLA directory and running:
bash
Copy code
./CarlaUE4.sh
In a separate terminal, navigate to the directory containing this project and run:
bash
Copy code
python Carla.py
Sensors
The autonomous vehicle is equipped with the following sensors:

RGB Camera
Depth Camera
GNSS (GPS)
IMU (Inertial Measurement Unit)
Semantic Lidar
Traffic Light Detector
Speed Limit Detector
Radar Sensor
Lane Invasion Detector
Vehicle Control
The vehicle's behavior is controlled based on the data received from the sensors. It follows traffic rules, avoids collisions, and stays within lane boundaries.

Rules and Reinforcement Learning
The vehicle's driving behavior is evaluated based on a set of predefined rules. Points are awarded or deducted based on the vehicle's adherence to these rules. This forms the basis for a reinforcement learning model where the vehicle learns to drive autonomously by maximizing its reward.