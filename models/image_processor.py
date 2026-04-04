import cv2
import numpy as np
import os


def analyze_image(image_path):
    """
    Performs OpenCV-based image analysis on an uploaded border surveillance image.
    Includes: face detection, person detection, edge analysis, contour analysis,
    brightness analysis. Returns a human-readable analysis result string.
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            return "ERROR: Image could not be read for analysis."

        h, w = img.shape[:2]
        total_pixels = h * w
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        annotated = img.copy()

        results = {}
        flags = []

        # ── 1. FACE DETECTION (Haar Cascade) ──
        face_cascade_path = os.path.join(cv2.data.haarcascades, 'haarcascade_frontalface_default.xml')
        face_cascade = cv2.CascadeClassifier(face_cascade_path)
        faces = face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )
        num_faces = len(faces)
        results['faces'] = num_faces

        # Draw rectangles around faces on annotated image
        for (x, y, fw, fh) in faces:
            cv2.rectangle(annotated, (x, y), (x + fw, y + fh), (0, 0, 255), 2)
            cv2.putText(annotated, 'FACE', (x, y - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        if num_faces > 0:
            flags.append(f"ALERT: {num_faces} human face(s) detected")

        # ── 2. PERSON DETECTION (HOG Descriptor) ──
        hog = cv2.HOGDescriptor()
        hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

        # Resize large images for faster HOG detection
        scale = 1.0
        detect_img = gray
        if max(h, w) > 800:
            scale = 800.0 / max(h, w)
            detect_img = cv2.resize(gray, None, fx=scale, fy=scale)

        persons, _ = hog.detectMultiScale(
            detect_img, winStride=(8, 8), padding=(4, 4), scale=1.05
        )
        num_persons = len(persons)
        results['persons'] = num_persons

        # Draw rectangles around detected persons
        for (px, py, pw, ph) in persons:
            rx = int(px / scale)
            ry = int(py / scale)
            rw = int(pw / scale)
            rh = int(ph / scale)
            cv2.rectangle(annotated, (rx, ry), (rx + rw, ry + rh), (255, 0, 0), 2)
            cv2.putText(annotated, 'PERSON', (rx, ry - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        if num_persons > 0:
            flags.append(f"ALERT: {num_persons} person(s) detected in frame")

        # ── 3. EDGE DETECTION (Canny) ──
        edges = cv2.Canny(gray, threshold1=100, threshold2=200)
        edge_ratio = np.count_nonzero(edges) / total_pixels
        results['edge_density'] = f"{edge_ratio:.1%}"

        if edge_ratio > 0.15:
            flags.append("High edge density — complex scene or multiple objects")

        # ── 4. CONTOUR DETECTION ──
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        large_contours = [c for c in contours if cv2.contourArea(c) > 500]
        num_objects = len(large_contours)
        results['objects'] = num_objects

        # Draw contours on annotated image
        cv2.drawContours(annotated, large_contours, -1, (0, 255, 0), 1)

        if num_objects > 10:
            flags.append(f"High object count: {num_objects} distinct regions")

        # ── 5. BRIGHTNESS ANALYSIS ──
        mean_brightness = np.mean(gray)
        results['brightness'] = f"{mean_brightness:.0f}/255"

        if mean_brightness < 40:
            flags.append("Low brightness — possible night/obscured capture")

        # ── BUILD FINAL RESULT ──
        summary_parts = []
        summary_parts.append(f"Faces: {num_faces}")
        summary_parts.append(f"Persons: {num_persons}")
        summary_parts.append(f"Objects: {num_objects}")
        summary_parts.append(f"Edge density: {results['edge_density']}")
        summary_parts.append(f"Brightness: {results['brightness']}")

        summary = " | ".join(summary_parts)

        if flags:
            flag_text = " | ".join(flags)
            verdict = f"⚠ SUSPICIOUS: {flag_text}"
        else:
            verdict = "✓ CLEAR: No suspicious patterns detected"

        # ── SAVE ANNOTATED IMAGE ──
        name, ext = os.path.splitext(image_path)
        annotated_path = f"{name}_analyzed{ext}"
        # Add detection summary text to annotated image
        cv2.putText(annotated, f"Faces:{num_faces} Persons:{num_persons} Objects:{num_objects}",
                    (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.imwrite(annotated_path, annotated)

        return f"{verdict} | {summary}"

    except Exception as e:
        return f"Analysis error: {str(e)}"
