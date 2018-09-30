#!/usr/bin/env python
#coding=utf8
import time
import psutil
import sqlite3
import os
db_name=''
def myencode(s):
        ans='a'
        for i in range(len(s)):
                ans+=str(hex(ord(s[i])))
        return ans
def mydecode(s):
        ans=''
        for i in range(len(s)/4):
                ans+=chr(eval(s[i*4+1:(i+1)*4+1]))
        return ans
def create_db(m,flag):
        if flag==False:
                conn = sqlite3.connect(db_name)
                c = conn.cursor()
                c.execute('''CREATE TABLE subsact (time FLOAT PRIMARY KEY ,user char(50),cpu_per CHAR(20), vm_percent CHAR(20), disk_total CHAR(20),disk_used CHAR(20),disk_per CHAR(20), net_bytes_sent CHAR(20),net_bytes_recv CHAR(20),proc_pids CHAR(20))''')
                c.execute('''CREATE TABLE cpu (time FLOAT PRIMARY KEY ,num char(10), per_dict char(100), ctx_switches char(20),interrupts char(20),soft_interrupts char(20),syscalls char(20),freq char(20))''')
                c.execute('''CREATE TABLE memory (time FLOAT PRIMARY KEY ,vm_total char(20), vm_available char(20), vm_percent char(20),vm_used char(20),vm_free char(20),sm_total char(20), sm_percent char(20),sm_used char(20),sm_free char(20))''')
                c.execute('''CREATE TABLE net (time FLOAT PRIMARY KEY ,bytes_sent char(20), bytes_recv char(20), packets_sent char(20),packets_recv char(20),errin char(20),errout char(20), dropin char(20),dropout char(20))''')
                for i in m.phy_disk_list:
                        c.execute("CREATE TABLE "+i+" (time FLOAT PRIMARY KEY ,read_count char(20),write_count char(20),read_bytes char(20),write_bytes char(20),read_time char(20),write_time char(20))")
                for i in m.disk_list:
                        c.execute("CREATE TABLE "+i+" (time FLOAT PRIMARY KEY ,total char(20),used char(20),free char(20),percent char(20))")
                c.execute('''CREATE TABLE process (time DOUBLE PRIMARY KEY ,pids char(20),pids_list char(2000))''')
                c.execute('''CREATE TABLE userlist (username CHAR(100) PRIMARY KEY ,password char(100))''')
                admin="admin"
                c.execute('INSERT INTO userlist(username,password) VALUES (?,?)',[admin,admin])
                conn.commit()
                conn.close()
