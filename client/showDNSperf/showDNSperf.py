def showPerf():
    elapsed = []
    qPersecond = []
    elapsedE = 0
    perE = 0
    num = 0

    file = open("sample.txt")
    while 1:
        line = file.readline()
        if not line:
            break
        if line in ['\n', '\r\n', '\r'] or line.strip() == "":
            continue
        else:
            if 'Elapsed ' in line:
                elapsedE = 1
                etmp = line.split(":", 1)
                elapsed.append(etmp[1].strip())
            elif 'Per ' in line:
                perE = 1
                pertemp = line.split(":", 1)
                qPersecond.append(pertemp[1].strip())
        if elapsedE+perE == 2:
            elapsedE = 0
            perE = 0
            num += 1

    print(num)
    file = open('elapsed.txt', mode='a')
    for e in elapsed:
        print(e)
        file.write(e
                   + " ")
    file.close()
    file = open('qps.txt', mode='a')
    for q in qPersecond:
        print(q)
        file.write(q + " ")
    file.close()

if __name__ == "__main__":
    showPerf()
