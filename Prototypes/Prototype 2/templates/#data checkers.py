    #data checkers
stats=[]
saveType=0
error=0
entered = False
gameStart=False

def checkNotTaken(nameToAdd):
    conn = sqlite3.connect('players.db') #establish db connection
    cursor = conn.cursor() #establish cursor
    cursor.execute("SELECT count(*) FROM Players WHERE player = ?", [nameToAdd])
    check= cursor.fetchone()[0] #returns as tuple, so make it 1 value
    if check==1: #if there is a matching name in the db
        #gets matching name
        cursor.execute("SELECT player FROM Players WHERE player = ?", [nameToAdd])
        player = cursor.fetchone()[0] #store matching name as variable
        if player == nameToAdd: #if name actually matches
            conn.close() #close connection
            return False #return name is taken
        else: #name didnt match
            conn.close() #close connection
            return True #name isn't taken
    else:
        conn.close() #close connection
        return True #name isn't taken


def checkUserDisplay(widget, menu):
    global currentUser
    global saveType
    global gameStart
    if saveType == 0:
        if widget.get_title()!='Currently not logged in: Guest ':
            widget.set_title('Currently not logged in: Guest ')
    elif saveType==1:
        widget.set_title('Currently logged in as: '+ currentUser)
    if gameStart:
        menu.disable()


def checkUserLog(widget,menu):
    global saveType
    title=widget.get_title() #get current title
    if saveType==0 and title!="Your progress won't be saved, it is highly recommended to select a save to be able to utilize all features of the game":
        widget.set_title("Your progress won't be saved, it is highly recommended to select a save to be able to utilize all features of the game")
    elif saveType==1 and title=="Your progress won't be saved, it is highly recommended to select a save to be able to utilize all features of the game":
        widget.set_title('')

def checkValid(widget, menu):
    global entered
    global valid
    global taken
    global startNum
    global error
    if entered:
        if error == 0:
            widget.set_title('')
        elif error == 1:
            widget.set_title('Invalid data-type, use alphanumerical characters only')
        elif error == 2:
            widget.set_title('Your username cannot start with a number')
        elif error == 3:
            widget.set_title('This username already exists, please go back to choose an existing player or use a different name')
        elif error==4:
            widget.set_title('Username cannot be none')
        entered=False


