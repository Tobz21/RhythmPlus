import pygame,time,os, os.path, csv,pygame_menu,sqlite3; #imports modules listed

#creates new database if not found
if not os.path.isfile('./players.db'): #check if file doesn't exist
    conn = sqlite3.connect('players.db') #connect/create new .db players
    #creates table Players with:
        #player and skill rating columns 
    conn.execute('''CREATE TABLE Players
           (player         TEXT PRIMARY KEY NOT NULL,
            skillrating    REAL);''')
    #creates table Scores with:
        #recordid,player,chart,score,grade,combo,rank columns
    conn.execute('''CREATE TABLE Scores
           (recordid       INTEGER PRIMARY KEY,
            player        TEXT,
            chart          INT,
            score          INT,
            grade          INT,
            accuracy       REAL,
            combo          INT,
            rank           INT,
            FOREIGN KEY (player) REFERENCES Players (player)
            );''')
    conn.commit() #save changes
    conn.close() #close connection
    print("created") #test print statement

pygame.mixer.pre_init(22050, -16, 2, 64)
pygame.init()
pygame.mixer.quit()
pygame.mixer.init(22050, -16, 2, 64)
pygame.display.set_caption(("Rhythm PLUS")) #sets caption of window

#global variables
clock = pygame.time.Clock() #variable for the game clock
WIDTH, HEIGHT = 1280, 720 #width and height of the display window
screen = pygame.display.set_mode((WIDTH, HEIGHT)) #set game surface using the window resolutions given
FPSE = 60  #frames per second, used to do clock.tick

    #data checkers
stats=[]
saveType=0
error=0
gameStart=False

chartList ={0:["Easy: On and On LVL:3",3], 1:["Medium: Invincible LVL:5",5],2:["Hard: Different Heaven LVL:8",8]}
chartIndex=0

#options menu globals
    #sliders
sfxVol=100
bgmVol=100
    #toggles
accDisplayState=True
healthDeathState=True
hitSfxState=True
progMetreState=True
wordJudge=True
lateEarlyState=True

#images preloading with alpha to keep transparency
#   then transforming to scale within the game
#arrow images
lImg = pygame.image.load('l_arrow.png').convert_alpha()
lImg = pygame.transform.scale(lImg, (65,60))
uImg = pygame.image.load('u_arrow.png').convert_alpha()
uImg = pygame.transform.scale(uImg, (65,60))
dImg = pygame.image.load('d_arrow.png').convert_alpha()
dImg = pygame.transform.scale(dImg, (65,60))
rImg = pygame.image.load('r_arrow.png').convert_alpha()
rImg = pygame.transform.scale(rImg, (65,60))
#judgement line image
jLineImg = pygame.image.load('j_line.png').convert_alpha()
jLineImg = pygame.transform.scale(jLineImg, (260,60))

#useful functions
#function to round any number
def roundAny (value, resolution): #function to round a value, taking value and resolution as parameters
    rounded = round(float(value) / float(resolution)) * resolution #algorithm to return rounded value
    return rounded #return rounded value

#decimal place cut off function
def formatNumber(n, digits): #function to format decimal places, taking value and decimal places as parameters
    formatter = '{:.' + '{}'.format(digits) + 'f}' #format for new value
    x = round(n, digits) #for input into format
    return float(formatter.format(x)) #create the new string and then convert it to float for returning

