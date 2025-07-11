#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import socket
from subprocess import call
from datetime import datetime, date, timedelta
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'icons')
weatherdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'icons/weather')
fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fonts')
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd7in5b_V2
import time
from PIL import Image,ImageDraw,ImageFont
from PIL.ImageFont import FreeTypeFont
import traceback
from openweather import current_weather, tomorrow_weather
from aqidata import current_aqi, get_aqi_status_data, aqi_trend, write_aqi_stats
from todoist import gettodolist, getodolistbyduedate
from getquote import quoteoftheday, addquotetofile, quotefromfile
from garbage_schedule import get_garbage_status, get_garbage_config_data
from pi_info import getRAMinfo, getDiskSpace, getCPUtemperature, getCPUuse

from pisugar import *

import configparser

from dataclasses import dataclass

@dataclass
class screen:
    width : int
    height : int
    middle_w : int
    middle_h : int
    quote_max : int
    reminder_max : int
    use_red : int
    refresh_rate_min : int
    clean_screen : int
    sleep_hour :int
    wake_hour : int

@dataclass
class dashboard:
    show_weather: int
    show_weather_details : int
    show_quote : int
    show_quote_live : int
    quote : str
    show_todo : int
    todo_rows : int
    todo_filter :str
    todo_garbage : str
    todo_recycle : str
    todo_compost : str
    show_power : int
    delay_start_sec : int
    shutdown_after_run : int
    quote_length : int


@dataclass
class hourglass:
    day : int
    hour : int
    curenttime : int
    currentday : int
    live_cutin_hour : int
    live_cutout_hour : int
    last_refresh : str
    evening_hour : str

@dataclass
class GenGarbage:
    garbage_vars : dict
    g_data : dict
    garbageDay : bool
    recycleDay : bool
    compostDay : bool

@dataclass
class performance:
    usedram : int
    freeram : int
    ramincrease : int
    previousram : int
    cli : str
    debug : str
    ip_address : str
    host_name : str

@dataclass
class battery:
    level : int
    state : str

@dataclass
class font:
    DayTitle :FreeTypeFont
    SFMonth :FreeTypeFont
    SFDate :FreeTypeFont

    SFToday_temp :FreeTypeFont
    SFToday_cond :FreeTypeFont
    SFToday_hl :FreeTypeFont
    SFWdetails :FreeTypeFont
    SFWdetails_bold :FreeTypeFont
    SFWdetails_semibold :FreeTypeFont
    SFWdetails_sub :FreeTypeFont
    SFWdetails_sub_bold :FreeTypeFont
    SFWAQI_bold :FreeTypeFont
    SFWAQI_bold_small :FreeTypeFont

    SFToDo :FreeTypeFont
    SFToDo_sub :FreeTypeFont

    SFQuote :FreeTypeFont
    SFQuoteAuthor :FreeTypeFont
    SFReminder :FreeTypeFont
    SFReminder_sub :FreeTypeFont
    SFTransitID :FreeTypeFont
    SF_TransitName :FreeTypeFont
    SFTransitTime :FreeTypeFont

    SleepFont  :FreeTypeFont
    SleepFont_foot :FreeTypeFont


