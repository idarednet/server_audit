#! /usr/bin/env python3
import json, glob
from collections import defaultdict

html_doc = ""
results = defaultdict(list)

def genHTMLHead():
    global html_doc 
    html_doc = '''<!DOCTYPE html>
<html lang=en>
<head>
    <title>Ansible-Audit-Report</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="css/my-style.css">
    <link rel="stylesheet" href="css/bootstrap-3.3.7.min.css">
</head>
<body class="w3-black">\n'''

#<script src="js/jquery-3.3.1.min.js"></script>
#<link rel="stylesheet" href="css/bootstrap-3.3.7.min.css">
#<script src="js/bootstrap-3.3.7.min.js"></script>

#<div id="Report1" class="tabcontent">
#  <h3>Report1</h3>
#  <p>London is the capital city of England.</p>
#</div>

#<div id="Report2" class="tabcontent">
#  <h3>Report2</h3>
#  <p>Paris is the capital of France.</p> 
#</div>

#<div id="ReportDiff" class="tabcontent">
#  <h3>Report-Diff</h3>
#  <p>Tokyo is the capital of Japan.</p>
#</div>'''

def loadJSONs(json_path):
    '''loadJSON(json_path)
    opens a json formatted file glob (i.e. *.json) from json_path
    and loads it into data var. Also, constructs a list of dicts 
    with task num, command name, and results as key/values.
    '''
    data = []
    report_names = []
    filepath = json_path + '../files/json/192.168.1.175/*.json'
    json_files = glob.glob(filepath)
    print("[+] Loading JSON Files ")
    
    try:
        for json_file in json_files:
            with open(json_file, 'r') as f:
                data.append(json.load(f))
            f.close()
    except Exception as e:
        print(e)
    finally:
        f.close()

    # CREATE LIST WITH NAME OF FILES
    for jf in json_files:
        #jf = jf.replace('.json','').replace('\\','').replace('.','')
        jf = jf.split('./files/json/')[1]
        jf = jf.split('/')[1]
        jf = jf.replace('.json','').replace('\\','').replace('./','')
        report_names.append(jf)
        print("[+] JSON File Loaded - " + jf)

    # CONSTRUCT DICTIONARY WITH LIST OF DICTIONARIES WITH PERTINENT DATA
    i = 0
    for d in data:
        #result = {}
        for task in d['results']:
            result = {"task": task['cmd_idx'] + 1, "command": task['item'], "result": task['stdout_lines']}
            results[report_names[i]].append(result)
        i += 1

def genHTMLContent():
    global html_doc
    # Construct HTML TABLINKS
    html_doc += '<div class="tab">'
    for report in results:
        html_doc += '<button class="tablinks" onclick="openReport(event, \'' + report.upper() +'\')">' + report.upper() + '</button>'
    # TODO: ADD REPORT DIFF TABLINK HERE
    if len(results) > 1:
        html_doc += '<button class="tablinks" onclick="openReport(event, \'DIFF\')">DIFF</button>'
    html_doc += '</div>'

    for report in results:
        html_doc += '<div id="' + report.upper() + '" class="tabcontent">'
        html_doc += '<h3><b>' + report.upper() + '</b></h3>'
        for task in results[report]:
            html_doc += '\t<div class="panel-group" id="accordion">\n'
            html_doc += '\t\t<div class="w3-code w3-black" id="' + task['command'] + '">\n'
            html_doc += '\t\t\t<font color="yellow"><b>COMMAND: </b>' + task['command'] + '</font><br><font color="green">' 
            for stdout_line in task['result']:
                html_doc += stdout_line + '<br>\n'
            html_doc += '\t\t\t</font>\n\t\t</div><br>\n\t</div>\n'
        html_doc += '</div>'
    html_doc += '<div id="DIFF" class="tabcontent">'
    html_doc += '<h3><b>DIFF</b></h3>'
    for taska, taskb in zip(results['report1'], results['report2']):
        if taska != taskb:
            html_doc += '\t<div class="panel-group" id="accordion">\n'
            html_doc += '\t\t<div class="w3-code w3-black" id="' + taska['command'] + '">\n'
            html_doc += '\t\t\t<font color="red"><b>FOUND DIFF: </b>' + taska['command'] + '</font><br><font color="green">' 
            line_cnt = 1
            for linea, lineb in zip(taska['result'], taskb['result']):
                if linea != lineb:
                    html_doc += 'Line Number: ' + str(line_cnt) + '<br>REPORT1 --> ' + linea + '<br>REPORT2 --> ' + lineb + '\n'
                line_cnt += 1
            html_doc += '\t\t\t</font>\n\t\t</div><br>\n\t</div>\n'
    html_doc += '</div>'


def finalizeHTML():
    global html_doc
    html_doc += '''
    <script>
        function openReport(evt, reportName) {
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tabcontent");
            for (i = 0; i < tabcontent.length; i++) {
                tabcontent[i].style.display = "none";
        }
        tablinks = document.getElementsByClassName("tablinks");
        for (i = 0; i < tablinks.length; i++) {
            tablinks[i].className = tablinks[i].className.replace(" active", "");
        }
        document.getElementById(reportName).style.display = "block";
        evt.currentTarget.className += " active";
        }
    </script>
    <button onclick="topFunction()" id="myBtn" title="Go to top">Top</button>
    <script type="text/javascript">
        // When the user scrolls down 20px from the top of the document, show the button
        window.onscroll = function() {scrollFunction()};
        
        function scrollFunction() {
            if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
                document.getElementById("myBtn").style.display = "block";
            } else {
                document.getElementById("myBtn").style.display = "none";
            }
        }
        
        // When the user clicks on the button, scroll to the top of the document
        function topFunction() {
            document.body.scrollTop = 0;
            document.documentElement.scrollTop = 0;
        }
    </script>
</body>
</html>
    '''
    # WRITE HTML Document to a file
    try:
        htmlFile = open("report.html", "w", encoding="utf-8")
        htmlFile.write(html_doc)
    except Exception as e:
        print(e)
    finally:
        htmlFile.close()
        print('(+) HTML FILE GENERATED')

def main():
    loadJSONs('./')
    genHTMLHead()
    genHTMLContent()
    finalizeHTML()

if __name__ == "__main__":
    main()
