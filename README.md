## Flask API implementation - Event management project

### Introduction
This is my project for practicing API functionality, aimed at managing event information, integrating with a cloud MongoDB database and Google Calendar.   
The user can use this API with basic functionalities to achieve these tasks:  
* Get events: You can get all events or events by conditions based on different dimensions. 
* Get locations: You can get all location with matching capability for the event with specified number of attendees. 
* Create events: You can create an event by sending event data in JSON format. After creating an event, the event can be found in cloud MongoDB database and Google Calendar. 
* Create spaces: You can create a space by sending space data in JSON format. After creating a space, the space can be found in cloud MongoDB database. 

Noted that this API is just for practice, the events and spaces are all fabricated. 

### Functionality in detail
For step-by-step introduction, please find [this slide](https://docs.google.com/presentation/d/16mao4MVB9rA3hJzdqOauKIpuAZC90q84/edit?usp=drive_link&ouid=115877165825501589225&rtpof=true&sd=true) for functionalities in detail. 

### Run this project 
This API project is built in Python Flask, and saved in image on Dockerhub.   
To run this project, you have to   
1. Install Docker
2. Pull the latest version of [this docker image](https://hub.docker.com/r/alionking821/calendar_api_img/)
3. Run the following command on cmd line. 

```
docker run -v /path/to/the/mongodb_access.txt:/event_site_project_access/mongodb_access.txt -v /path/to/the/service_account_credentials.json:/event_site_project_access/service_account_credentials.json -d -p 80:3000 --name set_your_container_name alionking821/calendar_api_img:version_tag
```