#round to 2 decimal places function
def round2dp(value): #function to round a value, taking value as parameter
    rounded = round(float(value) // float(0.02)) * 0.02 #algorithm to return rounded value
    return rounded #return rounded value

def rankToNum(rank):
    if rank =="MAX":
        rank = 7
    elif rank == "SS":
        rank=6
    elif rank == "S":
        rank=5
    elif rank == "A":
        rank=4
    elif rank == "B":
        rank=3
    elif rank == "C":
        rank=2
    elif rank == "D":
        rank=1
    return rank

def gradeToNum(grade):
    if grade =="ALL PERFECT":
        grade = 4 
    if grade =="FULL COMBO":
        grade = 3 
    if grade =="PASS":
        grade = 2 
    if grade =="FAIL":
        grade = 1 
    return grade

#function to convert numbers to rank strings
def numToRank(rank):
    if rank == 7:
        rank = "MAX"
    elif rank == 6:
        rank="SS"
    elif rank == 5:
        rank="S"
    elif rank == 4:
        rank="A"
    elif rank == 3:
        rank="B"
    elif rank == 2:
        rank="C"
    elif rank == 1:
        rank="D"
    return rank
#function to convert numbers to grade strings
def numToGrade(grade):
    if grade ==4:
        grade = "D"
    if grade ==3:
        grade = "FULL COMBO"
    if grade ==2:
        grade = "PASS"
    if grade ==1:
        grade = "FAIL"
    return grade

#database functions
#function to add a new player to the database
def newPlayerDB(name):
    #establish connection
    conn = sqlite3.connect('players.db')
    #execute insert sql statement
    conn.execute("INSERT INTO Players(player,skillrating) VALUES(?,?)",[name,0]) 
    conn.commit() #saves changes
    conn.close() #close connection

#function to check if name is taken in db
# returns True if not taken, False if taken
def checkNotTaken(nameToAdd):
    conn = sqlite3.connect('players.db') #establish db connection
    cursor = conn.cursor() #establish cursor
    cursor.execute("SELECT count(*) FROM Players WHERE player = ?", [nameToAdd])
    check= cursor.fetchone()[0] #returns count of players in table
    
    if check==1: #if there is a matching name in the db
        conn.close() #close connection
        return False #name is taken
    else: 
        conn.close() #close connection
        return True #name isn't taken

#function to get list of players from db and return it
def getPlayersDB():
    conn = sqlite3.connect('players.db') #establish connection
    cursor = conn.cursor() #establish cursor
    cursor.execute("SELECT player FROM Players") #select statement
    players=[] #initialize array for formatting
    for player in cursor.fetchall(): #loops through each player
        players.append(player[0]) #adds item only to array
    conn.close() #close connection
    return players #return formatted player list

#function to get skill rating from players
def getSkillRating():
    global currentUser
    conn = sqlite3.connect('players.db') #establish connection
    cursor = conn.cursor() #establish cursor
    #select statement of skill rating of player record from players with currentUser
    cursor.execute("SELECT skillrating FROM Players WHERE player = ?", [currentUser])
    rating=cursor.fetchone()[0] #fetches and formats
    conn.close() #close connection
    return rating #returns formatted rating

#function to save new record to database scores as well as new rating
def saveStats(player,chart,score,grade,accuracy,combo,rank,newRating):
    conn = sqlite3.connect('players.db') #establish connection
    #save new scores record
    conn.execute("INSERT INTO Scores(player,chart,score,grade,accuracy,combo,rank) VALUES(?,?,?,?,?,?,?)",[player,chart,score,grade,accuracy,combo,rank])
    #save skill rating
    conn.execute("UPDATE Players SET skillrating=? WHERE player=?",[newRating,player])
    conn.commit() #save changes
    conn.close() #close connection

#menu functions
#function for user display widget to change title
# also handles game starting 
def checkUserDisplay(widget, menu):
    global currentUser
    global saveType
    global gameStart
    if saveType == 0: #if guest/no save
        widget.set_title('Currently not logged in: Guest ')
    elif saveType==1: #if player/not guest save
        widget.set_title('Currently logged in as: '+ currentUser)
    if gameStart: #if play button on charts menu pressed
        menu.disable() #disables main menu 
        gameStart=False #re-initializes for next loop

#function for second user display widget to warn user
# if not logged in
#function for user warn widget to change title
def checkUserLog(widget,menu):
    global saveType
    if saveType==0: #if guest/no save
        widget.set_title("Your progress won't be saved, it is highly recommended to select a save to be able to utilize all features of the game")
    elif saveType==1: #if player/not guest save
        widget.set_title('')
    
#function to check if name input is valid
# if it is valid then the name will be added to
# the database and send the user back to main menu
# if it is not valid, an error value will be set
def addName(name):
    global newPlayer
    global error
    global currentUser
    global saveType
    #check if username is reserved word none
    if name.lower()!="none": 
        #check if username is alphanumeric
        if name.isalnum():
            #check if username doesn't start with an number
            if not name[0].isnumeric():
                #check if username isn't taken
                if checkNotTaken(name):
                    newPlayerDB(name) #adds player to database
                    print("added")
                    currentUser = name #sets current user to be player
                    saveType = 1 #sets saveType to player value
                    error = 0 #no errors
                    newPlayer.reset(2) #sends user back to main menu
                else:
                    error = 3 #username is taken
            else:
                error = 2 #username starts with a number  
        else:
            error = 1 #username is not alphanumeric only
    else:
        error=4 #username is reserved word none

#function to set valid label title based on error input
def checkValid(widget, menu):
    global error
    if error == 0: #if no error
        widget.set_title('')
    elif error == 1: #if not alphanumeric
        widget.set_title('Invalid data-type, use alphanumerical characters only')
    elif error == 2: #if starts with number
        widget.set_title('Your username cannot start with a number')
    elif error == 3: #if username already exists
        widget.set_title('This username already exists, please go back to choose an existing player or use a different name')
    elif error==4: #if username is none
        widget.set_title('Username cannot be none')
        
#function to get new list of players and set drop selector items
def getPlayers(widget, menu):
    players = getPlayersDB() #gets list of players in db
    new_items=[] #initialize array
    index=0 #initialize index
    for player in players:
        item = (player, index) #format item as tuple
        new_items.append(item) #add to array
        index = index + 1 #increment index
    #if there has been a change to the items
    if not (new_items == widget.get_items()):
        if len(players)==0: #if there are no players in db
            #if item list has changed
            if not (widget.get_items()==[('None',0)]): 
                widget.update_items([('None',0)])
        else: #if there ARE players in db
            widget.update_items(new_items)

#function to assign player on drop select widget
def setPlayer(item, index):
    global oldPlayer
    global currentUser
    global saveType
    currentUser = item[0][0] #item contains index automatically
    if not (currentUser=='None'): #if player name is a player
        saveType = 1 #save type is player
        oldPlayer.reset(2) #send back to main menu

#function to update high score widgets 
def updateHighScores(widget,menu):
    global saveType
    global currentUser
    global highestWidgets
    global chartIndex
    #order->score,combo,grade,rank
    if saveType==0: # if guest
        for i in range(4): #assign N/A if not already
            if highestWidgets[i].get_title()!='N/A':
                highestWidgets[i].set_title('N/A')
    elif saveType==1: #if player
        conn = sqlite3.connect('players.db') #establish connection
        cursor = conn.cursor() #establish cursor
        #execute sql select to check if there are any records with that chart and player
        cursor.execute("SELECT count(*) FROM Scores WHERE (player = ?) AND (chart=?)", [currentUser,chartIndex])
        check= cursor.fetchone()[0] #fetches result
        if check>=1: 
            #sql statement to select all max values from scores records
            cursor.execute("SELECT MAX(score), MAX(combo), MAX(grade),MAX(rank) FROM Scores,Players WHERE (Players.player = ?) AND (Scores.chart=?) AND (Scores.player=Players.player)", [currentUser,chartIndex])
            result=cursor.fetchone() #fetches result
            #format result
            readResults=[str(result[0]),str(result[1]),numToGrade(result[2]),numToRank(result[3])]
            #assign highest record if not already
            for i in range(4):
                if highestWidgets[i].get_title()!=readResults[i]:
                    highestWidgets[i].set_title(readResults[i])
        else:#if no records found
            #assign records n/a if not already
            for i in range(4):
                if highestWidgets[i].get_title()!='N/A':
                    highestWidgets[i].set_title('N/A')
        conn.close() #close connection

#function to change skill rating widget display
def showSkillRating(widget,menu):
    global saveType
    if saveType==0: #if guest
        widget.set_title('Skill rating: N/A')
    elif saveType==1: #if player
        widget.set_title('Skill rating: ' + str(getSkillRating()))

#change volumes functions from range sliders
def sfxChange(vol):
    global sfxVol
    sfxVol = round(vol)
def bgmChange(vol):
    global bgmVol
    bgmVol = round(vol)


#options toggles functions to change state when clicked
def accDispChange(state):
    global accDisplayState
    accDisplayState=state
def deathChange(state):
    global healthDeathState
    healthDeathState=state
def hitSfxChange(state):
    global hitSfxState
    hitSfxState=state
def progDispChange(state):
    global progMetreState
    progMetreState=state
def judgeChange(state):
    global wordJudge
    wordJudge=state
def laEaChange(state):
    global lateEarlyState
    lateEarlyState=state

#function to exit to game for play button press
def exitToGame():
    global chartMenu
    global gameStart
    gameStart=True #signals game should be started
    chartMenu.reset(1) #send back to main menu

#function to change chart when selection changes
def changeChart(chart, index):
    global chartIndex
    chartIndex = index

#function to calculate grade and return it
def checkGrade(notes,health,combo,perfects):
    if health<=0:
        return "FAIL"
    elif perfects==notes:
        return "ALL PERFECT"
    elif combo==notes:
        return "FULL COMBO"
    else:
        return "PASS"

#function to calculate rank and return it
def checkRank(notes,score):  
    maxScore= notes*300
    scoreP=(score/maxScore)*100
    if scoreP==100:
        return "MAX"
    elif scoreP>=95:
        return "SS"
    elif scoreP>=90:
        return "S"
    elif scoreP>=85:
        return "A"
    elif scoreP>=80:
        return "B"
    elif scoreP>=75:
        return "C"
    elif scoreP<75:
        return "D"

#function to calculate performance using 
# number of notes and score and return
# a tuple of performance and max performance
def performanceCalc(notes,score):
    global chartList
    global chartIndex
    #creates variables for checks
    chartLVL=chartList[chartIndex][1]
    maxscore = (notes)*300
    scoreP = score/maxscore
    #calculates modifier
    if scoreP>0.95:
        modifier= 1 + ((scoreP-0.95)/0.05)
    elif scoreP>0.9:
        modifier = (scoreP-0.9)/0.1
    else:
        modifier = (scoreP-0.9)/0.2
    #performance is the modifier + the chart level
    performance = chartLVL + modifier
    #maximum possible is 2 more than the chart number
    maxPerf=chartLVL+2 
    if performance<0: #if performance negative
        performance=0 #performance can't be negative 
    return formatNumber(round2dp(performance),2),maxPerf

#calculate rating change using performance
# then return current, new and difference ratings
def ratingChangeCalc(performance):
    currentRating = getSkillRating()
    newRating=((currentRating*19)+performance)/20
    difference=newRating-currentRating
    return currentRating,round2dp(newRating),round2dp(difference)

#function when save button is pressed to save data
def saveButton(player,chart,stats,grade,rank,newRating):
    #convert string to number for saving
    rank=rankToNum(rank) 
    grade=gradeToNum(grade)
    #perfect=0, greats=1, goods=2, bads=3, misses=4, lates=5, earlys=6, score = 7 progress=8, accuracy=9, health=10, combo=11
    saveStats(player,chart,stats[7][1],grade,stats[9][1],stats[11][1],rank,newRating)
       
    
#function to return to main menu when clicked
def returnF():
    global reportMenu
    reportMenu.disable()

#function to restart main game when clicked
def retry():
    global reportMenu
    global restart
    restart=True
    reportMenu.disable()
#menus
    #layer 1
mainMenu = pygame_menu.Menu('Welcome to Rhythm PLUS',1280,720, theme=pygame_menu.themes.THEME_DARK)
    #layer 2
chartMenu = pygame_menu.Menu('Select a Chart',1280,720, theme=pygame_menu.themes.THEME_DARK)
optionsMenu = pygame_menu.Menu('Adjust your preferences',1280,720, theme=pygame_menu.themes.THEME_DARK)
saveMenu = pygame_menu.Menu('Select a Save Type',1280,720, theme=pygame_menu.themes.THEME_DARK,)
    #layer 3
newPlayer = pygame_menu.Menu('Create a new player save',1280,720, theme=pygame_menu.themes.THEME_DARK)
oldPlayer = pygame_menu.Menu('Choose your existing Save',1280,720, theme=pygame_menu.themes.THEME_DARK)


#menu layouts
    #main menu
        #buttons
mainMenu.add.button("Play",chartMenu)  
mainMenu.add.button("Change Save",saveMenu)
mainMenu.add.button("Options",optionsMenu)
        #labels
userDisplay = mainMenu.add.label('Currently not logged in: Guest ', font_size=20)
userDisplay.add_draw_callback(checkUserDisplay)
userDisplay.force_menu_surface_update()
userWarn = mainMenu.add.label('', font_size=20)
userWarn.add_draw_callback(checkUserLog)
userWarn.force_menu_surface_update()



    #savemenu
saveMenu.add.button("New Player",newPlayer)
saveMenu.add.button("Returning Player",oldPlayer)

    #new player menu
newPlayer.add.text_input('Player Name:', maxchar=10, onreturn=addName)
validShow = newPlayer.add.label('', font_size=20)
validShow.add_draw_callback(checkValid)

    #existing player menu
choosePlayer = oldPlayer.add.dropselect(title='Select a Player:', items=[("None", 0)], onchange=setPlayer)
choosePlayer.add_draw_callback(getPlayers)

    #charts menu
#display of logged in player
userDisplay2=chartMenu.add.label('', font_size=20)
userDisplay2.add_draw_callback(checkUserDisplay)
userDisplay2.force_menu_surface_update()
#display of player rating
ratingDisplay=chartMenu.add.label('', font_size=20)
ratingDisplay.add_draw_callback(showSkillRating)
ratingDisplay.force_menu_surface_update()

#selector widget
chartMenu.add.selector('Select a chart', items=[(chartList[0][0],0),(chartList[1][0],1),(chartList[2][0],2)], onchange=changeChart)

#play button
chartMenu.add.button("Play", exitToGame)

     #frame master
highScores=chartMenu.add.frame_h(1240,260)
    #frames sub
    #score frame
scoreH=chartMenu.add.frame_v(300,250)
scoreH.pack(chartMenu.add.label('Score:',padding=0),margin=(2,2), align=pygame_menu.locals.ALIGN_CENTER)
highestScore=chartMenu.add.label('N/A',padding=0)
scoreH.pack(highestScore,margin=(2,2), align=pygame_menu.locals.ALIGN_CENTER)
    #combo frame
comboH=chartMenu.add.frame_v(300,250)
comboH.pack(chartMenu.add.label('Max Combo:',padding=0),margin=(2,2), align=pygame_menu.locals.ALIGN_CENTER)
highestCombo=chartMenu.add.label('N/A',padding=0)
comboH.pack(highestCombo,margin=(2,2), align=pygame_menu.locals.ALIGN_CENTER)
    #grade frame
gradeH=chartMenu.add.frame_v(300,250)
gradeH.pack(chartMenu.add.label('Grade:',padding=0),margin=(2,2), align=pygame_menu.locals.ALIGN_CENTER)
highestGrade=chartMenu.add.label('N/A',padding=0)
gradeH.pack(highestGrade,margin=(2,2), align=pygame_menu.locals.ALIGN_CENTER)
    #rank frame
rankH=chartMenu.add.frame_v(300,250)
rankH.pack(chartMenu.add.label('Rank:',padding=0),margin=(2,2), align=pygame_menu.locals.ALIGN_CENTER)
highestRank=chartMenu.add.label('N/A',padding=0)
rankH.pack(highestRank,margin=(2,2), align=pygame_menu.locals.ALIGN_CENTER)
    #pack frames in
highScores.pack(scoreH)
highScores.pack(comboH)
highScores.pack(gradeH)
highScores.pack(rankH)
#for use in global calls
highestWidgets=[highestScore,highestCombo,highestGrade,highestRank]
#draw callbacks
highScores.add_draw_callback(updateHighScores)
highScores.force_menu_surface_update() 

    #options menu
    #toggles
optionsMenu.add.toggle_switch('Accuracy Display', True, onchange=accDispChange)
optionsMenu.add.toggle_switch('Health death',True, onchange=deathChange)
optionsMenu.add.toggle_switch('Hit SFX', True, onchange=hitSfxChange)
optionsMenu.add.toggle_switch('Progress Meter',True, onchange=progDispChange)
optionsMenu.add.toggle_switch('Word Judgement', True, onchange=judgeChange)
optionsMenu.add.toggle_switch('Late/Early Display',True, onchange=laEaChange)
    #sliders
optionsMenu.add.range_slider('SFX Volume:',100,(0,100),1, onchange=sfxChange, value_format=lambda x: str(int(x)))
optionsMenu.add.range_slider('BGM Volume:',100,(0,100),1, onchange=bgmChange, value_format=lambda x: str(int(x)))


#functions

#function to determine whether a hit can be registered on the frame
def hitCheck(previous): #takes in array of previous key states
    hits=[] #initialize array of hit states be added to
    pressedStore=[] #initialize array of pressed states to be added to 
    pressed= pygame.key.get_pressed() #gets current state of hits and stores as array
    
    pressedStore.append(pressed[pygame.K_LEFT])
    pressedStore.append(pressed[pygame.K_UP])
    pressedStore.append(pressed[pygame.K_DOWN])
    pressedStore.append(pressed[pygame.K_RIGHT])
    # index order: 0 left, 1 up, 2 down, 3 right
    #if key wasn't pressed on the last frame, but pressed on this frame:
        #add True to its index in hits
    #otherwise:
        #add False to its index in hits
    #left key
    if pressedStore[0] and previous[0]==False:
        hits.append(True)
    else:
        hits.append(False)
    #up key
    if pressedStore[1] and previous[1]==False:
        hits.append(True)
    else:
        hits.append(False)
    #down key
    if pressedStore[2] and previous[2]==False:
        hits.append(True)
    else:
        hits.append(False)
    #right key
    if pressedStore[3] and previous[3]==False:
        hits.append(True)
    else:
        hits.append(False)
    #return hit values for hit detection, pressed states for previous frame storage
    return hits, pressedStore 

#get chart data function
def getChart(chartIndex): #new function getChart taking chartIndex as a parameter
    filename = str(chartIndex) + ".csv" #concatenate with given chart index, and load this file
    returnNotes=[] #initialize array for appending to return
    with open(filename, "r", encoding='utf-8-sig') as csvfile: #open the file as reading
        datareader = csv.reader(csvfile) #csv function to read the chart file
        for row in datareader: #loop through rows in the chart file
            toAdd=[row[0].strip(),row[1].strip()]
            returnNotes.append(toAdd) #add each row as an item in the array
    return returnNotes #return the returnNotes array

#function drawing text to screen with specific font and settings
def draw_text(text, font, text_col, x, y): #takes text, font, colour and position as parameters
    img = font.render(text,True, text_col) #create parameter to render with
    screen.blit(img, (x, y)) #render the text

#draw text
comboFont = pygame.font.SysFont("Arial", 50 , bold = True) #font setup variable for combo display
scoreFont = pygame.font.SysFont("Arial", 25 , bold = True) #font setup variable for score display
noteFont = pygame.font.SysFont("Arial", 18 , bold = True) #font setup variable for note display
judgeFont = pygame.font.SysFont("Arial", 30 , bold = True) #font setup variable for judgement display
timingFont = pygame.font.SysFont("Arial", 20 , bold = True) #font setup variable for timing display

#classes
#sound engine/class to set sound settings and play sounds
class Sounds:
    #takes parameters volumes, sfx state and chart
    def __init__(self, musicVol, sfxVol, sfxState, chart): 
        #volume will be 0-100, pygame uses 0-1 so divide by 100
        self._musicVol = musicVol/100 
        self._sfxVol = sfxVol/100
        #if sfx is turned off, set sfx volume to 0
        if not sfxState:
            self._sfxVol=0
        # save chart file name, load it and set the volume
        self._chart = str(chart) + ".mp3"
        pygame.mixer.music.load(self._chart)
        pygame.mixer.music.set_volume(self._musicVol)
        #save sfx file names as objects and set their volumes to sfx volume
        self._perfectHit = pygame.mixer.Sound("perfect.mp3")
        self._perfectHit.set_volume(self._sfxVol)
        self._greatHit = pygame.mixer.Sound("great.mp3")
        self._greatHit.set_volume(self._sfxVol)
        self._goodHit = pygame.mixer.Sound("good.mp3")
        self._goodHit.set_volume(self._sfxVol)
        self._badHit = pygame.mixer.Sound("bad.mp3")
        self._badHit.set_volume(self._sfxVol)
        self._missHit = pygame.mixer.Sound("miss.mp3")
        self._missHit.set_volume(self._sfxVol)

    #method to play the chart music
    def playChart(self):
        pygame.mixer.music.play()
    #methods to play corresponding judgement sounds
    def perfectHit(self):
        self._perfectHit.play()
    def greatHit(self):
        self._greatHit.play()
    def goodHit(self):
        self._goodHit.play()
    def badHit(self):
        self._badHit.play()
    def missHit(self):
        self._missHit.play()
    #method to end the chart music playback
    def endSong(self):
        pygame.mixer.music.stop()

    #methods to redirect to judgement sounds depending on the judgement received 
    def sfxHandle(self, judgement):
        if judgement=="PERFECT":
            self.perfectHit()
        if judgement=="GREAT":
            self.greatHit()
        if judgement=="GOOD":
            self.goodHit()
        if judgement=="BAD":
            self.badHit()

#note class to move, draw and get the judgement data of notes
class Note: 
    def __init__(self, time, direction): #constructor method for note class, takes 2 parameters, note time and direction/conveyor
        if direction=="LEFT": #if left pointing note
            x = 420 #starting x position will be furthest to the left
            self._image = lImg #set image to left arrow
        elif direction=="DOWN": #if down pointing note
            x = 485 #starting x position will be second from the left
            self._image = dImg #set image to left arrow
        elif direction=="UP": #if up pointing note
            x = 550  #starting x pos will be after the down note
            self._image = uImg #set image to left arrow
        elif direction=="RIGHT": #if right pointing note
            x = 615 #starting x pos will be furthest away and after up conveyor
            self._image = rImg #set image to left arrow
        self._x=x #set x value of note to x
        self._y=620 #set y value to a fixed value- every note will spawn on the same line
        self._time=float(time) #time of note, taken from parameter input
        self._direction=direction #direction of note, taken from parameter input
        
    #procedure to update the note every frame
    def update(self): 
        screen.blit(self._image, (self._x, self._y))
    #method to move the notes when the frame time changes
    def move(self): 
        self._y = self._y + (-10) # updates y co-ordinate of the note instance to be incremented by the speed
    
    #function to report notes reaching judgement line, takes elapsed time as parameter
    def report(self,elapsed_time):
        if self._time == elapsed_time: #if the time of the note = time elapsed
            print(self._time, "happened at", self._y) #print the note's y coordinate that it shouldve been at
        if self._y == 50: #if the y coordinate of the note = y coordinate of judgement line
            print(self._time, "happened at", elapsed_time,"s") #print time it met the judgement line
    
    #method to check if note is ready to be acted upon
    def checkInput(self, hit, time):
        #test if key pressed and matches note key
        if ((self._direction=='LEFT') and (hit[0])) or ((self._direction=='DOWN') and (hit[2])) or ((self._direction=='UP') and (hit[1])) or ((self._direction=='RIGHT') and (hit[3])): 
            difference = time - self._time #calculate time difference of note
            if difference<= 0.15 and difference>=-0.15: #if note within time range 
                #note direction will have hit variable set false to avoid multiple notes hit by one input
                global hits
                if self._direction=='LEFT':
                    hits[0]=False
                if self._direction=='UP':
                    hits[1]= False
                if self._direction=='DOWN':
                    hits[2]= False
                if self._direction=='RIGHT':
                    hits[3]=False
                               
                return True #true return for note to be acted upon when conditions are met
            else: #when key is pressed but not in time frame
                return False # then return false 
        else: #when key is not pressed
            return False #then return false
    
    #method to check if note is too late
    def checkOut(self, time): #takes the time on the frame as a parameter
        difference= time - self._time
        if difference>0.15: #if time passed is beyond 0.15s of the note's time
            return True
        else:
            return False
    
    #method to give a judgement for the note
    def judge(self, time):
        difference = time - self._time 
        if difference>=0: #group of late judgements   
            if difference<0.12:
                if difference<0.09:
                    if difference<0.05:
                        judge="PERFECT"
                    else:
                        judge="GREAT"
                else:
                    judge="GOOD"        
            else:
                judge="BAD"
        else: #group of early judgements
            if difference>-0.12:
                if difference>-0.09:
                    if difference>-0.05:
                        judge="PERFECT"
                    else:
                        judge="GREAT"
                else:
                    judge="GOOD"        
            else:
                judge="BAD"
        return judge
#method to check if late or early
    def lateOrEarly(self, time):
        difference = time - self._time #calculate time difference
        #initialize early late variables
        early=False
        late=False
        #if difference is not at max judgement/perfect, 
        #then late early assigned accordingly
        if difference>=0.05: #if hit is late/positive
            late=True
        elif difference<-0.05: #if hit is early/negative
            early=True
        return late, early #return late early as tuple

#class of statistics to store statistical variables and update them
class Statistics:
    def __init__(self, notes,accDisp,death,progDisp,wordJudge,laEaDisp): #initialize class and its variables
        #initialize variable statistics
        #variables for adjusting to preferences
        self._death=death
        self._progDisp=progDisp
        self._wordJudge=wordJudge
        self._laEaDisp=laEaDisp
        self._accDisp=accDisp
        #counting judgement variables
        self._perfects=0
        self._greats=0
        self._goods=0
        self._bads=0
        self._misses=0
        self._score=0
        self._lates=0
        self._earlys=0
        self._currentCombo=0
        self._maxCombo=0
        self._health=1000
        self._accuracy=0
        #variables for drawing judgements correctly
        self._judgeName=""
        self._judgeStart=0
        self._judgeFlag=False
        self._currentTiming=[False,False]
        self._leEaStart=0
        self._leEaFlag=False
        #variables for drawing statistics
        self._endTime = float(notes[len(notes)-1][0]) + 0.15

        self._progress=0
        self._increment= (self._endTime)/100
        self._progressMultiplier = 0
        self._lastTime=0
        
    #method to handle incoming judgements, judgement as parameter
    def judgeHandle(self,judgement):
        #method redirects
        # sets number value for number judge
        if judgement=="PERFECT":
            self.perfect() 
            number=300 
        if judgement=="GREAT":
            self.great()
            number=150
        if judgement=="GOOD":
            self.good()
            number=100
        if judgement=="BAD":
            self.bad()
            number=50
        #save judgement characteristics for drawing method
        if self._wordJudge:
            self._judgeName=judgement #save name of judgement
        else:
            self._judgeName=str(number) #format number to string
        self._judgeFlag=True #set to True-> that there is a new judgement given
        return judgement #return judgement passed in for next function criteria

    #method to draw and update statistics on the screen
    def statsUpdate(self,time):
        self.judgeDraw(time)
        if self._laEaDisp:
            self.leEaDraw(time)
        self.scoreDraw()
        self.comboDraw()
        self.healthDraw()
        self.progressUpdate(time)
        if self._progDisp:
            self.progressDraw()
        self.accuracyUpdate()
        if self._accDisp:
            self.accuracyDraw()

    #method to draw the accuracy onto the screen
    def accuracyDraw(self):
        draw_text(("Accuracy: " + str(self._accuracy) + "%"), scoreFont, (255,255,255) ,1100, 40)

    #method to update the accuracy of the play
    def accuracyUpdate(self):
        #find maximum possible score by adding up how many notes have passed * maximum score attainable 
        maxPos= (self._perfects + self._greats + self._goods + self._bads + self._misses)*300 
        if maxPos!=0: # less than 0 as division by 0 cannot be done
            #define accuracy as score/maxPossibleScore rounded to 2dp by round function
            acc= (self._score/maxPos)*100
            self._accuracy = formatNumber((roundAny(acc, 0.01)), 4)
        else:
            self._accuracy = 100.00 #always starts with 100% accuracy
        
    #method to increment progress
    def progressUpdate(self, time):
        if time <= self._endTime: # if time is before or at game ends
            while self._lastTime <= time: #while maximum total interval time isn't surpassed
                self._progressMultiplier = self._progressMultiplier + 1 #increment multiplier
                self._lastTime = self._increment * self._progressMultiplier #multiply time increment by multiplier 
            self._progress = self._progressMultiplier - 1 #deduct 1 because lastTime must be greater than current time
            #progress is the amount of whole number intervals the game has reached
    
    #method to draw progress bar to the screen
    def progressDraw(self):
        size = (self._progress/100)*400 #adjust size to reflect progress meter
        progressMeter=pygame.Rect(420, 30, size, 20) #uses size as length, defines as rectangle
        pygame.draw.rect(screen,(0, 0, 128),progressMeter,) #draws rectangle using progress meter and blue colour 
        
    #method to give 100% progress when game ends by end of chart
    def progressEnd(self):
        self._progress = 100
    
    #method to draw the health value onto the screen
    def healthDraw(self):
        draw_text(("Health: " + str(self._health)), scoreFont, (0,255,0) ,1100, 0)

    #method to cancel the game if the health drops below 0
    def healthDeath(self):
        if self._death:
            if self._health<=0: #if health reaches 0 or below
                return True
        
    #method to update judgement drawings
    def judgeDraw(self,time):
        draw=False
        if self._judgeName!="": #if there is a judgement type given
            if self._judgeFlag: #if there is a new judgement
                self._judgeStart=time #change to the new time
                self._judgeFlag=False #set so that there is no new judgement for next cycle
                draw = True #can draw the judgement
            elif self._judgeStart + 0.5 > time: #if 0.5 seconds has passed since old judgement
                draw = True #can draw the judgement
        if draw: #if can draw | draw is true
            draw_text(self._judgeName, judgeFont, (255,255,255) ,540, 520)
    
    #method to update combo drawings
    def comboDraw(self):
        if self._currentCombo >= 2: #if current combo is greater than 2
            #draws combo text
            draw_text("COMBO", scoreFont, (255,255,255) ,550, 410)
            #draws combo value
            draw_text(str(self._currentCombo), comboFont, (255,255,255) ,550, 360)
    
    #method to draw the score onto the screen
    def scoreDraw(self):
        draw_text(("Score: " + str(self._score)), scoreFont, (255,255,255) ,1100, 20)
    
    #method to draw late and early to the screen
    def leEaDraw(self,time):
        draw=False
        if self._leEaFlag: #if there is a new judgement
            self._leEaFlag=False #set so that there is no new judgement for next cycle
            self._leEaStart=time #change to the new time
            draw=True #can draw the late/early
        elif self._leEaStart + 0.5 > time: #if 0.5 seconds has passed since old judgement
            draw=True #can draw the late/early
        
        if draw: #if can draw | draw is true
            if self._currentTiming[0]: #if late is true
                draw_text("LATE", timingFont, (152, 5, 126, 1) ,540, 540)
            if self._currentTiming[1]: #if early is true
                draw_text("EARLY", timingFont, (11, 153, 230, 1) ,540, 540)
    
    #method to handle late or early judgement and redirect to methods
    def lateEarly(self, timing):
        if timing[0]: #if late timing is true 
            self.late()
        elif timing[1]: #if early timing is true
            self.early()
        self._currentTiming=timing
        self._leEaFlag=True

    #methods to handle judgements from the judgement handling method
    #increments the count for the judgement,adds score if applicable
    #resets or adds to the combo 
    def perfect(self):
        self._perfects = self._perfects + 1
        self._score = self._score + 300
        self.comboUpdate()
    def great(self):
        self._greats = self._greats + 1
        self._score = self._score + 150
        self.comboUpdate()
    def good(self):
        self._goods = self._goods + 1
        self._score = self._score + 100
        self._currentCombo = 0
    def bad(self):
        self._bads = self._bads + 1
        self._score = self._score + 50
        self._currentCombo = 0
        self._health = self._health - 50
    def miss(self):
        self._misses = self._misses + 1
        self._currentCombo = 0
        self._health = self._health - 100
        #set variables for late early and judge display
        if not self._wordJudge:
            self._judgeName="0"
        else:
            self._judgeName="MISS"
        self._judgeFlag=True
        self._leEaFlag=True
        self._currentTiming=[False, False]
    
    def late(self):
        self._lates = self._lates + 1
    def early(self):
        self._earlys = self._earlys + 1
    
    #method to update the maximum combo 
    def comboUpdate(self):
        self._currentCombo = self._currentCombo  + 1
        if self._currentCombo >= 2:
            if self._currentCombo > self._maxCombo: #if current combo is greater than maximum combo
                self._maxCombo = self._currentCombo #max combo set to value of current combo
        
    #test method to output stats
    def report(self):
        print("score:",self._score)
        print("perfects:",self._perfects)
        print("greats",self._greats)
        print("goods:",self._goods)
        print("bad:",self._bads)
        print("miss:",self._misses)
        print("lates:",self._lates)
        print("earlys:",self._earlys)
        print("progress:",self._progress)
        print("Accuracy:", self._accuracy)

    def getStats(self):
        #perfect=0, greats=1, goods=2, bads=3, misses=4, lates=5, earlys=6, score = 7 progress=8, accuracy=9,health=10,max combo=11
        stats= [["Perfects",self._perfects], ["Greats",self._greats], ["Goods", self._goods], ["Bads",self._bads], ["Misses",self._misses], ["Lates",self._lates],["Earlys",self._earlys], ["Score",self._score], ["Progress",self._progress], ["Accuracy",self._accuracy],["Health",self._health],["Max Combo",self._maxCombo]]
        return stats

#main loop
restart=False
run = True #game loop flag
#functionality
while run: #loop that is active when game loop flag is True
    #pre-game    
    if not restart: #if retry hasnt been pressed
        mainMenu.enable()
        mainMenu.mainloop(screen)
    restart=False
    gameState=True
    start = True
    while gameState:    
        #events
        for event in pygame.event.get(): #loops through events
            if event.type == pygame.QUIT: #if a quit type event occurs
                exit() #exit game  

        #start functionality
        if start: #if it is the loop's first run
            restart=False
            start=False #set state flag so that this if statement never runs the code after
            start_time = time.time() #get the current time
            notes = getChart(chartIndex) #get the notes layout as an array
            unspawnedNotes = notes #initialise unspawned notes array
            spawnedNotes = [] #initialize the spawned notes
            print (notes) #test notes array initialized correctly
            print (start_time) #test start time initialized correctly
        #initialize play statistics            
            #initialize inputs to be hit on the first frame
            previous = [False,False,False,False]
            #creates statistics object taking in note layout of all notes, to save and edit statistics to
            playStats = Statistics(notes,accDisplayState,healthDeathState,progMetreState,wordJudge,lateEarlyState)
            #creates sounds object taking in sound levels, sfx state and chart index to play sounds
            SoundE = Sounds(bgmVol,sfxVol, hitSfxState, chartIndex)
            musicStart=False #initialize as false to show that chart music hasn't been played yet
            elapsed_time=-5 #initialize as -5 to avoid undefined errors at first run
            elapsedN = -5 #test variable for elapsed time
        #checks until time has passed 0 and if music hasnt started yet
        if elapsed_time>=0 and musicStart==False:
            SoundE.playChart() #plays music of the chart
            musicStart=True #sets true so that music doesn't play more than once
            print("music played") #for testing
        
        #key input check
        #if the key wasn't pressed on the last frame, but pressed on this frame, 
        #   then let it be hit(true)
        #otherwise 
        #   it will be recognized as not being hit(false)
        hitdata = hitCheck(previous)
        #save the last key states for the next frame
        previous = hitdata[1]
        hits = hitdata[0]
        #print(lState,uState,dState,rState) #print left,up,down,right arrow state
        elapsed_time = float(formatNumber(roundAny((time.time() - start_time) - 5, 0.02),3)) #get elapsed time
        
        #test if statement to print elapsed time in intervals of 1 second
        if elapsed_time>=elapsedN: #check if elapsed time greater than elapsedN
            elapsedN+= 1 #increment elapsedN by 1
            print("elapsed time is (s)", elapsed_time) #prints elapsed time for testing
        
        #test elapsed time on each frame
        #note spawning algorithm
        for note in unspawnedNotes: #for each note array inside the unspawnedNotes list
            if (float(note[0])-0.94)<=elapsed_time: #if it is time to spawn
                spawnedNotes.append(Note(note[0], note[1])) #add note to list of spawned notes
                unspawnedNotes.remove(note) #remove note from list of unspawned notes
        #rendering
        screen.fill((0,0,0)) #fill screen with color black
        screen.blit(jLineImg, (420, 50))
        
        #note update sequence
        index=0 #initialize index of the note so it can be identified
        for noteInstance in spawnedNotes: #for every note instance in the spawnedNotes list
            noteInstance.move() #note should move 
            noteInstance.update() #call update method for each instance
            noteInstance.report(elapsed_time) #report time note met judgement line or time met elapsed_time
            #assign variable to check if a note should be acted upon on this frame using current time and key states
            noteState=noteInstance.checkInput(hits, elapsed_time) 
            if noteState: #if note should be acted upon
                #get judgement, record it and play the sfx
                SoundE.sfxHandle(playStats.judgeHandle(noteInstance.judge(elapsed_time))) 
                playStats.lateEarly(noteInstance.lateOrEarly(elapsed_time)) #record late/early
                del spawnedNotes[index]  #despawn the note
            else: #if note shouldnt be acted upon
                if noteInstance.checkOut(elapsed_time): #if note is too late
                    playStats.miss() #record miss
                    SoundE.missHit() #play miss sfx
                    del spawnedNotes[index]  #despawn the note
            index+=1 #increment index for each loop
        #statistics drawing sequence

        playStats.statsUpdate(elapsed_time)
        
        #stopping condition- if all notes have been judged 
        if len(unspawnedNotes)==0 and len(spawnedNotes)==0:
            gameState=False #changes run state of game loop
            SoundE.endSong()
            playStats.progressEnd()
        
        elif playStats.healthDeath():
            gameState=False #changes run state of game loop
            SoundE.endSong()
            
            
        pygame.display.update() #update screen
        clock.tick(FPSE) #tick the clock based on FPSE variable integer
    stats= playStats.getStats()
    #initialize menu
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
    #adds judgements and late early
    for i in range(7):
        if i>=5: #when late early judgements
            #make them position at the bottom
            x=pygame_menu.locals.POSITION_SOUTH
        else: #when other judgements
            #make them position at the top
            x=pygame_menu.locals.POSITION_NORTH
        #create label and pack it
        newlabel=reportMenu.add.label(stats[i][0] + ": " + str(stats[i][1]),padding=0)
        frameContentJ.pack(newlabel,align=pygame_menu.locals.ALIGN_CENTER, vertical_position=x)
    
    #frame 2- chart stats
    chartframe = reportMenu.add.frame_v(300,450, background_colour=(20,20,20), padding=0,align=pygame_menu.locals.ALIGN_CENTER)
    container.pack(chartframe)
    chartFtitle = reportMenu.add.frame_h(300, 50, background_color=(40, 40, 40), padding=0)
    frameContentC = reportMenu.add.frame_v(300,400,background_color =(30,30,30), padding=0,vertical_position=pygame_menu.locals.POSITION_NORTH)
    chartframe.pack(chartFtitle)
    chartframe.pack(frameContentC)
    chartFtitle.pack(reportMenu.add.label('Chart Result:',padding=0),margin=(2,2), align=pygame_menu.locals.ALIGN_CENTER)
    #calculations
    noOfNotes=len(getChart(chartIndex))
    grade=checkGrade(noOfNotes,stats[10][1],stats[11][1],stats[0][1])
    rank= checkRank(noOfNotes,stats[7][1])
    #content labels
    nameOfChart=reportMenu.add.label(chartList[chartIndex][0],padding=0, font_size=25)
    nameOfChart.set_max_width(300)
    frameContentC.pack(nameOfChart,margin=(2,2),align=pygame_menu.locals.ALIGN_CENTER)
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
    performance=performanceCalc(noOfNotes,stats[7][1]) #calculate performance tuple
    if saveType==0: #if player is guest
        frameContentR.pack(reportMenu.add.label('Not Applicable',padding=0),margin=(2,2),align=pygame_menu.locals.ALIGN_CENTER)
    elif saveType==1: #if player is logged in
        ratings=ratingChangeCalc(performance[0]) #calculate ratings
        line = str(ratings[0]) + " -> " + str(ratings[1]) #format line
        frameContentR.pack(reportMenu.add.label(line,padding=0),margin=(2,2),align=pygame_menu.locals.ALIGN_CENTER)
        if ratings[2]>=0: #if the change in rating is positive
            line= "(+" + str(ratings[2]) + ")"
        else: #if change in rating is negative
            line= "(" + str(ratings[2]) + ")"
        frameContentR.pack(reportMenu.add.label(line,padding=0),margin=(2,2),align=pygame_menu.locals.ALIGN_CENTER)

    #frame 4- performance
    perfframe = reportMenu.add.frame_v(300,450, background_colour=(20,20,20), padding=0,align=pygame_menu.locals.ALIGN_RIGHT)
    container.pack(perfframe)
    perfFtitle = reportMenu.add.frame_h(300, 50, background_color=(40, 40, 40), padding=0)
    frameContentP = reportMenu.add.frame_v(300,400,background_color =(30,30,30), padding=0,vertical_position=pygame_menu.locals.POSITION_NORTH)
    perfframe.pack(perfFtitle)
    perfframe.pack(frameContentP)
    perfFtitle.pack(reportMenu.add.label('Performance:',padding=0),margin=(2,2), align=pygame_menu.locals.ALIGN_CENTER)
    perfDisplay=reportMenu.add.label("Overall: " + str(performance[0]) + " / " + str(performance[1]) ,padding=0)
    perfDisplay.set_max_width(300)
    frameContentP.pack(perfDisplay,margin=(2,2),align=pygame_menu.locals.ALIGN_CENTER)
    for i in range(2): #loop to add progress and accuracy labels
        #line format
        line= stats[i + 8][0] + ": " + str(stats[i + 8][1]) + "%"
        #add line as label
        frameContentP.pack(reportMenu.add.label(line,padding=0),margin=(2,2),align=pygame_menu.locals.ALIGN_CENTER)

    #buttons
    #return button
    returnB=reportMenu.add.button("Return",returnF,align=pygame_menu.locals.ALIGN_LEFT)
    returnB.set_float(True)
    #retry button
    retryB=reportMenu.add.button("Retry",retry,align=pygame_menu.locals.ALIGN_RIGHT)
    retryB.set_float(True)
    if saveType==1: #save button if player is logged in
        saveB=reportMenu.add.button("Save",align=pygame_menu.locals.ALIGN_CENTER)
        saveB.set_float(True) 
        def saveClicked(): #function to save data when button clicked
            #function to save data
            saveButton(currentUser,chartIndex,stats,grade,rank,ratings[1])
            saveB.hide() #hide button when data saved
            #new label to show data has been saved
            saveL=reportMenu.add.label("Saved!",align=pygame_menu.locals.ALIGN_CENTER)
            saveL.set_float(True)
        #apply new callback
        saveB.update_callback(saveClicked)


    #enable and run menu
    reportMenu.enable()
    reportMenu.mainloop(screen)



        




