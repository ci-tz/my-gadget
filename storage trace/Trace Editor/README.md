# Trace Editor

Please keep in mind that **every trace must be preprocessed first** before getting into script's another functionalities.

To run, access the `trace-editor.py` in the root directory.

Before running, create 2 symlinks/folders inside this directory:
`./in`: contains all input files
`./out`: contains all output files

The scripts will take every input and produce every output to those directories.


The target format of the trace is the same as `DiskSim` and `MQSim`，which is defined in `The DiskSim Simulation Environment Version 4.0 Reference Manual`.

The format is as follows:

1. **Request arrival time**: Float [nonnegative milliseconds] specifying the time the request “arrives” relative to the start of the simulation (at time 0.0).
2.	**Device number**: [ Not used ]Integer specifying the device number (i.e., the storage component that the request accesses). 
3.	**Block number**: Integer [nonnegative] specifying the ﬁrst device address of the request. The value is speciﬁed in the access unit of the logical device (**sector number** for now).
4.	**Request size**: Integer [positive] specifying the size of the request in device blocks(**the number of sectors** that the request involved).
5.	**Request ﬂags**: [0 for write, 1 for read]

## List of commands:

### 1.Preprocess a trace or traces inside a directory.
* Type of traces:
  * Microsoft Server Trace
  * BlkReplay's blktrace
  * Unix's blktrace
  * Systor '17 Traces

**1.Microsoft Server Trace**

