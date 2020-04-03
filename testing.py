# import time
#
# from apscheduler.schedulers.background import BackgroundScheduler
#
#
# def test():
#     sched = BackgroundScheduler()
#     sched.start()
#
#     sched.add_job(pri, 'cron', hour=9, minute=7, id="pri")
#
# def pri():
#     print("running")
#
#
# test()
# while True :
#     time.sleep(1)