def MorningDash():
    applog("MorningDash","Initializing...")    
    try:

        epd = epd7in5b_V2.EPD()
        epd.init()
        #epd.Clear()
        screen.height = epd.height
        screen.width = epd.width
        screen.middle_w = screen.width/2
        screen.middle_h = screen.height/2
    except IOError as e:
        applog("Screen init error:" ,e)

    except KeyboardInterrupt:
        applog("System runtime" ,"ctrl + c:")
        epd7in5b_V2.epdconfig.module_exit()
        exit()

    # Check if we should clear the E-ink (daily)
    if screen.clean_screen < int(datetime.now().strftime("%d")):
        if "noclean" in performance.cli:
            applog("System runtime" ,"Screen cleaning skipped")
            performance.cli = ""
        else:
            applog("System runtime" ,"Time to clean the screen - once daily")
            epd.Clear()
            screen.clean_screen = int(datetime.now().strftime("%d"))
            applog("System runtime" ,"Re-loading config parameters daily.")


    black = 'rgb(0,0,0)'
    white = 'rgb(255,255,255)'
    grey = 'rgb(206,206,206)'

    w_x = 10
    w_y = 75
    w_icon_offset = 170
    w_icon_row_height = 40


    imageB = Image.new('L', (epd.width, epd.height), 255)  # 255: clear the frame
    imageR = Image.new('L', (epd.width, epd.height), 255)  # 255: clear the frame

    draw_black = ImageDraw.Draw(imageB)
    draw_red = ImageDraw.Draw(imageR)

    # Find out how many characters pixels per line of screen for Quotes
    screen.quote_max = screen.width - 100

    # Find out how many characters per line of screen for Reminder text
    screen.reminder_max = screen.width - 40

    screen.offset = 95

    header_Day = datetime.now().strftime("%A")
    header_Day_short = datetime.now().strftime("%a")
    header_Month_Date = datetime.now().strftime("%b %-d")
    header_Month = datetime.now().strftime("%b")
    header_Date = datetime.now().strftime("%-d")

    header_Day_t_size = draw_black.textbbox((0, 0), header_Day, font=font.DayTitle)
    header_Date_t_size = draw_black.textbbox((0, 0), header_Date, font=font.SFDate)
    header_Month_t_size = draw_black.textbbox((0, 0), header_Month, font=font.SFMonth)
    header_Day_w = header_Day_t_size[2] + header_Day_t_size[0]
    header_Day_h = header_Day_t_size[3]
    header_Month_w = header_Month_t_size[2]
    header_Month_h = header_Month_t_size[3]
    header_date_w = header_Date_t_size[2]
    header_date_h = header_Date_t_size[3]

    x_master = 10
    y_master = 10
    can_show_quote = True



    if dashboard.show_weather == 1:
        applog("Dashboard","Weather feature ON")
        applog("Weather feature","Getting current AQI")
        today_aqi = current_aqi()

        applog("Dashboard","Weather feature ON")
        applog("Weather feature","Getting current weather")
        today_weather = current_weather()
        weather_error = today_weather.error

        applog("Weather feature","Getting weather forecast")
        forecast_weather = tomorrow_weather()
        today_forecast = forecast_weather[0]
        tomorrow_forecast = forecast_weather[1]
        applog("Weather feature","Getting weather forecast, DONE")


    salute_text = "Hello"
    if hourglass.curenttime >= 0 and hourglass.curenttime <=6:
        salute_text = "Hey earlybird!"
    if hourglass.curenttime >= 7 and hourglass.curenttime <=11:
        salute_text = "Good Morning"
    if hourglass.curenttime > 12 and hourglass.curenttime <=15:
        salute_text = "Good Afternoon"
    if hourglass.curenttime > 16 and hourglass.curenttime <=19:
        salute_text = "Good Afternoon"
    if hourglass.curenttime > 20 and hourglass.curenttime <=22:
        salute_text = "Good Evening"
    if hourglass.curenttime > 22 :
        salute_text = "Bed time..."


    applog("Dashboard" ,"Drawing todays day")

    x = 10
    y = 2
    screen_y = y
    draw_black.text((x,y), header_Day, font = font.DayTitle, fill = black)
    t_G, t_G, test_t_w, test_t_h = draw_black.textbbox((0,0),header_Day, font=font.DayTitle)
    screen_y = y + test_t_h

    if dashboard.show_weather == 1:

        weather_cond_icon = Image.open(os.path.join(weatherdir, today_weather.icon+'.png'))


        fl_icon = Image.open(os.path.join(weatherdir, "t.png"))
        fl_icon_red = 0
        if today_weather.feelslike < today_weather.temperature :
            fl_icon = Image.open(os.path.join(weatherdir, "temp_low.png"))

        if today_weather.feelslike > today_weather.temperature  :
            fl_icon = Image.open(os.path.join(weatherdir, "temp_high.png"))
            fl_icon_b = Image.open(os.path.join(weatherdir, "temp_high_b.png"))
            fl_icon_r =  Image.open(os.path.join(weatherdir, "temp_high_r.png"))     
            fl_icon_red = 1

        if today_weather.icon == "EE":
            today_temp = "?"
        else:
            today_temp = str(round(today_weather.temperature,1))+"\N{DEGREE SIGN}"
            today_feels_temp = "("+str(round(today_weather.feelslike,1))+"\N{DEGREE SIGN})"
        x = int(x + test_t_w + 8)
        i_off = int ( (y + (test_t_h/2)) - (fl_icon.size[1]/2))

        imageB.paste(weather_cond_icon, (x,(y+8)),weather_cond_icon)

        x = x + weather_cond_icon.width

        if screen.use_red == 0:
            imageB.paste(fl_icon, (x,(y+i_off)),fl_icon)
            x = x + int(fl_icon.size[0]+ 4)
        else:
            if fl_icon_red == 1:
                imageB.paste(fl_icon_b, (x,(y+i_off)),fl_icon_b)
                imageR.paste(fl_icon_r, (x,(y+i_off)),fl_icon_r)
                x = x + int(fl_icon_b.size[0]+ 4)
            else:
                imageB.paste(fl_icon, (x,(y+i_off)),fl_icon)
                x = x + int(fl_icon.size[0]+ 4)
        draw_black.text((x,y), today_temp, font = font.DayTitle, fill = black)
        t_G, t_G, test_t_w, test_t_h = draw_black.textbbox((0,0),today_temp, font=font.DayTitle)
        x = x + test_t_w
        xt_G, xt_G, xtest_t_w, xtest_t_h = draw_black.textbbox((0,0),today_temp, font=font.SFReminder)
        y = y + int(xtest_t_h/2)
        draw_black.text((x,y), today_feels_temp, font = font.SFReminder, fill = black)




    screen_y = y + test_t_h

    cal_icon = Image.open(os.path.join(picdir, 'calendar_header.png'))
    cal_icon_R = Image.open(os.path.join(picdir, 'calendar_header_R.png'))
    cal_icon_B = Image.open(os.path.join(picdir, 'calendar_header_B.png'))
    
    xcal = int(screen.middle_w - (cal_icon.size[0] * 2))
    xcal = int(screen.width - (cal_icon.size[0])) - 20
    
    ycal = y + 6
   
    if screen.use_red == 1:
        imageR.paste(cal_icon_R, (xcal,ycal), cal_icon_R)
        imageB.paste(cal_icon_B, (xcal,ycal), cal_icon_B)
    else :
        imageB.paste(cal_icon, (xcal,ycal), cal_icon) 

    y = ycal + (int(cal_icon.size[1]/2) - int(header_date_h/2)) + 1
    x = xcal + (int(cal_icon.size[0]/2) - int(header_date_w/2))

    draw_black.text((x, y), header_Date, font = font.SFDate, fill = black)

    y = ycal + 2
    x = xcal + (int(cal_icon.size[0]/2) - int(header_Month_w/2))
    if screen.use_red == 1:
        draw_red.text((x, y), header_Month, font = font.SFMonth, fill=white)
    else:
        draw_black.text((x, y), header_Month, font = font.SFMonth, fill=white)

    screen_y = int(y + test_t_h) +10

 #   applog("dashboard.show_todo",str(dashboard.show_todo))
    if dashboard.show_todo == 1 :

        ############
            ####
            ####
            ####
            ####
            ####
        

        applog("Dashboard" ,"Todoist feature : ON")

        GenGarbage.garbageDay = False
        GenGarbage.compostDay = False
        GenGarbage.recycleDay = False



        if dashboard.todo_filter == "TODAY":
            applog("Todoist feature" ,"Getting only todo's due today...")
            show_dude_date = False
            today_todo_list = getodolistbyduedate(datetime.now())
        else:
            applog("Todoist feature" ,"Getting all todos due...")
            show_dude_date = True
            today_todo_list = gettodolist()
        numtodos = len(today_todo_list)


        applog("Todoist feature" ,"Got "+str(numtodos)+" tasks to show")
        tnum = 0
        tdrow = 0
        col_space = 0
        tg, tg, td_w, tdrow_h = draw_black.textbbox((0,0),"adjGgTsK", font=font.SFToDo) #Setting basic text parameters for spacing.

        if numtodos > 0:
            can_show_quote = False
            applog("Todoist feature" ,"geting todoist list...")

            todo_icon = Image.open(os.path.join(picdir, "tasks_icon.png"))
            todo_icon_B = Image.open(os.path.join(picdir, "tasks_iconB.png"))
            todo_icon_R = Image.open(os.path.join(picdir, "tasks_iconR.png"))
            todo_mini_icon  = Image.open(os.path.join(picdir, "todo_mini.png"))
            x = w_x
            y = screen_y
            todostart_y = screen_y
            todostop_y = screen_y

            qx = w_x
            qy = screen_y + 4

            #Show the todo icon status
            
            gTy = qy + 14
            gTx = x + int(todo_icon.size[0]+5)
            gTTop = gTy
            gTTy = int(qy + todo_icon.size[1] + 5)


            ################ WHITE BORDER SPACE CALCULATIONS #################
            today_todo_list.sort(key=lambda x: x.due_date, reverse=True) # Sort by Due date
            for tsk in today_todo_list:
                tsk_title = tsk.content.replace('\n', '')
                tg, tg, td_w, td_h = draw_black.textbbox((0,0),tsk_title, font=font.SFToDo)
                if int(td_w + (todo_mini_icon.size[0]*2)) > col_space:
                    col_space = int(td_w + (todo_mini_icon.size[0]*2))
                if int(gTx + col_space) >= int(screen.width - 5):
                    applog("Todoist feature" ,"No more space for tasks on screen...")
                    break
                if show_dude_date and tsk.due_date:
                    due_daymonth = tsk.due_date.strftime("%d%m")
                    if due_daymonth == daymonth:
                        due_date_text = "Today"
                    else:
                        due_date_text = tsk.due_date.strftime("%A, %b %-d")
                    gTy = gTy + tdrow_h_s
                gTy = gTy + tdrow_h
                if gTy > gTTy:
                    gTTy = gTy
                tdrow +=1
                if tdrow == dashboard.todo_rows:
                    gTx = gTx + col_space
                    gTy = gTTop
                    col_space = 0
                    tdrow = 0
                if gTy > gTTy:
                    todostop_y = int(gTy)
                else:
                    todostop_y = int(gTTy)

                if dashboard.todo_garbage in tsk_title:
                    applog("Todoist feature" ,"Its garbage day today")
                    GenGarbage.garbageDay = True

                if dashboard.todo_compost in tsk_title:
                    applog("Todoist feature" ,"Its compost day today")
                    GenGarbage.compostDay = True

                if dashboard.todo_recycle in tsk_title:
                    applog("Todoist feature" ,"Its recycle day today")
                    GenGarbage.recycleDay = True
            
            todoheight = int(todostop_y - todostart_y)
            shape = [(0, todostart_y), (screen.width, todoheight + todostart_y)]
            # create rectangle image 
            draw_black.rectangle(shape, fill = white)
            draw_red.rectangle(shape, fill = white) 


            ################ WHITE BORDER SPACE CALCULATIONS #################
            tnum = 0
            tdrow = 0
            col_space = 0

            draw_black.line([(x, y), (int(screen.width - (x*2)), y)], black)

            qx = w_x
            qy = screen_y + 4

            #Show the todo icon status
            if screen.use_red == 1:
                imageB.paste(todo_icon_B,(qx,qy),todo_icon_B)
                imageR.paste(todo_icon_R,(qx,qy),todo_icon_R)
            else:
                imageB.paste(todo_icon,(qx,qy),todo_icon)
            gTy = qy + 14
            gTx = x + int(todo_icon.size[0]+5)
            gTTop = gTy
            gTTy = int(qy + todo_icon.size[1] + 5)
            tg, tg, td_w, tdrow_h = draw_black.textbbox((0,0),"adjGgTsK", font=font.SFToDo)
            tg, tg, td_w_s, tdrow_h_s = draw_black.textbbox((0,0),",adjGgTsK", font=font.SFToDo_sub)
            daymonth = datetime.today().strftime("%d%m")

            today_todo_list.sort(key=lambda x: x.due_date, reverse=True) # Sort by Due date
            for tsk in today_todo_list:
                tsk_title = tsk.content.replace('\n', '')
                tg, tg, td_w, td_h = draw_black.textbbox((0,0),tsk_title, font=font.SFToDo)
                if int(td_w + (todo_mini_icon.size[0]*2)) > col_space:
                    col_space = int(td_w + (todo_mini_icon.size[0]*2))
                if int(gTx + col_space) >= int(screen.width - 5):
                    applog("Todoist feature" ,"No more space for tasks on screen...")
                    break
                imageB.paste(todo_mini_icon,(gTx, gTy),todo_mini_icon)
                draw_black.text((int(gTx+todo_mini_icon.size[0]+2), int(gTy - todo_mini_icon.size[1]/3)), tsk_title, font=font.SFToDo, fill=black)
                if show_dude_date and tsk.due_date:
                    due_daymonth = tsk.due_date.strftime("%d%m")
                    if due_daymonth == daymonth:
                        due_date_text = "Today"
                    else:
                        due_date_text = tsk.due_date.strftime("%A, %b %-d")
                    gTy = gTy + tdrow_h_s
                    
                    draw_black.text((int(gTx+todo_mini_icon.size[0]+8), int(gTy - todo_mini_icon.size[1]/3)), due_date_text, font=font.SFToDo_sub, fill=black)
                gTy = gTy + tdrow_h
                if gTy > gTTy:
                    gTTy = gTy
                tdrow +=1
                if tdrow == dashboard.todo_rows:
                    gTx = gTx + col_space
                    gTy = gTTop
                    col_space = 0
                    tdrow = 0

            if gTy > gTTy:
                screen_y = int(gTy)
            else:
                screen_y = int(gTTy)

            y = screen_y
            draw_black.line([(x, y), (int(screen.width - (x*2)), y)], black)


        else:
            applog("Todoist feature" ,"No Tasks found - skipping to show....")
            can_show_quote = True

    else:
        applog("Dashboard" ,"Todoist feature : OFF")
        can_show_quote = True



    # Quote Section

           #######
        ####     ####
        ####     #### 
        ####     ####
        ####     #### 
            #######  ###
    if dashboard.show_quote == 1 and can_show_quote:
        applog("Dashboard","Quote of the day feature : ON")
        y = screen_y

        quote_icon = Image.open(os.path.join(picdir, "quote_icon.png"))
        quote_iconB = Image.open(os.path.join(picdir, "quote_b.png"))
        quote_iconR = Image.open(os.path.join(picdir, "quote_r.png"))
        quotebar_icon = Image.open(os.path.join(picdir, "quote_bar_top.png"))

        qx = w_x
        qy = y + 12
        x = 10

        qml = dashboard.quote_length
        qll = qml+1
        qmaxtries = 0


        if hourglass.currentday != int(datetime.now().day):
            applog("Message of the day" ,"Time to get a new message...")
            applog("Message of the day" ,"Getting a message under "+str(qml)+" lenght")

            while qll >= qml :
                applog("Message state","Getting a quote")
                applog("Message of the day" ,"Getting random quote from local database...")
                dashboard.quote = quotefromfile("quotes.txt")
                qll = len(dashboard.quote.quote_text)
                qmaxtries +=1
                if qmaxtries > 10:
                    break

                if qll >  qml:
                    applog("Message of the day" ,"Message Feature : Attempt: "+str(qmaxtries))
                else:
                    applog("Message of the day" ,"Message lenght is "+str(qll))
            hourglass.currentday = int(datetime.now().day)
        else:
            applog("Message of the day" ,"Keeping current message message...")
            qll = len(dashboard.quote.quote_text)
            
        #FIXME
        #dashboard.quote.quote_text = "One line quote."
        #dashboard.quote.quote_author = "Dashboard Ai Error ;("
        #qll = len(dashboard.quote.quote_text)


        if qll == 0 or qll > qml:
            applog("Quote of the day" ,"Max attempts to get a short enough quote exhausted.")
            #Just in case we could not find a short enough quote in 10 attempts.
            dashboard.quote.quote_text = "A quote was not found..."
            dashboard.quote.quote_author = "Dashboard Ai Error ;("
            hourglass.currentday = -1

        daily_message = dashboard.quote.quote_text
        
        #print("Now trying to slice the text in chunks")
        text_g, text_g, test_t_w, test_t_h = draw_black.textbbox((0,0),daily_message, font=font.SFQuote)
        text_max = test_t_w
        toff = x + int(quote_icon.size[0]+2)
        toff = 0
        screen.offset = int( quote_icon.size[0] + (x_master * 2) )
        text_line_max = screen.quote_max - (toff + screen.offset)

        text_line = []
        textbuffer = ""
        onlyOneRow = False

        #Split the quote into words in an array

        quote_words = daily_message.split()
        wl = len(quote_words)

        #See if the total is larger than the text_line_max value set.
        applog("Message of the day" ,"Max pixels per line is "+str(text_line_max))
        applog("Message of the day" ,daily_message)
        t_g, t_g, test_t_w, test_t_h = draw_black.textbbox((0,0),daily_message, font=font.SFQuote)



        if test_t_w > text_line_max:
            applog("Message of the day" ,"We need to split this message over many rows...")

            l = 0
            ql = len(quote_words)
            numrows = 0
            while l < ql:
                textbuffer = textbuffer + quote_words[l] + " "
                t_g, t_g, test_t_w, test_t_h = draw_black.textbbox((0,0),textbuffer, font=font.SFQuote)
                #print("Witdh of line "+str(numrows)+" is "+str(test_t_w))
                try:
                    t_g, t_g, test_t_w, test_t_h = draw_black.textbbox((0,0),textbuffer+quote_words[l+1], font=font.SFQuote)
                except:
                    applog("Message of the day" ,"done with the rows...")
                if test_t_w >= text_line_max:
                    text_line.append(textbuffer)
                    textbuffer = ""
                    #print(l)
                    numrows +=1
                l +=1
            if (len(textbuffer)):
                text_line.append(textbuffer)

        else :
            applog("Message of the day" ,"Message fits in one row...")
            if len(daily_message):
                applog("Message of the day" ,"Using only one row here.")
                text_line.append(daily_message)
                t_g, t_g, test_t_w, test_t_h = draw_black.textbbox((0,0),daily_message, font=font.SFQuote)
            else :
                text_line = "Oops there is a bug here..."
                dashboard.quote.quote_author = "Dashboard Ai Error ;("
                t_g, t_g, test_t_w, test_t_h = draw_black.textbbox((0,0),daily_message, font=font.SFQuote)
                applog("Message of the day" ,"QUOTE IS EMPTY!.")

        # Get number of arrays generated
        qs = len(text_line)
        qc = 0
        #qx = 20
    
        g_w = 0
        q_h = 0
        q_w = 0
    
        tq_g, tq_g, tq_w, tq_h = draw_black.textbbox((0,0),daily_message, font=font.SFQuote)

        #Getting the widest line of text
        row = 0
        for i in text_line:
            #print(i)
            row +=1
            tq_g, tq_g, tq_w, tq_h = draw_black.textbbox((0,0),i, font=font.SFQuote)
            q_h = tq_h
            if tq_w > q_w :
                q_w = tq_w


        quote_total_height = int(tq_h * qs)
        
        aqG, aqG, aq_w, aq_h = draw_black.textbbox((0,0),"- "+dashboard.quote.quote_author, font=font.SFQuoteAuthor)

        quote_total_height = int(quote_total_height + aq_h)

        applog("Message of the day","Total message height is "+str(quote_total_height))
        applog("Message of the day","Total rows "+str(row+1))

        #Writing the quote line by line.
        qc = 0

        # Setting gTy to be in the middle

        gTy = screen.middle_h - int(quote_total_height/2)

        # Setting gTy to be in the middle

        gTx = x + int(quote_icon.size[0]+2)

        ### PRINTING THE QUOTE ON THE SCREEN HERE.

        while qc < qs:
            tq_g, tq_g, tq_ww, tq_g = draw_black.textbbox((0,0),text_line[qc], font=font.SFQuote)
            gTx = screen.middle_w - int(tq_ww/2)
            draw_black.text((gTx, gTy), text_line[qc], font=font.SFQuote, fill=black)
            #print(text_line[qc])
            qc += 1
            gTy = gTy + int(q_h)
            if qc == 1:
                gTx = gTx + 20
        
        qG, qG, q_w, q_h = draw_black.textbbox((0,0),"- "+dashboard.quote.quote_author, font=font.SFQuoteAuthor)
        gTx = int(screen.middle_w - q_w/2)
        
        
        gTy = gTy -2
        if screen.use_red == 1:
            draw_red.text((gTx, gTy), "- "+dashboard.quote.quote_author, font=font.SFQuoteAuthor, fill=black)
        else :
            draw_black.text((gTx, gTy), "- "+dashboard.quote.quote_author, font=font.SFQuoteAuthor, fill=black)
    
        gTy = gTy + int(q_h) + 2
        #screen_y = int(gTy)

        ###########################
        # End of Message of the day
        ###########################
    else:
         applog("Dashboard","Quote of the day feature : OFF or Skipped due to to-do active and preset")


    # MASK Section
    if dashboard.show_weather ==1 :

        if today_aqi.aqi_value > 100:

            mask_icon = Image.open(os.path.join(picdir, "Mask.png"))

            shape = [(0, screen_y), (screen.width, int(mask_icon.height + screen_y))]
            # create rectangle image 
            draw_black.rectangle(shape, fill = white)
            draw_red.rectangle(shape, fill = white) 


            x = 10
            y = screen_y
            draw_black.line([(x, y), (int(screen.width - (x*2)), y)], black)

            y = y + 4
            print(x)
            print(y)
            imageB.paste(mask_icon, (x,y), mask_icon)

            mtx = x + int(mask_icon.width) + 8
            mty = y + 8
            mask_text = today_aqi.aqi_message
            mask_g, mask_g, mask_w, mask_h = draw_black.textbbox((0,0),mask_text, font = font.SFReminder)
            draw_black.text((mtx,mty),mask_text, font = font.SFReminder, fill=black)
            
            y = int(screen_y + mask_icon.height + 8) 
            draw_black.line([(x, y), (int(screen.width - (x*2)), y)], black)
            y = y + 6
            #screen_y = y


    #  #  # ######   ##   ##### #    # ###### #####     ####### BAR    
    #  #  # #       #  #    #   #    # #      #    # 
    #  #  # #####  #    #   #   ###### #####  #    # 
    #  #  # #      ######   #   #    # #      #####  
    #  #  # #      #    #   #   #    # #      #   #  
     ## ##  ###### #    #   #   #    # ###### #    # 
 
    if dashboard.show_weather == 1:
   
        t_G, t_G, test_t_w, test_t_h = draw_black.textbbox((0,0),"Weather :", font=font.SFWdetails_semibold)
        weatherbar_h = int(test_t_h * 3) + 18


        x = 10
        #y = screen_y
        y = screen.height - weatherbar_h # Putting this at the bottom of the screen
        draw_black.line([(x, y), (int(screen.width - (x*2)), y)], black)

        applog("Weather feature","Weather feature ON, Building weather bar...")
        y = y + 1
        bottom_weather_top_y = y
        draw_black.text((x,y),"Weather :", font = font.SFWdetails_semibold, fill = black)
        t_G, t_G, test_t_w, test_t_h = draw_black.textbbox((0,0),"Weather :", font=font.SFWdetails_semibold)
        x = x + test_t_w
        weather_title_x = x

        # Todays Weahter Icon:      
        weather_cond_icon = Image.open(os.path.join(weatherdir, today_forecast.icon+'.png'))
        weather_cond_icon = weather_cond_icon.resize((int(weather_cond_icon.size[0] /2.5), int(weather_cond_icon.size[1] / 2.5)))
    
        weather_pop_icon = Image.open(os.path.join(weatherdir, 'rain.png'))
        weather_pop_icon = weather_pop_icon.resize((int(weather_pop_icon.size[0] /1.5), int(weather_pop_icon.size[1] / 1.5)))
    
        weather_sunrise_icon = Image.open(os.path.join(weatherdir, 'SunRise.png'))
        weather_sunrise_icon = weather_sunrise_icon.resize((int(weather_sunrise_icon.size[0] /1.5), int(weather_sunrise_icon.size[1] / 1.5)))
        imageB.paste(weather_cond_icon, (x,(y+1)),weather_cond_icon)
        x = x + int(weather_cond_icon.size[0]+ 4)

        
        # Weather string:
        fc_string = today_forecast.condition.capitalize()
        wetaher_string = fc_string+" | H:"+str(round(today_weather.temp_high,1))+"\N{DEGREE SIGN}"+" L:"+str(round(today_weather.temp_low,1))+"\N{DEGREE SIGN}"
        popp = int(today_forecast.pop * 100)
    
        draw_black.text((x,y),wetaher_string , font = font.SFWdetails_semibold, fill = black)
        t_G, t_G, test_t_w, test_t_h = draw_black.textbbox((0,0),wetaher_string, font=font.SFWdetails_semibold)
        x = x + test_t_w + 2
        if popp > 0:
            imageB.paste(weather_pop_icon, (x,(y+3)),weather_pop_icon)
            x = x + int(weather_pop_icon.size[0]) + 2
            draw_black.text((x,y),str(popp)+"%" , font = font.SFWdetails_semibold, fill = black)
            t_G, t_G, test_t_w, test_t_h = draw_black.textbbox((0,0),str(popp)+"%", font=font.SFWdetails_semibold)
            x = x + int(test_t_w) + 2
        if screen.use_red == 1:
            imageR.paste(weather_sunrise_icon, (x,(y+2)),weather_sunrise_icon)
        else:
            imageB.paste(weather_sunrise_icon, (x,(y+2)),weather_sunrise_icon)
        x = x + int(weather_sunrise_icon.size[0]) +2
        sunrise_text = datetime.fromtimestamp(today_weather.sun_rise).strftime('%H:%M')
        draw_black.text((x,y), sunrise_text, font = font.SFWdetails_semibold, fill = black)
        t_G, t_G, test_t_w, test_t_h = draw_black.textbbox((0,0),sunrise_text, font=font.SFWdetails_semibold)
        x = int(x + test_t_w)

        weather_sunset_icon = Image.open(os.path.join(weatherdir, 'SunSet.png'))
        weather_sunset_icon = weather_sunset_icon.resize((int(weather_sunset_icon.size[0] /1.5), int(weather_sunset_icon.size[1] / 1.5)))
        imageB.paste(weather_sunset_icon, (x,(y+1)),weather_sunset_icon)
        x = x + int(weather_sunset_icon.size[0]+ 4)
        sunset_text = datetime.fromtimestamp(today_weather.sun_set).strftime('%H:%M')
        draw_black.text((x,y), sunset_text, font = font.SFWdetails_semibold, fill = black)
        #applog("DEBUG,sunset",sunset_text)


        # Weather string second row:

        #Load the right feels like icon


        fl_icon = Image.open(os.path.join(weatherdir, "t.png"))
        fl_icon_red = 0
        if today_weather.feelslike < today_weather.temperature :
            fl_icon = Image.open(os.path.join(weatherdir, "temp_low.png"))

        if today_weather.feelslike > today_weather.temperature  :
            fl_icon = Image.open(os.path.join(weatherdir, "temp_high.png"))
            fl_icon_b = Image.open(os.path.join(weatherdir, "temp_high_b.png"))
            fl_icon_r =  Image.open(os.path.join(weatherdir, "temp_high_r.png"))
            fl_icon_b = fl_icon_b.resize((int(fl_icon_b.size[0] /1.5), int(fl_icon_b.size[1] / 1.5)))
            fl_icon_r = fl_icon_r.resize((int(fl_icon_r.size[0] /1.5), int(fl_icon_r.size[1] / 1.5)))
            fl_icon_red = 1
        fl_icon = fl_icon.resize((int(fl_icon.size[0] /1.5), int(fl_icon.size[1] / 1.5)))

        if today_weather.icon == "EE":
            feels_like_text = "?"
        else:
            feels_like_text = str(round(today_weather.feelslike,1))+"\N{DEGREE SIGN}"

        wetaher_string = feels_like_text+" AQI:"+today_aqi.aqi_status+" ("+str(today_aqi.aqi_value)+")"
        x = weather_title_x
        y = y + int(test_t_h) + 2
        
        if screen.use_red == 0:
            imageB.paste(fl_icon, (x,(y+1)),fl_icon)
            x = x + int(fl_icon.size[0]+ 4)
        else:
            if fl_icon_red == 1:
                imageB.paste(fl_icon_b, (x,(y+1)),fl_icon_b)
                imageR.paste(fl_icon_r, (x,(y+1)),fl_icon_r)
                x = x + int(fl_icon_b.size[0]+ 4)
            else:
                imageB.paste(fl_icon, (x,(y+1)),fl_icon)
                x = x + int(fl_icon.size[0]+ 4)

        draw_black.text((x,y),wetaher_string , font = font.SFWdetails_semibold, fill = black)


        y = y + int(test_t_h) + 2
        y = y + 5
        x = 10
        draw_black.line([(x, y), (int(screen.width - (x*2)), y)], black)
        bottom_weather_bottom_y = y


        applog("Bottom weather banner","Now checking if we need to show garbage icon...")
        # Now checking if we need to show garbage icon...
        garbageicon = Image.open(os.path.join(picdir, "Garbage_Trash.png"))
        gby_height = int( bottom_weather_bottom_y - bottom_weather_top_y)
        gby = int( bottom_weather_top_y + (gby_height/2) )
        gbx = int(screen.width - garbageicon.size[0]) - 10
        gby = gby - int(garbageicon.size[1]/2)

        #print("gby_height: "+str(gby_height))
        #print("gby: "+str(gby))
        #garbageRecycleicon = Image.open(os.path.join(picdir, "Garbage_Recycle.png"))
        #garbageTrashicon = Image.open(os.path.join(picdir, "Garbage_Trash.png"))
        #garbageComposticon = Image.open(os.path.join(picdir, "Garbage_Compost.png"))

        todo_items = 3
        
        if GenGarbage.compostDay or GenGarbage.garbageDay or GenGarbage.recycleDay:
            applog("Bottom weather banner","we need to show garbage icon(s)...")
            for x in range(todo_items):

                if GenGarbage.garbageDay:
                    garbageicon = Image.open(os.path.join(picdir, "Garbage_Trash.png"))
                    imageB.paste(garbageicon, (gbx,gby), garbageicon)
                    gbx = gbx - int(garbageicon.size[0] + 5)
                    applog("Bottom weather banner","we need to show Trash , gbx="+str(gbx))
                    GenGarbage.garbageDay = False


                if GenGarbage.recycleDay:
                    garbageicon = Image.open(os.path.join(picdir, "Garbage_Recycle.png"))
                    imageB.paste(garbageicon, (gbx,gby), garbageicon)
                    gbx = gbx - int(garbageicon.size[0] + 5)
                    applog("Bottom weather banner","we need to show recycle , gbx="+str(gbx))
                    GenGarbage.recycleDay = False
 
                if GenGarbage.compostDay:
                    garbageicon = Image.open(os.path.join(picdir, "Garbage_Compost.png"))
                    imageB.paste(garbageicon, (gbx,gby), garbageicon)
                    gbx = gbx - int(garbageicon.size[0] + 5)
                    applog("Bottom weather banner","we need to show compost , gbx="+str(gbx))
                    GenGarbage.compostDay = False



    else:
        applog("Weather feature","Feature is OFF")
        y = y + 5

    

    hourglass.last_refresh = salute_text+", "+hourglass.last_refresh
    applog("Dashoard","Show the last refresh text at the bottom, centered "+hourglass.last_refresh)
    t_G, t_G, test_t_w, test_t_h = draw_black.textbbox((0,0),hourglass.last_refresh, font=font.SFMonth)
    gTx = int(screen.middle_w) - int(test_t_w/2)
    gTy = screen.height - int(test_t_h + 4)
    draw_black.text((gTx, gTy), hourglass.last_refresh, font=font.SFMonth, fill=black)

    if dashboard.show_power == 1:
        # DEBUG BATTERY
        #battlevel.state = "Not Charging"
        #battlevel.level = 10
    
        applog("Dashoard","Getting battery status and level...")
        battlevel = get_pibatt()

        if battlevel.level !=-1: #Checking if battery level can be goten -1 means error
            applog("Dashoard","Loading battery icon and drawing status bottom left")
            applog("Dashboard","Battery state: "+battlevel.state+" @ "+str(battlevel.level)+"%")
            if battlevel.state == "Charging":
                if battlevel.level <100:
                    batt_icon = Image.open(os.path.join(picdir, 'Battery_chrg.png'))
                else:
                    batt_icon = Image.open(os.path.join(picdir, 'Battery_chrg_full.png'))
                btx = 5
                bty = (screen.height) - int(batt_icon.height)
                imageB.paste(batt_icon, (btx,bty), batt_icon)
            else:
                if battlevel.level > 20:
                    if battlevel.level == 100:
                        batt_icon = Image.open(os.path.join(picdir, 'Battery_full.png'))
                    else:
                        batt_icon = Image.open(os.path.join(picdir, 'Battery.png'))
                        batt_load_txt = str(battlevel.level)
                    btx = 5
                    bty = (screen.height) - int(batt_icon.height)
                    imageB.paste(batt_icon, (btx,bty), batt_icon)
                    if battlevel.level < 100:
                        t_G, t_G, batt_t_w, batt_t_h = draw_black.textbbox((0,0),batt_load_txt, font=font.SFMonth)
                        btx = btx + int(batt_icon.width/2)
                        btx = btx - int(batt_t_w/2)
                        bty = bty + int(batt_t_h/2)
                        draw_black.text((btx, bty), batt_load_txt, font=font.SFMonth, fill = black)
                else:
                    if screen.use_red == 1:
                        batt_iconB = Image.open(os.path.join(picdir, 'Battery_low_B.png'))
                        batt_iconR = Image.open(os.path.join(picdir, 'Battery_low_R.png'))
                        btx = 5
                        bty = (screen.height) - int(batt_iconB.height)
                        imageB.paste(batt_iconB, (btx,bty), batt_iconB)
                        imageR.paste(batt_iconR, (btx,bty), batt_iconR)
                    else:
                        batt_icon = Image.open(os.path.join(picdir, 'Battery_low.png'))
                        btx = 5
                        bty = (screen.height) - int(batt_icon.height)
                        bty = bty - 4
                        imageB.paste(batt_icon, (btx,bty), batt_icon)
        else:
            applog("Dashboard","Battery not found!")
            batt_icon = Image.open(os.path.join(picdir, 'Battery_no_batt.png'))
            btx = 5
            bty = (screen.height) - int(batt_icon.height)
            imageB.paste(batt_icon, (btx,bty), batt_icon)
    else:
        applog("Dasboard","Show Power is OFF")



    #Save screenshot
    #s_b = imageB.convert('RGBA')
    #s_r = imageR.convert('RGBA')
    #s_b.save("InkFrame_B.png", format='png')
    #s_r.save("InkFrame_R.png", format='png')
    epd.display(epd.getbuffer(imageB),epd.getbuffer(imageR))
    #epd.display(epd.getbuffer(imageR),epd.getbuffer(imageB))
    epd.sleep()


