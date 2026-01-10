## Developing an HPM Walk-thru video

Creating a screen capture tutorial for the **HSTL Photo Metadata System (HPM)** is a great way to document its GUI workflow. Since you want to start simple and skip audio, we can focus on a **high-quality visual sequence** that allows users to follow the metadata process at their own pace.

Here is a two-phase plan to get you from a basic recording to a polished, annotated walkthrough.

---

## Phase 1: The Foundation (Single-Screen Captures)

Instead of recording a long, rambling video, focus on capturing "clean" segments. This makes editing much easier later.

### 1. Preparation & Environment

* **Resolution:** Set your monitor (or the app window) to a standard resolution like **1920x1080 (1080p)**. This ensures the text in the HPM interface remains crisp.
* **Clean Desktop:** Hide your taskbar or any messy background files.
* **Sample Data:** Have a specific folder of photos ready that contains the metadata fields you want to demonstrate (e.g., EXIF data, GPS, or custom HSTL tags).

### 2. The "One Screen" Capture Strategy

Use a tool like **OBS Studio** (Free/Open Source) or **ShareX**.

* **Record in segments:** Record one specific action at a time (e.g., "Loading a Directory," then "Editing a Metadata Field," then "Saving Changes").
* **Static Mouse:** Keep your mouse still when you aren't clicking. This prevents the video from feeling "busy."

---

## Phase 2: Adding Annotations & Polish

Once you have your raw clips, you can layer in information without needing a voiceover.

### 1. Choosing an Editing Tool

Since you aren't using audio, the visual cues need to be strong.

* **CapCut or DaVinci Resolve:** Great for adding professional-looking text overlays and arrows.
* **ActivePresenter:** Specifically designed for software simulations; it can automatically highlight where you click.

### 2. Annotation Techniques

Since there is no audio, use these visual "anchors" to guide the user:

* **Callouts:** Use text boxes to explain *why* a certain metadata field is being filled.
* **Zoom & Pan:** If the HPM GUI has small text fields, zoom in on that specific area of the framework during the edit.
* **Mouse Highlights:** Use a "halo" or "click ripple" effect so users can clearly see where your cursor is interacting with the framework.

---

## Suggested Content Structure

To keep the walkthrough logical, I recommend following this sequence:

| Step | Action | Visual Focus |
| --- | --- | --- |
| **01** | **Initialization** | Opening the HPM directory and launching the executable. |
| **02** | **Importing** | Using the file browser to pull in HSTL photo batches. |
| **03** | **Metadata Entry** | Highlighting the specific HSTL schema fields. |
| **04** | **Validation** | Showing how the system checks for metadata errors. |
| **05** | **Export/Save** | The final step of committing the metadata to the files. |

---

## Tools Recommendation

* **For Recording:** **OBS Studio**. It’s the industry standard for capturing high-frame-rate GUI interactions.
* **For "Quick & Dirty" Annotations:** **Screenity** (Chrome Extension) or **Snagit**. These allow you to draw directly on the screen while you record.

**Would you like me to help you draft the specific "on-screen text" for each step of the HPM workflow?**