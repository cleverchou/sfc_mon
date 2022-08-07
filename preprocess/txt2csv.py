import csv
with open('file.csv', 'w+',newline='') as csvfile:
    spamwriter = csv.writer(csvfile, dialect='excel')
    # 读要转换的txt文件，文件每行各词间以@@@字符分隔
    with open('f_d1cm.txt', 'r',encoding='utf-8') as filein:
        for line in filein:
            line_list = line.strip('\n').split('\t')
            spamwriter.writerow(line_list)