import pygame,sys,time, os, csv; #imports modules listed

#tkinter functions
customtkinter.set_appearance_mode("System")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

app = customtkinter.CTk()  # create CTk window 
app.geometry("1280x720")

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
judgeLine=pygame.Rect(420, 50, 260, 60) #variable for control of judgement line display

lImg = pygame.image.load('l_arrow.png').convert_alpha()
lImg = pygame.transform.scale(lImg, (65,60))
uImg = pygame.image.load('u_arrow.png').convert_alpha()
uImg = pygame.transform.scale(uImg, (65,60))
dImg = pygame.image.load('d_arrow.png').convert_alpha()
dImg = pygame.transform.scale(dImg, (65,60))
rImg = pygame.image.load('r_arrow.png').convert_alpha()
rImg = pygame.transform.scale(rImg, (65,60))
jLineImg = pygame.image.load('j_line.png').convert_alpha()
jLineImg = pygame.transform.scale(jLineImg, (260,60))

#functions
def hitCheck(previous):
    hits=[]
    pressed= pygame.key.get_pressed()

    if pressed[pygame.K_LEFT] and previous[0]==False:
        hits.append(True)
    else:
        hits.append(False)
    if pressed[pygame.K_UP] and previous[1]==False:
        hits.append(True)
    else:
        hits.append(False)
    if pressed[pygame.K_DOWN] and previous[2]==False:
        hits.append(True)
    else:
        hits.append(False)
    if pressed[pygame.K_RIGHT] and previous[3]==False:
        hits.append(True)
    else:
        hits.append(False)
    
    return hits

#get chart data function
def getChart(chartIndex): #new function getChart taking chartIndex as a parameter
    filename = str(chartIndex) + ".csv" #concatenate with given chart index, and load this file
    returnNotes=[] #initialize array for appending to return
    with open(filename, "r", encoding='utf-8-sig') as csvfile: #open the file as reading
        datareader = csv.reader(csvfile) #csv function to read the chart file
        for row in datareader: #loop through rows in the chart file
            returnNotes.append(row) #add each row as an item in the array
    return returnNotes #return the returnNotes array

#function to round any number
def roundAny (value, resolution): #function to round a value, taking value and resolution as parameters
    rounded = round(float(value) / float(resolution)) * resolution #algorithm to return rounded value
    return rounded #return rounded value

#decimal place cut off function
def formatNumber(n, digits): #function to format decimal places, taking value and decimal places as parameters
    formatter = '{:.' + '{}'.format(digits) + 'f}' #format for new value
    x = round(n, digits) #for input into format
    return float(formatter.format(x)) #create the new string and then convert it to float for returning

#draw text
comboFont = pygame.font.SysFont("Arial", 50 , bold = True) #font setup variable for combo display
scoreFont = pygame.font.SysFont("Arial", 25 , bold = True) #font setup variable for score display
noteFont = pygame.font.SysFont("Arial", 18 , bold = True) #font setup variable for note display
judgeFont = pygame.font.SysFont("Arial", 30 , bold = True) #font setup variable for judgement display
timingFont = pygame.font.SysFont("Arial", 20 , bold = True) #font setup variable for timing display

#function drawing text to screen with specific font and settings
def draw_text(text, font, text_col, x, y): #takes text, font, colour and position as parameters
    img = font.render(text,True, text_col) #create parameter to render with
    screen.blit(img, (x, y)) #render the text


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
            color=(255,0,0) #red color
            self._image = lImg
        elif direction=="DOWN": #if down pointing note
            x = 485 #starting x pos will be after the left note
            color=(0,255,0) #green color
            self._image = dImg
        elif direction=="UP": #if up pointing note
            x = 550  #starting x pos will be after the down note
            color=(0,0,255) #blue color
            self._image = uImg
        elif direction=="RIGHT": #if right pointing note
            x = 615 #starting x pos will be furthest away and after up conveyor
            color=(255,255,255) #white
            self._image = rImg
        self.color=color
        self._x=x #set x value of note to x
        self._y=620 #set y value to a fixed value- every note will spawn on the same line
        self._rect=pygame.Rect(self._x,self._y, 65, 60) #private attribute for rectangle
        self._time=float(time) #time of note, taken from parameter input
        self._direction=direction #direction of note, taken from parameter input
        
    #procedure to update the note every frame
    def update(self): 
        #self._rect=pygame.Rect(self._x,self._y, 65, 60) #update the note with the latest x y coordinates
        #pygame.draw.rect(screen,self.color,self._rect,) #draw note as rectangle on screen
        #draw_text(self._direction, noteFont, (0,0,0) ,self._x, self._y) #draw note name on note
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
        if ((self._direction=='LEFT') and (hit[0])) or ((self._direction=='DOWN') and (hit[2])) or ((self._direction=='UP') and (hit[1])) or ((self._direction=='RIGHT') and (hit[3])): #test if key pressed and matches note key
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
    def __init__(self, notes): #initialize class and its variables
        #initialize variable statistics
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
        self._increment= (self._endTime - 5)/100
        self._progressMultiplier = 0
        self._lastTime=0
        
    #method to handle incoming judgements, judgement as parameter
    def judgeHandle(self,judgement):
        #method redirects
        if judgement=="PERFECT":
            self.perfect()
        if judgement=="GREAT":
            self.great()
        if judgement=="GOOD":
            self.good()
        if judgement=="BAD":
            self.bad()
        #save judgement characteristics for drawing method
        self._judgeName=judgement #save name of judgement
        self._judgeFlag=True #set to True-> that there is a new judgement given
        return judgement #return judgement passed in for next function criteria

    #method to draw and update statistics on the screen
    def statsUpdate(self,time):
        self.judgeDraw(time)
        self.leEaDraw(time)
        self.scoreDraw()
        self.comboDraw()
        self.healthDraw()
        self.progressUpdate(time)
        self.progressDraw()
        self.accuracyUpdate()
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
            draw_text("COMBO", scoreFont, (255,255,255) ,550, 410)
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
        #perfect=0, greats=1, goods=2, bads=3, misses=4, lates=5, earlys=6, score = 7 progress=8, accuracy=9
        stats= [["Perfects",self._perfects], ["Greats",self._greats], ["Goods", self._goods], ["Bads",self._bads], ["Misses",self._misses], ["Lates",self._lates],["Earlys",self._earlys], ["Score",self._score], ["Progress",self._progress], ["Accuracy",self._accuracy]]
        return stats

