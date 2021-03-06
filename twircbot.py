import time, config, pid, irc, db, log

pid = pid.pid()
irc = irc.irc()
db = db.db()
log = log.log()

db.get_raffle_status()

if pid.oktorun:
    try:
        while True:
            time.sleep(1)
            # Output
            out = db.get_next_output(time.time())
            if out:
                sendStr = 'PRIVMSG '+ out[1] +' :'+ out[2] +'\n'
                print(sendStr)
                irc.sendmsg(sendStr)
                log.logmsg(sendStr, False)
                db.delete_output(out[0])

            try:
                msg = irc.getmsg()
                print(msg)

                # Reconnect if disconnected
                if len(msg) == 0:
                    irc.connect()

                # Prevent Timeout
                if irc.ping(msg):
                    irc.pong(msg)

                # Log mentions of us
                if msg.find('PRIVMSG') != -1 and msg.casefold().find(config.ownernick) != -1:
                    log.logmsg(msg)

                # Log shenbot output
                #if msg.find('PRIVMSG') != -1 and irc.isshenbot(msg):
                #    log.logmsg(msg)

                # Commands in #selfchannel
                if irc.isselfchannel(msg):
                    if irc.isowner(msg):
                        if msg.find(':!help') != -1:
                            ts = float(time.time() + 3)
                            chan = str(config.selfchannel)
                            msg = str('Commands: !online, !joinraffle, !nojoinraffle, !rafflestatus, !last10, !total, !best5, !worst5')
                            db.write_output(ts, chan, msg)
                        elif msg.find(':!online') != -1:
                            ts = float(time.time() + 3)
                            chan = str(config.selfchannel)
                            msg = str('Twircbot is online.')
                            db.write_output(ts, chan, msg)
                        elif msg.find(':!joinraffle') != -1:
                            ts = float(time.time() + 3)
                            chan = str(config.selfchannel)
                            msg = str('Will join raffles.')
                            db.set_raffle_status('on')
                            db.write_output(ts, chan, msg)
                        elif msg.find(':!nojoinraffle') != -1:
                            ts = float(time.time() + 3)
                            chan = str(config.selfchannel)
                            msg = str('Automatic raffle joining turned off.')
                            db.set_raffle_status('off')
                            db.write_output(ts, chan, msg)
                        elif msg.find(':!rafflestatus') != -1:
                            ts = float(time.time() + 3)
                            chan = str(config.selfchannel)
                            rafflestatus = db.get_raffle_status()
                            if rafflestatus == 'on':
                                msg = str('Automatic raffle joining is on.')
                            else:
                                msg = str('Not joining raffles.')
                            db.write_output(ts, chan, msg)
                        elif msg.find(':!last10') != -1:
                            res = db.get_last_10_heists()
                            if res:
                                i = 1
                                total = 0
                                for row in reversed(res):
                                    ts = float(time.time() + i)
                                    chan = str(config.selfchannel)
                                    heistts = row[0]
                                    heiststarter = row[1]
                                    points = row[2]
                                    score = round(points - 1000)
                                    total = total + score
                                    if points > 1000:
                                        msg = str('#'+ str(i) +': '+ time.strftime('%Y-%m-%d %H:%M', time.localtime(heistts)) +': WON '+ str(score) +' points. Thanks '+ str(heiststarter) +'. shenTea')
                                    elif points < 1000:
                                        msg = str('#'+ str(i) +': '+ time.strftime('%Y-%m-%d %H:%M', time.localtime(heistts)) +': LOST '+ str(abs(score)) +' points. #blame '+ str(heiststarter) +'. shenRage')
                                    else:
                                        msg = str('#'+ str(i) +': '+ time.strftime('%Y-%m-%d %H:%M', time.localtime(heistts)) +': EVEN 0 points. Good going '+ str(heiststarter) +'. shenFacepalm')
                                    db.write_output(ts, chan, msg)
                                    i = i + 1
                                ts = float(time.time() + i)
                                chan = str(config.selfchannel)
                                if total > 0:
                                    msg = str('Total won: '+ str(total) +' points.')
                                elif total < 0:
                                    msg = str('Total lost: '+ str(abs(total)) +' points.')
                                else:
                                    msg = str('Total: '+ str(total) +' points won/lost.')
                                db.write_output(ts, chan, msg)
                            else:
                                ts = float(time.time() + 3)
                                chan = str(config.selfchannel)
                                msg = str('No recorded heists.')
                                db.write_output(ts, chan, msg)
                        elif msg.find(':!total') != -1:
                            row = db.get_heist_total_score()
                            print(row)
                            if row:
                                score = row[0]
                                heists = row[1]
                                earnings = (score - (heists * 1000))
                                ts = float(time.time() + 3)
                                chan = str(config.selfchannel)
                                if earnings > 0:
                                    msg = str('# heists: '+ str(heists) +'. points won: '+ str(earnings) +'.')
                                elif earnings < 0:
                                    msg = str('# heists: '+ str(heists) +'. points lost: '+ str(abs(earnings)) +'.')
                                else:
                                    msg = str('# heists: '+ str(heists) +'. points even: '+ str(earnings) +'.')
                                db.write_output(ts, chan, msg)
                            else:
                                ts = float(time.time() + 3)
                                chan = str(config.selfchannel)
                                msg = str('No recorded heists.')
                        elif msg.find(':!best5') != -1:
                            res = db.get_5_best_heisters()
                            if res:
                                i = 1
                                for row in res:
                                    ts = float(time.time() + i)
                                    chan = str(config.selfchannel)
                                    heiststarter = row[0]
                                    score = row[1]
                                    heists = row[2]
                                    if score > 0:
                                        msg = str('#'+ str(i) +': '+ str(heiststarter) +' generated '+ str(score) +' profit in '+ str(heists) +' heists.')
                                    elif score < 0:
                                        msg = str('#'+ str(i) +': '+ str(heiststarter) +' lost us '+ str(abs(score)) +' points in '+ str(heists) +' heists.')
                                    else:
                                        msg = str('#'+ str(i) +': '+ str(heiststarter) +' turned us even with '+ str(score) +' points in '+ str(heists) +' heists.')
                                    db.write_output(ts, chan, msg)
                                    i = i + 1
                            else:
                                ts = float(time.time() + 3)
                                chan = str(config.selfchannel)
                                msg = str('No recorded heists.')
                                db.write_output(ts, chan, msg)
                        elif msg.find(':!worst5') != -1:
                            res = db.get_5_worst_heisters()
                            if res:
                                i = 1
                                for row in res:
                                    ts = float(time.time() + i)
                                    chan = str(config.selfchannel)
                                    heiststarter = row[0]
                                    score = row[1]
                                    heists = row[2]
                                    if score > 0:
                                        msg = str('#'+ str(i) +': '+ str(heiststarter) +' generated '+ str(score) +' profit in '+ str(heists) +' heists.')
                                    elif score < 0:
                                        msg = str('#'+ str(i) +': '+ str(heiststarter) +' lost us '+ str(abs(score)) +' points in '+ str(heists) +' heists.')
                                    else:
                                        msg = str('#'+ str(i) +': '+ str(heiststarter) +' turned us even with '+ str(score) +' points in '+ str(heists) +' heists.')
                                    db.write_output(ts, chan, msg)
                                    i = i + 1
                            else:
                                ts = float(time.time() + 3)
                                chan = str(config.selfchannel)
                                msg = str('No recorded heists.')
                                db.write_output(ts, chan, msg)

                # Commands and whatnot in #targetchannel
                if irc.istargetchannel(msg):
                    if irc.isshenbot(msg):
                        if msg.find('started a Heist type !heist to help them out.') != -1:
                            print('Heist started')
                            words = msg.split(' ')
                            print(words)
                            starter = words[3]
                            print('Starter: '+ starter)
                            print('Formatted: '+ starter[1:])
                            ts = float(time.time() + 3)
                            chan = str(config.channel)
                            msg = str('!heist')
                            db.write_output(ts, chan, msg)
                            db.new_heist(ts, starter[1:])
                        if msg.find('Stage 1 passed with') != -1:
                            words = msg.split(' ')
                            points = words[-2]
                            points = int(points)
                            ts = time.time()
                            db.update_heist(points)
                        if msg.find('Stage 2 passed with') != -1:
                            words = msg.split(' ')
                            points = words[-2]
                            points = int(points)
                            db.update_heist(points)
                        if msg.find('Stage 3 passed with') != -1:
                            words = msg.split(' ')
                            points = words[-2]
                            points = int(points)
                            db.update_heist(points)
                        if msg.find('Stage 4 passed with') != -1:
                            words = msg.split(' ')
                            points = words[-2]
                            points = int(points)
                            db.update_heist(points)
                            row = db.get_last_heist_details()
                            score = row[0]
                            heiststarter = row[1]
                            score = round(score - 1000)
                            ts = float(time.time() + 6)
                            chan = str(config.channel)
                            msg2 = str('#blame '+ heiststarter)
                            if score > 1:
                                msg = str('Yay, '+ str(score) +' points profit. shenTea')
                            elif score == 1:
                                msg = str('Yay, '+ str(score) +' point profit. shenTea')
                            elif score == -1:
                                msg = str('No, my point shenRage')
                            elif score < -1:
                                msg = str('No, my '+ str(abs(score)) +' points shenRage')
                            else:
                                msg = str('No profit but no loss either. shenFacepalm')
                            db.write_output(ts, chan, msg)
                            if score <= 0:
                                ts = ts + 3
                                db.write_output(ts, chan, msg2)
                        if msg.find('Stage 1 Failed with') != -1:
                            db.update_heist(0)
                            row = db.get_last_heist_details()
                            score = row[0]
                            heiststarter = row[1]
                            ts = float(time.time() + 6)
                            chan = str(config.channel)
                            msg = str('#blame '+ heiststarter)
                            db.write_output(ts, chan, msg)
                        if msg.find('Stage 2 Failed with') != -1:
                            row = db.get_last_heist_details()
                            score = row[0]
                            heiststarter = row[1]
                            score = round(score - 1000)
                            ts = float(time.time() + 6)
                            chan = str(config.channel)
                            msg2 = str('#blame '+ heiststarter)
                            if score > 1:
                                msg = str('Yay, '+ str(score) +' points profit. shenTea')
                            elif score == 1:
                                msg = str('Yay, '+ str(score) +' point profit. shenTea')
                            elif score == -1:
                                msg = str('No, my point shenRage')
                            elif score < -1:
                                msg = str('No, my '+ str(abs(score)) +' points shenRage')
                            else:
                                msg = str('No profit but no loss either. shenFacepalm')
                            db.write_output(ts, chan, msg)
                            if score <= 0:
                                ts = ts + 3
                                db.write_output(ts, chan, msg2)
                        if msg.find('Stage 3 Failed with') != -1:
                            row = db.get_last_heist_details()
                            score = row[0]
                            heiststarter = row[1]
                            score = round(score - 1000)
                            ts = float(time.time() + 6)
                            chan = str(config.channel)
                            msg2 = str('#blame '+ heiststarter)
                            if score > 1:
                                msg = str('Yay, '+ str(score) +' points profit. shenTea')
                            elif score == 1:
                                msg = str('Yay, '+ str(score) +' point profit. shenTea')
                            elif score == -1:
                                msg = str('No, my point shenRage')
                            elif score < -1:
                                msg = str('No, my '+ str(abs(score)) +' points shenRage')
                            else:
                                msg = str('No profit but no loss either. shenFacepalm')
                            db.write_output(ts, chan, msg)
                            if score <= 0:
                                ts = ts + 3
                                db.write_output(ts, chan, msg2)
                        if msg.find('Stage 4 Failed with') != -1:
                            row = db.get_last_heist_details()
                            score = row[0]
                            heiststarter = row[1]
                            score = round(score - 1000)
                            ts = float(time.time() + 6)
                            chan = str(config.channel)
                            msg2 = str('#blame '+ heiststarter)
                            if score > 1:
                                msg = str('Yay, '+ str(score) +' points profit. shenTea')
                            elif score == 1:
                                msg = str('Yay, '+ str(score) +' point profit. shenTea')
                            elif score == -1:
                                msg = str('No, my point shenRage')
                            elif score < -1:
                                msg = str('No, my '+ str(abs(score)) +' points shenRage')
                            else:
                                msg = str('No profit but no loss either. shenFacepalm')
                            db.write_output(ts, chan, msg)
                            if score <= 0:
                                ts = ts + 3
                                db.write_output(ts, chan, msg2)
                        if msg.find('Type !Raffle in subchat for your chance to win') != -1:
                            rafflestatus = db.get_raffle_status()
                            if rafflestatus == 'on':
                                ts = float(time.time() + 3)
                                chan = str(config.subchan +':'+ config.shenchannelid +':'+ config.shensubchat)
                                msg = str('!raffle')
                                db.write_output(ts, chan, msg)
                        if msg.find('Congratulations to') != -1:
                            if msg.casefold().find(' '+ config.ownernick) != -1:
                                rafflestatus = db.get_raffle_status()
                                if rafflestatus == 'on':
                                    db.set_raffle_status('off')

                # Commands and whatnot in #subchannel
                if irc.issubchannel(msg):
                    if irc.isshenbot(msg):
                        if msg.find('Type !Raffle for your chance to win') != -1:
                            rafflestatus = db.get_raffle_status()
                            if rafflestatus == 'on':
                                ts = float(time.time() + 3)
                                chan = str(config.subchan +':'+ config.shenchannelid +':'+ config.shensubchat)
                                msg = str('!raffle')
                                db.write_output(ts, chan, msg)
                        if msg.find('Congratulations to') != -1:
                            if msg.casefold().find(' '+ config.ownernick) != -1:
                                rafflestatus = db.get_raffle_status()
                                if rafflestatus == 'on':
                                    db.set_raffle_status('off')

            except Exception:
                continue
    finally:
        pid.unlink()