#REPORTS MENU
    saved=False
    stats= playStats.getStats()
    
    reportMenu =pygame_menu.Menu('Reports Screen',1280,720, theme=pygame_menu.themes.THEME_DARK)
    #report menu frame
    container=reportMenu.add.frame_h(1280,500, background_colour=(20,20,20), padding=0)
    #frame 1- judgements
    judgeframe = reportMenu.add.frame_v(300,450, background_colour=(20,20,20), padding=0,align=pygame_menu.locals.ALIGN_LEFT)
    container.pack(judgeframe)
    frameTitleJ = reportMenu.add.frame_h(300, 50, background_color=(40, 40, 40), padding=0)
    frameContentJ = reportMenu.add.frame_v(300,400,background_color =(30,30,30), padding=0,vertical_position=pygame_menu.locals.POSITION_NORTH)
    judgeframe.pack(frameTitleJ)
    judgeframe.pack(frameContentJ)
    frameTitleJ.pack(reportMenu.add.label('Judgements:',padding=0),margin=(2,2), align=pygame_menu.locals.ALIGN_CENTER)
    #perfect=0, greats=1, goods=2, bads=3, misses=4, lates=5, earlys=6, score = 7 progress=8, accuracy=9, health=10, combo=11
    for i in range(7):
        if i>=5:
            x=pygame_menu.locals.POSITION_SOUTH
        else:
            x=pygame_menu.locals.POSITION_NORTH
        newlabel=reportMenu.add.label(stats[i][0] + ": " + str(stats[i][1]),padding=0)
        frameContentJ.pack(newlabel,align=pygame_menu.locals.ALIGN_CENTER, vertical_position=x)
    
    #frame 2- chart stats
    chartframe = reportMenu.add.frame_v(300,450, background_colour=(20,20,20), padding=0,align=pygame_menu.locals.ALIGN_CENTER)
    container.pack(chartframe)
    chartFtitle = reportMenu.add.frame_h(300, 50, background_color=(40, 40, 40), padding=0)
    frameContentC = reportMenu.add.frame_v(300,400,background_color =(30,30,30), padding=0,vertical_position=pygame_menu.locals.POSITION_NORTH)
    chartframe.pack(chartFtitle)
    chartframe.pack(frameContentC)
    chartFtitle.pack(reportMenu.add.label('Chart Result',padding=0),margin=(2,2), align=pygame_menu.locals.ALIGN_CENTER)
    noOfNotes=len(getChart(chartIndex))
    grade=checkGrade(noOfNotes,stats[10][1],stats[11][1],stats[0][1])
    rank= checkRank(noOfNotes,stats[7][1])
    frameContentC.pack(reportMenu.add.label("Grade: " + grade,padding=0),margin=(2,2),align=pygame_menu.locals.ALIGN_CENTER)
    frameContentC.pack(reportMenu.add.label("Rank: " + rank,padding=0),margin=(2,2),align=pygame_menu.locals.ALIGN_CENTER)
    frameContentC.pack(reportMenu.add.label(stats[7][0] + " [" + str(stats[7][1]) + "]",padding=0),margin=(2,2),align=pygame_menu.locals.ALIGN_CENTER)
    frameContentC.pack(reportMenu.add.label(str(stats[10][1]) + "HP",padding=0),margin=(2,2),align=pygame_menu.locals.ALIGN_CENTER)
    frameContentC.pack(reportMenu.add.label("Highest Combo:" + str(stats[11][1]),padding=0),margin=(2,2),align=pygame_menu.locals.ALIGN_CENTER)
    
    
    #frame 3- ratings
    ratingframe = reportMenu.add.frame_v(300,450, background_colour=(20,20,20), padding=0,align=pygame_menu.locals.ALIGN_RIGHT)
    container.pack(ratingframe)
    ratingFtitle = reportMenu.add.frame_h(300, 50, background_color=(40, 40, 40), padding=0)
    frameContentR = reportMenu.add.frame_v(300,400,background_color =(30,30,30), padding=0,vertical_position=pygame_menu.locals.POSITION_NORTH)
    ratingframe.pack(ratingFtitle)
    ratingframe.pack(frameContentR)
    ratingFtitle.pack(reportMenu.add.label('Rating:',padding=0),margin=(2,2), align=pygame_menu.locals.ALIGN_CENTER)
    
    performance=performanceCalc(noOfNotes,stats[7][1])
    if saveType==0:
        frameContentR.pack(reportMenu.add.label('Not Applicable',padding=0),margin=(2,2),align=pygame_menu.locals.ALIGN_CENTER)
        ratings="null"
    elif saveType==1:
        ratings=ratingChangeCalc(performance[0])
        line = str(ratings[0]) + " -> " + str(ratings[1])
        frameContentR.pack(reportMenu.add.label(line,padding=0),margin=(2,2),align=pygame_menu.locals.ALIGN_CENTER)
        if ratings[2]>=0:
            line= "(+" + str(ratings[2]) + ")"
        else:
            line= "(-" + str(ratings[2]) + ")"
        frameContentR.pack(reportMenu.add.label(line,padding=0),margin=(2,2),align=pygame_menu.locals.ALIGN_CENTER)
    
    #frame 4- performance
    

    perfframe = reportMenu.add.frame_v(300,450, background_colour=(20,20,20), padding=0,align=pygame_menu.locals.ALIGN_RIGHT)
    container.pack(perfframe)
    perfFtitle = reportMenu.add.frame_h(300, 50, background_color=(40, 40, 40), padding=0)
    frameContentP = reportMenu.add.frame_v(300,400,background_color =(30,30,30), padding=0,vertical_position=pygame_menu.locals.POSITION_NORTH)
    perfframe.pack(perfFtitle)
    perfframe.pack(frameContentP)
    perfFtitle.pack(reportMenu.add.label('Performance:',padding=0),margin=(2,2), align=pygame_menu.locals.ALIGN_CENTER)
    frameContentP.pack(reportMenu.add.label("Overall: " + str(performance[0]) + " / " + str(performance[1]) ,padding=0),margin=(2,2),align=pygame_menu.locals.ALIGN_CENTER)
    for i in range(2):
        line= stats[i + 8][0] + ": " + str(stats[i + 8][1]) + "%"
        frameContentP.pack(reportMenu.add.label(line,padding=0),margin=(2,2),align=pygame_menu.locals.ALIGN_CENTER)
    
    #buttons
    returnB=reportMenu.add.button("Return",returnF,align=pygame_menu.locals.ALIGN_LEFT)
    returnB.set_float(True)
    retryB=reportMenu.add.button("Retry",retry,align=pygame_menu.locals.ALIGN_RIGHT)
    retryB.set_float(True)

    if saveType==1:
        saveB=reportMenu.add.button("Save",align=pygame_menu.locals.ALIGN_CENTER)
        saveB.set_float(True)
        def saveClicked():
            saveButton(currentUser,chartIndex,stats,grade,rank,ratings[1])
            saveB.hide()
            saveL=reportMenu.add.label("Saved!",align=pygame_menu.locals.ALIGN_CENTER)
            saveL.set_float(True)
        saveB.update_callback(saveClicked)
        
 
    reportMenu.enable()
    reportMenu.mainloop(screen)
