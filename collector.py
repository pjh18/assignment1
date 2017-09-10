#!/usr/bin/env python
import ADC0832
import time
import redis

r = redis.Redis(host='redis-11762.c14.us-east-1-2.ec2.cloud.redislabs.com', port='11762', password='nope')

def init():
        ADC0832.setup()

def loop():
        while True:
                #The ADC0832 has two channels
                #res = ADC0832.getResult()   <-- It reads channel 0 by default. Equivalent to getResult(0)
                #res = ADC0832.getResult(1)  <-- Use this to read the second channel

                res = ADC0832.getResult() - 110
                if res < 0:
                        res = 0
                if res > 100:
                        res = 100
                print 'res = %d' % res

                #Store the result in the database
                epoch_time = int(time.time())
                epoch_key = "assignment" + str(epoch_time)

                print 'time = ' + epoch_key

                r.hmset(epoch_key,{'photoresistor': res})
                #print 'db value = ' + r.hget(epoch_key,'photoresistor')
                time.sleep(0.8)

if __name__ == '__main__':
        init()
        try:
                loop()
        except KeyboardInterrupt:
                ADC0832.destroy()
                print 'The end !'

