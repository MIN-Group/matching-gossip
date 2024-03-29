"""calculate.py是一个用来读取日志文件计算实验指标的脚本，使用到的技术主要是正则表达式
"""
import os
import argparse
import re


parser = argparse.ArgumentParser()
parser.add_argument("-logs_dir", help="your logs dirctory", default="MGossip/logs", type=str)
parser.add_argument("-gossip_interval", help="your gossip interval", default=100000000, type=int)
parser.add_argument("-limit_time", help="your limitTime to test the total packet sent", default=500000000, type=int)
args = parser.parse_args()


def main():
    begin_time = 0
    receive_times = []
    infected_nodes_every_epoch = []
    send_packet_count = 0
    node_count = 0
    create_packet_pattern = r'.*I create a message called (\d+), now time (\d+).*'
    receive_packet_pattern = r'.*I receive a message called (\d+), now time is (\d+).*'
    send_packet_pattern = r'.*I send a packet to ([\d,.]+):(\d+), now time (\d+).*'
    
    for file in os.listdir(args.logs_dir):
        file_path = os.path.join(args.logs_dir, file)
        if not os.path.isdir(file_path) and file.split(".")[-1] == 'log': # 判断是日志文件
            node_count += 1 # 每一个日志文件代表一个网络节点的日志输出
            flag = True 
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f.readlines():
                    # 计算种子节点创造测试消息的起始时间
                    m = re.match(create_packet_pattern, line)
                    if m:
                        begin_time = int(m.group(2))
                        flag = False
                    # 计算每个节点被感染的时间
                    m = re.match(receive_packet_pattern, line)
                    if m and flag:
                        receive_times.append(int(m.group(2)))
                        flag = False
                    # 计算每个节点在限制时间内发送的总数据包 
                    m = re.match(send_packet_pattern, line)
                    if m:
                        now_time = m.group(3)
                        if int(now_time) >= begin_time + args.limit_time:
                            break
                        send_packet_count += 1
    # 以下计算各个周期内被感染的节点数
    receive_times.sort()
    count = 1
    interval = args.gossip_interval
    time_limit = begin_time + interval
    for each_time in receive_times:
        if each_time >= time_limit:
            infected_nodes_every_epoch.append(count)
            count = 1
            time_limit += interval
        else:
            count += 1
    infected_nodes_every_epoch.append(count)
    # for file in os.listdir(args.logs_dir):
    #     file_path = os.path.join(args.logs_dir, file)
    #     if not os.path.isdir(file_path) and file.split(".")[-1] == 'log':
    #         with open(file_path, "r", encoding="utf-8") as f:
    #             for line in f.readlines():
    #                 m = re.match(send_packet_pattern, line)
    #                 if m:
    #                     now_time = m.group(3)
    #                     if int(now_time) >= begin_time + args.limit_time:
    #                         break
    #                     send_packet_count += 1
    convergence_time = receive_times[-1] - begin_time
    print(f"node convergence rate: {(len(receive_times) + 1) / node_count:.2f}")
    print(f"convergence time: {convergence_time} ns")
    print(f"total packet the network send: {send_packet_count}")
    print(f"infected nodes every gossip epoch: {infected_nodes_every_epoch}")
    
    
if __name__ == '__main__':
    main()    