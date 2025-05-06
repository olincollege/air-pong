# air-pong

Ping Pong game simulator that uses computer vision for human input.

<img src="models/logo.png" alt="drawing" width="200" style="display: block; margin-left: auto; margin-right: auto;" />

![Demo](models/demo.gif)

## Requirements
* python: = 3.10.xx
There might be package conflicts if not with python 3.10.
* pip
* conda/miniconda (highly recommended)
* un-isolated shell environment
    * This means that our project cannot run is WSL because it dosn't have access to cameras.

## Setup
### Clone the Github repository
Clone the github repository to your local machine using your desired method. Navigate to the folder in terminal.
```
git clone <PROJECT KEY OR HTTP>
```

If you don't know how or require further resources on cloning Github repositories, [use this resources](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository)
To install MediaPipe and all the other dependencies, open the project folder and run:

### Create a conda env (highly recommended)
To isolate dependencies and python versions, create a conda environment that uses python 3.10.

Use the following command to create
```
conda create -n <NAME_OF_ENV> python==3.10
```

Use the following command to activate
```
conda activate <NAME_OF_ENV>
```
Note that NAME_OF_ENV must be identical to the previous name you input however it doesn't matter which folder you are in when you activate.

### Install requirements
The final setup step is installing the requirements. Make sure you are in the root folder of the repository before running the following command.

```
pip install -r requirements.txt
```

## Playing the game

### Running
1. Navigate to the repository root folder. 
2. Make sure all setup instructions are followed and the conda env is activated. 
3. Run the following command
```
python3 main.py
```

Please note that the program requires a fast single thread CPU. If the code runs but is very slow it is a hardware limitation.

### Game rules

Welcome to AIR-PONG, the best way of playing 1v1 Ping Pong on the go. You may look a bit silly while playing, but trust me - it really changes your ping pong game.

Before we begin, let's lay some ground truths.
* Each player must control with a different hand
    * Players using their right hand to play use WAD to control serve and rotation
    * Players using their left hand to play use arros UP, LEFT and RIGHT to control serve and rotation
* Games are played until 11 points, win by 2, serve switches every 2
* Only one player can rotate their paddle at a time

Now you can start playing! Good luck!

## Acknowledgements
- This project runs using Google's open source project [MediaPipe](https://ai.google.dev/edge/mediapipe/solutions/guide).
- This project makes heavy use of pygame for visuals
- This project makes heavy use of pynput for keyboard inputs
- This project makes heavy use of vpython for physics and math
