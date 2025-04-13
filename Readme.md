### Scenario Description
The Rideau Canal Skateway, a cherished historic landmark and a premier winter attraction in Ottawa, demands vigilant monitoring to ensure the safety of its thousands of daily skaters. Fluctuating ice conditions and unpredictable weather patterns pose significant risks, making real-time oversight essential for timely decision-making and public safety.
To address these challenges, our solution deploys simulated IoT sensors at three critical locations: Dow's Lake, Fifth Avenue, and NAC. And capturing vital metrics such as ice thickness, surface temperature, snow accumulation, and external temperature every ten seconds. By leveraging Azure IoT Hub for seamless data ingestion, Azure Stream Analytics for real-time processing and aggregation, and Azure Blob Storage for comprehensive data archival, the system enables the National Capital Commission (NCC) to detect and respond to unsafe conditions promptly.
This integrated approach not only enhances the safety and reliability of the Skateway but also provides invaluable data for future analysis and infrastructure improvements.

### System Architecture
The system architecture for the Rideau Canal Skateway monitoring solution utilizes Azure services to create a real-time IoT data streaming pipeline. Simulated IoT sensors at three locations—Dow’s Lake, Fifth Avenue, and NAC—generate data every 10 seconds on ice thickness, surface temperature, snow accumulation, and external temperature, sending JSON payloads to Azure IoT Hub. The IoT Hub acts as the ingestion point, feeding the data into Azure Stream Analytics, which processes it in real time by aggregating metrics like average ice thickness and maximum snow accumulation over 5-minute windows for each location. The processed results are then output to Azure Blob Storage, where they are stored in a designated container for further analysis, ensuring continuous monitoring and safety assessment of the Skateway.

### Implementation Details
#### IoT Sensor Simulation:
* Describe how the simulated IoT sensors generate and send data to Azure IoT Hub.
* Include the structure of the JSON payload and any scripts or applications used.

I have built a python script to generate data in certain area and sent to the 3 connection link of the devices in Ottawa time zone.
the json structure follow the example
```
{
  "location": "Dow's Lake",
  "iceThickness": 27,
  "surfaceTemperature": -1,
  "snowAccumulation": 8,
  "externalTemperature": -4,
  "timestamp": "2024-11-23T12:00:00Z"
}
```
Setting part as below
```
DEVICES = [
    {
        "location": "Dow's Lake",
        "connection_string": "HostName=8916final.azure-devices.net;DeviceId=Rideau_001;SharedAccessKey=k+a8vVRv8w8Tr1PseuvH7IzERXLgF3JnO8EE55dU4wc="
    },
    {
        "location": "Fifth Avenue",
        "connection_string": "HostName=8916final.azure-devices.net;DeviceId=Rideau_002;SharedAccessKey=4fKfKCFcmDW/4Zua/i1dFMHqLTQ/u9yyBPA/gwf1zuk="
    },
    {
        "location": "NAC",
        "connection_string": "HostName=8916final.azure-devices.net;DeviceId=Rideau_003;SharedAccessKey=8OhuLQcxWjd3l+0s/33mPRWllbW89M/Occpa5Bdug/g="
    }
]

BATCH_INTERVAL = 10
DELAY_BETWEEN_DEVICES = 2
TIME_ZONE = ZoneInfo("America/Toronto")  # Ottawa's time zone

# === Functions ===
def get_sensor_data(location):
    return {
        "location": location,
        "iceThickness": random.randint(0, 50),
        "surfaceTemperature": round(random.uniform(-10.0, 10.0), 2),
        "snowAccumulation": random.randint(0, 30),
        "externalTemperature": round(random.uniform(-15.0, 15.0), 2),
        "timestamp": datetime.now(TIME_ZONE).isoformat()
    }
```

#### Azure IoT Hub Configuration:
* Explain the configuration steps for setting up the IoT Hub, including endpoints and message routing.
1. Create an IoT Hub
In the Azure Portal, search for IoT Hub and click Create.
Provide a name for your IoT Hub and select a resource group.
2. Register 3 Devices for 3 sensors
In the IoT Hub, go to the Devices section and click Add Device.
After the device is created, click on it to view the connection string. Copy the connection string for use in the Python script that going to simulate the sensor. 

#### Azure Stream Analytics Job:
* Describe the job configuration, including input sources, query logic, and output destinations.
* Provide sample queries used for data processing.

1. Create the Stream Analytics Job
In the Azure Portal, search for Stream Analytics jobs and click Create.
Choose Cloud as the hosting environment and create the job.
2. Define Input
In the Stream Analytics job, go to the Inputs section and click Add.
Choose IoT Hub as the input source.
Provide the following details:
	IoT Hub Namespace: Select my IoT Hub.
	IoT Hub Policy Name: Use the iothubowner policy.
	Consumer Group: Use $Default or create a new consumer group in your IoT Hub.
	Serialization Format: Choose JSON. 
3. Define Output
Go to the Outputs section and click Add.
Choose Blob Storage as the output destination.
Provide the following details:
	Storage Account: Select your Azure Storage Account 8916final (Build it first).
	Container: Create an container (rideau) for storing results.
	Path Pattern: Optionally define a folder structure "{date}/{time}".
4. Write the Stream Analytics Query, Save, Test, and Start the Job
```
SELECT
    location AS Location,
    AVG(iceThickness) AS AvgIceThickness,
    MAX(snowAccumulation) AS MaxSnowAccumulation,
    DATEADD(hour, -5, System.Timestamp) AS WindowEndTime
INTO
    [rideau]
FROM
    [8916final]
GROUP BY
    location,
    TumblingWindow(minute, 5)
```

#### Azure Blob Storage:
* Explain how the processed data is organized in Blob Storage (e.g., folder structure, file naming convention).
* Specify the formats of stored data (JSON/CSV).
regard to the (2. Define Input) and (3. Define Output)
I have already define the data will save in Blob as json file with {date}/{time} folder structure

### Usage Instructions:
#### Running the IoT Sensor Simulation:
Provide step-by-step instructions for running the simulation script or application.
In a Linux environment with python3, and use the command below to ensure it support Azure IoT device
```
pip install azure-iot-device
```
and use the command below to run the script
```
python3 generate.py
```
#### Configuring Azure Services:
Describe how to set up and run the IoT Hub and Stream Analytics job.
regard the (Implementation Details)
#### Accessing Stored Data:
Include steps to locate and view the processed data in Azure Blob Storage.
Inside the Storage Account and the related Container, we can see the folder as {date}/{time}
the report inside it. And we can see it including location, AvgIceThickness and MaxSnowAccumulation in 5 minutes and the report time in Ottawa time zone
```
{"Location":"Dow's Lake","AvgIceThickness":32.888888888888886,"MaxSnowAccumulation":28.0,"WindowEndTime":"2025-04-12T18:45:00.0000000Z"}
{"Location":"NAC","AvgIceThickness":31.944444444444443,"MaxSnowAccumulation":20.0,"WindowEndTime":"2025-04-12T18:45:00.0000000Z"}
{"Location":"Fifth Avenue","AvgIceThickness":28.38888888888889,"MaxSnowAccumulation":29.0,"WindowEndTime":"2025-04-12T18:45:00.0000000Z"}
```

### Results:
#### Highlight key findings, such as:
Aggregated data outputs (e.g., average ice thickness).
#### Include references to sample output files stored in Blob Storage.

Regarding to Accessing Stored Data

### Reflection:
Discuss any challenges faced during implementation and how they were addressed.
The default time zone of the data will make the result not clear, so we have to make the timezone in to Ottawa time zone.