class monitor:
        def __init__(self):
                self.cpu_num=psutil.cpu_count()
                self.cpu_corefreq=psutil.cpu_freq().max
                mid1=psutil.disk_partitions(all=True)
                mid2=psutil.disk_io_counters(perdisk=True)
                self.disk_num=len(mid1)
                self.phy_disk_num=len(mid2)
                self.disk_list=[]
                for i in range (self.disk_num):
                        self.disk_list.append(myencode(mid1[i].device))
                self.phy_disk_list=[]
                for key in mid2:
                        self.phy_disk_list.append(myencode(key))
                self.user= psutil.users()[0].name
                print self.disk_list
                print self.phy_disk_list
        def getsubsact(self):
                cpu_per=psutil.cpu_percent()
                vm_percent=psutil.virtual_memory().percent
                disk_per=0.0
                mid1=0.0
                mid2=0.0
                disk_total=0
                disk_used=0
                for i in self.disk_list:
                        j=mydecode(i)
                        disk_total+=psutil.disk_usage(j).total
                        disk_used+=psutil.disk_usage(j).used
                mid1+=disk_total
                mid2+=disk_used
                disk_per=mid2/mid1
                net_bytes_sent=psutil.net_io_counters().bytes_sent
                net_bytes_recv=psutil.net_io_counters().bytes_recv
                proc_pids=len(psutil.pids())
                conn = sqlite3.connect(db_name)
                c = conn.cursor()
                c.execute('INSERT INTO subsact(time,user,cpu_per,vm_percent,disk_total,disk_used,disk_per,disk_used,net_bytes_sent,net_bytes_recv,proc_pids) VALUES (?,?,?,?,?,?,?,?,?,?,?)', [self.key,self.user,str(cpu_per),str(vm_percent),str(disk_total),str(disk_used),str(disk_per),str(disk_used),str(net_bytes_sent),str(net_bytes_recv),str(proc_pids)])
                conn.commit()
                conn.close()
        def getTime(self):
                self.key=time.time()
        def getCPU(self):
                self.cpu_num
                cpu_per_dict=str(psutil.cpu_percent(percpu=True))
                cpu_ctx_switches=psutil.cpu_stats().ctx_switches
                cpu_interrupts=psutil.cpu_stats().interrupts
                cpu_soft_interrupts=psutil.cpu_stats().soft_interrupts
                cpu_syscalls=psutil.cpu_stats().syscalls
                cpu_freq=psutil.cpu_freq().current
                conn = sqlite3.connect(db_name)
                c = conn.cursor()
                c.execute('INSERT INTO cpu(time,num,per_dict,ctx_switches,interrupts,soft_interrupts,syscalls,freq) VALUES (?,?,?,?,?,?,?,?)', [self.key,str(self.cpu_num),str(cpu_per_dict),str(cpu_ctx_switches),str(cpu_interrupts),str(cpu_soft_interrupts),str(cpu_syscalls),str(cpu_freq)])
                conn.commit()
                conn.close()
        def getMemory(self):
                vm_total=psutil.virtual_memory().total
                vm_available=psutil.virtual_memory().available
                vm_percent=psutil.virtual_memory().percent
                vm_used=psutil.virtual_memory().used
                vm_free=psutil.virtual_memory().free
                sm_total=psutil.swap_memory().total
                sm_percent=psutil.swap_memory().percent
                sm_used=psutil.swap_memory().used
                sm_free=psutil.swap_memory().free
                conn = sqlite3.connect(db_name)
                c = conn.cursor()
                c.execute('INSERT INTO memory(time,vm_total,vm_available,vm_percent,vm_used,vm_free,sm_total,sm_percent,sm_used,sm_free) VALUES (?,?,?,?,?,?,?,?,?,?)', [self.key,str(vm_total),str(vm_available),str(vm_percent),str(vm_used),str(vm_free),str(sm_total),str(sm_percent),str(sm_used),str(sm_free)])
                conn.commit()
                conn.close()
        def getDisk(self):
                disk_io_dict=psutil.disk_io_counters(perdisk=True)
                for i in self.phy_disk_list:
                        j=mydecode(i)
                        disk_read_count=disk_io_dict[j].read_count
                        disk_write_count=disk_io_dict[j].write_count
                        disk_read_bytes=disk_io_dict[j].read_bytes
                        disk_write_bytes=disk_io_dict[j].write_bytes
                        disk_read_time=disk_io_dict[j].read_time
                        disk_write_time=disk_io_dict[j].write_time
                        conn = sqlite3.connect(db_name)
                        c = conn.cursor()
                        c.execute('INSERT INTO '+i+' (time,read_count,write_count,read_bytes,write_bytes,read_time,write_time) VALUES (?,?,?,?,?,?,?)', [self.key,str(disk_read_count),str(disk_write_count),str(disk_read_bytes),str(disk_write_bytes),str(disk_read_time),str(disk_write_time)])
                        conn.commit()
                        conn.close()
                disk_dict=str(psutil.disk_partitions())
                for i in self.disk_list:
                        j=mydecode(i)
                        disk_total=psutil.disk_usage(j).total
                        disk_used=psutil.disk_usage(j).used
                        disk_free=psutil.disk_usage(j).free
                        disk_percent=psutil.disk_usage(j).percent
                        conn = sqlite3.connect(db_name)
                        c = conn.cursor()
                        c.execute('INSERT INTO '+i+'(time,total,used,free,percent) VALUES (?,?,?,?,?)', [self.key,str(disk_total),str(disk_used),str(disk_free),str(disk_percent)])
                        conn.commit()
                        conn.close()
        def getNet(self):
                net_bytes_sent=psutil.net_io_counters().bytes_sent
                net_bytes_recv=psutil.net_io_counters().bytes_recv
                net_packets_sent=psutil.net_io_counters().packets_sent
                net_packets_recv=psutil.net_io_counters().packets_recv
                net_errin=psutil.net_io_counters().errin
                net_errout=psutil.net_io_counters().errout
                net_dropin=psutil.net_io_counters().dropin
                net_dropout=psutil.net_io_counters().dropout
                conn = sqlite3.connect(db_name)
                c = conn.cursor()
                c.execute('INSERT INTO net(time,bytes_sent,bytes_recv,packets_sent,packets_recv,errin,errout,dropin,dropout) VALUES (?,?,?,?,?,?,?,?,?)', [self.key,str(net_bytes_sent),str(net_bytes_recv),str(net_packets_sent),str(net_packets_recv),str(net_errin),str(net_errout),str(net_dropin),str(net_dropout)])
                conn.commit()
                conn.close()
        def getProcess(self):
                proc_pids=len(psutil.pids())
                proc_pids_list=str(psutil.pids())
                conn = sqlite3.connect(db_name)
                c = conn.cursor()
                c.execute('INSERT INTO process(time,pids,pids_list) VALUES (?,?,?)', [self.key,str(proc_pids),proc_pids_list])
                conn.commit()
                conn.close()
        def mainloop(self):
                self.getTime()
                self.getsubsact()
                self.getCPU()
                self.getMemory()
                self.getDisk()
                self.getNet()
                self.getProcess()
                print self.key
                time.sleep(5)
if __name__ == "__main__":
        m=monitor()
        db_name=m.user
        db_name+='db.db'
        create_db(m,os.path.exists(db_name))
        while(True):
                m.mainloop()
                
        