[SNIA - Storage Networking Industry Association: IOTTA Repository Home](http://iotta.snia.org/traces/block-io/158)

The head of the trace is the header, for example:

    BeginHeader    
              DiskRead,  TimeStamp,     Process Name ( PID),   ThreadID,             IrpPtr,   ByteOffset,     IOSize, ElapsedTime,  DiskNum, IrpFlags, DiskSvcTime, I/O Pri,  VolSnap,         FileObject, FileName
              DiskWrite,  TimeStamp,     Process Name ( PID),   ThreadID,             IrpPtr,   ByteOffset,     IOSize, ElapsedTime,  DiskNum, IrpFlags, DiskSvcTime, I/O Pri,  VolSnap,         FileObject, FileName
           DiskReadInit,  TimeStamp,     Process Name ( PID),   ThreadID,             IrpPtr
          DiskWriteInit,  TimeStamp,     Process Name ( PID),   ThreadID,             IrpPtr
              DiskFlush,  TimeStamp,     Process Name ( PID),   ThreadID,             IrpPtr,                           ElapsedTime,  DiskNum, IrpFlags, DiskSvcTime, I/O Pri
          DiskFlushInit,  TimeStamp,     Process Name ( PID),   ThreadID,             IrpPtr
    EndHeader

The following is the trace, we only care about two kind of trace:

```
DiskRead, TimeStamp, Process Name ( PID), ThreadID, IrpPtr, ByteOffset, IOSize, ElapsedTime, DiskNum, IrpFlags, DiskSvcTime, I/O Pri, VolSnap, FileObject, FileName
```

```
DiskWrite, TimeStamp, Process Name ( PID), ThreadID, IrpPtr, ByteOffset, IOSize, ElapsedTime,  DiskNum, IrpFlags, DiskSvcTime, I/O Pri,  VolSnap, FileObject, FileName
```

**2.Unix's blktrace format example**

[SNIA - Storage Networking Industry Association: IOTTA Repository Home](http://iotta.snia.org/traces/block-io/28568)

Each blocktrace record contains the following fields：

[Device Major Number,Device Minor Number] [CPU Core ID] [Record ID] [Timestamp (in nanoseconds)] 

[ProcessID] [Trace Action] [OperationType] [SectorNumber + I/O Size] [ProcessName]

More details about each blocktrace field can be obtained here: https://linux.die.net/man/1/blkparse


**3.Systor '17 Traces**
[SNIA - Storage Networking Industry Association: IOTTA Repository Home](http://iotta.snia.org/traces/block-io/4964)

The files are gzipped csv (comma-separated text) files. The fields in
the csv are:

Timestamp,Response,IOType,LUN,Offset,Size

  - **Timestamp** is the time the I/O was issued.
    The timestamp is given as a Unix time (seconds since 1/1/1970) with a fractional part. 
    Although the fractional part is nine digits, it is accurate only to the microsecond level; 
    Please  ignore the nanosecond part.  
    If you need to process the timestamps in their original local timezone, it is UTC+0900 (JST).
    For example:
     > head 2016022219-LUN4.csv.gz  ← (Mon, 22 Feb 2016 19:00:00 JST)
       1456135200.013118000 ← (Mon, 22 Feb 2016 10:00:00 GMT)       
  - **Response** is the time needed to complete the I/O.
  - **IOType** is "Read(R)", "Write(W)", or ""(blank). The blank indicates that there was no response message.
  - **LUN** corresponds to each block storage device.(0,1,2,3,4, or 5).
  - **Offset** is the starting offset of the I/O in bytes from the start of the logical disk.
  - **Size** is the transfer size of the I/O request in bytes.

---

Use example:

```shell
python trace-editor.py -file <tracename> -preprocessMSTrace [-filter read/write]
python trace-editor.py -file <tracename> -preprocessBlkReplayTrace [-filter read/write]
python trace-editor.py -file <tracename> -preprocessUnixBlkTrace [-filter read/write]
```

It can also preprocess all traces inside a directory（put directory in `in/`）, here's an example using MS-Trace

```shell
python trace-editor.py -dir <dirname> -preprocessMSTrace [-filter read/write]
```

### 2.Modify a trace
Resize all read requests size by 2x and rerate all write request arrival time by 0.5x :

```shell
python trace-editor.py -file <tracename> -rresize 2 -wrerate 0.5
```

Insert a 4KB read (iotype == 1) for every 1000ms:

```shell
python trace-editor.py -file <tracename> -insert -size 4 -iotype 1 -interval 1000
```

### 3.Combine traces 

Make sure that the traces' names are well ordered because the script will just do the process without ordering the traces. Well ordered means the traces are ordered from the earliest time to the latest time. Just check this condition with -ls.

```
python trace-editor.py -dir <dirname> -combine
```

### 4.Merge traces 

Merge the traces in a directory, all timestamps will be subtracted with the lowest timestamp.

```shell
python trace-editor.py -dir <dirname> -merge
```

### 5.Break to RAID-0 disks 

In this example get RAID disks from 4 disks with the stripe unit size 65536 bytes

```shell
python trace-editor.py -breaktoraid -file <infile> -ndisk 4 -stripe 65536
```

### 6.Check IO imbalance in the RAID Disks. 

This example uses 3disks with the granularity of 5minutes.

```shell
python trace-editor.py -ioimbalance -file <filename> -granularity 5
```

### 7.Check the busiest or the most loaded (in kB) time for a specific disk in a directory
**Busiest**: a time range with **the largest number of requests** 

**Most Loaded**: a time range with **the largest total requests size**

Options：

* -duration: in mins, in this example 1hrs (60mins)
* -top: top n result, in this example 3 top results

```shell
python trace-editor.py -dir <dirname> -mostLoaded -duration 60 -top 3
python trace-editor.py -dir <dirname> -busiest -duration 60 -top 3
```

Check the largest average time, the usage is the same with busiest and most loaded

```shell
python trace-editor.py -dir <dirname> -busiest -duration 60 -top 3
```

### 8.Top Large IO

In this example:

Top 3 large IO with size greater than or equal 64kB, with 1hr duration

```shell
python trace-editor.py -toplargeio -file <filename> -offset 64 -devno 0 -duration 60 -top 3
```

### 9.Find most random write time range

In this example:

Find a time range(min) where has most random write

```shell
python trace-editor.py -dir <dirname> -mostRandomWrite -duration 5 -devno 5 -top 3
```

### 10.Get characteristic info

In this example:
You can get something like whisker plot info about write size, read size, time density, and % write, % read, % random write

```shell
python trace-editor.py -dir <dirname> -char
```

### 11.Cut trace

In this example between time range of minute 5 and minute 10

```shell
python trace-editor.py -cuttrace -file <filename> -timerange 5 10
```

### 12.Sanitize the trace 

incorporate contiguous IO + remove repeated reads

```shell
python trace-editor.py -file <filename> -sanitize
```
