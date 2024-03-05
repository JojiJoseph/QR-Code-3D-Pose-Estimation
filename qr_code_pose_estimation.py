import cv2
from pyzbar.pyzbar import decode
import numpy as np
import argparse

def parse_args():
    """ Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Detect QR codes in a video stream.")
    parser.add_argument("--video", type=str, default="0", help="Path to the video file or device index.")
    return parser.parse_args()

def pseudo_camera_matrix(img):
    """ Calculate a pseudo camera matrix for the image."""
    fx = img.shape[1]
    fy = fx
    cx = img.shape[1] / 2
    cy = img.shape[0] / 2
    return np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]])

def process_frame(frame):
    """ Process a single frame for QR code detection and pose estimation."""
    pyzbar_result = decode(frame)
    if pyzbar_result:
        for pybar_data in pyzbar_result:
            qr_data = pybar_data.data.decode('utf-8')
            print(f"Pyzbar detected QR Code data: {qr_data}")
            
            points_2d = np.array([point for point in pybar_data.polygon], dtype=np.float32)
            points_3d = np.array([[-0.4, -0.4, 0], [0.4, -0.4, 0], [0.4, 0.4, 0], [-0.4, 0.4, 0]], dtype=np.float32)
            
            retval, rvec, tvec = cv2.solvePnP(points_3d, points_2d, pseudo_camera_matrix(frame), None)
            # Draw the polygon around the QR code
            cv2.polylines(frame, [points_2d.astype(int)], True, (0, 255, 0), 2)
            x_mean, y_mean = np.mean(points_2d, axis=0)
            cv2.drawFrameAxes(frame, pseudo_camera_matrix(frame), None, rvec, tvec, 1.0)
            # Put the QR code data on the frame
            cv2.putText(frame, qr_data, (int(x_mean), int(y_mean)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    
    cv2.imshow('QR Code', frame)
    return frame

def main():
    """ Main function to capture video and detect QR codes."""
    args = parse_args()
    video_path = args.video
    # check if the video path is an integer
    if video_path.isnumeric():
        video_path = int(video_path)
    cap = cv2.VideoCapture(video_path)  # Adjust the device index as needed

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
        
        processed_frame = process_frame(frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("Exiting...")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
