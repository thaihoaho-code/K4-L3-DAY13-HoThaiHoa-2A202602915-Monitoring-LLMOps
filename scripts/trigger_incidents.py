# -*- coding: utf-8 -*-
import urllib.request
import time
import subprocess
import threading

BASE_URL = 'http://localhost:8000'

def run_normal_traffic():
    # Ban traffic binh thuong lien tuc de tao baseline dep
    for _ in range(15):
        subprocess.run(['python', 'scripts/load_test.py', '--concurrency', '2'], 
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(5)

def run_incident_load():
    # Ban traffic nang vao dung luc co su co
    subprocess.run(['python', 'scripts/load_test.py', '--concurrency', '4'], 
                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def toggle(incident, state='enable'):
    req = urllib.request.Request(f'{BASE_URL}/incidents/{incident}/{state}', method='POST')
    try:
        urllib.request.urlopen(req)
        print(f'-> {state.upper()}D incident: {incident}')
    except Exception as e:
        print('Error:', e)

# Chay normal traffic song song
threading.Thread(target=run_normal_traffic, daemon=True).start()

print('Cho 15s de tao baseline normal traffic...')
time.sleep(15)

print('\n--- INCIDENT 1: TOOL_FAIL (Sap Database Vector) ---')
toggle('tool_fail', 'enable')
run_incident_load()
toggle('tool_fail', 'disable')

print('\nCho 45s de bieu do on dinh tro lai (Gian cach)...')
for i in range(45, 0, -5):
    print(f'... {i}s')
    time.sleep(5)

print('\n--- INCIDENT 2: COST_SPIKE (LLM output dai, ton token) ---')
toggle('cost_spike', 'enable')
run_incident_load()
toggle('cost_spike', 'disable')

print('\nCho 45s de bieu do on dinh tro lai (Gian cach)...')
for i in range(45, 0, -5):
    print(f'... {i}s')
    time.sleep(5)

print('\n--- INCIDENT 3: RAG_SLOW (Nghen mang noi bo) ---')
toggle('rag_slow', 'enable')
run_incident_load()
toggle('rag_slow', 'disable')

print('\nDONE! Bieu do se hien thi 3 dinh rieng biet ro rang tren truc 10s.')