def DayDash():
    applog("DayScreen","Initializing...")    
    try:

        epd = epd7in5b_V2.EPD()
        epd.init()
        #epd.Clear()
        screen.height = epd.height
        screen.width = epd.width
        screen.middle_w = screen.width/2
        screen.middle_h = screen.height/2
    except IOError as e:
        applog("Screen init error:" ,e)

    except KeyboardInterrupt:
        applog("System runtime" ,"ctrl + c:")
        epd7in5b_V2.epdconfig.module_exit()
        exit()

    # Check if we should clear the E-ink (daily)
    if screen.clean_screen < int(datetime.now().strftime("%d")):
        if "noclean" in performance.cli:
            applog("System runtime" ,"Screen cleaning skipped")
            performance.cli = ""
        else:
            applog("System runtime" ,"Time to clean the screen - once daily")
            epd.Clear()
            screen.clean_screen = int(datetime.now().strftime("%d"))
            applog("System runtime" ,"Re-loading config parameters daily.")


    black = 'rgb(0,0,0)'
    white = 'rgb(255,255,255)'
    grey = 'rgb(206,206,206)'

    w_x = 10
    w_y = 75
    w_icon_offset = 170
    w_icon_row_height = 40


    imageB = Image.new('L', (epd.width, epd.height), 255)  # 255: clear the frame
    imageR = Image.new('L', (epd.width, epd.height), 255)  # 255: clear the frame

    draw_black = ImageDraw.Draw(imageB)
    draw_red = ImageDraw.Draw(imageR)

    # Find out how many characters pixels per line of screen for Quotes
    screen.quote_max = screen.width - 100

    # Find out how many characters per line of screen for Reminder text
    screen.reminder_max = screen.width - 40

    screen.offset = 95

    header_Day = datetime.now().strftime("%A")
    header_Day_short = datetime.now().strftime("%a")
    header_Month_Date = datetime.now().strftime("%b %-d")
    header_Month = datetime.now().strftime("%b")
    header_Date = datetime.now().strftime("%-d")

    header_Day_t_size = draw_black.textbbox((0, 0), header_Day, font=font.DayTitle)
    header_Date_t_size = draw_black.textbbox((0, 0), header_Date, font=font.SFDate)
    header_Month_t_size = draw_black.textbbox((0, 0), header_Month, font=font.SFMonth)
    header_Day_w = header_Day_t_size[2] + header_Day_t_size[0]
    header_Day_h = header_Day_t_size[3]
    header_Month_w = header_Month_t_size[2]
    header_Month_h = header_Month_t_size[3]
    header_date_w = header_Date_t_size[2]
    header_date_h = header_Date_t_size[3]

    x_master = 10
    y_master = 10
    can_show_quote = True



    if dashboard.show_weather == 1:
        applog("Dashboard","Weather feature ON")
        applog("Weather feature","Getting current AQI")
        today_aqi = current_aqi()

        applog("Dashboard","Weather feature ON")
        applog("Weather feature","Getting current weather")
        today_weather = current_weather()
        weather_error = today_weather.error

        applog("Weather feature","Getting weather forecast")
        forecast_weather = tomorrow_weather()
        today_forecast = forecast_weather[0]
        tomorrow_forecast = forecast_weather[1]
        applog("Weather feature","Getting weather forecast, DONE")


    salute_text = "Hello"
    if hourglass.curenttime >= 0 and hourglass.curenttime <=6:
        salute_text = "Hey earlybird!"
    if hourglass.curenttime >= 7 and hourglass.curenttime <=11:
        salute_text = "Good Morning"
    if hourglass.curenttime > 12 and hourglass.curenttime <=15:
        salute_text = "Good Afternoon"
    if hourglass.curenttime > 16 and hourglass.curenttime <=19:
        salute_text = "Good Afternoon"
    if hourglass.curenttime > 20 and hourglass.curenttime <=22:
        salute_text = "Good Evening"
    if hourglass.curenttime > 22 :
        salute_text = "Bed time..."

 #   applog("dashboard.show_todo",str(dashboard.show_todo))
    if dashboard.show_todo == 1 :

        ############
            ####
            ####
            ####
            ####
            ####
        

        applog("Dashboard" ,"Todoist feature : ON, checing for Garbage items...")

        GenGarbage.garbageDay = False
        GenGarbage.compostDay = False
        GenGarbage.recycleDay = False



        if dashboard.todo_filter == "TODAY":
            applog("Todoist feature" ,"Getting only todo's due today...")
            show_dude_date = False
            today_todo_list = getodolistbyduedate(datetime.now())
        else:
            applog("Todoist feature" ,"Getting all todos due...")
            show_dude_date = True
            today_todo_list = gettodolist()
        numtodos = len(today_todo_list)
        applog("To-do","Checking if there are any triggers..")
        applog("To-do","Trigers: "+dashboard.todo_garbage+", "+dashboard.todo_compost+", "+dashboard.todo_recycle)

        if numtodos > 0:

            for tsk in today_todo_list:
                tsk_title = tsk.content.replace('\n', '')

                if dashboard.todo_garbage in tsk_title:
                    applog("Todoist feature" ,"Its garbage day today")
                    GenGarbage.garbageDay = True

                if dashboard.todo_compost in tsk_title:
                    applog("Todoist feature" ,"Its compost day today")
                    GenGarbage.compostDay = True

                if dashboard.todo_recycle in tsk_title:
                    applog("Todoist feature" ,"Its recycle day today")
                    GenGarbage.recycleDay = True


    applog("Dashboard" ,"Drawing todays day")

    x = 10
    y = 2
    screen_y = y
    draw_black.text((x,y), header_Day, font = font.DayTitle, fill = black)
    t_G, t_G, test_t_w, test_t_h = draw_black.textbbox((0,0),header_Day, font=font.DayTitle)
    screen_y = y + test_t_h

    if dashboard.show_weather == 1:

        weather_cond_icon = Image.open(os.path.join(weatherdir, today_weather.icon+'.png'))


        fl_icon = Image.open(os.path.join(weatherdir, "t.png"))
        fl_icon_red = 0
        if today_weather.feelslike < today_weather.temperature :
            fl_icon = Image.open(os.path.join(weatherdir, "temp_low.png"))

        if today_weather.feelslike > today_weather.temperature  :
            fl_icon = Image.open(os.path.join(weatherdir, "temp_high.png"))
            fl_icon_b = Image.open(os.path.join(weatherdir, "temp_high_b.png"))
            fl_icon_r =  Image.open(os.path.join(weatherdir, "temp_high_r.png"))     
            fl_icon_red = 1

        if today_weather.icon == "EE":
            today_temp = "?"
        else:
            today_temp = str(round(today_weather.temperature,1))+"\N{DEGREE SIGN}"
            today_feels_temp = "("+str(round(today_weather.feelslike,1))+"\N{DEGREE SIGN})"
        x = int(x + test_t_w + 8)
        i_off = int ( (y + (test_t_h/2)) - (fl_icon.size[1]/2))

        imageB.paste(weather_cond_icon, (x,(y+8)),weather_cond_icon)

        x = x + weather_cond_icon.width


        if screen.use_red == 0:
            imageB.paste(fl_icon, (x,(y+i_off)),fl_icon)
            x = x + int(fl_icon.size[0]+ 4)
        else:
            if fl_icon_red == 1:
                imageB.paste(fl_icon_b, (x,(y+i_off)),fl_icon_b)
                imageR.paste(fl_icon_r, (x,(y+i_off)),fl_icon_r)
                x = x + int(fl_icon_b.size[0]+ 4)
            else:
                imageB.paste(fl_icon, (x,(y+i_off)),fl_icon)
                x = x + int(fl_icon.size[0]+ 4)
        draw_black.text((x,y), today_temp, font = font.DayTitle, fill = black)
        t_G, t_G, test_t_w, test_t_h = draw_black.textbbox((0,0),today_temp, font=font.DayTitle)
        x = x + test_t_w
        xt_G, xt_G, xtest_t_w, xtest_t_h = draw_black.textbbox((0,0),today_temp, font=font.SFReminder)
        y = y + int(xtest_t_h/2)
        draw_black.text((x,y), today_feels_temp, font = font.SFReminder, fill = black)




    screen_y = y + test_t_h

    cal_icon = Image.open(os.path.join(picdir, 'calendar_header.png'))
    cal_icon_R = Image.open(os.path.join(picdir, 'calendar_header_R.png'))
    cal_icon_B = Image.open(os.path.join(picdir, 'calendar_header_B.png'))
    
    xcal = int(screen.middle_w - (cal_icon.size[0] * 2))
    xcal = int(screen.width - (cal_icon.size[0])) - 20
    
    ycal = y + 6
   
    if screen.use_red == 1:
        imageR.paste(cal_icon_R, (xcal,ycal), cal_icon_R)
        imageB.paste(cal_icon_B, (xcal,ycal), cal_icon_B)
    else :
        imageB.paste(cal_icon, (xcal,ycal), cal_icon) 

    y = ycal + (int(cal_icon.size[1]/2) - int(header_date_h/2)) + 1
    x = xcal + (int(cal_icon.size[0]/2) - int(header_date_w/2))

    draw_black.text((x, y), header_Date, font = font.SFDate, fill = black)

    y = ycal + 2
    x = xcal + (int(cal_icon.size[0]/2) - int(header_Month_w/2))
    if screen.use_red == 1:
        draw_red.text((x, y), header_Month, font = font.SFMonth, fill=white)
    else:
        draw_black.text((x, y), header_Month, font = font.SFMonth, fill=white)

    screen_y = int(y + test_t_h) +10

    # Quote Section

           #######
        ####     ####
        ####     #### 
        ####     ####
        ####     #### 
            #######  ###
    if dashboard.show_quote == 1 and can_show_quote:
        applog("Dashboard","Quote of the day feature : ON")
        y = screen_y

        quote_icon = Image.open(os.path.join(picdir, "quote_icon.png"))
        quote_iconB = Image.open(os.path.join(picdir, "quote_b.png"))
        quote_iconR = Image.open(os.path.join(picdir, "quote_r.png"))
        quotebar_icon = Image.open(os.path.join(picdir, "quote_bar_top.png"))

        qx = w_x
        qy = y + 12
        x = 10

        qml = dashboard.quote_length
        qll = qml+1
        qmaxtries = 0


        if hourglass.currentday != int(datetime.now().day):
            applog("Message of the day" ,"Time to get a new message...")
            applog("Message of the day" ,"Getting a message under "+str(qml)+" lenght")

            while qll >= qml :
                applog("Message state","Getting a quote")
                applog("Message of the day" ,"Getting random quote from local database...")
                dashboard.quote = quotefromfile("quotes.txt")
                qll = len(dashboard.quote.quote_text)
                qmaxtries +=1
                if qmaxtries > 10:
                    break

                if qll >  qml:
                    applog("Message of the day" ,"Message Feature : Attempt: "+str(qmaxtries))
                else:
                    applog("Message of the day" ,"Message lenght is "+str(qll))
            hourglass.currentday = int(datetime.now().day)
        else:
            applog("Message of the day" ,"Keeping current message message...")
            qll = len(dashboard.quote.quote_text)
            
        #FIXME
        #dashboard.quote.quote_text = "One line quote."
        #dashboard.quote.quote_author = "Dashboard Ai Error ;("
        #qll = len(dashboard.quote.quote_text)


        if qll == 0 or qll > qml:
            applog("Quote of the day" ,"Max attempts to get a short enough quote exhausted.")
            #Just in case we could not find a short enough quote in 10 attempts.
            dashboard.quote.quote_text = "A quote was not found..."
            dashboard.quote.quote_author = "Dashboard Ai Error ;("
            hourglass.currentday = -1

        daily_message = dashboard.quote.quote_text
        
        #print("Now trying to slice the text in chunks")
        text_g, text_g, test_t_w, test_t_h = draw_black.textbbox((0,0),daily_message, font=font.SFQuote)
        text_max = test_t_w
        toff = x + int(quote_icon.size[0]+2)
        toff = 0
        screen.offset = int( quote_icon.size[0] + (x_master * 2) )
        text_line_max = screen.quote_max - (toff + screen.offset)

        text_line = []
        textbuffer = ""
        onlyOneRow = False

        #Split the quote into words in an array

        quote_words = daily_message.split()
        wl = len(quote_words)

        #See if the total is larger than the text_line_max value set.
        applog("Message of the day" ,"Max pixels per line is "+str(text_line_max))
        applog("Message of the day" ,daily_message)
        t_g, t_g, test_t_w, test_t_h = draw_black.textbbox((0,0),daily_message, font=font.SFQuote)



        if test_t_w > text_line_max:
            applog("Message of the day" ,"We need to split this message over many rows...")

            l = 0
            ql = len(quote_words)
            numrows = 0
            while l < ql:
                textbuffer = textbuffer + quote_words[l] + " "
                t_g, t_g, test_t_w, test_t_h = draw_black.textbbox((0,0),textbuffer, font=font.SFQuote)
                #print("Witdh of line "+str(numrows)+" is "+str(test_t_w))
                try:
                    t_g, t_g, test_t_w, test_t_h = draw_black.textbbox((0,0),textbuffer+quote_words[l+1], font=font.SFQuote)
                except:
                    applog("Message of the day" ,"done with the rows...")
                if test_t_w >= text_line_max:
                    text_line.append(textbuffer)
                    textbuffer = ""
                    #print(l)
                    numrows +=1
                l +=1
            if (len(textbuffer)):
                text_line.append(textbuffer)

        else :
            applog("Message of the day" ,"Message fits in one row...")
            if len(daily_message):
                applog("Message of the day" ,"Using only one row here.")
                text_line.append(daily_message)
                t_g, t_g, test_t_w, test_t_h = draw_black.textbbox((0,0),daily_message, font=font.SFQuote)
            else :
                text_line = "Oops there is a bug here..."
                dashboard.quote.quote_author = "Dashboard Ai Error ;("
                t_g, t_g, test_t_w, test_t_h = draw_black.textbbox((0,0),daily_message, font=font.SFQuote)
                applog("Message of the day" ,"QUOTE IS EMPTY!.")

        # Get number of arrays generated
        qs = len(text_line)
        qc = 0
        #qx = 20
    
        g_w = 0
        q_h = 0
        q_w = 0
    
        tq_g, tq_g, tq_w, tq_h = draw_black.textbbox((0,0),daily_message, font=font.SFQuote)

        #Getting the widest line of text
        row = 0
        for i in text_line:
            #print(i)
            row +=1
            tq_g, tq_g, tq_w, tq_h = draw_black.textbbox((0,0),i, font=font.SFQuote)
            q_h = tq_h
            if tq_w > q_w :
                q_w = tq_w


        quote_total_height = int(tq_h * qs)
        
        aqG, aqG, aq_w, aq_h = draw_black.textbbox((0,0),"- "+dashboard.quote.quote_author, font=font.SFQuoteAuthor)

        quote_total_height = int(quote_total_height + aq_h)

        applog("Message of the day","Total message height is "+str(quote_total_height))
        applog("Message of the day","Total rows "+str(row+1))

        #Writing the quote line by line.
        qc = 0

        # Setting gTy to be in the middle

        gTy = screen.middle_h - int(quote_total_height/2)

        # Setting gTy to be in the middle

        gTx = x + int(quote_icon.size[0]+2)

        ### PRINTING THE QUOTE ON THE SCREEN HERE.

        while qc < qs:
            tq_g, tq_g, tq_ww, tq_g = draw_black.textbbox((0,0),text_line[qc], font=font.SFQuote)
            gTx = screen.middle_w - int(tq_ww/2)
            draw_black.text((gTx, gTy), text_line[qc], font=font.SFQuote, fill=black)
            #print(text_line[qc])
            qc += 1
            gTy = gTy + int(q_h)
            if qc == 1:
                gTx = gTx + 20
        
        qG, qG, q_w, q_h = draw_black.textbbox((0,0),"- "+dashboard.quote.quote_author, font=font.SFQuoteAuthor)
        gTx = int(screen.middle_w - q_w/2)
        
        
        gTy = gTy -2
        if screen.use_red == 1:
            draw_red.text((gTx, gTy), "- "+dashboard.quote.quote_author, font=font.SFQuoteAuthor, fill=black)
        else :
            draw_black.text((gTx, gTy), "- "+dashboard.quote.quote_author, font=font.SFQuoteAuthor, fill=black)
    
        gTy = gTy + int(q_h) + 2
        #screen_y = int(gTy)

        ###########################
        # End of Message of the day
        ###########################
    else:
         applog("Dashboard","Quote of the day feature : OFF or Skipped due to to-do active and preset")



    # MASK Section
    if dashboard.show_weather ==1 :

        if today_aqi.aqi_value > 100:

            mask_icon = Image.open(os.path.join(picdir, "Mask.png"))

            shape = [(0, screen_y), (screen.width, int(mask_icon.height + screen_y))]
            # create rectangle image 
            draw_black.rectangle(shape, fill = white)
            draw_red.rectangle(shape, fill = white) 


            x = 10
            y = screen_y
            draw_black.line([(x, y), (int(screen.width - (x*2)), y)], black)

            y = y + 4
            #print(x)
            #print(y)
            imageB.paste(mask_icon, (x,y), mask_icon)

            mtx = x + int(mask_icon.width) + 8
            mty = y + 8
            mask_text = today_aqi.aqi_message
            mask_g, mask_g, mask_w, mask_h = draw_black.textbbox((0,0),mask_text, font = font.SFReminder)
            draw_black.text((mtx,mty),mask_text, font = font.SFReminder, fill=black)
            
            y = int(screen_y + mask_icon.height + 8) 
            draw_black.line([(x, y), (int(screen.width - (x*2)), y)], black)
            y = y + 6
            #screen_y = y


    #  #  # ######   ##   ##### #    # ###### #####  
    #  #  # #       #  #    #   #    # #      #    # 
    #  #  # #####  #    #   #   ###### #####  #    # 
    #  #  # #      ######   #   #    # #      #####  
    #  #  # #      #    #   #   #    # #      #   #  
     ## ##  ###### #    #   #   #    # ###### #    # 
 
    if dashboard.show_weather == 1:
    
        t_G, t_G, test_t_w, test_t_h = draw_black.textbbox((0,0),"Weather: ", font=font.SFWdetails_semibold)
        weatherbar_h = int(test_t_h * 3) + 18


        x = 10
        #y = screen_y
        y = screen.height - weatherbar_h # Putting this at the bottom of the screen
        draw_black.line([(x, y), (int(screen.width - (x*2)), y)], black)

        applog("Weather feature","Weather feature ON, Building weather bar...")
        y = y + 1
        bottom_weather_top_y = y
        draw_black.text((x,y),"Weather: ", font = font.SFWdetails_semibold, fill = black)
        t_G, t_G, test_t_w, test_t_h = draw_black.textbbox((0,0),"Weather: ", font=font.SFWdetails_semibold)
        x = x + test_t_w
        weather_title_x = x

        # Todays Weahter Icon:      
        weather_cond_icon = Image.open(os.path.join(weatherdir, today_weather.icon+'.png'))
        weather_cond_icon = weather_cond_icon.resize((int(weather_cond_icon.size[0] /2.5), int(weather_cond_icon.size[1] / 2.5)))
    
        weather_pop_icon = Image.open(os.path.join(weatherdir, 'rain.png'))
        weather_pop_icon = weather_pop_icon.resize((int(weather_pop_icon.size[0] /1.5), int(weather_pop_icon.size[1] / 1.5)))
    
        weather_sunrise_icon = Image.open(os.path.join(weatherdir, 'SunRise.png'))
        weather_sunrise_icon = weather_sunrise_icon.resize((int(weather_sunrise_icon.size[0] /1.5), int(weather_sunrise_icon.size[1] / 1.5)))
        imageB.paste(weather_cond_icon, (x,(y+1)),weather_cond_icon)
        x = x + int(weather_cond_icon.size[0]+ 4)

        
        # Weather string:
        fc_string = tomorrow_forecast.condition.capitalize()
        wetaher_string = fc_string+" | H:"+str(round(today_weather.temp_high,1))+"\N{DEGREE SIGN}"+" L:"+str(round(today_weather.temp_low,1))+"\N{DEGREE SIGN}"
        popp = int(today_forecast.pop * 100)
    
        draw_black.text((x,y),wetaher_string , font = font.SFWdetails_semibold, fill = black)
        t_G, t_G, test_t_w, test_t_h = draw_black.textbbox((0,0),wetaher_string, font=font.SFWdetails_semibold)
        x = x + test_t_w + 2
        if popp > 0:
            imageB.paste(weather_pop_icon, (x,(y+3)),weather_pop_icon)
            x = x + int(weather_pop_icon.size[0]) + 2
            draw_black.text((x,y),str(popp)+"%" , font = font.SFWdetails_semibold, fill = black)
            t_G, t_G, test_t_w, test_t_h = draw_black.textbbox((0,0),str(popp)+"%", font=font.SFWdetails_semibold)
            x = x + int(test_t_w) + 2
        if screen.use_red == 1:
            imageR.paste(weather_sunrise_icon, (x,(y+2)),weather_sunrise_icon)
        else:
            imageB.paste(weather_sunrise_icon, (x,(y+2)),weather_sunrise_icon)
        x = x + int(weather_sunrise_icon.size[0]) +2
        sunrise_text = datetime.fromtimestamp(today_weather.sun_rise).strftime('%H:%M')
        draw_black.text((x,y), sunrise_text, font = font.SFWdetails_semibold, fill = black)
        t_G, t_G, test_t_w, test_t_h = draw_black.textbbox((0,0),sunrise_text, font=font.SFWdetails_semibold)
        x = int(x + test_t_w)

        weather_sunset_icon = Image.open(os.path.join(weatherdir, 'SunSet.png'))
        weather_sunset_icon = weather_sunset_icon.resize((int(weather_sunset_icon.size[0] /1.5), int(weather_sunset_icon.size[1] / 1.5)))
        imageB.paste(weather_sunset_icon, (x,(y+1)),weather_sunset_icon)
        x = x + int(weather_sunset_icon.size[0]+ 4)
        sunset_text = datetime.fromtimestamp(today_weather.sun_set).strftime('%H:%M')
        draw_black.text((x,y), sunset_text, font = font.SFWdetails_semibold, fill = black)
        #applog("DEBUG,sunset",sunset_text)


        # Weather string second row:

        #Load the right feels like icon


        fl_icon = Image.open(os.path.join(weatherdir, "t.png"))
        fl_icon_red = 0
        if today_weather.feelslike < today_weather.temperature :
            fl_icon = Image.open(os.path.join(weatherdir, "temp_low.png"))

        if today_weather.feelslike > today_weather.temperature  :
            fl_icon = Image.open(os.path.join(weatherdir, "temp_high.png"))
            fl_icon_b = Image.open(os.path.join(weatherdir, "temp_high_b.png"))
            fl_icon_r =  Image.open(os.path.join(weatherdir, "temp_high_r.png"))
            fl_icon_b = fl_icon_b.resize((int(fl_icon_b.size[0] /1.5), int(fl_icon_b.size[1] / 1.5)))
            fl_icon_r = fl_icon_r.resize((int(fl_icon_r.size[0] /1.5), int(fl_icon_r.size[1] / 1.5)))
            fl_icon_red = 1
        fl_icon = fl_icon.resize((int(fl_icon.size[0] /1.5), int(fl_icon.size[1] / 1.5)))

        if today_weather.icon == "EE":
            feels_like_text = "?"
        else:
            feels_like_text = str(round(today_weather.feelslike,1))+"\N{DEGREE SIGN}"

        wetaher_string = feels_like_text+" AQI:"+today_aqi.aqi_status+" ("+str(today_aqi.aqi_value)+")"
        x = weather_title_x
        y = y + int(test_t_h) + 2
        
        if screen.use_red == 0:
            imageB.paste(fl_icon, (x,(y+1)),fl_icon)
            x = x + int(fl_icon.size[0]+ 4)
        else:
            if fl_icon_red == 1:
                imageB.paste(fl_icon_b, (x,(y+1)),fl_icon_b)
                imageR.paste(fl_icon_r, (x,(y+1)),fl_icon_r)
                x = x + int(fl_icon_b.size[0]+ 4)
            else:
                imageB.paste(fl_icon, (x,(y+1)),fl_icon)
                x = x + int(fl_icon.size[0]+ 4)

        draw_black.text((x,y),wetaher_string , font = font.SFWdetails_semibold, fill = black)


        y = y + int(test_t_h) + 2
        y = y + 5
        x = 10
        draw_black.line([(x, y), (int(screen.width - (x*2)), y)], black)
        bottom_weather_bottom_y = y

        applog("Bottom weather banner","Now checking if we need to show garbage icon...")
        # Now checking if we need to show garbage icon...
        garbageicon = Image.open(os.path.join(picdir, "Garbage_Trash.png"))
        gby_height = int( bottom_weather_bottom_y - bottom_weather_top_y)
        gby = int( bottom_weather_top_y + (gby_height/2) )
        gbx = int(screen.width - garbageicon.size[0]) - 10
        gby = gby - int(garbageicon.size[1]/2)

        #print("gby_height: "+str(gby_height))
        #print("gby: "+str(gby))
        #garbageRecycleicon = Image.open(os.path.join(picdir, "Garbage_Recycle.png"))
        #garbageTrashicon = Image.open(os.path.join(picdir, "Garbage_Trash.png"))
        #garbageComposticon = Image.open(os.path.join(picdir, "Garbage_Compost.png"))

        todo_items = 3
        
        if GenGarbage.compostDay or GenGarbage.garbageDay or GenGarbage.recycleDay:
            applog("Bottom weather banner","we need to show garbage icon(s)...")
            for x in range(todo_items):

                if GenGarbage.garbageDay:
                    garbageicon = Image.open(os.path.join(picdir, "Garbage_Trash.png"))
                    imageB.paste(garbageicon, (gbx,gby), garbageicon)
                    gbx = gbx - int(garbageicon.size[0] + 5)
                    applog("Bottom weather banner","we need to show Trash , gbx="+str(gbx))
                    GenGarbage.garbageDay = False


                if GenGarbage.recycleDay:
                    garbageicon = Image.open(os.path.join(picdir, "Garbage_Recycle.png"))
                    imageB.paste(garbageicon, (gbx,gby), garbageicon)
                    gbx = gbx - int(garbageicon.size[0] + 5)
                    applog("Bottom weather banner","we need to show recycle , gbx="+str(gbx))
                    GenGarbage.recycleDay = False
 
                if GenGarbage.compostDay:
                    garbageicon = Image.open(os.path.join(picdir, "Garbage_Compost.png"))
                    imageB.paste(garbageicon, (gbx,gby), garbageicon)
                    gbx = gbx - int(garbageicon.size[0] + 5)
                    applog("Bottom weather banner","we need to show compost , gbx="+str(gbx))
                    GenGarbage.compostDay = False


    else:
        applog("Weather feature","Feature is OFF")
        y = y + 5

    

    hourglass.last_refresh = salute_text+", "+hourglass.last_refresh
    applog("Dashoard","Show the last refresh text at the bottom, centered "+hourglass.last_refresh)
    t_G, t_G, test_t_w, test_t_h = draw_black.textbbox((0,0),hourglass.last_refresh, font=font.SFMonth)
    gTx = int(screen.middle_w) - int(test_t_w/2)
    gTy = screen.height - int(test_t_h + 4)
    draw_black.text((gTx, gTy), hourglass.last_refresh, font=font.SFMonth, fill=black)

    if dashboard.show_power == 1:
        # DEBUG BATTERY
        #battlevel.state = "Not Charging"
        #battlevel.level = 10
    
        applog("Dashoard","Getting battery status and level...")
        battlevel = get_pibatt()

        if battlevel.level !=-1: #Checking if battery level can be goten -1 means error
            applog("Dashoard","Loading battery icon and drawing status bottom left")
            applog("Dashboard","Battery state: "+battlevel.state+" @ "+str(battlevel.level)+"%")
            if battlevel.state == "Charging":
                if battlevel.level <100:
                    batt_icon = Image.open(os.path.join(picdir, 'Battery_chrg.png'))
                else:
                    batt_icon = Image.open(os.path.join(picdir, 'Battery_chrg_full.png'))
                btx = 5
                bty = (screen.height) - int(batt_icon.height)
                imageB.paste(batt_icon, (btx,bty), batt_icon)
            else:
                if battlevel.level > 20:
                    if battlevel.level == 100:
                        batt_icon = Image.open(os.path.join(picdir, 'Battery_full.png'))
                    else:
                        batt_icon = Image.open(os.path.join(picdir, 'Battery.png'))
                        batt_load_txt = str(battlevel.level)
                    btx = 5
                    bty = (screen.height) - int(batt_icon.height)
                    imageB.paste(batt_icon, (btx,bty), batt_icon)
                    if battlevel.level < 100:
                        t_G, t_G, batt_t_w, batt_t_h = draw_black.textbbox((0,0),batt_load_txt, font=font.SFMonth)
                        btx = btx + int(batt_icon.width/2)
                        btx = btx - int(batt_t_w/2)
                        bty = bty + int(batt_t_h/2)
                        draw_black.text((btx, bty), batt_load_txt, font=font.SFMonth, fill = black)
                else:
                    if screen.use_red == 1:
                        batt_iconB = Image.open(os.path.join(picdir, 'Battery_low_B.png'))
                        batt_iconR = Image.open(os.path.join(picdir, 'Battery_low_R.png'))
                        btx = 5
                        bty = (screen.height) - int(batt_iconB.height)
                        imageB.paste(batt_iconB, (btx,bty), batt_iconB)
                        imageR.paste(batt_iconR, (btx,bty), batt_iconR)
                    else:
                        batt_icon = Image.open(os.path.join(picdir, 'Battery_low.png'))
                        btx = 5
                        bty = (screen.height) - int(batt_icon.height)
                        bty = bty - 4
                        imageB.paste(batt_icon, (btx,bty), batt_icon)
        else:
            applog("Dashboard","Battery not found!")
            batt_icon = Image.open(os.path.join(picdir, 'Battery_no_batt.png'))
            btx = 5
            bty = (screen.height) - int(batt_icon.height)
            imageB.paste(batt_icon, (btx,bty), batt_icon)
    else:
        applog("Dasboard","Show Power is OFF")



    #Save screenshot
    #s_b = imageB.convert('RGBA')
    #s_r = imageR.convert('RGBA')
    #s_b.save("InkFrame_B.png", format='png')
    #s_r.save("InkFrame_R.png", format='png')
    epd.display(epd.getbuffer(imageB),epd.getbuffer(imageR))
    #epd.display(epd.getbuffer(imageR),epd.getbuffer(imageB))
    epd.sleep()

