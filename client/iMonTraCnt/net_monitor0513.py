#!/usr/bin/python
#
# net_monitor.py Aggregates incoming network traffic
# outputs source ip, destination ip, the number of their network traffic, the size of their network traffic,and current time
# how to use : net_monitor.py <net_interface> IP
# 
# Copyright (c) 2020 cleverchou

from bcc import BPF
import time
from ast import literal_eval
from ctypes import *
import ctypes as ct
import sys
import socket
import os
import struct
#from prometheus_client import Gauge,start_http_server
from influxdb import InfluxDBClient




def help():
    print("execute: python3 {0} ens33 172.17.0.2(influxDBIP)".format(sys.argv[0]))
    exit(1)

if len(sys.argv) != 3:
    help()
elif len(sys.argv) == 3:
    INTERFACE = sys.argv[1]
    InfluxDBIP = sys.argv[2]   #IP2int

bpf_text = """

#include <uapi/linux/ptrace.h>
#include <net/sock.h>
#include <bcc/proto.h>
#include <linux/bpf.h>

#define IP_TCP 6
#define IP_UDP 17
#define IP_ICMP 1
#define ETH_HLEN 14

struct value {
    long num;
    long size;
    u64 tstart;
    u64 tend;
    long maxSize;
    long minSize;
    long pktNopayLoad;
}; 

struct tupleKey {
    u32 saddr;
    u32 daddr;
    long sport;
    long dport;
    u8 protocol;
};


BPF_HASH(stats, struct tupleKey, struct value); 

int packet_monitor(struct __sk_buff *skb) {
    u8 *cursor = 0;
    struct tupleKey tkey = {};
    long one = 1;
    long size = 0;
    u8 pktNoPayLoad = 0;

    struct ethernet_t *ethernet = cursor_advance(cursor, sizeof(*ethernet));
    struct ip_t *ip = cursor_advance(cursor, sizeof(*ip));
    tkey.saddr = ip -> src;
    tkey.daddr = ip -> dst;

    if (ip->nextp == IP_TCP) {
        tkey.protocol = IP_TCP;
        struct tcp_t *tcp = cursor_advance(cursor, sizeof(*tcp));
        tkey.sport = tcp->src_port;
        tkey.dport = tcp->dst_port;
        size = ip->tlen - (ip->hlen << 2) - (tcp->offset << 2); //ip->tlen - ip_header_length - tcp_header_length
    }else if (ip -> nextp == IP_UDP){
        tkey.protocol = IP_UDP;
        struct udp_t *udp = cursor_advance(cursor, sizeof(*udp));
        tkey.sport = udp->sport;
        tkey.dport = udp->dport;
        size = udp->length;
    }else if (ip -> nextp == IP_ICMP){
        tkey.protocol = IP_ICMP;
        tkey.sport = 0;
        tkey.dport = 0;
        size = 0 ;
    }else{ 
        return 0; 
    }

    if(size == 0 )
        pktNoPayLoad++;
    struct value* tvalue = stats.lookup(&tkey); 
    if (tvalue){  // check if this map exists, update values
        tvalue->tend = bpf_ktime_get_ns();
        tvalue->num += 1;
        tvalue->size += size;
        if(tvalue->maxSize < size)
            tvalue->maxSize = size ;
        if(tvalue->minSize > size && size > 0)
            tvalue->minSize = size ;
        tvalue->pktNopayLoad = pktNoPayLoad;
    }else{        // if the map for the key doesn't exist, create one
        u64 ts = bpf_ktime_get_ns(); 
        struct value tvalueInit = {one,size,ts,ts,size,size,pktNoPayLoad};
        stats.update(&tkey, &tvalueInit);
    }

    //bpf_trace_printk("pass_value = %u",pass_value);

    return -1;
}

"""

OUTPUT_INTERVAL = 10
#NetMonPort = 80
bpf = BPF(text=bpf_text)
function_skb_matching = bpf.load_func("packet_monitor", BPF.SOCKET_FILTER)
BPF.attach_raw_socket(function_skb_matching, INTERFACE)
#print(INTERFACE)

    # retrieeve packet_cnt map
stats = bpf.get_table('stats')    # retrieeve packet_cnt map
#bpf.trace_print()


def decimal_to_human(input_value):
    input_value = int(input_value)
    if input_value == 0:
        return '0.0.0.0'
    #print("input_value = %d "%input_value)
    hex_value = hex(input_value)[2:]
    #print("hex_value "+hex_value)
    pt3 = literal_eval((str('0x'+str(hex_value[-2:]))))
    pt2 = literal_eval((str('0x'+str(hex_value[-4:-2]))))
    pt1 = literal_eval((str('0x'+str(hex_value[-6:-4]))))
    pt0 = literal_eval((str('0x'+str(hex_value[-8:-6]))))
    result = str(pt0)+'.'+str(pt1)+'.'+str(pt2)+'.'+str(pt3)
    #print("result = %s"%result)

    return result

