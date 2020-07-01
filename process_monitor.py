import sys, time, psutil, csv

class process_monitor():
    # get pid from args
    if len(sys.argv) < 2:
        print ("missing pid arg")
        sys.exit()

    # get process
    pid = int(sys.argv[1])
    p = psutil.Process(pid)
    stopped_num = 10
    cores = 6
    sum = 0

    # monitor process and write data to file
    interval = 1 # polling seconds
    csvfile = open("process_monitor_" + p.name() + '_' + str(pid) + ".csv", "a+")
    with csvfile as f:
        f.write("time,cpu%,mem%\n") # titles
        times = 0
        while True:
            if times < stopped_num:
                current_time = time.strftime('%Y%m%d-%H%M%S',time.localtime(time.time()))
                cpu_percent = p.cpu_percent()/cores
                mem_percent = p.memory_percent()
                line = current_time + ',' + str(cpu_percent) + ',' + str(mem_percent)
                print (line)
                f.write(line + "\n")
                time.sleep(interval)
                times += 1
                sum += cpu_percent
            else:
                cpu_average = round(sum/(times-1), 2)
                print("CPU percent: {} %".format(cpu_average))
                sys.exit()