def get_dashboard_config_data(file_path:str):
    

    applog("Dashboard","Loading fonts...")
    ####################
    ###################
    #######
    #######
    ############
    ############
    #######
    #######
    #######


    font.DayTitle = ImageFont.truetype("fonts/SF-Compact-Rounded-Bold.ttf", 62)
    font.SFMonth = ImageFont.truetype("fonts/SF-Compact-Rounded-Bold.ttf", 14)
    font.SFDate = ImageFont.truetype("fonts/SF-Compact-Rounded-Bold.ttf", 42)

    font.SFToday_temp = ImageFont.truetype("fonts/SF-Compact-Rounded-Bold.ttf",64)
    font.SFToday_cond = ImageFont.truetype("fonts/SF-Compact-Rounded-Semibold.otf",32)
    font.SFToday_hl = ImageFont.truetype("fonts/SF-Compact-Rounded-Medium.otf",26)
    font.SFWdetails = ImageFont.truetype("fonts/SF-Compact-Rounded-Medium.otf",22)
    font.SFWdetails_bold = ImageFont.truetype("fonts/SF-Compact-Rounded-Bold.ttf",22)
    font.SFWdetails_semibold = ImageFont.truetype("fonts/SF-Compact-Rounded-Semibold.otf",22)
    font.SFWdetails_sub = ImageFont.truetype("fonts/SF-Compact-Rounded-Semibold.otf",16)
    font.SFWdetails_sub_bold = ImageFont.truetype("fonts/SF-Compact-Rounded-Bold.ttf",16)
    font.SFWAQI_bold = ImageFont.truetype("fonts/SF-Compact-Rounded-Bold.ttf",22)
    font.SFWAQI_bold_small = ImageFont.truetype("fonts/SF-Compact-Rounded-Bold.ttf",14)

    font.SFToDo = ImageFont.truetype("fonts/SF-Compact-Rounded-Medium.otf",24)
    font.SFToDo_sub = ImageFont.truetype("fonts/SF-Compact-Rounded-Medium.otf",16)

    font.SFQuote = ImageFont.truetype("fonts/SF-Compact-Rounded-Semibold.otf",46)
    font.SFQuoteAuthor = ImageFont.truetype("fonts/SF-Compact-Rounded-Medium.otf",36)
    font.SFReminder = ImageFont.truetype("fonts/SF-Compact-Rounded-Semibold.otf",24)
    font.SFReminder_sub = ImageFont.truetype("fonts/SF-Compact-Rounded-Semibold.otf",20)
    font.SFTransitID = ImageFont.truetype("fonts/SF-Compact-Rounded-Semibold.otf",24)
    font.SF_TransitName = ImageFont.truetype("fonts/SF-Compact-Rounded-Semibold.otf",18)
    font.SFTransitTime = ImageFont.truetype("fonts/RobotoMono-Bold.ttf",24)

    font.SleepFont = ImageFont.truetype("fonts/SF-Compact-Rounded-Semibold.otf",32)
    font.SleepFont_foot = ImageFont.truetype("fonts/SF-Compact-Rounded-Semibold.otf",24)

    applog("Dashboard","Fonts loaded...")
    applog("Dashboard","Loading dashboard.ini")
    parser = configparser.ConfigParser()
    parser.read(file_path)
    data = dict()
    
    data['screen_type-id'] = parser.get("screen-config", "screen_type")
    data['use_red-id'] = parser.get("screen-config", "use_red")
    data['refresh-rate-min-id'] = parser.get("screen-config", "refresh-rate-min")
    data['screen_sleep_hour-id'] = parser.get("screen-config", "screen_sleep_hour")
    data['screen_wake_hour-id'] = parser.get("screen-config", "screen_wake_hour")
    data['evening_hour-id'] = parser.get("screen-config", "evening_hour")
    data['delay_start_sec-id'] = parser.get("screen-config", "delay_start_sec")
    


    data['show_weather-id'] = parser.get("feature-config", "show_weather")
    data['show_weather_details-id'] = parser.get("feature-config", "show_weather_details")
    
    data['show_quote-id'] = parser.get("feature-config", "show_quote")
    data['show_quote_live-id'] = parser.get("feature-config", "show_quote_live")

    data['show_quote_lenght-id'] = parser.get("feature-config", "show_quote_lenght")


    data['show-todo-id'] = parser.get("feature-config", "show-todo")
    data['todo-rows-id'] = parser.get("feature-config", "todo-rows")
    data['todo-filter-id'] = parser.get("feature-config", "todo-filter")

    data['todo-garbage-id'] = parser.get("todo-config", "todoGarbage")
    data['todo-recycle-id'] = parser.get("todo-config", "todoRecycle")
    data['todo-compost-id'] = parser.get("todo-config", "todoCompost")


    data['show-power-id'] = parser.get("feature-config", "show-power")
    data['shutdown-after-run-id'] = parser.get("feature-config", "shutdown-after-run")
    
    
    hourglass.evening_hour = int(data['evening_hour-id'])

    screen.refresh_rate_min = int(data['refresh-rate-min-id'])
    screen.sleep_hour = int(data['screen_sleep_hour-id'])
    screen.wake_hour = int(data['screen_wake_hour-id'])

    dashboard.todo_garbage = data['todo-garbage-id']
    dashboard.todo_recycle = data['todo-recycle-id']
    dashboard.todo_compost = data['todo-compost-id']

    if data['use_red-id'] == "TRUE":
        screen.use_red = 1
        applog("System settings" ,"Red pigment is enabled")

    else:
        screen.use_red = 0

    if data['show_weather-id'] == "TRUE":
        dashboard.show_weather = 1
    else : 
        dashboard.show_weather = 0
    if data['show_weather_details-id'] == "TRUE":
        dashboard.show_weather_details = 1
    else : 
        dashboard.show_weather_details = 0



    if data['show_quote-id'] == "TRUE":
        dashboard.show_quote = 1
    else : 
        dashboard.show_quote = 0
    
    if data['show_quote_live-id'] == "TRUE":
        dashboard.show_quote_live = 1
    else : 
        dashboard.show_quote_live = 0

    if data['show-todo-id'] == "TRUE":
        dashboard.show_todo = 1
    else : 
        dashboard.show_todo = 0

    if data['show-power-id'] == "TRUE":
        dashboard.show_power = 1
    else : 
        dashboard.show_power  = 0

    if data['shutdown-after-run-id'] == "TRUE":
        dashboard.shutdown_after_run = 1
    else : 
        dashboard.shutdown_after_run  = 0

    dashboard.quote_length = int(data['show_quote_lenght-id'])
    #175


        
    
    dashboard.todo_rows = int(data['todo-rows-id'])
    dashboard.todo_filter = data['todo-filter-id']
    dashboard.delay_start_sec = int(data['delay_start_sec-id'])

    applog("Dashboard","Completed dashboard.ini")

    return data


