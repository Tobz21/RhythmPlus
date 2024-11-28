        #stopping condition- if all notes have been judged 
        if len(unspawnedNotes)==0 and len(spawnedNotes)==0:
            gameState=False #changes run state of game loop
            SoundE.endSong()
            playStats.progressEnd()
            screen.fill((0,0,0))
            draw_text("Chart Complete!", comboFont, (255,255,255) ,550, 360)
            draw_text("Loading reports screen...", comboFont, (255,255,255) ,350, 420)
            dead=False
        #stopping condition 2- if player died/health<=0
        elif playStats.healthDeath():
            gameState=False #changes run state of game loop
            SoundE.endSong()
            screen.fill((0,0,0))
            draw_text("Chart Failed!", comboFont, (255,255,255) ,550, 360)
            draw_text("Loading reports screen...", comboFont, (255,255,255) ,350, 420)
            dead=True
            deadTime=elapsed_time 