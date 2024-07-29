from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
import random
from collections import deque, defaultdict
import subprocess

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mp3'}

# Utility function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Cache replacement algorithms with additional metrics
def lru_cache_simulation(file_size, cache_size):
    cache = deque(maxlen=cache_size)
    hit, miss, evictions = 0, 0, 0
    for _ in range(file_size):
        page = random.randint(0, 100)
        if page in cache:
            cache.remove(page)
            cache.append(page)
            hit += 1
        else:
            if len(cache) >= cache_size:
                evictions += 1
            cache.append(page)
            miss += 1
    hit_rate = hit / file_size
    miss_rate = miss / file_size
    eviction_rate = evictions / file_size
    latency_reduction = hit_rate * 0.01  # example calculation
    memory_usage = len(cache) / cache_size
    cache_utilization = len(cache) / cache_size
    bandwidth_saving = hit_rate * 0.02  # example calculation
    return hit_rate, miss_rate, eviction_rate, latency_reduction, memory_usage, cache_utilization, bandwidth_saving, "O(1)"

def lfu_cache_simulation(file_size, cache_size):
    cache = defaultdict(int)
    hit, miss, evictions = 0, 0, 0
    for _ in range(file_size):
        page = random.randint(0, 100)
        if page in cache:
            cache[page] += 1
            hit += 1
        else:
            if len(cache) >= cache_size:
                evictions += 1
                lfu_page = min(cache, key=cache.get)
                del cache[lfu_page]
            cache[page] = 1
            miss += 1
    hit_rate = hit / file_size
    miss_rate = miss / file_size
    eviction_rate = evictions / file_size
    latency_reduction = hit_rate * 0.01
    memory_usage = len(cache) / cache_size
    cache_utilization = len(cache) / cache_size
    bandwidth_saving = hit_rate * 0.02
    return hit_rate, miss_rate, eviction_rate, latency_reduction, memory_usage, cache_utilization, bandwidth_saving, "O(log n)"

