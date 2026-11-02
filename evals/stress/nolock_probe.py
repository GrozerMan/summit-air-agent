"""Probe: is BEGIN IMMEDIATE load-bearing? Removes the lock in-process (monkeypatch, repo untouched)
and races 4 bookings for the last seat 30 times.  uv run python -m evals.stress.nolock_probe"""
import threading, contextlib
from pathlib import Path
from tempfile import TemporaryDirectory
from summit import config
from summit.store import Store
from summit.scheduling import Scheduler
from summit.seed import seed
from summit.models import Pool, Priority
from datetime import datetime
from zoneinfo import ZoneInfo
T = datetime(2026,11,3,10,0,tzinfo=ZoneInfo("America/New_York")); CFG=config.load()
Store.write_lock = lambda self: contextlib.nullcontext(self.conn)   # lock removed
# widen the check->insert gap the way a slow disk/GIL switch would
orig = Scheduler.seats_left
def slow(self,*a):
    r = orig(self,*a); import time; time.sleep(0.01); return r
Scheduler.seats_left = slow
over=0
with TemporaryDirectory() as d:
    for i in range(30):
        p=Path(d)/f"r{i}.db"; seed(Store(p), today=T.date()); s=Scheduler(Store(p),CFG)
        o=next(x for x in s.find_options("Suffolk",Priority.P3,False,T,limit=20) if x.pool==Pool.REGULAR)
        kw=dict(customer_id=1,call_id="f",job_type="x",priority=Priority.P3,service_address="x",contact_name="x",contact_phone="+15165550000")
        while orig(s,o.county,o.day,o.window,o.pool)>1: s.book(o,**kw)
        b=threading.Barrier(4); res=[]
        def go():
            own=Scheduler(Store(p),CFG); b.wait(); res.append(own.book(o,**kw))
        ts=[threading.Thread(target=go) for _ in range(4)]; [t.start() for t in ts]; [t.join() for t in ts]
        over += sum(isinstance(r,int) for r in res) > 1
print(f"without the lock: {over}/30 runs overbooked the last seat")
