import numpy as np
import cv2
import pygame
import smtplib
from email.mime.text import MIMEText
import os

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Load siren sound
sound_file = 'police-6007.mp3'
if not os.path.exists(sound_file):
    print(f"Sound file {sound_file} not found.")
    exit(1)
siren_sound = pygame.mixer.Sound(sound_file)
paused = False

# Function to send email notification
def send_email_alert():
    msg = MIMEText("Tampering detected on your CCTV system.")
    msg['Subject'] = 'CCTV Alert'
    msg['From'] = 'your_email@example.com'
    msg['To'] = 'recipient@example.com'

    try:
        with smtplib.SMTP('smtp.example.com', 587) as server:
            server.starttls()
            server.login('your_email@example.com', 'password')
            server.send_message(msg)
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Video capturing starts
cap = cv2.VideoCapture(0)
fgbg = cv2.createBackgroundSubtractorMOG2()
ret, frame = cap.read()
fgmask = fgbg.apply(frame)
kernel = np.ones((5, 5), np.uint8)

while True:
    ret, frame = cap.read()
    if frame is None:
        print("End of frame")
        break
    else:
        a = 0
        bounding_rect = []
        fgmask = fgbg.apply(frame)
        fgmask = cv2.erode(fgmask, kernel, iterations=5)
        fgmask = cv2.dilate(fgmask, kernel, iterations=5)
        contours, _ = cv2.findContours(fgmask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        for i in range(len(contours)):
            bounding_rect.append(cv2.boundingRect(contours[i]))
        
        for i in range(len(contours)):
            if bounding_rect[i][2] >= 40 or bounding_rect[i][3] >= 40:
                a += (bounding_rect[i][2]) * (bounding_rect[i][3])
        
        if a >= int(frame.shape[0]) * int(frame.shape[1]) / 3:
            cv2.putText(frame, "TAMPERING DETECTED", (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            # Play siren sound if not paused
            if not paused:
                siren_sound.play()
            # Send email notification
            send_email_alert()
        
        cv2.imshow('frame', frame)
    
    # Handle key events
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if paused:
                    siren_sound.unpause()
                    paused = False
                else:
                    siren_sound.pause()
                    paused = True

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
pygame.quit()