def arc_cache_simulation(file_size, cache_size):
    t1, t2 = deque(maxlen=cache_size // 2), deque(maxlen=cache_size // 2)
    b1, b2 = deque(maxlen=cache_size // 2), deque(maxlen=cache_size // 2)
    hit, miss, evictions = 0, 0, 0
    for _ in range(file_size):
        page = random.randint(0, 100)
        if page in t1:
            t1.remove(page)
            t2.append(page)
            hit += 1
        elif page in t2:
            hit += 1
        elif page in b1 or page in b2:
            miss += 1
        else:
            if len(t1) + len(b1) == cache_size // 2:
                if len(t1) < cache_size // 2:
                    b1.pop()
                else:
                    t1.popleft()
            if len(t1) + len(b1) < cache_size // 2:
                if len(t1) + len(b1) + len(t2) + len(b2) >= cache_size:
                    if len(t1) + len(b1) + len(t2) + len(b2) == cache_size:
                        b2.pop()
                    else:
                        t2.popleft()
            t1.append(page)
            miss += 1
            evictions += 1
    hit_rate = hit / file_size
    miss_rate = miss / file_size
    eviction_rate = evictions / file_size
    latency_reduction = hit_rate * 0.01
    memory_usage = (len(t1) + len(t2)) / cache_size
    cache_utilization = (len(t1) + len(t2)) / cache_size
    bandwidth_saving = hit_rate * 0.02
    return hit_rate, miss_rate, eviction_rate, latency_reduction, memory_usage, cache_utilization, bandwidth_saving, "O(1)"

def wtiny_lfu_cache_simulation(file_size, cache_size):
    cache = set()
    frequency = defaultdict(int)
    hit, miss, evictions = 0, 0, 0
    for _ in range(file_size):
        page = random.randint(0, 100)
        if page in cache:
            frequency[page] += 1
            hit += 1
        else:
            if len(cache) >= cache_size:
                evictions += 1
                lfu_page = min(frequency, key=frequency.get)
                cache.remove(lfu_page)
                del frequency[lfu_page]
            cache.add(page)
            frequency[page] = 1
            miss += 1
    hit_rate = hit / file_size
    miss_rate = miss / file_size
    eviction_rate = evictions / file_size
    latency_reduction = hit_rate * 0.01
    memory_usage = len(cache) / cache_size
    cache_utilization = len(cache) / cache_size
    bandwidth_saving = hit_rate * 0.02
    return hit_rate, miss_rate, eviction_rate, latency_reduction, memory_usage, cache_utilization, bandwidth_saving, "O(1)"

def random_cache_simulation(file_size, cache_size):
    cache = set()
    hit, miss, evictions = 0, 0, 0
    for _ in range(file_size):
        page = random.randint(0, 100)
        if page in cache:
            hit += 1
        else:
            if len(cache) >= cache_size:
                evictions += 1
                cache.pop()
            cache.add(page)
            miss += 1
    hit_rate = hit / file_size
    miss_rate = miss / file_size
    eviction_rate = evictions / file_size
    latency_reduction = hit_rate * 0.01
    memory_usage = len(cache) / cache_size
    cache_utilization = len(cache) / cache_size
    bandwidth_saving = hit_rate * 0.02
    return hit_rate, miss_rate, eviction_rate, latency_reduction, memory_usage, cache_utilization, bandwidth_saving, "O(1)"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_simulator', methods=['POST'])
def run_simulator():
    if 'input_file' not in request.files:
        return jsonify(error="No file part")
    
    file = request.files['input_file']
    if file.filename == '':
        return jsonify(error="No selected file")
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        file_size_kb = os.path.getsize(file_path) // 1024  # in KB
        file_size_mb = file_size_kb / 1024  # in MB

        cache_size = int(request.form['cache_size'])
        algorithm_type = request.form['algorithm_type']

        if algorithm_type == 'LRU':
            hit_rate, miss_rate, eviction_rate, latency_reduction, memory_usage, cache_utilization, bandwidth_saving, time_complexity = lru_cache_simulation(file_size_kb, cache_size)
        elif algorithm_type == 'LFU':
            hit_rate, miss_rate, eviction_rate, latency_reduction, memory_usage, cache_utilization, bandwidth_saving, time_complexity = lfu_cache_simulation(file_size_kb, cache_size)
        elif algorithm_type == 'ARC':
            hit_rate, miss_rate, eviction_rate, latency_reduction, memory_usage, cache_utilization, bandwidth_saving, time_complexity = arc_cache_simulation(file_size_kb, cache_size)
        elif algorithm_type == 'WTinyLFU':
            hit_rate, miss_rate, eviction_rate, latency_reduction, memory_usage, cache_utilization, bandwidth_saving, time_complexity = wtiny_lfu_cache_simulation(file_size_kb, cache_size)
        elif algorithm_type == 'Random':
            hit_rate, miss_rate, eviction_rate, latency_reduction, memory_usage, cache_utilization, bandwidth_saving, time_complexity = random_cache_simulation(file_size_kb, cache_size)
        else:
            return jsonify(error="Unknown algorithm type")

        # Generate graph
        subprocess.run(['python', 'generate_complexity_graphs.py'])

        return jsonify(
            file_size_mb=file_size_mb,
            hit_rate=hit_rate,
            miss_rate=miss_rate,
            eviction_rate=eviction_rate,
            latency_reduction=latency_reduction,
            memory_usage=memory_usage,
            cache_utilization=cache_utilization,
            bandwidth_saving=bandwidth_saving,
            time_complexity=time_complexity
        )
    else:
        return jsonify(error="File not allowed")

@app.route('/result')
def result():
    file_size_mb = request.args.get('file_size_mb', type=float)
    hit_rate = request.args.get('hit_rate', type=float)
    miss_rate = request.args.get('miss_rate', type=float)
    eviction_rate = request.args.get('eviction_rate', type=float)
    latency_reduction = request.args.get('latency_reduction', type=float)
    memory_usage = request.args.get('memory_usage', type=float)
    cache_utilization = request.args.get('cache_utilization', type=float)
    bandwidth_saving = request.args.get('bandwidth_saving', type=float)
    time_complexity = request.args.get('time_complexity')

    return render_template(
        'result.html',
        file_size_mb=file_size_mb,
        hit_rate=hit_rate,
        miss_rate=miss_rate,
        eviction_rate=eviction_rate,
        latency_reduction=latency_reduction,
        memory_usage=memory_usage,
        cache_utilization=cache_utilization,
        bandwidth_saving=bandwidth_saving,
        time_complexity=time_complexity
    )

if __name__ == '__main__':
    app.run(debug=True)
