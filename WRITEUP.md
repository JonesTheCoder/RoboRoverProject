## Project: Search and Sample Return
### Writeup Template: You can use this file as a template for your writeup if you want to submit it as a markdown file, but feel free to use some other method and submit a pdf if you prefer.

---


**The goals / steps of this project are the following:**  

**Training / Calibration**  

* Download the simulator and take data in "Training Mode"
* Test out the functions in the Jupyter Notebook provided
* Add functions to detect obstacles and samples of interest (golden rocks)
* Fill in the `process_image()` function with the appropriate image processing steps (perspective transform, color threshold etc.) to get from raw images to a map.  The `output_image` you create in this step should demonstrate that your mapping pipeline works.
* Use `moviepy` to process the images in your saved dataset with the `process_image()` function.  Include the video you produce as part of your submission.

**Autonomous Navigation / Mapping**

* Fill in the `perception_step()` function within the `perception.py` script with the appropriate image processing functions to create a map and update `Rover()` data (similar to what you did with `process_image()` in the notebook).
* Fill in the `decision_step()` function within the `decision.py` script with conditional statements that take into consideration the outputs of the `perception_step()` in deciding how to issue throttle, brake and steering commands.
* Iterate on your perception and decision function until your rover does a reasonable (need to define metric) job of navigating and mapping.  

[//]: # (Image References)

[image1]: ./misc/rover_image.jpg
[image2]: ./calibration_images/example_grid1.jpg
[image3]: ./calibration_images/example_rock1.jpg

## [Rubric](https://review.udacity.com/#!/rubrics/916/view) Points
### Here I will consider the rubric points individually and describe how I addressed each point in my implementation.  

---
### Writeup / README

#### 1. Provide a Writeup / README that includes all the rubric points and how you addressed each one.  You can submit your writeup as markdown or pdf.  

You're reading it!

### Notebook Analysis
#### 1. Run the functions provided in the notebook on test images (first with the test data provided, next on data you have recorded). Add/modify functions to allow for color selection of obstacles and rock samples.

To do obstacle and rock sample detection, I started with the `color_thresh`
function provided in the source implementation.  To do obstacle detection
I defined a new function `detect_obstacles` that accepts an image,
passes it through `color_thresh`, and then just inverts the selection
by multiplying it by -1 and then adding 1 (mapping 1 to 0 and 0 to 1).
Because the "out of view" portion of the rover's view gets marked
as obstacles this way (when really the rover just can't see it),
I used an all-white image passed through the perspective transformation
 to make a mask so that we can filter to just obstacles the rover can
 actually see.

For rock detection, I found that the third value (RG *B*) is the one that
goes down quite sharply for rock pixels, so I used similar logic to
color_thresh selecting pixels with high values in the first 2 slots of their
tuple, and a relatively low value in the 3rd spot (function is named:
`detect_sample_rocks`)


#### 1. Populate the `process_image()` function with the appropriate analysis steps to map pixels identifying navigable terrain, obstacles and rock samples into a worldmap.  Run `process_image()` on your test data using the `moviepy` functions provided to create video output of your result.

For this step I took each image (after perspective transforming it)
and passed it through all 3 color thresholding operations to obtain
pixels where there's navigable terrain, obstacles, and rocks.

After transforming these to world pixel values, I set the color values
on the world map to red for obstacles, green for safe terrain, and yellow
for rocks, dealing with overlap by prioritizing rocks > navigable > obstacles.

Humorously, because my test video involves collecting some of the rock
samples, the world map gets annotated with wedges of yellow as the rock
sweeps across the field of view while being recovered.

### Autonomous Navigation and Mapping

#### 1. Fill in the `perception_step()` (at the bottom of the `perception.py` script) and `decision_step()` (in `decision.py`) functions in the autonomous mapping scripts and an explanation is provided in the writeup of how and why these functions were modified as they were.

For the perception step, the code is very similar to `process_image`
in the notebook.  I copied over into `perception.py` all the relevent
color-thresholding functions for rocks and obstacles, and applied
the same pipeline to each rover image: warp, detect all 3 categories,
and apply their detections to the output (in this case both the
  rover vision image and the world map).  For rover vision,
  I just let each category (nav, obstacle, rock) have it's own
  color channel (0, 1, 2) for simplicity.

While testing autonomous driving, I realized that sometimes the terrain
detection was extrapolating too far in front of the robot and marking
big swaths of territory as navigable that were really just difficult to
judge distance on, and it was impacting my mapping fidelity.  To combat
this I added a mask to the navigable terrain detection (by writing
  a new function, `detect_terrain`) and here I just cut off
all pixels in the first 50 rows so that the rover wouldn't interpret
as navigable anything it was close enough to see well.  This helped a lot.

For the decision step, I left most of the program intact.  One important
modification I did make was to nudge the rover to the right side of
it's navigable angles rather than the strict mean (by sorting the angles
  and then discarding the left-most 25% of them before taking the mean).
This makes the rover prefer to stick close to the right wall, which helps it
make progress throughout the map rather than bouncing around more or less
at random.  I also realized that there was a common issue of getting stuck
so I added some code to track the last 30 frames of driving in `forward` mode
and if the position has stopped changing much, I make it back up a fixed
distance and start again.  This seems to eliminate most of the cases of
getting stuck on terrain.  I implemented a similar
history-checking function for steering angle to prevent cases where the
rover tries to steer hard-right indefinitely (by attenuating the clip
  threshold for the steering angle down if we've been turning hard for
  30 frames or so).


#### 2. Launching in autonomous mode your rover can navigate and map autonomously.  Explain your results and how you might improve them in your writeup.  

**Note: running the simulator with different choices of resolution and graphics quality may produce different results, particularly on different machines!  Make a note of your simulator settings (resolution and graphics quality set on launch) and frames per second (FPS output to terminal by `drive_rover.py`) in your writeup when you submit the project so your reviewer can reproduce your results.**

The rover now tends to follow the right wall and most of the time manages
to get to over 40% of the terrain with 60% fidelity.  (1024x768, 6 FPS).
I do notice that the rover makes bad decisions when a close-up obstacle is
in the way.  I think one way to improve steering decisions further would
be to weight the nav angles by the perceived distance, thus preferring to
turn more towards angles that have lots of distance in front of them and
devaluing nav angles where an obstacle is a few feet away.
