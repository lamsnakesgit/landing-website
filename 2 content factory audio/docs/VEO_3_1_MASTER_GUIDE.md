# Master Guide: Video Analysis & Prompting for Google Veo 3.1 Light

To achieve a 1:1 recreation of high-end commercials like the "sen sulu" video, you need to move beyond simple descriptions and use **technical cinematic language** that Veo 3.1 understands.

---

## 1. How to Analyze Videos for Veo (The "Reverse Engineering" Method)

Don't just look at *what* is in the frame; look at *how* it moves and *how* it's lit.

### A. Motion Analysis (The "Speed & Direction" Rule)
*   **Primary Motion:** What is the main object doing? (Rotating, sliding, opening).
*   **Secondary Motion:** What is the camera doing? (Fast whip pan, rapid zoom, tracking).
*   **Temporal Dynamics:** Is it slow-motion (high FPS look) or fast-paced?
    *   *Tip:* For the "sen sulu" video, the motion is **snappy**. It uses "Ease-in/Ease-out" dynamics.

### B. Lighting & Texture Analysis
*   **Key Light:** Where is the strongest light? (e.g., "Rim lighting" for the gold edges).
*   **Material Response:** How does the light hit the surface? (e.g., "Anisotropic highlights" on metal, "Subsurface scattering" on cream).

### C. Frame Composition
*   **Focal Length:** Is it a wide shot or a tight macro? (Commercials use 85mm-100mm for products).

---

## 2. Advanced Prompting Techniques for Veo 3.1

### A. The "Action-First" Structure
Veo prioritizes the beginning of the prompt for motion.
*   **Bad:** "A cosmetic tube on a table, it rotates fast."
*   **Good:** "Fast 360-degree rotation of a sleek black cosmetic tube..."

### B. Using "Power Keywords" for Dynamics
To fix the "too slow/static" issue, use these specific terms:
*   **Motion:** `Kinetic`, `High-velocity`, `Whip pan`, `Rapid zoom-in`, `Dynamic burst`, `Explosive movement`.
*   **Camera:** `Handheld jitter`, `FPV drone style`, `Dolly zoom`, `Crash zoom`.
*   **Physics:** `Fluid dynamics`, `Satisfying weight`, `High inertia`.

### C. The "Technical Stack" (Add to the end of every prompt)
> `... 4k, highly detailed, cinematic lighting, 60fps look, commercial color grade, Unreal Engine 5.4 render style, shot on Arri Alexa.`

---

## 3. "Sen Sulu" Specific Improvements

The original video has **fast transitions** and **dynamic shifts**. To replicate this in a single clip:

1.  **Specify Speed:** Use words like "Rapidly", "Instantly", or "Aggressive".
2.  **Camera Transitions:** Describe the camera moving *through* the scene.
3.  **Lighting Shifts:** Mention "Dynamic shadows" or "Moving highlights".

### Example of an "Aggressive" Prompt for Scene 1:
> "Dynamic high-speed macro shot: A black 'sen sulu' tube aggressively enters the frame with a whip-pan motion, stopping abruptly with a slight bounce (inertia). Metallic gold lettering catches a sharp rim light. The camera then performs a rapid 180-degree orbit around the cap. High contrast, premium beauty commercial style, 4k, 60fps."

---

## 4. Pro Tips from the "Forums" (Hidden Gems)
*   **Negative Prompting (via positive words):** To avoid "AI blur," use `sharp focus`, `zero motion blur on subject`, `clean edges`.
*   **The "Material" Trick:** Instead of just "gold," use `18k polished gold with mirror reflections`.
*   **The "Environment" Trick:** Instead of "beige background," use `out-of-focus luxury spa interior, soft bokeh, warm ambient glow`.