#main loop
reportState=False
gameState=True
start=True #game state flag
run = True #game loop flag
#functionality
while run: #loop that is active when game loop flag is True
    while gameState:    
        #events
        for event in pygame.event.get(): #loops through events
            if event.type == pygame.QUIT: #if a quit type event occurs
                gameState=False #set game loop flag to False    
                
                
        
        #start functionality
        if start: #if it is the loop's first run
            start=False #set state flag so that this if statement never runs the code after
            start_time = time.time() #get the current time
            notes = getChart(0) #get the notes layout as an array
            unspawnedNotes = [] #initialise unspawned notes array
            for note in notes: #loops through notes array 
                #modifies time of note to be ahead by 1 second
                note[0]= float(note[0]) + 5 
                unspawnedNotes.append(note) #adds note to unspawned notes array
            spawnedNotes = [] #initialize the spawned notes
            print (notes) #test notes array initialized correctly
            print (start_time) #test start time initialized correctly
            #initialize inputs to be hit on the first frame
            previous = [False,False,False,False]
            #initialize play statistics
            playStats = Statistics(unspawnedNotes)
            SoundE = Sounds(100, 100, True, 0)
            musicStart=False
            elapsed_time=0
        #checks until time has passed and if music hasnt started yet
        if elapsed_time>=5 and musicStart==False:
            SoundE.playChart() #plays music of the chart
            musicStart=True #sets true so that music doesn't play more than once
        
        #key input check
        #if the key wasn't pressed on the last frame, but pressed on this frame, then let it be hit(true)
        #otherwise it will be recognized as not being hit(false)
        hits = hitCheck(previous)
        #save the last key states for the next frame
        previous = hits
        #print(lState,uState,dState,rState) #print left,up,down,right arrow state
        #each loop's logic
        elapsed_time = float(formatNumber(roundAny(time.time() - start_time, 0.02),3)) #get elapsed time
        #print("elapsed time is (s)", elapsed_time) #prints elapsed time for testing
        #test elapsed time on each frame6
        #note spawning algorithm
        for note in unspawnedNotes: #for each note array inside the unspawnedNotes list
            if (float(note[0])-0.94)<=elapsed_time: #if it is time to spawn
                spawnedNotes.append(Note(note[0], note[1])) #add note to list of spawned notes
                unspawnedNotes.remove(note) #remove note from list of unspawned notes
        #rendering
        screen.fill((0,0,0)) #fill screen with color black
        #pygame.draw.rect(screen,(102, 255, 255),judgeLine,) #draw judgement line
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
            
            playStats.progressEnd()
        
        elif playStats.healthDeath():
            gameState=False #changes run state of game loop
            
            
            
        pygame.display.update() #update screen
        clock.tick(FPSE) #tick the clock based on FPSE variable integer

        if not gameState:
            pygame.quit()
            reportState=True
            start=True
            
    while reportState:

        if start:
            playStats.report() #print report stats
            stats=playStats.getStats()
            string=""
            for i in range(10):
                string = (string + stats[i][0] + ": " + str(stats[i][1]) + "\n")
            
            judgements = customtkinter.CTkLabel(master=app, text=string)
            judgements.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
            app.mainloop()
            start=False

        




