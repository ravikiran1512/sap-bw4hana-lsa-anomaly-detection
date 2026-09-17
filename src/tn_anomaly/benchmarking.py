from __future__ import annotations
from contextlib import contextmanager
from dataclasses import dataclass
import os,time,psutil

@dataclass
class BenchmarkResult:
    runtime_seconds: float
    memory_mb: float
    cpu_usage: float
    records_processed: int
    throughput: float

@contextmanager
def measure(records_processed: int):
    process=psutil.Process(os.getpid()); mem0=process.memory_info().rss; cpu0=process.cpu_times(); t0=time.perf_counter(); box={}
    yield box
    runtime=time.perf_counter()-t0; mem1=process.memory_info().rss; cpu1=process.cpu_times()
    cpu_time=(cpu1.user+cpu1.system)-(cpu0.user+cpu0.system)
    box["benchmark"]=BenchmarkResult(runtime_seconds=runtime,memory_mb=max(0.,(mem1-mem0)/(1024**2)),cpu_usage=(cpu_time/runtime*100 if runtime else 0.),records_processed=records_processed,throughput=(records_processed/runtime if runtime else 0.))