def sleep_screen(wake_date:date):
    applog("Inkframe" ,"Sleeping screen initiated")

    black = 'rgb(0,0,0)'
    white = 'rgb(255,255,255)'


    try:

        epd = epd7in5b_V2.EPD()
        epd.init()
        epd.Clear()
        screen.height = epd.height
        screen.width = epd.width
        screen.middle_w = screen.width/2
        screen.middle_h = screen.height/2
    except IOError as e:
        applog("Inkframe" ,"error"+str(e)) 

    except KeyboardInterrupt:
        applog("Inkframe" ,"ctrl + c received") 
        epd7in5b_V2.epdconfig.module_exit()
        exit()
    imageB = Image.new('L', (epd.width, epd.height), 255)  # 255: clear the frame
    imageR = Image.new('L', (epd.width, epd.height), 255)  # 255: clear the frame
    draw_black = ImageDraw.Draw(imageB)

    #  #  # ######   ##   ##### #    # ###### #####  
    #  #  # #       #  #    #   #    # #      #    # 
    #  #  # #####  #    #   #   ###### #####  #    # 
    #  #  # #      ######   #   #    # #      #####  
     ## ##  ###### #    #   #   #    # ###### #    # 
 
    if dashboard.show_weather == 1:
        forecast_weather = tomorrow_weather()
        tomorrow_forecast = forecast_weather[1]
        tmr_g, tmr_g, tmr_w, tmr_h = draw_black.textbbox((0,0),"Tomorrow: ", font=font.SFWdetails_semibold)
        x = 10
        y = int(tmr_h)
        draw_black.text((x,y),"Tomorrow: ", font = font.SFWdetails_semibold, fill = black)
        t_G, t_G, test_t_w, test_t_h = draw_black.textbbox((0,0),"Tomorrow :", font=font.SFWdetails_semibold)
        x = int(x + test_t_w)

        # Tomorrows Weahter Icon:      
        tomorrow_cond_icon = Image.open(os.path.join(weatherdir, tomorrow_forecast.icon+'.png'))
        tomorrow_cond_icon = tomorrow_cond_icon.resize((int(tomorrow_cond_icon.size[0] /2.5), int(tomorrow_cond_icon.size[1] / 2.5)))
        tomorrow_pop_icon = Image.open(os.path.join(weatherdir, 'rain.png'))
        tomorrow_pop_icon = tomorrow_pop_icon.resize((int(tomorrow_pop_icon.size[0] /1.5), int(tomorrow_pop_icon.size[1] / 1.5)))
        tomorrow_sunrise_icon = Image.open(os.path.join(weatherdir, 'SunRise.png'))
        tomorrow_sunrise_icon = tomorrow_sunrise_icon.resize((int(tomorrow_sunrise_icon.size[0] /1.5), int(tomorrow_sunrise_icon.size[1] / 1.5)))
        imageB.paste(tomorrow_cond_icon, (x,(y+1)),tomorrow_cond_icon)
        x = x + int(tomorrow_cond_icon.size[0]+ 4)
        # Tomorrow's Weather string:
        fc_string = tomorrow_forecast.condition.capitalize()
        tomorrow_string = fc_string+" | H:"+str(round(tomorrow_forecast.temp_high,1))+"\N{DEGREE SIGN}"+" L:"+str(round(tomorrow_forecast.temp_low,1))+"\N{DEGREE SIGN}, feels like "+str(round(tomorrow_forecast.feels_like,1))+"\N{DEGREE SIGN}"
        popp = int(tomorrow_forecast.pop * 100)
        draw_black.text((x,y),tomorrow_string , font = font.SFWdetails_semibold, fill = black)
        t_G, t_G, test_t_w, test_t_h = draw_black.textbbox((0,0),tomorrow_string, font=font.SFWdetails_semibold)
        x = x + test_t_w + 2
        if popp > 0:
            imageB.paste(tomorrow_pop_icon, (x,(y+3)),tomorrow_pop_icon)
            x = x + int(tomorrow_pop_icon.size[0]) + 2
            draw_black.text((x,y),str(popp)+"%" , font = font.SFWdetails_semibold, fill = black)
            t_G, t_G, test_t_w, test_t_h = draw_black.textbbox((0,0),str(popp)+"%", font=font.SFWdetails_semibold)
            x = x + int(test_t_w) + 2

    sleep_icon = Image.open(os.path.join(picdir, 'sleep_icon.png'))

    sleep_string = "Good Night..."
    t_g, t_g, test_t_w, test_t_h = draw_black.textbbox((0,0),sleep_string, font=font.SleepFont)

    sX = int(screen.middle_w) - int(sleep_icon.size[0]/2)
    sY = int(screen.middle_h) - int(sleep_icon.size[1]/2)
    sY = sY - int(test_t_h)
    imageB.paste(sleep_icon, (sX,sY), sleep_icon)



    sX = int(screen.middle_w) - int(test_t_w/2)
    sY = int(sY + sleep_icon.size[1]) + 4
    draw_black.text((sX, sY), sleep_string, font = font.SleepFont, fill = 'rgb(0,0,0)')

    sleep_string = "Screen will wakeup tomorrow at "+str(screen.wake_hour)+", sleep well!"
    t_g, t_g, test_t_w, test_t_h = draw_black.textbbox((0,0),sleep_string, font=font.SleepFont_foot)
    sX = int(screen.width - (int(test_t_w) + 5))
    sY = int(screen.height - (int(test_t_h) + 5))
    draw_black.text((sX, sY), sleep_string, font = font.SleepFont_foot, fill = 'rgb(0,0,0)')

    epd.display(epd.getbuffer(imageB),epd.getbuffer(imageR))
    epd.sleep()
    wakeup_day = wake_date.strftime("%d")
    applog("Sleep screen" ,"Set to wake up on the "+wakeup_day)
    while True:
        applog("Sleep screen" ,"Entring coma...")
        if datetime.now().strftime("%d") == wakeup_day:
            if int(datetime.now().strftime("%H")) >= screen.wake_hour:
                break
        applog("Sleep screen" ,"Sleeping for one hour")
        time.sleep(3600)


