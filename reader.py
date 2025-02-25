import requests
import matplotlib.pyplot as plt
import re
from flask import Flask, request, jsonify, send_file
import os



app = Flask(__name__)

BANNER = """
==========================================
  GIT SCRAPER CONTAINER STARTED!
==========================================

TO RUN, USE THIS COMMAND:

curl -L \\
    -H "Authorization: token <GITHUB_TOKEN>" \\
    "http://<YOUR_IP>:8080/generate-chart?org={org}&repo={repo}" \\
    -o chart.png

==========================================
"""

print(BANNER)

def extract_time(time_string):
        match = re.search(r"(\d+)h", time_string)
        hours = int(match.group(1)) if match else 0

        match = re.search(r"(\d+)m", time_string)
        minutes = int(match.group(1)) if match else 0

        return hours, minutes
    
def draw_plot(milestones, est, spt, repo): 
    w = 0.4
    x1 = [i for i in range(len(milestones))]
    x2 = [i+w for i in x1]

    print(x1)
    plt.bar(x1, est, w, label = 'Estimated')
    plt.bar(x2, spt, w, label = 'Spent')
    plt.xlabel('Milestones')
    plt.ylabel('Hours')
    plt.title(f'Time Chart for {repo}')

    plt.xticks([i+w/2 for i in x1], milestones)

    plt.legend()
    
    file = f"{repo}_time_chart.png"
    plt.savefig(file, dpi=300, bbox_inches="tight") 
    plt.close()
    
    return file


@app.route('/generate-chart', methods=['GET'])
def generate_chart(): 
    org = request.args.get("org")
    repo = request.args.get("repo")

    github_token = request.headers.get("Authorization")

    if github_token and not github_token.startswith("token "):
        github_token = f"token {github_token}"

    if not org or not repo:
        return jsonify({"error": "Missing organization or repository"}), 400
    
    url = f"https://api.github.com/repos/{org}/{repo}/milestones?state=all&sort=number"

    headers = {"Authorization": github_token} if github_token else {}

    response = requests.get(url, headers=headers)
    
    if response.status_code != 200: 
        return jsonify({"error": "Failed to get milestones"}), 400
    
    milestones = response.json()
        
    titles = []
    estimates = []
    spent  = []

    for m in milestones:
        titles.append(m['title'])
        
        milestone_id = m['number']
        issues_url = f"https://api.github.com/repos/{org}/{repo}/issues?milestone={milestone_id}&state=all"
        response = requests.get(issues_url)
        issues = response.json()

        hours_e = 0
        hours_s = 0

        for issue in issues:
            
            body = issue.get("body", "")
            if not body:
                continue
        
            timespent_index = body.find('Timespent')
            timeestimate_index = body.find('Time estimated')
            
            spent_string = body[timespent_index:timespent_index+20]
            estimated_string = body[timeestimate_index:timeestimate_index+25]
            
            timespent_hours, timespent_minutes = extract_time(spent_string)
            estimated_hours, estimated_minutes = extract_time(estimated_string)
            
            hours_s += timespent_hours + timespent_minutes/60
            hours_e += estimated_hours + estimated_minutes/60
            
        spent.append(hours_s)  
        estimates.append(hours_e)  
    chart_filename = draw_plot(titles, estimates, spent, repo)  
    
    return send_file(chart_filename, mimetype='image/png')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)