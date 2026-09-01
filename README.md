# attack-radar

## Overview
attack-radar is a web application whose end goal is to visualize the geographical location of the origin of possible cyberattacks across the globe.

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

This data is processed in the following manner: 
  - Validating that this IP has comitted some sort of malicious activity in the last 7 days.
  - Fetching this IP's location, reported attacks, category of attack and the timestamp of the reported attacks (AbuseIPDB).
  - This data is then written to a PostGresql database.