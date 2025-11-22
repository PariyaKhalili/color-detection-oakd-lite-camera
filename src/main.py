import depthai as dai
import cv2
import numpy as np
import os
from util import get_limits

OUTPUT_FOLDER = r"output_folder"
OUTPUT_FILENAME = "output.mp4"
FPS = 30.0

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
output_path = os.path.join(OUTPUT_FOLDER, OUTPUT_FILENAME)

# -----------------------------------------------------------
# Define impurity colors in BGR (input to get_limits)
# -----------------------------------------------------------
BLACK_BGR = [0, 0, 0]                # pure black
BROWN_BGR = [35, 20, 16]             # typical brown in BGR (tunable!)
# -----------------------------------------------------------

def main():
    pipeline = dai.Pipeline()

    # ------- Camera -------
    cam = pipeline.create(dai.node.ColorCamera)
    cam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_4_K)
    cam.setVideoSize(1920, 1080)
    cam.setIspScale(1, 1)
    cam.setFps(FPS)

    xout = pipeline.create(dai.node.XLinkOut)
    xout.setStreamName("video")
    cam.video.link(xout.input)

    control_in = pipeline.create(dai.node.XLinkIn)
    control_in.setStreamName("control")
    control_in.out.link(cam.inputControl)

    # ---------------------------------------------------------
    with dai.Device(pipeline) as device:

        video_q = device.getOutputQueue("video", maxSize=4, blocking=True)

        writer = None
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        print("[INFO] Running impurity detection... Press Q to quit.")

        while True:
            frame_packet = video_q.get()
            frame = frame_packet.getCvFrame()

            # ---------------------------------------------------------
            # 1) Convert to HSV
            # ---------------------------------------------------------
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # ---------------------------------------------------------
            # 2) Limits using the SAME util.py function
            # ---------------------------------------------------------
            lower_brown, upper_brown = get_limits("brown")
            lower_black, upper_black = get_limits("black")

            # ---------------------------------------------------------
            # 3) Two masks: black + brown
            # ---------------------------------------------------------
            mask_black = cv2.inRange(hsv, lower_black, upper_black)
            mask_brown = cv2.inRange(hsv, lower_brown, upper_brown)

            combined_mask = cv2.bitwise_or(mask_black, mask_brown)

            # ---------------------------------------------------------
            # 4) Find impurities using contours
            # ---------------------------------------------------------
            contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for c in contours:
                area = cv2.contourArea(c)
                if area > 200:  # ignore noise
                    x, y, w, h = cv2.boundingRect(c)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 3)
                    cv2.putText(frame, "Impurity", (x, y - 8),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

            # ---------------------------------------------------------
            # 5) Save & show frame
            # ---------------------------------------------------------
            if writer is None:
                h, w = frame.shape[:2]
                writer = cv2.VideoWriter(output_path, fourcc, FPS, (w, h), True)

            writer.write(frame)
            cv2.imshow("OAK-D Impurity Detection (using get_limits)", frame)

            key = cv2.waitKey(1) & 0xFF
            if key in [ord('q'), ord('Q')]:
                break

        if writer:
            writer.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()