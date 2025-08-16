# attack-radar

## Overview
attack-radar is a web application whose end goal is to visualize the geographical location of the origin of possible cyberattacks across the globe.

## System Components

### Data Pipeline

attack-radar's data pipeline is pretty standard. 
  - Raw data is injested and then placed into a queue for processing. 
  - The data processing layer consumes (processes) events stored in the queue. 
    - This decouples the data injestion & processing layers, allowing both to continue working even if the other is down.
    - It also allows our data processing layer to process data at a constant rate no matter how fast it arrives.
    - Decoupling these services also allows for indepdent scaling and for multiple consumers to access raw data without impacting each other.
  - The data is then stored into an separate container, this data is ready for analytics.
    - Since these queries can be resource intensive and long running, its a good idea to separate this container from others to avoid overloading the entire system.
    - This allows for pre-aggregation, avoiding compolex joins and calculations on each request in the API layer.
  - Data is served by the API layer and then visualized on the frontend. 

#### Data Sources

##### Compromised IP sources

These sources tell attack-radar what IPs are known to have engaged in malicious activities.

  - [FireHOL IP Lists](https://iplists.firehol.org/)
    - A list of all IPs known for engaging in malicious activities. 
  - [Proofpoint Emerging Threats Rules](https://rules.emergingthreats.net/blockrules/compromised-ips.txt) compromised IP list.
    - As the name suggest this list contains compromised IPs and is updated daily.
  - [Feodo Tracker](https://feodotracker.abuse.ch/)
    - Tracks botnet C&C servers
  - [CyberCrime-Tracker](https://cybercrime-tracker.net/)
    - Tracks IP addresses that are known to host malware or engage in cyberattacks.
  - [URLHaus](https://urlhaus.abuse.ch/)
    - Tracks known malicious URLs.
  - [C2 Tracker](https://tracker.viriback.com/)
    - Tracks IP addresses that are known to host malware. 
  - Honeypots
    - These include infrastructure that is hosted by the attack-radar team and other honeypot logs. 
  - Compromised IP scanner
    - An attack-radar subsystem that searches for compromised IPs. 
    
##### IP Abuse Reports  

These sources help attack-radar validate that an IP has been compromised and what kind of attacks it has been engaging in.

  - AbuseIPDB
    - This a database of IPs that have been reported engaging in hacking attemps and other malicious activities.

#### Data Injestion Layer

This layer of the pipeline pulls data from the sources using different methods. 
The data injestion layer runs workers that fetch data from the various sources and place them into a Redis Stream.
The rate at which workers are run can be configured using a crontab

#### Data Processing Layer

This layer consumes events from the Redis Stream and processes them by 
  - Validating that this IP has comitted some sort of malicious activity in the last 7 days.
  - Fetching this IP's location, reported attacks, category of attack and the timestamp of the reported attacks (AbuseIPDB).
  - This data is then written to the storage layer.

#### Storage
### API Layer

### Visualizations 