def get_ip():
    try:
        testIP = "8.8.8.8"
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((testIP, 0))       
        performance.ip_address = s.getsockname()[0]
        performance.host_name = socket.gethostname()
        applog("System Hostname is",performance.host_name)
        applog("System IP Address is",performance.ip_address)
    except Exception as e:
        print("exc. ignored {}".format(e))
        performance.ip_address = "no_ip"
        performance.host_name = "Not networked"
        applog("System IP Address is","NO IP FOUND")
    applog("System","Network : "+performance.ip_address+"@"+performance.host_name)

def wifi_off():
    applog("System","Turning off WiFi now...")
    cmd = 'sudo ifconfig wlan0 down'
    os.system(cmd)


def welcome_screen(delay_time_in_sec):
    font.SleepFont = ImageFont.truetype("fonts/SF-Compact-Rounded-Semibold.otf",32)
    font.SleepFont_foot = ImageFont.truetype("fonts/SF-Compact-Rounded-Semibold.otf",24)

    applog("Welcome Screen" ,"Welcome screen initiated")

    black = 'rgb(0,0,0)'
    white = 'rgb(255,255,255)'

    try:
        applog("Welcome Screen" ,"Setting screen")
        epd = epd7in5b_V2.EPD()
        epd.init()
        applog("Welcome Screen" ,"INIT screen")
        if "noclean" in performance.cli :
            applog("Welcome Screen" ,"Screen cleaning skipped")
        else:
            applog("Welcome Screen" ,"Time to clean the screen")
            epd.Clear()
        screen.height = epd.height
        screen.width = epd.width
        screen.middle_w = screen.width/2
        screen.middle_h = screen.height/2
    except IOError as e:
        applog("Welcome Screen" ,"error"+str(e)) 

    except KeyboardInterrupt:
        applog("Welcome Screen" ,"ctrl + c received") 
        epd7in5b_V2.epdconfig.module_exit()
        exit()
    imageB = Image.new('L', (epd.width, epd.height), 255)  # 255: clear the frame
    imageR = Image.new('L', (epd.width, epd.height), 255)  # 255: clear the frame
    draw_black = ImageDraw.Draw(imageB)

    if performance.ip_address == "no_ip":
        applog("Welcome Screen" ,"loading no-wifi icon") 
        net_icon = Image.open(os.path.join(picdir, 'wifi_off.png'))
        gx = 20
        gy = 20
        imageB.paste(net_icon, (gx,gy), net_icon)

    else:
        applog("Welcome Screen" ,"loading wifi icon") 
        if "wifi-off" in performance.cli:
            net_icon = Image.open(os.path.join(picdir, 'wifi_off_option.png'))
        else:
            net_icon = Image.open(os.path.join(picdir, 'wifi_on.png'))
        
        gx = 20
        gy = 20
        imageB.paste(net_icon, (gx,gy), net_icon)
        tx = int(gx + (net_icon.size[0] + 4))
        ty = gy
        if "wifi-off" in performance.cli:
            draw_black.text((tx, ty), performance.ip_address+" WiFi Will shut off after this screen", font = font.SleepFont_foot, fill = 'rgb(0,0,0)')
        else:
            draw_black.text((tx, ty), performance.ip_address, font = font.SleepFont_foot, fill = 'rgb(0,0,0)')

    welome_icon = Image.open(os.path.join(picdir, 'welcome.png'))

    welcome_string = "Welcome to HomeInkFrame @"+performance.host_name+"..."
    t_g, t_g, test_t_w, test_t_h = draw_black.textbbox((0,0),welcome_string, font=font.SleepFont)

    sX = int(screen.middle_w) - int(welome_icon.size[0]/2)
    sY = int(screen.middle_h) - int(welome_icon.size[1]/2)
    sY = sY - int(test_t_h)
    imageB.paste(welome_icon, (sX,sY), welome_icon)



    sX = int(screen.middle_w) - int(test_t_w/2)
    sY = int(sY + welome_icon.size[1]) + 4
    draw_black.text((sX, sY), welcome_string, font = font.SleepFont, fill = 'rgb(0,0,0)')

    header_Month_Date = datetime.now().strftime("%b %-d")


    wakeup_string = "System time is "+header_Month_Date+", "+datetime.now().strftime("%H:%M")
    t_g, t_g, test_t_w, test_t_h = draw_black.textbbox((0,0),wakeup_string, font=font.SleepFont_foot)
    sX = int(screen.middle_w) - int(test_t_w/2)
    sY = sY + 40
    draw_black.text((sX, sY), wakeup_string, font = font.SleepFont_foot, fill = 'rgb(0,0,0)')


    wakeup_string = "DailyInk will start in "+str(delay_time_in_sec)+" seconds, press ctrl + c to exit."
    t_g, t_g, test_t_w, test_t_h = draw_black.textbbox((0,0),wakeup_string, font=font.SleepFont_foot)
    sX = int(screen.middle_w) - int(test_t_w/2)
    sY = int(screen.height - (int(test_t_h) + 5))
    draw_black.text((sX, sY), wakeup_string, font = font.SleepFont_foot, fill = 'rgb(0,0,0)')
    
    applog("Dashoard","Getting battery status and level...")
    battlevel = get_pibatt()

    if battlevel.level !=-1: #Checking if battery level can be goten -1 means error
        applog("Dashoard","Loading battery icon and drawing status bottom left")
        applog("Dashboard","Battery state: "+battlevel.state+" @ "+str(battlevel.level)+"%")
        if battlevel.state == "Charging":
            if battlevel.level <100:
                batt_icon = Image.open(os.path.join(picdir, 'Battery_chrg.png'))
            else:
                batt_icon = Image.open(os.path.join(picdir, 'Battery_chrg_full.png'))
            btx = 5
            bty = (screen.height - 5) - int(batt_icon.height)
            imageB.paste(batt_icon, (btx,bty), batt_icon)
        else:
            if battlevel.level > 20:
                if battlevel.level == 100:
                    batt_icon = Image.open(os.path.join(picdir, 'Battery_full.png'))
                else:
                    batt_icon = Image.open(os.path.join(picdir, 'Battery.png'))
                    batt_load_txt = str(battlevel.level)
                btx = 5
                bty = (screen.height - 5) - int(batt_icon.height)
                imageB.paste(batt_icon, (btx,bty), batt_icon)
                if battlevel.level < 100:
                    t_G, t_G, batt_t_w, batt_t_h = draw_black.textbbox((0,0),batt_load_txt, font=font.SFMonth)
                    btx = btx + int(batt_icon.width/2)
                    btx = btx - int(batt_t_w/2)
                    bty = bty + int(batt_t_h/2)
                    draw_black.text((btx, bty), batt_load_txt, font=font.SFMonth, fill = black)
            else:
                if screen.use_red == 1:
                    batt_iconB = Image.open(os.path.join(picdir, 'Battery_low_B.png'))
                    batt_iconR = Image.open(os.path.join(picdir, 'Battery_low_R.png'))
                    btx = 5
                    bty = (screen.height - 5) - int(batt_iconB.height)
                    imageB.paste(batt_iconB, (btx,bty), batt_iconB)
                    imageR.paste(batt_iconR, (btx,bty), batt_iconR)
                else:
                    batt_icon = Image.open(os.path.join(picdir, 'Battery_low.png'))
                    btx = 5
                    bty = (screen.height - 5) - int(batt_icon.height)
                    bty = bty - 4
                    imageB.paste(batt_icon, (btx,bty), batt_icon)
    else:
        applog("Dashboard","Battery not found!")
        batt_icon = Image.open(os.path.join(picdir, 'Battery_no_batt.png'))
        btx = 5
        bty = (screen.height - 5) - int(batt_icon.height)
        imageB.paste(batt_icon, (btx,bty), batt_icon)

    epd.display(epd.getbuffer(imageB),epd.getbuffer(imageR))
    epd.sleep()
    applog("DailyInk" ,"Starting up in "+str(delay_time_in_sec)+" seconds...")
    time.sleep(delay_time_in_sec)


