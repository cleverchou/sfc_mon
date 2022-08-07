// dataMerge project main.go
package main

import (
	"bufio"
	"fmt"
	"io/ioutil"
	"math"
	"os"
	"strconv"
	"strings"
)

var LineNum int64
var StractTime [110000]int64
var StractValue [110000]float64

func WriterTXT(filename, content string) error {
	// 写入文件
	// 判断文件是否存在
	if _, err := os.Stat(filename); os.IsNotExist(err) {
		fmt.Println(err)
		return err
	}
	fd, err := os.OpenFile(filename, os.O_RDWR|os.O_APPEND, 0666)
	defer fd.Close()
	if err != nil {
		return err
	}
	w := bufio.NewWriter(fd)
	_, err2 := w.WriteString(content)
	if err2 != nil {
		return err2
	} else {
		fmt.Println("write to file:", content)
	}
	w.Flush()
	fd.Sync()
	return nil
}

func readFromTXT(filename string) {
	// 判断文件是否存在
	if _, err := os.Stat(filename); os.IsNotExist(err) {
		fmt.Println(err)
		return
	}
	//记录行数
	LineNum = 0

	lines, err := ioutil.ReadFile(filename)
	if err != nil {
		fmt.Println(err)
	} else {
		contents := string(lines)
		lines := strings.Split(contents, "\n")
		for _, line := range lines {
			//fmt.Println("line=", line)

			term := strings.Fields(line)
			StractTime[LineNum], _ = strconv.ParseInt(term[0], 10, 64)
			StractValue[LineNum], _ = strconv.ParseFloat(term[1], 64)

			//fmt.Println("time=", StractTime[LineNum], " value=", StractValue[LineNum], " lineNum=", LineNum)

			LineNum += 1
		}
	}

	fmt.Println("LineNum=", LineNum)
	return
}

func matchTime(time string) string {
	v := 0.0
	t, _ := strconv.ParseInt(time, 10, 64)
	var i int64
	diff := 1.0e+16

	for i = 0; i < LineNum; i++ {
		if math.Abs(float64(t-StractTime[i])) < diff {
			diff = math.Abs(float64(t - StractTime[i]))
			v = StractValue[i]
		} else if math.Abs(float64(t-StractTime[i])) == diff {
			v = (v + StractValue[i]) / 2.0
		} else {
			fmt.Println("match ", time, " in ", i, "  -->", v)
			break
		}
	}

	return fmt.Sprintf("%f", v)
}

func main() {
	featureFileName := "f_d1m.txt"
	stractFileName := "d2m.txt"
	file, err := os.OpenFile(featureFileName, os.O_RDWR, 0666)
	if err != nil {
		fmt.Println("Open file error!", err)
		return
	}
	defer file.Close()

	readFromTXT(stractFileName)
	buf := bufio.NewReader(file)
	for {
		line, _ := buf.ReadString('\n')
		line = strings.TrimSpace(line)
		if strings.Count(line, "") < 2 {
			return
		}
		time := strings.Fields(line)
		value := matchTime(time[0])
		line = line + "\t " + value + "\n"
		WriterTXT("newFeature.txt", line)
	}
}
