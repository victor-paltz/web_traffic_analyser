# Web traffic analyser

## Description

The goal of this project is to monitor HTTP traffic on a machine.

There are several parts in the project:
- A generator of logs that reads a csv file and fills a buffer with requests, following the csv file history.
- A console program that reads incoming logs and do some statistics:
    - Computing the average traffic on a sliding window of 2 minutes and raising alerts if it exceeds a threashold.
    - Computing statistics on the requests every 10 seconds

## Installation

Use the package manager [pip3](https://pip.pypa.io/en/stable/) to install the dependencies.
There is only one dependency which is "pytest", we could have chosen unittest to remain independant from third-party libraries.

```bash
pip3 install -r requirements.txt
```

## Usage

To run the simulation, you should first download the sample_csv.txt file and store it on you machine (ex: "data/sample_csv.txt").
Once it is done, just launch the following command:
```bash
python3 main.py --src_path "data/sample_csv.txt" --avg_trafic_threshold 10 
```
You can use the flag -h for help.

Once it's done, just press any key to start the monitoring app.

## Files
```
├── Alert.py            -> class storing Alert objects
├── ConsoleApp.py       -> class defining our console application
├── Deserializer.py     -> class defining deserializer (convert string to dict)
├── LogGenerator.py     -> class defining a log generator besed on a csv logs file
├── README.md
├── data                -> folder containing data for test and simulation
│   ├── sample_csv.txt
│   └── test_csv.txt
├── log_analyse_fcts.py -> Contains some functions to do stats on logs
├── main.py             -> main file to launch the project
├── requirements.txt    -> requirements for installation
├── test_alert.py       -> test for the Alert logic
└── utils.py            -> some utils functions to format time, etc..
```

## Future improvements

There are still many improvement that could be done for this project:
- Coding more tests for the monitoring app
- Improving the design of the app (using colors)
- Handling more edge case in the program (checking that the inputs are in the good format)
- Creating more general classes for the objects in order to reuse the code
- Controling the simulation time speed in order to run faster tests
- Drawing a traffic curve in real time and a threshold line
- ...