def crashlog(file_path:str, crash_message: str):
    subdir = os.path.dirname(file_path)
    #print(subdir)
    if os.path.exists(subdir) == False:
        os.mkdir(subdir)
    aqi_array = []
    date_time_stamp = datetime.now().strftime("%d.%b.%Y, %H:%M:%S")
    my_file = open(file_path, 'a')
    applog("HomeInkFrame" ,"Logging crash message")
    my_file.write(date_time_stamp+" | "+crash_message+'\n')
    my_file.close

def applog(app_section: str ,app_message: str):
    date_time_stamp = datetime.now().strftime("%d.%b.%Y, %H:%M:%S")
    print(date_time_stamp+" | "+app_section+" | "+app_message)

def get_pibatt():
    try:
        conn, event_conn = connect_tcp('127.0.0.1')
        s = PiSugarServer(conn, event_conn)

        s.register_single_tap_handler(lambda: print('single'))
        s.register_double_tap_handler(lambda: print('double'))
        battery.level = int(s.get_battery_level())
        bstate = s.get_battery_charging()
        if bstate == True:
            battery.state = "Charging"
        else:
            battery.state = "Not Charging"

        return_data = battery(level=battery.level,state=battery.state)
    except:
        return_data = battery(level=-1,
                            state="Unknown")
        applog("System","Getting battery state error")

    return return_data

