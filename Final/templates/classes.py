
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
            x = 440 #starting x position will be furthest to the left
            color=(255,0,0) #red color
        elif direction=="DOWN": #if down pointing note
            x = 540 #starting x pos will be after the left note
            color=(0,255,0) #green color
        elif direction=="UP": #if up pointing note
            x = 640  #starting x pos will be after the down note
            color=(0,0,255) #blue color
        elif direction=="RIGHT": #if right pointing note
            x = 740 #starting x pos will be furthest away and after up conveyor
            color=(255,255,255) #white
        self.color=color
        self._x=x #set x value of note to x
        self._y=620 #set y value to a fixed value- every note will spawn on the same line
        self._rect=pygame.Rect(self._x,self._y, 60, 30) #private attribute for rectangle
        self._time=float(time) #time of note, taken from parameter input
        self._direction=direction #direction of note, taken from parameter input
    
    #procedure to update the note every frame
    def update(self): 
        self._rect=pygame.Rect(self._x,self._y, 60, 30) #update the note with the latest x y coordinates
        pygame.draw.rect(screen,self.color,self._rect,) #draw note as rectangle on screen
        draw_text(self._direction, noteFont, (0,0,0) ,self._x, self._y) #draw note name on note
    
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
        self.healthDeath()
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
            while self._lastTime <= time - 5: #while maximum total interval time isn't surpassed
                self._progressMultiplier = self._progressMultiplier + 1 #increment multiplier
                self._lastTime = self._increment * self._progressMultiplier #multiply time increment by multiplier 
            self._progress = self._progressMultiplier - 1 #deduct 1 because lastTime must be greater than current time
            #progress is the amount of whole number intervals the game has reached
    
    #method to draw progress bar to the screen
    def progressDraw(self):
        size = (self._progress/100)*400 #adjust size to reflect progress meter
        progressMeter=pygame.Rect(420, 50, size, 20) #uses size as length, defines as rectangle
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
            global run #use global run variable in main game loop
            run= False #stop run of the main game loop
        
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
