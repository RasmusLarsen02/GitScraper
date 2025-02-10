import requests
import re

org = "ITU-DevOps2025-GROUP-A"
repo = "itu-minitwit"
url = f"https://api.github.com/repos/{org}/{repo}/milestones"

response = requests.get(url)
milestones = response.json()

def extract_time(time_string):
        match = re.search(r"(\d+)h", time_string)
        hours = int(match.group(1)) if match else 0

        match = re.search(r"(\d+)m", time_string)
        minutes = int(match.group(1)) if match else 0

        return hours, minutes



for m in milestones:
    f = open("overview.txt", "r") 
    print(f"Milestone: {m['title']}, ID: {m['number']}")
    if m['title'] in f.read():
        continue
    
    f.close()
    # Replace with actual milestone ID
    milestone_id = m['number']
    issues_url = f"https://api.github.com/repos/{org}/{repo}/issues?milestone={milestone_id}&state=all"

    response = requests.get(issues_url)
    issues = response.json()

    print("Issues in milestone: " + str(len(issues)))

    hours_e = 0
    minutes_e = 0 
    hours_s = 0
    minutes_s = 0

    for issue in issues:
        body = issue.get('body', 'No description')
        timespent_index = body.find('Timespent')
        timeestimate_index = body.find('Time estimated')
        
        spent_string = body[timespent_index:timespent_index+18]
        estimated_string = body[timeestimate_index:timeestimate_index+20]
        
        timespent_hours, timespent_minutes = extract_time(spent_string)
        estimated_hours, estimated_minutes = extract_time(estimated_string)
        
        hours_s += timespent_hours
        minutes_s += timespent_minutes
        
        hours_e += estimated_hours
        minutes_e += estimated_minutes
    f = open("overview.txt", "a") 
    f.write(f"Milestone: {milestones[0].get('title')}\n")
    f.write("Spent: " + str(hours_s) + "h " + str(minutes_s) + "m\nEstimate: " + str(hours_e) + "h " + str(minutes_e) + "m\n")
    f.close()