#start_http_server(NetMonPort)
client = InfluxDBClient(InfluxDBIP, 8086, 'root', '', 'netmonitor')

try:
    #npkt = Gauge(name='npkt', documentation='count of packets',labelnames=['SIP' ,'DIP','Sport','Dport','protocol'])
    #spkt = Gauge(name='spkt', documentation='size of packets',labelnames=['SIP' ,'DIP','Sport','Dport','protocol'])
    #npktAll = Gauge(name='npktall', documentation='count ALL of packets')
    #spktAll = Gauge(name='spktall', documentation='size ALL of packets')
    #maxPkt =  Gauge(name='maxPkt',  documentation='MAX size of packets')
    #minPkt =  Gauge(name='minPkt',  documentation='MIN size of packets')
    #avgPkt =  Gauge(name='avgPkt',  documentation='average size of packets')
    #duration = Gauge(name='duration', documentation='duration time')

    nAllSend,sAllSend,nAllRec,sAllRec = 0.0, 0.0, 0.0, 0.0
    maxpSend,minpSend,maxpRec,minpRec = 0.0, 9999.0, 0.0, 9999.0
    dutSend,dutRec = 0.0, 0.0
    initFlag = 0
    t0 = time.time()

    while True :
        time.sleep(OUTPUT_INTERVAL)
        
        for k,v in stats.items():
            print("SIP=%s_%d,DIP=%s,SPort=%d,DPort=%d,l4P=%d:Num=%d,Size=%d,MaxPkt=%d,MinPkt=%d,Dutime=%d"%(decimal_to_human(k.saddr),k.saddr,decimal_to_human(k.daddr),k.sport,k.dport,k.protocol,v.num,v.size,v.maxSize,v.minSize,( v.tend-v.tstart ) ) )
            initFlag = 1
            if k.saddr == 0 or k.daddr == 0 :
                continue;

            if k.saddr == 3232235531 :
                nAllSend += v.num
                sAllSend += v.size
                if maxpSend < v.maxSize :
                    maxpSend = v.maxSize
                if minpSend > v.minSize :
                    minpSend = v.minSize
                dutSend += v.tend-v.tstart
            else :
                nAllRec += v.num
                sAllRec += v.size
                if maxpRec < v.maxSize :
                    maxpRec = v.maxSize
                if minpRec > v.minSize :
                    minpRec = v.minSize
                dutRec +=  v.tend-v.tstart
            
        stats.clear()      
        t1 = time.time()
        if t1 - t0 >= OUTPUT_INTERVAL and initFlag == 1:
            t0 = t1
            if nAllSend > 0:
                avgPktSend = sAllSend/nAllSend
                durationSend = dutSend/nAllSend
            else : 
                avgPktSend = 0
                durationSend = 0
            if minpSend == 9999.0 :
                minpSend = 0.0

            if nAllRec > 0:
                avgPktRec = sAllRec/nAllRec
                durationRec = dutRec/nAllRec
            else : 
                avgPktRec = 0
                durationRec = 0
            if minpRec == 9999.0 :
                minpRec = 0.0
            #duration pktAvg pktMax pktMin pktNum pktSize
            json_body = [
                {
                     "measurement": "feature",
                     "tags": {
                                 "sfc": "s123"
                      },
                      #"time": t1,
                      "fields": {
                      "durationSend": int(durationSend),
                      "pktAvgSend":   int(avgPktSend),
                      "pktMaxSend":   int(maxpSend),
                      "pktMinSend":   int(minpSend),
                      "pktNumSend":   int(nAllSend),
                      "pktSizeSend":  int(sAllSend),

                      "durationRec": int(durationRec),
                      "pktAvgRec":   int(avgPktRec),
                      "pktMaxRec":   int(maxpRec),
                      "pktMinRec":   int(minpRec),
                      "pktNumRec":   int(nAllRec),
                      "pktSizeRec":  int(sAllRec)
                      }
                }
            ]
            client.write_points(json_body)
            print("push to influxDB")

            nAllSend,sAllSend,nAllRec,sAllRec = 0.0, 0.0, 0.0, 0.0
            maxpSend,minpSend,maxpRec,minpRec = 0.0, 9999.0, 0.0, 9999.0
            dutSend,dutRec = 0.0, 0.0
            initFlag = 0

except KeyboardInterrupt:
    sys.stdout.close()
    pass