def gotosleep():
    applog("HomeInkFrame","Shutting down the host...")
    time.sleep(2)
    call("sudo shutdown -h now", shell=True)


def main():
    try:
        performance.cli = sys.argv
        print("Startup Command Line paramters detected:")
        print(performance.cli)
    except:
        performance.cli = ""
    applog("Dashboard","Initializing config parameters...")
    get_dashboard_config_data("inkdashboard.ini")

    battery.is_charging = False
    GenGarbage.garbageDay = False
    GenGarbage.compostDay = False
    GenGarbage.recycleDay = False

    get_ip()
    battlevel = get_pibatt()
    hourglass.day = 0
    hourglass.currentday = 0
    screen.clean_screen = 0
    trend = 0
    ram = getRAMinfo()
    performance.usedram = int(ram[2])
    performance.previousram = performance.usedram
    applog("HomeInkFrame","Evening hour is set to: "+str(hourglass.evening_hour))
    applog("HomeInkFrame","Initial used RAM is: "+str(performance.usedram))
    
    if "nowelcome" in performance.cli:
        applog("HomeInkFrame","Skipping welcome screen...")
    else:
        applog("HomeInkFrame","Showing welcome screen...")
        welcome_screen(dashboard.delay_start_sec)

    while True :
        applog("HomeInkFrame","Screen sleep at: "+str(screen.sleep_hour))
        applog("HomeInkFrame","Wake up at: "+str(screen.wake_hour))
        min = 0
        hourglass.last_refresh = datetime.now().strftime("Last Refresh @ %H:%M")
        hourglass.curenttime = int(datetime.now().strftime("%H"))
        hourglass.hour = int(datetime.now().strftime("%H"))
        applog("HomeInkFrame","it is now "+datetime.now().strftime("%H"))

        if hourglass.hour > 5 and hourglass.hour < 11 and hourglass.hour < screen.sleep_hour:
            applog("HomeInkFrame","Time to draw the Morning dashboard...")
            MorningDash()

        elif hourglass.hour >= 11 and hourglass.hour < hourglass.evening_hour:
            applog("HomeInkFrame","Time to draw the Day dashboard...")
            DayDash()

        elif hourglass.hour >= hourglass.evening_hour and hourglass.hour < screen.sleep_hour:
            applog("HomeInkFrame","Time to draw the Morning dashboard...")
            MorningDash()

        elif hourglass.hour > screen.sleep_hour:
            applog("HomeInkFrame","Time to go to sleep...")
            sleep_screen(datetime.now() + timedelta(days=1))

        ram = getRAMinfo()
        performance.usedram = int(ram[2])
        if performance.previousram > performance.usedram :
            trend = -1
            performance.ramincrease = performance.previousram - performance.usedram
        if performance.previousram < performance.usedram :
            trend = 1
            performance.ramincrease = performance.usedram - performance.previousram

        if performance.previousram == performance.usedram :
            trend = 0
            performance.ramincrease = performance.usedram - performance.previousram
            
        performance.freeram = int(ram[1])
        
        cpuT = getCPUtemperature()
        cpuU = getCPUuse()
        applog("System Performance","********************************")
        applog("System Performance","RAM: "+str(performance.usedram)+" used, and "+str(performance.freeram)+" free")
        applog("System Performance","RAM Previous was: "+str(performance.previousram))
        applog("System Performance","Battery Level: "+str(battlevel.level))
        if trend == 1:
            applog("System Performance","Used RAM Increase by: "+str(performance.ramincrease))
        if trend == -1 :
            applog("System Performance","Used RAM Decresed by: "+str(performance.ramincrease))
        if trend == 0 :
            applog("System Performance","Used RAM unchanged")


        applog("System Performance","CPU Usage: "+cpuU)
        applog("System Performance","********************************")
        performance.previousram = performance.usedram

        
        if dashboard.shutdown_after_run == 1:
            gotosleep()
        else:
            applog("HomeInkFrame","Refresh in "+str(screen.refresh_rate_min)+" minutes")
            time.sleep((screen.refresh_rate_min*60))

if __name__ == "__main__":
    main()
